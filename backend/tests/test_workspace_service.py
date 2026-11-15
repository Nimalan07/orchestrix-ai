import pytest
import tempfile
from pathlib import Path
from app.services.workspace_service import WorkspaceService, SecurityError


@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as tmp_dir:
        svc = WorkspaceService(root_dir=tmp_dir)
        yield svc


def test_slugify(temp_workspace):
    assert temp_workspace.slugify("Student Management Platform") == "student-management-platform"
    assert temp_workspace.slugify("Project #1: Cool App!!") == "project-1-cool-app"
    assert temp_workspace.slugify("   Spaces   ") == "spaces"
    assert temp_workspace.slugify("") == "unnamed-project"


def test_safe_write_and_read(temp_workspace):
    meta = temp_workspace.write_file(
        project_slug="demo-app",
        relative_path="backend/app/main.py",
        content="print('Hello World')",
    )
    assert meta["relative_path"] == "backend/app/main.py"
    assert meta["size_bytes"] == len("print('Hello World')".encode("utf-8"))
    assert len(meta["sha256"]) == 64

    content = temp_workspace.read_file("demo-app", "backend/app/main.py")
    assert content == "print('Hello World')"


def test_path_traversal_prevention(temp_workspace):
    # Attempt to write outside workspace using ..
    with pytest.raises(SecurityError):
        temp_workspace.resolve_safe_path("demo-app", "../outside.txt")

    with pytest.raises(SecurityError):
        temp_workspace.resolve_safe_path("demo-app", "../../etc/passwd")

    with pytest.raises(SecurityError):
        temp_workspace.resolve_safe_path("demo-app", "sub/../../escaped.py")

    with pytest.raises(SecurityError):
        temp_workspace.resolve_safe_path("demo-app", "C:/Windows/System32/calc.exe")


def test_list_files(temp_workspace):
    temp_workspace.write_file("my-app", "README.md", "# My App")
    temp_workspace.write_file("my-app", "backend/main.py", "app = FastAPI()")
    temp_workspace.write_file("my-app", "frontend/page.tsx", "export default Page")

    files = temp_workspace.list_files("my-app")
    assert len(files) == 3
    rel_paths = [f["relative_path"] for f in files]
    assert "README.md" in rel_paths
    assert "backend/main.py" in rel_paths
    assert "frontend/page.tsx" in rel_paths
