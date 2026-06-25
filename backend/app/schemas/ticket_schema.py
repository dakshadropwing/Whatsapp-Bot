from __future__ import annotations

import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.ticket import TicketPriority, TicketStatus


class TicketBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    assigned_user_id: Optional[uuid.UUID] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_name: Optional[str] = Field(None, max_length=255)


class TicketCreate(TicketBase):
    conversation_id: Optional[uuid.UUID] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_user_id: Optional[uuid.UUID] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_name: Optional[str] = Field(None, max_length=255)


class TicketResponse(TicketBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
