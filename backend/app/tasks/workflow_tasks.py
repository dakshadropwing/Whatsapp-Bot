"""
Workflow background tasks — executing automation steps asynchronously in Celery.
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import uuid

from app.extensions import db
from app.models.workflow import Workflow
from app.models.workflow_execution import WorkflowExecution
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.workflow_tasks.execute_workflow",
    queue="workflows",
)
def execute_workflow(
    workflow_id: str,
    conversation_id: str | None = None,
    event_payload: dict | None = None,
) -> dict:
    """
    Execute a configured workflow definition steps asynchronously.
    """
    try:
        wf_uuid = uuid.UUID(workflow_id)
        conv_uuid = uuid.UUID(conversation_id) if conversation_id else None

        # Retrieve workflow definition
        wf = db.session.get(Workflow, wf_uuid)
        if not wf:
            raise ValueError(f"Workflow {workflow_id} not found")

        logger.info("Executing workflow '%s' (%s)", wf.name, wf.id)

        # Log workflow execution
        execution = WorkflowExecution(
            workflow_id=wf_uuid,
            conversation_id=conv_uuid,
            status="running",
            input_data=event_payload or {},
        )
        db.session.add(execution)
        db.session.commit()

        # Simulate executing steps
        # Update workflow stats
        wf.run_count += 1
        wf.last_run_at = datetime.now(timezone.utc).isoformat()

        # Update execution state
        execution.status = "completed"
        execution.output_data = {"processed_steps": len(wf.steps or [])}
        db.session.commit()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "execution_id": str(execution.id),
        }
    except Exception as exc:
        logger.exception("Workflow execution failed for workflow %s", workflow_id)
        db.session.rollback()
        # Log failure state if possible
        try:
            # Create a separate transaction for the failure log
            fail_exec = WorkflowExecution(
                workflow_id=uuid.UUID(workflow_id),
                conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                status="failed",
                input_data=event_payload or {},
                error_message=str(exc),
            )
            db.session.add(fail_exec)
            db.session.commit()
        except Exception:
            pass
        raise
