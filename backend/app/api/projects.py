from typing import Optional
from fastapi import (
    APIRouter, Depends, HTTPException, Query, Response, status, Body
)
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse
)
from app.schemas.requirement import (
    RequirementSpecification,
    RequirementAnalysisResponse,
)
from app.services.project_service import (
    create_project as create_project_service,
    get_project,
    get_all_projects,
    update_project,
    delete_project
)
from app.services.requirement_service import (
    get_requirement_by_project_id,
    save_requirement,
)
from app.agents.requirement_analyzer import requirement_analyzer_agent

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


# CREATE PROJECT
@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_project(
    data: ProjectCreate,
    db: Session = Depends(get_db)
):
    return create_project_service(db, data)


# GET ALL PROJECTS
@router.get(
    "",
    response_model=list[ProjectResponse]
)
def list_projects(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    return get_all_projects(db, limit, offset)


# GET PROJECT BY ID
@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def retrieve_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    return project


# UPDATE PROJECT
@router.patch(
    "/{project_id}",
    response_model=ProjectResponse
)
def modify_project(
    project_id: str,
    data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    return update_project(db, project, data)


# DELETE PROJECT
@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    delete_project(db, project)
    return Response(status_code=204)


# ANALYZE REQUIREMENTS (AI Agent)
@router.post(
    "/{project_id}/analyze",
    response_model=RequirementAnalysisResponse,
    status_code=status.HTTP_200_OK
)
async def analyze_project_requirements(
    project_id: str,
    additional_context: Optional[str] = Body(
        default=None,
        embed=True,
        description="Optional additional instructions or context"
    ),
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Transition status to analyzing
    update_project(db, project, ProjectUpdate(status="analyzing"))

    try:
        specification = await requirement_analyzer_agent.analyze(
            project_name=project.name,
            project_description=project.description,
            additional_context=additional_context,
        )

        # Save requirement specification in database
        save_requirement(db, project.id, specification)

        # Update status to planning (ready for planner & architect)
        update_project(db, project, ProjectUpdate(status="planning"))

        return RequirementAnalysisResponse(
            project_id=project.id,
            status="planning",
            specification=specification
        )
    except Exception as exc:
        update_project(db, project, ProjectUpdate(status="failed"))
        raise HTTPException(
            status_code=500,
            detail=f"Requirement analysis failed: {str(exc)}"
        )


# GET PROJECT REQUIREMENTS
@router.get(
    "/{project_id}/requirements",
    response_model=RequirementSpecification
)
def get_project_requirements(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    req = get_requirement_by_project_id(db, project_id)
    if req is None:
        raise HTTPException(
            status_code=404,
            detail="Requirements have not been analyzed yet for this project"
        )

    return RequirementSpecification.model_validate(req.specification)
