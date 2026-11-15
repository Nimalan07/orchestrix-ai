"""
Testing Agent for Orchestrix.
Generates automated test suites, executes them in isolated sandboxes, and parses failure diagnostics.
"""

import json
import logging
import re
from typing import Dict, List, Optional
from app.services.llm_service import llm_service
from app.sandbox.runner import sandbox_runner
from app.schemas.architecture import SystemArchitecture
from app.schemas.testing import TestCaseResult, TestRunReport
from app.prompts.testing_prompts import TESTING_AGENT_SYSTEM_PROMPT, TEST_GENERATION_USER_PROMPT

logger = logging.getLogger(__name__)


class TestingAgent:
    """
    Automated QA and Testing Agent.
    Creates pytest test suites, runs them in sandboxed environments,
    and extracts structured test reports.
    """

    async def generate_tests(
        self,
        project_name: str,
        architecture: SystemArchitecture,
        existing_files: List[str],
    ) -> List[Dict[str, str]]:
        """
        Synthesize automated test suite for the project backend.
        """
        contracts_summary = json.dumps(
            [c.model_dump() for c in architecture.api_contracts], indent=2
        ) if architecture.api_contracts else "None explicitly listed."

        user_prompt = TEST_GENERATION_USER_PROMPT.format(
            project_name=project_name,
            architecture_pattern=architecture.architecture_pattern,
            backend_stack=architecture.tech_stack.backend,
            db_stack=architecture.tech_stack.database,
            api_contracts=contracts_summary,
            existing_files="\n".join(f"- {f}" for f in existing_files),
        )

        try:
            parsed = await llm_service.generate_json(
                system_prompt=TESTING_AGENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.2,
            )
            if "test_files" in parsed and isinstance(parsed["test_files"], list):
                return parsed["test_files"]
        except Exception as exc:
            logger.warning(f"LLM test generation failed or timed out: {exc}. Using deterministic test generator.")

        return self.generate_default_tests(project_name, existing_files)

    def generate_default_tests(self, project_name: str, existing_files: List[str]) -> List[Dict[str, str]]:
        """
        Deterministic fallback test generator to guarantee testability even without LLM inference.
        """
        test_content = f'''"""Automated pytest test suite for {project_name}."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {{"status": "healthy"}}
'''
        return [
            {
                "file_path": "backend/tests/test_api.py",
                "content": test_content,
            }
        ]

    def execute_tests(
        self,
        project_slug: str,
        timeout: float = 60.0,
    ) -> TestRunReport:
        """
        Run the test suite inside the sandboxed environment and parse results.
        """
        res = sandbox_runner.run_tests(project_slug=project_slug, timeout=timeout)
        return self.parse_pytest_output(
            stdout=res.stdout,
            stderr=res.stderr,
            duration=res.duration_seconds,
            exit_code=res.exit_code,
            sandbox_mode=res.sandbox_mode,
        )

    def parse_pytest_output(
        self,
        stdout: str,
        stderr: str,
        duration: float,
        exit_code: int,
        sandbox_mode: str,
    ) -> TestRunReport:
        """
        Extract structured test metrics and failure details from pytest logs.
        """
        raw_combined = f"{stdout}\n{stderr}".strip()

        passed_match = re.search(r"(\d+)\s+passed", stdout)
        failed_match = re.search(r"(\d+)\s+failed", stdout)
        errors_match = re.search(r"(\d+)\s+error", stdout)
        skipped_match = re.search(r"(\d+)\s+skipped", stdout)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(errors_match.group(1)) if errors_match else 0
        skipped = int(skipped_match.group(1)) if skipped_match else 0

        total = passed + failed + errors + skipped
        all_passed = (exit_code == 0) and (failed == 0) and (errors == 0) and (total > 0)

        # Extract failure snippets
        failures: List[TestCaseResult] = []
        failure_headers = re.findall(r"_{3,}\s+(.+?)\s+_{3,}", stdout)
        for name in failure_headers:
            clean_name = name.strip()
            failures.append(
                TestCaseResult(
                    test_name=clean_name,
                    status="failed",
                    error_message=f"Test failure detected in {clean_name}",
                    stack_trace=stdout,
                )
            )

        if exit_code != 0 and total == 0:
            # Collection failure or import error
            failures.append(
                TestCaseResult(
                    test_name="collection_or_import_error",
                    status="error",
                    error_message=stderr or stdout or "Unknown execution failure",
                    stack_trace=raw_combined,
                )
            )
            errors = 1
            total = 1

        return TestRunReport(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            duration_seconds=duration,
            all_passed=all_passed,
            sandbox_mode=sandbox_mode,
            failures=failures,
            raw_output=raw_combined,
        )


testing_agent = TestingAgent()
