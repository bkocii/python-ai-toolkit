# Python AI Toolkit

Python AI Toolkit provides reusable, provider-independent building blocks for
adding Large Language Model (LLM) capabilities to Python applications.

It keeps provider communication, response validation, retries, usage metadata,
logging, retrieval, and workflow primitives behind consistent interfaces so
application business logic can remain in Python.

> **Project status:** `0.7.0-dev`. Sprint 9 is preparing the toolkit for a
> stable Version 1.0 release. The built-in provider is currently OpenAI; custom
> providers can be registered through the provider abstraction.

## Contents

- [Why use the toolkit?](#why-use-the-toolkit)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick start](#quick-start)
- [Structured responses](#structured-responses)
- [Major capabilities](#major-capabilities)
- [Examples](#examples)
- [Documentation](#documentation)
- [Development](#development)
- [Project status](#project-status)

## Why use the toolkit?

An LLM is only one part of an AI application:

```text
Application
    ↓
Python AI Toolkit
    ↓
AI provider
    ↓
Language model
```

The toolkit handles AI infrastructure:

- synchronous and asynchronous requests
- provider selection and custom provider registration
- plain-text and validated Pydantic responses
- structured-response repair and retries
- streaming, tool calls, and image inputs
- token usage, estimated cost, duration, and request IDs
- embeddings, vector search, retrieval, and RAG
- memory, agents, workflows, and multi-agent orchestration
- Django, FastAPI, and command-line integrations
- configurable application logging

Your application remains responsible for business rules, permissions, data
access, tool execution, and decisions based on model output.

## Installation

Python `3.11` or newer is required.

The project is not published on PyPI yet. From a local source checkout, create
and activate a virtual environment:

```bash
cd python-ai-toolkit
python -m venv .venv
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux or macOS
source .venv/bin/activate
```

Then install the toolkit:

```bash
python -m pip install .
```

Add an optional extra only when you need it:

```bash
python -m pip install ".[django]"
python -m pip install ".[fastapi]"
```

Contributors should use an editable installation with the development and
benchmark dependencies:

```bash
python -m pip install -e ".[dev,benchmark]"
```

See the [installation guide](docs/installation.md) for the complete extras
matrix, clean-environment verification, and the difference between user and
contributor installations.

## Configuration

Copy `.env.example` to `.env`, then set the provider credentials and models:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Never commit `.env` or real API keys.

The toolkit validates configuration before sending a request. Configuration can
also be supplied explicitly with `AIConfig`, which is useful for application
factories, framework integrations, and tests:

```python
import os

from ai.client import AIClient
from ai.config import AIConfig

config = AIConfig(
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-5.4-mini",
    embedding_model="text-embedding-3-small",
    file_logging_enabled=False,
)

client = AIClient(config=config)
```

The placeholder above is illustrative. Production credentials should come from
environment variables or a secret manager.

## Quick start

Create a client and send a plain-text request:

```python
from ai.client import AIClient

client = AIClient()
result = client.ask("Explain dependency injection in one short paragraph.")

print(result.data)
```

`AIClient.ask()` returns `AIResult`, which keeps the response together with
request metadata:

```python
print(result.data)
print(result.model)
print(result.request_id)
print(result.duration_ms)
print(result.retries_used)
print(result.token_usage)
print(result.estimated_cost_usd)
```

## Structured responses

Pass a Pydantic model as `response_type` to receive validated application data:

```python
from pydantic import BaseModel

from ai.client import AIClient


class Recommendation(BaseModel):
    title: str
    reason: str


client = AIClient()
result = client.ask(
    prompt="Recommend one beginner Python project.",
    response_type=Recommendation,
)

print(result.data.title)
print(result.data.reason)
```

The toolkit builds a schema-aware prompt, parses the provider response, validates
it with Pydantic, and can request a repaired response when parsing or validation
fails.

## Major capabilities

### Request construction

`AIClient.ask()` is the simple request API. The fluent builder supports requests
assembled through method chaining:

```python
result = (
    client.request()
    .prompt("Explain dependency injection in one paragraph.")
    .execute()
)
```

Reusable prompt templates are available through `PromptTemplate`:

```python
from ai.prompts import PromptTemplate

template = PromptTemplate("Summarize this article in {language}: {article}")
prompt = template.render(
    language="English",
    article="Python is popular.",
)
```

### Streaming and async requests

Stream plain text as it arrives:

```python
for chunk in client.stream("Explain Python generators briefly."):
    print(chunk, end="", flush=True)
```

Use the separate async client in event-loop-based applications:

```python
import asyncio

from ai.async_client import AsyncAIClient


async def main() -> None:
    client = AsyncAIClient()
    result = await client.ask("Explain Python generators briefly.")
    print(result.data)


asyncio.run(main())
```

### Tool calling

Tools are declared with provider-independent schemas. Requested tool calls are
returned to the application:

```python
from ai.tools import ToolDefinition

weather_tool = ToolDefinition(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string"},
        },
        "required": ["location"],
        "additionalProperties": False,
    },
)

response = client.ask_with_tools(
    prompt="What is the weather in Paris?",
    tools=[weather_tool],
)
```

The toolkit does not automatically execute requested tools. Application code
must authorize and perform any external action.

### Image inputs

Send image URLs or Base64 data URLs through `ImageInput`:

```python
from ai.images import ImageInput

result = client.ask_with_images(
    prompt="Describe this image.",
    images=[ImageInput(source="https://example.com/image.jpg")],
)
```

Plain-text and structured Pydantic responses are supported for image requests.

### Embeddings, retrieval, and RAG

The retrieval stack is composed from separate provider-independent layers:

```text
Documents
    ↓
Embeddings
    ↓
Vector store
    ↓
Retriever
    ↓
RAG pipeline
    ↓
Answer and retrieved contexts
```

Main public components include:

- `AIClient.embed_text()` and `AIClient.embed_texts()`
- `EmbeddingInput` and `EmbeddingResponse`
- `BaseVectorStore` and `InMemoryVectorStore`
- `BaseRetriever` and `VectorStoreRetriever`
- `RAGPipeline` and `RAGResponse`
- `TextFileLoader`, `MarkdownFileLoader`, and `DirectoryLoader`

`InMemoryVectorStore` is a reference implementation for tests, examples, demos,
and small local workflows. Production applications can implement persistent
storage behind `BaseVectorStore`.

See examples
[10 through 14](examples/README.md#10--embeddings) for the complete progression
from embeddings to document-backed RAG.

### Memory, agents, and workflows

The orchestration stack remains explicit and composable:

- `InMemoryConversationMemory` stores conversation messages.
- `Agent` combines instructions, an AI client, and memory.
- `WorkflowEngine` runs sequential application-defined steps with shared state.
- `MultiAgentOrchestrator` runs named agents individually or sequentially.

Tool execution, routing, and business decisions remain under application
control. See examples
[15 through 18](examples/README.md#15--conversation-memory).

### Framework integrations

Django helpers translate an `AI_TOOLKIT` setting into configured synchronous or
asynchronous clients:

```python
from ai.integrations.django import get_ai_client

client = get_ai_client()
```

FastAPI provides dependency aliases for synchronous and asynchronous endpoints:

```python
from ai.integrations.fastapi import AIClientDependency
```

Install the corresponding optional dependency group before using an integration.
See [the Django and FastAPI examples](examples/README.md#19--django-integration).

### Command-line interface

Editable installation exposes the `ai-toolkit` command:

```bash
ai-toolkit ask "Explain dependency injection simply."
ai-toolkit config show
ai-toolkit config validate
```

Configuration display masks API keys, and structural validation does not contact
the configured provider.

### Logging and errors

Toolkit-managed logging records operational metadata rather than prompts or
model responses. Its level, path, and file handler can be configured with:

```env
AI_LOG_LEVEL=INFO
AI_LOG_FILE_PATH=logs/ai_toolkit.log
AI_FILE_LOGGING_ENABLED=true
```

Expected failures use toolkit-specific exceptions such as
`AIConfigurationError`, `AIProviderError`, `AIJSONParseError`, and
`AISchemaValidationError`.

Detailed configuration, error-handling, and security guidance is part of the
active Sprint 9 documentation work.

## Examples

The [example gallery](examples/README.md) provides a numbered learning path:

| Area | Examples |
| --- | --- |
| Requests and prompts | 01–04 |
| Streaming, async, tools, and images | 05–09 |
| Embeddings, vector search, retrieval, and RAG | 10–14 |
| Memory, agents, workflows, and orchestration | 15–18 |
| Django and FastAPI | 19–20 |
| Command-line usage and configuration | 21–22 |

Network-dependent examples require valid provider configuration. The examples
remain application-focused and keep business logic intentionally small.

## Documentation

Use the root README for orientation and first use. The repository keeps deeper
concerns in focused documents:

| Document | Purpose |
| --- | --- |
| [Installation guide](docs/installation.md) | Local installation, optional extras, and contributor setup |
| [Example gallery](examples/README.md) | Numbered, runnable usage examples |
| [Architecture](docs/architecture/architecture.md) | Components, boundaries, and request flows |
| [Architecture decisions](docs/architecture/decisions/) | Reasons behind important design choices |
| [Benchmark guide](benchmarks/README.md) | Running and interpreting deterministic benchmarks |
| [Profiling report](docs/development/performance_profiling.md) | Performance evidence and optimization decisions |
| [Roadmap](docs/development/roadmap.md) | Active and planned development |
| [Project state](docs/development/project_state.md) | Current milestone and implemented capabilities |
| [Changelog](CHANGELOG.md) | User-visible changes by version |

The README should not duplicate the roadmap, architecture, benchmark manual, or
full example catalog.

## Development

Install development dependencies:

```bash
python -m pip install -e ".[dev,benchmark]"
```

Run the normal test suite:

```bash
python -m pytest
```

Format and lint:

```bash
python -m black .
python -m ruff check .
```

Run the isolated benchmark suite:

```bash
python -m pytest benchmarks --benchmark-only
```

Benchmark methodology and comparison rules are documented in
[`benchmarks/README.md`](benchmarks/README.md).

## Project status

The current release line is `0.7.0-dev`.

Completed capability milestones include:

- core request and provider infrastructure
- developer-experience APIs
- advanced request types
- retrieval and RAG
- agents and workflows
- Django, FastAPI, and CLI integrations
- deterministic benchmarks and performance profiling

Sprint 9 focuses on documentation, additional examples, packaging, continuous
integration, security review, API stability, and the Version 1.0 release.

See the authoritative [roadmap](docs/development/roadmap.md) instead of
maintaining a second roadmap in this README.

## Design principles

- business logic remains in the application
- provider-specific behavior stays behind provider interfaces
- public APIs return typed, inspectable results
- explicit control is preferred over hidden autonomous behavior
- composition is preferred over inheritance
- correctness and maintainability outweigh small performance gains

## License

MIT
