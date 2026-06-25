from __future__ import annotations

import datetime
import uuid
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field


class WhatsAppAccountBase(BaseModel):
    phone_number_id: str = Field(..., max_length=50)
    waba_id: str = Field(..., max_length=50)
    is_active: bool = True


class WhatsAppAccountCreate(WhatsAppAccountBase):
    access_token: str
    verify_token: str = Field(..., max_length=255)


class WhatsAppAccountUpdate(BaseModel):
    phone_number_id: Optional[str] = Field(None, max_length=50)
    waba_id: Optional[str] = Field(None, max_length=50)
    access_token: Optional[str] = None
    verify_token: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class WhatsAppAccountResponse(WhatsAppAccountBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SendMessageRequest(BaseModel):
    phone: str = Field(..., max_length=20)
    message: str


class SendTemplateRequest(BaseModel):
    phone: str = Field(..., max_length=20)
    template_name: str
    language: str = "en_US"
    parameters: List[Any] = Field(default_factory=list)
