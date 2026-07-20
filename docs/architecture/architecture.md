# Architecture

## Purpose

The Python AI Toolkit provides reusable infrastructure for integrating Large Language Models (LLMs) into Python applications.

The toolkit intentionally avoids business logic.

Applications remain responsible for domain-specific decisions, while the toolkit handles AI communication, provider abstraction, structured output, retrieval, memory, agents, and workflow infrastructure.

---

# Design Philosophy

The toolkit is designed around these principles.

1. Separation of concerns
2. Strong typing
3. Extensibility
4. Provider independence
5. Explicit interfaces
6. Small public API

Every component should have one clearly defined responsibility.

Business logic belongs in applications, not in the toolkit.

---

# High-Level Architecture

```text
Application
        │
        ▼
AIClient / AsyncAIClient
        │
        ▼
RequestExecutor / AsyncRequestExecutor
        │
        ▼
ProviderFactory
        │
        ▼
BaseAIProvider
        │
        ▼
Provider Implementation
        │
        ▼
Language Model Provider
        │
        ▼
ProviderResponse
        │
        ▼
Parser / Structured Output
        │
        ▼
AIResult
        │
        ▼
Application
```

Additional toolkit layers build on top of the core client.

```text
Application
        │
        ├── Prompt Templates
        ├── Fluent Request Builder
        ├── Tool Calling
        ├── Image Inputs
        ├── Embeddings
        ├── Vector Store
        ├── Retriever
        ├── RAG Pipeline
        ├── Document Loaders
        ├── Conversation Memory
        ├── Agents
        ├── Workflow Engine
        └── Multi-Agent Orchestration
```

---

# Core Responsibilities

## AIClient

Responsibilities

- Public synchronous API
- Resolve supplied or environment-based configuration
- Create provider through `ProviderFactory`
- Delegate request execution
- Expose advanced request helpers
- Expose embedding helpers
- Supports explicit AIConfig injection for framework integrations and tests.

Supports

- `ask()`
- `ask_text()`
- `request()`
- `stream()`
- `ask_with_tools()`
- `ask_with_images()`
- `embed_text()`
- `embed_texts()`

Does NOT

- Retry requests directly
- Parse JSON directly
- Log requests directly
- Calculate cost directly
- Execute tools automatically
- Store application business logic

---

## AsyncAIClient

Responsibilities

- Public asynchronous API
- Resolve supplied or environment-based configuration
- Create provider through `ProviderFactory`
- Delegate async request execution to `AsyncRequestExecutor`
- Supports explicit AIConfig injection for framework integrations and tests.

Supports

- `ask()`
- `ask_text()`

Does NOT

- Replace `AIClient`
- Mix sync and async behavior in one client
- Provide async streaming yet
- Provide async tool calling yet
- Provide async image input yet

Reason

Sync and async usage are intentionally separated to keep the public API clear.

---

## RequestExecutor

Responsibilities

- Execute synchronous requests
- Measure duration
- Retry failed structured responses
- Parse structured responses
- Validate schemas
- Calculate estimated cost
- Log request outcomes
- Return `AIResult`
- Execute image-aware requests
- Execute tool-aware requests
- Execute streaming requests

RequestExecutor owns the synchronous request lifecycle.

---

## AsyncRequestExecutor

Responsibilities

- Execute asynchronous requests
- Measure duration
- Retry failed structured responses
- Parse structured responses
- Validate schemas
- Calculate estimated cost
- Log async request outcomes
- Return `AIResult`

AsyncRequestExecutor mirrors RequestExecutor for async applications.

---

## ProviderFactory

Responsibilities

- Own provider registry
- Create provider instances
- Support custom provider registration
- List available providers
- Pass supported configuration into providers

ProviderFactory keeps provider selection out of `AIClient`.

Applications should not instantiate provider implementations directly.

---

## BaseAIProvider

Responsibilities

Define the provider interface used by the toolkit.

Required capability

- `ask_text()`

Optional capabilities

- `ask_text_async()`
- `stream_text()`
- `stream_text_async()`
- `ask_with_tools()`
- `ask_with_images()`
- `embed_text()`
- `embed_texts()`

Optional capabilities raise helpful `AIProviderError` messages when a provider does not support them.

---

## Provider Implementations

Responsibilities

