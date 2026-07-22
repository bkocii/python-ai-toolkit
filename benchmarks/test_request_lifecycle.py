from ai.executor import RequestExecutor


def test_plain_request_lifecycle(
    benchmark,
    fake_text_provider,
    benchmark_logger,
):
    executor = RequestExecutor(
        provider=fake_text_provider,
        model="benchmark-model",
        logger=benchmark_logger,
    )

    result = benchmark(
        executor.execute,
        "Benchmark prompt",
    )

    assert result.data == "Benchmark response"
    assert result.raw_response == "Benchmark response"
    assert result.original_raw_response == "Benchmark response"
    assert result.model == "benchmark-model"
    assert result.retries_used == 0
    assert result.request_id
    assert result.duration_ms is not None
    assert result.duration_ms >= 0
    assert result.token_usage is not None
    assert result.token_usage.input_tokens == 10
    assert result.token_usage.output_tokens == 5
    assert result.token_usage.total_tokens == 15
