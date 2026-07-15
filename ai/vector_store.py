from abc import ABC, abstractmethod
import math
from pydantic import BaseModel, Field


class VectorRecord(BaseModel):
    """
    One item stored in a vector store.

    id:
        Stable application-level identifier.

    text:
        Original text represented by the vector.

    vector:
        Embedding vector.

    metadata:
        Extra information such as source file, table name, row ID, chunk ID,
        user ID, or document type.
    """

    id: str
    text: str
    vector: list[float]
    metadata: dict[str, str] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    """
    One search result returned from a vector store.
    """

    id: str
    text: str
    vector: list[float]
    score: float
    metadata: dict[str, str] = Field(default_factory=dict)


class BaseVectorStore(ABC):
    """
    Provider-independent vector store interface.
    """

    @abstractmethod
    def add(
        self,
        records: list[VectorRecord],
    ) -> None:
        """
        Add records to the vector store.
        """
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self,
        query_vector: list[float],
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Return records most similar to the query vector.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """
        Return number of records in the vector store.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all records from the vector store.
        """
        raise NotImplementedError


class InMemoryVectorStore(BaseVectorStore):
    """
    Simple in-memory vector store.

    Useful for tests, demos, small local apps, and as the reference
    implementation for the vector store interface.
    """

    def __init__(self):
        self._records: dict[str, VectorRecord] = {}

    def add(
        self,
        records: list[VectorRecord],
    ) -> None:
        """
        Add or replace records by ID.
        """
        for record in records:
            self._records[record.id] = record

    def similarity_search(
        self,
        query_vector: list[float],
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Return records ranked by cosine similarity.
        """
        if limit <= 0:
            return []

        candidates = [
            record
            for record in self._records.values()
            if self._matches_metadata_filter(record, metadata_filter)
        ]

        results = [
            VectorSearchResult(
                id=record.id,
                text=record.text,
                vector=record.vector,
                score=self._cosine_similarity(query_vector, record.vector),
                metadata=record.metadata,
            )
            for record in candidates
        ]

        return sorted(
            results,
            key=lambda result: result.score,
            reverse=True,
        )[:limit]

    def count(self) -> int:
        """
        Return number of stored records.
        """
        return len(self._records)

    def clear(self) -> None:
        """
        Remove all stored records.
        """
        self._records.clear()

    def _matches_metadata_filter(
        self,
        record: VectorRecord,
        metadata_filter: dict[str, str] | None,
    ) -> bool:
        if metadata_filter is None:
            return True

        return all(
            record.metadata.get(key) == value for key, value in metadata_filter.items()
        )

    def _cosine_similarity(
        self,
        first: list[float],
        second: list[float],
    ) -> float:
        if len(first) != len(second):
            raise ValueError(
                "Vectors must have the same dimensions for similarity search."
            )

        dot_product = sum(a * b for a, b in zip(first, second, strict=True))
        first_norm = math.sqrt(sum(a * a for a in first))
        second_norm = math.sqrt(sum(b * b for b in second))

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return dot_product / (first_norm * second_norm)
