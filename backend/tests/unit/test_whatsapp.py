"""
Unit tests for WhatsApp integration components.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import uuid

from app.integrations.whatsapp.webhook_handler import WebhookHandler
from app.integrations.whatsapp.human_handoff import escalate_to_human
from app.integrations.whatsapp.interactive import (
    build_button_message,
    build_list_message,
    parse_interactive_reply,
)
from app.integrations.whatsapp.media_handler import MediaHandler
from app.integrations.whatsapp.template_manager import (
    build_template_payload,
    build_text_parameter,
)
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageStatus


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session


# --- Interactive Message Tests ---

def test_interactive_builders():
    # Buttons
    btn_msg = build_button_message(
        body_text="Choose one",
        buttons=[{"id": "y", "title": "Yes"}, {"id": "n", "title": "No"}]
    )
    assert btn_msg["type"] == "interactive"
    assert btn_msg["interactive"]["type"] == "button"
    assert len(btn_msg["interactive"]["action"]["buttons"]) == 2

    # Lists
    sections = [{"title": "Header", "rows": [{"id": "r1", "title": "Row 1"}]}]
    list_msg = build_list_message(
        body_text="Choose list item",
        button_label="Menu",
        sections=sections
    )
    assert list_msg["type"] == "interactive"
    assert list_msg["interactive"]["type"] == "list"
    assert list_msg["interactive"]["action"]["button"] == "Menu"


def test_parse_interactive_reply():
    # Button Reply
    payload_btn = {
        "type": "interactive",
        "interactive": {
            "type": "button_reply",
            "button_reply": {"id": "btn_1", "title": "Yes"}
        }
    }
    parsed = parse_interactive_reply(payload_btn)
    assert parsed == {"id": "btn_1", "title": "Yes"}

    # Text message (should be None)
    payload_txt = {"type": "text", "text": {"body": "hello"}}
    assert parse_interactive_reply(payload_txt) is None


# --- Template Manager Tests ---

def test_template_payload_builders():
    params = [build_text_parameter("Pranav")]
    payload = build_template_payload(
        template_name="welcome_user",
        language_code="en_US",
        components=[{"type": "body", "parameters": params}]
    )
    assert payload["type"] == "template"
    assert payload["template"]["name"] == "welcome_user"
    assert payload["template"]["components"][0]["parameters"][0]["text"] == "Pranav"


# --- Media Handler Tests ---

def test_media_download_upload():
    handler = MediaHandler(access_token="test-token")
    
    with patch("requests.get") as mock_get:
        # Mock metadata response
        mock_meta = MagicMock()
        mock_meta.status_code = 200
        mock_meta.json.return_value = {"url": "https://cdn.whatsapp.com/123", "mime_type": "image/png"}
        
        # Mock binary response
        mock_bin = MagicMock()
        mock_bin.status_code = 200
        mock_bin.content = b"imagebytes"
        
        mock_get.side_effect = [mock_meta, mock_bin]

        res = handler.download_media("media-id-123")
        assert res["data"] == b"imagebytes"
        assert res["mime_type"] == "image/png"

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "uploaded-media-999"}
        mock_post.return_value = mock_resp

        res = handler.upload_media("phone-id", b"filebytes", "image/png", "file.png")
        assert res == "uploaded-media-999"


# --- Human Handoff Tests ---

def test_human_handoff(mock_db_session):
    conv = MagicMock(spec=Conversation)
    conv.organization_id = uuid.uuid4()
    conv.status = ConversationStatus.BOT_HANDLING
    conv.contact_phone = "+123456"
    conv.contact_name = "Pranav"
    mock_db_session.get.return_value = conv

    with patch("app.services.ticket_service.TicketService.create_support_ticket") as mock_ticket, \
         patch("app.tasks.notification_tasks.send_critical_alert.delay") as mock_alert:
        
        conv_id = str(uuid.uuid4())
        res = escalate_to_human(conv_id, reason="Requested human assistant")
        
        assert res is True
        assert conv.status == ConversationStatus.HUMAN_HANDLING
        mock_ticket.assert_called_once()
        mock_alert.assert_called_once()
        mock_db_session.commit.assert_called_once()


# --- Webhook Handler Status Dispatch Test ---

@pytest.mark.asyncio
async def test_webhook_status_dispatch(mock_db_session):
    handler = WebhookHandler()
    
    msg = MagicMock(spec=Message)
    msg.status = MessageStatus.PENDING
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = msg

    payload = {
        "entry": [{
            "changes": [{
                "field": "statuses",
                "value": {
                    "statuses": [{
                        "id": "wa-msg-id-123",
                        "status": "delivered"
                    }]
                }
            }]
        }]
    }

    await handler.dispatch(payload)
    assert msg.status == MessageStatus.DELIVERED
    mock_db_session.commit.assert_called_once()
