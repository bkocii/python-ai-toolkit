# Public API Reference

This reference defines the approved Version 1.0 Python and command-line surface
of Python AI Toolkit. Package metadata is `1.0.0`; tagging and publication
remain separate release tasks and do not change the frozen contract recorded
here.

Only the modules, symbols, signatures, models, enum values, exceptions, and
behaviors documented below are compatibility promises. Importable names that
are not listed remain implementation details.

## Version 1.0 stability policy

- Patch releases may fix defects without intentionally breaking this surface.
- Minor releases may add backward-compatible symbols, methods, fields, or
  capabilities.
- Removing or incompatibly changing a documented contract requires a
  deprecation path when practical and a new major version.
- Exact provider SDK calls, private attributes, internal executors, prompt
  formatting, logs, and undocumented import paths are not compatibility
  promises.
- A provider registration confirms construction only; it does not promise that
  every model supports every optional capability.

## Import contract

`ai.__init__` currently provides no top-level re-exports. Use the documented
module paths:

```python
from ai.client import AIClient
from ai.config import AIConfig
from ai.schemas import AIResult
```

The top-level package intentionally provides no re-exports. Imports such as
`from ai import AIClient` are not part of Version 1.0. Keeping the documented
module paths avoids a second, much larger namespace that must remain stable.

## Surface index

| Area | Supported module | Public symbols |
| --- | --- | --- |
| Synchronous client | `ai.client` | `AIClient` |
| Asynchronous client | `ai.async_client` | `AsyncAIClient` |
| Configuration | `ai.config` | `AIConfig`, `AILoggingConfig`, `get_ai_config`, `get_ai_logging_config` |
| Validation | `ai.config_validator` | `ConfigValidator` |
| Results | `ai.schemas` | `AIResult`, `TokenUsage`, `ProviderResponse` |
| Request building | `ai.request_builder` | `AIRequestBuilder` |
| Prompt helpers | `ai.prompts` | `PromptBuilder`, `PromptTemplate` |
| Tools | `ai.tools` | `ToolDefinition`, `ToolCall`, `ToolResponse` |
| Images | `ai.images` | `ImageInputType`, `ImageInput` |
| Embeddings | `ai.embeddings` | `EmbeddingInput`, `EmbeddingVector`, `EmbeddingResponse` |
| Vector stores | `ai.vector_store` | `VectorRecord`, `VectorSearchResult`, `BaseVectorStore`, `InMemoryVectorStore` |
| Retrieval | `ai.retriever` | `RetrievedContext`, `BaseRetriever`, `VectorStoreRetriever`, `format_retrieved_context` |
| RAG | `ai.rag` | `RAGResponse`, `RAGPipeline`, `build_rag_prompt` |
| Documents | `ai.documents` | `Document`, `BaseDocumentLoader`, `TextFileLoader`, `MarkdownFileLoader`, `DirectoryLoader`, `documents_to_embedding_inputs` |
| Memory | `ai.memory` | `MessageRole`, `ConversationMessage`, `BaseConversationMemory`, `InMemoryConversationMemory`, `format_conversation_messages` |
| Agents | `ai.agent` | `AgentResponse`, `BaseAgent`, `Agent` |
| Workflows | `ai.workflow` | `WorkflowContext`, `WorkflowStepResult`, `WorkflowRunResult`, `BaseWorkflowStep`, `FunctionWorkflowStep`, `WorkflowEngine` |
| Multi-agent orchestration | `ai.orchestrator` | `AgentRunResult`, `MultiAgentResponse`, `MultiAgentOrchestrator` |
| Provider extensions | `ai.providers.base`, `ai.providers.factory` | `BaseAIProvider`, `ProviderFactory` |
| Django | `ai.integrations.django` | `get_django_ai_config`, `get_ai_client`, `get_async_ai_client` |
| FastAPI | `ai.integrations.fastapi` | `AIClientDependency`, `AsyncAIClientDependency`, `get_ai_client`, `get_async_ai_client` |
| Exceptions | `ai.exceptions` | `AIError`, `AIConfigurationError`, `AIProviderError`, `AIJSONParseError`, `AISchemaValidationError` |
| Low-level parsing | `ai.parser` | `parse_json_response` |
| Cost compatibility | `ai.cost` | `estimate_cost_usd` |
| Command line | `ai-toolkit` | `ask`, `config show`, `config validate` |

