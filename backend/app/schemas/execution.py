"""
Pydantic schemas for Execution REST API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExecuteProjectRequest(BaseModel):
    """Payload for triggering project execution and self-healing test loop."""
    max_iterations: int = Field(default=3, ge=1, le=5, description="Maximum self-healing attempts")
    sandbox_mode: str = Field(default="auto", description="'auto', 'docker', or 'local_process'")


class ExecutionRunResponse(BaseModel):
    """Response schema representing an execution run record."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    run_type: str
    sandbox_mode: str
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    iterations: int
    duration_seconds: float
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    diagnostic_report: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
