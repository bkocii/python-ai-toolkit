import pytest

from ai.embeddings import EmbeddingResponse, EmbeddingVector
from ai.retriever import (
    RetrievedContext,
    VectorStoreRetriever,
    format_retrieved_context,
)
from ai.vector_store import InMemoryVectorStore, VectorRecord


class FakeAIClient:
    def embed_text(self, text: str) -> EmbeddingResponse:
        vectors = {
            "cache query": [1.0, 0.0],
            "database query": [0.0, 1.0],
        }

        return EmbeddingResponse(
            embeddings=[
                EmbeddingVector(
                    text=text,
                    vector=vectors.get(text, [1.0, 0.0]),
                    index=0,
                )
            ],
            model="fake-embedding-model",
        )


def make_store() -> InMemoryVectorStore:
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="redis",
                text="Redis is often used as a cache.",
                vector=[1.0, 0.0],
                metadata={"topic": "redis", "source": "docs"},
            ),
            VectorRecord(
                id="postgres",
                text="PostgreSQL is a relational database.",
                vector=[0.0, 1.0],
                metadata={"topic": "postgres", "source": "docs"},
            ),
        ]
    )

    return store


def test_retrieved_context_stores_values():
    context = RetrievedContext(
        id="doc-1",
        text="Redis is often used as a cache.",
        score=0.95,
        metadata={"topic": "redis"},
    )

    assert context.id == "doc-1"
    assert context.text == "Redis is often used as a cache."
    assert context.score == 0.95
    assert context.metadata == {"topic": "redis"}


def test_vector_store_retriever_returns_relevant_context():
    retriever = VectorStoreRetriever(
        ai_client=FakeAIClient(),
        vector_store=make_store(),
    )

    contexts = retriever.retrieve(
        query="cache query",
        limit=1,
    )

    assert len(contexts) == 1
    assert contexts[0].id == "redis"
    assert contexts[0].text == "Redis is often used as a cache."
    assert contexts[0].metadata["topic"] == "redis"


def test_vector_store_retriever_respects_limit():
    retriever = VectorStoreRetriever(
        ai_client=FakeAIClient(),
        vector_store=make_store(),
    )

    contexts = retriever.retrieve(
        query="cache query",
        limit=1,
    )

    assert len(contexts) == 1


def test_vector_store_retriever_supports_metadata_filter():
    retriever = VectorStoreRetriever(
        ai_client=FakeAIClient(),
        vector_store=make_store(),
    )

    contexts = retriever.retrieve(
        query="cache query",
        metadata_filter={"topic": "postgres"},
    )

    assert len(contexts) == 1
    assert contexts[0].id == "postgres"


def test_vector_store_retriever_rejects_empty_query():
    retriever = VectorStoreRetriever(
        ai_client=FakeAIClient(),
        vector_store=make_store(),
    )

    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        retriever.retrieve("   ")


def test_format_retrieved_context_formats_contexts():
    contexts = [
        RetrievedContext(
            id="redis",
            text="Redis is often used as a cache.",
            score=0.98765,
            metadata={"topic": "redis"},
        )
    ]

    formatted = format_retrieved_context(contexts)

    assert "[Context 1]" in formatted
    assert "ID: redis" in formatted
    assert "Score: 0.9877" in formatted
    assert "Metadata: {'topic': 'redis'}" in formatted
    assert "Text:\nRedis is often used as a cache." in formatted


def test_format_retrieved_context_without_metadata():
    contexts = [
        RetrievedContext(
            id="doc-1",
            text="Some text.",
            score=0.5,
        )
    ]

    formatted = format_retrieved_context(contexts)

    assert "ID: doc-1" in formatted
    assert "Metadata:" not in formatted
    assert "Text:\nSome text." in formatted


def test_format_retrieved_context_returns_message_for_empty_contexts():
    formatted = format_retrieved_context([])

    assert formatted == "No relevant context found."
