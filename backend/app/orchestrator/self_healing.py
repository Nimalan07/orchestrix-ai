"""
Autonomous Self-Healing Loop Orchestrator for Orchestrix.
Executes test-and-repair cycles bounded by max_iterations to self-heal failing generated code.
"""

import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.models.project import Project
from app.services.workspace_service import workspace_service
from app.services.artifact_service import save_file_artifact
from app.agents.testing_agent import testing_agent
from app.agents.debugger import debugger_agent
from app.schemas.debugger import SelfHealingResult, CodeFix
from app.schemas.testing import TestRunReport

logger = logging.getLogger(__name__)


class SelfHealingEngine:
    """
    Executes a bounded feedback loop between Testing Agent and Debugger Agent.
    """

    async def execute_loop(
        self,
        db: Session,
        project: Project,
        max_iterations: int = 3,
    ) -> SelfHealingResult:
        """
        Execute bounded self-healing loop:
        1. Run test suite in isolated sandbox.
        2. If passed, complete immediately.
        3. If failed, invoke debugger agent, apply patches, recalculate hashes, and re-test.
        4. Repeat up to max_iterations.
        """
        logger.info(f"Starting execution & self-healing loop for project: {project.name}")

        # Initial baseline test run
        report = testing_agent.execute_tests(project.name)
        if report.all_passed:
            logger.info(f"Initial tests passed cleanly for {project.name} on first run.")
            return SelfHealingResult(
                project_name=project.name,
                status="passed",
                iterations_run=0,
                max_iterations=max_iterations,
                final_report=report,
                fixes_applied=[],
                iteration_history=[{
                    "iteration": 0,
                    "passed": report.passed,
                    "failed": report.failed,
                    "all_passed": True,
                }],
            )

        applied_fixes: List[CodeFix] = []
        history: List[Dict[str, Any]] = [{
            "iteration": 0,
            "passed": report.passed,
            "failed": report.failed,
            "all_passed": False,
            "raw_output": report.raw_output[:500],
        }]

        # Gather relevant backend files for context
        all_files = [f["relative_path"] for f in workspace_service.list_files(project.name)]
        backend_files = [f for f in all_files if f.startswith("backend/") and f.endswith(".py")]

        file_contexts: Dict[str, str] = {}
        for f in backend_files:
            try:
                file_contexts[f] = workspace_service.read_file(project.name, f)
            except Exception:
                pass

        # Bounded repair iterations
        current_report = report
        for iteration in range(1, max_iterations + 1):
            logger.info(f"Self-Healing iteration {iteration}/{max_iterations} for {project.name}")

            analysis = await debugger_agent.diagnose_and_repair(
                project_name=project.name,
                test_report=current_report,
                file_contexts=file_contexts,
            )

            if not analysis.files_to_fix:
                logger.warning(f"Debugger produced no actionable fixes on iteration {iteration}.")
                break

            for fix in analysis.files_to_fix:
                meta = workspace_service.write_file(
                    project_slug=project.name,
                    relative_path=fix.file_path,
                    content=fix.replacement_content,
                    overwrite=True,
                )
                save_file_artifact(
                    db=db,
                    project_id=project.id,
                    file_path=meta["relative_path"],
                    file_hash=meta["sha256"],
                    agent="debugger",
                )
                applied_fixes.append(fix)
                # Update file context in memory
                file_contexts[fix.file_path] = fix.replacement_content

            # Re-execute tests
            current_report = testing_agent.execute_tests(project.name)
            history.append({
                "iteration": iteration,
                "root_cause": analysis.root_cause,
                "fixes_count": len(analysis.files_to_fix),
                "passed": current_report.passed,
                "failed": current_report.failed,
                "all_passed": current_report.all_passed,
            })

            if current_report.all_passed:
                logger.info(f"Project {project.name} successfully healed on iteration {iteration}!")
                return SelfHealingResult(
                    project_name=project.name,
                    status="healed",
                    iterations_run=iteration,
                    max_iterations=max_iterations,
                    final_report=current_report,
                    fixes_applied=applied_fixes,
                    iteration_history=history,
                )

        logger.warning(f"Self-healing exhausted {max_iterations} iterations without full resolution.")
        return SelfHealingResult(
            project_name=project.name,
            status="failed",
            iterations_run=max_iterations,
            max_iterations=max_iterations,
            final_report=current_report,
            fixes_applied=applied_fixes,
            iteration_history=history,
        )


self_healing_engine = SelfHealingEngine()
