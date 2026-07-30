# Python AI Toolkit

Python AI Toolkit provides reusable, provider-independent building blocks for
adding Large Language Model (LLM) capabilities to Python applications.

It keeps provider communication, response validation, retries, usage metadata,
logging, retrieval, and workflow primitives behind consistent interfaces so
application business logic can remain in Python.

> **Project status:** Version `1.0.0` is the first stable release. Its public
> API is frozen across the documented Version 1 surface. The built-in provider
> is currently OpenAI; custom providers can be registered through the provider
> abstraction.

## Contents

- [Why use the toolkit?](#why-use-the-toolkit)
- [Installation](#installation)
- [Configuration](#configuration)
- [Providers](#providers)
- [Quick start](#quick-start)
- [Structured responses](#structured-responses)
- [Major capabilities](#major-capabilities)
- [Examples](#examples)
- [Documentation](#documentation)
- [Public API reference](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/api_reference.md)
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

Create and activate a virtual environment:

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

Then install the toolkit from PyPI:

```bash
python -m pip install python-ai-toolkit
```

Add an optional extra only when you need it:

```bash
python -m pip install "python-ai-toolkit[django]"
python -m pip install "python-ai-toolkit[fastapi]"
```

Contributors working from a source checkout should use an editable installation
with the development and benchmark dependencies:

```bash
python -m pip install -e ".[dev,benchmark]"
```

See the [installation guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/installation.md) for the complete extras
matrix, clean-environment verification, and the difference between user and
contributor installations. The
[compatibility guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/compatibility.md) separates the declared Python
range from verified environments, dependency resolution, framework support,
and live provider/model availability.

## Configuration

Copy `.env.example` to `.env`, then set the provider credentials and models:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Never commit `.env` or real API keys.

`AIClient()` loads and structurally validates environment-based configuration.
Configuration can instead be supplied explicitly with `AIConfig`, which is
useful for application factories, framework integrations, and tests:

```python
import os

from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator

config = AIConfig(
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-5.4-mini",
    embedding_model="text-embedding-3-small",
    file_logging_enabled=False,
)

ConfigValidator.validate(config)
client = AIClient(config=config)
```

An explicit `AIConfig` completely replaces environment loading; omitted fields
use dataclass defaults rather than `.env` values. Both client constructors
validate the resolved configuration automatically; the explicit call above is
useful when an application wants an earlier startup check. See the
[configuration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/configuration.md) for the complete variable
reference, defaults, precedence rules, validation boundary, and CLI checks.

The placeholder above is illustrative. Production credentials should come from
environment variables or a secret manager.

## Providers

The built-in provider is OpenAI. Registered providers can be inspected without
making a network request:

```python
from ai.providers.factory import ProviderFactory

print(ProviderFactory.available_providers())
```

Custom providers are registered explicitly before client construction. The
factory uses an exact provider name and a small constructor contract while
`BaseAIProvider` separates required plain-text behavior from optional
capabilities.

See the [provider guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/providers.md) for custom registration, constructor
requirements, capability methods, registration lifecycle, and expected errors.
See the [compatibility guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/compatibility.md) before treating a
registered adapter as proof that a selected model supports a capability.

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

Use `client.ask_text(prompt)` only when the response string is all you need.
See the [request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/requests.md) for the return-value difference,
metadata semantics, and retry boundaries.

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
fails. The [request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/requests.md) explains the complete structured
lifecycle and the boundary between schema validation and application business
rules.

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

Streaming returns chunks rather than `AIResult`, while `AsyncAIClient` currently
supports async plain and structured requests but not async streaming, tools, or
images. See the [advanced request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/advanced_requests.md) for the
return contracts and capability boundaries.

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
must allow-list the tool, validate its arguments, authorize the operation, and
perform any external action. See the
[advanced request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/advanced_requests.md#tool-calling).

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
The source must already be a URL or Base64 data URL; `ImageInput` does not read
local paths. See the
[advanced request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/advanced_requests.md#image-inputs).

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

See the [retrieval and RAG guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/retrieval.md) for embedding return
contracts, batch ordering, vector scores and filters, document-loading
boundaries, RAG metadata, and grounding limitations.

See examples
[10 through 14](https://github.com/bkocii/python-ai-toolkit/blob/main/examples/README.md#10--embeddings) for the complete progression
from embeddings to document-backed RAG. The release-focused
[end-to-end indexing example](https://github.com/bkocii/python-ai-toolkit/blob/main/examples/27_document_indexing_and_rag.py) adds
stable document IDs, batch-order restoration, and deterministic verification
of the complete grounded-answer workflow.

### Memory, agents, and workflows

The orchestration stack remains explicit and composable:

- `InMemoryConversationMemory` stores conversation messages.
- `Agent` combines instructions, an AI client, and memory.
- `WorkflowEngine` runs sequential application-defined steps with shared state.
- `MultiAgentOrchestrator` runs named agents individually or sequentially.

Tool execution, routing, and business decisions remain under application
control. See the
[memory, agents, workflows, and orchestration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/orchestration.md) for
message, state, failure, metadata, persistence, and autonomy boundaries. See
examples
[15 through 18](https://github.com/bkocii/python-ai-toolkit/blob/main/examples/README.md#15--conversation-memory).

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
See the [framework and CLI integration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/integrations.md) for
configuration sources, client lifetimes, dependency overrides, CLI behavior,
and failure boundaries. The
[Django and FastAPI examples](https://github.com/bkocii/python-ai-toolkit/blob/main/examples/README.md#19--django-integration) provide
application-focused starting points.

### Command-line interface

Installing the package exposes the `ai-toolkit` command:

```bash
ai-toolkit --help
ai-toolkit ask "Explain dependency injection simply."
ai-toolkit config show
ai-toolkit config validate
```

Configuration display masks API keys, and structural validation does not contact
the configured provider. The
[framework and CLI integration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/integrations.md#command-line-interface)
documents command scope, output, and exit codes. The
[installation guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/installation.md#verify-the-console-command-on-windows)
includes a local PowerShell verification procedure.

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

See the [exception and error-handling guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/error_handling.md) for the
complete hierarchy, catch boundaries, repair and retry behavior, ordinary
Python exceptions, failed result objects, framework propagation, and CLI error
handling.

### Security

Keep real credentials outside source control and inject them from the process
environment or an application-owned secret manager. Treat prompts, provider
responses, raw result fields, RAG contexts, memory, tool arguments, image data
URLs, CLI output, and provider errors as potentially sensitive.

The [security and secret-handling guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/security.md) covers local,
testing, CI, and production secret sources; repository and logging safety;
provider data governance; tool authorization; multi-tenant boundaries; and
incident response.

## Examples

The [example gallery](https://github.com/bkocii/python-ai-toolkit/blob/main/examples/README.md) provides a numbered learning path:

| Area | Examples |
| --- | --- |
| Requests and prompts | 01–04 |
| Streaming, async, tools, and images | 05–09 |
| Embeddings, vector search, retrieval, and RAG | 10–14 |
| Memory, agents, workflows, and orchestration | 15–18 |
| Django and FastAPI | 19–20 |
| Command-line usage and configuration | 21–22 |
| Explicit application configuration | 23 |
| Custom provider registration | 24 |
| Testing application code with a fake provider | 25 |
| Batch embedding and retrieval | 26 |
| End-to-end document indexing and RAG | 27 |
| Structured application service | 28 |

Network-dependent examples require valid provider configuration. The examples
remain application-focused and keep business logic intentionally small.
Every gallery entry identifies its file or command, demonstrated behavior,
requirements, run instructions, and unsupported or application-owned
boundaries. The catalog also explains why command workflows 21–22, the
example-09 Base64 variant, and the two unnumbered legacy modules retain their
existing names. All example modules and command workflows are covered by
deterministic current-public-API regressions; live provider behavior remains a
separate explicit smoke-test boundary.

## Documentation

Use the root README for orientation and first use. The repository keeps deeper
concerns in focused documents:

| Document | Purpose |
| --- | --- |
| [Public API reference](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/api_reference.md) | Frozen Version 1.0 import paths, signatures, models, exceptions, behaviors, and compatibility policy |
| [Installation guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/installation.md) | PyPI, local, optional-extra, and contributor installation |
| [Configuration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/configuration.md) | Environment variables, defaults, precedence, explicit configuration, and validation |
| [Provider guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/providers.md) | Built-in provider, custom registration, constructor contract, capabilities, and errors |
| [Request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/requests.md) | Plain and structured requests, `AIResult`, parsing, validation, and repair |
| [Advanced request guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/advanced_requests.md) | Streaming, async requests, tool calling, image inputs, and capability limits |
| [Retrieval and RAG guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/retrieval.md) | Embeddings, vector storage, retrieval, document loading, RAG responses, and grounding limits |
| [Orchestration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/orchestration.md) | Memory, agents, workflows, multi-agent sequencing, state, and failure boundaries |
| [Framework and CLI integration guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/integrations.md) | Django settings, FastAPI dependencies and test overrides, CLI commands, output, and exit codes |
| [Exception and error-handling guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/error_handling.md) | Toolkit exception hierarchy, retry decisions, ordinary Python failures, failed result objects, and application catch boundaries |
| [Security and secret-handling guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/security.md) | Credentials, sensitive data, logging, provider governance, tool authorization, and incident response |
| [Compatibility guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/compatibility.md) | Python versions, dependency resolution, provider SDKs and models, optional frameworks, and verification evidence |
| [Release procedure](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/releasing.md) | Maintainer preflight, version tags, protected PyPI approval, installed-package smoke tests, release notes, and recovery |
| [Example gallery](https://github.com/bkocii/python-ai-toolkit/blob/main/examples/README.md) | Numbered, runnable usage examples |
| [Architecture](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/architecture/architecture.md) | Components, boundaries, and request flows |
| [Architecture decisions](https://github.com/bkocii/python-ai-toolkit/tree/main/docs/architecture/decisions) | Reasons behind important design choices |
| [Benchmark guide](https://github.com/bkocii/python-ai-toolkit/blob/main/benchmarks/README.md) | Running and interpreting deterministic benchmarks |
| [Profiling report](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/development/performance_profiling.md) | Performance evidence and optimization decisions |
| [Roadmap](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/development/roadmap.md) | Active and planned development |
| [Project state](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/development/project_state.md) | Current milestone and implemented capabilities |
| [Changelog](https://github.com/bkocii/python-ai-toolkit/blob/main/CHANGELOG.md) | User-visible changes by version |

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

The same installation and test boundary runs automatically on every GitHub
push and pull request through `.github/workflows/ci.yml`. Independent jobs use
Python `3.11`, `3.12`, `3.13`, and `3.14`; each installs `.[dev]` from
`pyproject.toml`, runs `python -m pip check`, disables toolkit-managed file
logging, checks Black formatting, runs Ruff, and runs the normal test suite.
After every matrix job succeeds, a separate read-only job builds the wheel and
source distribution, validates both with strict Twine and project-specific
archive checks, and retains the validated files as the
`python-package-distributions` workflow artifact.

Run its current functional equivalent locally:

```bash
python -m pip install -e ".[dev]"
python -m pip check
python -m black --check .
python -m ruff check .
python -m pytest -q
python -m pip install build twine
python -m build
python -m twine check --strict dist/*
python scripts/validate_distributions.py
```

See the [compatibility guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/compatibility.md) for the tested-version
matrix and local multi-version procedure. CI uploads the distributions only
after both validation commands pass. Ordinary pushes and pull requests never
publish packages, and the CI workflow requires only read access to repository
contents.

An explicit version tag starts the production path in the separate release
workflow. The tag must exactly match the package version in `pyproject.toml`;
for example, version `1.0.0` requires tag `v1.0.0`. A manual
non-production rehearsal can run the same validation, supported-version
quality matrix, build, validators, and artifact retention from a selected
commit without creating a tag. Manual runs always skip the publishing job.

For a real tag, a final isolated job downloads the validated files and
publishes them through PyPI trusted publishing. Only that job can request a
short-lived identity token; the repository stores no PyPI password or API
token. The protected `pypi` environment can require manual approval before
upload. See the [installation guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/installation.md#configure-trusted-pypi-publishing)
for the one-time account configuration and the
[release procedure](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/releasing.md) for the complete maintainer checklist,
safe rehearsal, verification, and recovery path.

Format and lint:

```bash
python -m black .
python -m ruff check .
```

Run the isolated benchmark suite:

```bash
python -m pytest benchmarks --benchmark-only
```

Build the local wheel and source distribution:

```bash
python -m pip install build
python -m build
```

Benchmark methodology and comparison rules are documented in
[`benchmarks/README.md`](https://github.com/bkocii/python-ai-toolkit/blob/main/benchmarks/README.md).
The [installation guide](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/installation.md#build-distributions-locally)
explains the generated files, clean Windows build steps, and the boundary
between building and validating a release.

## Project status

The current stable package version is `1.0.0`.

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

See the authoritative [roadmap](https://github.com/bkocii/python-ai-toolkit/blob/main/docs/development/roadmap.md) instead of
maintaining a second roadmap in this README.

## Design principles

- business logic remains in the application
- provider-specific behavior stays behind provider interfaces
- public APIs return typed, inspectable results
- explicit control is preferred over hidden autonomous behavior
- composition is preferred over inheritance
- correctness and maintainability outweigh small performance gains

## License

Python AI Toolkit is released under the [MIT License](https://github.com/bkocii/python-ai-toolkit/blob/main/LICENSE).

This permissive license allows use, modification, redistribution, and
commercial use, including inside closed-source applications. Copies or
substantial portions of the toolkit must retain the copyright and license
notice. The software is provided without warranty.
