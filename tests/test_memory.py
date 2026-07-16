from ai.memory import (
    ConversationMessage,
    InMemoryConversationMemory,
    MessageRole,
    format_conversation_messages,
)


def test_conversation_message_stores_role_content_and_metadata():
    message = ConversationMessage(
        role=MessageRole.USER,
        content="What is Redis?",
        metadata={
            "user_id": "123",
            "source": "chat",
        },
    )

    assert message.role == MessageRole.USER
    assert message.content == "What is Redis?"
    assert message.metadata == {
        "user_id": "123",
        "source": "chat",
    }
    assert message.created_at > 0


def test_conversation_message_defaults_metadata():
    message = ConversationMessage(
        role=MessageRole.ASSISTANT,
        content="Redis is often used as a cache.",
    )

    assert message.metadata == {}


def test_message_roles_have_expected_values():
    assert MessageRole.SYSTEM == "system"
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
    assert MessageRole.TOOL == "tool"


def test_memory_adds_message():
    memory = InMemoryConversationMemory()

    message = ConversationMessage(
        role=MessageRole.USER,
        content="Hello",
    )

    memory.add_message(message)

    assert memory.messages() == [message]


def test_memory_adds_system_message():
    memory = InMemoryConversationMemory()

    memory.add_system_message(
        "You are a helpful assistant.",
        metadata={"type": "instruction"},
    )

    messages = memory.messages()

    assert len(messages) == 1
    assert messages[0].role == MessageRole.SYSTEM
    assert messages[0].content == "You are a helpful assistant."
    assert messages[0].metadata == {"type": "instruction"}


def test_memory_adds_user_message():
    memory = InMemoryConversationMemory()

    memory.add_user_message(
        "What is Redis?",
        metadata={"user_id": "123"},
    )

    messages = memory.messages()

    assert len(messages) == 1
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "What is Redis?"
    assert messages[0].metadata == {"user_id": "123"}


def test_memory_adds_assistant_message():
    memory = InMemoryConversationMemory()

    memory.add_assistant_message(
        "Redis is often used as a cache.",
        metadata={"request_id": "req-123"},
    )

    messages = memory.messages()

    assert len(messages) == 1
    assert messages[0].role == MessageRole.ASSISTANT
    assert messages[0].content == "Redis is often used as a cache."
    assert messages[0].metadata == {"request_id": "req-123"}


def test_memory_adds_tool_message():
    memory = InMemoryConversationMemory()

    memory.add_tool_message(
        '{"temperature": "18C"}',
        metadata={"tool_name": "get_weather"},
    )

    messages = memory.messages()

    assert len(messages) == 1
    assert messages[0].role == MessageRole.TOOL
    assert messages[0].content == '{"temperature": "18C"}'
    assert messages[0].metadata == {"tool_name": "get_weather"}


def test_memory_preserves_message_order():
    memory = InMemoryConversationMemory()

    memory.add_system_message("System instruction.")
    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi")

    messages = memory.messages()

    assert [message.role for message in messages] == [
        MessageRole.SYSTEM,
        MessageRole.USER,
        MessageRole.ASSISTANT,
    ]
    assert [message.content for message in messages] == [
        "System instruction.",
        "Hello",
        "Hi",
    ]


def test_memory_returns_recent_messages():
    memory = InMemoryConversationMemory()

    memory.add_user_message("First")
    memory.add_assistant_message("Second")
    memory.add_user_message("Third")

    recent = memory.recent_messages(limit=2)

    assert [message.content for message in recent] == [
        "Second",
        "Third",
    ]


def test_memory_recent_messages_returns_empty_list_for_zero_limit():
    memory = InMemoryConversationMemory()

    memory.add_user_message("Hello")

    assert memory.recent_messages(limit=0) == []


def test_memory_recent_messages_returns_empty_list_for_negative_limit():
    memory = InMemoryConversationMemory()

    memory.add_user_message("Hello")

    assert memory.recent_messages(limit=-1) == []


def test_memory_clear_removes_messages():
    memory = InMemoryConversationMemory()

    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi")

    memory.clear()

    assert memory.messages() == []


def test_memory_messages_returns_copy():
    memory = InMemoryConversationMemory()

    memory.add_user_message("Hello")

    messages = memory.messages()
    messages.clear()

    assert len(memory.messages()) == 1


def test_format_conversation_messages_formats_messages():
    messages = [
        ConversationMessage(
            role=MessageRole.USER,
            content="What is Redis?",
        ),
        ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="Redis is often used as a cache.",
        ),
    ]

    formatted = format_conversation_messages(messages)

    assert "USER:\nWhat is Redis?" in formatted
    assert "ASSISTANT:\nRedis is often used as a cache." in formatted


def test_format_conversation_messages_includes_metadata():
    messages = [
        ConversationMessage(
            role=MessageRole.TOOL,
            content='{"temperature": "18C"}',
            metadata={"tool_name": "get_weather"},
        )
    ]

    formatted = format_conversation_messages(messages)

    assert "TOOL:" in formatted
    assert '{"temperature": "18C"}' in formatted
    assert "Metadata: {'tool_name': 'get_weather'}" in formatted


def test_format_conversation_messages_returns_message_for_empty_list():
    formatted = format_conversation_messages([])

    assert formatted == "No previous conversation."
