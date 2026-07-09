# Project State

## Project

Python AI Toolkit

## Current Version

0.3.0-dev

## Current Milestone

Sprint 3 completed — Provider Infrastructure

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

---

## Sprint 3 – Provider Infrastructure

Status: Completed

### Goal

Support multiple AI providers without changing application code.

### Completed Tasks

- PROVIDER-001 ProviderFactory
- PROVIDER-002 Provider registry
- PROVIDER-003 Provider Registration API
- PROVIDER-004 Provider configuration cleanup

### Exit Criteria

- Adding a new provider requires no changes to AIClient.

---

# Next Sprint

## Sprint 4 – Developer Experience

### Goal

Improve usability for developers.

### Next Task

DX-001 Fluent Request Builder

---

# Implemented

- Provider-based architecture
- OpenAI provider
- `AIClient`
- `RequestExecutor`
- `ProviderFactory`
- Provider registry
- Provider Registration API
- Provider-aware configuration loading
- Prompt builder
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
- Parser tests
- Prompt builder tests
- Request executor tests
- Retry behavior test
- Provider factory tests
- Provider configuration tests

---

# Current Architecture

```text
Application
    ↓
AIClient
    ↓
RequestExecutor
    ↓
ProviderFactory
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
- `AIClient` delegates provider creation to `ProviderFactory`.
- Provider lookup is handled through a provider registry.
- Additional providers can be registered through the Provider Registration API.
- Provider configuration is loaded in a provider-aware way.
- `RequestExecutor` owns the request lifecycle.
- Structured responses use Pydantic models.
- `AIResult` returns both validated data and metadata.
- Prompts and responses are not logged by default for privacy.
- Business logic must stay outside the toolkit.
- Retry behavior is configurable and currently applies to structured responses.
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
```

---

# Current Technical Debt

- Retry behavior is implemented but can be improved with a dedicated retry strategy object.
- Cost table is still a scaffold and should eventually use verified provider pricing.
- Provider selection currently supports only OpenAI as a built-in provider.
- Error handling around non-toolkit exceptions can be improved.
- Logging currently writes only to a file.
- Streaming and async support are not yet implemented.

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

1. Commit Sprint 3 provider infrastructure updates.
2. Start Sprint 4.
3. Implement `DX-001 Fluent Request Builder`.
4. Add tests for the fluent request builder.
5. Update roadmap after completing DX-001.

---

# How To Continue In A New Chat

Paste this file or upload it and say:

> Continue the Python AI Toolkit from this project state.

The next task should be:

```text
DX-001 Fluent Request Builder
```

---

# Last Updated

2026-07-08
