from __future__ import annotations

import datetime
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=320)
    phone: str = Field(..., max_length=20)
    company: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=320)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ClientResponse(ClientBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
