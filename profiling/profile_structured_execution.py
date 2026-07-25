import cProfile
import io
import json
import logging
import platform
import pstats
import sys
from collections.abc import Callable
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

from pydantic import BaseModel

from ai.executor import RequestExecutor
from ai.retry import build_json_repair_prompt
from ai.schemas import AIResult, TokenUsage
from ai.structured import build_structured_prompt, parse_structured_response

COMPONENT_ITERATIONS = 50_000
LIFECYCLE_ITERATIONS = 25_000

ORIGINAL_PROMPT = "Return contact information."
INVALID_RESPONSE = "This is not valid JSON."
VALID_RESPONSE = (
    '{"name":"Profile User","email":"profile@example.com","age":35,'
    '"active":true,"tags":["python","automation","ai"]}'
)


class ProfileContact(BaseModel):
    name: str
    email: str
    age: int
    active: bool
    tags: list[str]


VALID_DATA = json.loads(VALID_RESPONSE)
TOKEN_USAGE = TokenUsage(
    input_tokens=10,
    output_tokens=5,
    total_tokens=15,
)


class ProfileStructuredProvider:
    """
    Return one prebuilt valid structured response for every request.
    """

    def __init__(self) -> None:
        self.response = SimpleNamespace(
            text=VALID_RESPONSE,
            token_usage=TOKEN_USAGE,
        )

    def ask_text(self, _prompt: str) -> Any:
        return self.response


class ProfileRepairProvider:
    """
    Alternate between one invalid response and one valid repaired response.
    """

    def __init__(self) -> None:
        self.responses = (
            SimpleNamespace(
                text=INVALID_RESPONSE,
                token_usage=TOKEN_USAGE,
            ),
            SimpleNamespace(
                text=VALID_RESPONSE,
                token_usage=TOKEN_USAGE,
            ),
        )
        self.call_count = 0

    def ask_text(self, _prompt: str) -> Any:
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response


def build_profile_logger() -> logging.Logger:
    """
    Build an INFO logger that creates records without console or file output.
    """
    logger = logging.getLogger("python_ai_toolkit.profiling.structured_execution")

    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.NullHandler())

    return logger


def profile_structured_prompt_construction() -> None:
    prompt = ""

    for _ in range(COMPONENT_ITERATIONS):
        prompt = build_structured_prompt(
            prompt=ORIGINAL_PROMPT,
            response_type=ProfileContact,
        )

    if ORIGINAL_PROMPT not in prompt or "ProfileContact" not in prompt:
        raise AssertionError("Unexpected structured prompt.")


def profile_json_decoding() -> None:
    data = None

    for _ in range(COMPONENT_ITERATIONS):
        data = json.loads(VALID_RESPONSE)

    if data != VALID_DATA:
        raise AssertionError("Unexpected decoded JSON data.")


def profile_pydantic_validation() -> None:
    result = None

    for _ in range(COMPONENT_ITERATIONS):
        result = ProfileContact.model_validate(VALID_DATA)

    if result is None or result.email != "profile@example.com":
        raise AssertionError("Unexpected Pydantic validation result.")


def profile_combined_structured_parsing() -> None:
    result = None

    for _ in range(COMPONENT_ITERATIONS):
        result = parse_structured_response(
            raw_response=VALID_RESPONSE,
            response_type=ProfileContact,
        )

    if result is None or result.tags != ["python", "automation", "ai"]:
        raise AssertionError("Unexpected structured parsing result.")


def profile_repair_prompt_construction() -> None:
    prompt = ""
    structured_prompt = build_structured_prompt(
        prompt=ORIGINAL_PROMPT,
        response_type=ProfileContact,
    )

    for _ in range(COMPONENT_ITERATIONS):
        prompt = build_json_repair_prompt(
            original_prompt=structured_prompt,
            invalid_response=INVALID_RESPONSE,
        )

    if INVALID_RESPONSE not in prompt or structured_prompt not in prompt:
        raise AssertionError("Unexpected repair prompt.")