Translate toolkit requests into provider-specific SDK calls.

Current implementation

- OpenAI

Future implementations may include

- Anthropic
- Google Gemini
- Azure OpenAI
- Ollama
- Local LLM providers

Applications should never communicate with provider SDKs directly.

---

# Structured Output Architecture

## Structured Helpers

Structured output logic is centralized in `ai/structured.py`.

Responsibilities

- Build schema-aware prompts
- Parse raw model responses into Pydantic models
- Keep structured-output behavior separate from request execution

Flow

```text
response_type
        │
        ▼
build_structured_prompt()
        │
        ▼
Provider request
        │
        ▼
Raw response
        │
        ▼
parse_structured_response()
        │
        ▼
Pydantic model
        │
        ▼
AIResult[data]
```

Reason

Structured output behavior is shared by sync requests, async requests, and image requests.

---

## Parser

Responsibilities

- Convert raw model responses into Python objects
- Parse JSON
- Raise toolkit-specific parse errors
- Delegate schema validation to Pydantic

Parser should know nothing about providers.

---

## Schemas

Responsibilities

Define contracts between AI output and Python code.

Schemas ensure

- validation
- type safety
- editor autocomplete
- predictable application behavior

Applications should work with typed objects instead of unvalidated raw JSON.

---

## AIResult

AIResult is the standard response object returned by most toolkit requests.

It contains

- `data`
- `model`
- `duration_ms`
- `retries_used`
- `request_id`
- `token_usage`
- `estimated_cost_usd`
- `raw_response`
- `original_raw_response`
- `cached`

This allows future metadata without changing the public API.

---

# Prompting Architecture

## PromptBuilder

Responsibilities

- Build prompts from sections
- Keep prompt assembly readable
- Support dynamic prompt construction

---

## PromptTemplate

Responsibilities

- Store reusable prompt templates
- Render variables with Python format strings
- Keep prompt structure separate from prompt data

---

## AIRequestBuilder

Responsibilities

- Provide fluent request configuration
- Delegate execution to `RequestExecutor`
- Keep advanced request setup readable

Example flow

```text
AIClient.request()
        │
        ▼
AIRequestBuilder
        │
        ▼
.prompt(...)
        │
        ▼
.response_type(...)
        │
        ▼
.execute()
        │
        ▼
RequestExecutor
```

---

# Advanced Request Architecture

## Streaming

Streaming flow

```text
Application
        │
        ▼
AIClient.stream()
        │
        ▼
RequestExecutor.stream()
        │
        ▼
Provider.stream_text()
        │
        ▼
Text chunks
        │
        ▼
Application
```

Current support

- Synchronous plain text streaming

Not yet supported

- Async streaming
- Structured streaming
- Streaming token metadata

---

## Tool Calling

Tool calling exposes requested tool calls but does not execute tools automatically.

Flow

```text
ToolDefinition
        │
        ▼
AIClient.ask_with_tools()
        │
        ▼
RequestExecutor.execute_with_tools()
        │
        ▼
Provider.ask_with_tools()
        │
        ▼
ToolResponse
        │
        ▼
Application executes or ignores tool calls
```

Responsibilities

- Toolkit defines provider-independent tool models
- Provider translates tool definitions to provider format
- Model returns requested tool calls
- Application decides whether and how to execute tools

Reason

Tool execution can have side effects and must remain under application control.

---

## Image Inputs

Image input flow

```text
ImageInput
        │
        ▼
AIClient.ask_with_images()
        │
        ▼
RequestExecutor.execute_with_images()
        │
        ▼
Provider.ask_with_images()
        │
        ▼
ProviderResponse
        │
        ▼
AIResult
```

Current support

- Image URLs
- Base64 data URLs
- Multiple images
- Plain text responses
- Structured responses

Not yet supported

- Local image file helper
- Provider file ID helper
- Image generation
- Image editing
- Async image input

---

# Retrieval and Knowledge Architecture

## Embeddings

Embedding flow

```text
Text / EmbeddingInput
        │
        ▼
AIClient.embed_text() / AIClient.embed_texts()
        │
        ▼
Provider.embed_texts()
        │
        ▼
EmbeddingResponse
```

Responsibilities

- Convert text into vectors
- Preserve metadata
- Use separate embedding model configuration
- Keep embedding provider details hidden inside providers

