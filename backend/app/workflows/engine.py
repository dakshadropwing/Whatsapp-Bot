"""
Workflow Engine — coordinates trigger matching and step executors.
"""
from __future__ import annotations

import logging
from typing import Any

from app.workflows.state_machine import WorkflowState, WorkflowStateMachine

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Executes automation workflow steps.
    """

    @staticmethod
    def execute(
        workflow_id: str,
        steps: list[dict],
        conversation_id: str | None = None,
        initial_context: dict | None = None,
    ) -> dict:
        sm = WorkflowStateMachine(workflow_id, initial_context)
        sm.start()

        executed_steps = []
        try:
            for i, step in enumerate(steps):
                action = step.get("action")
                payload = step.get("payload", {})
                logger.info("Engine: Executing step %d - action: %s", i, action)

                result = WorkflowEngine.execute_step(action, payload, conversation_id, sm.context)
                executed_steps.append({"step": i, "action": action, "result": result})

                if action == "wait":
                    sm.transition_to(WorkflowState.PENDING)
                    return {"status": "paused", "current_step": i, "context": sm.context}

                sm.next_step()

            sm.transition_to(WorkflowState.COMPLETED)
            return {"status": "completed", "steps": executed_steps, "context": sm.context}
        except Exception as exc:
            logger.exception("Engine: Workflow %s failed at step %d", workflow_id, sm.current_step_index)
            sm.transition_to(WorkflowState.FAILED)
            return {"status": "failed", "error": str(exc), "context": sm.context}

    @staticmethod
    def execute_step(
        action: str, payload: dict, conversation_id: str | None, context: dict
    ) -> Any:
        from app.workflows.executors import get_executor

        executor = get_executor(action)
        if executor:
            return executor(payload, conversation_id, context)
        logger.warning("Engine: No executor found for action %s", action)
        return None