def profile_token_usage_aggregation() -> None:
    result = None

    for _ in range(COMPONENT_ITERATIONS):
        result = TOKEN_USAGE.add(TOKEN_USAGE)

    if result is None or result.total_tokens != 30:
        raise AssertionError("Unexpected token aggregation result.")


def profile_result_construction() -> None:
    result = None
    contact = ProfileContact.model_validate(VALID_DATA)

    for _ in range(COMPONENT_ITERATIONS):
        result = AIResult(
            data=contact,
            model="profile-model",
            raw_response=VALID_RESPONSE,
            original_raw_response=VALID_RESPONSE,
            duration_ms=1.0,
            retries_used=0,
            token_usage=TOKEN_USAGE,
            estimated_cost_usd=Decimal("0.000020"),
            request_id="profile-request-id",
        )

    if result is None or result.data != contact:
        raise AssertionError("Unexpected AIResult.")


def profile_successful_structured_lifecycle(
    executor: RequestExecutor,
) -> None:
    result = None

    for _ in range(LIFECYCLE_ITERATIONS):
        result = executor.execute(
            prompt=ORIGINAL_PROMPT,
            response_type=ProfileContact,
        )

    if result is None or result.retries_used != 0:
        raise AssertionError("Unexpected successful structured result.")


def profile_repair_lifecycle(
    executor: RequestExecutor,
) -> None:
    result = None

    for _ in range(LIFECYCLE_ITERATIONS):
        result = executor.execute(
            prompt=ORIGINAL_PROMPT,
            response_type=ProfileContact,
        )

    if result is None or result.retries_used != 1:
        raise AssertionError("Unexpected repaired structured result.")


def print_profile(
    title: str,
    operation: Callable[[], None],
) -> None:
    profiler = cProfile.Profile()

    profiler.enable()
    operation()
    profiler.disable()

    output = io.StringIO()
    statistics = pstats.Stats(
        profiler,
        stream=output,
    )
    statistics.strip_dirs()
    statistics.sort_stats("cumulative")
    statistics.print_stats(35)
    statistics.print_stats(
        r"(cost|executor|parser|profile_structured_execution|"
        r"retry|schemas|structured)\.py"
    )

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(output.getvalue())


def main() -> None:
    logger = build_profile_logger()

    successful_executor = RequestExecutor(
        provider=ProfileStructuredProvider(),
        model="profile-model",
        logger=logger,
        input_cost_per_1m_tokens="1.00",
        output_cost_per_1m_tokens="2.00",
    )
    repair_executor = RequestExecutor(
        provider=ProfileRepairProvider(),
        model="profile-model",
        max_retries=1,
        logger=logger,
        input_cost_per_1m_tokens="1.00",
        output_cost_per_1m_tokens="2.00",
    )

    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"Component iterations: {COMPONENT_ITERATIONS:,}")
    print(f"Lifecycle iterations: {LIFECYCLE_ITERATIONS:,}")

    profile_cases = (
        (
            "Structured prompt construction",
            profile_structured_prompt_construction,
        ),
        (
            "JSON decoding",
            profile_json_decoding,
        ),
        (
            "Pydantic schema validation",
            profile_pydantic_validation,
        ),
        (
            "Combined structured parsing",
            profile_combined_structured_parsing,
        ),
        (
            "Repair prompt construction",
            profile_repair_prompt_construction,
        ),
        (
            "Token usage aggregation",
            profile_token_usage_aggregation,
        ),
        (
            "AIResult construction",
            profile_result_construction,
        ),
        (
            "Successful structured request lifecycle",
            lambda: profile_successful_structured_lifecycle(successful_executor),
        ),
        (
            "One-retry structured repair lifecycle",
            lambda: profile_repair_lifecycle(repair_executor),
        ),
    )

    for title, operation in profile_cases:
        print_profile(
            title=title,
            operation=operation,
        )


if __name__ == "__main__":
    main()
