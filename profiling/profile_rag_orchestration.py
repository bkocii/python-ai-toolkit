import cProfile
import io
import platform
import pstats
import sys
from collections.abc import Callable

from ai.rag import RAGPipeline, RAGResponse, build_rag_prompt
from ai.retriever import RetrievedContext, format_retrieved_context
from ai.schemas import AIResult

COMPONENT_ITERATIONS = 100_000
LIFECYCLE_ITERATIONS = 50_000

QUESTION = "Which technologies can support a Python web application?"
INSTRUCTIONS = "Answer in one concise paragraph."
METADATA_FILTER = {"source": "documentation"}
RESULT_LIMIT = 5

CONTEXTS = [
    RetrievedContext(
        id="django",
        text="Django is a Python web framework.",
        score=0.99,
        metadata={
            "source": "documentation",
            "topic": "web",
        },
    ),
    RetrievedContext(
        id="postgresql",
        text="PostgreSQL is a relational database.",
        score=0.95,
        metadata={
            "source": "documentation",
            "topic": "database",
        },
    ),
    RetrievedContext(
        id="redis",
        text="Redis can be used for caching and messaging.",
        score=0.91,
        metadata={
            "source": "documentation",
            "topic": "cache",
        },
    ),
    RetrievedContext(
        id="celery",
        text="Celery processes background tasks.",
        score=0.87,
        metadata={
            "source": "documentation",
            "topic": "tasks",
        },
    ),
    RetrievedContext(
        id="nginx",
        text="Nginx can proxy requests to a Python application.",
        score=0.82,
        metadata={
            "source": "documentation",
            "topic": "deployment",
        },
    ),
]

ANSWER = (
    "Django can provide the web application, PostgreSQL can store relational "
    "data, Redis can support caching and messaging, Celery can process "
    "background tasks, and Nginx can proxy incoming requests."
)

AI_RESULT = AIResult(
    data=ANSWER,
    model="profile-model",
    raw_response=ANSWER,
    original_raw_response=ANSWER,
    request_id="profile-request",
)

FORMATTED_CONTEXT = format_retrieved_context(CONTEXTS)


class ProfileRetriever:
    """
    Return prebuilt contexts without embeddings or vector search.
    """

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedContext]:
        return CONTEXTS


class ProfileAIClient:
    """
    Return a prebuilt result without provider or model execution.
    """

    def ask(self, prompt: str) -> AIResult:
        return AI_RESULT


def profile_context_formatting() -> None:
    context_text = ""

    for _ in range(COMPONENT_ITERATIONS):
        context_text = format_retrieved_context(CONTEXTS)

    if "[Context 5]" not in context_text or "Nginx" not in context_text:
        raise AssertionError("Unexpected formatted context.")


def profile_prompt_construction_without_instructions() -> None:
    prompt = ""

    for _ in range(COMPONENT_ITERATIONS):
        prompt = build_rag_prompt(
            question=QUESTION,
            context_text=FORMATTED_CONTEXT,
        )

    if QUESTION not in prompt or "Additional instructions:" in prompt:
        raise AssertionError("Unexpected grounded prompt.")


def profile_prompt_construction_with_instructions() -> None:
    prompt = ""

    for _ in range(COMPONENT_ITERATIONS):
        prompt = build_rag_prompt(
            question=QUESTION,
            context_text=FORMATTED_CONTEXT,
            instructions=INSTRUCTIONS,
        )

    if INSTRUCTIONS not in prompt or "Additional instructions:" not in prompt:
        raise AssertionError("Unexpected instructed grounded prompt.")


def profile_rag_response_construction() -> None:
    response = None

    for _ in range(COMPONENT_ITERATIONS):
        response = RAGResponse(
            answer=ANSWER,
            contexts=CONTEXTS,
            model=AI_RESULT.model,
            request_id=AI_RESULT.request_id,
            raw_response=AI_RESULT.raw_response,
        )

    if response is None or response.contexts != CONTEXTS:
        raise AssertionError("Unexpected RAG response.")


def profile_rag_orchestration(
    pipeline: RAGPipeline,
) -> None:
    response = None

    for _ in range(LIFECYCLE_ITERATIONS):
        response = pipeline.ask(
            question=QUESTION,
            limit=RESULT_LIMIT,
            metadata_filter=METADATA_FILTER,
            instructions=INSTRUCTIONS,
        )

    if response is None or response.answer != ANSWER:
        raise AssertionError("Unexpected RAG orchestration response.")


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
    statistics.print_stats(r"(profile_rag_orchestration|rag|retriever)\.py")

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(output.getvalue())


def main() -> None:
    pipeline = RAGPipeline(
        ai_client=ProfileAIClient(),
        retriever=ProfileRetriever(),
    )

    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"Component iterations: {COMPONENT_ITERATIONS:,}")
    print(f"Lifecycle iterations: {LIFECYCLE_ITERATIONS:,}")

    profile_cases = (
        (
            "Retrieved-context formatting",
            profile_context_formatting,
        ),
        (
            "Grounded prompt construction without instructions",
            profile_prompt_construction_without_instructions,
        ),
        (
            "Grounded prompt construction with instructions",
            profile_prompt_construction_with_instructions,
        ),
        (
            "RAGResponse construction",
            profile_rag_response_construction,
        ),
        (
            "Complete RAG orchestration",
            lambda: profile_rag_orchestration(pipeline),
        ),
    )

    for title, operation in profile_cases:
        print_profile(
            title=title,
            operation=operation,
        )


if __name__ == "__main__":
    main()
