import asyncio
import json
from app.database.session import SessionLocal
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import create_project, update_project
from app.services.requirement_service import save_requirement, get_requirement_by_project_id
from app.agents.requirement_analyzer import requirement_analyzer_agent


async def main():
    db = SessionLocal()
    try:
        # Create project in real PostgreSQL
        proj = create_project(
            db,
            ProjectCreate(
                name="Student Management Platform",
                description="Build a student management platform with authentication, attendance tracking, student profiles and an admin dashboard.",
            ),
        )
        print(f"Created project '{proj.name}' with ID: {proj.id}")

        # Run live Requirement Analyzer Agent with Ollama qwen2.5-coder:7b
        print("Invoking RequirementAnalyzerAgent with live Ollama qwen2.5-coder:7b...")
        spec = await requirement_analyzer_agent.analyze(
            project_name=proj.name,
            project_description=proj.description,
        )
        print("\n=== LIVE REQUIREMENT ANALYSIS RESULT ===")
        print(f"Project: {spec.project_name}")
        print(f"Complexity: {spec.complexity_score}")
        print(f"Overview: {spec.overview}")
        print(f"\nUser Roles ({len(spec.user_roles)}):")
        for role in spec.user_roles:
            print(f" - [{role.role}]: {role.description} (Permissions: {', '.join(role.permissions)})")

        print(f"\nFunctional Requirements ({len(spec.functional_requirements)}):")
        for fr in spec.functional_requirements:
            print(f" - [{fr.id}] {fr.title} (Priority: {fr.priority}) -> {fr.description}")

        print(f"\nNon-Functional Requirements ({len(spec.non_functional_requirements)}):")
        for nfr in spec.non_functional_requirements:
            print(f" - [{nfr.category.upper()}] {nfr.description} | Target: {nfr.metric}")

        print(f"\nCore Features ({len(spec.core_features)}):")
        for cf in spec.core_features:
            print(f" - {cf.name}: {cf.description} (Components: {', '.join(cf.components)})")

        print(f"\nAcceptance Criteria ({len(spec.acceptance_criteria)}):")
        for ac in spec.acceptance_criteria:
            print(f" - [{ac.id}] {ac.scenario}")
            print(f"    Given: {ac.given}")
            print(f"    When:  {ac.when}")
            print(f"    Then:  {ac.then}")

        if spec.clarifying_questions:
            print(f"\nClarifying Questions ({len(spec.clarifying_questions)}):")
            for q in spec.clarifying_questions:
                print(f" ? {q}")

        # Persist into real PostgreSQL 18 database
        req_record = save_requirement(db, proj.id, spec)
        update_project(db, proj, ProjectUpdate(status="planning"))
        print(f"\nSuccessfully stored requirement specification in PostgreSQL! (Requirement ID: {req_record.id})")

        # Verify retrieval from database
        persisted = get_requirement_by_project_id(db, proj.id)
        assert persisted is not None
        assert persisted.specification["project_name"] == spec.project_name
        print(f"Database verification passed! Project status is now '{proj.status}'.")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
