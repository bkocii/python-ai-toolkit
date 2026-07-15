from pydantic import BaseModel, Field

from ai.schemas import TokenUsage


class EmbeddingInput(BaseModel):
    """
    Text input to embed.
    """

    text: str
    metadata: dict[str, str] = Field(default_factory=dict)


class EmbeddingVector(BaseModel):
    """
    One embedded text result.
    """

    text: str
    vector: list[float]
    index: int
    metadata: dict[str, str] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    """
    Provider-independent embedding response.

    embeddings:
        One vector per input text.

    model:
        Embedding model used by the provider.

    token_usage:
        Optional token usage reported by the provider.
    """

    embeddings: list[EmbeddingVector]
    model: str
    token_usage: TokenUsage | None = None

    @property
    def vectors(self) -> list[list[float]]:
        """
        Convenience accessor for only the raw vectors.
        """
        return [embedding.vector for embedding in self.embeddings]

    @property
    def texts(self) -> list[str]:
        """
        Convenience accessor for original input texts.
        """
        return [embedding.text for embedding in self.embeddings]
