"""
REST API Endpoints for Sandboxed Execution and Self-Healing Loops.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.project_service import get_project
from app.services.workspace_service import workspace_service
from app.services.execution_service import (
    create_execution_run,
    update_execution_run,
    get_execution_run_by_id,
    get_execution_runs_by_project,
)
from app.orchestrator.code_orchestrator import code_generation_orchestrator
from app.orchestrator.self_healing import self_healing_engine
from app.agents.testing_agent import testing_agent
from app.schemas.execution import ExecuteProjectRequest, ExecutionRunResponse

router = APIRouter(prefix="/api/projects", tags=["Execution & Sandbox"])


@router.post(
    "/{project_id}/execute",
    response_model=ExecutionRunResponse,
    status_code=status.HTTP_200_OK,
)
async def execute_and_heal_project(
    project_id: str,
    payload: ExecuteProjectRequest = ExecuteProjectRequest(),
    db: Session = Depends(get_db),
):
    """
    Execute tests against the generated project inside an isolated sandbox,
    triggering the autonomous debugger and self-healing loop on any failures.
    """
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    # 1. Ensure scaffolding is present
    code_generation_orchestrator.ensure_project_scaffolding(db, project)

    # 2. Ensure automated tests exist and are valid
    workspace_dir = workspace_service.get_workspace_dir(project.name)
    test_file = workspace_dir / "backend" / "tests" / "test_api.py"
    valid_tests = False
    if test_file.exists():
        try:
            content = test_file.read_text(encoding="utf-8")
            if "def test_" in content:
                valid_tests = True
        except Exception:
            valid_tests = False

    if not valid_tests:
        default_tests = testing_agent.generate_default_tests(project.name, existing_files)
        for t in default_tests:
            workspace_service.write_file(
                project_slug=project.name,
                relative_path=t["file_path"],
                content=t["content"],
                overwrite=True,
            )

    # 3. Create execution run in db
    run_record = create_execution_run(
        db=db,
        project_id=project.id,
        run_type="heal",
        sandbox_mode=payload.sandbox_mode,
    )

    try:
        # 4. Run Self-Healing Engine
        heal_result = await self_healing_engine.execute_loop(
            db=db,
            project=project,
            max_iterations=payload.max_iterations,
        )

        final_rep = heal_result.final_report
        updated_run = update_execution_run(
            db=db,
            run_id=run_record.id,
            status=heal_result.status,
            total_tests=final_rep.total,
            passed_tests=final_rep.passed,
            failed_tests=final_rep.failed,
            iterations=heal_result.iterations_run,
            duration_seconds=final_rep.duration_seconds,
            stdout=final_rep.raw_output,
            stderr="",
            diagnostic_report={
                "status": heal_result.status,
                "iterations_run": heal_result.iterations_run,
                "fixes_count": len(heal_result.fixes_applied),
                "history": heal_result.iteration_history,
            },
        )
        return updated_run

    except Exception as exc:
        update_execution_run(
            db=db,
            run_id=run_record.id,
            status="error",
            stderr=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {exc}",
        )


@router.get(
    "/{project_id}/runs",
    response_model=List[ExecutionRunResponse],
)
def list_execution_runs(
    project_id: str,
    db: Session = Depends(get_db),
):
    """List execution history for a given project."""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_execution_runs_by_project(db, project_id)


@router.get(
    "/{project_id}/runs/{run_id}",
    response_model=ExecutionRunResponse,
)
def get_execution_run_detail(
    project_id: str,
    run_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve details and diagnostic report for an execution run."""
    run = get_execution_run_by_id(db, run_id)
    if not run or run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution run '{run_id}' not found for project '{project_id}'.",
        )
    return run
