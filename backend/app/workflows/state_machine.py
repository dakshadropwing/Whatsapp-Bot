"""
Workflow State Machine — manages state transitions and context.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WorkflowState:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStateMachine:
    """
    Manages the execution flow and transitions of a workflow.
    """

    def __init__(self, workflow_id: str, context: dict[str, Any] | None = None) -> None:
        self.workflow_id = workflow_id
        self.state = WorkflowState.PENDING
        self.context = context or {}
        self.current_step_index = 0

    def start(self) -> None:
        self.state = WorkflowState.RUNNING
        self.current_step_index = 0
        logger.info("StateMachine: Started workflow %s", self.workflow_id)

    def transition_to(self, new_state: str) -> None:
        logger.info("StateMachine: Transitioned workflow %s state %s -> %s", self.workflow_id, self.state, new_state)
        self.state = new_state

    def next_step(self) -> int:
        self.current_step_index += 1
        return self.current_step_index
