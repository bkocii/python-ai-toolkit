from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.vector_store import InMemoryVectorStore, VectorRecord


def main() -> None:
    ai = AIClient()
    store = InMemoryVectorStore()

    texts = [
        EmbeddingInput(
            text="Django is a Python web framework.",
            metadata={"topic": "django"},
        ),
        EmbeddingInput(
            text="Redis is often used as a cache and message broker.",
            metadata={"topic": "redis"},
        ),
        EmbeddingInput(
            text="PostgreSQL is a relational database.",
            metadata={"topic": "postgres"},
        ),
    ]

    embedding_response = ai.embed_texts(texts)

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

    query_response = ai.embed_text("Which technology should I use for caching?")

    query_vector = query_response.embeddings[0].vector

    results = store.similarity_search(
        query_vector=query_vector,
        limit=2,
    )

    print("Search results:")

    for result in results:
        print(f"- {result.text}")
        print(f"  Score: {result.score:.4f}")
        print(f"  Metadata: {result.metadata}")


if __name__ == "__main__":
    main()
