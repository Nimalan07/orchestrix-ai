import logging
from typing import Optional
from app.services.llm_service import LLMService, llm_service
from app.schemas.requirement import RequirementSpecification
from app.prompts.requirement_prompts import (
    REQUIREMENT_ANALYZER_SYSTEM_PROMPT,
    REQUIREMENT_ANALYSIS_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class RequirementAnalyzerAgent:
    """
    Autonomous Requirement Analyzer Agent for Orchestrix.
    Translates raw user requirements into rigorous, validated Pydantic technical specifications.
    """

    def __init__(self, service: Optional[LLMService] = None):
        self.llm_service = service or llm_service

    async def analyze(
        self,
        project_name: str,
        project_description: str,
        additional_context: Optional[str] = None,
    ) -> RequirementSpecification:
        """
        Execute requirement analysis against natural language input.
        Returns a validated RequirementSpecification model.
        """
        logger.info(f"RequirementAnalyzer analyzing project: {project_name}")

        context_clause = (
            f"Additional User Guidance:\n{additional_context}"
            if additional_context
            else "No additional guidance provided."
        )

        prompt = REQUIREMENT_ANALYSIS_USER_TEMPLATE.format(
            project_name=project_name,
            project_description=project_description,
            additional_context_clause=context_clause,
        )

        specification = await self.llm_service.generate_structured(
            prompt=prompt,
            schema=RequirementSpecification,
            system_prompt=REQUIREMENT_ANALYZER_SYSTEM_PROMPT,
            temperature=0.2,
        )

        logger.info(
            f"RequirementAnalyzer generated {len(specification.functional_requirements)} "
            f"functional requirements for {project_name}"
        )
        return specification


requirement_analyzer_agent = RequirementAnalyzerAgent()
