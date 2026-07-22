import pytest

from ai.vector_store import (
    InMemoryVectorStore,
    VectorRecord,
)

RECORD_COUNT = 1_000
VECTOR_DIMENSIONS = 64
RESULT_LIMIT = 5
TARGET_INDEX = 500


def build_deterministic_vector(
    record_index: int,
) -> list[float]:
    """
    Create a deterministic, non-random vector.

    The generated vectors require no embedding provider and remain
    identical across benchmark runs.
    """
    vector = []

    for dimension_index in range(VECTOR_DIMENSIONS):
        value = (((record_index + 1) * (dimension_index + 3)) % 101) / 100.0

        if dimension_index == record_index % VECTOR_DIMENSIONS:
            value += 1.0

        vector.append(value)

    return vector


@pytest.fixture(scope="module")
def vector_search_dataset():
    """
    Build the vector store before benchmark timing begins.
    """
    records = [
        VectorRecord(
            id=f"record-{record_index}",
            text=f"Benchmark document {record_index}",
            vector=build_deterministic_vector(record_index),
            metadata={
                "source": ("even" if record_index % 2 == 0 else "odd"),
                "group": str(record_index % 10),
            },
        )
        for record_index in range(RECORD_COUNT)
    ]

    store = InMemoryVectorStore()
    store.add(records)

    query_vector = list(records[TARGET_INDEX].vector)

    return store, query_vector


def test_vector_similarity_search(
    benchmark,
    vector_search_dataset,
):
    store, query_vector = vector_search_dataset

    results = benchmark(
        store.similarity_search,
        query_vector=query_vector,
        limit=RESULT_LIMIT,
    )

    assert len(results) == RESULT_LIMIT
    assert results[0].id == f"record-{TARGET_INDEX}"
    assert results[0].score == pytest.approx(1.0)
    assert results[0].vector == query_vector

    assert all(
        results[index].score >= results[index + 1].score
        for index in range(len(results) - 1)
    )


def test_vector_similarity_search_with_metadata_filter(
    benchmark,
    vector_search_dataset,
):
    store, query_vector = vector_search_dataset

    results = benchmark(
        store.similarity_search,
        query_vector=query_vector,
        limit=RESULT_LIMIT,
        metadata_filter={"source": "even"},
    )

    assert len(results) == RESULT_LIMIT
    assert results[0].id == f"record-{TARGET_INDEX}"
    assert results[0].score == pytest.approx(1.0)

    assert all(result.metadata["source"] == "even" for result in results)

    assert all(
        results[index].score >= results[index + 1].score
        for index in range(len(results) - 1)
    )
