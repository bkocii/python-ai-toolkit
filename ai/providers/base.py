from abc import ABC, abstractmethod
from ai.schemas import ProviderResponse


class BaseAIProvider(ABC):
    """
    Common interface for all AI providers.

    AIClient will talk to this interface, not directly to OpenAI.
    That makes it possible to add Anthropic, Google, Ollama, etc. later
    without rewriting application code.
    """

    @abstractmethod
    def ask_text(self, prompt: str) -> ProviderResponse:
        """Send a prompt and return a text response."""
        raise NotImplementedError