Pydantic model constructors below are keyword-only. Their normal Pydantic
validation errors are not automatically converted into toolkit exceptions.

## Clients

### `AIClient`

Import:

```python
from ai.client import AIClient
```

Constructor:

```text
AIClient(config: AIConfig | None = None)
```

If `config` is omitted, the client calls `get_ai_config()`. If it is supplied,
the client uses it instead of merging with environment configuration. The
client structurally validates both paths before provider, logger, or executor
construction. Applications may call `ConfigValidator.validate(config)` earlier
when they want a separate startup check.

Client construction creates a provider and configures toolkit logging. The
public lifecycle does not define `close()`, context-manager, or application-wide
singleton behavior. The visible `provider` and `executor` attributes are
implementation exposure, not supported extension points.

Methods:

| Signature | Return | Contract |
| --- | --- | --- |
| `ask(prompt, response_type=None)` | `AIResult[str]` or `AIResult[T]` | Plain request, or structured Pydantic response when `response_type` is supplied |
| `ask_text(prompt)` | `str` | Returns only `ask(prompt).data` |
| `request()` | `AIRequestBuilder` | Creates a new mutable request builder |
| `stream(prompt)` | `Iterator[str]` | Synchronous plain-text chunks; no `AIResult` metadata |
| `ask_with_tools(prompt, tools)` | `ToolResponse` | Returns requested calls; never executes tools |
| `ask_with_images(prompt, images, response_type=None)` | `AIResult[str]` or `AIResult[T]` | URL or Base64 data-URL images; optional structured response |
| `embed_text(text, metadata=None)` | `EmbeddingResponse` | One embedding wrapped in a batch response |
| `embed_texts(inputs)` | `EmbeddingResponse` | Accepts `list[str]` or `list[EmbeddingInput]` |

Request methods can raise `AIProviderError`. Structured request methods can
also raise `AIJSONParseError` or `AISchemaValidationError` after configured
repair attempts are exhausted. Unexpected provider or application exceptions
are not universally wrapped.

### `AsyncAIClient`

Import:

```python
from ai.async_client import AsyncAIClient
```

Constructor:

```text
AsyncAIClient(config: AIConfig | None = None)
```

Methods:

| Signature | Return | Contract |
| --- | --- | --- |
| `await ask(prompt, response_type=None)` | `AIResult[str]` or `AIResult[T]` | Async plain or structured request |
| `await ask_text(prompt)` | `str` | Async data-only shortcut |

The current async client does not expose streaming, tools, images, embeddings,
retrieval, RAG, agents, workflows, or orchestration. It has the same automatic
configuration validation boundary and no public close/context-manager
lifecycle.

## Configuration

### `AIConfig`

Import:

```python
from ai.config import AIConfig
```

Frozen dataclass fields:

| Field | Type | Default |
| --- | --- | --- |
| `api_key` | `str` | required |
| `model` | `str` | `"gpt-5.4-mini"` |
| `provider` | `str` | `"openai"` |
| `embedding_model` | `str` | `"text-embedding-3-small"` |
| `embedding_dimensions` | `int \| None` | `None` |
| `input_cost_per_1m_tokens` | `str \| None` | `None` |
| `output_cost_per_1m_tokens` | `str \| None` | `None` |
| `max_retries` | `int` | `1` |
| `log_level` | `str` | `"INFO"` |
| `log_file_path` | `str` | `"logs/ai_toolkit.log"` |
| `file_logging_enabled` | `bool` | `True` |

`max_retries` controls structured-response repair requests after the initial
request. It is not a network, rate-limit, or authentication retry policy.

### `AILoggingConfig`

Frozen dataclass:

```text
AILoggingConfig(
    level: str = "INFO",
    file_path: str = "logs/ai_toolkit.log",
    file_logging_enabled: bool = True,
)
```

