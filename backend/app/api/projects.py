from typing import Optional, List
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
from app.schemas.architecture import (
    SystemArchitecture,
    ArchitectureResponse,
)
from app.schemas.task import (
    TaskResponse,
    TaskPlan,
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
from app.services.architecture_service import (
    get_architecture_by_project_id,
    save_architecture,
)
from app.services.task_service import (
    get_tasks_by_project_id,
    save_task_plan,
    build_task_plan_response,
)
from app.agents.requirement_analyzer import requirement_analyzer_agent
from app.agents.architect import architect_agent
from app.agents.planner import planner_agent

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


# ANALYZE REQUIREMENTS (Requirement Analyzer Agent)
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

        # Update status to analyzed
        update_project(db, project, ProjectUpdate(status="analyzed"))

        return RequirementAnalysisResponse(
            project_id=project.id,
            status="analyzed",
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


# ARCHITECT SYSTEM (Architect Agent)
@router.post(
    "/{project_id}/architect",
    response_model=ArchitectureResponse,
    status_code=status.HTTP_200_OK
)
async def architect_project_system(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    req_record = get_requirement_by_project_id(db, project_id)
    if req_record is None:
        raise HTTPException(
            status_code=400,
            detail="Project requirements must be analyzed before architecting the system."
        )

    requirements = RequirementSpecification.model_validate(req_record.specification)

    # Transition status to architecting
    update_project(db, project, ProjectUpdate(status="architecting"))

    try:
        architecture = await architect_agent.design(
            project_name=project.name,
            requirements=requirements,
        )

        # Save architecture in database
        save_architecture(db, project.id, architecture)

        # Update status to architected
        update_project(db, project, ProjectUpdate(status="architected"))

        return ArchitectureResponse(
            project_id=project.id,
            status="architected",
            architecture=architecture
        )
    except Exception as exc:
        update_project(db, project, ProjectUpdate(status="failed"))
        raise HTTPException(
            status_code=500,
            detail=f"System architecture generation failed: {str(exc)}"
        )


# GET PROJECT ARCHITECTURE
@router.get(
    "/{project_id}/architecture",
    response_model=SystemArchitecture
)
def get_project_architecture(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    arch = get_architecture_by_project_id(db, project_id)
    if arch is None:
        raise HTTPException(
            status_code=404,
            detail="Architecture has not been generated yet for this project"
        )

    return SystemArchitecture.model_validate(arch.specification)


# PLAN TASKS (Planner Agent + DAG Engine)
@router.post(
    "/{project_id}/plan",
    response_model=TaskPlan,
    status_code=status.HTTP_200_OK
)
async def plan_project_tasks(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    req_record = get_requirement_by_project_id(db, project_id)
    if req_record is None:
        raise HTTPException(
            status_code=400,
            detail="Requirements must be analyzed before planning."
        )

    arch_record = get_architecture_by_project_id(db, project_id)
    if arch_record is None:
        raise HTTPException(
            status_code=400,
            detail="System architecture must be generated before planning tasks."
        )

    requirements = RequirementSpecification.model_validate(req_record.specification)
    architecture = SystemArchitecture.model_validate(arch_record.specification)

    # Transition status to planning
    update_project(db, project, ProjectUpdate(status="planning"))

    try:
        ordered_tasks, parallel_batches = await planner_agent.plan(
            project_name=project.name,
            requirements=requirements,
            architecture=architecture,
        )

        # Persist tasks in database
        saved_tasks = save_task_plan(db, project.id, ordered_tasks)

        # Transition status to planned
        update_project(db, project, ProjectUpdate(status="planned"))

        return build_task_plan_response(project.id, saved_tasks)
    except Exception as exc:
        update_project(db, project, ProjectUpdate(status="failed"))
        raise HTTPException(
            status_code=500,
            detail=f"Task planning and DAG verification failed: {str(exc)}"
        )


# GET TASKS LIST
@router.get(
    "/{project_id}/tasks",
    response_model=List[TaskResponse]
)
def list_project_tasks(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    tasks = get_tasks_by_project_id(db, project_id)
    return [TaskResponse.model_validate(t) for t in tasks]


# GET TASK DAG / BATCHES
@router.get(
    "/{project_id}/tasks/dag",
    response_model=TaskPlan
)
def get_project_task_dag(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    tasks = get_tasks_by_project_id(db, project_id)
    if not tasks:
        raise HTTPException(
            status_code=404,
            detail="No tasks planned yet for this project"
        )

    return build_task_plan_response(project.id, tasks)
