import json
import logging
from typing import Optional
from app.services.llm_service import LLMService, llm_service
from app.schemas.architecture import SystemArchitecture
from app.schemas.task import TaskResponse
from app.schemas.code import TaskCodeOutput
from app.prompts.frontend_developer_prompts import (
    FRONTEND_DEVELOPER_SYSTEM_PROMPT,
    FRONTEND_DEVELOPER_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class FrontendDeveloperAgent:
    """
    Autonomous Frontend Developer Agent for Orchestrix.
    Generates Next.js 14 App Router (TypeScript) components, views, and API client integrations.
    """

    def __init__(self, service: Optional[LLMService] = None):
        self.llm_service = service or llm_service

    async def execute_task(
        self,
        project_name: str,
        task: TaskResponse,
        architecture: SystemArchitecture,
        existing_code_context: Optional[str] = None,
    ) -> TaskCodeOutput:
        """Execute a frontend development task and return structured source files."""
        logger.info(f"FrontendDeveloperAgent executing task [{task.task_key}]: {task.title}")

        contracts_json = json.dumps(
            [c.model_dump() for c in architecture.api_contracts], indent=2
        )

        existing_section = (
            f"Existing Project Code Context (Backend Routers & Endpoints):\n{existing_code_context}\n"
            if existing_code_context
            else ""
        )

        prompt = FRONTEND_DEVELOPER_USER_TEMPLATE.format(
            project_name=project_name,
            task_key=task.task_key,
            task_title=task.title,
            task_description=task.description,
            contracts_json=contracts_json,
            existing_context_section=existing_section,
        )

        code_output = await self.llm_service.generate_structured(
            prompt=prompt,
            schema=TaskCodeOutput,
            system_prompt=FRONTEND_DEVELOPER_SYSTEM_PROMPT,
            temperature=0.1,
        )

        logger.info(
            f"FrontendDeveloperAgent completed task [{task.task_key}] "
            f"producing {len(code_output.files)} file(s)"
        )
        return code_output


frontend_developer_agent = FrontendDeveloperAgent()
