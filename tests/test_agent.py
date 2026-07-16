import pytest

from ai.agent import Agent, AgentResponse
from ai.memory import InMemoryConversationMemory, MessageRole
from ai.schemas import AIResult


class FakeAIClient:
    def __init__(self):
        self.received_prompt = None

    def ask(self, prompt: str):
        self.received_prompt = prompt

        return AIResult(
            data="Redis is often used as a cache.",
            raw_response="Redis is often used as a cache.",
            model="fake-model",
            request_id="request-123",
            duration_ms=10.0,
            cached=False,
            token_usage=None,
            estimated_cost_usd=None,
            retries_used=0,
            original_raw_response="Redis is often used as a cache.",
        )


def test_agent_response_stores_output_metadata_and_messages():
    memory = InMemoryConversationMemory()
    memory.add_user_message("What is Redis?")

    response = AgentResponse(
        output="Redis is often used as a cache.",
        model="fake-model",
        request_id="request-123",
        messages=memory.messages(),
    )

    assert response.output == "Redis is often used as a cache."
    assert response.model == "fake-model"
    assert response.request_id == "request-123"
    assert len(response.messages) == 1


def test_agent_rejects_empty_instructions():
    with pytest.raises(
        ValueError,
        match="Agent instructions cannot be empty",
    ):
        Agent(
            ai_client=FakeAIClient(),
            instructions="   ",
        )


def test_agent_rejects_invalid_memory_limit():
    with pytest.raises(
        ValueError,
        match="Agent memory_limit must be greater than zero",
    ):
        Agent(
            ai_client=FakeAIClient(),
            instructions="You are helpful.",
            memory_limit=0,
        )


def test_agent_rejects_empty_message():
    agent = Agent(
        ai_client=FakeAIClient(),
        instructions="You are helpful.",
    )

    with pytest.raises(
        ValueError,
        match="Agent message cannot be empty",
    ):
        agent.run("   ")


def test_agent_stores_user_and_assistant_messages():
    memory = InMemoryConversationMemory()

    agent = Agent(
        ai_client=FakeAIClient(),
        instructions="You are helpful.",
        memory=memory,
    )

    response = agent.run("What is Redis?")

    messages = response.messages

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "What is Redis?"
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == "Redis is often used as a cache."


def test_agent_preserves_user_metadata():
    memory = InMemoryConversationMemory()

    agent = Agent(
        ai_client=FakeAIClient(),
        instructions="You are helpful.",
        memory=memory,
    )

    response = agent.run(
        "What is Redis?",
        metadata={"user_id": "123"},
    )

    assert response.messages[0].metadata == {"user_id": "123"}


def test_agent_stores_assistant_metadata():
    memory = InMemoryConversationMemory()

    agent = Agent(
        ai_client=FakeAIClient(),
        instructions="You are helpful.",
        memory=memory,
    )

    response = agent.run("What is Redis?")

    assistant_message = response.messages[1]

    assert assistant_message.metadata == {
        "request_id": "request-123",
        "model": "fake-model",
    }


def test_agent_returns_ai_result_metadata():
    agent = Agent(
        ai_client=FakeAIClient(),
        instructions="You are helpful.",
    )

    response = agent.run("What is Redis?")

    assert response.output == "Redis is often used as a cache."
    assert response.model == "fake-model"
    assert response.request_id == "request-123"


def test_agent_prompt_includes_instructions_conversation_and_message():
    ai_client = FakeAIClient()

    agent = Agent(
        ai_client=ai_client,
        instructions="You are a concise assistant.",
    )

    agent.run("What is Redis?")

    assert ai_client.received_prompt is not None
    assert "Instructions:" in ai_client.received_prompt
    assert "You are a concise assistant." in ai_client.received_prompt
    assert "Conversation so far:" in ai_client.received_prompt
    assert "USER:\nWhat is Redis?" in ai_client.received_prompt
    assert "Current user message:" in ai_client.received_prompt
    assert "What is Redis?" in ai_client.received_prompt


def test_agent_uses_recent_memory_limit():
    ai_client = FakeAIClient()
    memory = InMemoryConversationMemory()

    memory.add_user_message("First")
    memory.add_assistant_message("Second")
    memory.add_user_message("Third")

    agent = Agent(
        ai_client=ai_client,
        instructions="You are helpful.",
        memory=memory,
        memory_limit=2,
    )

    agent.run("Fourth")

    assert ai_client.received_prompt is not None
    assert "First" not in ai_client.received_prompt
    assert "Second" not in ai_client.received_prompt
    assert "Third" in ai_client.received_prompt
    assert "Fourth" in ai_client.received_prompt


def test_agent_reuses_memory_across_runs():
    memory = InMemoryConversationMemory()

    agent = Agent(
        ai_client=FakeAIClient(),
        instructions="You are helpful.",
        memory=memory,
    )

    agent.run("What is Redis?")
    response = agent.run("Can it help Django apps?")

    assert len(response.messages) == 4
    assert response.messages[0].content == "What is Redis?"
    assert response.messages[2].content == "Can it help Django apps?"
