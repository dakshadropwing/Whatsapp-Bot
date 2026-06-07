import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from google.genai import types

from app.ai.providers.base_provider import CompletionRequest, Message
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.provider_factory import ProviderFactory, ProviderType
from app.core.config.settings import Settings


@pytest.fixture
def provider():
    return GeminiProvider(api_key="test-api-key", model="gemini-2.5-flash")


def test_gemini_provider_configure():
    with patch("google.genai.Client") as mock_client_class:
        provider = GeminiProvider(api_key="custom-key", model="gemini-exp")
        mock_client_class.assert_called_once_with(api_key="custom-key")
        assert provider.default_model == "gemini-exp"
        assert provider.provider_name == "gemini"


@pytest.mark.asyncio
async def test_gemini_provider_complete_success(provider):
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    mock_response.usage_metadata = MagicMock(
        prompt_token_count=12,
        candidates_token_count=8,
        total_token_count=20,
    )
    mock_response.candidates = [MagicMock(finish_reason="STOP")]
    mock_response.function_calls = None

    provider._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    request = CompletionRequest(
        messages=[
            Message(role="system", content="You are a helper."),
            Message(role="user", content="Hi!"),
        ],
        temperature=0.5,
        max_tokens=100,
    )

    response = await provider.complete(request)

    assert response.content == "Hello from Gemini"
    assert response.model == "gemini-2.5-flash"
    assert response.provider == "gemini"
    assert response.input_tokens == 12
    assert response.output_tokens == 8
    assert response.total_tokens == 20
    assert response.tool_calls == []
    assert response.finish_reason == "stop"

    # Verify how contents and config were constructed
    provider._client.aio.models.generate_content.assert_called_once()
    args, kwargs = provider._client.aio.models.generate_content.call_args
    
    # Check model passed
    assert kwargs["model"] == "gemini-2.5-flash"
    
    # Check contents mapping (system filtered out, user kept)
    contents = kwargs["contents"]
    assert len(contents) == 1
    assert contents[0].role == "user"
    assert contents[0].parts[0].text == "Hi!"

    # Check config
    config = kwargs["config"]
    assert config.temperature == 0.5
    assert config.max_output_tokens == 100
    assert config.system_instruction == "You are a helper."


@pytest.mark.asyncio
async def test_gemini_provider_complete_tool_calls(provider):
    mock_response = MagicMock()
    mock_response.text = None
    mock_response.usage_metadata = MagicMock(
        prompt_token_count=15,
        candidates_token_count=10,
        total_token_count=25,
    )
    mock_response.candidates = [MagicMock(finish_reason="STOP")]
    
    # Mock a function call
    mock_func_call = MagicMock()
    mock_func_call.id = "call-123"
    mock_func_call.name = "get_current_weather"
    mock_func_call.args = {"location": "Paris"}
    mock_response.function_calls = [mock_func_call]

    provider._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get weather info",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }
    ]

    request = CompletionRequest(
        messages=[Message(role="user", content="What is the weather in Paris?")],
        tools=tools,
        tool_choice="auto",
    )

    response = await provider.complete(request)

    assert response.content == ""
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].id == "call-123"
    assert response.tool_calls[0].name == "get_current_weather"
    assert response.tool_calls[0].arguments == {"location": "Paris"}

    args, kwargs = provider._client.aio.models.generate_content.call_args
    config = kwargs["config"]
    assert config.tools is not None
    assert len(config.tools) == 1
    assert config.tools[0].function_declarations[0].name == "get_current_weather"
    assert config.tool_config.function_calling_config.mode == "AUTO"


@pytest.mark.asyncio
async def test_gemini_provider_tool_response(provider):
    mock_response = MagicMock()
    mock_response.text = "It's 20C and sunny."
    mock_response.usage_metadata = MagicMock()
    mock_response.candidates = [MagicMock(finish_reason="STOP")]
    mock_response.function_calls = None

    provider._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    request = CompletionRequest(
        messages=[
            Message(role="user", content="What is the weather in Paris?"),
            Message(role="assistant", content=""),
            Message(role="tool", content='{"result": "sunny"}', name="get_current_weather"),
        ]
    )

    response = await provider.complete(request)
    assert response.content == "It's 20C and sunny."

    args, kwargs = provider._client.aio.models.generate_content.call_args
    contents = kwargs["contents"]
    assert len(contents) == 3
    assert contents[0].role == "user"
    assert contents[1].role == "model"
    assert contents[2].role == "tool"
    assert contents[2].parts[0].function_response.name == "get_current_weather"
    assert contents[2].parts[0].function_response.response == {"result": "sunny"}


@pytest.mark.asyncio
async def test_gemini_provider_stream(provider):
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "Hello"
    mock_chunk2 = MagicMock()
    mock_chunk2.text = " world!"

    async def mock_generator():
        yield mock_chunk1
        yield mock_chunk2

    provider._client.aio.models.generate_content_stream = AsyncMock(return_value=mock_generator())

    request = CompletionRequest(
        messages=[Message(role="user", content="Say hello world")]
    )

    stream = provider.stream(request)
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    assert chunks == ["Hello", " world!"]


@pytest.mark.asyncio
async def test_gemini_provider_embed(provider):
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1, 0.2, 0.3])]
    provider._client.aio.models.embed_content = AsyncMock(return_value=mock_response)

    emb = await provider.embed("test text")
    assert emb == [0.1, 0.2, 0.3]
    provider._client.aio.models.embed_content.assert_called_once_with(
        model="gemini-embedding-2",
        contents="test text",
    )


@pytest.mark.asyncio
async def test_gemini_provider_health_check_success(provider):
    mock_model = MagicMock()
    mock_model.name = "models/gemini-2.5-flash"
    
    # mock_list returns a coroutine that resolves to an iterable list of models
    provider._client.aio.models.list = AsyncMock(return_value=[mock_model])

    healthy = await provider.health_check()
    assert healthy is True


@pytest.mark.asyncio
async def test_gemini_provider_health_check_failure(provider):
    provider._client.aio.models.list = AsyncMock(side_effect=Exception("API Error"))

    healthy = await provider.health_check()
    assert healthy is False


def test_provider_factory_instantiates_gemini():
    mock_settings = MagicMock()
    mock_settings.DEFAULT_AI_PROVIDER = "gemini"
    mock_settings.GOOGLE_AI_API_KEY = "dummy-google-key"
    mock_settings.GOOGLE_AI_MODEL = "gemini-2.5-flash"
    
    with patch("app.ai.providers.provider_factory.get_settings", return_value=mock_settings):
        # Clear factory cache
        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider(ProviderType.GEMINI, force_new=True)
        assert isinstance(provider, GeminiProvider)
        assert provider.api_key == "dummy-google-key"
        assert provider.default_model == "gemini-2.5-flash"
