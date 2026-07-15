from ai.client import AIClient
from ai.embeddings import EmbeddingInput, EmbeddingResponse, EmbeddingVector
from ai.providers.base import BaseAIProvider
from ai.schemas import ProviderResponse
from types import SimpleNamespace

import pytest

from ai.exceptions import AIProviderError
from ai.providers.openai_provider import OpenAIProvider


class FakeEmbeddingProvider(BaseAIProvider):
    def __init__(self):
        self.received_inputs = None

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="plain response")

    def embed_texts(
        self,
        inputs: list[EmbeddingInput],
    ) -> EmbeddingResponse:
        self.received_inputs = inputs

        return EmbeddingResponse(
            embeddings=[
                EmbeddingVector(
                    text=input_item.text,
                    vector=[float(index), 0.1, 0.2],
                    index=index,
                    metadata=input_item.metadata,
                )
                for index, input_item in enumerate(inputs)
            ],
            model="fake-embedding-model",
        )


def test_embedding_input_defaults_metadata():
    input_item = EmbeddingInput(text="Hello world")

    assert input_item.text == "Hello world"
    assert input_item.metadata == {}


def test_embedding_response_exposes_vectors_and_texts():
    response = EmbeddingResponse(
        embeddings=[
            EmbeddingVector(
                text="First text",
                vector=[0.1, 0.2],
                index=0,
            ),
            EmbeddingVector(
                text="Second text",
                vector=[0.3, 0.4],
                index=1,
            ),
        ],
        model="fake-embedding-model",
    )

    assert response.texts == ["First text", "Second text"]
    assert response.vectors == [[0.1, 0.2], [0.3, 0.4]]


def test_ai_client_embed_text_delegates_to_provider():
    provider = FakeEmbeddingProvider()

    ai = AIClient.__new__(AIClient)
    ai.provider = provider

    response = ai.embed_text(
        text="Django is a Python web framework.",
        metadata={"source": "notes.md"},
    )

    assert provider.received_inputs is not None
    assert provider.received_inputs[0].text == "Django is a Python web framework."
    assert provider.received_inputs[0].metadata == {"source": "notes.md"}
    assert response.embeddings[0].vector == [0.0, 0.1, 0.2]


def test_ai_client_embed_texts_accepts_plain_strings():
    provider = FakeEmbeddingProvider()

    ai = AIClient.__new__(AIClient)
    ai.provider = provider

    response = ai.embed_texts(
        [
            "Django is a Python web framework.",
            "Redis is often used as a cache.",
        ]
    )

    assert provider.received_inputs is not None
    assert provider.received_inputs[0].text == "Django is a Python web framework."
    assert provider.received_inputs[1].text == "Redis is often used as a cache."
    assert len(response.embeddings) == 2


def test_ai_client_embed_texts_accepts_embedding_inputs():
    provider = FakeEmbeddingProvider()

    ai = AIClient.__new__(AIClient)
    ai.provider = provider

    response = ai.embed_texts(
        [
            EmbeddingInput(
                text="PostgreSQL is a relational database.",
                metadata={
                    "source": "database_notes.md",
                    "topic": "postgres",
                },
            )
        ]
    )

    assert provider.received_inputs is not None
    assert provider.received_inputs[0].metadata == {
        "source": "database_notes.md",
        "topic": "postgres",
    }
    assert response.embeddings[0].metadata == {
        "source": "database_notes.md",
        "topic": "postgres",
    }


class FakeOpenAIEmbeddingsAPI:
    def __init__(self, response):
        self.response = response
        self.received_kwargs = None

    def create(self, **kwargs):
        self.received_kwargs = kwargs
        return self.response


def make_openai_embedding_provider(
    response,
    embedding_dimensions: int | None = None,
) -> OpenAIProvider:
    provider = OpenAIProvider.__new__(OpenAIProvider)
    provider.embedding_model = "text-embedding-3-small"
    provider.embedding_dimensions = embedding_dimensions

    fake_embeddings_api = FakeOpenAIEmbeddingsAPI(response)
    provider.client = SimpleNamespace(embeddings=fake_embeddings_api)

    return provider


