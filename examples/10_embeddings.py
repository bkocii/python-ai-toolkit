from ai.client import AIClient
from ai.embeddings import EmbeddingInput


def main() -> None:
    ai = AIClient()

    single_response = ai.embed_text(
        "Django is a Python web framework.",
        metadata={
            "source": "example",
            "topic": "django",
        },
    )

    single_embedding = single_response.embeddings[0]

    print("Single embedding")
    print(f"Text: {single_embedding.text}")
    print(f"Model: {single_response.model}")
    print(f"Vector length: {len(single_embedding.vector)}")
    print(f"Metadata: {single_embedding.metadata}")
    print()

    batch_response = ai.embed_texts(
        [
            EmbeddingInput(
                text="Redis is often used as a cache.",
                metadata={"topic": "redis"},
            ),
            EmbeddingInput(
                text="PostgreSQL is a relational database.",
                metadata={"topic": "postgres"},
            ),
        ]
    )

    print("Batch embeddings")

    for embedding in batch_response.embeddings:
        print(f"- {embedding.text}")
        print(f"  Vector length: {len(embedding.vector)}")
        print(f"  Metadata: {embedding.metadata}")


if __name__ == "__main__":
    main()
