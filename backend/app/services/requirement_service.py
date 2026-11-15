from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.requirement import Requirement
from app.schemas.requirement import RequirementSpecification


def get_requirement_by_project_id(db: Session, project_id: str) -> Optional[Requirement]:
    """Retrieve existing requirement specification for a project."""
    stmt = select(Requirement).where(Requirement.project_id == project_id)
    return db.scalar(stmt)


def save_requirement(
    db: Session, project_id: str, specification: RequirementSpecification
) -> Requirement:
    """Insert or update requirement specification for a project."""
    req = get_requirement_by_project_id(db, project_id)
    spec_dict = specification.model_dump()

    if req:
        req.specification = spec_dict
    else:
        req = Requirement(project_id=project_id, specification=spec_dict)
        db.add(req)

    db.commit()
    db.refresh(req)
    return req
