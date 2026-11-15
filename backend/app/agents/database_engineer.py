import json
import logging
from typing import Optional
from app.services.llm_service import LLMService, llm_service
from app.schemas.architecture import SystemArchitecture
from app.schemas.task import TaskResponse
from app.schemas.code import TaskCodeOutput
from app.prompts.database_engineer_prompts import (
    DATABASE_ENGINEER_SYSTEM_PROMPT,
    DATABASE_ENGINEER_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class DatabaseEngineerAgent:
    """
    Autonomous Database Engineer Agent for Orchestrix.
    Generates SQLAlchemy models, schemas, and database initialization code.
    """

    def __init__(self, service: Optional[LLMService] = None):
        self.llm_service = service or llm_service

    async def execute_task(
        self,
        project_name: str,
        task: TaskResponse,
        architecture: SystemArchitecture,
    ) -> TaskCodeOutput:
        """Execute a database engineering task and return structured source files."""
        logger.info(f"DatabaseEngineerAgent executing task [{task.task_key}]: {task.title}")

        entities_json = json.dumps(
            [e.model_dump() for e in architecture.data_entities], indent=2
        )
        security_guidelines_json = json.dumps(architecture.security_guidelines, indent=2)

        prompt = DATABASE_ENGINEER_USER_TEMPLATE.format(
            project_name=project_name,
            task_key=task.task_key,
            task_title=task.title,
            task_description=task.description,
            entities_json=entities_json,
            security_guidelines_json=security_guidelines_json,
        )

        code_output = await self.llm_service.generate_structured(
            prompt=prompt,
            schema=TaskCodeOutput,
            system_prompt=DATABASE_ENGINEER_SYSTEM_PROMPT,
            temperature=0.1,
        )

        logger.info(
            f"DatabaseEngineerAgent completed task [{task.task_key}] "
            f"producing {len(code_output.files)} file(s)"
        )
        return code_output


database_engineer_agent = DatabaseEngineerAgent()
