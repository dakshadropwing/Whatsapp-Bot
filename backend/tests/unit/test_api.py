"""
Unit tests for all 15 implemented Flask API Blueprints.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import uuid
from flask import g
from flask_jwt_extended import create_access_token

from app.core.config.settings import Settings
from app.models.whatsapp_account import WhatsAppAccount
from app.models.message import Message, MessageDirection, MessageType, MessageStatus
from app.models.conversation import Conversation, ConversationStatus
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.ai_agent import AIAgent
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document, SourceType, DocumentStatus
from app.models.client import Client
from app.models.employee import Employee
from app.models.user import User
from app.models.workflow import Workflow
from app.models.endpoint_config import EndpointConfig
from app.models.prompt_template import PromptTemplate
from app.models.organization import Organization
from app.models.audit_log import AuditLog

class ApiTestSettings(Settings):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"
    JWT_SECRET_KEY: str = "test-secret-key"
    WHATSAPP_ACCESS_TOKEN: str = "fake-token"
    WHATSAPP_PHONE_NUMBER_ID: str = "fake-phone"
    WHATSAPP_API_VERSION: str = "v18.0"
    WHATSAPP_API_BASE_URL: str = "https://graph.facebook.com"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = "verify-token"
    APP_SECRET_KEY: str = "app-secret"

@pytest.fixture
def app():
    from app.factory import create_app
    settings = ApiTestSettings()
    app = create_app(settings)
    return app

@pytest.fixture
def org_id():
    return "00000000-0000-0000-0000-000000000001"

@pytest.fixture
def token(app, org_id):
    with app.app_context():
        return create_access_token(
            identity="test-user",
            additional_claims={"org_id": org_id, "role": "admin"}
        )

@pytest.fixture
def headers(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session

@pytest.fixture(autouse=True)
def mock_user_repo(org_id):
    with patch("app.repositories.user_repo.UserRepository.find_active_by_id") as mock_find:
        user = MagicMock()
        user.is_active = True
        user.organization_id = uuid.UUID(org_id)
        mock_find.return_value = user
        yield mock_find


# ── 1. WhatsApp Routes Tests ──────────────────────────────────

def test_verify_webhook(app):
    client = app.test_client()
    with patch("app.api.v1.whatsapp.routes._handler.handle_verification") as mock_verify:
        mock_verify.return_value = ("challenge_code", 200)
        resp = client.get("/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.challenge=challenge_code")
        assert resp.status_code == 200
        assert resp.data.decode() == "challenge_code"

def test_receive_webhook(app):
    client = app.test_client()
    with patch("app.api.v1.whatsapp.routes._handler.verify_signature") as mock_sig, \
         patch("app.api.v1.whatsapp.routes._handler.dispatch", new_callable=AsyncMock) as mock_dispatch:
        mock_sig.return_value = True
        resp = client.post("/api/v1/whatsapp/webhook", json={"object": "whatsapp_business_account"})
        assert resp.status_code == 200
        assert resp.json == {"status": "ok"}
        mock_dispatch.assert_called_once()

def test_list_accounts(app, headers, org_id, mock_db_session):
    client = app.test_client()
    acc = MagicMock(spec=WhatsAppAccount)
    acc.id = uuid.uuid4()
    acc.phone_number_id = "12345"
    acc.waba_id = "67890"
    acc.is_active = True

    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [acc]

    resp = client.get("/api/v1/whatsapp/accounts", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json["accounts"]) == 1
    assert resp.json["accounts"][0]["phone_number_id"] == "12345"

def test_send_message(app, headers):
    client = app.test_client()
    with patch("app.integrations.whatsapp.client.WhatsAppClient.send_text", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"messages": [{"id": "wamid.test_send"}]}
        resp = client.post("/api/v1/whatsapp/send", json={"phone": "+1234", "message": "hello"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json["sent"] is True
        assert resp.json["message_id"] == "wamid.test_send"


# ── 2. Conversations Routes Tests ──────────────────────────────

@patch("app.services.conversation_service.ConversationService.list_conversations")
def test_list_conversations(mock_list, app, headers):
    client = app.test_client()
    mock_list.return_value = {"data": [], "total": 0}
    resp = client.get("/api/v1/conversations/?status=active", headers=headers)
    assert resp.status_code == 200
    assert resp.json["total"] == 0

@patch("app.services.conversation_service.ConversationService.get_conversation")
def test_get_conversation(mock_get, app, headers, org_id):
    client = app.test_client()
    conv = MagicMock(spec=Conversation)
    conv.id = uuid.uuid4()
    conv.organization_id = uuid.UUID(org_id)
    conv.contact_phone = "+123"
    conv.contact_name = "Jane"
    conv.contact_wa_id = "jane_wa"
    conv.status = ConversationStatus.ACTIVE
    conv.channel = None
    conv.assigned_agent_id = None
    conv.assigned_user_id = None
    conv.priority = 1
    conv.message_count = 0
    conv.last_message_at = None
    conv.tags = []
    conv.created_at = None
    conv.updated_at = None

    mock_get.return_value = conv

    resp = client.get(f"/api/v1/conversations/{conv.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json["conversation"]["contact_name"] == "Jane"

@patch("app.services.conversation_service.ConversationService.get_conversation")
@patch("app.services.conversation_service.ConversationService.update_conversation")
def test_update_conversation(mock_update, mock_get, app, headers, org_id):
    client = app.test_client()
    conv = MagicMock(spec=Conversation)
    conv.organization_id = uuid.UUID(org_id)
    mock_get.return_value = conv

    updated = MagicMock(spec=Conversation)
    updated.id = uuid.uuid4()
    mock_update.return_value = updated

    resp = client.patch(f"/api/v1/conversations/{uuid.uuid4()}", json={"status": "resolved"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json["updated"] is True


@patch("app.services.conversation_service.ConversationService.get_conversation")
@patch("app.services.conversation_service.ConversationService.assign_conversation")
@patch("app.services.conversation_service.ConversationService.update_conversation")
def test_update_conversation_assignment(mock_update, mock_assign, mock_get, app, headers, org_id):
    client = app.test_client()
    conv = MagicMock(spec=Conversation)
    conv.organization_id = uuid.UUID(org_id)
    mock_get.return_value = conv

    updated = MagicMock(spec=Conversation)
    updated.id = uuid.uuid4()
    mock_assign.return_value = updated

    agent_id = str(uuid.uuid4())
    resp = client.patch(f"/api/v1/conversations/{uuid.uuid4()}", json={"assigned_agent_id": agent_id}, headers=headers)
    assert resp.status_code == 200
    assert resp.json["updated"] is True
    mock_assign.assert_called_once()


# ── 3. Messages Routes Tests ──────────────────────────────────

def test_list_messages(app, headers, org_id, mock_db_session):
    client = app.test_client()
    msg = MagicMock(spec=Message)
    msg.id = uuid.uuid4()
    msg.organization_id = uuid.UUID(org_id)
    msg.conversation_id = uuid.uuid4()
    msg.wa_message_id = "wa-1"
    msg.direction = MessageDirection.INBOUND
    msg.message_type = MessageType.TEXT
    msg.status = MessageStatus.READ
    msg.body = "ping"
    msg.media_url = None
    msg.ai_generated = False
    msg.tokens_used = None
    msg.processing_time_ms = None
    msg.created_at = None

    mock_db_session.execute.return_value.scalar.return_value = 1
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [msg]

    resp = client.get("/api/v1/messages/", headers=headers)
    assert resp.status_code == 200
    assert resp.json["total"] == 1
    assert resp.json["data"][0]["body"] == "ping"


# ── 4. Tickets Routes Tests ───────────────────────────────────

@patch("app.services.ticket_service.TicketService.create_support_ticket")
def test_create_ticket(mock_create, app, headers):
    client = app.test_client()
    ticket = MagicMock(spec=Ticket)
    ticket.id = uuid.uuid4()
    ticket.organization_id = uuid.uuid4()
    ticket.title = "Broken button"
    ticket.status = TicketStatus.OPEN
    ticket.priority = TicketPriority.MEDIUM

    mock_create.return_value = ticket

    resp = client.post("/api/v1/tickets/", json={"title": "Broken button"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json["title"] == "Broken button"


# ── 5. Agents Routes Tests ───────────────────────────────────

@patch("app.services.agent_service.AgentService.list_agents")
def test_list_agents(mock_list, app, headers):
    client = app.test_client()
    mock_list.return_value = {"data": [], "total": 0}
    resp = client.get("/api/v1/agents/", headers=headers)
    assert resp.status_code == 200
    assert resp.json["total"] == 0

@patch("app.services.agent_service.AgentService.get_agent")
@patch("app.services.agent_service.AgentService.toggle_agent")
def test_toggle_agent(mock_toggle, mock_get, app, headers, org_id):
    client = app.test_client()
    agent = MagicMock(spec=AIAgent)
    agent.organization_id = uuid.UUID(org_id)
    mock_get.return_value = agent

    toggled = MagicMock(spec=AIAgent)
    toggled.id = uuid.uuid4()
    toggled.is_active = False
    mock_toggle.return_value = toggled

    resp = client.post(f"/api/v1/agents/{uuid.uuid4()}/toggle", headers=headers)
    assert resp.status_code == 200
    assert resp.json["is_active"] is False


# ── 6. Analytics Routes Tests ─────────────────────────────────

@patch("app.services.analytics_service.AnalyticsService.get_stats")
def test_get_stats(mock_stats, app, headers):
    client = app.test_client()
    mock_stats.return_value = {"total_conversations": 10}
    resp = client.get("/api/v1/analytics/stats", headers=headers)
    assert resp.status_code == 200
    assert resp.json["total_conversations"] == 10


# ── 7. Knowledge Base Routes Tests ────────────────────────────

@patch("app.services.knowledge_base_service.KnowledgeBaseService.create_knowledge_base")
def test_create_knowledge_base(mock_create, app, headers):
    client = app.test_client()
    kb = MagicMock(spec=KnowledgeBase)
    kb.id = uuid.uuid4()
    kb.name = "My KB"
    kb.description = "Test description"

    mock_create.return_value = kb

    resp = client.post("/api/v1/knowledge-base/", json={"name": "My KB"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json["name"] == "My KB"

@patch("app.services.knowledge_base_service.KnowledgeBaseService.get_knowledge_base")
def test_upload_document(mock_get, app, headers, org_id, mock_db_session):
    client = app.test_client()
    kb = MagicMock(spec=KnowledgeBase)
    kb.organization_id = uuid.UUID(org_id)
    mock_get.return_value = kb

    with patch("app.tasks.ai_tasks.generate_embedding.delay") as mock_delay:
        resp = client.post(
            f"/api/v1/knowledge-base/{uuid.uuid4()}/documents",
            json={"name": "FAQ.txt", "raw_text": "Answers"},
            headers=headers
        )
        assert resp.status_code == 201
        assert resp.json["uploaded"] is True
        mock_delay.assert_called_once()


# ── 8. Clients Routes Tests ───────────────────────────────────

@patch("app.services.client_service.ClientService.list_clients")
def test_list_clients(mock_list, app, headers):
    client = app.test_client()
    mock_list.return_value = {"data": [], "total": 0}
    resp = client.get("/api/v1/clients/", headers=headers)
    assert resp.status_code == 200
    assert resp.json["total"] == 0


# ── 9. Employees Routes Tests ─────────────────────────────────

@patch("app.services.employee_service.EmployeeService.create_employee")
def test_create_employee(mock_create, app, headers):
    client = app.test_client()
    emp = MagicMock(spec=Employee)
    emp.id = uuid.uuid4()
    emp.name = "Alice"
    emp.email = "alice@company.com"
    emp.role = "agent"

    mock_create.return_value = emp

    resp = client.post("/api/v1/employees/", json={"name": "Alice", "email": "alice@company.com"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json["name"] == "Alice"


# ── 10. Users Routes Tests ────────────────────────────────────

@patch("app.services.user_service.UserService.get_user")
@patch("app.services.user_service.UserService.deactivate_user")
def test_delete_user(mock_deactivate, mock_get, app, headers, org_id):
    client = app.test_client()
    user = MagicMock(spec=User)
    user.organization_id = uuid.UUID(org_id)
    mock_get.return_value = user

    deactivated = MagicMock(spec=User)
    mock_deactivate.return_value = deactivated

    resp = client.delete(f"/api/v1/users/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 200
    assert resp.json["deleted"] is True


# ── 11. Workflows Routes Tests ────────────────────────────────

@patch("app.services.workflow_service.WorkflowService.create_workflow")
def test_create_workflow(mock_create, app, headers):
    client = app.test_client()
    wf = MagicMock(spec=Workflow)
    wf.id = uuid.uuid4()
    wf.name = "Lead Gen"
    wf.trigger = "keyword"
    wf.is_active = True

    mock_create.return_value = wf

    resp = client.post("/api/v1/workflows/", json={"name": "Lead Gen", "trigger": "keyword"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json["name"] == "Lead Gen"


# ── 12. Endpoints Routes Tests ────────────────────────────────

def test_create_endpoint(app, headers, mock_db_session):
    client = app.test_client()
    resp = client.post("/api/v1/endpoints/", json={"name": "crm", "url": "https://crm.com/api"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json["name"] == "crm"
    mock_db_session.add.assert_called_once()

@patch("app.services.endpoint_service.EndpointService.dispatch")
def test_test_endpoint(mock_dispatch, app, headers, org_id, mock_db_session):
    client = app.test_client()
    endpoint = MagicMock(spec=EndpointConfig)
    endpoint.organization_id = uuid.UUID(org_id)
    endpoint.name = "crm"
    mock_db_session.get.return_value = endpoint

    mock_dispatch.return_value = {"success": True, "status_code": 200, "body": "OK"}

    resp = client.post(f"/api/v1/endpoints/{uuid.uuid4()}/test", json={"payload": {}}, headers=headers)
    assert resp.status_code == 200
    assert resp.json["success"] is True


# ── 13. Prompts Routes Tests ──────────────────────────────────

@patch("app.services.prompt_service.PromptService.create_prompt")
def test_create_prompt(mock_create, app, headers):
    client = app.test_client()
    p = MagicMock(spec=PromptTemplate)
    p.id = uuid.uuid4()
    p.name = "welcome"
    p.category = "support"

    mock_create.return_value = p

    resp = client.post("/api/v1/prompts/", json={"name": "welcome", "system_prompt": "Hello"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json["name"] == "welcome"


# ── 14. Settings Routes Tests ─────────────────────────────────

def test_get_settings(app, headers, org_id, mock_db_session):
    client = app.test_client()
    org = MagicMock(spec=Organization)
    org.settings = {"ai": {"default_model": "custom-model"}}
    mock_db_session.get.return_value = org

    resp = client.get("/api/v1/settings/", headers=headers)
    assert resp.status_code == 200
    assert resp.json["ai"]["default_model"] == "custom-model"
    assert resp.json["whatsapp"]["phone_number_id"] == "" # default merged

def test_update_settings(app, headers, org_id, mock_db_session):
    client = app.test_client()
    org = MagicMock(spec=Organization)
    org.settings = {}
    mock_db_session.get.return_value = org

    with patch("app.api.v1.settings.routes.flag_modified") as mock_flag:
        resp = client.patch("/api/v1/settings/", json={"ai": {"max_tokens": 100}}, headers=headers)
        assert resp.status_code == 200
        assert resp.json["updated"] is True
        assert org.settings["ai"]["max_tokens"] == 100


# ── 15. Audit Routes Tests ────────────────────────────────────

@patch("app.services.audit_service.AuditService.list_logs")
def test_list_audit(mock_list, app, headers):
    client = app.test_client()
    mock_list.return_value = {"data": [], "total": 0}
    resp = client.get("/api/v1/audit/", headers=headers)
    assert resp.status_code == 200
    assert resp.json["total"] == 0
