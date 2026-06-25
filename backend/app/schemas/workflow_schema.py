from __future__ import annotations

import datetime
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class WorkflowBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    trigger: str = Field("manual", max_length=100)
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    trigger: Optional[str] = Field(None, max_length=100)
    trigger_config: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    last_run_at: Optional[str] = None
    run_count: int
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
