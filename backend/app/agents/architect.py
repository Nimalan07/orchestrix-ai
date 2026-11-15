import json
import logging
from typing import Optional
from app.services.llm_service import LLMService, llm_service
from app.schemas.requirement import RequirementSpecification
from app.schemas.architecture import SystemArchitecture
from app.prompts.architect_prompts import (
    ARCHITECT_AGENT_SYSTEM_PROMPT,
    ARCHITECT_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class ArchitectAgent:
    """
    Autonomous Architect Agent for Orchestrix.
    Designs system architecture, technology contracts, and data models
    from validated requirements.
    """

    def __init__(self, service: Optional[LLMService] = None):
        self.llm_service = service or llm_service

    async def design(
        self,
        project_name: str,
        requirements: RequirementSpecification,
    ) -> SystemArchitecture:
        """Produce full system architecture from requirement specification."""
        logger.info(f"ArchitectAgent designing system for: {project_name}")

        prompt = ARCHITECT_USER_TEMPLATE.format(
            project_name=project_name,
            overview=requirements.overview,
            target_audience=requirements.target_audience,
            user_roles_json=json.dumps(
                [r.model_dump() for r in requirements.user_roles], indent=2
            ),
            functional_requirements_json=json.dumps(
                [f.model_dump() for f in requirements.functional_requirements], indent=2
            ),
            non_functional_requirements_json=json.dumps(
                [n.model_dump() for n in requirements.non_functional_requirements], indent=2
            ),
        )

        architecture = await self.llm_service.generate_structured(
            prompt=prompt,
            schema=SystemArchitecture,
            system_prompt=ARCHITECT_AGENT_SYSTEM_PROMPT,
            temperature=0.2,
        )

        logger.info(
            f"ArchitectAgent generated architecture with {len(architecture.api_contracts)} "
            f"API contracts and {len(architecture.data_entities)} data entities"
        )
        return architecture


architect_agent = ArchitectAgent()
