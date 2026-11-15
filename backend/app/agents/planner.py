import logging
from typing import Optional, List, Dict, Any, Tuple
from app.services.llm_service import LLMService, llm_service
from app.schemas.requirement import RequirementSpecification
from app.schemas.architecture import SystemArchitecture
from app.schemas.task import TaskPlanLLMOutput
from app.orchestrator.dag_engine import DAGEngine
from app.prompts.planner_prompts import (
    PLANNER_AGENT_SYSTEM_PROMPT,
    PLANNER_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Autonomous Planner Agent for Orchestrix.
    Translates requirements and architecture into a Directed Acyclic Graph (DAG)
    of verified engineering tasks scheduled with topological order.
    """

    def __init__(self, service: Optional[LLMService] = None):
        self.llm_service = service or llm_service

    async def plan(
        self,
        project_name: str,
        requirements: RequirementSpecification,
        architecture: SystemArchitecture,
    ) -> Tuple[List[Dict[str, Any]], List[List[str]]]:
        """
        Produce a topologically ordered task plan with parallel execution batches.
        Returns:
          (ordered_tasks, parallel_batches)
        """
        logger.info(f"PlannerAgent generating task plan for: {project_name}")

        entities_summary = ", ".join(
            f"{e.name} ({e.table_name})" for e in architecture.data_entities
        )
        contracts_summary = ", ".join(
            f"{c.method} {c.endpoint}" for c in architecture.api_contracts
        )

        prompt = PLANNER_USER_TEMPLATE.format(
            project_name=project_name,
            architecture_pattern=architecture.architecture_pattern,
            entities_summary=entities_summary or "Standard relational models",
            contracts_summary=contracts_summary or "Standard REST endpoints",
            overview=requirements.overview,
        )

        llm_output = await self.llm_service.generate_structured(
            prompt=prompt,
            schema=TaskPlanLLMOutput,
            system_prompt=PLANNER_AGENT_SYSTEM_PROMPT,
            temperature=0.2,
        )

        raw_tasks = [t.model_dump() for t in llm_output.tasks]
        logger.info(f"PlannerAgent received {len(raw_tasks)} raw tasks from LLM. Validating DAG...")

        # Deterministic topological sorting and validation
        ordered_tasks, parallel_batches = DAGEngine.validate_and_order(raw_tasks)

        logger.info(
            f"DAG validation successful: {len(ordered_tasks)} tasks across "
            f"{len(parallel_batches)} parallel execution tiers"
        )
        return ordered_tasks, parallel_batches


planner_agent = PlannerAgent()
