from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator
from ai.tools import ToolDefinition, ToolResponse
from ai.exceptions import AIProviderError
from ai.schemas import ProviderResponse
from ai.images import ImageInput
from ai.embeddings import EmbeddingInput, EmbeddingResponse


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

    async def ask_text_async(self, prompt: str) -> ProviderResponse:
        """
        Send a prompt asynchronously.

        Providers that support async requests should override this method.
        """
        raise AIProviderError(
            f"Provider '{self.__class__.__name__}' does not support async requests. "
            "Implement ask_text_async() on the provider before using AsyncAIClient."
        )

    def stream_text(self, prompt: str) -> Iterator[str]:
        """
        Stream text chunks from the provider.

        Providers that support streaming should override this method.
        """
        raise AIProviderError(
            f"Provider '{self.__class__.__name__}' does not support streaming. "
            "Implement stream_text() on the provider before using AIClient.stream()."
        )

    async def stream_text_async(self, prompt: str) -> AsyncIterator[str]:
        """
        Stream text chunks asynchronously.

        Providers that support async streaming should override this method.
        """
        raise AIProviderError(
            f"Provider '{self.__class__.__name__}' does not support async streaming. "
            "Implement stream_text_async() on the provider before using async streaming."
        )

    def ask_with_tools(
        self,
        prompt: str,
        tools: list[ToolDefinition],
    ) -> ToolResponse:
        """
        Send a prompt with available tool definitions.

        Providers that support tool calling should override this method.
        """
        raise AIProviderError(
            f"Provider '{self.__class__.__name__}' does not support tool calling. "
            "Implement ask_with_tools() on the provider before using tools."
        )

    def ask_with_images(
        self,
        prompt: str,
        images: list[ImageInput],
    ) -> ProviderResponse:
        """
        Send a prompt with image inputs.

        Providers that support image input should override this method.
        """
        raise AIProviderError(
            f"Provider '{self.__class__.__name__}' does not support image inputs. "
            "Implement ask_with_images() on the provider before using image requests."
        )

    def embed_text(
        self,
        text: str,
        metadata: dict[str, str] | None = None,
    ) -> EmbeddingResponse:
        """
        Embed one text input.

        Providers can override this method, but by default it delegates to
        embed_texts() so providers only need to implement batch embedding once.
        """
        return self.embed_texts(
            [
                EmbeddingInput(
                    text=text,
                    metadata=metadata or {},
                )
            ]
        )

    def embed_texts(
        self,
        inputs: list[EmbeddingInput],
    ) -> EmbeddingResponse:
        """
        Embed multiple text inputs.

        Providers that support embeddings should override this method.
        """
        raise AIProviderError(
            f"Provider '{self.__class__.__name__}' does not support embeddings. "
            "Implement embed_texts() on the provider before using embedding requests."
        )
