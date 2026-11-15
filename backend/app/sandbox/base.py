"""
Base interfaces and data schemas for Orchestrix Sandboxed Execution Engine.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Encapsulates the output and performance metrics of a sandboxed execution."""
    exit_code: int = Field(..., description="Process exit code (0 indicates success)")
    stdout: str = Field(default="", description="Captured standard output")
    stderr: str = Field(default="", description="Captured standard error")
    duration_seconds: float = Field(default=0.0, description="Execution duration in seconds")
    timed_out: bool = Field(default=False, description="True if command exceeded time limit")
    sandbox_mode: str = Field(..., description="Engine mode used: 'docker' or 'local_process'")
    command: str = Field(default="", description="Command string executed")


class BaseSandbox(ABC):
    """Abstract interface for code execution environments."""

    @abstractmethod
    def is_available(self) -> bool:
        """Verify whether this execution engine is reachable and usable."""
        pass

    @abstractmethod
    def execute_command(
        self,
        cmd: List[str],
        workdir: Path,
        timeout: float = 60.0,
        env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """Execute command in sandbox and return ExecutionResult."""
        pass
