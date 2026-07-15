import pytest

from ai.vector_store import (
    InMemoryVectorStore,
    VectorRecord,
    VectorSearchResult,
)


def test_vector_record_stores_text_vector_and_metadata():
    record = VectorRecord(
        id="doc-1",
        text="Django is a Python web framework.",
        vector=[1.0, 0.0, 0.0],
        metadata={
            "source": "docs",
            "topic": "django",
        },
    )

    assert record.id == "doc-1"
    assert record.text == "Django is a Python web framework."
    assert record.vector == [1.0, 0.0, 0.0]
    assert record.metadata == {
        "source": "docs",
        "topic": "django",
    }


def test_vector_search_result_stores_score():
    result = VectorSearchResult(
        id="doc-1",
        text="Django is a Python web framework.",
        vector=[1.0, 0.0, 0.0],
        score=0.95,
        metadata={"topic": "django"},
    )

    assert result.score == 0.95
    assert result.metadata == {"topic": "django"}


def test_in_memory_vector_store_adds_and_counts_records():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="Django is a Python web framework.",
                vector=[1.0, 0.0, 0.0],
            ),
            VectorRecord(
                id="doc-2",
                text="Redis is often used as a cache.",
                vector=[0.0, 1.0, 0.0],
            ),
        ]
    )

    assert store.count() == 2


def test_in_memory_vector_store_replaces_records_by_id():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="Old text.",
                vector=[1.0, 0.0, 0.0],
            )
        ]
    )

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="Updated text.",
                vector=[0.0, 1.0, 0.0],
            )
        ]
    )

    results = store.similarity_search(
        query_vector=[0.0, 1.0, 0.0],
        limit=1,
    )

    assert store.count() == 1
    assert results[0].text == "Updated text."


def test_in_memory_vector_store_returns_most_similar_records_first():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="django",
                text="Django is a Python web framework.",
                vector=[1.0, 0.0, 0.0],
            ),
            VectorRecord(
                id="redis",
                text="Redis is often used as a cache.",
                vector=[0.0, 1.0, 0.0],
            ),
            VectorRecord(
                id="postgres",
                text="PostgreSQL is a relational database.",
                vector=[0.0, 0.0, 1.0],
            ),
        ]
    )

    results = store.similarity_search(
        query_vector=[0.9, 0.1, 0.0],
        limit=2,
    )

    assert [result.id for result in results] == ["django", "redis"]
    assert results[0].score > results[1].score


def test_in_memory_vector_store_respects_limit():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="First.",
                vector=[1.0, 0.0],
            ),
            VectorRecord(
                id="doc-2",
                text="Second.",
                vector=[0.9, 0.1],
            ),
            VectorRecord(
                id="doc-3",
                text="Third.",
                vector=[0.8, 0.2],
            ),
        ]
    )

    results = store.similarity_search(
        query_vector=[1.0, 0.0],
        limit=2,
    )

    assert len(results) == 2


def test_in_memory_vector_store_returns_empty_list_for_zero_limit():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="First.",
                vector=[1.0, 0.0],
            )
        ]
    )

    results = store.similarity_search(
        query_vector=[1.0, 0.0],
        limit=0,
    )

    assert results == []


def test_in_memory_vector_store_filters_by_metadata():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="faq-1",
                text="Refunds are available within 14 days.",
                vector=[1.0, 0.0],
                metadata={"source": "faq"},
            ),
            VectorRecord(
                id="product-1",
                text="Espresso is a strong coffee.",
                vector=[0.9, 0.1],
                metadata={"source": "products"},
            ),
        ]
    )

    results = store.similarity_search(
        query_vector=[1.0, 0.0],
        metadata_filter={"source": "faq"},
    )

    assert len(results) == 1
    assert results[0].id == "faq-1"
    assert results[0].metadata == {"source": "faq"}


def test_in_memory_vector_store_returns_empty_list_when_metadata_filter_matches_nothing():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="faq-1",
                text="Refunds are available within 14 days.",
                vector=[1.0, 0.0],
                metadata={"source": "faq"},
            )
        ]
    )

    results = store.similarity_search(
        query_vector=[1.0, 0.0],
        metadata_filter={"source": "products"},
    )

    assert results == []


def test_in_memory_vector_store_clear_removes_records():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="Some text.",
                vector=[1.0, 0.0],
            )
        ]
    )

    store.clear()

    assert store.count() == 0
    assert store.similarity_search([1.0, 0.0]) == []


def test_in_memory_vector_store_rejects_dimension_mismatch():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="Some text.",
                vector=[1.0, 0.0, 0.0],
            )
        ]
    )

    with pytest.raises(
        ValueError,
        match="Vectors must have the same dimensions",
    ):
        store.similarity_search(
            query_vector=[1.0, 0.0],
        )


def test_in_memory_vector_store_zero_vector_scores_zero():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="doc-1",
                text="Some text.",
                vector=[0.0, 0.0],
            )
        ]
    )

    results = store.similarity_search(
        query_vector=[1.0, 0.0],
    )

    assert results[0].score == 0.0
