# Project State

## Project

Python AI Toolkit

## Current Version

0.5.0-dev

## Current Milestone

Sprint 5 completed — Advanced Requests

## Current Sprint Status

Sprint 5 is complete.

Completed Sprint 5 tasks:

- REQUEST-001 Streaming responses
- REQUEST-002 Async AIClient
- REQUEST-003 Tool Calling
- REQUEST-004 Image inputs
- REQUEST-005 Structured output improvements

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

Tool-calling flow:

```text
ToolDefinition
    ↓
AIClient.ask_with_tools()
    ↓
RequestExecutor.execute_with_tools()
    ↓
Provider.ask_with_tools()
    ↓
ToolResponse
```

Image-input flow:

```text
ImageInput
    ↓
AIClient.ask_with_images()
    ↓
RequestExecutor.execute_with_images()
    ↓
Provider.ask_with_images()
    ↓
AIResult
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

## Next Milestone

Sprint 6 — Agents and Workflows

## Next Recommended Focus

The toolkit now supports individual advanced request capabilities.

The next architectural step is to build controlled multi-step workflows on top of those capabilities.

Recommended next tasks:

- define agent/workflow scope
- add tool result submission
- add one-step tool execution helper
- add multi-step agent loop later
- keep application approval/control explicit

## Important Design Decisions

- `AIClient.ask()` remains the main simple API.
- `AIClient.request()` is the fluent advanced API.
- `AsyncAIClient` is separate from `AIClient`.
- Tool calling does not automatically execute tools yet.
- Image inputs support URLs and Base64 data URLs, not local paths directly.
- Structured output remains provider-independent for now.
- Provider-native strict structured output is deferred.
- Agents should build on top of tools, not be mixed into basic request execution.

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