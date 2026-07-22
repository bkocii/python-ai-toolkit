from pydantic import BaseModel

from ai.executor import RequestExecutor

BENCHMARK_ROUNDS = 100

INVALID_RESPONSE = "This is not valid JSON."

VALID_RESPONSE = """
{
    "name": "Recovered User",
    "age": 35,
    "active": true
}
""".strip()


class RepairedContact(BaseModel):
    name: str
    age: int
    active: bool


def execute_repair_request(
    executor: RequestExecutor,
):
    return executor.execute(
        prompt="Return contact information.",
        response_type=RepairedContact,
    )


def test_structured_response_retry_and_repair(
    benchmark,
    make_sequence_text_provider,
    benchmark_logger,
):
    def setup():
        provider = make_sequence_text_provider(
            [
                INVALID_RESPONSE,
                VALID_RESPONSE,
            ]
        )

        executor = RequestExecutor(
            provider=provider,
            model="benchmark-model",
            max_retries=1,
            logger=benchmark_logger,
        )

        return (executor,), {}

    result = benchmark.pedantic(
        execute_repair_request,
        setup=setup,
        rounds=BENCHMARK_ROUNDS,
        iterations=1,
    )

    assert isinstance(result.data, RepairedContact)
    assert result.data.name == "Recovered User"
    assert result.data.age == 35
    assert result.data.active is True

    assert result.original_raw_response == INVALID_RESPONSE
    assert result.raw_response == VALID_RESPONSE
    assert result.retries_used == 1

    assert result.token_usage is not None
    assert result.token_usage.input_tokens == 20
    assert result.token_usage.output_tokens == 10
    assert result.token_usage.total_tokens == 30

    assert result.request_id
    assert result.duration_ms is not None
    assert result.duration_ms >= 0
