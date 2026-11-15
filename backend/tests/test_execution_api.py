"""
Integration tests for Execution and Self-Healing REST API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.project import Project
from app.models.execution import ExecutionRun
from app.schemas.testing import TestRunReport
from app.schemas.debugger import SelfHealingResult


@pytest.fixture
def test_project(db: Session):
    proj = Project(
        name="API Execution Test Project",
        description="Verifying execution REST endpoints",
        status="completed",
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


def test_list_runs_empty(client, test_project: Project):
    response = client.get(f"/api/projects/{test_project.id}/runs")
    assert response.status_code == 200
    assert response.json() == []


def test_list_runs_nonexistent_project(client):
    response = client.get("/api/projects/nonexistent-id/runs")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_execute_project_endpoint(client, test_project: Project):
    mock_report = TestRunReport(
        total=2,
        passed=2,
        failed=0,
        all_passed=True,
        sandbox_mode="local_process",
        duration_seconds=0.12,
        raw_output="2 passed in 0.12s",
    )
    mock_result = SelfHealingResult(
        project_name=test_project.name,
        status="passed",
        iterations_run=0,
        max_iterations=3,
        final_report=mock_report,
        fixes_applied=[],
        iteration_history=[],
    )

    with patch("app.orchestrator.self_healing.self_healing_engine.execute_loop", new_callable=AsyncMock, return_value=mock_result), \
         patch("app.orchestrator.code_orchestrator.code_generation_orchestrator.ensure_project_scaffolding", return_value=[]):

        response = client.post(
            f"/api/projects/{test_project.id}/execute",
            json={"max_iterations": 3, "sandbox_mode": "local_process"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == test_project.id
        assert data["status"] == "passed"
        assert data["total_tests"] == 2
        assert data["passed_tests"] == 2
        assert data["failed_tests"] == 0

        run_id = data["id"]
        detail_response = client.get(f"/api/projects/{test_project.id}/runs/{run_id}")
        assert detail_response.status_code == 200
        assert detail_response.json()["id"] == run_id

        list_response = client.get(f"/api/projects/{test_project.id}/runs")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
