from fastapi import (
    APIRouter, Depends, HTTPException, Query, Response, status
)
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse
)
from app.services.project_service import (
    create_project as create_project_service,
    get_project,
    get_all_projects,
    update_project,
    delete_project
)

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
