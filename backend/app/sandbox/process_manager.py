"""
Local Process Sandbox Manager for Orchestrix.
Provides isolated, timeout-bounded process execution when Docker is unavailable or for rapid local testing.
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from app.sandbox.base import BaseSandbox, ExecutionResult

logger = logging.getLogger(__name__)


class ProcessSandbox(BaseSandbox):
    """
    Executes commands as isolated child processes with sandboxed working directories,
    sanitized environments, and strict timeouts.
    """

    def is_available(self) -> bool:
        """Local process execution is always available in supported environments."""
        return True

    def execute_command(
        self,
        cmd: List[str],
        workdir: Path,
        timeout: float = 60.0,
        env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Execute command with workdir set strictly to the project directory.
        """
        abs_workdir = workdir.resolve()
        if not abs_workdir.exists():
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr=f"Working directory does not exist: {abs_workdir}",
                duration_seconds=0.0,
                timed_out=False,
                sandbox_mode="local_process",
                command=" ".join(cmd),
            )

        # Build clean environment
        clean_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "TEMP": os.environ.get("TEMP", "C:\\Temp"),
            "TMP": os.environ.get("TMP", "C:\\Temp"),
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": f"{abs_workdir}{os.pathsep}{abs_workdir.parent}",
        }

        # Inherit virtualenv path if available
        venv_bin = Path(sys.executable).parent
        if venv_bin.exists():
            clean_env["PATH"] = f"{venv_bin}{os.pathsep}{clean_env['PATH']}"

        if env:
            clean_env.update(env)

        start_time = time.time()
        timed_out = False

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(abs_workdir),
                env=clean_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                shell=False,
            )
            duration = round(time.time() - start_time, 3)
            return ExecutionResult(
                exit_code=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                duration_seconds=duration,
                timed_out=False,
                sandbox_mode="local_process",
                command=" ".join(cmd),
            )
        except subprocess.TimeoutExpired as exc:
            duration = round(time.time() - start_time, 3)
            out = exc.stdout if isinstance(exc.stdout, str) else ((exc.stdout or b"").decode("utf-8", errors="replace"))
            err = exc.stderr if isinstance(exc.stderr, str) else ((exc.stderr or b"").decode("utf-8", errors="replace"))
            return ExecutionResult(
                exit_code=-1,
                stdout=out or "",
                stderr=f"{err}\nExecution timed out after {timeout} seconds.",
                duration_seconds=duration,
                timed_out=True,
                sandbox_mode="local_process",
                command=" ".join(cmd),
            )
        except Exception as exc:
            duration = round(time.time() - start_time, 3)
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr=f"Process execution failed: {exc}",
                duration_seconds=duration,
                timed_out=False,
                sandbox_mode="local_process",
                command=" ".join(cmd),
            )


process_sandbox = ProcessSandbox()
