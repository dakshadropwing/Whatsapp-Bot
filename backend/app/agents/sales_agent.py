"""
Sales Agent — TODO: implement full agent logic.
"""
from app.agents.base_agent import BaseAgent


class SalesAgent(BaseAgent):
    agent_name = "sales"
    system_prompt = "TODO: add Sales agent system prompt."

    def _register_tools(self):
        return []

    async def handle(self, message):
        response = await self._generate_response(message["from"], message["body"])
        from app.integrations.whatsapp.client import WhatsAppClient
        async with WhatsAppClient() as wa:
            await wa.send_text(message["from"], response)
