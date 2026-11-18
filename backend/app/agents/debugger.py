"""
Autonomous Debugger Agent for Orchestrix.
Analyzes test failure diagnostics, determines root causes, and generates code repairs.
"""

import logging
import re
from typing import Dict, List
from app.services.llm_service import llm_service
from app.schemas.testing import TestRunReport
from app.schemas.debugger import DebugAnalysis, CodeFix
from app.prompts.debugger_prompts import DEBUGGER_AGENT_SYSTEM_PROMPT, DEBUGGER_USER_PROMPT

logger = logging.getLogger(__name__)


class DebuggerAgent:
    """
    Cognitive Debugging Agent that reads stack traces, identifies broken logic,
    and returns exact replacement code.
    """

    async def diagnose_and_repair(
        self,
        project_name: str,
        test_report: TestRunReport,
        file_contexts: Dict[str, str],
    ) -> DebugAnalysis:
        """
        Diagnose test failures and generate fix patches.
        """
        context_snippets = []
        for path, content in file_contexts.items():
            # Include first 150 lines of relevant files to keep context manageable
            truncated = "\n".join(content.splitlines()[:150])
            context_snippets.append(f"--- File: {path} ---\n{truncated}")

        user_prompt = DEBUGGER_USER_PROMPT.format(
            project_name=project_name,
            test_logs=test_report.raw_output[-3000:],  # Tail of test logs
            file_contexts="\n\n".join(context_snippets) if context_snippets else "No files provided.",
        )

        try:
            parsed = await llm_service.generate_json(
                system_prompt=DEBUGGER_AGENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )

            fixes = []
            for item in parsed.get("files_to_fix", []):
                content = item.get("replacement_content", "")
                if item.get("file_path", "").endswith(".py"):
                    content = re.sub(r"\bfrom\s+backend\.app\b", "from app", content)
                    content = re.sub(r"\bimport\s+backend\.app\b", "import app", content)
                    content = re.sub(r"\bfrom\s+backend\b", "from app", content)
                fixes.append(
                    CodeFix(
                        file_path=item["file_path"],
                        explanation=item.get("explanation", "Autonomous bug repair"),
                        replacement_content=content,
                    )
                )

            return DebugAnalysis(
                root_cause=parsed.get("root_cause", "Automated root cause identification"),
                files_to_fix=fixes,
            )
        except Exception as exc:
            logger.error(f"Debugger Agent failed to produce repair analysis: {exc}", exc_info=True)
            return DebugAnalysis(
                root_cause=f"Diagnostic failure: {exc}",
                files_to_fix=[],
            )


debugger_agent = DebuggerAgent()
