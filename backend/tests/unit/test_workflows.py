"""
Unit tests for all backend workflows logic.
"""
import pytest
from unittest.mock import MagicMock, patch
import uuid

from app.workflows.state_machine import WorkflowStateMachine, WorkflowState
from app.workflows.engine import WorkflowEngine
from app.workflows.executors import (
    get_executor,
    update_context_executor,
    wait_executor,
    send_message_executor,
    create_ticket_executor,
)
from app.workflows.triggers import match_and_run_workflows, evaluate_trigger_config

from app.workflows.definitions.appointment_booking import get_definition as get_booking
from app.workflows.definitions.followup import get_definition as get_followup
from app.workflows.definitions.lead_qualification import get_definition as get_lead
from app.workflows.definitions.onboarding import get_definition as get_onboard
from app.workflows.definitions.support_ticket import get_definition as get_support


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session


# --- Definitions Loader Test ---

def test_workflow_definitions():
    assert get_booking()["trigger"] == "message_received"
    assert get_followup()["name"] == "Inactive Contact Follow-up"
    assert get_lead()["name"] == "Lead Qualification"
    assert get_onboard()["name"] == "Customer Onboarding Sequence"
    assert get_support()["steps"][0]["action"] == "create_ticket"


# --- State Machine Test ---

def test_workflow_state_machine():
    sm = WorkflowStateMachine(workflow_id="wf-123", context={"a": 1})
    assert sm.state == WorkflowState.PENDING
    assert sm.context == {"a": 1}

    sm.start()
    assert sm.state == WorkflowState.RUNNING
    assert sm.current_step_index == 0

    sm.transition_to(WorkflowState.COMPLETED)
    assert sm.state == WorkflowState.COMPLETED

    step = sm.next_step()
    assert step == 1
    assert sm.current_step_index == 1


# --- Executors Test ---

def test_update_context_executor():
    ctx = {"user": "pranav"}
    res = update_context_executor({"role": "admin"}, conversation_id=None, context=ctx)
    assert res["status"] == "success"
    assert ctx["role"] == "admin"


def test_wait_executor():
    ctx = {}
    res = wait_executor({"duration_seconds": 60}, conversation_id=None, context=ctx)
    assert res["status"] == "paused"
    assert res["duration_seconds"] == 60


def test_skipped_executors():
    # Calling executors without conversation should gracefully skip
    res1 = send_message_executor({"body": "hi"}, conversation_id=None, context={})
    assert res1["status"] == "skipped"

    res2 = create_ticket_executor({"title": "help"}, conversation_id=None, context={})
    assert res2["status"] == "skipped"


# --- Workflow Triggers Test ---

def test_evaluate_trigger_config():
    # Matched keywords
    config = {"keywords": ["error", "bug"]}
    assert evaluate_trigger_config(config, {"body": "Found a critical bug!"}) is True
    assert evaluate_trigger_config(config, {"body": "Everything is fine."}) is False

    # No keywords configured
    assert evaluate_trigger_config({}, {"body": "hello"}) is True


def test_match_and_run_workflows():
    with patch("app.repositories.workflow_repo.WorkflowRepository.find_by_trigger") as mock_find, \
         patch("app.tasks.workflow_tasks.execute_workflow.delay") as mock_delay:
        
        wf = MagicMock()
        wf.id = uuid.uuid4()
        wf.name = "Test Trigger Workflow"
        wf.trigger_config = {"keywords": ["alert"]}
        mock_find.return_value = [wf]

        org_id = str(uuid.uuid4())
        res = match_and_run_workflows(
            org_id=org_id,
            trigger_type="message_received",
            conversation_id="conv-1",
            event_payload={"body": "Send an alert now!"}
        )

        assert res == [str(wf.id)]
        mock_delay.assert_called_once()


# --- Workflow Engine Test ---

def test_workflow_engine_execution():
    steps = [
        {"action": "update_context", "payload": {"foo": "bar"}},
        {"action": "wait", "payload": {"duration_seconds": 10}}
    ]

    wf_id = str(uuid.uuid4())
    res = WorkflowEngine.execute(wf_id, steps, conversation_id=None, initial_context={})

    assert res["status"] == "paused"
    assert res["current_step"] == 1
    assert res["context"]["foo"] == "bar"
