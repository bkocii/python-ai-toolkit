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

# Next Sprint

## Sprint 3 – Provider Infrastructure

### Goal

Support multiple AI providers without changing application code.

### Next Task

PROVIDER-001 ProviderFactory

---

# Implemented

- Provider-based architecture
- OpenAI provider
- `AIClient`
- `RequestExecutor`
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

---

# Current Architecture

```text
Application
    ↓
AIClient
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

    development/
        roadmap.md
        project_state.md
```

---

# Current Technical Debt

- Retry behavior is implemented but can be improved with a dedicated retry strategy object.
- Cost table is still a scaffold and should eventually use verified provider pricing.
- Provider selection currently supports only OpenAI.
- Error handling around non-toolkit exceptions can be improved.
- Logging currently writes only to a file.
- ProviderFactory is not yet implemented.
- Provider registry is not yet implemented.
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

1. Commit Sprint 2 documentation updates.
2. Start Sprint 3.
3. Implement `PROVIDER-001 ProviderFactory`.
4. Add tests for provider creation.
5. Update roadmap after completing PROVIDER-001.

---

# How To Continue In A New Chat

Paste this file or upload it and say:

> Continue the Python AI Toolkit from this project state.

The next task should be:

```text
PROVIDER-001 ProviderFactory
```

---

# Last Updated

2026-07-07
