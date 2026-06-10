import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.ai.orchestrator.router import AgentRouter
from app.agents.supervisor_agent import SupervisorAgent
from app.ai.providers.base_provider import CompletionResponse


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.complete = AsyncMock()
    return provider


@pytest.fixture
def mock_redis():
    redis_client = MagicMock()
    redis_client.get = AsyncMock(return_value=None)
    redis_client.setex = AsyncMock()
    return redis_client


@pytest.mark.asyncio
async def test_supervisor_classification(mock_provider):
    """Test that SupervisorAgent successfully parses LLM classification output."""
    with patch("app.ai.providers.provider_factory.ProviderFactory.get_provider", return_value=mock_provider):
        supervisor = SupervisorAgent()
        
        # Test case 1: exact category matching
        mock_provider.complete.return_value = CompletionResponse(
            content="support",
            model="test-model",
            provider="test-provider",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
        )
        assert await supervisor.classify("My account is locked.") == "support"
        
        # Test case 2: category with uppercase and spaces/periods
        mock_provider.complete.return_value = CompletionResponse(
            content=" SALES. ",
            model="test-model",
            provider="test-provider",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
        )
        assert await supervisor.classify("How much does the premium pack cost?") == "sales"

        # Test case 3: invalid/unknown category falling back to default
        mock_provider.complete.return_value = CompletionResponse(
            content="something_invalid",
            model="test-model",
            provider="test-provider",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
        )
        assert await supervisor.classify("blah blah") == "support"


@pytest.mark.asyncio
async def test_router_routing_flow(mock_provider, mock_redis):
    """Test the complete dynamic routing and session persistence flow."""
    router = AgentRouter()

    # Mock the Redis client used by AgentRouter
    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.ai.providers.provider_factory.ProviderFactory.get_provider", return_value=mock_provider):

        # Scenario A: No active session, triggers supervisor classification
        mock_provider.complete.return_value = CompletionResponse(
            content="sales",
            model="test-model",
            provider="test-provider",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
        )

        message = {
            "from": "+1234567890",
            "body": "Tell me about prices.",
            "type": "text",
        }

        # Mock the dynamic load_agent call so it returns a mock agent instead of launching actual agents that try to hit WhatsApp Client APIs
        mock_sales_agent = MagicMock()
        mock_sales_agent.handle = AsyncMock()
        
        with patch.object(router, "_load_agent", return_value=mock_sales_agent) as mock_load:
            await router.route(message)
            
            # 1. Router classified the message using Supervisor
            mock_provider.complete.assert_called_once()
            
            # 2. Router stored active session in Redis with 1800s TTL
            mock_redis.setex.assert_called_once_with("session:agent:+1234567890", 1800, "sales")
            
            # 3. Router loaded the Sales Agent dynamically
            mock_load.assert_called_once_with("sales")
            
            # 4. Router invoked the Sales Agent
            mock_sales_agent.handle.assert_called_once_with(message)

        # Reset mocks for next scenario
        mock_provider.complete.reset_mock()
        mock_redis.setex.reset_mock()

        # Scenario B: Session exists in Redis, bypasses classification
        mock_redis.get.return_value = "support"
        
        mock_support_agent = MagicMock()
        mock_support_agent.handle = AsyncMock()

        with patch.object(router, "_load_agent", return_value=mock_support_agent) as mock_load:
            await router.route(message)
            
            # 1. Redis lookup was done
            mock_redis.get.assert_called_with("session:agent:+1234567890")
            
            # 2. Supervisor classification was NOT called (bypassed)
            mock_provider.complete.assert_not_called()
            
            # 3. Session TTL got extended / saved
            mock_redis.setex.assert_called_once_with("session:agent:+1234567890", 1800, "support")
            
            # 4. Support Agent got loaded and handled the message
            mock_load.assert_called_once_with("support")
            mock_support_agent.handle.assert_called_once_with(message)
