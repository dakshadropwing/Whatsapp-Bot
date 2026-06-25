from __future__ import annotations

import datetime
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.models.conversation import ConversationStatus, ConversationChannel


class ConversationBase(BaseModel):
    contact_phone: str = Field(..., max_length=20)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_wa_id: str = Field(..., max_length=50)
    status: ConversationStatus = ConversationStatus.ACTIVE
    channel: ConversationChannel = ConversationChannel.WHATSAPP
    assigned_agent_id: Optional[uuid.UUID] = None
    assigned_user_id: Optional[uuid.UUID] = None
    context: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    priority: str = Field("normal", max_length=20)


class ConversationCreate(ConversationBase):
    whatsapp_account_id: uuid.UUID


class ConversationUpdate(BaseModel):
    contact_name: Optional[str] = Field(None, max_length=255)
    status: Optional[ConversationStatus] = None
    channel: Optional[ConversationChannel] = None
    assigned_agent_id: Optional[uuid.UUID] = None
    assigned_user_id: Optional[uuid.UUID] = None
    context: Optional[dict] = None
    tags: Optional[List[str]] = None
    priority: Optional[str] = Field(None, max_length=20)


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    whatsapp_account_id: uuid.UUID
    message_count: int
    last_message_at: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
