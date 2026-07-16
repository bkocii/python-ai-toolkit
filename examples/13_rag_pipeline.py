from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.rag import RAGPipeline
from ai.retriever import VectorStoreRetriever
from ai.vector_store import InMemoryVectorStore, VectorRecord


def main() -> None:
    ai = AIClient()
    store = InMemoryVectorStore()

    knowledge = [
        EmbeddingInput(
            text="Redis is often used as a cache and message broker.",
            metadata={
                "topic": "redis",
                "source": "technical_notes",
            },
        ),
        EmbeddingInput(
            text="PostgreSQL is a relational database used for structured data.",
            metadata={
                "topic": "postgres",
                "source": "technical_notes",
            },
        ),
        EmbeddingInput(
            text="Django is a Python web framework for building web applications.",
            metadata={
                "topic": "django",
                "source": "technical_notes",
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

    rag = RAGPipeline(
        ai_client=ai,
        retriever=retriever,
    )

    response = rag.ask(
        question="Which technology should I use for caching?",
        limit=2,
        instructions="Answer in three short paragraphs.",
    )

    print("Answer:")
    print(response.answer)
    print()

    print("Sources:")

    for context in response.contexts:
        print(f"- {context.id}")
        print(f"  Score: {context.score:.4f}")
        print(f"  Metadata: {context.metadata}")
        print(f"  Text: {context.text}")


if __name__ == "__main__":
    main()
