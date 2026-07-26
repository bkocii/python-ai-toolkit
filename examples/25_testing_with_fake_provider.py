"""
Test provider-independent application code without a live AI provider.

The application function depends only on AIClient. Test code supplies a
deterministic BaseAIProvider while AIClient is constructed, then exercises the
real request executor and structured-response parsing path.

The factory patch is scoped and automatically restored. No provider is
registered, no credential is used, and no network request is made.
"""

import json
from unittest.mock import patch

from pydantic import BaseModel

from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.schemas import ProviderResponse, TokenUsage


class TicketClassification(BaseModel):
    category: str
    priority: str


def classify_support_ticket(
    client: AIClient,
    message: str,
) -> TicketClassification:
    """Application code: depend on AIClient, not a provider SDK."""
    prompt = (
        "Classify this support ticket by category and priority.\n\n"
        f"Ticket: {message}"
    )
    result = client.ask(prompt, response_type=TicketClassification)
    return result.data


class FakeProvider(BaseAIProvider):
    """Test code: return one controlled response and record received prompts."""

    def __init__(self, response: dict[str, str]):
        self.response = response
        self.prompts: list[str] = []

    def ask_text(self, prompt: str) -> ProviderResponse:
        self.prompts.append(prompt)
        return ProviderResponse(
            text=json.dumps(self.response),
            token_usage=TokenUsage(
                input_tokens=12,
                output_tokens=8,
                total_tokens=20,
            ),
        )


def build_test_client(fake_provider: BaseAIProvider) -> AIClient:
    """Construct a real client with a fake provider for this test only."""
    config = AIConfig(
        provider="openai",
        api_key="test-only-placeholder",
        model="test-model",
        file_logging_enabled=False,
    )
    ConfigValidator.validate(config)

    with patch.object(
        ProviderFactory,
        "create",
        return_value=fake_provider,
    ) as create_provider:
        client = AIClient(config=config)
        create_provider.assert_called_once_with(config)

    return client


def test_classify_support_ticket() -> None:
    registry_before = ProviderFactory.available_providers()
    fake_provider = FakeProvider(
        {
            "category": "billing",
            "priority": "high",
        }
    )
    client = build_test_client(fake_provider)

    ticket = "I was charged twice for the same invoice."
    classification = classify_support_ticket(client, ticket)

    assert classification == TicketClassification(
        category="billing",
        priority="high",
    )
    assert len(fake_provider.prompts) == 1
    assert "Classify this support ticket" in fake_provider.prompts[0]
    assert ticket in fake_provider.prompts[0]
    assert ProviderFactory.available_providers() == registry_before


def main() -> None:
    test_classify_support_ticket()
    print("Fake-provider application test passed without network access.")


if __name__ == "__main__":
    main()
