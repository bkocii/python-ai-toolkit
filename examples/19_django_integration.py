"""
Example usage inside an existing Django project.

Django settings.py must contain:

AI_TOOLKIT = {
    "provider": "openai",
    "api_key": os.environ["OPENAI_API_KEY"],
    "model": "gpt-5.4-mini",
}
"""

from pydantic import BaseModel

from ai.integrations.django import get_ai_client


class TicketAnalysis(BaseModel):
    category: str
    priority: str
    summary: str


def analyze_support_ticket(message: str) -> TicketAnalysis:
    """
    Example Django service function.

    A Django view, Celery task, management command, or model service
    can call this function.
    """
    client = get_ai_client()

    result = client.ask(
        prompt=(
            "Analyze the following support ticket. "
            "Return its category, priority, and a short summary.\n\n"
            f"{message}"
        ),
        response_type=TicketAnalysis,
    )

    return result.data