def test_openai_provider_embeds_texts():
    response = SimpleNamespace(
        data=[
            SimpleNamespace(
                index=0,
                embedding=[0.1, 0.2, 0.3],
            ),
            SimpleNamespace(
                index=1,
                embedding=[0.4, 0.5, 0.6],
            ),
        ],
        model="text-embedding-3-small",
        usage=SimpleNamespace(
            prompt_tokens=10,
            total_tokens=10,
        ),
    )
    provider = make_openai_embedding_provider(response)

    result = provider.embed_texts(
        [
            EmbeddingInput(
                text="Django is a Python web framework.",
                metadata={"source": "django.md"},
            ),
            EmbeddingInput(
                text="Redis is often used as a cache.",
                metadata={"source": "redis.md"},
            ),
        ]
    )

    assert result.model == "text-embedding-3-small"
    assert result.embeddings[0].text == "Django is a Python web framework."
    assert result.embeddings[0].vector == [0.1, 0.2, 0.3]
    assert result.embeddings[0].metadata == {"source": "django.md"}
    assert result.embeddings[1].text == "Redis is often used as a cache."
    assert result.embeddings[1].vector == [0.4, 0.5, 0.6]
    assert result.embeddings[1].metadata == {"source": "redis.md"}
    assert result.token_usage is not None
    assert result.token_usage.input_tokens == 10
    assert result.token_usage.total_tokens == 10


def test_openai_provider_sends_embedding_request_kwargs():
    response = SimpleNamespace(
        data=[
            SimpleNamespace(
                index=0,
                embedding=[0.1, 0.2],
            ),
        ],
        model="text-embedding-3-small",
        usage=None,
    )
    provider = make_openai_embedding_provider(
        response,
        embedding_dimensions=512,
    )

    provider.embed_texts(
        [
            EmbeddingInput(text="Hello world"),
        ]
    )

    received_kwargs = provider.client.embeddings.received_kwargs

    assert received_kwargs == {
        "model": "text-embedding-3-small",
        "input": ["Hello world"],
        "encoding_format": "float",
        "dimensions": 512,
    }


def test_openai_provider_omits_dimensions_when_not_configured():
    response = SimpleNamespace(
        data=[
            SimpleNamespace(
                index=0,
                embedding=[0.1, 0.2],
            ),
        ],
        model="text-embedding-3-small",
        usage=None,
    )
    provider = make_openai_embedding_provider(response)

    provider.embed_texts(
        [
            EmbeddingInput(text="Hello world"),
        ]
    )

    received_kwargs = provider.client.embeddings.received_kwargs

    assert "dimensions" not in received_kwargs


def test_openai_provider_rejects_empty_embedding_inputs():
    provider = make_openai_embedding_provider(
        response=SimpleNamespace(
            data=[],
            model="text-embedding-3-small",
            usage=None,
        )
    )

    with pytest.raises(
        AIProviderError,
        match="At least one embedding input is required",
    ):
        provider.embed_texts([])


def test_openai_provider_rejects_empty_embedding_text():
    provider = make_openai_embedding_provider(
        response=SimpleNamespace(
            data=[],
            model="text-embedding-3-small",
            usage=None,
        )
    )

    with pytest.raises(
        AIProviderError,
        match="Embedding input text cannot be empty",
    ):
        provider.embed_texts(
            [
                EmbeddingInput(text="   "),
            ]
        )


def test_openai_provider_rejects_invalid_embedding_index():
    response = SimpleNamespace(
        data=[
            SimpleNamespace(
                index=5,
                embedding=[0.1, 0.2],
            ),
        ],
        model="text-embedding-3-small",
        usage=None,
    )
    provider = make_openai_embedding_provider(response)

    with pytest.raises(
        AIProviderError,
        match="OpenAI returned an invalid embedding index",
    ):
        provider.embed_texts(
            [
                EmbeddingInput(text="Hello world"),
            ]
        )
