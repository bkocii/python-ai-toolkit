import importlib
import inspect
from dataclasses import fields

import ai
from ai.agent import Agent, AgentResponse, BaseAgent
from ai.async_client import AsyncAIClient
from ai.client import AIClient
from ai.config import AIConfig, AILoggingConfig
from ai.embeddings import EmbeddingInput, EmbeddingResponse, EmbeddingVector
from ai.exceptions import (
    AIConfigurationError,
    AIError,
    AIJSONParseError,
    AIProviderError,
    AISchemaValidationError,
)
from ai.images import ImageInput, ImageInputType
from ai.memory import (
    BaseConversationMemory,
    ConversationMessage,
    InMemoryConversationMemory,
    MessageRole,
)
from ai.orchestrator import AgentRunResult, MultiAgentOrchestrator, MultiAgentResponse
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.rag import RAGPipeline, RAGResponse
from ai.request_builder import AIRequestBuilder
from ai.retriever import BaseRetriever, RetrievedContext, VectorStoreRetriever
from ai.schemas import AIResult, ProviderResponse, TokenUsage
from ai.tools import ToolCall, ToolDefinition, ToolResponse
from ai.vector_store import (
    BaseVectorStore,
    VectorRecord,
    VectorSearchResult,
)
from ai.workflow import (
    BaseWorkflowStep,
    FunctionWorkflowStep,
    WorkflowContext,
    WorkflowEngine,
    WorkflowRunResult,
    WorkflowStepResult,
)

PUBLIC_SYMBOLS = {
    "ai.client": {"AIClient"},
    "ai.async_client": {"AsyncAIClient"},
    "ai.config": {
        "AIConfig",
        "AILoggingConfig",
        "get_ai_config",
        "get_ai_logging_config",
    },
    "ai.config_validator": {"ConfigValidator"},
    "ai.schemas": {"AIResult", "TokenUsage", "ProviderResponse"},
    "ai.request_builder": {"AIRequestBuilder"},
    "ai.prompts": {"PromptBuilder", "PromptTemplate"},
    "ai.tools": {"ToolDefinition", "ToolCall", "ToolResponse"},
    "ai.images": {"ImageInputType", "ImageInput"},
    "ai.embeddings": {"EmbeddingInput", "EmbeddingVector", "EmbeddingResponse"},
    "ai.vector_store": {
        "VectorRecord",
        "VectorSearchResult",
        "BaseVectorStore",
        "InMemoryVectorStore",
    },
    "ai.retriever": {
        "RetrievedContext",
        "BaseRetriever",
        "VectorStoreRetriever",
        "format_retrieved_context",
    },
    "ai.rag": {"RAGResponse", "RAGPipeline", "build_rag_prompt"},
    "ai.documents": {
        "Document",
        "BaseDocumentLoader",
        "TextFileLoader",
        "MarkdownFileLoader",
        "DirectoryLoader",
        "documents_to_embedding_inputs",
    },
    "ai.memory": {
        "MessageRole",
        "ConversationMessage",
        "BaseConversationMemory",
        "InMemoryConversationMemory",
        "format_conversation_messages",
    },
    "ai.agent": {"AgentResponse", "BaseAgent", "Agent"},
    "ai.workflow": {
        "WorkflowContext",
        "WorkflowStepResult",
        "WorkflowRunResult",
        "BaseWorkflowStep",
        "FunctionWorkflowStep",
        "WorkflowEngine",
    },
    "ai.orchestrator": {
        "AgentRunResult",
        "MultiAgentResponse",
        "MultiAgentOrchestrator",
    },
    "ai.providers.base": {"BaseAIProvider"},
    "ai.providers.factory": {"ProviderFactory"},
    "ai.integrations.django": {
        "get_django_ai_config",
        "get_ai_client",
        "get_async_ai_client",
    },
    "ai.integrations.fastapi": {
        "AIClientDependency",
        "AsyncAIClientDependency",
        "get_ai_client",
        "get_async_ai_client",
    },
    "ai.exceptions": {
        "AIError",
        "AIConfigurationError",
        "AIProviderError",
        "AIJSONParseError",
        "AISchemaValidationError",
    },
    "ai.parser": {"parse_json_response"},
    "ai.cost": {"estimate_cost_usd"},
}