Current implementation

- OpenAI embeddings

---

## Vector Store

Vector store flow

```text
VectorRecord
        │
        ▼
BaseVectorStore
        │
        ▼
InMemoryVectorStore
        │
        ▼
similarity_search()
        │
        ▼
VectorSearchResult
```

Responsibilities

- Store vectors
- Preserve text and metadata
- Run similarity search
- Support metadata filtering

Current implementation

- `InMemoryVectorStore`

Purpose

The vector store abstraction allows future persistent stores without changing retriever or RAG pipeline code.

Future stores may include

- PostgreSQL with pgvector
- Chroma
- Pinecone
- FAISS
- Qdrant

---

## Retriever

Retriever flow

```text
Query
        │
        ▼
VectorStoreRetriever
        │
        ▼
AIClient.embed_text()
        │
        ▼
BaseVectorStore.similarity_search()
        │
        ▼
RetrievedContext
```

Responsibilities

- Embed user query
- Search vector store
- Return prompt-ready context objects
- Hide raw vectors from higher-level RAG code
- Support metadata filtering

---

## RAG Pipeline

RAG flow

```text
Question
        │
        ▼
RAGPipeline
        │
        ▼
BaseRetriever.retrieve()
        │
        ▼
format_retrieved_context()
        │
        ▼
build_rag_prompt()
        │
        ▼
AIClient.ask()
        │
        ▼
RAGResponse(answer, contexts)
```

Responsibilities

- Retrieve relevant context
- Build grounded prompt
- Ask AI client for answer
- Return answer and source contexts

Reason

RAG lets applications answer using their own documents, database rows, support articles, policies, or project knowledge.

---

## Document Loaders

Document loading flow

```text
File / Directory
        │
        ▼
DocumentLoader
        │
        ▼
Document
        │
        ▼
EmbeddingInput
        │
        ▼
Embeddings
        │
        ▼
VectorRecord
        │
        ▼
Vector Store
        │
        ▼
Retriever
        │
        ▼
RAG Pipeline
```

Current loaders

- `TextFileLoader`
- `MarkdownFileLoader`
- `DirectoryLoader`

Responsibilities

- Load text from sources
- Preserve source metadata
- Keep loading separate from embedding and indexing

Reason

Document loading, embedding, chunking, and indexing are separate responsibilities.

---

# Agents and Workflows Architecture

## Conversation Memory

Memory flow

```text
ConversationMessage
        │
        ▼
BaseConversationMemory
        │
        ▼
InMemoryConversationMemory
```

Responsibilities

- Store system, user, assistant, and tool messages
- Preserve metadata
- Return all messages
- Return recent messages
- Clear memory
- Format memory for prompts

Current implementation

- `InMemoryConversationMemory`

---

## Agent

Agent flow

```text
User message
        │
        ▼
Agent
        │
        ▼
ConversationMemory
        │
        ▼
Prompt with instructions and recent memory
        │
        ▼
AIClient.ask()
        │
        ▼
Assistant response
        │
        ▼
ConversationMemory
        │
        ▼
AgentResponse
```

Responsibilities

- Hold system instructions
- Store user messages
- Include recent memory in prompts
- Ask AI client
- Store assistant responses
- Return agent response metadata

Does NOT

- Execute tools automatically
- Perform RAG automatically
- Run workflows automatically
- Route to other agents

---

## Workflow Engine

Workflow flow

```text
Input
        │
        ▼
WorkflowEngine
        │
        ▼
WorkflowStep
        │
        ▼
WorkflowContext.state
        │
        ▼
Next WorkflowStep
        │
        ▼
WorkflowRunResult
```

Responsibilities

- Run sequential steps
- Pass shared workflow context
- Apply state updates
- Keep execution history
- Stop on failure
- Convert unexpected exceptions into failed step results

Current implementation

- `WorkflowEngine`
- `FunctionWorkflowStep`

Not yet supported

- Branching workflows
- Parallel execution
- Step retries
- Async workflows
- Durable workflow persistence

---

## Multi-Agent Orchestration

Multi-agent flow

```text
Message
        │
        ▼
MultiAgentOrchestrator
        │
        ▼
Agent 1
        │
        ▼
Agent 2
        │
        ▼
Agent 3
        │
        ▼
MultiAgentResponse
```

Responsibilities

