"""
Workflow Triggers — matches events to workflow triggers.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def match_and_run_workflows(
    org_id: str, trigger_type: str, conversation_id: str | None, event_payload: dict
) -> list[str]:
    """
    Evaluate trigger criteria and enqueue matched workflows.
    """
    try:
        from app.repositories.workflow_repo import WorkflowRepository
        from app.tasks.workflow_tasks import execute_workflow

        repo = WorkflowRepository()
        workflows = repo.find_by_trigger(org_id, trigger_type)

        matched_workflow_ids = []
        for wf in workflows:
            if evaluate_trigger_config(wf.trigger_config, event_payload):
                logger.info("Trigger matched for workflow %s (%s)", wf.name, wf.id)
                # Dispatch execution asynchronously
                execute_workflow.delay(
                    workflow_id=str(wf.id),
                    conversation_id=conversation_id,
                    event_payload=event_payload,
                )
                matched_workflow_ids.append(str(wf.id))

        return matched_workflow_ids
    except Exception as exc:
        logger.exception("Failed matching workflows for trigger %s", trigger_type)
        return []


def evaluate_trigger_config(config: dict, event_payload: dict) -> bool:
    """
    Evaluate trigger criteria (e.g., keyword matches).
    """
    keywords = config.get("keywords", [])
    if keywords:
        body = event_payload.get("body", "").strip().lower()
        return any(k.lower() in body for k in keywords)
    return True
