"""
Unit tests for all Pydantic validation schemas.
"""
import pytest
import uuid
from pydantic import ValidationError
from app.schemas import (
    AgentCreate,
    ConversationCreate,
    MessageCreate,
    TicketCreate,
    UserCreate,
    ClientCreate,
    LoginRequest,
)

def test_agent_schema_validation():
    # Valid input
    data = {
        "name": "Support Agent",
        "role_type": "support",
        "system_prompt": "You are a helpful assistant",
        "provider": "gemini",
        "model_name": "gemini-2.5-flash",
        "is_active": True
    }
    agent = AgentCreate(**data)
    assert agent.name == "Support Agent"
    assert agent.is_active is True

    # Invalid input
    with pytest.raises(ValidationError):
        AgentCreate(role_type="support") # Missing name & system_prompt

def test_conversation_schema_validation():
    data = {
        "contact_phone": "+123456789",
        "contact_wa_id": "wa-123",
        "whatsapp_account_id": uuid.uuid4(),
    }
    conv = ConversationCreate(**data)
    assert conv.contact_phone == "+123456789"
    assert conv.priority == "normal"

def test_message_schema_validation():
    data = {
        "direction": "inbound",
        "conversation_id": uuid.uuid4(),
    }
    msg = MessageCreate(**data)
    assert msg.direction.value == "inbound"
    assert msg.message_type.value == "text"

def test_ticket_schema_validation():
    data = {
        "title": "Help with login",
        "description": "Cannot login",
    }
    ticket = TicketCreate(**data)
    assert ticket.title == "Help with login"

def test_user_schema_validation():
    data = {
        "email": "user@corp.com",
        "username": "user123",
        "full_name": "John Doe",
        "password": "securepassword",
    }
    user = UserCreate(**data)
    assert user.email == "user@corp.com"

def test_client_schema_validation():
    data = {
        "name": "Jane Customer",
        "phone": "+199988877",
    }
    client = ClientCreate(**data)
    assert client.name == "Jane Customer"

def test_login_schema_validation():
    # Valid
    data = {"email": "test@corp.com", "password": "password123"}
    req = LoginRequest(**data)
    assert req.email == "test@corp.com"

    # Invalid password length
    with pytest.raises(ValidationError):
        LoginRequest(email="test@corp.com", password="123")
