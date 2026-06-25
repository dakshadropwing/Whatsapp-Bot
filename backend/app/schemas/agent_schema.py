from __future__ import annotations

import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    role_type: str = Field("support", max_length=50)
    system_prompt: str
    provider: str = Field("gemini", max_length=50)
    model_name: str = Field("gemini-2.5-flash", max_length=100)
    is_active: bool = True


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    role_type: Optional[str] = Field(None, max_length=50)
    system_prompt: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=50)
    model_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