- Register named agents
- Run one selected agent by name
- Run multiple agents sequentially
- Pass successful output to the next agent
- Collect agent results
- Stop sequence on failure

Does NOT

- Automatically route with AI
- Run agents in parallel
- Create recursive loops
- Run agent debates
- Share global memory automatically

Reason

The first multi-agent design is intentionally explicit, sequential, testable, and safe.

---

# Configuration Architecture

Configuration is loaded from environment variables.

Provider configuration

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini
```

Embedding configuration

```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
AI_EMBEDDING_DIMENSIONS=
```

Generic fallback configuration

```env
AI_API_KEY=
AI_MODEL=
AI_EMBEDDING_MODEL=
```

Retry and cost configuration

```env
AI_MAX_RETRIES=1
AI_INPUT_COST_PER_1M_TOKENS=
AI_OUTPUT_COST_PER_1M_TOKENS=
```

Responsibilities

- `ai/config.py` loads configuration
- `ConfigValidator` validates configuration
- `ProviderFactory` uses configuration to create providers

---

# Framework Integration Architecture

Framework integrations translate framework-specific configuration into the toolkit's provider-independent configuration model.

Current integration

- Django
- FastAPI
- Command-line interface

Future integrations may include

* FastAPI
* command-line applications
* other Python frameworks

Framework integration flow:

```text
Framework configuration
        │
        ▼
Framework adapter
        │
        ▼
AIConfig
        │
        ▼
AIClient / AsyncAIClient
        │
        ▼
ProviderFactory
```

## Explicit Client Configuration

`AIClient` and `AsyncAIClient` accept an optional `AIConfig`.

Environment-based configuration remains the default:

```python
client = AIClient()
```

Applications and framework adapters may provide explicit configuration:

```python
client = AIClient(config=config)
```

Responsibilities

* `get_ai_config()` loads environment-based configuration.
* Framework adapters create `AIConfig` from framework settings.
* `ConfigValidator` validates provider-independent configuration.
* `ProviderFactory` creates the configured provider.
* Clients create the appropriate request executor.

Reason

Explicit configuration injection allows framework integrations without modifying environment variables or adding framework dependencies to core modules.

## Django Integration

Django integration flow:

```text
Django settings.AI_TOOLKIT
        │
        ▼
get_django_ai_config()
        │
        ▼
AIConfig
        │
        ▼
get_ai_client() / get_async_ai_client()
        │
        ▼
AIClient / AsyncAIClient
```

Responsibilities

* Read the configured Django setting.
* Validate that the setting is a mapping.
* Reject unsupported fields.
* Normalize the provider name.
* Construct `AIConfig`.
* Reuse `ConfigValidator`.
* Create synchronous or asynchronous toolkit clients.

Does NOT

* Add Django models.
* Add database migrations.
* Add middleware.
* Add views or API endpoints.
* Add Django business logic.
* Modify environment variables.
* Import Django inside core toolkit modules.
* Automatically create or cache global clients.

Django remains an optional dependency.

Applications explicitly import the integration:

```python
from ai.integrations.django import get_ai_client
```

Core users do not import Django when using:

```python
from ai.client import AIClient
```

Reason

Framework-specific concerns remain at the application boundary while the core toolkit stays framework-independent.

## FastAPI Integration

FastAPI integration uses the framework's dependency injection system.

Flow:

```text
HTTP request
        │
        ▼
FastAPI endpoint
        │
        ▼
AIClientDependency / AsyncAIClientDependency
        │
        ▼
get_ai_client() / get_async_ai_client()
        │
        ▼
AIClient / AsyncAIClient
        │
        ▼
ProviderFactory
        │
        ▼
Configured provider
```

Responsibilities

* Provide synchronous and asynchronous client dependencies.
* Expose reusable `Annotated` dependency aliases.
* Allow FastAPI to inject toolkit clients into endpoints.
* Support FastAPI dependency overrides during tests.
* Reuse the existing environment-based toolkit configuration.
* Keep endpoint and application logic outside the toolkit.

Public dependency helpers

```python
from ai.integrations.fastapi import (
    get_ai_client,
    get_async_ai_client,
)
```

Public dependency aliases

```python
from ai.integrations.fastapi import (
    AIClientDependency,
    AsyncAIClientDependency,
)
```

Synchronous endpoint example:

```python
from fastapi import FastAPI
from pydantic import BaseModel

