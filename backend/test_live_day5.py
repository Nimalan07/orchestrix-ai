import asyncio
from pathlib import Path
from app.database.session import SessionLocal
from app.models.project import Project
from app.models.task import Task
from app.models.file_artifact import FileArtifact
from app.orchestrator.code_orchestrator import code_generation_orchestrator
from app.services.workspace_service import workspace_service


async def main():
    db = SessionLocal()
    try:
        # Load planned project
        project = (
            db.query(Project)
            .filter(Project.name == "Student Management Platform")
            .order_by(Project.created_at.desc())
            .first()
        )
        if not project:
            print("Project not found.")
            return

        print(f"Loaded Planned Project: '{project.name}' (ID: {project.id}, Status: {project.status})")
        tasks = db.query(Task).filter(Task.project_id == project.id).order_by(Task.execution_order.asc()).all()
        print(f"Found {len(tasks)} tasks in execution queue.")

        print("\n--- [Starting Multi-Agent Code Generation with Ollama qwen2.5-coder:7b] ---")
        manifest = await code_generation_orchestrator.generate_project(
            db=db,
            project=project,
        )

        print("\n=== CODE GENERATION COMPLETE ===")
        print(f"Workspace Directory: {manifest.workspace_directory}")
        print(f"Total Files Generated: {manifest.total_files}")

        print("\nGenerated Workspace Files:")
        for f in manifest.files:
            print(f"  + {f['relative_path']} ({f['size_bytes']} bytes, SHA-256: {f['sha256'][:10]}...)")

        # Verify on filesystem directly
        workspace_path = Path(manifest.workspace_directory)
        assert workspace_path.exists(), "Workspace directory must exist on disk"
        readme_path = workspace_path / "README.md"
        assert readme_path.exists(), "README.md must exist on disk"
        manifest_path = workspace_path / "generation_manifest.json"
        assert manifest_path.exists(), "generation_manifest.json must exist on disk"

        # Verify database artifacts
        db_artifacts = db.query(FileArtifact).filter(FileArtifact.project_id == project.id).all()
        print(f"\nTracked Database FileArtifacts in PostgreSQL: {len(db_artifacts)}")
        for art in db_artifacts:
            print(f"  [Artifact] {art.file_path} (v{art.version}, by {art.generated_by_agent})")

        # Verify task completion
        completed_tasks = db.query(Task).filter(Task.project_id == project.id, Task.status == "completed").count()
        print(f"Completed Tasks: {completed_tasks}/{len(tasks)}")
        print(f"Project status is now: '{project.status}'")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
