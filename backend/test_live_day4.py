import asyncio
from app.database.session import SessionLocal
from app.models.project import Project
from app.models.requirement import Requirement
from app.services.requirement_service import get_requirement_by_project_id
from app.services.architecture_service import save_architecture, get_architecture_by_project_id
from app.services.task_service import save_task_plan, get_tasks_by_project_id, build_task_plan_response
from app.services.project_service import update_project
from app.schemas.project import ProjectUpdate
from app.schemas.requirement import RequirementSpecification
from app.agents.architect import architect_agent
from app.agents.planner import planner_agent


async def main():
    db = SessionLocal()
    try:
        # Find project from Day 3 that has requirements analyzed
        project = (
            db.query(Project)
            .join(Requirement, Requirement.project_id == Project.id)
            .order_by(Project.created_at.desc())
            .first()
        )
        if not project:
            print("Project not found, please run Day 3 analysis first.")
            return

        print(f"Loaded Project: '{project.name}' (ID: {project.id})")
        req_record = get_requirement_by_project_id(db, project.id)
        assert req_record is not None, "Project requirements must exist"
        requirements = RequirementSpecification.model_validate(req_record.specification)
        print(f"Loaded Requirements with {len(requirements.functional_requirements)} functional requirements.")

        # Step 1: Architect Agent
        print("\n--- [Step 1: Architect Agent Running with Ollama qwen2.5-coder:7b] ---")
        architecture = await architect_agent.design(
            project_name=project.name,
            requirements=requirements,
        )
        print("Architect Agent finished successfully!")
        print(f"Architecture Pattern: {architecture.architecture_pattern}")
        print(f"Tech Stack: {architecture.tech_stack.backend} + {architecture.tech_stack.frontend} + {architecture.tech_stack.database}")
        print(f"Data Entities ({len(architecture.data_entities)}):")
        for entity in architecture.data_entities:
            field_names = [f.name for f in entity.fields]
            print(f"  - {entity.name} ({entity.table_name}): {', '.join(field_names)}")

        print(f"API Contracts ({len(architecture.api_contracts)}):")
        for contract in architecture.api_contracts:
            auth_str = " [Auth Required]" if contract.auth_required else ""
            print(f"  - {contract.method} {contract.endpoint}{auth_str} -> {contract.description}")

        print(f"Key Architectural Decisions ({len(architecture.decisions)}):")
        for d in architecture.decisions:
            print(f"  - {d.title}: {d.decision} (Trade-off: {d.trade_off})")

        # Save architecture to PostgreSQL
        arch_record = save_architecture(db, project.id, architecture)
        update_project(db, project, ProjectUpdate(status="architected"))
        print(f"Saved architecture to PostgreSQL with ID: {arch_record.id}")

        # Step 2: Planner Agent + DAG Engine
        print("\n--- [Step 2: Planner Agent & DAG Engine Running with Ollama qwen2.5-coder:7b] ---")
        ordered_tasks, parallel_batches = await planner_agent.plan(
            project_name=project.name,
            requirements=requirements,
            architecture=architecture,
        )

        # Save tasks to PostgreSQL
        saved_tasks = save_task_plan(db, project.id, ordered_tasks)
        update_project(db, project, ProjectUpdate(status="planned"))

        plan_response = build_task_plan_response(project.id, saved_tasks)
        print(f"\nPlanner Agent finished! Total Tasks: {plan_response.total_tasks}, Total Execution Tiers: {plan_response.total_tiers}")
        print("\nParallel Execution Waves (DAG Tiers):")
        for tier_idx, batch in enumerate(plan_response.parallel_batches):
            print(f"  Wave {tier_idx} (Can execute concurrently): {', '.join(batch)}")

        print("\nSequenced Task Details:")
        for t in plan_response.tasks:
            deps_str = f" [Depends on: {', '.join(t.dependencies)}]" if t.dependencies else " [Root task]"
            print(f"  [{t.task_key}] Tier {t.tier} | Order {t.execution_order} | Agent: {t.assigned_agent}")
            print(f"        Title: {t.title}{deps_str}")
            print(f"        Description: {t.description}")

        print(f"\nAll Day 4 milestones verified in PostgreSQL 18! Project status is now '{project.status}'.")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