### Configuration functions

```text
get_ai_config() -> AIConfig
get_ai_logging_config() -> AILoggingConfig
ConfigValidator.validate(config: AIConfig) -> None
ConfigValidator.validate_logging(config: AILoggingConfig) -> None
```

Environment-based resolvers and both client constructors validate configuration
and raise `AIConfigurationError` for invalid or missing values. Calling
`ConfigValidator` directly remains useful when an application wants to check a
configuration before client construction. The validators perform structural
checks only; they do not verify credentials, models, accounts, regions, quotas,
networks, or provider capabilities.

## Result models

### `AIResult[T]`

Keyword-only Pydantic fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `data` | `T` | Plain text or validated Pydantic model |
| `model` | `str` | Configured generation model |
| `raw_response` | `str` | Final accepted provider text |
| `original_raw_response` | `str \| None` | First invalid response when repair occurred |
| `duration_ms` | `float \| None` | Toolkit request duration |
| `retries_used` | `int` | Structured repair requests used |
| `token_usage` | `TokenUsage \| None` | Provider-reported usage |
| `estimated_cost_usd` | `Decimal \| None` | Estimate when usage and pricing are available |
| `request_id` | `str` | Toolkit-generated request identifier |

Streaming, tool calling, and embedding methods do not return `AIResult`.

### `TokenUsage`

Fields:

```text
input_tokens: int | None = None
output_tokens: int | None = None
total_tokens: int | None = None
```

`add(other: TokenUsage | None) -> TokenUsage` returns a new aggregate. Missing
numeric values contribute zero during aggregation.

### `ProviderResponse`

Provider-extension model:

```text
ProviderResponse(
    *,
    text: str,
    token_usage: TokenUsage | None = None,
)
```

Applications normally receive `AIResult`; custom provider implementations
return `ProviderResponse` to the request executor.

## Request and prompt utilities

### `AIRequestBuilder`

Obtain a builder through `AIClient.request()`:

```text
prompt(text: str) -> AIRequestBuilder
response_type(response_type: type[T]) -> AIRequestBuilder[T]
execute() -> AIResult[str] | AIResult[T]
```

The builder is mutable and reusable state is not guaranteed. `execute()` raises
`ValueError` when no prompt has been set, and otherwise propagates the same
request exceptions as `AIClient.ask()`. Applications obtain it through
`AIClient.request()`. The constructor's executor parameter is internal wiring,
not a supported direct-construction contract.

### `PromptBuilder`

```text
PromptBuilder()
add(title: str, content: str) -> PromptBuilder
build() -> str
```

`add()` mutates the builder and strips the title and content. `build()` joins
sections in insertion order.

### `PromptTemplate`

```text
PromptTemplate(template: str)
render(**values: object) -> str
```

Construction raises `ValueError` for an empty template. `render()` uses Python
format-string substitution and raises `ValueError` when a required key is
missing. Other format-string errors remain ordinary Python exceptions.

### `parse_json_response`

```text
parse_json_response(raw_response: str, response_type: type[T]) -> T
```

This low-level helper strictly parses JSON and validates it with a Pydantic
model. It raises `AIJSONParseError` for invalid JSON and
`AISchemaValidationError` for a schema mismatch. It performs no provider
request or repair attempt.

### `estimate_cost_usd`

```text
estimate_cost_usd(
    model: str,
    token_usage: TokenUsage | None,
) -> Decimal | None
```

This compatibility helper resolves pricing through environment configuration.
Request execution uses pre-resolved internal pricing instead. It can therefore
raise `AIConfigurationError` while loading configuration; it returns `None`
when usage or pricing is unavailable.

## Tools and images

### Tool models

```text
ToolDefinition(*, name: str, description: str, parameters: dict[str, Any] = {})
ToolCall(*, name: str, arguments: dict[str, Any], call_id: str | None = None)
ToolResponse(*, text: str | None = None, tool_calls: list[ToolCall] = [])
```

