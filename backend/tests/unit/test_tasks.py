"""
Unit tests for all Celery background tasks.
"""
import pytest
from unittest.mock import MagicMock, patch
import uuid

from app.tasks.ai_tasks import process_ai_message, generate_embedding
from app.tasks.analytics_tasks import compute_daily_metrics
from app.tasks.cleanup_tasks import cleanup_expired_ai_sessions, check_key_rotation
from app.tasks.followup_tasks import process_due_followups
from app.tasks.notification_tasks import send_critical_alert, send_notification
from app.tasks.sync_tasks import sync_external_data
from app.tasks.workflow_tasks import execute_workflow

from app.models.document import Document
from app.models.embedding import DocumentChunk
from app.models.organization import Organization
from app.models.ai_session import AISession
from app.models.encryption_metadata import EncryptionMetadata
from app.models.conversation import Conversation
from app.models.workflow import Workflow


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session


# --- AI Tasks ---

def test_process_ai_message_task():
    from unittest.mock import AsyncMock
    with patch("app.ai.orchestrator.router.AgentRouter") as mock_router_cls:
        mock_router = MagicMock()
        mock_router.route = AsyncMock()
        mock_router_cls.return_value = mock_router
        
        process_ai_message("conv-1", "msg-1", "Hello")
        mock_router.route.assert_called_once()


def test_generate_embedding_task(mock_db_session):
    from unittest.mock import AsyncMock
    with patch("app.ai.providers.provider_factory.ProviderFactory") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
        mock_factory.get_provider.return_value = mock_provider

        doc = MagicMock(spec=Document)
        mock_db_session.get.return_value = doc
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0

        doc_id = str(uuid.uuid4())
        res = generate_embedding(doc_id, "chunk text", "gemini")

        assert res["document_id"] == doc_id
        assert res["dimensions"] == 3
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


# --- Analytics Tasks ---

def test_compute_daily_metrics_task(mock_db_session):
    with patch("app.services.analytics_service.AnalyticsService.get_stats") as mock_get_stats:
        mock_get_stats.return_value = {"total_conversations": 5}
        
        org = MagicMock(spec=Organization)
        org.id = uuid.uuid4()
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [org]

        res = compute_daily_metrics()
        assert res["status"] == "success"
        assert res["organizations_processed"] == 1
        mock_get_stats.assert_called_once_with(str(org.id))


# --- Cleanup Tasks ---

def test_cleanup_expired_ai_sessions_task(mock_db_session):
    session = MagicMock(spec=AISession)
    session.status = "active"
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [session]

    res = cleanup_expired_ai_sessions()
    assert res["status"] == "success"
    assert res["expired_count"] == 1
    assert session.status == "expired"
    mock_db_session.commit.assert_called_once()


def test_check_key_rotation_task(mock_db_session):
    from datetime import datetime, timedelta, timezone
    meta = MagicMock(spec=EncryptionMetadata)
    meta.key_id = "key-v1"
    meta.last_rotated_at = datetime.now(timezone.utc) - timedelta(days=100)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = meta

    res = check_key_rotation()
    assert res["status"] == "success"
    assert res["rotation_recommended"] is True
    assert res["key_id"] == "key-v1"


# --- Followup Tasks ---

def test_process_due_followups_task(mock_db_session):
    conv = MagicMock(spec=Conversation)
    conv.status = "waiting"
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [conv]

    res = process_due_followups()
    assert res["status"] == "success"
    assert res["followups_triggered"] == 1
    assert conv.status == "active"
    mock_db_session.commit.assert_called_once()


# --- Notification Tasks ---

def test_send_critical_alert_task():
    with patch("app.services.notification_service.NotificationService.create_notification") as mock_create:
        notif = MagicMock()
        notif.id = uuid.uuid4()
        mock_create.return_value = notif

        res = send_critical_alert("org-1", "DB Down", "Main database is offline")
        assert res == str(notif.id)
        mock_create.assert_called_once()


def test_send_notification_task():
    with patch("app.services.notification_service.NotificationService.create_notification") as mock_create:
        notif = MagicMock()
        notif.id = uuid.uuid4()
        mock_create.return_value = notif

        res = send_notification("org-1", "Welcome", "Welcome to the team")
        assert res == str(notif.id)
        mock_create.assert_called_once()


# --- Sync Tasks ---

def test_sync_external_data_task():
    res = sync_external_data("org-1", "whatsapp")
    assert res["status"] == "success"
    assert res["organization_id"] == "org-1"
    assert res["resource_type"] == "whatsapp"


# --- Workflow Tasks ---

def test_execute_workflow_task(mock_db_session):
    wf = MagicMock(spec=Workflow)
    wf.id = uuid.uuid4()
    wf.name = "Test Workflow"
    wf.steps = [{"action": "send_whatsapp"}]
    wf.run_count = 0
    mock_db_session.get.return_value = wf

    wf_id = str(wf.id)
    res = execute_workflow(wf_id, conversation_id=str(uuid.uuid4()))
    assert res["status"] == "success"
    assert res["workflow_id"] == wf_id
    assert wf.run_count == 1
    mock_db_session.commit.assert_called()
