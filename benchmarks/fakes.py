from ai.schemas import ProviderResponse, TokenUsage


class FakeTextProvider:
    """
    Deterministic synchronous provider for benchmarks.

    The provider performs no network calls, sleeping, logging,
    file access, or response generation.
    """

    def __init__(
        self,
        response_text: str = "Benchmark response",
        token_usage: TokenUsage | None = None,
    ):
        self.response = ProviderResponse(
            text=response_text,
            token_usage=token_usage,
        )

    def ask_text(self, _prompt: str) -> ProviderResponse:
        return self.response


class FakeAsyncTextProvider:
    """
    Deterministic asynchronous provider for benchmarks.
    """

    def __init__(
        self,
        response_text: str = "Benchmark response",
        token_usage: TokenUsage | None = None,
    ):
        self.response = ProviderResponse(
            text=response_text,
            token_usage=token_usage,
        )

    async def ask_text_async(
        self,
        _prompt: str,
    ) -> ProviderResponse:
        return self.response


class SequenceTextProvider:
    """
    Return predefined synchronous responses in order.

    This provider supports deterministic structured-response
    repair and retry benchmarks.
    """

    def __init__(
        self,
        responses: list[str],
        token_usage: TokenUsage | None = None,
    ):
        if not responses:
            raise ValueError("SequenceTextProvider requires at least one response.")

        self.responses = tuple(
            ProviderResponse(
                text=response,
                token_usage=token_usage,
            )
            for response in responses
        )
        self.call_count = 0

    def ask_text(self, _prompt: str) -> ProviderResponse:
        if self.call_count >= len(self.responses):
            raise RuntimeError("SequenceTextProvider has no remaining responses.")

        response = self.responses[self.call_count]
        self.call_count += 1

        return response