`ToolDefinition.parameters` is a provider-independent JSON-schema-shaped
mapping. The model may return text, tool calls, both, or neither. Applications
own allow-listing, argument validation, authorization, execution, side effects,
and any follow-up request.

### Image models

`ImageInputType` values:

| Member | Value |
| --- | --- |
| `URL` | `"url"` |
| `BASE64` | `"base64"` |

`ImageInput`:

```text
ImageInput(
    *,
    source: str,
    type: ImageInputType = ImageInputType.URL,
    detail: str | None = None,
)
```

`source` is an ordinary URL or a complete Base64 data URL. The selected
provider/model must support the input and requested detail value. If a
structured image response needs repair, the repair request contains text only;
the image is not resent.

## Embeddings, vectors, retrieval, and RAG

### Embedding models

```text
EmbeddingInput(*, text: str, metadata: dict[str, str] = {})
EmbeddingVector(
    *,
    text: str,
    vector: list[float],
    index: int,
    metadata: dict[str, str] = {},
)
EmbeddingResponse(
    *,
    embeddings: list[EmbeddingVector],
    model: str,
    token_usage: TokenUsage | None = None,
)
```

`EmbeddingResponse.vectors` returns the raw vectors. `.texts` returns the
corresponding input texts. Correlate a batch by `EmbeddingVector.index`, not by
assuming provider result order. `EmbeddingResponse` is not `AIResult`.

### Vector stores

Models:

```text
VectorRecord(
    *,
    id: str,
    text: str,
    vector: list[float],
    metadata: dict[str, str] = {},
)
VectorSearchResult(
    *,
    id: str,
    text: str,
    vector: list[float],
    score: float,
    metadata: dict[str, str] = {},
)
```

Extension interface:

```text
BaseVectorStore.add(records: list[VectorRecord]) -> None
BaseVectorStore.similarity_search(
    query_vector: list[float],
    limit: int = 5,
    metadata_filter: dict[str, str] | None = None,
) -> list[VectorSearchResult]
BaseVectorStore.count() -> int
BaseVectorStore.clear() -> None
```

`InMemoryVectorStore` implements this interface. It stores records by ID,
replaces duplicate IDs, applies exact metadata equality, ranks with cosine
similarity, and returns an empty list when `limit <= 0`. It raises `ValueError`
for vector dimension mismatches. It is volatile, mutable, linear-scan, and not
documented as thread-safe or durable. Similarity scores are ranking signals,
not confidence probabilities.

### Retrievers

```text
RetrievedContext(
    *,
    id: str,
    text: str,
    score: float,
    metadata: dict[str, str] = {},
)
BaseRetriever.retrieve(
    query: str,
    limit: int = 5,
    metadata_filter: dict[str, str] | None = None,
) -> list[RetrievedContext]
VectorStoreRetriever(ai_client: AIClient, vector_store: BaseVectorStore)
VectorStoreRetriever.retrieve(...) -> list[RetrievedContext]
format_retrieved_context(contexts: list[RetrievedContext]) -> str
```

`VectorStoreRetriever` embeds the query and searches the supplied store. It
raises `ValueError` for a blank query and propagates embedding/store failures.
The formatting helper returns `"No relevant context found."` for an empty list.

### RAG

```text
RAGPipeline(ai_client: AIClient, retriever: BaseRetriever)
RAGPipeline.ask(
    question: str,
    limit: int = 5,
    metadata_filter: dict[str, str] | None = None,
    instructions: str | None = None,
) -> RAGResponse
build_rag_prompt(
    question: str,
    context_text: str,
    instructions: str | None = None,
) -> str
```

`RAGResponse` fields:

```text
answer: str
contexts: list[RetrievedContext]
model: str
request_id: str
raw_response: str
```

`ask()` raises `ValueError` for a blank question and propagates retriever and
client failures. It is synchronous and plain-text only. `RAGResponse` omits
duration, retries, token usage, cost, and original raw response from the
underlying `AIResult`. Returned contexts support traceability but are not
verified sentence-level citations, and prompt grounding is not a factual
guarantee.

## Documents

Models and extension interface:

