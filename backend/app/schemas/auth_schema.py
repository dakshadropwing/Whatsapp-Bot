from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.user_schema import UserResponse


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=320)
    password: str = Field(..., min_length=6, max_length=255)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse


class TokenRefreshResponse(BaseModel):
    access_token: str
