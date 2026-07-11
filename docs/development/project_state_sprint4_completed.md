# Project State

## Project

Python AI Toolkit

## Current Version

0.4.0-dev

## Current Milestone

Sprint 4 completed — Developer Experience

## Current Goal

Build a reusable AI engineering toolkit for Python developers.

The toolkit should provide reusable infrastructure for:

- AI client abstraction
- Provider integrations
- Structured responses
- Validation
- Retry handling
- Logging
- Token tracking
- Cost tracking
- Tool calling
- Embeddings
- RAG
- Agents
- Django integration

---

# Current Sprint Status

## Sprint 4 – Developer Experience

Status: Completed

### Completed Tasks

- DX-001 Fluent Request Builder
- DX-002 Prompt templates
- DX-003 Example gallery
- DX-004 Configuration validation improvements
- DX-005 Better error messages

### Exit Criteria

- Building prompts should require minimal boilerplate.

---

# Completed Milestones

## Sprint 2 – Core Infrastructure Refinement

Status: Completed

### Completed Tasks

- CORE-001 Create architecture documentation
- CORE-002 Create Architecture Decision Records (ADRs)
- CORE-003 Create project roadmap
- CORE-004 Remove duplicate success logging
- CORE-005 Extract retry prompt helper
- CORE-006 Configurable retry count

### Exit Criteria

- Core architecture documented
- RequestExecutor cleaned up
- Retry configurable
- Sprint documentation complete

## Sprint 3 – Provider Infrastructure

Status: Completed

### Completed Tasks

- PROVIDER-001 ProviderFactory
- PROVIDER-002 Provider registry
- PROVIDER-003 Provider Registration API
- PROVIDER-004 Provider configuration cleanup

### Exit Criteria

- Adding a new provider requires no changes to AIClient.

---

# Next Sprint

## Sprint 5 – Advanced Requests

### Goal

Support advanced LLM capabilities.

### Next Task

REQUEST-001 Streaming responses

---

# Implemented

- Provider-based architecture
- OpenAI provider
- `ProviderFactory`
- Provider registry
- Provider registration API
- Provider-aware configuration loading
- Configuration validation
- Improved developer-friendly error messages
- `AIClient`
- `RequestExecutor`
- Fluent request builder
- Prompt builder
- Prompt templates
- Pydantic schema-based responses
- `AIResult`
- `ProviderResponse`
- `TokenUsage`
- Custom exceptions
- JSON parser
- JSON repair prompt helper
- Configurable retry count through `.env`
- Request duration tracking
- Request IDs
- Token usage tracking
- Token usage aggregation across retries
- Estimated cost scaffold
- Configurable token pricing through `.env`
- Basic file logging
- Drink recommender example
- Example gallery
- Parser tests
- Prompt builder tests
- Prompt template tests
- Request executor tests
- Request builder tests
- Configuration tests
- Configuration validator tests
- Provider factory tests
- Retry behavior test

---

# Current Architecture

```text
Application
    ↓
AIClient
    ├── ask()
    └── request()
            ↓
        AIRequestBuilder
            ↓
RequestExecutor
    ↓
Provider
    ↓
LLM
    ↓
ProviderResponse
    ↓
Parser / Validator
    ↓
AIResult
    ↓
Application
```

---

# Important Design Decisions

- Applications should use `AIClient`, not provider SDKs directly.
- Provider-specific SDK code lives inside provider classes.
- `AIClient` is intentionally small and acts as the public API.
- `AIClient.ask()` remains the simple request API.
- `AIClient.request()` creates a mutable fluent request builder for advanced requests.
- `AIRequestBuilder` collects request configuration but does not own execution logic.
- `RequestExecutor` owns the request lifecycle.
- Structured responses use Pydantic models.
- `AIResult` returns both validated data and metadata.
- Prompts and responses are not logged by default for privacy.
- Business logic must stay outside the toolkit.
- Retry behavior is configurable and currently applies to structured responses.
- Configuration loading and configuration validation are separated.
- Provider availability is validated by `ProviderFactory`, not by the configuration validator.
- Error messages should explain the problem and suggest a fix whenever possible.
- Architecture decisions are documented using ADR files.

---

# Documentation Structure

```text
docs/
    architecture/
        architecture.md
        decisions/
            template.md
            0001-airesult.md
            0002-provider-abstraction.md
            0003-request-executor.md
            0004-schema-validation.md
            0005-provider-factory.md
            0006-provider-registry.md
            0007-provider-registration-api.md

    development/
        roadmap.md
        project_state.md
        error_messages.md
```

---

# Current Technical Debt

- Retry behavior is implemented but can be improved with a dedicated retry strategy object.
- Cost table is still a scaffold and should eventually use verified provider pricing.
- Provider selection currently supports only OpenAI by default.
- Additional providers are not yet implemented.
- Error handling around non-toolkit exceptions can be improved.
- Logging currently writes only to a file.
- Streaming and async support are not yet implemented.
- The mutable request builder is intentionally simple; immutable / reusable builders are a future backlog idea.
- Example scripts are manually verified; future CI could run examples against mocked providers.

---

# Roadmap Source of Truth

The active roadmap is stored in:

```text
docs/development/roadmap.md
```

Current rule:

- Only one sprint is active at a time.
- New ideas go to the Future Backlog.
- The active sprint does not change without an explicit decision.
- Every completed task updates the roadmap immediately.
- Every architectural decision requires an ADR.
- Every public API change updates the README.
- Every released feature updates the CHANGELOG.
- `PROJECT_STATE.md` is updated only when project state meaningfully changes.

---

# Development Workflow

Every task follows this lifecycle:

1. Design
2. Code
3. Tests
4. Documentation
5. Review
6. Git
7. Roadmap update
8. Project state update, only when milestone changes

A task is not complete until all relevant steps are done.

---

# Next Recommended Steps

1. Commit DX-005 changes if not already committed.
2. Ensure roadmap marks all Sprint 4 tasks complete.
3. Replace `docs/development/project_state.md` with this updated file.
4. Commit the Sprint 4 project-state update.
5. Start Sprint 5.
6. Implement `REQUEST-001 Streaming responses`.

---

# How To Continue In A New Chat

Paste this file or upload it and say:

> Continue the Python AI Toolkit from this project state.

The next task should be:

```text
REQUEST-001 Streaming responses
```

---

# Last Updated

2026-07-11
