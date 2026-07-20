from typing import Annotated, get_args, get_origin

from fastapi.params import Depends

from ai.async_client import AsyncAIClient
from ai.client import AIClient
from ai.integrations.fastapi import (
    AIClientDependency,
    AsyncAIClientDependency,
    get_ai_client,
    get_async_ai_client,
)
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


class SummaryRequest(BaseModel):
    text: str


def test_get_ai_client_returns_ai_client(monkeypatch):
    expected_client = object()

    monkeypatch.setattr(
        "ai.integrations.fastapi.dependencies.AIClient",
        lambda: expected_client,
    )

    client = get_ai_client()

    assert client is expected_client


def test_get_async_ai_client_returns_async_ai_client(monkeypatch):
    expected_client = object()

    monkeypatch.setattr(
        "ai.integrations.fastapi.dependencies.AsyncAIClient",
        lambda: expected_client,
    )

    client = get_async_ai_client()

    assert client is expected_client


def test_fastapi_helpers_have_expected_return_annotations():
    assert get_ai_client.__annotations__["return"] is AIClient
    assert get_async_ai_client.__annotations__["return"] is AsyncAIClient


def test_ai_client_dependency_wraps_sync_client():
    origin = get_origin(AIClientDependency)
    arguments = get_args(AIClientDependency)

    assert origin is Annotated
    assert arguments[0] is AIClient

    dependency = arguments[1]

    assert isinstance(dependency, Depends)
    assert dependency.dependency is get_ai_client


def test_async_ai_client_dependency_wraps_async_client():
    origin = get_origin(AsyncAIClientDependency)
    arguments = get_args(AsyncAIClientDependency)

    assert origin is Annotated
    assert arguments[0] is AsyncAIClient

    dependency = arguments[1]

    assert isinstance(dependency, Depends)
    assert dependency.dependency is get_async_ai_client


def test_fastapi_injects_ai_client_into_endpoint():
    app = FastAPI()
    captured_prompts: list[str] = []

    class FakeAIClient:
        def ask(self, prompt: str):
            captured_prompts.append(prompt)
            return SimpleNamespace(data="Short summary")

    @app.post("/summarize")
    def summarize(
        request: SummaryRequest,
        client: AIClientDependency,
    ):
        result = client.ask(f"Summarize this text:\n\n{request.text}")

        return {"summary": result.data}

    app.dependency_overrides[get_ai_client] = FakeAIClient

    test_client = TestClient(app)

    response = test_client.post(
        "/summarize",
        json={"text": "This is a long customer message."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": "Short summary",
    }
    assert captured_prompts == [
        "Summarize this text:\n\nThis is a long customer message."
    ]


def test_fastapi_injects_async_ai_client_into_endpoint():
    app = FastAPI()
    captured_prompts: list[str] = []

    class FakeAsyncAIClient:
        async def ask(self, prompt: str):
            captured_prompts.append(prompt)
            return SimpleNamespace(data="Async summary")

    @app.post("/summarize-async")
    async def summarize_async(
        request: SummaryRequest,
        client: AsyncAIClientDependency,
    ):
        result = await client.ask(
            f"Summarize this text asynchronously:\n\n{request.text}"
        )

        return {"summary": result.data}

    app.dependency_overrides[get_async_ai_client] = FakeAsyncAIClient

    test_client = TestClient(app)

    response = test_client.post(
        "/summarize-async",
        json={"text": "This is an asynchronous customer message."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": "Async summary",
    }
    assert captured_prompts == [
        (
            "Summarize this text asynchronously:\n\n"
            "This is an asynchronous customer message."
        )
    ]
