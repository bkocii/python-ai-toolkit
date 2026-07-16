from ai.client import AIClient
from ai.documents import DirectoryLoader, documents_to_embedding_inputs
from ai.rag import RAGPipeline
from ai.retriever import VectorStoreRetriever
from ai.vector_store import InMemoryVectorStore, VectorRecord


def main() -> None:
    ai = AIClient()
    store = InMemoryVectorStore()

    documents = DirectoryLoader(
        path="examples/sample_docs",
        recursive=True,
    ).load()

    embedding_inputs = documents_to_embedding_inputs(documents)

    embedding_response = ai.embed_texts(embedding_inputs)

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
        instructions="Answer briefly and mention the source if relevant.",
    )

    print("Answer:")
    print(response.answer)
    print()

    print("Sources:")

    for context in response.contexts:
        print(f"- {context.metadata.get('filename')}")
        print(f"  Score: {context.score:.4f}")
        print(f"  Loader: {context.metadata.get('loader')}")
        print(f"  Text: {context.text[:120]}...")


if __name__ == "__main__":
    main()
