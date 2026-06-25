from __future__ import annotations

import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    email: str = Field(..., max_length=320)
    username: str = Field(..., max_length=150)
    full_name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True
    is_superadmin: bool = False
    role_id: Optional[uuid.UUID] = None
    preferences: dict = Field(default_factory=dict)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255)


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=320)
    username: Optional[str] = Field(None, max_length=150)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    role_id: Optional[uuid.UUID] = None
    preferences: Optional[dict] = None


class UserResponse(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    last_login_at: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