```text
Document(*, text: str, metadata: dict[str, str] = {})
BaseDocumentLoader.load() -> list[Document]
```

Loaders:

```text
TextFileLoader(path: str | Path, encoding: str = "utf-8")
MarkdownFileLoader(path: str | Path, encoding: str = "utf-8")
DirectoryLoader(
    path: str | Path,
    recursive: bool = False,
    encoding: str = "utf-8",
    extensions: set[str] | None = None,
)
```

Each loader exposes `load() -> list[Document]`. Missing paths raise
`FileNotFoundError`; wrong path kinds raise `ValueError`; decoding and other
file failures remain ordinary Python exceptions. Empty files return no
document. `DirectoryLoader` defaults to `.txt` and `.md` files and returns
results in sorted path order.

```text
documents_to_embedding_inputs(
    documents: list[Document],
) -> list[EmbeddingInput]
```

Loaders read whole files. They do not chunk, embed, index, watch, or persist
documents.

## Memory and agents

### Conversation memory

`MessageRole` values are `system`, `user`, `assistant`, and `tool`.

```text
ConversationMessage(
    *,
    role: MessageRole,
    content: str,
    metadata: dict[str, str] = {},
    created_at: float = <current Unix time>,
)
```

Extension interface:

```text
BaseConversationMemory.add_message(message) -> None
BaseConversationMemory.messages() -> list[ConversationMessage]
BaseConversationMemory.recent_messages(limit: int) -> list[ConversationMessage]
BaseConversationMemory.clear() -> None
```

`InMemoryConversationMemory` implements the interface and also exposes
`add_system_message`, `add_user_message`, `add_assistant_message`, and
`add_tool_message`, each accepting `content` and optional string metadata.
Returned message lists are shallow copies. `recent_messages(limit)` returns an
empty list for non-positive limits.

```text
format_conversation_messages(
    messages: list[ConversationMessage],
) -> str
```

The helper returns `"No previous conversation."` for an empty list.

### Agents

```text
AgentResponse(
    *,
    output: str,
    model: str,
    request_id: str,
    messages: list[ConversationMessage] = [],
)
BaseAgent.run(
    message: str,
    metadata: dict[str, str] | None = None,
) -> AgentResponse
Agent(
    ai_client: AIClient,
    instructions: str,
    memory: BaseConversationMemory | None = None,
    memory_limit: int = 10,
)
Agent.run(...) -> AgentResponse
```

`Agent` raises `ValueError` for blank instructions, a non-positive
`memory_limit`, or a blank message. The limit counts messages, not turns or
tokens, and includes the current message. The current message is stored before
the request and appears only in the prompt's dedicated current-message
section; at most `memory_limit - 1` earlier messages appear in the conversation
section. If the client request fails, the user message remains in memory; no
rollback occurs. The agent is synchronous, text-only, and not an autonomous
tool runner.

## Workflows and multi-agent orchestration

### Workflow models

```text
WorkflowContext(
    *,
    input: dict[str, Any] = {},
    state: dict[str, Any] = {},
    metadata: dict[str, str] = {},
)
WorkflowStepResult(
    *,
    step_name: str,
    output: Any = None,
    state_updates: dict[str, Any] = {},
    metadata: dict[str, str] = {},
    success: bool = True,
    error: str | None = None,
)
WorkflowRunResult(
    *,
    success: bool,
    context: WorkflowContext,
    steps: list[WorkflowStepResult] = [],
)
```

`WorkflowRunResult.final_output` is the last executed step's output, including
a failed step's output, or `None` when no step ran.

Extension and engine:

```text
BaseWorkflowStep.name: str
BaseWorkflowStep.run(context: WorkflowContext) -> WorkflowStepResult
FunctionWorkflowStep(
    name: str,
    function: Callable[[WorkflowContext], WorkflowStepResult],
)
WorkflowEngine(steps: list[BaseWorkflowStep])
WorkflowEngine.run(
    input_data: dict[str, Any] | None = None,
    metadata: dict[str, str] | None = None,
) -> WorkflowRunResult
```

