"""
Tests for Project Scaffolding Automation in Orchestrix.
"""

import json
import pytest
from app.orchestrator.scaffolding import scaffolding_generator
from app.schemas.architecture import SystemArchitecture, TechStack


@pytest.fixture
def sample_architecture():
    return SystemArchitecture(
        project_name="Test App",
        architecture_pattern="layered",
        tech_stack=TechStack(
            backend="FastAPI",
            frontend="Next.js",
            database="PostgreSQL",
            orm="SQLAlchemy",
            authentication="JWT",
        ),
        components=[],
        entities=[],
        api_contracts=[],
        architectural_decisions=[],
    )


def test_scaffolding_generator_creates_all_core_files(sample_architecture):
    discovered_routers = ["backend/app/api/items.py", "backend/app/api/users.py"]
    scaffold = scaffolding_generator.generate_scaffolding(
        project_name="Test App",
        architecture=sample_architecture,
        discovered_api_routers=discovered_routers,
    )

    expected_files = [
        "backend/requirements.txt",
        "backend/app/database/session.py",
        "backend/app/main.py",
        "backend/Dockerfile",
        "frontend/package.json",
        "frontend/tsconfig.json",
        "frontend/Dockerfile",
        "docker-compose.yml",
    ]

    for expected in expected_files:
        assert expected in scaffold, f"Missing scaffolding file: {expected}"
        assert len(scaffold[expected].strip()) > 0

    # Verify requirements.txt
    reqs = scaffold["backend/requirements.txt"]
    assert "fastapi" in reqs
    assert "pytest" in reqs
    assert "sqlalchemy" in reqs

    # Verify main.py
    main_py = scaffold["backend/app/main.py"]
    assert "FastAPI" in main_py
    assert "/health" in main_py
    assert "from app.api.items import router as items_router" in main_py
    assert "from app.api.users import router as users_router" in main_py

    # Verify package.json validity
    pkg = json.loads(scaffold["frontend/package.json"])
    assert pkg["name"] == "test-app-frontend"
    assert "next" in pkg["dependencies"]

    # Verify docker-compose.yml
    compose = scaffold["docker-compose.yml"]
    assert "backend:" in compose
    assert "frontend:" in compose
    assert "db:" in compose
