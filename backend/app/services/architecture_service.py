from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.architecture import Architecture
from app.schemas.architecture import SystemArchitecture


def get_architecture_by_project_id(db: Session, project_id: str) -> Optional[Architecture]:
    """Retrieve existing architecture specification for a project."""
    stmt = select(Architecture).where(Architecture.project_id == project_id)
    return db.scalar(stmt)


def save_architecture(
    db: Session, project_id: str, architecture: SystemArchitecture
) -> Architecture:
    """Insert or update system architecture for a project."""
    arch = get_architecture_by_project_id(db, project_id)
    spec_dict = architecture.model_dump()

    if arch:
        arch.specification = spec_dict
    else:
        arch = Architecture(project_id=project_id, specification=spec_dict)
        db.add(arch)

    db.commit()
    db.refresh(arch)
    return arch
