import asyncio
import os
from dotenv import load_dotenv

from app.ai.providers.base_provider import CompletionRequest, Message
from app.ai.providers.provider_factory import ProviderFactory, ProviderType


async def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("Error: GOOGLE_AI_API_KEY not found in environment!")
        return

    print("Initializing Gemini provider via ProviderFactory...")
    # This also confirms ProviderFactory can resolve and instantiate the provider correctly
    provider = ProviderFactory.get_provider(ProviderType.GEMINI, force_new=True)
    print(f"Provider details: {provider}")

    # 1. Health check
    print("\n--- 1. Testing Health Check ---")
    healthy = await provider.health_check()
    print(f"Health check status: {healthy}")

    # 2. Text completion
    print("\n--- 2. Testing Complete Method ---")
    request = CompletionRequest(
        messages=[
            Message(role="system", content="You are a short, concise assistant."),
            Message(role="user", content="What is the capital of France? Answer in one word."),
        ]
    )
    completion = await provider.complete(request)
    print("Completion response content:", repr(completion.content))
    print("Completion response model:", completion.model)
    print("Completion response tokens (in/out/total):", completion.input_tokens, completion.output_tokens, completion.total_tokens)
    print("Completion response finish reason:", completion.finish_reason)

    # 3. Streaming
    print("\n--- 3. Testing Stream Method ---")
    stream_request = CompletionRequest(
        messages=[Message(role="user", content="Count from 1 to 5 with space separators.")]
    )
    print("Streaming chunks:")
    async for chunk in provider.stream(stream_request):
        print(repr(chunk), end=" ")
    print()

    # 4. Embeddings
    print("\n--- 4. Testing Embed Method ---")
    embedding = await provider.embed("Paris")
    print("Embedding generated, length:", len(embedding))
    print("First 5 values:", embedding[:5])


if __name__ == "__main__":
    asyncio.run(main())