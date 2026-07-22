def increment(value: int) -> int:
    return value + 1


def test_benchmark_tooling_is_available(benchmark):
    result = benchmark(increment, 1)

    assert result == 2
