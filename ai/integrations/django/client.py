from ai.async_client import AsyncAIClient
from ai.client import AIClient
from ai.integrations.django.config import (
    DEFAULT_DJANGO_SETTING_NAME,
    get_django_ai_config,
)


def get_ai_client(
    setting_name: str = DEFAULT_DJANGO_SETTING_NAME,
) -> AIClient:
    """
    Create a synchronous AIClient from Django settings.
    """
    config = get_django_ai_config(setting_name)

    return AIClient(config=config)


def get_async_ai_client(
    setting_name: str = DEFAULT_DJANGO_SETTING_NAME,
) -> AsyncAIClient:
    """
    Create an AsyncAIClient from Django settings.
    """
    config = get_django_ai_config(setting_name)

    return AsyncAIClient(config=config)
