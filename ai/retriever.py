from abc import ABC, abstractmethod

from pydantic import BaseModel, Field
from ai.client import AIClient
from ai.vector_store import BaseVectorStore


class RetrievedContext(BaseModel):
    """
    One retrieved context item.

    This is the clean retrieval result that higher-level RAG pipelines
    can pass into prompts.
    """

    id: str
    text: str
    score: float
    metadata: dict[str, str] = Field(default_factory=dict)


class BaseRetriever(ABC):
    """
    Provider-independent retriever interface.
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedContext]:
        """
        Retrieve context relevant to a query.
        """
        raise NotImplementedError


class VectorStoreRetriever(BaseRetriever):
    """
    Retriever backed by AIClient embeddings and a vector store.

    It embeds the query, searches the vector store, and returns clean
    RetrievedContext objects without exposing raw vectors.
    """

    def __init__(
        self,
        ai_client: AIClient,
        vector_store: BaseVectorStore,
    ):
        self.ai_client = ai_client
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedContext]:
        """
        Retrieve context relevant to a query.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        query_embedding = self.ai_client.embed_text(query)
        query_vector = query_embedding.embeddings[0].vector

        results = self.vector_store.similarity_search(
            query_vector=query_vector,
            limit=limit,
            metadata_filter=metadata_filter,
        )

        return [
            RetrievedContext(
                id=result.id,
                text=result.text,
                score=result.score,
                metadata=result.metadata,
            )
            for result in results
        ]


def format_retrieved_context(
    contexts: list[RetrievedContext],
) -> str:
    """
    Format retrieved context items for use inside a prompt.
    """
    if not contexts:
        return "No relevant context found."

    formatted_items = []

    for index, context in enumerate(contexts, start=1):
        metadata_text = f"\nMetadata: {context.metadata}" if context.metadata else ""

        formatted_items.append(
            f"[Context {index}]\n"
            f"ID: {context.id}\n"
            f"Score: {context.score:.4f}"
            f"{metadata_text}\n"
            f"Text:\n{context.text}"
        )

    return "\n\n".join(formatted_items)
