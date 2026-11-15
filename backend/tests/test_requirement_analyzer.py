import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.session import Base, get_db
from app.services.llm_service import llm_service
from app.schemas.requirement import (
    RequirementSpecification,
    FunctionalRequirement,
    NonFunctionalRequirement,
    UserRole,
    FeatureModule,
    TechnicalConstraint,
    AcceptanceCriterion,
)


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
def mock_spec():
    return RequirementSpecification(
        project_name="Student Portal",
        overview="A unified portal for managing student attendance, grades, and profiles.",
        target_audience="University faculty, administrators, and students.",
        user_roles=[
            UserRole(
                role="Admin",
                description="System administrator",
                permissions=["manage_users", "view_reports", "system_config"],
            ),
            UserRole(
                role="Student",
                description="Enrolled student",
                permissions=["view_grades", "view_attendance"],
            ),
        ],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001",
                title="Student Authentication",
                description="Secure login using email and hashed passwords with JWT sessions.",
                priority="critical",
                target_roles=["Admin", "Student"],
            ),
            FunctionalRequirement(
                id="FR-002",
                title="Attendance Logging",
                description="Faculty records daily lecture attendance per course.",
                priority="high",
                target_roles=["Admin"],
            ),
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(
                category="security",
                description="All passwords must be hashed using bcrypt with salt rounds >= 12.",
                metric="100% compliance",
            ),
            NonFunctionalRequirement(
                category="performance",
                description="API endpoints response time under 200ms p95.",
                metric="<200ms",
            ),
        ],
        core_features=[
            FeatureModule(
                name="Auth Module",
                description="Handles authentication and authorization",
                components=["LoginForm", "JWTMiddleware"],
            ),
            FeatureModule(
                name="Attendance Module",
                description="Attendance roster and reporting",
                components=["AttendanceTable", "ExportCSV"],
            ),
        ],
        technical_constraints=[
            TechnicalConstraint(
                category="Backend",
                constraint="FastAPI with async SQLAlchemy session",
                rationale="Ensures high concurrency and clean typing",
            )
        ],
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-001",
                scenario="Successful user login",
                given="An active user with valid credentials exists",
                when="User submits valid email and password",
                then="Server returns 200 OK with valid JWT bearer token",
            )
        ],
        clarifying_questions=[
            "Should attendance support biometric verification in phase 2?"
        ],
        complexity_score="medium",
    )


def test_schema_validation(mock_spec):
    """Verify that RequirementSpecification validates clean data correctly."""
    assert mock_spec.project_name == "Student Portal"
    assert len(mock_spec.user_roles) == 2
    assert len(mock_spec.functional_requirements) == 2
    assert mock_spec.functional_requirements[0].priority == "critical"
    assert mock_spec.complexity_score == "medium"


def test_llm_clean_json_string():
    """Verify markdown fences and surrounding commentary are stripped."""
    raw = "Here is the JSON specification:\n```json\n{\"project_name\": \"Clean\"}\n```\nHope this helps!"
    cleaned = llm_service._clean_json_string(raw)
    assert cleaned == '{"project_name": "Clean"}'


def test_agents_roster_endpoint(client):
    """Verify agent list API returns all 9 specialized engineering agents."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_agents"] == 9
    agent_ids = [a["id"] for a in data["agents"]]
    assert "requirement_analyzer" in agent_ids
    assert "architect" in agent_ids
    assert "planner" in agent_ids
    assert "debugger" in agent_ids


def test_project_analyze_with_mocked_llm(client, mock_spec):
    """Verify project requirement analysis end-to-end with mocked LLM."""
    # Create project first
    create_res = client.post(
        "/api/projects",
        json={
            "name": "Student Portal",
            "description": "Student management system with attendance tracking and profiles.",
        },
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # Mock the RequirementAnalyzerAgent.analyze call
    with patch(
        "app.api.projects.requirement_analyzer_agent.analyze",
        new_callable=AsyncMock,
    ) as mock_analyze:
        mock_analyze.return_value = mock_spec

        analyze_res = client.post(f"/api/projects/{project_id}/analyze")
        assert analyze_res.status_code == 200
        analysis_data = analyze_res.json()
        assert analysis_data["status"] == "analyzed"
        assert analysis_data["specification"]["project_name"] == "Student Portal"
        assert len(analysis_data["specification"]["functional_requirements"]) == 2

    # Verify requirements are persisted and retrievable
    req_res = client.get(f"/api/projects/{project_id}/requirements")
    assert req_res.status_code == 200
    saved_spec = req_res.json()
    assert saved_spec["project_name"] == "Student Portal"
    assert len(saved_spec["user_roles"]) == 2

    # Verify project status in projects table is updated to analyzed
    proj_res = client.get(f"/api/projects/{project_id}")
    assert proj_res.status_code == 200
    assert proj_res.json()["status"] == "analyzed"


def test_analyze_nonexistent_project(client):
    """Verify analyzing a non-existent project returns 404."""
    response = client.post("/api/projects/non-existent-uuid/analyze")
    assert response.status_code == 404


def test_requirements_not_analyzed_yet(client):
    """Verify querying requirements before analysis returns 404."""
    create_res = client.post(
        "/api/projects",
        json={
            "name": "Unanalyzed Project",
            "description": "Project created without running analysis yet.",
        },
    )
    project_id = create_res.json()["id"]

    req_res = client.get(f"/api/projects/{project_id}/requirements")
    assert req_res.status_code == 404
