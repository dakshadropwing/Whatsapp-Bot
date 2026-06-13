import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.ai.orchestrator.handoff import SessionHandoffManager
from app.models.conversation import Conversation, ConversationStatus
from app.ai.orchestrator.router import AgentRouter


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    return session


@pytest.fixture
def mock_redis():
    redis_client = MagicMock()
    redis_client.get = AsyncMock(return_value=None)
    redis_client.setex = AsyncMock()
    redis_client.delete = AsyncMock()
    return redis_client


@pytest.mark.asyncio
async def test_handoff_to_agent(mock_redis, mock_db_session):
    """Test that SessionHandoffManager updates Redis and database Conversation status."""
    handoff = SessionHandoffManager()
    
    mock_conv = MagicMock()
    mock_conv.contact_phone = "+1234567890"
    mock_conv.status = ConversationStatus.ACTIVE
    mock_conv.context = {}

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conv
    mock_db_session.execute.return_value = mock_result

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.extensions.db.session", mock_db_session):
         
        success = await handoff.handoff_to_agent("+1234567890", "sales")
        
        assert success is True
        # Verify Redis key update
        mock_redis.setex.assert_called_once_with("session:agent:+1234567890", 1800, "sales")
        # Verify DB updates
        assert mock_conv.status == ConversationStatus.BOT_HANDLING
        assert mock_conv.context["active_agent"] == "sales"
        mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_handoff_to_human(mock_redis, mock_db_session):
    """Test that SessionHandoffManager clears Redis key and updates DB status to human_handling."""
    handoff = SessionHandoffManager()
    
    mock_conv = MagicMock()
    mock_conv.contact_phone = "+1234567890"
    mock_conv.status = ConversationStatus.BOT_HANDLING
    mock_conv.context = {}

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conv
    mock_db_session.execute.return_value = mock_result

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.extensions.db.session", mock_db_session):
         
        success = await handoff.handoff_to_human("+1234567890", "Frustrated customer")
        
        assert success is True
        # Verify Redis key removal
        mock_redis.delete.assert_called_once_with("session:agent:+1234567890")
        # Verify DB updates
        assert mock_conv.status == ConversationStatus.HUMAN_HANDLING
        assert mock_conv.context["escalation"]["reason"] == "Frustrated customer"
        assert mock_conv.assigned_agent_id is None
        mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_resolve_conversation(mock_redis, mock_db_session):
    """Test resolving a conversation wipes Redis locks and resolves status."""
    handoff = SessionHandoffManager()
    
    mock_conv = MagicMock()
    mock_conv.contact_phone = "+1234567890"
    mock_conv.status = ConversationStatus.BOT_HANDLING
    mock_conv.context = {"active_agent": "sales"}

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conv
    mock_db_session.execute.return_value = mock_result

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.extensions.db.session", mock_db_session):
         
        success = await handoff.resolve_conversation("+1234567890")
        
        assert success is True
        mock_redis.delete.assert_called_once_with("session:agent:+1234567890")
        assert mock_conv.status == ConversationStatus.RESOLVED
        assert "active_agent" not in mock_conv.context
        mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_router_bypasses_human_handling(mock_redis, mock_db_session):
    """Test that AgentRouter ignores message routing if conversation status is human_handling."""
    import uuid
    router = AgentRouter()

    mock_acc = MagicMock()
    mock_acc.organization_id = uuid.uuid4()
    mock_acc.id = uuid.uuid4()

    mock_conv = MagicMock()
    mock_conv.status = ConversationStatus.HUMAN_HANDLING
    mock_conv.id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_acc
    mock_db_session.execute.return_value = mock_result

    message = {
        "from": "+1234567890",
        "body": "Can you help me?",
        "type": "text",
    }

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.extensions.db.session", mock_db_session), \
         patch("app.services.conversation_service.ConversationService.get_or_create", return_value=(mock_conv, False)), \
         patch("app.services.message_service.MessageService.create_message"):
        
        # We mock get_active_agent and _classify to make sure they are NOT called
        with patch.object(router, "_get_active_agent") as mock_get_active, \
             patch.object(router, "_classify") as mock_classify:
             
            await router.route(message)
            
            # Since status is human_handling, router should return early immediately
            mock_get_active.assert_not_called()
            mock_classify.assert_not_called()


@pytest.mark.asyncio
async def test_router_bypasses_escalated(mock_redis, mock_db_session):
    """Test that AgentRouter ignores message routing if conversation status is escalated."""
    import uuid
    router = AgentRouter()

    mock_acc = MagicMock()
    mock_acc.organization_id = uuid.uuid4()
    mock_acc.id = uuid.uuid4()

    mock_conv = MagicMock()
    mock_conv.status = ConversationStatus.ESCALATED
    mock_conv.id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_acc
    mock_db_session.execute.return_value = mock_result

    message = {
        "from": "+1234567890",
        "body": "Hello?",
        "type": "text",
    }

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.extensions.db.session", mock_db_session), \
         patch("app.services.conversation_service.ConversationService.get_or_create", return_value=(mock_conv, False)), \
         patch("app.services.message_service.MessageService.create_message"):
        
        with patch.object(router, "_get_active_agent") as mock_get_active, \
             patch.object(router, "_classify") as mock_classify:
             
            await router.route(message)
            
            mock_get_active.assert_not_called()
            mock_classify.assert_not_called()
