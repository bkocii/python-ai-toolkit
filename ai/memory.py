from abc import ABC, abstractmethod
from enum import StrEnum
from time import time

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    """
    Supported conversation message roles.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ConversationMessage(BaseModel):
    """
    One message in a conversation.

    role:
        Who produced the message.

    content:
        Message text.

    metadata:
        Optional application-specific information such as tool name,
        request ID, source, user ID, or trace information.

    created_at:
        Unix timestamp for ordering and debugging.
    """

    role: MessageRole
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time)


class BaseConversationMemory(ABC):
    """
    Provider-independent conversation memory interface.
    """

    @abstractmethod
    def add_message(
        self,
        message: ConversationMessage,
    ) -> None:
        """
        Add one message to memory.
        """
        raise NotImplementedError

    @abstractmethod
    def messages(self) -> list[ConversationMessage]:
        """
        Return all messages in memory.
        """
        raise NotImplementedError

    @abstractmethod
    def recent_messages(
        self,
        limit: int,
    ) -> list[ConversationMessage]:
        """
        Return the most recent messages.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all messages from memory.
        """
        raise NotImplementedError


class InMemoryConversationMemory(BaseConversationMemory):
    """
    Simple in-memory conversation memory.

    Useful for tests, examples, demos, and short-lived agent workflows.
    """

    def __init__(self):
        self._messages: list[ConversationMessage] = []

    def add_message(
        self,
        message: ConversationMessage,
    ) -> None:
        """
        Add one message to memory.
        """
        self._messages.append(message)

    def add_system_message(
        self,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Add a system message.
        """
        self.add_message(
            ConversationMessage(
                role=MessageRole.SYSTEM,
                content=content,
                metadata=metadata or {},
            )
        )

    def add_user_message(
        self,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Add a user message.
        """
        self.add_message(
            ConversationMessage(
                role=MessageRole.USER,
                content=content,
                metadata=metadata or {},
            )
        )

    def add_assistant_message(
        self,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Add an assistant message.
        """
        self.add_message(
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content=content,
                metadata=metadata or {},
            )
        )

    def add_tool_message(
        self,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Add a tool message.
        """
        self.add_message(
            ConversationMessage(
                role=MessageRole.TOOL,
                content=content,
                metadata=metadata or {},
            )
        )

    def messages(self) -> list[ConversationMessage]:
        """
        Return all messages in memory.
        """
        return list(self._messages)

    def recent_messages(
        self,
        limit: int,
    ) -> list[ConversationMessage]:
        """
        Return the most recent messages.
        """
        if limit <= 0:
            return []

        return self._messages[-limit:]

    def clear(self) -> None:
        """
        Remove all messages from memory.
        """
        self._messages.clear()


def format_conversation_messages(
    messages: list[ConversationMessage],
) -> str:
    """
    Format conversation messages for use inside prompts.
    """
    if not messages:
        return "No previous conversation."

    formatted_messages = []

    for message in messages:
        metadata_text = f"\nMetadata: {message.metadata}" if message.metadata else ""

        formatted_messages.append(
            f"{message.role.value.upper()}:\n" f"{message.content}" f"{metadata_text}"
        )

    return "\n\n".join(formatted_messages)
