# Project State

## Project

Python AI Toolkit

## Current Version

0.7.0-dev

## Current Milestone

Sprint 7 completed — Agents & Workflows

## Current Sprint Status

Sprint 7 is complete.

Completed Sprint 7 tasks:

- AGENT-001 Conversation memory
- AGENT-002 Agent abstraction
- AGENT-003 Workflow engine
- AGENT-004 Multi-agent orchestration

## Implemented Capabilities

### Core Client

- `AIClient`
- `AsyncAIClient`
- plain text requests
- structured Pydantic responses
- request metadata through `AIResult`
- request IDs
- token usage tracking
- estimated cost tracking
- retry tracking

### Providers

- provider-independent `BaseAIProvider`
- OpenAI provider implementation
- `ProviderFactory`
- provider registry
- custom provider registration
- provider-aware configuration through `AI_PROVIDER`

### Configuration

- `.env` based configuration
- provider-specific API keys and models
- generic fallback API key and model
- separate embedding model configuration
- optional embedding dimensions configuration
- configurable retry count
- configuration validation through `ConfigValidator`
- helpful configuration error messages

### Request Execution

- sync request execution
- async request execution
- structured-output retry repair
- centralized structured-output helpers in `ai/structured.py`
- streaming text responses
- image input requests
- tool-aware requests

### Developer Experience

- fluent request builder
- prompt templates
- example gallery
- improved README documentation
- error message guidelines

### Advanced Requests

- synchronous streaming text responses
- async AI client
- provider-independent tool definitions
- provider-independent tool-call responses
- OpenAI tool-call adapter
- provider-independent image inputs
- OpenAI image-input adapter
- structured output support for text, async, and image requests

### Retrieval & Knowledge

- provider-independent embedding models
- OpenAI embedding adapter
- embedding metadata preservation
- vector store abstraction
- in-memory vector store
- cosine similarity search
- metadata filtering
- retriever interface
- vector-store-backed retriever
- prompt-ready retrieved context formatting
- RAG prompt builder
- RAG pipeline
- answer generation with returned sources
- document model
- text file loader
- Markdown file loader
- directory loader
- document-to-embedding conversion helper

### Agents & Workflows

- provider-independent conversation message model
- conversation memory interface
- in-memory conversation memory
- conversation formatting helper
- memory-backed agent abstraction
- agent response model
- system instructions
- recent memory limit
- sequential workflow engine
- workflow context
- workflow step results
- function-backed workflow steps
- workflow state passing
- workflow execution history
- fail-fast workflow behavior
- multi-agent orchestration
- named agent registration
- single-agent execution by name
- sequential multi-agent execution
- multi-agent result collection
- multi-agent failure handling

## Current Architecture

```text
Application
    ↓
AIClient / AsyncAIClient
    ↓
RequestExecutor / AsyncRequestExecutor
    ↓
ProviderFactory
    ↓
BaseAIProvider implementation
    ↓
LLM provider
```

Additional request helpers:

```text
AIClient.request()
    ↓
AIRequestBuilder
    ↓
RequestExecutor
```

Structured-output flow:

```text
response_type
    ↓
ai.structured.build_structured_prompt()
    ↓
provider request
    ↓
ai.structured.parse_structured_response()
    ↓
AIResult[data]
```

Embedding flow:

```text
text / EmbeddingInput
    ↓
AIClient.embed_text() / AIClient.embed_texts()
    ↓
Provider.embed_texts()
    ↓
EmbeddingResponse
```

Retriever and RAG flow:

```text
question
    ↓
RAGPipeline
    ↓
BaseRetriever.retrieve()
    ↓
format_retrieved_context()
    ↓
build_rag_prompt()
    ↓
AIClient.ask()
    ↓
RAGResponse(answer, contexts)
```

Agent flow:

```text
user message
    ↓
Agent
    ↓
ConversationMemory
    ↓
AIClient.ask()
    ↓
AgentResponse
```

Workflow flow:

```text
input
    ↓
WorkflowEngine
    ↓
WorkflowStep
    ↓
WorkflowContext.state
    ↓
WorkflowRunResult
```

Multi-agent flow:

```text
message
    ↓
MultiAgentOrchestrator
    ↓
agent 1
    ↓
agent 2
    ↓
agent 3
    ↓
MultiAgentResponse
```

## Completed Milestones

### Sprint 2 — Core Architecture

Completed:

- architecture documentation
- decisions documentation
- roadmap documentation
- retry helper
- configurable retry behavior
- duplicate logging cleanup

### Sprint 3 — Provider Infrastructure

Completed:

- provider interface
- OpenAI provider implementation
- provider factory
- provider configuration cleanup

### Sprint 4 — Developer Experience

Completed:

- fluent request builder
- prompt templates
- example gallery
- configuration validation improvements
- better error messages

### Sprint 5 — Advanced Requests

Completed:

- streaming responses
- async client
- tool calling
- image inputs
- structured output improvements

### Sprint 6 — Retrieval & Knowledge

Completed:

- embeddings
- vector store abstraction
- retriever interface
- RAG pipeline
- document loaders

### Sprint 7 — Agents & Workflows

Completed:

- conversation memory
- agent abstraction
- workflow engine
- multi-agent orchestration

## Next Milestone

To be selected from roadmap.

## Next Recommended Focus

Sprint 7 completed the first reusable agents and workflows layer.

The next recommended focus depends on the remaining roadmap.

Strong candidates:

- testing and quality hardening
- packaging and public API cleanup
- provider expansion
- production persistence features
- evaluation and observability

## Important Design Decisions

- `AIClient.ask()` remains the main simple API.
- `AIClient.request()` is the fluent advanced API.
- `AsyncAIClient` is separate from `AIClient`.
- Tool calling does not automatically execute tools yet.
- Image inputs support URLs and Base64 data URLs, not local paths directly.
- Structured output remains provider-independent for now.
- Provider-native strict structured output is deferred.
- Embeddings use a separate embedding model configuration.
- Retrieval is provider-independent.
- Vector storage is abstracted behind `BaseVectorStore`.
- `InMemoryVectorStore` is for tests, examples, demos, and small local workflows.
- Production RAG should later use a persistent vector store.
- Document loaders produce `Document`; embedding happens separately.
- Chunking is intentionally deferred.
- Agents are explicit and memory-backed.
- Multi-agent orchestration is explicit and sequential.
- Autonomous routing, recursive loops, and agent debate are deferred.

## Current Testing Expectation

Before committing each task:

```bash
python -m pytest
python -m black .
python -m ruff check .
```

## Current Git Workflow

Each roadmap task should be committed separately.

Sprint completion updates:

- `docs/development/roadmap.md`
- `docs/development/project_state.md`