from ai.integrations.fastapi import AIClientDependency

app = FastAPI()


class SummaryRequest(BaseModel):
    text: str


@app.post("/summarize")
def summarize(
    request: SummaryRequest,
    client: AIClientDependency,
):
    result = client.ask(
        f"Summarize the following text:\n\n{request.text}"
    )

    return {
        "summary": result.data,
    }
```

Asynchronous endpoint example:

```python
from fastapi import FastAPI
from pydantic import BaseModel

from ai.integrations.fastapi import AsyncAIClientDependency

app = FastAPI()


class SummaryRequest(BaseModel):
    text: str


@app.post("/summarize-async")
async def summarize_async(
    request: SummaryRequest,
    client: AsyncAIClientDependency,
):
    result = await client.ask(
        f"Summarize the following text:\n\n{request.text}"
    )

    return {
        "summary": result.data,
    }
```

Testing flow:

```text
FastAPI test request
        │
        ▼
app.dependency_overrides
        │
        ▼
Fake AI client
        │
        ▼
Endpoint execution
        │
        ▼
Test response
```

FastAPI applications can replace the real toolkit dependency during tests:

```python
from types import SimpleNamespace

from ai.integrations.fastapi import get_ai_client


class FakeAIClient:
    def ask(self, prompt: str):
        return SimpleNamespace(data="Test response")


app.dependency_overrides[get_ai_client] = FakeAIClient
```

Does NOT

* Add API routes.
* Add request or response schemas.
* Add middleware.
* Manage authentication or permissions.
* Perform database operations.
* Define application prompts.
* Add application business logic.
* Automatically create application-lifetime singleton clients.
* Automatically manage FastAPI lifespan resources.

Reason

FastAPI dependency aliases reduce repeated dependency declaration boilerplate while preserving the existing `AIClient` and `AsyncAIClient` configuration and execution lifecycle.

The first implementation creates clients through normal FastAPI dependencies.

Application-lifetime client management is intentionally deferred until there is a clear lifecycle, connection-management, caching, or resource-cleanup requirement.

## Command-Line Interface

The command-line interface provides terminal access to the existing toolkit client.

CLI flow:

```text
Terminal command
        │
        ▼
ai-toolkit console entry point
        │
        ▼
main()
        │
        ▼
argparse command parser
        │
        ▼
Command handler
        │
        ▼
AIClient
        │
        ▼
ProviderFactory
        │
        ▼
Configured provider
```

Current command:

```text
ai-toolkit ask "<prompt>"
```

Example:

```bash
ai-toolkit ask "Explain dependency injection simply."
```

Responsibilities

* Parse command-line arguments.
* Route subcommands to their registered handlers.
* Create the existing `AIClient`.
* Send plain-text prompts.
* Print successful responses to standard output.
* Print expected toolkit errors to standard error.
* Return predictable process exit codes.
* Reuse the existing environment-based toolkit configuration.

Exit codes:

```text
0   Command completed successfully
1   Toolkit configuration or provider error
2   Invalid command-line syntax
```

The CLI catches exceptions derived from `AIError`.

This includes expected toolkit failures such as:

* `AIConfigurationError`
* `AIProviderError`
* `AIJSONParseError`
* `AISchemaValidationError`

Unexpected exceptions are not silently hidden because they may represent programming defects.

The console entry point is configured in `pyproject.toml`:

```toml
[project.scripts]
ai-toolkit = "ai.cli.main:main"
```

This means that running:

```text
ai-toolkit
```

executes:

```python
ai.cli.main.main()
```

The CLI uses subcommand handlers.

For example, the `ask` parser registers:

```python
ask_parser.set_defaults(handler=run_ask_command)
```

After parsing the command, `main()` executes the selected handler:

```python
return args.handler(args)
```

This structure allows future commands to be added without replacing the parser architecture or creating a large conditional block.

Does NOT

* Implement a separate AI request lifecycle.
* Communicate directly with provider SDKs.
* Store API keys.
* Modify `.env` files.
* Manage provider or model configuration.
* Support structured output.
* Support streaming responses.
* Support tool calling.
* Support image inputs.
* Provide an interactive conversation loop.
* Add business-specific commands.

Reason

The CLI is an application adapter around `AIClient`.

It reuses the existing configuration, provider selection, request execution, retry, logging, and response architecture instead of duplicating them.

The initial CLI uses Python's standard-library `argparse` module because the current command structure is small and does not justify another runtime dependency.

The CLI package uses subcommand handlers so future commands can be added while preserving the same public console entry point.

Configuration-related commands are intentionally reserved for:

```text
INTEGRATION-004 — Configuration CLI
```




## Structured Request

```text
Application
        │
        ▼
