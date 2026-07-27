"""
Use structured AI output inside a framework-independent application service.

The service depends on AIClient rather than a provider SDK. It validates input,
owns the prompt and routing rules, converts expected toolkit failures into an
application error, and returns a stable application result.

Running this module normally requires valid text-generation provider
configuration. The automated regression substitutes a deterministic provider,
so verification needs no credential or network request.
"""

from typing import ClassVar, Literal

from pydantic import BaseModel, Field

from ai.client import AIClient
from ai.exceptions import AIError

FeedbackCategory = Literal["product", "billing", "delivery", "other"]
QueueName = Literal["product-team", "billing-team", "delivery-team", "general"]


class FeedbackAnalysis(BaseModel):
    category: FeedbackCategory
    sentiment: Literal["positive", "neutral", "negative"]
    urgency: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=200)


class FeedbackOutcome(BaseModel):
    analysis: FeedbackAnalysis
    queue: QueueName
    requires_human_review: bool
    request_id: str


class FeedbackServiceUnavailable(RuntimeError):
    """Raised when expected toolkit failures prevent feedback analysis."""


class CustomerFeedbackService:
    """Application-owned service that uses an injected toolkit client."""

    _QUEUES: ClassVar[dict[FeedbackCategory, QueueName]] = {
        "product": "product-team",
        "billing": "billing-team",
        "delivery": "delivery-team",
        "other": "general",
    }

    def __init__(self, client: AIClient):
        self.client = client

    def analyze(self, message: str) -> FeedbackOutcome:
        normalized_message = message.strip()

        if not 10 <= len(normalized_message) <= 2_000:
            raise ValueError("Feedback must contain between 10 and 2,000 characters.")

        prompt = (
            "Analyze this customer feedback for internal routing.\n"
            "Choose one category: product, billing, delivery, or other.\n"
            "Choose one sentiment: positive, neutral, or negative.\n"
            "Set urgency from 1 (low) to 5 (critical).\n"
            "Summarize the issue without making policy or refund decisions.\n\n"
            f"Feedback: {normalized_message}"
        )

        try:
            result = self.client.ask(
                prompt,
                response_type=FeedbackAnalysis,
            )
        except AIError as exc:
            raise FeedbackServiceUnavailable(
                "Customer feedback analysis is temporarily unavailable."
            ) from exc

        analysis = result.data
        requires_human_review = analysis.category == "billing" or analysis.urgency >= 4

        return FeedbackOutcome(
            analysis=analysis,
            queue=self._QUEUES[analysis.category],
            requires_human_review=requires_human_review,
            request_id=result.request_id,
        )


def main() -> None:
    service = CustomerFeedbackService(AIClient())
    outcome = service.analyze(
        "I was charged twice for my order and need someone to check it."
    )

    print(outcome.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
