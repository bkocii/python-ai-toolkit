# Architecture

## Purpose

The Python AI Toolkit provides reusable infrastructure for integrating Large Language Models (LLMs) into Python applications.

The toolkit intentionally avoids business logic.

Applications remain responsible for domain-specific decisions, while the toolkit handles AI communication and infrastructure.

---

# Design Philosophy

The toolkit is designed around four principles.

1. Separation of concerns
2. Strong typing
3. Extensibility
4. Provider independence

Every component should have one clearly defined responsibility.

---

# High-Level Architecture

```text
Application
        │
        ▼
AIClient
        │
        ▼
RequestExecutor
        │
        ├──────────────┐
        ▼              ▼
Provider         Prompt Builder
        │
        ▼
Language Model
        │
        ▼
ProviderResponse
        │
        ▼
Parser
        │
        ▼
Pydantic Validation
        │
        ▼
AIResult
        │
        ▼
Application
```

---

# Responsibilities

## AIClient

Responsibilities

- Public API
- Provider selection
- Delegate execution

Does NOT

- Retry requests
- Parse JSON
- Log
- Calculate cost

---

## RequestExecutor

Responsibilities

- Execute requests
- Measure duration
- Retry failed structured responses
- Parse responses
- Validate schemas
- Calculate estimated cost
- Log requests
- Return AIResult

RequestExecutor owns the request lifecycle.

---

## Provider

Responsibilities

Translate toolkit requests into provider-specific SDK calls.

Current implementation

- OpenAI

Future implementations

- Anthropic
- Google Gemini
- Azure OpenAI
- Ollama

Applications should never communicate with providers directly.

---

## Parser

Responsibilities

Convert raw model responses into Python objects.

Parser should know nothing about providers.

---

## Schemas

Responsibilities

Define contracts between AI and Python.

Schemas ensure:

- validation
- autocomplete
- type safety

Applications should work with typed objects instead of raw JSON.

---

## AIResult

AIResult is the standard response object returned by the toolkit.

It contains

- data
- model
- duration
- retries
- request id
- token usage
- estimated cost

This allows future metadata without changing the public API.

---

# Request Lifecycle

```text
Application

↓

AIClient.ask()

↓

RequestExecutor.execute()

↓

Provider.ask_text()

↓

Language Model

↓

ProviderResponse

↓

Parse

↓

Validate

↓

Retry if needed

↓

Create AIResult

↓

Return to application
```

---

# Why Provider Abstraction?

Without abstraction

```text
Application

↓

OpenAI SDK
```

Changing providers would require modifying every application.

With abstraction

```text
Application

↓

Toolkit

↓

Provider Interface

↓

OpenAI
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
```

The API stays stable even as metadata grows.

---

# Why Pydantic?

Pydantic provides

- validation
- type hints
- editor autocomplete
- predictable application behavior

AI should never be trusted without validation.

---

# Logging Strategy

By default

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

Prompts may contain confidential business information.

Future versions may include configurable debug logging.

---

# Current Technical Debt

Known improvements

- Duplicate success logging
- Retry strategy embedded in executor
- Retry count fixed at one
- Provider factory not yet implemented
- Cost table requires automatic updates
- Streaming support missing
- Async support missing

Technical debt is tracked intentionally and should not be ignored.

---

# Long-Term Vision

Current

```text
Application
        ↓
Toolkit
        ↓
OpenAI
```

Future

```text
Application
        ↓
Toolkit
        ↓
Provider Interface
        ↓
OpenAI
Anthropic
Gemini
Ollama
Azure
```

Applications should never need to change when providers change.

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

When making future design decisions, preserving these principles takes priority over adding features quickly.