AIClient.ask(response_type=...)
        │
        ▼
build_structured_prompt()
        │
        ▼
Provider.ask_text()
        │
        ▼
ProviderResponse
        │
        ▼
parse_structured_response()
        │
        ▼
Pydantic validation
        │
        ▼
Retry repair if needed
        │
        ▼
AIResult[PydanticModel]
        │
        ▼
Application
```

---

## Async Request

```text
Application
        │
        ▼
AsyncAIClient.ask()
        │
        ▼
AsyncRequestExecutor.execute()
        │
        ▼
Provider.ask_text_async()
        │
        ▼
ProviderResponse
        │
        ▼
AIResult
        │
        ▼
Application
```

---

# Why Provider Abstraction?

Without abstraction

```text
Application
        │
        ▼
OpenAI SDK
```

Changing providers would require modifying every application.

With abstraction

```text
Application
        │
        ▼
Toolkit
        │
        ▼
BaseAIProvider
        │
        ▼
OpenAI / Anthropic / Gemini / Ollama / Azure
```

Only the provider implementation changes.

Applications remain unchanged.

---

# Why AIResult?

Returning raw strings would make future improvements difficult.

Instead

```python
result = ai.ask(...)
```

gives

```python
result.data
result.model
result.duration_ms
result.token_usage
result.estimated_cost_usd
result.request_id
result.retries_used
```

The API stays stable even as metadata grows.

---

# Why Pydantic?

Pydantic provides

- validation
- type hints
- editor autocomplete
- predictable application behavior

AI output should never be trusted without validation.

---

# Logging Strategy

By default, successful and failed requests are logged.

Logged

- request id
- model
- duration
- retries
- token usage
- estimated cost

Not logged

- prompts
- model responses

Reason

Prompts and model responses may contain confidential business information.

Known future improvements

- Configurable log file path
- Configurable log level
- Option to disable file logging during tests
- Test-safe logging configuration
- Optional debug logging

---

# Current Technical Debt and Deferred Work

Known deferred improvements

- Provider-native strict structured output
- Async streaming
- Async tool calling
- Async image input
- Local image file helper
- Automatic tool execution
- Persistent vector stores
- Document chunking
- PDF, DOCX, HTML, and database loaders
- RAG citations formatter
- RAG reranking
- RAG evaluation
- Persistent conversation memory
- Token-aware memory trimming
- Agent prompt template customization
- Tool-using agents
- RAG-aware agents
- Async agents
- Branching workflow engine
- Parallel workflow execution
- Workflow step retries
- Durable workflow persistence
- AI-based agent routing
- Parallel multi-agent execution
- Shared multi-agent memory
- Recursive agent loops
- Test-safe logging configuration

Technical debt and deferred ideas are tracked intentionally in the roadmap and Future Backlog.

---

# Long-Term Vision

Current

```text
Application
        │
        ▼
Toolkit
        │
        ▼
OpenAI
```

Future

```text
Application
        │
        ▼
Toolkit
        │
        ▼
Provider Interface
        │
        ├── OpenAI
        ├── Anthropic
        ├── Gemini
        ├── Ollama
        ├── Azure OpenAI
        └── Local LLMs
```

Applications should never need to change when providers change.

The toolkit should become a reusable foundation for:

- structured AI requests
- provider switching
- tool-aware applications
- image-aware applications
- retrieval-augmented generation
- document-based knowledge systems
- conversation agents
- workflow automation
- multi-agent coordination

---

# Architecture Principles

The toolkit follows these principles.

- Single Responsibility Principle
- Dependency Inversion Principle
- Composition over inheritance
- Explicit interfaces
- Strong typing
- Small public API
- Extensible internal architecture
- Provider independence
- Application-controlled business logic

When making future design decisions, preserving these principles takes priority over adding features quickly.
