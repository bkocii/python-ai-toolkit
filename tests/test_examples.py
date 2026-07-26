import asyncio
import importlib
import inspect
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from ai.config import AIConfig
from ai.embeddings import EmbeddingResponse, EmbeddingVector
from ai.exceptions import AIConfigurationError
from ai.integrations.fastapi import get_async_ai_client
from ai.providers.factory import ProviderFactory
from ai.schemas import ProviderResponse, TokenUsage
from ai.tools import ToolCall, ToolResponse


class DeterministicExampleProvider:
    """
    Exercise documented examples without network access or credentials.
    """

    token_usage = TokenUsage(
        input_tokens=2,
        output_tokens=3,
        total_tokens=5,
    )

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(
            text=self._response_text(prompt),
            token_usage=self.token_usage,
        )

    async def ask_text_async(self, prompt: str) -> ProviderResponse:
        return self.ask_text(prompt)

    def stream_text(self, _prompt: str):
        yield "Deterministic "
        yield "stream."

    def ask_with_tools(self, prompt: str, tools):
        del prompt

        return ToolResponse(
            tool_calls=[
                ToolCall(
                    name=tools[0].name,
                    arguments={"location": "Paris"},
                    call_id="call-1",
                )
            ]
        )

    def ask_with_images(self, prompt: str, images) -> ProviderResponse:
        del images

        if "Return valid JSON only." in prompt:
            text = json.dumps(
                {
                    "subject": "Sketch",
                    "colors": ["black", "white"],
                    "visible_text": None,
                }
            )
        else:
            text = "A deterministic image description."

        return ProviderResponse(
            text=text,
            token_usage=self.token_usage,
        )

    def embed_texts(self, inputs) -> EmbeddingResponse:
        embeddings = []

        for index, item in enumerate(inputs):
            normalized_text = item.text.lower()

            if "redis" in normalized_text or "cach" in normalized_text:
                vector = [1.0, 0.0, 0.0]
            elif "postgres" in normalized_text or "relational" in normalized_text:
                vector = [0.0, 1.0, 0.0]
            else:
                vector = [0.0, 0.0, 1.0]

            embeddings.append(
                EmbeddingVector(
                    text=item.text,
                    vector=vector,
                    index=index,
                    metadata=item.metadata,
                )
            )

        return EmbeddingResponse(
            embeddings=embeddings,
            model="test-embedding",
            token_usage=TokenUsage(total_tokens=len(inputs)),
        )

    @staticmethod
    def _response_text(prompt: str) -> str:
        if "Extract the person's information" in prompt:
            return json.dumps(
                {
                    "name": "John Smith",
                    "email": "john@example.com",
                    "company": "OpenAI",
                }
            )

        if "beginner-friendly Python automation project" in prompt:
            return json.dumps(
                {
                    "title": "File organizer",
                    "difficulty": "beginner",
                    "reason": "It teaches filesystem automation.",
                }
            )

        if "Recommend exactly one product" in prompt:
            return json.dumps(
                {
                    "recommended_item": "Vodka Sour",
                    "reason": "It is fresh, fruity, and alcoholic.",
                }
            )

        if "support ticket" in prompt.lower() and "Return valid JSON only." in prompt:
            return json.dumps(
                {
                    "category": "technical",
                    "priority": "low",
                    "summary": "Deterministic support summary.",
                }
            )

        return "Deterministic example response."


@pytest.fixture
def deterministic_provider(monkeypatch):
    provider = DeterministicExampleProvider()

    monkeypatch.setenv("OPENAI_API_KEY", "example-test-key")
    monkeypatch.setenv("EXAMPLE_AI_API_KEY", "example-test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "test-embedding")
    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "false")
    monkeypatch.setattr(
        ProviderFactory,
        "create",
        classmethod(lambda _cls, _config: provider),
    )

    return provider


@pytest.mark.parametrize(
    "module_name",
    [
        "examples.01_plain_text",
        "examples.02_extract_structured_data",
        "examples.03_builder_usage",
        "examples.04_prompt_templates",
        "examples.05_streaming_response",
        "examples.06_async_client",
        "examples.07_tool_calling",
        "examples.08_image_inputs",
        "examples.09_structured_image_input",
        "examples.09_1_structured_image_with_helper",
        "examples.10_embeddings",
        "examples.11_vector_store",
        "examples.12_retriever",
        "examples.13_rag_pipeline",
        "examples.14_document_loader_rag",
        "examples.15_conversation_memory",
        "examples.16_agent",
        "examples.17_workflow_engine",
        "examples.18_multi_agent_orchestration",
        "examples.23_explicit_config",
        "examples.hello_ai",
        "examples.drink_recommender",
    ],
)
def test_example_main_runs_offline(
    module_name,
    deterministic_provider,
    capsys,
):
    module = importlib.import_module(module_name)

    if inspect.iscoroutinefunction(module.main):
        asyncio.run(module.main())
    else:
        module.main()

    assert capsys.readouterr().out


def test_django_example_runs_offline(
    monkeypatch,
    deterministic_provider,
):
    module = importlib.import_module("examples.19_django_integration")
    fake_settings = SimpleNamespace(
        AI_TOOLKIT={
            "provider": "openai",
            "api_key": "example-test-key",
            "model": "test-model",
            "embedding_model": "test-embedding",
            "file_logging_enabled": False,
        }
    )

    monkeypatch.setattr(
        "ai.integrations.django.config.django_settings",
        fake_settings,
    )

    result = module.analyze_support_ticket("The account settings page is unavailable.")

    assert result.category == "technical"
    assert result.priority == "low"


def test_fastapi_example_runs_offline(deterministic_provider):
    module = importlib.import_module("examples.20_fastapi_integration")

    class FakeAsyncAIClient:
        async def ask(self, prompt: str, response_type=None):
            assert "support ticket" in prompt.lower()
            assert response_type is module.TicketAnalysis

            return SimpleNamespace(
                data=module.TicketAnalysis(
                    category="technical",
                    priority="low",
                    summary="Deterministic support summary.",
                )
            )

    module.app.dependency_overrides[get_async_ai_client] = FakeAsyncAIClient

    try:
        response = TestClient(module.app).post(
            "/analyze-ticket",
            json={"message": "The account settings page is unavailable."},
        )
    finally:
        module.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "category": "technical",
        "priority": "low",
        "summary": "Deterministic support summary.",
    }


def test_explicit_config_example_uses_validated_supplied_values(
    monkeypatch,
    deterministic_provider,
):
    module = importlib.import_module("examples.23_explicit_config")
    observed_configs = []

    monkeypatch.setenv("AI_PROVIDER", "environment-provider")
    monkeypatch.setenv("OPENAI_MODEL", "environment-model")
    monkeypatch.setenv("AI_MODEL", "environment-fallback-model")
    monkeypatch.setattr(
        "ai.client.get_ai_config",
        lambda: pytest.fail("AIClient read environment configuration"),
    )
    monkeypatch.setattr(
        ProviderFactory,
        "create",
        classmethod(
            lambda _cls, config: observed_configs.append(config)
            or deterministic_provider
        ),
    )

    client = module.build_ai_client("runtime-injected-test-key")

    assert observed_configs == [
        AIConfig(
            provider="openai",
            api_key="runtime-injected-test-key",
            model="gpt-5.4-mini",
            embedding_model="text-embedding-3-small",
            max_retries=1,
            log_level="INFO",
            file_logging_enabled=False,
        )
    ]
    assert client.model == "gpt-5.4-mini"

    with pytest.raises(AIConfigurationError):
        module.build_ai_client(" ")

    assert len(observed_configs) == 1
