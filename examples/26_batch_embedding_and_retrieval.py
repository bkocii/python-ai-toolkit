"""
Embed a knowledge batch once, store it, and retrieve relevant context.

The knowledge texts are submitted in one AIClient.embed_texts() request.
EmbeddingVector.index restores input order if a provider returns batch results
out of order, while application-owned IDs and metadata are preserved in the
vector store.

Running this module normally requires configured provider credentials and an
embedding-capable model. The automated example test uses a deterministic
provider substitute and makes no network request.
"""

from ai.client import AIClient
from ai.embeddings import EmbeddingInput, EmbeddingResponse
from ai.retriever import RetrievedContext, VectorStoreRetriever
from ai.vector_store import InMemoryVectorStore, VectorRecord


def build_knowledge_batch() -> list[EmbeddingInput]:
    """Return small application-owned records ready for batch embedding."""
    return [
        EmbeddingInput(
            text="Redis is often used as an in-memory cache.",
            metadata={
                "record_id": "redis-cache",
                "source": "architecture-notes",
                "topic": "caching",
            },
        ),
        EmbeddingInput(
            text="PostgreSQL stores relational application data.",
            metadata={
                "record_id": "postgres-database",
                "source": "architecture-notes",
                "topic": "database",
            },
        ),
        EmbeddingInput(
            text="Django is a Python framework for web applications.",
            metadata={
                "record_id": "django-framework",
                "source": "framework-notes",
                "topic": "web",
            },
        ),
    ]


def records_in_input_order(
    response: EmbeddingResponse,
    expected_count: int,
) -> list[VectorRecord]:
    """Convert a complete embedding response into input-ordered records."""
    ordered_embeddings = sorted(
        response.embeddings,
        key=lambda embedding: embedding.index,
    )
    returned_indices = [embedding.index for embedding in ordered_embeddings]

    if returned_indices != list(range(expected_count)):
        raise ValueError(
            "Embedding response must contain one result for every input index."
        )

    return [
        VectorRecord(
            id=embedding.metadata["record_id"],
            text=embedding.text,
            vector=embedding.vector,
            metadata=embedding.metadata,
        )
        for embedding in ordered_embeddings
    ]


def index_knowledge(
    client: AIClient,
    store: InMemoryVectorStore,
) -> tuple[EmbeddingResponse, list[VectorRecord]]:
    """Embed all knowledge in one request and add ordered records to the store."""
    batch = build_knowledge_batch()
    response = client.embed_texts(batch)
    records = records_in_input_order(response, expected_count=len(batch))
    store.add(records)

    return response, records


def retrieve_contexts(
    client: AIClient,
    store: InMemoryVectorStore,
    question: str,
) -> list[RetrievedContext]:
    """Embed one query and retrieve matching architecture notes."""
    retriever = VectorStoreRetriever(
        ai_client=client,
        vector_store=store,
    )

    return retriever.retrieve(
        query=question,
        limit=2,
        metadata_filter={"source": "architecture-notes"},
    )


def main() -> None:
    client = AIClient()
    store = InMemoryVectorStore()

    response, records = index_knowledge(client, store)
    contexts = retrieve_contexts(
        client,
        store,
        question="Which technology can cache frequently used data?",
    )

    print(f"Embedded {len(records)} records in one batch with {response.model}.")
    print("Stored input order:")

    for record in records:
        print(f"- {record.id}: {record.metadata['topic']}")

    print()
    print("Retrieved contexts:")

    for context in contexts:
        print(f"- {context.id} ({context.score:.4f}): {context.text}")


if __name__ == "__main__":
    main()
