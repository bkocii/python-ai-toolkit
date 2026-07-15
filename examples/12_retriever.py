from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.retriever import VectorStoreRetriever, format_retrieved_context
from ai.vector_store import InMemoryVectorStore, VectorRecord


def main() -> None:
    ai = AIClient()
    store = InMemoryVectorStore()

    knowledge = [
        EmbeddingInput(
            text="Redis is often used as a cache and message broker.",
            metadata={
                "topic": "redis",
                "source": "notes",
            },
        ),
        EmbeddingInput(
            text="PostgreSQL is a relational database used for structured data.",
            metadata={
                "topic": "postgres",
                "source": "notes",
            },
        ),
        EmbeddingInput(
            text="Django is a Python web framework for building web applications.",
            metadata={
                "topic": "django",
                "source": "notes",
            },
        ),
    ]

    embedding_response = ai.embed_texts(knowledge)

    records = [
        VectorRecord(
            id=f"doc-{embedding.index}",
            text=embedding.text,
            vector=embedding.vector,
            metadata=embedding.metadata,
        )
        for embedding in embedding_response.embeddings
    ]

    store.add(records)

    retriever = VectorStoreRetriever(
        ai_client=ai,
        vector_store=store,
    )

    question = "Which technology should I use for caching?"

    contexts = retriever.retrieve(
        query=question,
        limit=2,
    )

    print("Retrieved contexts:")
    print(format_retrieved_context(contexts))


if __name__ == "__main__":
    main()
