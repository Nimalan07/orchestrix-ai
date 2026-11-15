"""
Unit and integration tests for Debugger Agent and Autonomous Self-Healing Engine.
"""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.testing import TestRunReport, TestCaseResult
from app.schemas.debugger import DebugAnalysis, CodeFix
from app.agents.debugger import debugger_agent
from app.orchestrator.self_healing import self_healing_engine
from app.services.workspace_service import workspace_service


@pytest.fixture
def mock_project(db: Session):
    proj = Project(
        name="Self Heal Test Platform",
        description="Project to verify self healing loop",
        status="generated",
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@pytest.mark.asyncio
async def test_debugger_diagnose_and_repair_mocked():
    report = TestRunReport(
        total=1,
        passed=0,
        failed=1,
        all_passed=False,
        raw_output="AssertionError: Expected 200, got 500",
    )
    mock_llm_response = {
        "root_cause": "Unhandled exception in endpoint",
        "files_to_fix": [
            {
                "file_path": "backend/app/main.py",
                "explanation": "Fix error handling",
                "replacement_content": "# corrected code",
            }
        ],
    }

    with patch("app.services.llm_service.llm_service.generate_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_response

        analysis = await debugger_agent.diagnose_and_repair(
            project_name="Test Project",
            test_report=report,
            file_contexts={"backend/app/main.py": "broken code"},
        )

        assert analysis.root_cause == "Unhandled exception in endpoint"
        assert len(analysis.files_to_fix) == 1
        assert analysis.files_to_fix[0].file_path == "backend/app/main.py"
        assert analysis.files_to_fix[0].replacement_content == "# corrected code"


@pytest.mark.asyncio
async def test_self_healing_loop_already_passing(db: Session, mock_project: Project):
    # If tests pass on attempt 0, no debugger is invoked
    passing_report = TestRunReport(
        total=2,
        passed=2,
        failed=0,
        all_passed=True,
        raw_output="2 passed in 0.1s",
    )

    with patch("app.agents.testing_agent.testing_agent.execute_tests", return_value=passing_report):
        result = await self_healing_engine.execute_loop(db=db, project=mock_project, max_iterations=3)

        assert result.status == "passed"
        assert result.iterations_run == 0
        assert result.final_report.all_passed is True
        assert len(result.fixes_applied) == 0


@pytest.mark.asyncio
async def test_self_healing_loop_repairs_failure(db: Session, mock_project: Project):
    # First run fails, second run passes after fix
    failing_report = TestRunReport(
        total=2,
        passed=1,
        failed=1,
        all_passed=False,
        raw_output="1 failed, 1 passed",
    )
    healed_report = TestRunReport(
        total=2,
        passed=2,
        failed=0,
        all_passed=True,
        raw_output="2 passed in 0.2s",
    )

    mock_analysis = DebugAnalysis(
        root_cause="Typo in response dictionary",
        files_to_fix=[
            CodeFix(
                file_path="backend/app/main.py",
                explanation="Fix status key",
                replacement_content="corrected content",
            )
        ],
    )

    with patch("app.agents.testing_agent.testing_agent.execute_tests", side_effect=[failing_report, healed_report]), \
         patch("app.agents.debugger.debugger_agent.diagnose_and_repair", new_callable=AsyncMock, return_value=mock_analysis), \
         patch("app.services.workspace_service.workspace_service.write_file", return_value={"relative_path": "backend/app/main.py", "sha256": "abc123hash"}):

        result = await self_healing_engine.execute_loop(db=db, project=mock_project, max_iterations=3)

        assert result.status == "healed"
        assert result.iterations_run == 1
        assert result.final_report.all_passed is True
        assert len(result.fixes_applied) == 1
        assert result.fixes_applied[0].file_path == "backend/app/main.py"
