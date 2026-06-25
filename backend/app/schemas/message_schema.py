from __future__ import annotations

import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.message import MessageDirection, MessageType, MessageStatus


class MessageBase(BaseModel):
    direction: MessageDirection
    message_type: MessageType = MessageType.TEXT
    status: MessageStatus = MessageStatus.PENDING
    body: Optional[str] = None
    media_url: Optional[str] = Field(None, max_length=2000)
    media_type: Optional[str] = Field(None, max_length=100)
    media_size: Optional[int] = None
    raw_payload: dict = Field(default_factory=dict)
    ai_generated: bool = False
    ai_session_id: Optional[uuid.UUID] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID
    wa_message_id: Optional[str] = Field(None, max_length=255)


class MessageUpdate(BaseModel):
    status: Optional[MessageStatus] = None
    wa_message_id: Optional[str] = Field(None, max_length=255)
    body: Optional[str] = None


class MessageResponse(MessageBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    conversation_id: uuid.UUID
    wa_message_id: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
