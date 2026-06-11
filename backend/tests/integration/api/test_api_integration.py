"""
Integration tests for the API layer.
Tests multi-request user journeys.
"""
import pytest
from unittest.mock import MagicMock, patch
import uuid

from app.models.client import Client
from app.models.prompt_template import PromptTemplate

@pytest.fixture(autouse=True)
def mock_user_repo(test_org_id):
    with patch("app.repositories.user_repo.UserRepository.find_active_by_id") as mock_find:
        user = MagicMock()
        user.is_active = True
        user.organization_id = uuid.UUID(test_org_id)
        mock_find.return_value = user
        yield mock_find


def test_client_and_prompt_management_journey(real_app, test_headers, mock_db_session):
    client = real_app.test_client()

    # Step 1: Create a Client
    created_client = MagicMock(spec=Client)
    created_client.id = uuid.uuid4()
    created_client.name = "John Doe"
    created_client.email = "john@example.com"
    created_client.phone = "+1111"
    created_client.company = "Corp"
    created_client.tags = []
    created_client.created_at = None
    created_client.updated_at = None

    with patch("app.services.client_service.ClientService.create_client") as mock_create_client:
        mock_create_client.return_value = created_client
        
        resp = client.post(
            "/api/v1/clients/",
            json={"name": "John Doe", "email": "john@example.com", "phone": "+1111"},
            headers=test_headers
        )
        assert resp.status_code == 201
        assert resp.json["name"] == "John Doe"

    # Step 2: List Clients and verify
    with patch("app.services.client_service.ClientService.list_clients") as mock_list_clients:
        mock_list_clients.return_value = {
            "data": [
                {
                    "id": str(created_client.id),
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1111"
                }
            ],
            "total": 1
        }
        
        resp = client.get("/api/v1/clients/", headers=test_headers)
        assert resp.status_code == 200
        assert resp.json["total"] == 1
        assert resp.json["data"][0]["name"] == "John Doe"

    # Step 3: Create a Prompt Template
    created_prompt = MagicMock(spec=PromptTemplate)
    created_prompt.id = uuid.uuid4()
    created_prompt.name = "sales_helper"
    created_prompt.category = "sales"

    with patch("app.services.prompt_service.PromptService.create_prompt") as mock_create_prompt:
        mock_create_prompt.return_value = created_prompt
        
        resp = client.post(
            "/api/v1/prompts/",
            json={"name": "sales_helper", "system_prompt": "Help pitch"},
            headers=test_headers
        )
        assert resp.status_code == 201
        assert resp.json["name"] == "sales_helper"
