import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.task import Task
from app.schemas.project import ProjectUpdate
from app.schemas.code import GenerationManifest, TaskCodeOutput
from app.services.project_service import update_project
from app.services.task_service import get_tasks_by_project_id, update_task_status
from app.services.architecture_service import get_architecture_by_project_id
from app.services.workspace_service import workspace_service
from app.services.artifact_service import save_file_artifact
from app.schemas.architecture import SystemArchitecture
from app.schemas.task import TaskResponse
from app.agents.database_engineer import database_engineer_agent
from app.agents.backend_developer import backend_developer_agent
from app.agents.frontend_developer import frontend_developer_agent
from app.orchestrator.scaffolding import scaffolding_generator

logger = logging.getLogger(__name__)


class CodeGenerationOrchestrator:
    """
    Orchestrates the multi-agent code generation pipeline.
    Executes tasks in strict topological order, routes to specialized agents,
    safely writes source files to the project workspace, and tracks file artifacts.
    """

    AGENT_MAP = {
        "database_engineer": database_engineer_agent,
        "backend_developer": backend_developer_agent,
        "frontend_developer": frontend_developer_agent,
    }

    def _build_workspace_context(self, project_name: str, task: TaskResponse) -> str:
        """
        Extract concise existing code context (models, schemas, routers) from workspace
        so downstream agents don't hallucinate or invent conflicting signatures.
        """
        try:
            workspace_dir = workspace_service.get_workspace_dir(project_name)
        except Exception:
            return ""

        if not workspace_dir.exists():
            return ""

        context_files = []
        target_dirs = [
            workspace_dir / "backend" / "app" / "database",
            workspace_dir / "backend" / "app" / "models",
            workspace_dir / "backend" / "app" / "schemas",
        ]
        if task.assigned_agent == "frontend_developer":
            target_dirs.append(workspace_dir / "backend" / "app" / "api")

        for target_dir in target_dirs:
            if not target_dir.exists():
                continue
            for py_file in target_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                try:
                    rel_path = py_file.relative_to(workspace_dir).as_posix()
                    content = py_file.read_text(encoding="utf-8")
                    lines = content.splitlines()
                    # Truncate to first 60 lines per file
                    truncated = "\n".join(lines[:60])
                    context_files.append(f"--- {rel_path} ---\n{truncated}")
                except Exception:
                    pass

        return "\n\n".join(context_files)

    def _sanitize_generated_file(self, file_path: str, content: str) -> str:
        """
        Defensive post-processing sanitizer for LLM-generated code.
        Repairs common hallucinations, import errors, and framework mismatches.
        """
        if file_path.endswith(".py"):
            # 1. Root package fix: 'from backend.app' / 'import backend.app' / 'from backend' -> 'from app' / 'import app'
            content = re.sub(r"\bfrom\s+backend\.app\b", "from app", content)
            content = re.sub(r"\bimport\s+backend\.app\b", "import app", content)
            content = re.sub(r"\bfrom\s+backend\b", "from app", content)

            # 2. Fix Pydantic v1 'class Config:\n    orm_mode = True' -> 'model_config = ConfigDict(from_attributes=True)'
            if "orm_mode = True" in content:
                if "from pydantic import" in content and "ConfigDict" not in content:
                    content = re.sub(r"from pydantic import ([^\n]+)", r"from pydantic import \1, ConfigDict", content)
                content = re.sub(
                    r"class\s+Config\s*:\s*\n\s*orm_mode\s*=\s*True",
                    "model_config = ConfigDict(from_attributes=True)",
                    content,
                )

            # 3. Fix multiple Base definitions in models if Base is already provided
            if "backend/app/models/" in file_path and "Base = declarative_base()" in content:
                content = re.sub(r"Base\s*=\s*declarative_base\(\)[^\n]*\n?", "", content)
                if "from app.database.session import Base" not in content and "from app.database import Base" not in content:
                    content = "from app.database.session import Base\n" + content

            # 4. Fix server_default=datetime.now()
            if "server_default=datetime.now" in content or "server_default=datetime.utcnow" in content:
                content = re.sub(r"server_default\s*=\s*datetime\.(now|utcnow)\(\)[^,\)]*", "server_default=func.now()", content)
                if "func" not in content:
                    if "from sqlalchemy import" in content:
                        content = re.sub(r"from sqlalchemy import ([^\n]+)", r"from sqlalchemy import \1, func", content)
                    else:
                        content = "from sqlalchemy import func\n" + content

        elif file_path.endswith(".tsx") or file_path.endswith(".jsx") or file_path.endswith(".ts") or file_path.endswith(".js"):
            # 1. Next.js 14 App Router: useRouter from 'next/router' throws an error in app directory!
            content = re.sub(r"from\s+['\"]next/router['\"]", "from 'next/navigation'", content)

            # 2. Add 'use client'; if hooks are used and directive is missing
            if file_path.endswith(".tsx") or file_path.endswith(".jsx"):
                hook_pattern = r"\b(useState|useEffect|useContext|useReducer|useCallback|useMemo|useRef|useRouter|usePathname|useSearchParams|useParams)\b"
                if re.search(hook_pattern, content):
                    first_line = content.strip().split("\n")[0].strip()
                    if not (first_line.startswith('"use client"') or first_line.startswith("'use client'")):
                        content = "'use client';\n\n" + content

            # 3. Fix recursive / invalid fetch imports: 'import { fetch } from 'next/server';'
            content = re.sub(r"import\s*\{[^}]*fetch[^}]*\}\s*from\s*['\"]next/server['\"];?\n?", "", content)

        return content

    async def execute_task_code_generation(
        self,
        project_name: str,
        task: TaskResponse,
        architecture: SystemArchitecture,
    ) -> TaskCodeOutput:
        """Route an individual task to its specialized developer agent with full workspace context."""
        agent = self.AGENT_MAP.get(task.assigned_agent)
        if not agent:
            # Fallback or pass for non-developer agents (e.g. tester, reviewer)
            return TaskCodeOutput(
                task_key=task.task_key,
                summary=f"Task assigned to {task.assigned_agent} will be executed in testing/verification phase.",
                files=[],
            )

        workspace_context = self._build_workspace_context(project_name, task)

        return await agent.execute_task(
            project_name=project_name,
            task=task,
            architecture=architecture,
            existing_code_context=workspace_context,
        )

    async def generate_project(
        self,
        db: Session,
        project: Project,
    ) -> GenerationManifest:
        """
        Execute full code generation for all planned tasks across the project.
        """
        logger.info(f"Starting code generation for project: {project.name} ({project.id})")

        arch_record = get_architecture_by_project_id(db, project.id)
        if not arch_record:
            raise ValueError("Project architecture must be generated before code generation.")

        architecture = SystemArchitecture.model_validate(arch_record.specification)
        tasks = get_tasks_by_project_id(db, project.id)
        if not tasks:
            raise ValueError("Project task plan must exist before code generation.")

        # Update status to generating
        update_project(db, project, ProjectUpdate(status="generating"))

        workspace_dir = workspace_service.get_workspace_dir(project.name)
        generated_artifacts_meta: List[Dict[str, Any]] = []

        try:
            for task in tasks:
                task_resp = TaskResponse.model_validate(task)
                logger.info(f"Generating code for Task [{task.task_key}]: {task.title} (Agent: {task.assigned_agent})")
                update_task_status(db, task.id, "in_progress")

                code_output = await self.execute_task_code_generation(
                    project_name=project.name,
                    task=task_resp,
                    architecture=architecture,
                )

                # Write generated files safely into the workspace with post-processing sanitation
                for file_entry in code_output.files:
                    sanitized_content = self._sanitize_generated_file(
                        file_entry.file_path, file_entry.content
                    )
                    meta = workspace_service.write_file(
                        project_slug=project.name,
                        relative_path=file_entry.file_path,
                        content=sanitized_content,
                        overwrite=True,
                    )
                    # Persist metadata in PostgreSQL
                    save_file_artifact(
                        db=db,
                        project_id=project.id,
                        file_path=meta["relative_path"],
                        file_hash=meta["sha256"],
                        agent=task.assigned_agent,
                        task_id=task.id,
                    )
                    generated_artifacts_meta.append(meta)

                update_task_status(db, task.id, "completed")

            # Synthesize runtime scaffolding (requirements, main.py, session.py, package.json, Dockerfiles, docker-compose)
            current_files = [f["relative_path"] for f in workspace_service.list_files(project.name)]
            api_routers = [f for f in current_files if "backend/app/api/" in f and f.endswith(".py")]
            scaffold_files = scaffolding_generator.generate_scaffolding(
                project_name=project.name,
                architecture=architecture,
                discovered_api_routers=api_routers,
            )
            for rel_path, content in scaffold_files.items():
                # Avoid overwriting already custom-generated user files unless they don't exist
                # But ensure foundational runtime configs exist
                if not (workspace_dir / rel_path).exists():
                    meta = workspace_service.write_file(
                        project_slug=project.name,
                        relative_path=rel_path,
                        content=content,
                        overwrite=True,
                    )
                    save_file_artifact(
                        db=db,
                        project_id=project.id,
                        file_path=meta["relative_path"],
                        file_hash=meta["sha256"],
                        agent="scaffolding",
                    )
                    generated_artifacts_meta.append(meta)

            # Generate project README.md and manifest in the generated project
            readme_content = self._build_project_readme(project, architecture, tasks)
            readme_meta = workspace_service.write_file(
                project_slug=project.name,
                relative_path="README.md",
                content=readme_content,
                overwrite=True,
            )
            save_file_artifact(
                db=db,
                project_id=project.id,
                file_path="README.md",
                file_hash=readme_meta["sha256"],
                agent="orchestrator",
            )
            generated_artifacts_meta.append(readme_meta)

            manifest_dict = {
                "project_id": project.id,
                "project_name": project.name,
                "workspace_directory": str(workspace_dir),
                "total_files": len(generated_artifacts_meta),
                "files": workspace_service.list_files(project.name),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            manifest_meta = workspace_service.write_file(
                project_slug=project.name,
                relative_path="generation_manifest.json",
                content=json.dumps(manifest_dict, indent=2),
                overwrite=True,
            )
            save_file_artifact(
                db=db,
                project_id=project.id,
                file_path="generation_manifest.json",
                file_hash=manifest_meta["sha256"],
                agent="orchestrator",
            )

            # Query all finalized files including manifest
            all_files = workspace_service.list_files(project.name)

            # Transition project status to generated
            update_project(db, project, ProjectUpdate(status="completed"))

            logger.info(
                f"Successfully completed code generation for {project.name}. "
                f"Generated {len(all_files)} files."
            )

            return GenerationManifest(
                project_id=project.id,
                project_name=project.name,
                workspace_directory=str(workspace_dir),
                total_files=len(all_files),
                files=all_files,
                generated_at=datetime.now(timezone.utc),
            )

        except Exception as exc:
            logger.error(f"Code generation failed: {exc}", exc_info=True)
            update_project(db, project, ProjectUpdate(status="failed"))
            raise exc

    def ensure_project_scaffolding(
        self,
        db: Session,
        project: Project,
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes any missing runtime scaffolding files for an existing project workspace.
        Returns list of newly created artifact metadata dicts.
        """
        arch_record = get_architecture_by_project_id(db, project.id)
        architecture = (
            SystemArchitecture.model_validate(arch_record.specification)
            if arch_record
            else SystemArchitecture.model_validate({
                "project_name": project.name,
                "architecture_pattern": "layered",
                "tech_stack": {
                    "backend": "FastAPI",
                    "frontend": "Next.js",
                    "database": "PostgreSQL",
                    "orm": "SQLAlchemy",
                    "authentication": "JWT",
                },
                "components": [],
                "entities": [],
                "api_contracts": [],
                "architectural_decisions": [],
            })
        )
        workspace_dir = workspace_service.get_workspace_dir(project.name)
        current_files = [f["relative_path"] for f in workspace_service.list_files(project.name)]
        api_routers = [f for f in current_files if "backend/app/api/" in f and f.endswith(".py")]

        scaffold_files = scaffolding_generator.generate_scaffolding(
            project_name=project.name,
            architecture=architecture,
            discovered_api_routers=api_routers,
        )

        created_meta = []
        for rel_path, content in scaffold_files.items():
            dest = workspace_dir / rel_path
            is_corrupt_entrypoint = rel_path.endswith("main.py") and dest.exists() and dest.stat().st_size < 100
            if not dest.exists() or is_corrupt_entrypoint:
                meta = workspace_service.write_file(
                    project_slug=project.name,
                    relative_path=rel_path,
                    content=content,
                    overwrite=True,
                )
                save_file_artifact(
                    db=db,
                    project_id=project.id,
                    file_path=meta["relative_path"],
                    file_hash=meta["sha256"],
                    agent="scaffolding",
                )
                created_meta.append(meta)

        return created_meta

    def _build_project_readme(
        self,
        project: Project,
        architecture: SystemArchitecture,
        tasks: List[Task],
    ) -> str:
        """Construct a developer README for the generated application."""
        return f"""# {project.name}

> Generated automatically by **Orchestrix** — Autonomous AI Software Engineer.

## Overview
{project.description}

## Architecture
- **Pattern**: {architecture.architecture_pattern}
- **Backend**: {architecture.tech_stack.backend}
- **Frontend**: {architecture.tech_stack.frontend}
- **Database**: {architecture.tech_stack.database} ({architecture.tech_stack.orm})
- **Authentication**: {architecture.tech_stack.authentication}

## Planned & Generated Tasks
{chr(10).join(f"- **[{t.task_key}]** {t.title} *(Agent: {t.assigned_agent})*" for t in tasks)}

## Running Locally
Refer to backend and frontend workspace configurations for dependencies and environment setup.
"""


code_generation_orchestrator = CodeGenerationOrchestrator()
