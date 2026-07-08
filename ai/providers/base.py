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
        """
        Send a prompt to the provider and return a ProviderResponse.

        Concrete implementations are responsible for translating
        toolkit requests into provider-specific SDK calls.
        """
        raise NotImplementedError
