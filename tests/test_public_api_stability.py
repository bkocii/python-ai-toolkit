import importlib
import inspect
import re
from dataclasses import fields
from pathlib import Path

from ai.agent import Agent, AgentResponse, BaseAgent
from ai.async_client import AsyncAIClient
from ai.client import AIClient
from ai.config import AIConfig, AILoggingConfig
from ai.documents import BaseDocumentLoader
from ai.embeddings import EmbeddingInput, EmbeddingResponse, EmbeddingVector
from ai.exceptions import (
    AIConfigurationError,
    AIError,
    AIJSONParseError,
    AIProviderError,
    AISchemaValidationError,
)
from ai.images import ImageInput, ImageInputType
from ai.memory import BaseConversationMemory, ConversationMessage, MessageRole
from ai.orchestrator import (
    AgentRunResult,
    MultiAgentOrchestrator,
    MultiAgentResponse,
)
from ai.providers.base import BaseAIProvider
from ai.rag import RAGResponse
from ai.retriever import BaseRetriever, RetrievedContext
from ai.schemas import AIResult, ProviderResponse, TokenUsage
from ai.tools import ToolCall, ToolDefinition, ToolResponse
from ai.vector_store import BaseVectorStore, VectorRecord, VectorSearchResult
from ai.workflow import (
    BaseWorkflowStep,
    WorkflowContext,
    WorkflowRunResult,
    WorkflowStepResult,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_REFERENCE_PATH = PROJECT_ROOT / "docs" / "api_reference.md"
REQUIRED = "<required>"

EXPECTED_PUBLIC_SURFACE = {
    "ai.client": ("AIClient",),
    "ai.async_client": ("AsyncAIClient",),
    "ai.config": (
        "AIConfig",
        "AILoggingConfig",
        "get_ai_config",
        "get_ai_logging_config",
    ),
    "ai.config_validator": ("ConfigValidator",),
    "ai.schemas": ("AIResult", "TokenUsage", "ProviderResponse"),
    "ai.request_builder": ("AIRequestBuilder",),
    "ai.prompts": ("PromptBuilder", "PromptTemplate"),
    "ai.tools": ("ToolDefinition", "ToolCall", "ToolResponse"),
    "ai.images": ("ImageInputType", "ImageInput"),
    "ai.embeddings": (
        "EmbeddingInput",
        "EmbeddingVector",
        "EmbeddingResponse",
    ),
    "ai.vector_store": (
        "VectorRecord",
        "VectorSearchResult",
        "BaseVectorStore",
        "InMemoryVectorStore",
    ),
    "ai.retriever": (
        "RetrievedContext",
        "BaseRetriever",
        "VectorStoreRetriever",
        "format_retrieved_context",
    ),
    "ai.rag": ("RAGResponse", "RAGPipeline", "build_rag_prompt"),
    "ai.documents": (
        "Document",
        "BaseDocumentLoader",
        "TextFileLoader",
        "MarkdownFileLoader",
        "DirectoryLoader",
        "documents_to_embedding_inputs",
    ),
    "ai.memory": (
        "MessageRole",
        "ConversationMessage",
        "BaseConversationMemory",
        "InMemoryConversationMemory",
        "format_conversation_messages",
    ),
    "ai.agent": ("AgentResponse", "BaseAgent", "Agent"),
    "ai.workflow": (
        "WorkflowContext",
        "WorkflowStepResult",
        "WorkflowRunResult",
        "BaseWorkflowStep",
        "FunctionWorkflowStep",
        "WorkflowEngine",
    ),
    "ai.orchestrator": (
        "AgentRunResult",
        "MultiAgentResponse",
        "MultiAgentOrchestrator",
    ),
    "ai.providers.base": ("BaseAIProvider",),
    "ai.providers.factory": ("ProviderFactory",),
    "ai.integrations.django": (
        "get_django_ai_config",
        "get_ai_client",
        "get_async_ai_client",
    ),
    "ai.integrations.fastapi": (
        "AIClientDependency",
        "AsyncAIClientDependency",
        "get_ai_client",
        "get_async_ai_client",
    ),
    "ai.exceptions": (
        "AIError",
        "AIConfigurationError",
        "AIProviderError",
        "AIJSONParseError",
        "AISchemaValidationError",
    ),
    "ai.parser": ("parse_json_response",),
    "ai.cost": ("estimate_cost_usd",),
}


def documented_public_surface() -> dict[str, tuple[str, ...]]:
    reference = API_REFERENCE_PATH.read_text(encoding="utf-8")
    surface_table = reference.split("## Surface index", 1)[1].split("\n## ", 1)[0]
    documented: dict[str, tuple[str, ...]] = {}

    for line in surface_table.splitlines():
        cells = line.split("|")

        if len(cells) < 5:
            continue

        modules = re.findall(r"`(ai(?:\.[a-z_]+)+)`", cells[2])
        symbols = re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", cells[3])

        if not modules:
            continue

        if len(modules) == 1:
            documented[modules[0]] = tuple(symbols)
            continue

        assert len(modules) == len(symbols)

        for module_name, symbol in zip(modules, symbols, strict=True):
            documented[module_name] = (symbol,)

    return documented


def parameter_contract(callable_object) -> tuple[tuple[str, object], ...]:
    parameters = inspect.signature(callable_object).parameters.values()

    return tuple(
        (
            parameter.name,
            (
                REQUIRED
                if parameter.default is inspect.Parameter.empty
                else parameter.default
            ),
        )
        for parameter in parameters
    )


def test_documented_public_surface_is_the_frozen_71_symbol_contract():
    documented = documented_public_surface()

    assert documented == EXPECTED_PUBLIC_SURFACE
    assert sum(len(symbols) for symbols in documented.values()) == 71


def test_every_frozen_public_symbol_is_importable():
    for module_name, symbols in EXPECTED_PUBLIC_SURFACE.items():
        module = importlib.import_module(module_name)

        for symbol in symbols:
            assert hasattr(module, symbol), f"Missing {module_name}.{symbol}"


def test_top_level_package_has_no_version_1_re_exports():
    package = importlib.import_module("ai")

    assert not hasattr(package, "__all__")

    for symbol in ("AIClient", "AsyncAIClient", "AIConfig", "AIResult"):
        assert not hasattr(package, symbol)


def test_core_constructor_and_method_parameter_contracts_are_stable():
    assert parameter_contract(AIClient) == (("config", None),)
    assert parameter_contract(AsyncAIClient) == (("config", None),)
    assert parameter_contract(AIClient.ask) == (
        ("self", REQUIRED),
        ("prompt", REQUIRED),
        ("response_type", None),
    )
    assert parameter_contract(AIClient.ask_with_images) == (
        ("self", REQUIRED),
        ("prompt", REQUIRED),
        ("images", REQUIRED),
        ("response_type", None),
    )
    assert parameter_contract(AIClient.embed_text) == (
        ("self", REQUIRED),
        ("text", REQUIRED),
        ("metadata", None),
    )
    assert parameter_contract(Agent) == (
        ("ai_client", REQUIRED),
        ("instructions", REQUIRED),
        ("memory", None),
        ("memory_limit", 10),
    )
    assert parameter_contract(MultiAgentOrchestrator) == (("agents", None),)
    assert parameter_contract(MultiAgentOrchestrator.run_sequence) == (
        ("self", REQUIRED),
        ("agent_names", REQUIRED),
        ("message", REQUIRED),
        ("metadata", None),
    )


def test_configuration_field_contracts_are_stable():
    assert tuple(field.name for field in fields(AIConfig)) == (
        "api_key",
        "model",
        "provider",
        "embedding_model",
        "embedding_dimensions",
        "input_cost_per_1m_tokens",
        "output_cost_per_1m_tokens",
        "max_retries",
        "log_level",
        "log_file_path",
        "file_logging_enabled",
    )
    assert tuple(field.name for field in fields(AILoggingConfig)) == (
        "level",
        "file_path",
        "file_logging_enabled",
    )
    assert AIConfig.__dataclass_params__.frozen is True
    assert AILoggingConfig.__dataclass_params__.frozen is True


def test_public_model_field_contracts_are_stable():
    expected_fields = {
        AIResult: (
            "data",
            "model",
            "raw_response",
            "original_raw_response",
            "duration_ms",
            "retries_used",
            "token_usage",
            "estimated_cost_usd",
            "request_id",
        ),
        TokenUsage: ("input_tokens", "output_tokens", "total_tokens"),
        ProviderResponse: ("text", "token_usage"),
        ToolDefinition: ("name", "description", "parameters"),
        ToolCall: ("name", "arguments", "call_id"),
        ToolResponse: ("text", "tool_calls"),
        ImageInput: ("source", "type", "detail"),
        EmbeddingInput: ("text", "metadata"),
        EmbeddingVector: ("text", "vector", "index", "metadata"),
        EmbeddingResponse: ("embeddings", "model", "token_usage"),
        VectorRecord: ("id", "text", "vector", "metadata"),
        VectorSearchResult: ("id", "text", "vector", "score", "metadata"),
        RetrievedContext: ("id", "text", "score", "metadata"),
        RAGResponse: ("answer", "contexts", "model", "request_id", "raw_response"),
        ConversationMessage: ("role", "content", "metadata", "created_at"),
        AgentResponse: ("output", "model", "request_id", "messages"),
        WorkflowContext: ("input", "state", "metadata"),
        WorkflowStepResult: (
            "step_name",
            "output",
            "state_updates",
            "metadata",
            "success",
            "error",
        ),
        WorkflowRunResult: ("success", "context", "steps"),
        AgentRunResult: ("agent_name", "response", "success", "error"),
        MultiAgentResponse: ("results",),
    }

    for model, field_names in expected_fields.items():
        assert tuple(model.model_fields) == field_names


def test_public_enums_and_exception_hierarchy_are_stable():
    assert tuple(role.value for role in MessageRole) == (
        "system",
        "user",
        "assistant",
        "tool",
    )
    assert tuple(input_type.value for input_type in ImageInputType) == (
        "url",
        "base64",
    )

    assert issubclass(AIConfigurationError, AIError)
    assert issubclass(AIProviderError, AIError)
    assert issubclass(AIJSONParseError, AIError)
    assert issubclass(AISchemaValidationError, AIError)


def test_extension_interfaces_keep_their_required_abstract_methods():
    assert BaseAIProvider.__abstractmethods__ == {"ask_text"}
    assert BaseDocumentLoader.__abstractmethods__ == {"load"}
    assert BaseVectorStore.__abstractmethods__ == {
        "add",
        "similarity_search",
        "count",
        "clear",
    }
    assert BaseRetriever.__abstractmethods__ == {"retrieve"}
    assert BaseConversationMemory.__abstractmethods__ == {
        "add_message",
        "messages",
        "recent_messages",
        "clear",
    }
    assert BaseAgent.__abstractmethods__ == {"run"}
    assert BaseWorkflowStep.__abstractmethods__ == {"run"}


def test_freeze_records_the_approved_version_1_behavior():
    reference = API_REFERENCE_PATH.read_text(encoding="utf-8")

    for contract in (
        "Both clients validate it automatically",
        "Include the current user message once",
        "Validate every requested agent name before execution",
        "success requires at least one result",
    ):
        assert contract in reference
