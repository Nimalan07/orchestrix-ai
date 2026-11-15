"""
Unit tests for Orchestrix Sandbox Execution Engine.
"""

import sys
import pytest
from pathlib import Path
from app.sandbox.process_manager import process_sandbox
from app.sandbox.docker_manager import docker_sandbox
from app.sandbox.runner import sandbox_runner


def test_process_sandbox_availability():
    assert process_sandbox.is_available() is True


def test_docker_sandbox_availability_check():
    # Calling is_available should not throw unhandled exceptions even if docker is stopped
    available = docker_sandbox.is_available()
    assert isinstance(available, bool)


def test_process_sandbox_execute_command(tmp_path):
    res = process_sandbox.execute_command(
        cmd=[sys.executable, "-c", "print('Orchestrix Sandbox Active')"],
        workdir=tmp_path,
        timeout=10.0,
    )

    assert res.exit_code == 0
    assert "Orchestrix Sandbox Active" in res.stdout
    assert res.timed_out is False
    assert res.sandbox_mode == "local_process"
    assert res.duration_seconds >= 0.0


def test_process_sandbox_timeout_handling(tmp_path):
    # Command sleeping longer than 1.0 second timeout
    res = process_sandbox.execute_command(
        cmd=[sys.executable, "-c", "import time; time.sleep(5)"],
        workdir=tmp_path,
        timeout=1.0,
    )

    assert res.timed_out is True
    assert res.exit_code == -1
    assert "timed out after 1.0 seconds" in res.stderr


def test_sandbox_runner_fallback(tmp_path):
    # With mode auto and docker potentially stopped, sandbox_runner falls back safely
    res = sandbox_runner.run_command(
        project_slug="student-management-platform",
        cmd=[sys.executable, "-c", "print('Runner Ok')"],
        timeout=10.0,
    )

    assert res.exit_code == 0
    assert "Runner Ok" in res.stdout
