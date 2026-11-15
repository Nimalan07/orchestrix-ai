from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.file_artifact import FileArtifact


def get_artifacts_by_project_id(db: Session, project_id: str) -> List[FileArtifact]:
    """Retrieve all file artifacts generated for a project."""
    stmt = (
        select(FileArtifact)
        .where(FileArtifact.project_id == project_id)
        .order_by(FileArtifact.file_path.asc())
    )
    return list(db.scalars(stmt).all())


def get_artifact_by_path(
    db: Session, project_id: str, file_path: str
) -> Optional[FileArtifact]:
    """Retrieve a specific file artifact by project ID and relative path."""
    stmt = select(FileArtifact).where(
        FileArtifact.project_id == project_id,
        FileArtifact.file_path == file_path,
    )
    return db.scalar(stmt)


def save_file_artifact(
    db: Session,
    project_id: str,
    file_path: str,
    file_hash: str,
    agent: str,
    task_id: Optional[str] = None,
) -> FileArtifact:
    """
    Insert or update a tracked file artifact.
    If the file path already exists for the project, increments version.
    """
    existing = get_artifact_by_path(db, project_id, file_path)

    if existing:
        existing.file_hash = file_hash
        existing.version += 1
        existing.generated_by_agent = agent
        if task_id:
            existing.task_id = task_id
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_artifact = FileArtifact(
            project_id=project_id,
            task_id=task_id,
            file_path=file_path,
            file_hash=file_hash,
            version=1,
            generated_by_agent=agent,
        )
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)
        return new_artifact
