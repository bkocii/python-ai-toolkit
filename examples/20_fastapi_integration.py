"""
Example usage inside an existing FastAPI project.

Required environment variables:

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini

Run with:

uvicorn examples.20_fastapi_integration:app --reload
"""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from ai.integrations.fastapi import AsyncAIClientDependency

app = FastAPI(
    title="AI Toolkit FastAPI Example",
)


class TicketRequest(BaseModel):
    message: str


class TicketAnalysis(BaseModel):
    category: Literal[
        "billing",
        "technical",
        "account",
        "other",
    ]
    priority: Literal[
        "low",
        "medium",
        "high",
    ]
    summary: str


@app.post(
    "/analyze-ticket",
    response_model=TicketAnalysis,
)
async def analyze_ticket(
    request: TicketRequest,
    client: AsyncAIClientDependency,
) -> TicketAnalysis:
    """
    Analyze a customer support ticket.

    FastAPI injects AsyncAIClient through AsyncAIClientDependency.
    """
    result = await client.ask(
        prompt=(
            "Analyze the following support ticket. "
            "Determine its category and priority, and return "
            "a short summary.\n\n"
            f"Ticket:\n{request.message}"
        ),
        response_type=TicketAnalysis,
    )

    return result.data
