import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
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

    async def execute_task_code_generation(
        self,
        project_name: str,
        task: TaskResponse,
        architecture: SystemArchitecture,
    ) -> TaskCodeOutput:
        """Route an individual task to its specialized developer agent."""
        agent = self.AGENT_MAP.get(task.assigned_agent)
        if not agent:
            # Fallback or pass for non-developer agents (e.g. tester, reviewer)
            return TaskCodeOutput(
                task_key=task.task_key,
                summary=f"Task assigned to {task.assigned_agent} will be executed in testing/verification phase.",
                files=[],
            )

        return await agent.execute_task(
            project_name=project_name,
            task=task,
            architecture=architecture,
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

                # Write generated files safely into the workspace
                for file_entry in code_output.files:
                    meta = workspace_service.write_file(
                        project_slug=project.name,
                        relative_path=file_entry.file_path,
                        content=file_entry.content,
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
