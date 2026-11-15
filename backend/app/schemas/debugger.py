"""
Pydantic schemas for the Autonomous Debugger Agent and Self-Healing Engine.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.testing import TestRunReport


class CodeFix(BaseModel):
    """Specific code correction proposed by Debugger Agent."""
    file_path: str = Field(..., description="Relative path of file to update")
    explanation: str = Field(..., description="Explanation of bug and rationale for fix")
    replacement_content: str = Field(..., description="Full corrected content of the file")


class DebugAnalysis(BaseModel):
    """Root cause diagnosis and proposed fixes."""
    root_cause: str = Field(..., description="Identified root cause of test failure")
    files_to_fix: List[CodeFix] = Field(default_factory=list)


class SelfHealingResult(BaseModel):
    """Outcome of the multi-iteration self-healing loop."""
    project_name: str
    status: str = Field(..., description="'passed', 'healed', or 'failed'")
    iterations_run: int = 0
    max_iterations: int = 3
    final_report: TestRunReport
    fixes_applied: List[CodeFix] = Field(default_factory=list)
    iteration_history: List[Dict[str, Any]] = Field(default_factory=list)
