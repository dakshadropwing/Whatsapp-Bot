"""
Unit tests for all AI specialist agents.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.agents import (
    SupportAgent,
    LeadAgent,
    SalesAgent,
    HRAgent,
    AppointmentAgent,
    KnowledgeAgent,
    ProjectAgent,
    SupervisorAgent,
)

@pytest.fixture(autouse=True)
def mock_agent_deps():
    with patch("app.ai.providers.provider_factory.ProviderFactory.get_provider") as mock_prov, \
         patch("app.ai.memory.context_manager.ContextManager") as mock_mem:
        mock_prov.return_value = MagicMock()
        mock_mem.return_value = MagicMock()
        yield mock_prov, mock_mem


def test_specialist_agents_initialization():
    agents = [
        (SupportAgent, "support"),
        (LeadAgent, "lead"),
        (SalesAgent, "sales"),
        (HRAgent, "hr"),
        (AppointmentAgent, "appointment"),
        (KnowledgeAgent, "knowledge"),
        (ProjectAgent, "project"),
        (SupervisorAgent, "supervisor"),
    ]
    for agent_cls, name in agents:
        agent = agent_cls()
        assert agent.agent_name == name
        if name != "supervisor":
            assert len(agent.tools) > 0
        assert agent.system_prompt is not None


@pytest.mark.asyncio
async def test_support_agent_handle():
    agent = SupportAgent()
    agent.provider.complete = AsyncMock()
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = "I can help with that."
    mock_response.tool_calls = None
    agent.provider.complete.return_value = mock_response
    
    # Mock memory history
    agent.memory.get_history = AsyncMock(return_value=[])
    agent.memory.save_turn = AsyncMock()

    with patch("app.integrations.whatsapp.client.WhatsAppClient.send_text", new_callable=AsyncMock) as mock_send:
        message = {"from": "+12345", "body": "Need help"}
        await agent.handle(message)
        
        # Verify provider complete was called
        agent.provider.complete.assert_called_once()
        # Verify text was sent to user
        mock_send.assert_called_once_with(to="+12345", body="I can help with that.")
