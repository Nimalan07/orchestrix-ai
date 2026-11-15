"""
Pydantic schemas for the Testing Agent and execution reports.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TestCaseResult(BaseModel):
    """Result of an individual test case."""
    __test__ = False
    test_name: str
    status: str = Field(..., description="passed, failed, error, skipped")
    duration: float = Field(default=0.0)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None


class TestRunReport(BaseModel):
    """Consolidated test suite execution report."""
    __test__ = False
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration_seconds: float = 0.0
    all_passed: bool = False
    sandbox_mode: str = "local_process"
    failures: List[TestCaseResult] = Field(default_factory=list)
    raw_output: str = ""