CALL_PARAMETERS = {
    AIClient: ("config",),
    AIClient.ask: ("self", "prompt", "response_type"),
    AIClient.ask_text: ("self", "prompt"),
    AIClient.request: ("self",),
    AIClient.stream: ("self", "prompt"),
    AIClient.ask_with_tools: ("self", "prompt", "tools"),
    AIClient.ask_with_images: ("self", "prompt", "images", "response_type"),
    AIClient.embed_text: ("self", "text", "metadata"),
    AIClient.embed_texts: ("self", "inputs"),
    AsyncAIClient: ("config",),
    AsyncAIClient.ask: ("self", "prompt", "response_type"),
    AsyncAIClient.ask_text: ("self", "prompt"),
    AIRequestBuilder.prompt: ("self", "text"),
    AIRequestBuilder.response_type: ("self", "response_type"),
    AIRequestBuilder.execute: ("self",),
    BaseAIProvider.ask_text: ("self", "prompt"),
    BaseAIProvider.ask_text_async: ("self", "prompt"),
    BaseAIProvider.stream_text: ("self", "prompt"),
    BaseAIProvider.stream_text_async: ("self", "prompt"),
    BaseAIProvider.ask_with_tools: ("self", "prompt", "tools"),
    BaseAIProvider.ask_with_images: ("self", "prompt", "images"),
    BaseAIProvider.embed_text: ("self", "text", "metadata"),
    BaseAIProvider.embed_texts: ("self", "inputs"),
    ProviderFactory.create: ("config",),
    ProviderFactory.register: ("name", "provider_class"),
    ProviderFactory.available_providers: (),
    BaseVectorStore.add: ("self", "records"),
    BaseVectorStore.similarity_search: (
        "self",
        "query_vector",
        "limit",
        "metadata_filter",
    ),
    BaseVectorStore.count: ("self",),
    BaseVectorStore.clear: ("self",),
    VectorStoreRetriever: ("ai_client", "vector_store"),
    VectorStoreRetriever.retrieve: ("self", "query", "limit", "metadata_filter"),
    RAGPipeline: ("ai_client", "retriever"),
    RAGPipeline.ask: (
        "self",
        "question",
        "limit",
        "metadata_filter",
        "instructions",
    ),
    BaseConversationMemory.add_message: ("self", "message"),
    BaseConversationMemory.messages: ("self",),
    BaseConversationMemory.recent_messages: ("self", "limit"),
    BaseConversationMemory.clear: ("self",),
    InMemoryConversationMemory.add_system_message: ("self", "content", "metadata"),
    InMemoryConversationMemory.add_user_message: ("self", "content", "metadata"),
    InMemoryConversationMemory.add_assistant_message: (
        "self",
        "content",
        "metadata",
    ),
    InMemoryConversationMemory.add_tool_message: ("self", "content", "metadata"),
    Agent: ("ai_client", "instructions", "memory", "memory_limit"),
    BaseAgent.run: ("self", "message", "metadata"),
    Agent.run: ("self", "message", "metadata"),
    FunctionWorkflowStep: ("name", "function"),
    BaseWorkflowStep.run: ("self", "context"),
    WorkflowEngine: ("steps",),
    WorkflowEngine.run: ("self", "input_data", "metadata"),
    MultiAgentOrchestrator: ("agents",),
    MultiAgentOrchestrator.register_agent: ("self", "name", "agent"),
    MultiAgentOrchestrator.agent_names: ("self",),
    MultiAgentOrchestrator.run_agent: (
        "self",
        "agent_name",
        "message",
        "metadata",
    ),
    MultiAgentOrchestrator.run_sequence: (
        "self",
        "agent_names",
        "message",
        "metadata",
    ),
}

PYDANTIC_FIELDS = {
    TokenUsage: ("input_tokens", "output_tokens", "total_tokens"),
    ProviderResponse: ("text", "token_usage"),
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


def test_documented_public_symbols_are_importable():
    for module_name, symbol_names in PUBLIC_SYMBOLS.items():
        module = importlib.import_module(module_name)

        for symbol_name in symbol_names:
            assert hasattr(module, symbol_name), f"{module_name}.{symbol_name}"


def test_top_level_package_does_not_create_an_accidental_public_surface():
    assert not hasattr(ai, "__all__")

    for symbol_name in ("AIClient", "AsyncAIClient", "AIConfig", "AIResult"):
        assert not hasattr(ai, symbol_name)


def test_public_callable_parameter_names_are_frozen():
    for callable_object, expected_names in CALL_PARAMETERS.items():
        actual_names = tuple(inspect.signature(callable_object).parameters)

        assert actual_names == expected_names, callable_object


def test_public_callables_keep_return_annotations():
    for callable_object in CALL_PARAMETERS:
        if inspect.isclass(callable_object):
            continue

        assert (
            inspect.signature(callable_object).return_annotation
            is not inspect.Signature.empty
        ), callable_object


def test_public_dataclass_fields_are_frozen():
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


def test_public_pydantic_model_fields_are_frozen():
    for model, expected_names in PYDANTIC_FIELDS.items():
        assert tuple(model.model_fields) == expected_names, model


def test_public_enums_are_frozen():
    assert {member.name: member.value for member in ImageInputType} == {
        "URL": "url",
        "BASE64": "base64",
    }
    assert {member.name: member.value for member in MessageRole} == {
        "SYSTEM": "system",
        "USER": "user",
        "ASSISTANT": "assistant",
        "TOOL": "tool",
    }


def test_extension_interfaces_keep_their_required_abstract_methods():
    assert BaseAIProvider.__abstractmethods__ == {"ask_text"}
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


def test_public_exception_hierarchy_is_frozen():
    assert AIError.__bases__ == (Exception,)

    for exception_type in {
        AIConfigurationError,
        AIProviderError,
        AIJSONParseError,
        AISchemaValidationError,
    }:
        assert exception_type.__bases__ == (AIError,)
