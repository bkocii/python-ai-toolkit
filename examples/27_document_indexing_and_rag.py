"""
Index sample documents and answer one grounded question with RAG.

This example keeps each retrieval layer explicit: file loading, document
preparation, ID assignment, batch embedding, vector storage, retrieval, and
answer generation. The toolkit does not automatically chunk or index files.

Running this module normally requires configured provider credentials plus
embedding- and text-generation-capable models. The automated example test uses
a deterministic provider substitute and makes no network request.
"""

from pathlib import Path

from ai.client import AIClient
from ai.documents import DirectoryLoader, Document, documents_to_embedding_inputs
from ai.embeddings import EmbeddingResponse
from ai.rag import RAGPipeline, RAGResponse
from ai.retriever import VectorStoreRetriever
from ai.vector_store import InMemoryVectorStore, VectorRecord

SAMPLE_DOCUMENTS_DIR = Path(__file__).resolve().parent / "sample_docs"
COLLECTION_NAME = "sample-docs"


def load_and_prepare_documents(
    documents_dir: Path = SAMPLE_DOCUMENTS_DIR,
) -> list[Document]:
    """Load sample files and attach application-owned record metadata."""
    resolved_directory = documents_dir.resolve()
    documents = DirectoryLoader(
        path=resolved_directory,
        recursive=True,
    ).load()

    prepared_documents = []

    for document in documents:
        source_path = Path(document.metadata["source"]).resolve()
        relative_source = source_path.relative_to(resolved_directory).as_posix()
        record_id = f"{COLLECTION_NAME}/{relative_source}"

        prepared_documents.append(
            Document(
                text=document.text,
                metadata={
                    **document.metadata,
                    "record_id": record_id,
                    "collection": COLLECTION_NAME,
                },
            )
        )

    return prepared_documents


def build_vector_records(
    response: EmbeddingResponse,
    expected_count: int,
) -> list[VectorRecord]:
    """Restore batch input order and create metadata-preserving records."""
    ordered_embeddings = sorted(
        response.embeddings,
        key=lambda embedding: embedding.index,
    )
    returned_indices = [embedding.index for embedding in ordered_embeddings]

    if returned_indices != list(range(expected_count)):
        raise ValueError(
            "Embedding response must contain one result for every document index."
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


def index_documents(
    client: AIClient,
    store: InMemoryVectorStore,
    documents_dir: Path = SAMPLE_DOCUMENTS_DIR,
) -> list[VectorRecord]:
    """Load, prepare, batch embed, and store the sample documents."""
    documents = load_and_prepare_documents(documents_dir)
    embedding_inputs = documents_to_embedding_inputs(documents)
    response = client.embed_texts(embedding_inputs)
    records = build_vector_records(response, expected_count=len(embedding_inputs))
    store.add(records)

    return records


def answer_question(
    client: AIClient,
    store: InMemoryVectorStore,
    question: str,
) -> RAGResponse:
    """Retrieve relevant indexed documents and generate a grounded answer."""
    retriever = VectorStoreRetriever(
        ai_client=client,
        vector_store=store,
    )
    pipeline = RAGPipeline(
        ai_client=client,
        retriever=retriever,
    )

    return pipeline.ask(
        question=question,
        limit=2,
        metadata_filter={"collection": COLLECTION_NAME},
        instructions="Answer in one sentence and name the technology.",
    )


def main() -> None:
    client = AIClient()
    store = InMemoryVectorStore()
    question = "Which technology should I use for caching?"

    records = index_documents(client, store)
    response = answer_question(client, store, question)

    print(f"Indexed {len(records)} documents.")
    print(f"Answer: {response.answer}")
    print("Retrieved sources:")

    for context in response.contexts:
        print(f"- {context.id} ({context.score:.4f})")


if __name__ == "__main__":
    main()