Blank step names and empty workflows raise `ValueError`. The engine runs steps
sequentially, converts step exceptions into failed results, applies shallow
`state_updates` even from a failed step, and stops on failure. It does not roll
back state or external side effects.

### Multi-agent models and orchestrator

```text
AgentRunResult(
    *,
    agent_name: str,
    response: AgentResponse | None = None,
    success: bool = True,
    error: str | None = None,
)
MultiAgentResponse(*, results: list[AgentRunResult] = [])
MultiAgentOrchestrator(agents: dict[str, BaseAgent] | None = None)
```

Methods:

```text
register_agent(name: str, agent: BaseAgent) -> None
agent_names() -> tuple[str, ...]
run_agent(
    agent_name: str,
    message: str,
    metadata: dict[str, str] | None = None,
) -> AgentRunResult
run_sequence(
    agent_names: list[str],
    message: str,
    metadata: dict[str, str] | None = None,
) -> MultiAgentResponse
```

Registration rejects blank or duplicate names with `ValueError`.
`run_agent()` raises `ValueError` for an unknown name but converts exceptions
from a known agent into a failed `AgentRunResult`. `run_sequence()` rejects an
empty sequence or blank message, passes each successful output to the next
agent, and stops after the first failed result. It validates every requested
name before execution, so an unknown name raises without running an earlier
agent.

`MultiAgentResponse.success` is true only when at least one result exists and
every contained result succeeds. `final_output` is the last successful agent
output, which can remain populated after a later failure.

## Provider extension API

### `BaseAIProvider`

Custom providers must implement:

```text
ask_text(prompt: str) -> ProviderResponse
```

Optional capability methods:

```text
await ask_text_async(prompt: str) -> ProviderResponse
stream_text(prompt: str) -> Iterator[str]
stream_text_async(prompt: str) -> AsyncIterator[str]
ask_with_tools(prompt: str, tools: list[ToolDefinition]) -> ToolResponse
ask_with_images(prompt: str, images: list[ImageInput]) -> ProviderResponse
embed_text(text: str, metadata: dict[str, str] | None = None) -> EmbeddingResponse
embed_texts(inputs: list[EmbeddingInput]) -> EmbeddingResponse
```

Unimplemented optional methods raise `AIProviderError`. `embed_text()` delegates
to `embed_texts()` by default. Async streaming exists on the provider base but
has no public client method in this release.

### `ProviderFactory`

```text
ProviderFactory.create(config: AIConfig) -> BaseAIProvider
ProviderFactory.register(
    name: str,
    provider_class: type[BaseAIProvider],
) -> None
ProviderFactory.available_providers() -> tuple[str, ...]
```

Unknown providers, duplicate names, and incompatible construction raise
`AIConfigurationError` or an ordinary constructor exception as documented in
the provider guide. Registration is process-local global state and has no
unregister/replace operation. It proves only that an adapter is registered,
not that a selected model supports each optional capability.

Applications should select the built-in OpenAI adapter through `AIConfig` and
`AIClient`. Direct `OpenAIProvider` construction and its provider-SDK
translation helpers are not part of the supported application API.

## Framework integrations

### Django

Import from `ai.integrations.django`:

```text
get_django_ai_config(setting_name: str = "AI_TOOLKIT") -> AIConfig
get_ai_client(setting_name: str = "AI_TOOLKIT") -> AIClient
get_async_ai_client(setting_name: str = "AI_TOOLKIT") -> AsyncAIClient
```

The named Django setting is a complete explicit mapping; missing values do not
merge from `.env`. Helpers validate configuration and raise
`AIConfigurationError`. Each call constructs a new client.

### FastAPI

Import from `ai.integrations.fastapi`:

```text
get_ai_client() -> AIClient
get_async_ai_client() -> AsyncAIClient
AIClientDependency
AsyncAIClientDependency
```

The aliases are `Annotated` FastAPI dependencies. Each dependency resolution
constructs an environment-configured client. Applications own dependency
overrides, singleton/lifespan management, shutdown, and HTTP exception mapping.

## Command-line interface

Installed entry point:

```text
ai-toolkit ask PROMPT...
ai-toolkit config show
ai-toolkit config validate
```

