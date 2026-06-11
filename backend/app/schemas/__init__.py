from __future__ import annotations

from app.schemas.agent_schema import AgentBase, AgentCreate, AgentUpdate, AgentResponse
from app.schemas.conversation_schema import ConversationBase, ConversationCreate, ConversationUpdate, ConversationResponse
from app.schemas.message_schema import MessageBase, MessageCreate, MessageUpdate, MessageResponse
from app.schemas.ticket_schema import TicketBase, TicketCreate, TicketUpdate, TicketResponse
from app.schemas.whatsapp_schema import (
    WhatsAppAccountBase,
    WhatsAppAccountCreate,
    WhatsAppAccountUpdate,
    WhatsAppAccountResponse,
    SendMessageRequest,
    SendTemplateRequest,
)
from app.schemas.workflow_schema import WorkflowBase, WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.schemas.user_schema import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.client_schema import ClientBase, ClientCreate, ClientUpdate, ClientResponse
from app.schemas.analytics_schema import DashboardStatsResponse, AnalyticsOverviewResponse
from app.schemas.auth_schema import LoginRequest, LoginResponse, TokenRefreshResponse
