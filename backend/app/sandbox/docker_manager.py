"""
Docker Sandbox Manager for Orchestrix.
Executes test suites and builds inside isolated, resource-constrained containers.
"""

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from app.sandbox.base import BaseSandbox, ExecutionResult

logger = logging.getLogger(__name__)


class DockerSandbox(BaseSandbox):
    """
    Runs tasks inside lightweight Docker containers with strict CPU,
    memory, and execution timeout boundaries.
    """

    def __init__(self, default_image: str = "python:3.13-slim"):
        self.default_image = default_image
        self._docker_path = shutil.which("docker")

    def is_available(self) -> bool:
        """Check if Docker CLI exists and daemon is actively responding."""
        if not self._docker_path:
            return False
        try:
            res = subprocess.run(
                [self._docker_path, "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5.0,
            )
            return res.returncode == 0
        except Exception:
            return False

    def execute_command(
        self,
        cmd: List[str],
        workdir: Path,
        timeout: float = 60.0,
        env: Optional[Dict[str, str]] = None,
        image: Optional[str] = None,
    ) -> ExecutionResult:
        """
        Execute command inside an isolated container mounting the project workspace.
        """
        if not self.is_available():
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr="Docker daemon is not reachable on this host.",
                duration_seconds=0.0,
                timed_out=False,
                sandbox_mode="docker",
                command=" ".join(cmd),
            )

        target_image = image or self.default_image
        abs_workdir = str(workdir.resolve())

        # Construct isolated docker run command
        docker_cmd = [
            self._docker_path,
            "run",
            "--rm",
            "--memory=512m",
            "--cpus=1.0",
            "-v",
            f"{abs_workdir}:/workspace",
            "-w",
            "/workspace",
        ]

        if env:
            for k, v in env.items():
                docker_cmd.extend(["-e", f"{k}={v}"])

        docker_cmd.append(target_image)
        docker_cmd.extend(cmd)

        start_time = time.time()
        timed_out = False

        try:
            proc = subprocess.run(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            duration = round(time.time() - start_time, 3)
            return ExecutionResult(
                exit_code=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                duration_seconds=duration,
                timed_out=False,
                sandbox_mode="docker",
                command=" ".join(cmd),
            )
        except subprocess.TimeoutExpired as exc:
            duration = round(time.time() - start_time, 3)
            return ExecutionResult(
                exit_code=-1,
                stdout=(exc.stdout or "").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
                stderr=f"Execution timed out after {timeout} seconds.",
                duration_seconds=duration,
                timed_out=True,
                sandbox_mode="docker",
                command=" ".join(cmd),
            )
        except Exception as exc:
            duration = round(time.time() - start_time, 3)
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr=f"Docker container execution error: {exc}",
                duration_seconds=duration,
                timed_out=False,
                sandbox_mode="docker",
                command=" ".join(cmd),
            )


docker_sandbox = DockerSandbox()
