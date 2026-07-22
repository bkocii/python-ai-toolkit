import pytest

from ai.rag import RAGPipeline
from ai.retriever import RetrievedContext
from ai.schemas import AIResult

QUESTION = "Which technologies can support a Python web application?"
INSTRUCTIONS = "Answer in one concise paragraph."
RESULT_LIMIT = 5


class BenchmarkRetriever:
    """
    Return prebuilt contexts without performing retrieval work.
    """

    def __init__(
        self,
        contexts: list[RetrievedContext],
    ):
        self.contexts = contexts

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedContext]:
        return self.contexts


class BenchmarkAIClient:
    """
    Return a prebuilt AIResult without provider execution.
    """

    def __init__(
        self,
        result: AIResult,
    ):
        self.result = result

    def ask(
        self,
        _prompt: str,
    ) -> AIResult:
        return self.result


@pytest.fixture(scope="module")
def rag_orchestration_pipeline() -> RAGPipeline:
    contexts = [
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

    ai_result = AIResult(
        data=(
            "Django can provide the web application, PostgreSQL can "
            "store relational data, Redis can support caching and "
            "messaging, Celery can process background tasks, and "
            "Nginx can proxy incoming requests."
        ),
        model="benchmark-model",
        raw_response=(
            "Django can provide the web application, PostgreSQL can "
            "store relational data, Redis can support caching and "
            "messaging, Celery can process background tasks, and "
            "Nginx can proxy incoming requests."
        ),
        original_raw_response=(
            "Django can provide the web application, PostgreSQL can "
            "store relational data, Redis can support caching and "
            "messaging, Celery can process background tasks, and "
            "Nginx can proxy incoming requests."
        ),
        request_id="benchmark-request",
    )

    return RAGPipeline(
        ai_client=BenchmarkAIClient(ai_result),
        retriever=BenchmarkRetriever(contexts),
    )


def test_rag_orchestration(
    benchmark,
    rag_orchestration_pipeline,
):
    response = benchmark(
        rag_orchestration_pipeline.ask,
        question=QUESTION,
        limit=RESULT_LIMIT,
        metadata_filter={"source": "documentation"},
        instructions=INSTRUCTIONS,
    )

    assert response.answer.startswith("Django can provide the web application")
    assert len(response.contexts) == RESULT_LIMIT
    assert [context.id for context in response.contexts] == [
        "django",
        "postgresql",
        "redis",
        "celery",
        "nginx",
    ]
    assert response.model == "benchmark-model"
    assert response.request_id == "benchmark-request"
    assert response.raw_response == response.answer
