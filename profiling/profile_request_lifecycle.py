import cProfile
import io
import logging
import pstats
from types import SimpleNamespace
from typing import Any

from ai.executor import RequestExecutor
from ai.schemas import TokenUsage

PROFILE_ITERATIONS = 100_000


class ProfileTextProvider:
    """
    Deterministic provider used to isolate toolkit overhead.

    It performs no network request and returns the same response object
    for every invocation.
    """

    def __init__(self) -> None:
        self.response = SimpleNamespace(
            text="Benchmark response",
            token_usage=TokenUsage(
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
            ),
        )

    def ask_text(self, prompt: str) -> Any:
        return self.response


def build_profile_logger() -> logging.Logger:
    """
    Build an INFO-level logger that creates log records without writing
    to the console or filesystem.
    """
    logger = logging.getLogger("python_ai_toolkit.profiling.request_lifecycle")

    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.NullHandler())

    return logger


def profile_plain_request(
    executor: RequestExecutor,
) -> None:
    for _ in range(PROFILE_ITERATIONS):
        result = executor.execute(
            "Benchmark prompt",
        )

        if result.data != "Benchmark response":
            raise AssertionError("Unexpected profiling response.")


def print_profile(
    profiler: cProfile.Profile,
) -> None:
    output = io.StringIO()

    statistics = pstats.Stats(
        profiler,
        stream=output,
    )
    statistics.strip_dirs()
    statistics.sort_stats("cumulative")
    statistics.print_stats(40)

    print()
    print("=" * 80)
    print("Plain Request Lifecycle")
    print("=" * 80)
    print(output.getvalue())


def main() -> None:
    provider = ProfileTextProvider()
    logger = build_profile_logger()

    executor = RequestExecutor(
        provider=provider,
        model="benchmark-model",
        logger=logger,
    )

    profiler = cProfile.Profile()

    profiler.enable()
    profile_plain_request(executor)
    profiler.disable()

    print_profile(profiler)


if __name__ == "__main__":
    main()
