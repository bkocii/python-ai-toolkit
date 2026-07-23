from collections.abc import Callable
from functools import partial
from statistics import mean, median
from time import perf_counter

from ai.vector_store import (
    InMemoryVectorStore,
    VectorRecord,
    VectorSearchResult,
)

VECTOR_DIMENSIONS = 64
RESULT_LIMIT = 5
WARMUP_ROUNDS = 3

DATASET_SIZES = (
    100,
    500,
    1_000,
    2_500,
    5_000,
)


def build_deterministic_vector(
    record_index: int,
) -> list[float]:
    vector = []

    for dimension_index in range(VECTOR_DIMENSIONS):
        value = (((record_index + 1) * (dimension_index + 3)) % 101) / 100.0

        if dimension_index == record_index % VECTOR_DIMENSIONS:
            value += 1.0

        vector.append(value)

    return vector


def build_store(
    record_count: int,
) -> tuple[
    InMemoryVectorStore,
    list[float],
    str,
]:
    records = [
        VectorRecord(
            id=f"record-{record_index}",
            text=f"Scaling document {record_index}",
            vector=build_deterministic_vector(record_index),
            metadata={
                "source": ("even" if record_index % 2 == 0 else "odd"),
                "group": str(record_index % 10),
            },
        )
        for record_index in range(record_count)
    ]

    store = InMemoryVectorStore()
    store.add(records)

    target_index = record_count // 2
    query_vector = list(records[target_index].vector)
    target_source = records[target_index].metadata["source"]

    return store, query_vector, target_source


def rounds_for_size(
    record_count: int,
) -> int:
    if record_count <= 500:
        return 50

    if record_count <= 1_000:
        return 30

    if record_count <= 2_500:
        return 15

    return 10


def measure_operation(
    operation: Callable[[], list[VectorSearchResult]],
    rounds: int,
) -> tuple[float, float]:
    for _ in range(WARMUP_ROUNDS):
        operation()

    durations = []

    for _ in range(rounds):
        started_at = perf_counter()
        operation()
        durations.append(perf_counter() - started_at)

    return (
        median(durations) * 1_000,
        mean(durations) * 1_000,
    )


def calculate_linear_fit(
    records_scanned: list[int],
    median_times_ms: list[float],
) -> tuple[float, float, float]:
    count = len(records_scanned)

    mean_x = sum(records_scanned) / count
    mean_y = sum(median_times_ms) / count

    numerator = sum(
        (x_value - mean_x) * (y_value - mean_y)
        for x_value, y_value in zip(
            records_scanned,
            median_times_ms,
            strict=True,
        )
    )

    denominator = sum((x_value - mean_x) ** 2 for x_value in records_scanned)

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    predicted_values = [intercept + slope * x_value for x_value in records_scanned]

    residual_sum = sum(
        (actual - predicted) ** 2
        for actual, predicted in zip(
            median_times_ms,
            predicted_values,
            strict=True,
        )
    )

    total_sum = sum((actual - mean_y) ** 2 for actual in median_times_ms)

    r_squared = 1.0 if total_sum == 0 else 1 - (residual_sum / total_sum)

    return slope, intercept, r_squared


def print_results(
    title: str,
    records_scanned: list[int],
    records_scored: list[int],
    median_times_ms: list[float],
    mean_times_ms: list[float],
) -> None:
    print()
    print(title)
    print("=" * len(title))
    print(
        f"{'Scanned':>10} "
        f"{'Scored':>10} "
        f"{'Median ms':>12} "
        f"{'Mean ms':>12} "
        f"{'us/scanned':>12}"
    )

    for scanned, scored, median_ms, mean_ms in zip(
        records_scanned,
        records_scored,
        median_times_ms,
        mean_times_ms,
        strict=True,
    ):
        microseconds_per_scanned_record = median_ms * 1_000 / scanned

        print(
            f"{scanned:>10,} "
            f"{scored:>10,} "
            f"{median_ms:>12.4f} "
            f"{mean_ms:>12.4f} "
            f"{microseconds_per_scanned_record:>12.4f}"
        )

    slope, intercept, r_squared = calculate_linear_fit(
        records_scanned,
        median_times_ms,
    )

    print()
    print("Estimated milliseconds per 1,000 scanned records: " f"{slope * 1_000:.4f}")
    print(f"Estimated fixed overhead: {intercept:.4f} ms")
    print(f"Linear-fit R^2: {r_squared:.6f}")


def main() -> None:
    unfiltered_scanned_counts = []
    unfiltered_scored_counts = []
    unfiltered_medians = []
    unfiltered_means = []

    filtered_scanned_counts = []
    filtered_scored_counts = []
    filtered_medians = []
    filtered_means = []

    for record_count in DATASET_SIZES:
        store, query_vector, target_source = build_store(record_count)

        rounds = rounds_for_size(record_count)

        unfiltered_operation = partial(
            store.similarity_search,
            query_vector=query_vector,
            limit=RESULT_LIMIT,
        )

        filtered_operation = partial(
            store.similarity_search,
            query_vector=query_vector,
            limit=RESULT_LIMIT,
            metadata_filter={
                "source": target_source,
            },
        )

        unfiltered_results = unfiltered_operation()
        filtered_results = filtered_operation()

        expected_target_id = f"record-{record_count // 2}"

        assert unfiltered_results[0].id == expected_target_id
        assert filtered_results[0].id == expected_target_id

        unfiltered_median, unfiltered_mean = measure_operation(
            operation=unfiltered_operation,
            rounds=rounds,
        )

        filtered_median, filtered_mean = measure_operation(
            operation=filtered_operation,
            rounds=rounds,
        )

        filtered_scored_count = sum(
            1
            for record in store._records.values()
            if record.metadata["source"] == target_source
        )

        unfiltered_scanned_counts.append(record_count)
        unfiltered_scored_counts.append(record_count)
        unfiltered_medians.append(unfiltered_median)
        unfiltered_means.append(unfiltered_mean)

        filtered_scanned_counts.append(record_count)
        filtered_scored_counts.append(filtered_scored_count)
        filtered_medians.append(filtered_median)
        filtered_means.append(filtered_mean)

    print_results(
        title="Unfiltered Vector Search Scaling",
        records_scanned=unfiltered_scanned_counts,
        records_scored=unfiltered_scored_counts,
        median_times_ms=unfiltered_medians,
        mean_times_ms=unfiltered_means,
    )

    print_results(
        title="Metadata-Filtered Vector Search Scaling",
        records_scanned=filtered_scanned_counts,
        records_scored=filtered_scored_counts,
        median_times_ms=filtered_medians,
        mean_times_ms=filtered_means,
    )


if __name__ == "__main__":
    main()
