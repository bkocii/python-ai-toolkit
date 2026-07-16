import pytest

from ai.rag import RAGPipeline, RAGResponse, build_rag_prompt
from ai.retriever import RetrievedContext
from ai.schemas import AIResult


class FakeRetriever:
    def __init__(self):
        self.received_query = None
        self.received_limit = None
        self.received_metadata_filter = None

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedContext]:
        self.received_query = query
        self.received_limit = limit
        self.received_metadata_filter = metadata_filter

        return [
            RetrievedContext(
                id="redis",
                text="Redis is often used as a cache.",
                score=0.95,
                metadata={"topic": "redis"},
            )
        ]


class FakeAIClient:
    def __init__(self):
        self.received_prompt = None

    def ask(self, prompt: str):
        self.received_prompt = prompt

        return AIResult(
            data="Redis is a good choice for caching.",
            raw_response="Redis is a good choice for caching.",
            model="fake-model",
            request_id="request-123",
            duration_ms=10.0,
            cached=False,
            token_usage=None,
            estimated_cost_usd=None,
            retries_used=0,
            original_raw_response="Redis is a good choice for caching.",
        )


def test_rag_response_stores_answer_and_contexts():
    context = RetrievedContext(
        id="redis",
        text="Redis is often used as a cache.",
        score=0.95,
    )

    response = RAGResponse(
        answer="Redis is useful for caching.",
        contexts=[context],
        model="fake-model",
        request_id="request-123",
        raw_response="Redis is useful for caching.",
    )

    assert response.answer == "Redis is useful for caching."
    assert response.contexts == [context]
    assert response.model == "fake-model"
    assert response.request_id == "request-123"
    assert response.raw_response == "Redis is useful for caching."


def test_build_rag_prompt_includes_question_and_context():
    prompt = build_rag_prompt(
        question="Which technology should I use for caching?",
        context_text="[Context 1]\nRedis is often used as a cache.",
    )

    assert "Which technology should I use for caching?" in prompt
    assert "[Context 1]" in prompt
    assert "Redis is often used as a cache." in prompt


def test_build_rag_prompt_includes_grounding_rules():
    prompt = build_rag_prompt(
        question="Which technology should I use?",
        context_text="Some context.",
    )

    assert "using only the context below" in prompt
    assert "Do not invent facts" in prompt
    assert "do not know based on the provided context" in prompt


def test_build_rag_prompt_includes_additional_instructions():
    prompt = build_rag_prompt(
        question="Which technology should I use?",
        context_text="Some context.",
        instructions="Answer in one sentence.",
    )

    assert "Additional instructions:" in prompt
    assert "Answer in one sentence." in prompt


def test_rag_pipeline_retrieves_context_and_asks_ai():
    ai_client = FakeAIClient()
    retriever = FakeRetriever()

    pipeline = RAGPipeline(
        ai_client=ai_client,
        retriever=retriever,
    )

    response = pipeline.ask(
        question="Which technology should I use for caching?",
        limit=2,
    )

    assert retriever.received_query == "Which technology should I use for caching?"
    assert retriever.received_limit == 2
    assert response.answer == "Redis is a good choice for caching."
    assert response.contexts[0].id == "redis"
    assert response.model == "fake-model"
    assert response.request_id == "request-123"


def test_rag_pipeline_passes_metadata_filter_to_retriever():
    ai_client = FakeAIClient()
    retriever = FakeRetriever()

    pipeline = RAGPipeline(
        ai_client=ai_client,
        retriever=retriever,
    )

    pipeline.ask(
        question="Which technology should I use for caching?",
        metadata_filter={"topic": "redis"},
    )

    assert retriever.received_metadata_filter == {"topic": "redis"}


def test_rag_pipeline_includes_context_in_prompt():
    ai_client = FakeAIClient()
    retriever = FakeRetriever()

    pipeline = RAGPipeline(
        ai_client=ai_client,
        retriever=retriever,
    )

    pipeline.ask(
        question="Which technology should I use for caching?",
    )

    assert ai_client.received_prompt is not None
    assert "Redis is often used as a cache." in ai_client.received_prompt
    assert "Which technology should I use for caching?" in ai_client.received_prompt


def test_rag_pipeline_includes_instructions_in_prompt():
    ai_client = FakeAIClient()
    retriever = FakeRetriever()

    pipeline = RAGPipeline(
        ai_client=ai_client,
        retriever=retriever,
    )

    pipeline.ask(
        question="Which technology should I use for caching?",
        instructions="Answer briefly.",
    )

    assert ai_client.received_prompt is not None
    assert "Answer briefly." in ai_client.received_prompt


def test_rag_pipeline_rejects_empty_question():
    pipeline = RAGPipeline(
        ai_client=FakeAIClient(),
        retriever=FakeRetriever(),
    )

    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        pipeline.ask("   ")
