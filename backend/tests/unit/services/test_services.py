"""
Unit tests for all backend services.
"""
import pytest
from unittest.mock import MagicMock, patch
import uuid
from datetime import datetime

from app.models.conversation import Conversation, ConversationStatus
from app.models.client import Client
from app.models.user import User
from app.models.workflow import Workflow
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.employee import Employee
from app.models.knowledge_base import KnowledgeBase
from app.models.prompt_template import PromptTemplate

from app.services.conversation_service import ConversationService
from app.services.client_service import ClientService
from app.services.user_service import UserService
from app.services.workflow_service import WorkflowService
from app.services.ticket_service import TicketService
from app.services.employee_service import EmployeeService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.prompt_service import PromptService


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session


# --- Conversation Service ---

def test_conversation_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Get conversation
    conv = MagicMock(spec=Conversation)
    mock_db_session.get.return_value = conv
    assert ConversationService.get_conversation(conv_id) == conv

    # Assign conversation
    assert ConversationService.assign_conversation(conv_id, assigned_user_id=user_id) == conv
    assert conv.status == ConversationStatus.HUMAN_HANDLING
    mock_db_session.commit.assert_called()


# --- Client Service ---

def test_client_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    client_id = str(uuid.uuid4())

    # Get client
    client = MagicMock(spec=Client)
    mock_db_session.get.return_value = client
    assert ClientService.get_client(client_id) == client

    # Create client
    ClientService.create_client(org_id, name="Alice", email="alice@corp.com", phone="+123")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()


# --- User Service ---

def test_user_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Get user
    user = MagicMock(spec=User)
    mock_db_session.get.return_value = user
    assert UserService.get_user(user_id) == user

    # Deactivate user
    assert UserService.deactivate_user(user_id) == user
    assert user.is_active is False
    mock_db_session.commit.assert_called()


# --- Workflow Service ---

def test_workflow_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    wf_id = str(uuid.uuid4())

    # Get workflow
    wf = MagicMock(spec=Workflow)
    mock_db_session.get.return_value = wf
    assert WorkflowService.get_workflow(wf_id) == wf

    # Toggle workflow
    wf.is_active = True
    assert WorkflowService.toggle_workflow(wf_id) == wf
    assert wf.is_active is False
    mock_db_session.commit.assert_called()


# --- Ticket Service ---

def test_ticket_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    ticket_id = str(uuid.uuid4())

    # Create ticket
    TicketService.create_support_ticket(org_id, title="Help", description="issue")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()

    # Update ticket status
    ticket = MagicMock(spec=Ticket)
    mock_db_session.get.return_value = ticket
    assert TicketService.update_ticket_status(ticket_id, "resolved") == ticket
    assert ticket.status == TicketStatus.RESOLVED


# --- Employee Service ---

def test_employee_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    emp_id = str(uuid.uuid4())

    # Get employee
    emp = MagicMock(spec=Employee)
    mock_db_session.get.return_value = emp
    assert EmployeeService.get_employee(emp_id) == emp

    # Create employee
    EmployeeService.create_employee(org_id, name="Bob", email="bob@corp.com")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()


# --- Knowledge Base Service ---

def test_kb_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    kb_id = str(uuid.uuid4())

    # Get KB
    kb = MagicMock(spec=KnowledgeBase)
    mock_db_session.get.return_value = kb
    assert KnowledgeBaseService.get_knowledge_base(kb_id) == kb


# --- Prompt Service ---

def test_prompt_service_methods(mock_db_session):
    org_id = str(uuid.uuid4())
    prompt_id = str(uuid.uuid4())

    # Get prompt
    p = MagicMock(spec=PromptTemplate)
    mock_db_session.get.return_value = p
    assert PromptService.get_prompt(prompt_id) == p
