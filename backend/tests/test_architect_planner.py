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
    ArchitecturalDecision,
)
from app.schemas.task import TaskBase, TaskPlanLLMOutput


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
def sample_requirements():
    return RequirementSpecification(
        project_name="Portal",
        overview="Student portal overview",
        target_audience="Admins and Students",
        user_roles=[UserRole(role="Admin", description="Admin user", permissions=["all"])],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001", title="Auth", description="Login", priority="critical", target_roles=["Admin"]
            )
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(category="security", description="bcrypt hashing", metric="100%")
        ],
        core_features=[FeatureModule(name="Auth", description="Auth module", components=["LoginForm"])],
        technical_constraints=[
            TechnicalConstraint(category="Backend", constraint="FastAPI", rationale="Fast async")
        ],
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-001",
                scenario="Login",
                given="User exists",
                when="User logs in",
                then="Token returned",
            )
        ],
        clarifying_questions=[],
        complexity_score="medium",
    )


@pytest.fixture
def sample_architecture():
    return SystemArchitecture(
        project_name="Portal",
        architecture_pattern="Layered Architecture with FastAPI and Next.js",
        tech_stack=TechStack(
            frontend="Next.js",
            backend="FastAPI",
            database="PostgreSQL",
            orm="SQLAlchemy 2.x",
            authentication="JWT",
            styling="Tailwind",
            testing="Pytest",
        ),
        frontend_structure=["app/login/page.tsx", "app/dashboard/page.tsx"],
        backend_structure=["app/api/auth.py", "app/services/auth_service.py"],
        api_contracts=[
            APIContract(
                endpoint="/api/auth/login",
                method="POST",
                description="Authenticate user",
                response_body="TokenResponse",
                auth_required=False,
            ),
            APIContract(
                endpoint="/api/students",
                method="GET",
                description="List students",
                response_body="List[StudentResponse]",
                auth_required=True,
            ),
        ],
        data_entities=[
            DataEntity(
                name="Student",
                table_name="students",
                description="Student record",
                fields=[
                    EntityField(name="id", type="String(36)", primary_key=True),
                    EntityField(name="name", type="String(150)", nullable=False),
                ],
                relationships=[],
            )
        ],
        security_guidelines=["Hash passwords using bcrypt", "Validate JWT on private endpoints"],
        decisions=[
            ArchitecturalDecision(
                title="JWT Authentication",
                decision="Stateless JWT Bearer Tokens",
                alternatives_considered=["Server-side session cookies"],
                trade_off="Simplified horizontal scaling at the cost of token revocation complexity",
            )
        ],
    )


def test_architect_workflow(client, sample_requirements, sample_architecture):
    """Test full architecture generation and persistence workflow."""
    # Create project
    create_res = client.post("/api/projects", json={"name": "Portal", "description": "Student management portal"})
    project_id = create_res.json()["id"]

    # Trying to architect before requirements analysis fails with 400
    pre_arch = client.post(f"/api/projects/{project_id}/architect")
    assert pre_arch.status_code == 400
    assert "requirements must be analyzed" in pre_arch.json()["detail"].lower()

    # Analyze requirements (mocked)
    with patch("app.api.projects.requirement_analyzer_agent.analyze", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = sample_requirements
        client.post(f"/api/projects/{project_id}/analyze")

    # Now architect project (mocked)
    with patch("app.api.projects.architect_agent.design", new_callable=AsyncMock) as mock_arch:
        mock_arch.return_value = sample_architecture
        arch_res = client.post(f"/api/projects/{project_id}/architect")
        assert arch_res.status_code == 200
        arch_data = arch_res.json()
        assert arch_data["status"] == "architected"
        assert len(arch_data["architecture"]["api_contracts"]) == 2

    # Verify retrieval
    get_arch = client.get(f"/api/projects/{project_id}/architecture")
    assert get_arch.status_code == 200
    assert get_arch.json()["project_name"] == "Portal"


def test_planner_workflow_and_dag_generation(client, sample_requirements, sample_architecture):
    """Test task planning with DAG verification, topological ordering, and batching."""
    # Create project
    create_res = client.post("/api/projects", json={"name": "Portal", "description": "Student portal"})
    project_id = create_res.json()["id"]

    # Try planning before requirements / architecture fails
    pre_plan = client.post(f"/api/projects/{project_id}/plan")
    assert pre_plan.status_code == 400

    # Inject requirements
    with patch("app.api.projects.requirement_analyzer_agent.analyze", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = sample_requirements
        client.post(f"/api/projects/{project_id}/analyze")

    # Inject architecture
    with patch("app.api.projects.architect_agent.design", new_callable=AsyncMock) as mock_arch:
        mock_arch.return_value = sample_architecture
        client.post(f"/api/projects/{project_id}/architect")

    # Plan tasks with Planner Agent (mocked LLM raw output with deliberate reverse order to test DAG engine)
    mock_raw_tasks = [
        TaskBase(
            task_key="T3",
            title="Frontend Dashboard",
            description="Build student dashboard UI",
            assigned_agent="frontend_developer",
            dependencies=["T2"],
        ),
        TaskBase(
            task_key="T1",
            title="Database Models",
            description="Create SQLAlchemy models",
            assigned_agent="database_engineer",
            dependencies=[],
        ),
        TaskBase(
            task_key="T2",
            title="Student API",
            description="Build FastAPI student router",
            assigned_agent="backend_developer",
            dependencies=["T1"],
        ),
        TaskBase(
            task_key="T4",
            title="Integration Tests",
            description="Write end-to-end pytest suite",
            assigned_agent="tester",
            dependencies=["T3"],
        ),
    ]

    with patch("app.agents.planner.planner_agent.llm_service.generate_structured", new_callable=AsyncMock) as mock_plan:
        mock_plan.return_value = TaskPlanLLMOutput(tasks=mock_raw_tasks)

        plan_res = client.post(f"/api/projects/{project_id}/plan")
        assert plan_res.status_code == 200
        plan_data = plan_res.json()

        assert plan_data["total_tasks"] == 4
        assert plan_data["total_tiers"] == 4
        assert plan_data["parallel_batches"] == [["T1"], ["T2"], ["T3"], ["T4"]]

        # Verify topological sort put T1 first, then T2, then T3, then T4
        ordered_keys = [t["task_key"] for t in plan_data["tasks"]]
        assert ordered_keys == ["T1", "T2", "T3", "T4"]

    # Verify task listing
    tasks_res = client.get(f"/api/projects/{project_id}/tasks")
    assert tasks_res.status_code == 200
    assert len(tasks_res.json()) == 4

    # Verify task DAG endpoint
    dag_res = client.get(f"/api/projects/{project_id}/tasks/dag")
    assert dag_res.status_code == 200
    assert dag_res.json()["total_tasks"] == 4
    assert dag_res.json()["parallel_batches"] == [["T1"], ["T2"], ["T3"], ["T4"]]
