"""
Integration tests for the Workflows engine.
"""
import pytest
from unittest.mock import MagicMock, patch
import uuid

from app.workflows.engine import WorkflowEngine
from app.workflows.state_machine import WorkflowState
from app.workflows.triggers import match_and_run_workflows

@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session


def test_workflow_ingestion_and_execution_flow(mock_db_session):
    # Step 1: Simulate trigger keyword matching
    with patch("app.repositories.workflow_repo.WorkflowRepository.find_by_trigger") as mock_find, \
         patch("app.tasks.workflow_tasks.execute_workflow.delay") as mock_delay:
        
        wf = MagicMock()
        wf.id = uuid.uuid4()
        wf.name = "Support Sequence"
        wf.trigger = "message_received"
        wf.trigger_config = {"keywords": ["billing", "invoice"]}
        wf.steps = [
            {"action": "update_context", "payload": {"billing_issue": True}},
            {"action": "wait", "payload": {"duration_seconds": 3600}}
        ]
        
        mock_find.return_value = [wf]
        
        # Trigger message matches
        matched = match_and_run_workflows(
            org_id=str(uuid.uuid4()),
            trigger_type="message_received",
            conversation_id="conv-123",
            event_payload={"body": "I have a billing question"}
        )
        
        assert len(matched) == 1
        assert matched[0] == str(wf.id)
        mock_delay.assert_called_once()

    # Step 2: Run the engine execution on matched steps
    res = WorkflowEngine.execute(
        workflow_id=str(wf.id),
        steps=wf.steps,
        conversation_id="conv-123",
        initial_context={"user_tier": "gold"}
    )

    # Verify state, context, and current step index
    assert res["status"] == "paused"
    assert res["current_step"] == 1
    assert res["context"]["user_tier"] == "gold"
    assert res["context"]["billing_issue"] is True