`ask` makes a live plain-text provider request. `config show` and
`config validate` resolve configuration without contacting a provider.
Configuration display masks the API key.

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | Command succeeded |
| `1` | A handled `AIError` occurred |
| `2` | `argparse` rejected command syntax |

Unexpected exceptions are not converted into exit code `1`.

## Exception hierarchy

```text
AIError
├── AIConfigurationError
├── AIProviderError
├── AIJSONParseError
└── AISchemaValidationError
```

Catch a concrete subclass when recovery differs, or `AIError` at an application
boundary for expected toolkit failures. The hierarchy is not a universal
wrapper: `ValueError`, `FileNotFoundError`, Pydantic validation errors,
framework errors, and unexpected custom-provider failures may remain ordinary
exceptions. Workflows and known-agent executions may represent failures as
result objects instead of raising.

## Excluded implementation surface

The following modules and names are importable for implementation and tests but
are not supported application APIs:

- `ai.executor.RequestExecutor`
- `ai.async_executor.AsyncRequestExecutor`
- `ai.structured.build_structured_prompt`
- `ai.structured.parse_structured_response`
- `ai.retry.build_json_repair_prompt`
- `ai.cost.resolve_cost_rates`
- `ai.cost.calculate_cost_usd`
- `ai.logger.get_ai_logger` and logger constants
- `ai.providers.openai_provider.OpenAIProvider`
- provider-specific conversion and parsing helpers
- private names beginning with `_`

`ImageRequest`, `normalize_path()`, and other importable-but-undocumented names
remain internal. Their current importability does not create a deprecation or
compatibility obligation.

## Version 1.0 freeze decisions

| Review area | Version 1.0 decision |
| --- | --- |
| Top-level `ai` namespace | Keep it empty; documented module paths are the stable imports |
| Explicit `AIConfig` | Both clients validate it automatically before construction side effects |
| Request builder construction | Support `AIClient.request()`; treat the executor-taking constructor as internal wiring |
| Client attributes | `model` is observable metadata; `provider` and `executor` remain implementation exposure, not extension contracts |
| Built-in provider adapter | Select OpenAI through configuration and the factory; direct `OpenAIProvider` use is internal |
| Low-level names | Keep `ImageRequest`, `normalize_path()`, executors, repair helpers, logger helpers, and provider translation helpers internal |
| Cost helper | Keep `estimate_cost_usd()` as a supported compatibility helper |
| Advanced return values | Freeze the current split: `AIResult` for normal/image requests, `Iterator[str]` for streaming, `ToolResponse` for tools, and `EmbeddingResponse` for embeddings |
| Capability discovery | Keep it outside `BaseAIProvider`; unsupported optional methods raise `AIProviderError` |
| Agent prompt construction | Include the current user message once; preserve the documented memory lifecycle while treating exact prompt wording as implementation detail |
| Memory limits and agent metadata | Keep message-count limits and the current `AgentResponse` fields |
| Workflow failures | Keep shallow state updates from failed steps, stop-on-failure behavior, and failure-bearing results |
| Orchestration failures | Validate every requested agent name before execution; unknown names raise `ValueError`, while known-agent failures remain typed partial results |
| Empty orchestration result | Report `MultiAgentResponse.success == False`; success requires at least one result and no failures |

The decisions are documented by
[ADR-0018](architecture/decisions/0018-version-1-public-api-freeze.md).
Automatic client-boundary configuration validation is recorded separately in
[ADR-0017](architecture/decisions/0017-client-configuration-validation.md).

## Related documentation

- [Configuration](configuration.md)
- [Providers](providers.md)
- [Plain and structured requests](requests.md)
- [Advanced requests](advanced_requests.md)
- [Embeddings, retrieval, and RAG](retrieval.md)
- [Memory, agents, workflows, and orchestration](orchestration.md)
- [Django, FastAPI, and CLI integrations](integrations.md)
- [Exceptions and error handling](error_handling.md)
- [Security](security.md)
- [Compatibility](compatibility.md)
- [Examples](../examples/README.md)
