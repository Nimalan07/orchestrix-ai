"""
Unified Sandbox Runner for Orchestrix.
Orchestrates transparent execution across Docker containers or isolated local processes.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from app.sandbox.base import ExecutionResult
from app.sandbox.docker_manager import docker_sandbox
from app.sandbox.process_manager import process_sandbox
from app.services.workspace_service import workspace_service

logger = logging.getLogger(__name__)


class SandboxRunner:
    """
    Coordinates execution requests across Docker and Local Process sandboxes.
    Automatically detects Docker daemon health and gracefully falls back to local sandbox.
    """

    def __init__(self, mode: str = "auto"):
        self.mode = mode

    def get_preferred_sandbox(self):
        """Select execution sandbox based on mode configuration and runtime availability."""
        if self.mode == "docker":
            return docker_sandbox
        if self.mode == "local_process":
            return process_sandbox

        # Mode == "auto"
        if docker_sandbox.is_available():
            logger.info("Docker daemon detected. Using Docker Sandbox.")
            return docker_sandbox

        logger.info("Docker daemon not reachable. Using Local Process Sandbox.")
        return process_sandbox

    def run_tests(
        self,
        project_slug: str,
        test_dir: str = "backend",
        timeout: float = 60.0,
    ) -> ExecutionResult:
        """
        Execute pytest inside the backend workspace of the generated project.
        """
        workspace_dir = workspace_service.get_workspace_dir(project_slug)
        target_dir = workspace_dir / test_dir
        if not target_dir.exists():
            target_dir = workspace_dir

        target_abs = str(target_dir.resolve())
        parent_abs = str(target_dir.parent.resolve())
        combined_pythonpath = f"{target_abs}{os.pathsep}{parent_abs}"

        # Resolve virtualenv Python interpreter if available
        py_exe = sys.executable
        possible_venvs = [
            workspace_dir.parent.parent / "backend" / "venv" / "Scripts" / "python.exe",
            workspace_dir.parent.parent / "venv" / "Scripts" / "python.exe",
            Path(sys.executable),
        ]
        for v in possible_venvs:
            if v.exists():
                py_exe = str(v.resolve())
                break

        cmd = [
            py_exe,
            "-m",
            "pytest",
            "-v",
            "-o",
            f"rootdir={target_abs}",
        ]
        ini_file = target_dir / "pytest.ini"
        if ini_file.exists():
            cmd.extend(["-c", str(ini_file.resolve())])

        sandbox = self.get_preferred_sandbox()
        return sandbox.execute_command(
            cmd=cmd,
            workdir=target_dir,
            timeout=timeout,
            env={"PYTHONPATH": combined_pythonpath},
        )

    def run_command(
        self,
        project_slug: str,
        cmd: List[str],
        subfolder: str = "",
        timeout: float = 60.0,
        env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Execute arbitrary command in isolated project workspace.
        """
        workspace_dir = workspace_service.get_workspace_dir(project_slug)
        workdir = workspace_dir / subfolder if subfolder else workspace_dir
        sandbox = self.get_preferred_sandbox()
        return sandbox.execute_command(
            cmd=cmd,
            workdir=workdir,
            timeout=timeout,
            env=env,
        )


sandbox_runner = SandboxRunner()
