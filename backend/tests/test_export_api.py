"""
Integration tests for Project ZIP Export API endpoint.
"""

import io
import zipfile
import pytest
from app.models.project import Project
from app.services.workspace_service import workspace_service


@pytest.fixture
def project_with_workspace(db):
    proj = Project(
        name="Export Test App",
        description="Testing ZIP packaging endpoint",
        status="completed",
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)

    # Write a test file into workspace
    workspace_service.write_file(
        project_slug=proj.name,
        relative_path="backend/app/main.py",
        content="# Export test content",
        overwrite=True,
    )
    workspace_service.write_file(
        project_slug=proj.name,
        relative_path="README.md",
        content="# Export Readme",
        overwrite=True,
    )

    yield proj


def test_export_project_nonexistent(client):
    response = client.get("/api/projects/nonexistent-id/export")
    assert response.status_code == 404


def test_export_project_zip_success(client, project_with_workspace: Project):
    response = client.get(f"/api/projects/{project_with_workspace.id}/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert "export-test-app-orchestrix.zip" in response.headers["content-disposition"]

    # Verify zip content
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes, "r") as z:
        file_list = z.namelist()
        assert any("backend/app/main.py" in f for f in file_list)
        assert any("README.md" in f for f in file_list)
