import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Body, status
from app.services.llm_service import llm_service
from app.agents.requirement_analyzer import requirement_analyzer_agent
from app.schemas.requirement import RequirementSpecification

router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"]
)

AGENTS_ROSTER = [
    {
        "id": "requirement_analyzer",
        "name": "Requirement Analyzer Agent",
        "role": "Converts natural-language requirements into structured JSON specifications",
        "status": "ready",
        "output": "requirements.json",
    },
    {
        "id": "architect",
        "name": "Architect Agent",
        "role": "Designs component architecture, API contracts, and technology stack",
        "status": "ready",
        "output": "architecture.json",
    },
    {
        "id": "planner",
        "name": "Planner Agent",
        "role": "Breaks architecture into dependency-aware ordered tasks (DAG)",
        "status": "ready",
        "output": "task_plan.json",
    },
    {
        "id": "database_engineer",
        "name": "Database Engineer Agent",
        "role": "Generates schemas, models, migrations, and relationship indexes",
        "status": "pending_orchestration",
        "output": "database_models",
    },
    {
        "id": "backend_developer",
        "name": "Backend Developer Agent",
        "role": "Generates API endpoints, business logic, and authentication",
        "status": "pending_orchestration",
        "output": "backend_source_files",
    },
    {
        "id": "frontend_developer",
        "name": "Frontend Developer Agent",
        "role": "Creates responsive UI components, state management, and page views",
        "status": "pending_orchestration",
        "output": "frontend_source_files",
    },
    {
        "id": "tester",
        "name": "Testing Agent",
        "role": "Generates test cases, executes test suites in sandbox, and reports failures",
        "status": "pending_orchestration",
        "output": "test_results",
    },
    {
        "id": "debugger",
        "name": "Debugger Agent",
        "role": "Analyzes stack traces and produces targeted unified diff patches",
        "status": "pending_orchestration",
        "output": "code_patches",
    },
    {
        "id": "reviewer",
        "name": "Reviewer & Security Agent",
        "role": "Audits code quality, AST structure, security risks, and OWASP compliance",
        "status": "pending_orchestration",
        "output": "review_reports",
    },
]


@router.get("", status_code=status.HTTP_200_OK)
def list_agents():
    """List all specialized AI engineering agents and their current readiness."""
    return {
        "total_agents": len(AGENTS_ROSTER),
        "agents": AGENTS_ROSTER
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def check_ai_health():
    """Verify connectivity and model readiness on the Ollama provider."""
    start_time = time.time()
    available = await llm_service.is_available()
    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "provider": "ollama",
        "base_url": llm_service.base_url,
        "model": llm_service.model_name,
        "is_available": available,
        "latency_ms": latency_ms,
        "status": "healthy" if available else "unavailable"
    }


@router.post("/analyze", response_model=RequirementSpecification, status_code=status.HTTP_200_OK)
async def direct_requirement_analysis(
    name: str = Body(..., description="Project name", embed=True),
    description: str = Body(..., description="User requirement description", embed=True),
    additional_context: Optional[str] = Body(default=None, embed=True),
):
    """Directly analyze requirements without creating a project in the database."""
    try:
        spec = await requirement_analyzer_agent.analyze(
            project_name=name,
            project_description=description,
            additional_context=additional_context,
        )
        return spec
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Requirement analysis failed: {str(exc)}"
        )
