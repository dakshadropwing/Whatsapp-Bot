"""
Unit tests for all 12 backend repositories.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.models.ai_agent import AIAgent
from app.models.audit_log import AuditLog
from app.models.client import Client
from app.models.conversation import Conversation, ConversationStatus
from app.models.endpoint_config import EndpointConfig
from app.models.knowledge_base import KnowledgeBase
from app.models.message import Message, MessageStatus
from app.models.prompt_template import PromptTemplate
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User
from app.models.workflow import Workflow

from app.repositories.agent_repo import AgentRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.client_repo import ClientRepository
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.endpoint_repo import EndpointRepository
from app.repositories.knowledge_base_repo import KnowledgeBaseRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.prompt_repo import PromptRepository
from app.repositories.ticket_repo import TicketRepository
from app.repositories.user_repo import UserRepository
from app.repositories.workflow_repo import WorkflowRepository


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session


# --- Agent Repository Tests ---

def test_agent_repo_instantiation():
    repo = AgentRepository()
    assert repo.model == AIAgent


def test_agent_repo_methods(mock_db_session):
    repo = AgentRepository()
    mock_agent = MagicMock(spec=AIAgent)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_agent]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_agent]
    assert repo.find_active_by_organization("org-1") == [mock_agent]
    assert repo.find_by_role_type("org-1", "support") == [mock_agent]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_agent
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_name("org-1", "Agent Smith") == mock_agent


# --- Audit Repository Tests ---

def test_audit_repo_instantiation():
    repo = AuditRepository()
    assert repo.model == AuditLog


def test_audit_repo_methods(mock_db_session):
    repo = AuditRepository()
    mock_log = MagicMock(spec=AuditLog)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_log]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1", action="create", resource_type="agent") == [mock_log]
    assert repo.find_by_user("user-1") == [mock_log]
    assert repo.find_by_resource("agent", "agent-1") == [mock_log]

    # Mock scalar() for count
    mock_result_scalar = MagicMock()
    mock_result_scalar.scalar.return_value = 42
    mock_db_session.execute.return_value = mock_result_scalar

    assert repo.count_by_organization("org-1") == 42


# --- Client Repository Tests ---

def test_client_repo_instantiation():
    repo = ClientRepository()
    assert repo.model == Client


def test_client_repo_methods(mock_db_session):
    repo = ClientRepository()
    mock_client = MagicMock(spec=Client)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_client]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_client]
    assert repo.search("org-1", "search-term") == [mock_client]
    assert repo.find_by_tag("org-1", "VIP") == [mock_client]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_client
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_phone("org-1", "+123456") == mock_client
    assert repo.find_by_email("org-1", "test@domain.com") == mock_client


# --- Endpoint Repository Tests ---

def test_endpoint_repo_instantiation():
    repo = EndpointRepository()
    assert repo.model == EndpointConfig


def test_endpoint_repo_methods(mock_db_session):
    repo = EndpointRepository()
    mock_endpoint = MagicMock(spec=EndpointConfig)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_endpoint]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_endpoint]
    assert repo.find_active_by_organization("org-1") == [mock_endpoint]
    assert repo.find_active_by_method("org-1", "POST") == [mock_endpoint]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_endpoint
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_name("org-1", "endpoint-name") == mock_endpoint


# --- Knowledge Base Repository Tests ---

def test_kb_repo_instantiation():
    repo = KnowledgeBaseRepository()
    assert repo.model == KnowledgeBase


def test_kb_repo_methods(mock_db_session):
    repo = KnowledgeBaseRepository()
    mock_kb = MagicMock(spec=KnowledgeBase)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_kb]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_kb]
    assert repo.find_active_by_organization("org-1") == [mock_kb]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_kb
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_name("org-1", "kb-name") == mock_kb

    # Mock scalar() for document count
    mock_result_scalar = MagicMock()
    mock_result_scalar.scalar.return_value = 5
    mock_db_session.execute.return_value = mock_result_scalar

    assert repo.count_documents("kb-1") == 5


# --- Prompt Repository Tests ---

def test_prompt_repo_instantiation():
    repo = PromptRepository()
    assert repo.model == PromptTemplate


def test_prompt_repo_methods(mock_db_session):
    repo = PromptRepository()
    mock_prompt = MagicMock(spec=PromptTemplate)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_prompt]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_prompt]
    assert repo.find_by_category("org-1", "general") == [mock_prompt]
    assert repo.find_active_by_organization("org-1") == [mock_prompt]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_prompt
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_name("org-1", "prompt-name") == mock_prompt


# --- Ticket Repository Tests ---

def test_ticket_repo_instantiation():
    repo = TicketRepository()
    assert repo.model == Ticket


def test_ticket_repo_methods(mock_db_session):
    repo = TicketRepository()
    mock_ticket = MagicMock(spec=Ticket)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_ticket]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1", status=TicketStatus.OPEN, priority=TicketPriority.HIGH) == [mock_ticket]
    assert repo.find_by_conversation("conv-1") == [mock_ticket]
    assert repo.find_by_assignee("user-1") == [mock_ticket]

    # Mock scalar() for open tickets count
    mock_result_scalar = MagicMock()
    mock_result_scalar.scalar.return_value = 10
    mock_db_session.execute.return_value = mock_result_scalar

    assert repo.count_open_by_organization("org-1") == 10

    # Mock all() for status grouping
    mock_row = MagicMock()
    mock_row.status = TicketStatus.OPEN
    mock_row.cnt = 3
    mock_db_session.execute.return_value.all.return_value = [mock_row]

    assert repo.count_by_status("org-1") == {"open": 3}


# --- Workflow Repository Tests ---

def test_workflow_repo_instantiation():
    repo = WorkflowRepository()
    assert repo.model == Workflow


def test_workflow_repo_methods(mock_db_session):
    repo = WorkflowRepository()
    mock_workflow = MagicMock(spec=Workflow)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_workflow]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_workflow]
    assert repo.find_active_by_organization("org-1") == [mock_workflow]
    assert repo.find_by_trigger("org-1", "message_received") == [mock_workflow]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_workflow
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_name("org-1", "workflow-name") == mock_workflow


# --- Conversation Repository Tests ---

def test_conversation_repo_instantiation():
    repo = ConversationRepository()
    assert repo.model == Conversation


def test_conversation_repo_methods(mock_db_session):
    repo = ConversationRepository()
    mock_conv = MagicMock(spec=Conversation)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_conv]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1", ConversationStatus.ACTIVE) == [mock_conv]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_conv
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_phone("+123456") == mock_conv
    assert repo.find_active_by_phone("+123456") == mock_conv


# --- Message Repository Tests ---

def test_message_repo_instantiation():
    repo = MessageRepository()
    assert repo.model == Message


def test_message_repo_methods(mock_db_session):
    repo = MessageRepository()
    mock_msg = MagicMock(spec=Message)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_msg]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_conversation("conv-1", limit=10) == [mock_msg]
    assert repo.find_failed_by_organization("org-1") == [mock_msg]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_msg
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_wa_message_id("wa-id") == mock_msg

    # Mock scalar() for message count
    mock_result_scalar = MagicMock()
    mock_result_scalar.scalar.return_value = 150
    mock_db_session.execute.return_value = mock_result_scalar

    assert repo.count_by_conversation("conv-1") == 150


# --- User Repository Tests ---

def test_user_repo_instantiation():
    repo = UserRepository()
    assert repo.model == User


def test_user_repo_methods(mock_db_session):
    repo = UserRepository()
    mock_user = MagicMock(spec=User)

    # Mock scalars().all()
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_user]
    mock_db_session.execute.return_value = mock_result_all

    assert repo.find_by_organization("org-1") == [mock_user]

    # Mock scalar_one_or_none()
    mock_result_one = MagicMock()
    mock_result_one.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result_one

    assert repo.find_by_email("TEST@domain.com") == mock_user
    assert repo.find_active_by_id("user-1") == mock_user
