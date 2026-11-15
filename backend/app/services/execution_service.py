"""
Service layer for ExecutionRun persistence and querying.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.execution import ExecutionRun


def create_execution_run(
    db: Session,
    project_id: str,
    run_type: str = "test",
    sandbox_mode: str = "local_process",
) -> ExecutionRun:
    """Create a new pending execution run."""
    run = ExecutionRun(
        project_id=project_id,
        run_type=run_type,
        sandbox_mode=sandbox_mode,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def update_execution_run(
    db: Session,
    run_id: str,
    status: str,
    total_tests: int = 0,
    passed_tests: int = 0,
    failed_tests: int = 0,
    iterations: int = 0,
    duration_seconds: float = 0.0,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    diagnostic_report: Optional[Dict[str, Any]] = None,
) -> Optional[ExecutionRun]:
    """Update execution run with final test report and output metrics."""
    run = db.query(ExecutionRun).filter(ExecutionRun.id == run_id).first()
    if not run:
        return None

    run.status = status
    run.total_tests = total_tests
    run.passed_tests = passed_tests
    run.failed_tests = failed_tests
    run.iterations = iterations
    run.duration_seconds = duration_seconds
    run.stdout = stdout
    run.stderr = stderr
    run.diagnostic_report = diagnostic_report
    run.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(run)
    return run


def get_execution_run_by_id(db: Session, run_id: str) -> Optional[ExecutionRun]:
    """Retrieve an execution run by ID."""
    return db.query(ExecutionRun).filter(ExecutionRun.id == run_id).first()


def get_execution_runs_by_project(
    db: Session,
    project_id: str,
    limit: int = 50,
) -> List[ExecutionRun]:
    """Retrieve execution history for a project ordered newest first."""
    return (
        db.query(ExecutionRun)
        .filter(ExecutionRun.project_id == project_id)
        .order_by(ExecutionRun.created_at.desc())
        .limit(limit)
        .all()
    )
