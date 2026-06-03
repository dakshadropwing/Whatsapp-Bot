"""
Supervisor Agent — TODO: implement full agent logic.
"""
from app.agents.base_agent import BaseAgent


class SupervisorAgent(BaseAgent):
    agent_name = "supervisor"
    system_prompt = "TODO: add Supervisor agent system prompt."

    def _register_tools(self):
        return []

    async def handle(self, message):
        response = await self._generate_response(message["from"], message["body"])
        from app.integrations.whatsapp.client import WhatsAppClient
        async with WhatsAppClient() as wa:
            await wa.send_text(message["from"], response)
