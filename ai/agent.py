from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from ai.memory import ConversationMessage
from ai.client import AIClient
from ai.memory import (
    BaseConversationMemory,
    InMemoryConversationMemory,
    format_conversation_messages,
)


class AgentResponse(BaseModel):
    """
    Response returned by an agent.

    output:
        Final assistant text.

    model:
        Model used by the underlying AI client.

    request_id:
        Request ID from the underlying AIResult.

    messages:
        Conversation messages after the agent run.
    """

    output: str
    model: str
    request_id: str
    messages: list[ConversationMessage] = Field(default_factory=list)


class BaseAgent(ABC):
    """
    Provider-independent agent interface.
    """

    @abstractmethod
    def run(
        self,
        message: str,
        metadata: dict[str, str] | None = None,
    ) -> AgentResponse:
        """
        Run the agent for one user message.
        """
        raise NotImplementedError


class Agent(BaseAgent):
    """
    Simple memory-backed AI agent.

    The agent stores the user message, builds a prompt using recent memory,
    asks the AI client, stores the assistant response, and returns an
    AgentResponse.
    """

    def __init__(
        self,
        ai_client: AIClient,
        instructions: str,
        memory: BaseConversationMemory | None = None,
        memory_limit: int = 10,
    ):
        if not instructions.strip():
            raise ValueError("Agent instructions cannot be empty.")

        if memory_limit <= 0:
            raise ValueError("Agent memory_limit must be greater than zero.")

        self.ai_client = ai_client
        self.instructions = instructions
        self.memory = memory or InMemoryConversationMemory()
        self.memory_limit = memory_limit

    def run(
        self,
        message: str,
        metadata: dict[str, str] | None = None,
    ) -> AgentResponse:
        """
        Run the agent for one user message.
        """
        if not message.strip():
            raise ValueError("Agent message cannot be empty.")

        self.memory.add_user_message(
            content=message,
            metadata=metadata or {},
        )

        conversation = format_conversation_messages(
            self.memory.recent_messages(self.memory_limit)
        )

        prompt = self._build_prompt(
            conversation=conversation,
            message=message,
        )

        result = self.ai_client.ask(prompt)

        self.memory.add_assistant_message(
            content=result.data,
            metadata={
                "request_id": result.request_id,
                "model": result.model,
            },
        )

        return AgentResponse(
            output=result.data,
            model=result.model,
            request_id=result.request_id,
            messages=self.memory.messages(),
        )

    def _build_prompt(
        self,
        conversation: str,
        message: str,
    ) -> str:
        """
        Build the prompt sent to the AI client.
        """
        return f"""
Instructions:
{self.instructions}

Conversation so far:
{conversation}

Current user message:
{message}

Respond as the assistant.
"""
