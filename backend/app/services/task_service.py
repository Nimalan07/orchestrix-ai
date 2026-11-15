from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskResponse, TaskPlan


def get_tasks_by_project_id(db: Session, project_id: str) -> List[Task]:
    """Retrieve all tasks for a project ordered by execution order."""
    stmt = (
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.execution_order.asc())
    )
    return list(db.scalars(stmt).all())


def save_task_plan(
    db: Session, project_id: str, ordered_tasks: List[Dict[str, Any]]
) -> List[Task]:
    """
    Persist ordered DAG tasks for a project.
    Cleans up any previous tasks for the project and inserts the new plan.
    """
    # Delete existing tasks for clean replacement
    db.execute(delete(Task).where(Task.project_id == project_id))

    task_objects = []
    for t in ordered_tasks:
        task_obj = Task(
            project_id=project_id,
            task_key=t["task_key"],
            title=t["title"],
            description=t["description"],
            assigned_agent=t["assigned_agent"],
            status="pending",
            dependencies=t.get("dependencies", []) or [],
            execution_order=t.get("execution_order", 0),
            tier=t.get("tier", 0),
        )
        task_objects.append(task_obj)
        db.add(task_obj)

    db.commit()
    for obj in task_objects:
        db.refresh(obj)

    return task_objects


def update_task_status(
    db: Session, task_id: str, status: str
) -> Optional[Task]:
    """Update execution status for a specific task."""
    stmt = select(Task).where(Task.id == task_id)
    task = db.scalar(stmt)
    if task:
        task.status = status
        db.commit()
        db.refresh(task)
    return task


def build_task_plan_response(project_id: str, tasks: List[Task]) -> TaskPlan:
    """Build a structured TaskPlan response including parallel batches."""
    batches_dict: Dict[int, List[str]] = defaultdict(list)
    task_responses = []

    for t in tasks:
        batches_dict[t.tier].append(t.task_key)
        task_responses.append(TaskResponse.model_validate(t))

    sorted_tiers = sorted(batches_dict.keys())
    parallel_batches = [batches_dict[tier] for tier in sorted_tiers]

    return TaskPlan(
        project_id=project_id,
        total_tasks=len(tasks),
        total_tiers=len(parallel_batches),
        parallel_batches=parallel_batches,
        tasks=task_responses,
    )
