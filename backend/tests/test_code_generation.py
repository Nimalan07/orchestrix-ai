import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.session import Base, get_db
from app.schemas.requirement import (
    RequirementSpecification,
    FunctionalRequirement,
    NonFunctionalRequirement,
    UserRole,
    FeatureModule,
    TechnicalConstraint,
    AcceptanceCriterion,
)
from app.schemas.architecture import (
    SystemArchitecture,
    TechStack,
    APIContract,
    DataEntity,
    EntityField,
)
from app.schemas.task import TaskBase, TaskPlanLLMOutput
from app.schemas.code import TaskCodeOutput, GeneratedFile


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def sample_setup(client):
    # Create project
    create_res = client.post(
        "/api/projects",
        json={"name": "Test Platform", "description": "Platform for code generation tests"},
    )
    project_id = create_res.json()["id"]

    # Mock requirement analyzer
    mock_req = RequirementSpecification(
        project_name="Test Platform",
        overview="Platform overview",
        target_audience="Engineers",
        user_roles=[UserRole(role="Admin", description="Admin role", permissions=["all"])],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001", title="Auth", description="Login", priority="critical"
            )
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(category="security", description="bcrypt")
        ],
        core_features=[FeatureModule(name="Auth", description="Auth module")],
        technical_constraints=[
            TechnicalConstraint(category="Backend", constraint="FastAPI", rationale="Fast")
        ],
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-001", scenario="Login", given="User", when="Submit", then="OK"
            )
        ],
        clarifying_questions=[],
        complexity_score="medium",
    )
    with patch("app.api.projects.requirement_analyzer_agent.analyze", new_callable=AsyncMock) as mock_an:
        mock_an.return_value = mock_req
        client.post(f"/api/projects/{project_id}/analyze")

    # Mock architect agent
    mock_arch = SystemArchitecture(
        project_name="Test Platform",
        architecture_pattern="Layered REST",
        tech_stack=TechStack(backend="FastAPI", frontend="Next.js", database="PostgreSQL"),
        api_contracts=[
            APIContract(
                endpoint="/api/students",
                method="GET",
                description="Get students",
                response_body="List[Student]",
            )
        ],
        data_entities=[
            DataEntity(
                name="Student",
                table_name="students",
                description="Student table",
                fields=[EntityField(name="id", type="String(36)", primary_key=True)],
            )
        ],
        security_guidelines=["Hash passwords"],
        decisions=[],
    )
    with patch("app.api.projects.architect_agent.design", new_callable=AsyncMock) as mock_ar:
        mock_ar.return_value = mock_arch
        client.post(f"/api/projects/{project_id}/architect")

    # Mock planner agent
    raw_tasks = [
        TaskBase(
            task_key="T1",
            title="Database Schema",
            description="Create models",
            assigned_agent="database_engineer",
            dependencies=[],
        ),
        TaskBase(
            task_key="T2",
            title="Backend API",
            description="Create API router",
            assigned_agent="backend_developer",
            dependencies=["T1"],
        ),
        TaskBase(
            task_key="T3",
            title="Frontend UI",
            description="Create Next.js page",
            assigned_agent="frontend_developer",
            dependencies=["T2"],
        ),
    ]
    with patch("app.agents.planner.planner_agent.llm_service.generate_structured", new_callable=AsyncMock) as mock_pl:
        mock_pl.return_value = TaskPlanLLMOutput(tasks=raw_tasks)
        client.post(f"/api/projects/{project_id}/plan")

    return project_id


def test_code_generation_orchestrator(client, sample_setup):
    project_id = sample_setup

    db_output = TaskCodeOutput(
        task_key="T1",
        summary="Database models generated",
        files=[
            GeneratedFile(
                file_path="backend/app/models/student.py",
                content="from sqlalchemy.orm import DeclarativeBase\nclass Student(DeclarativeBase):\n    pass\n",
                description="Student model",
                file_type="python",
            )
        ],
    )

    backend_output = TaskCodeOutput(
        task_key="T2",
        summary="Backend APIs generated",
        files=[
            GeneratedFile(
                file_path="backend/app/api/students.py",
                content="from fastapi import APIRouter\nrouter = APIRouter()\n",
                description="Students API router",
                file_type="python",
            )
        ],
    )

    frontend_output = TaskCodeOutput(
        task_key="T3",
        summary="Frontend UI generated",
        files=[
            GeneratedFile(
                file_path="frontend/app/students/page.tsx",
                content="'use client';\nexport default function Page() { return <div>Students</div>; }\n",
                description="Students page component",
                file_type="typescript",
            )
        ],
    )

    with patch(
        "app.agents.database_engineer.database_engineer_agent.execute_task",
        new_callable=AsyncMock,
        return_value=db_output,
    ), patch(
        "app.agents.backend_developer.backend_developer_agent.execute_task",
        new_callable=AsyncMock,
        return_value=backend_output,
    ), patch(
        "app.agents.frontend_developer.frontend_developer_agent.execute_task",
        new_callable=AsyncMock,
        return_value=frontend_output,
    ):
        gen_res = client.post(f"/api/projects/{project_id}/generate")
        assert gen_res.status_code == 200
        manifest = gen_res.json()

        assert manifest["total_files"] >= 5  # 3 generated + README.md + generation_manifest.json
        rel_paths = [f["relative_path"] for f in manifest["files"]]
        assert "backend/app/models/student.py" in rel_paths
        assert "backend/app/api/students.py" in rel_paths
        assert "frontend/app/students/page.tsx" in rel_paths
        assert "README.md" in rel_paths
        assert "generation_manifest.json" in rel_paths

    # Verify project files endpoint
    files_res = client.get(f"/api/projects/{project_id}/files")
    assert files_res.status_code == 200
    artifacts = files_res.json()
    assert len(artifacts) >= 5
    artifact_paths = [a["file_path"] for a in artifacts]
    assert "backend/app/models/student.py" in artifact_paths

    # Verify file content retrieval
    content_res = client.get(
        f"/api/projects/{project_id}/files/content",
        params={"file_path": "backend/app/models/student.py"},
    )
    assert content_res.status_code == 200
    assert "class Student" in content_res.text

    # Verify path traversal attack protection
    traversal_res = client.get(
        f"/api/projects/{project_id}/files/content",
        params={"file_path": "../../secret.txt"},
    )
    assert traversal_res.status_code == 403
