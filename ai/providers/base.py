from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """
    Common interface for all AI providers.

    AIClient will talk to this interface, not directly to OpenAI.
    That makes it possible to add Anthropic, Google, Ollama, etc. later
    without rewriting application code.
    """

    @abstractmethod
    def ask_text(self, prompt: str) -> str:
        """Send a prompt and return a text response."""
        raise NotImplementedError
