import cProfile
import io
import pstats

from ai.vector_store import InMemoryVectorStore, VectorRecord

RECORD_COUNT = 1_000
VECTOR_DIMENSIONS = 64
RESULT_LIMIT = 5
TARGET_INDEX = 500
PROFILE_ITERATIONS = 100


def build_deterministic_vector(
    record_index: int,
) -> list[float]:
    vector = []

    for dimension_index in range(VECTOR_DIMENSIONS):
        value = (
            ((record_index + 1) * (dimension_index + 3)) % 101
        ) / 100.0

        if dimension_index == record_index % VECTOR_DIMENSIONS:
            value += 1.0

        vector.append(value)

    return vector


def build_dataset() -> tuple[
    InMemoryVectorStore,
    list[float],
]:
    records = [
        VectorRecord(
            id=f"record-{record_index}",
            text=f"Profile document {record_index}",
            vector=build_deterministic_vector(record_index),
            metadata={
                "source": (
                    "even"
                    if record_index % 2 == 0
                    else "odd"
                ),
                "group": str(record_index % 10),
            },
        )
        for record_index in range(RECORD_COUNT)
    ]

    store = InMemoryVectorStore()
    store.add(records)

    query_vector = list(records[TARGET_INDEX].vector)

    return store, query_vector


def profile_unfiltered_search(
    store: InMemoryVectorStore,
    query_vector: list[float],
) -> None:
    for _ in range(PROFILE_ITERATIONS):
        store.similarity_search(
            query_vector=query_vector,
            limit=RESULT_LIMIT,
        )


def profile_filtered_search(
    store: InMemoryVectorStore,
    query_vector: list[float],
) -> None:
    for _ in range(PROFILE_ITERATIONS):
        store.similarity_search(
            query_vector=query_vector,
            limit=RESULT_LIMIT,
            metadata_filter={
                "source": "even",
            },
        )


def print_profile(
    title: str,
    function,
    store: InMemoryVectorStore,
    query_vector: list[float],
) -> None:
    profiler = cProfile.Profile()

    profiler.enable()
    function(store, query_vector)
    profiler.disable()

    output = io.StringIO()

    statistics = pstats.Stats(
        profiler,
        stream=output,
    )
    statistics.strip_dirs()
    statistics.sort_stats("cumulative")
    statistics.print_stats(30)

    print(f"\n{'=' * 80}")
    print(title)
    print(f"{'=' * 80}")
    print(output.getvalue())


def main() -> None:
    store, query_vector = build_dataset()

    print_profile(
        title="Unfiltered vector similarity search",
        function=profile_unfiltered_search,
        store=store,
        query_vector=query_vector,
    )

    print_profile(
        title="Metadata-filtered vector similarity search",
        function=profile_filtered_search,
        store=store,
        query_vector=query_vector,
    )


if __name__ == "__main__":
    main()
