"""
Integration tests for the WhatsApp ingestion flows.
"""
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_user_repo():
    with patch("app.repositories.user_repo.UserRepository.find_active_by_id") as mock_find:
        user = MagicMock()
        user.is_active = True
        mock_find.return_value = user
        yield mock_find


def test_whatsapp_webhook_verification(real_app):
    client = real_app.test_client()

    with patch("app.services.whatsapp_service.WhatsAppService.verify_token") as mock_verify:
        mock_verify.side_effect = lambda t: t == "verify-token"

        # Success: Mode subscribe + valid token
        # (verify-token from ApiTestSettings in conftest is "verify-token")
        resp = client.get(
            "/api/v1/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=verify-token&hub.challenge=12345"
        )
        assert resp.status_code == 200
        assert resp.data.decode() == "12345"

        # Failure: Invalid verify token
        resp = client.get(
            "/api/v1/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=wrong-token&hub.challenge=12345"
        )
        assert resp.status_code == 403


def test_whatsapp_webhook_ingestion(real_app):
    client = real_app.test_client()

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "waba_id_123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "16505553333",
                                "phone_number_id": "phone_id_123"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Jane Doe"
                                    },
                                    "wa_id": "16505551111"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551111",
                                    "id": "wamid.ABGGFlg5F",
                                    "timestamp": "1604924400",
                                    "text": {
                                        "body": "Hello World"
                                    },
                                    "type": "text"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    # Verify signature passes and processes inbound task enqueuing
    with patch("app.services.whatsapp_service.WhatsAppService.verify_webhook_signature") as mock_sig, \
         patch("app.tasks.queue_tasks.process_inbound_message_task.delay") as mock_task:
        mock_sig.return_value = True

        resp = client.post(
            "/api/v1/webhooks/whatsapp",
            json=payload,
            headers={"X-Hub-Signature-256": "sha256=dummysig"}
        )
        
        assert resp.status_code == 200
        assert resp.json["status"] == "ok"
        assert resp.json["processed"] == 1
        mock_task.assert_called_once()
