# Python AI Toolkit

A reusable AI engineering toolkit for Python developers.

The goal of this project is to provide clean, reusable building blocks for integrating Large Language Models (LLMs) into Python applications.

Instead of scattering AI code across projects, this toolkit centralizes configuration, provider integrations, validation, logging, and future AI capabilities behind a consistent interface.

---

## Philosophy

The LLM is only one part of an AI application.

Business logic should remain in Python.

```text
Application
        │
        ▼
 AI Toolkit
        │
        ▼
 AI Provider
        │
        ▼
 Language Model
```

The toolkit is responsible for:

- communicating with AI providers
- validating responses
- tracking usage
- handling retries
- exposing a clean developer API

Applications remain responsible for business logic.

---

# Current Features

## AI Client

Single entry point for all AI requests.

```python
from ai.client import AIClient

ai = AIClient()

response = ai.ask(...)
```

---

## Fluent Request Builder

For simple requests, use `AIClient.ask()`:

```python
from ai.client import AIClient

ai = AIClient()

result = ai.ask("Explain dependency injection in one paragraph.")
```

For advanced requests, use the fluent request builder:

```python
from ai.client import AIClient

ai = AIClient()

result = (
    ai.request()
    .prompt("Explain dependency injection in one paragraph.")
    .execute()
)

print(result.data)
```

Structured responses also work through the builder:

```python
from pydantic import BaseModel

from ai.client import AIClient


class Recommendation(BaseModel):
    title: str
    reason: str


ai = AIClient()

result = (
    ai.request()
    .prompt("Recommend one beginner Python project.")
    .response_type(Recommendation)
    .execute()
)

print(result.data.title)
```

The builder is intentionally mutable. Each method updates the current builder and returns `self`, which allows method chaining.

Request execution is still handled by `RequestExecutor`.

---

## Prompt Templates

Prompt templates provide a reusable way to build prompts by substituting named variables into a template.

```python
from ai.client import AIClient
from ai.prompts import PromptTemplate

template = PromptTemplate(
    "Summarize this article in {language}: {article}"
)

prompt = template.render(
    language="English",
    article="Python is popular.",
)

ai = AIClient()

result = ai.ask(prompt)

print(result.data)
```

Prompt templates are ideal for reusable prompts that differ only by input values.

For prompts assembled dynamically from multiple sections, use `PromptBuilder`.

---

## Provider Architecture

Current:

- OpenAI

Planned:

- Anthropic
- Google Gemini
- Ollama
- Azure OpenAI
- Custom providers

---

## Structured Responses

Supports returning validated Pydantic models instead of raw text.

```python
recommendation = ai.ask(
    prompt=prompt,
    response_type=DrinkRecommendation,
)

print(recommendation.data.recommended_item)
```

---

## Automatic Validation

Responses are validated using Pydantic schemas.

Invalid JSON and schema mismatches raise custom exceptions.

---

## Retry

Structured responses are automatically retried using the configured retry count if validation fails.

---

## Logging

Each request is logged with:

- request id
- model
- duration
- retry count
- token usage
- estimated cost

Prompts and model responses are not logged by default.

---

## Token Usage

Provider token usage is tracked and returned with every request.

---

## Cost Estimation

Supports configurable token pricing for estimating request cost.

---

## Custom Exceptions

Includes dedicated exception hierarchy.

Examples:

- `AIConfigurationError`
- `AIProviderError`
- `AIJSONParseError`
- `AISchemaValidationError`

---

# Current Project Structure

```text
python-ai-toolkit/

├── ai/
│   ├── client.py
│   ├── config.py
│   ├── cost.py
│   ├── exceptions.py
│   ├── executor.py
│   ├── logger.py
│   ├── parser.py
│   ├── prompts.py
│   ├── request_builder.py
│   ├── schemas.py
│   └── providers/
│       ├── base.py
│       ├── factory.py
│       └── openai_provider.py
│
├── docs/
│   ├── architecture/
│   └── development/
│
├── examples/
│
├── tests/
│
├── logs/
│
└── README.md
```

## Configuration Validation

Configuration is validated when `AIClient` loads the toolkit settings.

The toolkit fails early with `AIConfigurationError` when configuration is invalid.

Currently validated:

- provider is not empty
- API key is not empty
- model is not empty
- retry count is zero or greater

Example:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini
AI_MAX_RETRIES=1
```

Invalid configuration raises an error before an AI request is sent.

```python
from ai.client import AIClient
from ai.exceptions import AIConfigurationError

try:
    ai = AIClient()
except AIConfigurationError as exc:
    print(f"Invalid AI configuration: {exc}")
```


## Why this documentation matters

Configuration validation affects application startup behavior. Developers need to know that:

```python
AIClient()
```
may raise:
```python
AIConfigurationError
```
before any request is made.

That is intentional fail-fast behavior.

---

# Installation

Clone the repository.

```bash
git clone https://github.com/<your-username>/python-ai-toolkit.git
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env`.

```env
AI_PROVIDER=openai

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini

# Optional generic fallback for custom providers
AI_API_KEY=
AI_MODEL=

AI_MAX_RETRIES=1

AI_INPUT_COST_PER_1M_TOKENS=
AI_OUTPUT_COST_PER_1M_TOKENS=
```

---

# Development

Run tests.

```bash
python -m pytest
```

Format code.

```bash
python -m black .
```

Lint code.

```bash
python -m ruff check .
```

---

# Roadmap

## Core

- [x] Configuration management
- [x] Provider abstraction
- [x] Provider factory
- [x] Provider registry
- [x] Provider registration API
- [x] Provider configuration cleanup
- [x] OpenAI provider
- [x] AI client
- [x] Fluent request builder
- [x] Prompt builder
- [x] Prompt templates
- [x] Structured responses
- [x] Schema validation
- [x] Retry
- [x] Logging
- [x] Token tracking
- [x] Cost estimation
- [x] Request IDs

---

## Planned

- [ ] Example gallery
- [ ] Configuration validation improvements
- [ ] Better error messages
- [ ] Streaming responses
- [ ] Async client
- [ ] Tool calling
- [ ] Image inputs
- [ ] Conversation memory
- [ ] Embeddings
- [ ] Vector store abstraction
- [ ] RAG pipeline
- [ ] Agent framework
- [ ] Workflow engine
- [ ] Django integration
- [ ] FastAPI integration
- [ ] PyPI package

---

# Design Principles

- Single Responsibility Principle
- Dependency Inversion
- Composition over inheritance
- Strong typing
- Reusable components
- Clear interfaces
- Production-oriented architecture

---

# License

MIT
