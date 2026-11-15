from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    task_key: str = Field(description="Unique task identifier, e.g. T1, T2, TASK-001")
    title: str = Field(description="Clear title of the engineering task")
    description: str = Field(description="Actionable task details and deliverables")
    assigned_agent: Literal[
        "database_engineer",
        "backend_developer",
        "frontend_developer",
        "tester",
        "reviewer",
        "debugger",
    ] = Field(description="Specialized agent responsible for this task")
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of prerequisite task_keys that must complete before this task can start",
    )
    estimated_complexity: Literal["low", "medium", "high"] = Field(default="medium")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[
        Literal["pending", "in_progress", "completed", "failed", "blocked"]
    ] = None
    error_log: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    project_id: str
    task_key: str
    title: str
    description: str
    assigned_agent: str
    status: str
    dependencies: List[str]
    execution_order: int
    tier: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskPlan(BaseModel):
    """Execution plan containing DAG-validated tasks and topological execution batches."""

    project_id: str
    total_tasks: int
    total_tiers: int
    parallel_batches: List[List[str]] = Field(
        description="Batches of task keys organized by dependency tier (can execute concurrently within a tier)"
    )
    tasks: List[TaskResponse]

    model_config = ConfigDict(from_attributes=True)


class TaskPlanLLMOutput(BaseModel):
    """Raw structured output expected from Planner Agent LLM."""

    tasks: List[TaskBase]
