class AIError(Exception):
    """Base exception for all toolkit errors."""


class AIConfigurationError(AIError):
    """Raised when AI configuration is missing or invalid."""


class AIProviderError(AIError):
    """Raised when an AI provider request fails."""


class AIJSONParseError(AIError):
    """Raised when the AI response is not valid JSON."""


class AISchemaValidationError(AIError):
    """Raised when the AI response does not match the expected schema."""
