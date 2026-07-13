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

---

## Structured Outputs

Structured outputs allow the toolkit to return validated Pydantic models instead of plain text.

```python
from pydantic import BaseModel

from ai.client import AIClient


class Answer(BaseModel):
    summary: str
    confidence: float


ai = AIClient()

result = ai.ask(
    prompt="Summarize dependency injection in one sentence.",
    response_type=Answer,
)

print(result.data.summary)
print(result.data.confidence)
```

When `response_type` is provided, the toolkit:

- builds a schema-aware prompt
- asks the model to return valid JSON
- parses the raw response
- validates the response with Pydantic
- retries once when JSON parsing or schema validation fails, depending on `AI_MAX_RETRIES`

The structured-output logic is centralized in:

```text
ai/structured.py
```

This keeps structured prompt construction and structured response parsing separate from request execution.

The same structured-output behavior is used by:

- `AIClient.ask(...)`
- `AsyncAIClient.ask(...)`
- `AIClient.ask_with_images(...)`

Example with image input:

```python
from pydantic import BaseModel

from ai.client import AIClient
from ai.images import ImageInput


class ImageDescription(BaseModel):
    subject: str
    colors: list[str]
    visible_text: str | None = None


ai = AIClient()

result = ai.ask_with_images(
    prompt="Extract structured information from this image.",
    images=[
        ImageInput(
            source=(
                "https://api.nga.gov/iiif/"
                "a2e6da57-3cd1-4235-b20e-95dcaefed6c8/"
                "full/!800,800/0/default.jpg"
            ),
        )
    ],
    response_type=ImageDescription,
)

print(result.data.subject)
print(result.data.colors)
```

Current structured-output support:

- Pydantic response models
- schema-aware prompt generation
- JSON parsing
- Pydantic validation
- repair retry for invalid JSON or schema mismatch
- sync requests
- async requests
- image requests with structured responses

Not yet supported:

- provider-native strict structured output
- OpenAI `response_format` integration
- streaming structured output
- partial structured validation while streaming

Provider-native strict structured output may be added later without changing the public `response_type` API.

---

## Streaming Responses

For plain text responses, you can stream chunks as they arrive.

```python
from ai.client import AIClient

ai = AIClient()

for chunk in ai.stream("Explain dependency injection in one short paragraph."):
    print(chunk, end="", flush=True)

print()
```

Streaming is useful when you want to show output immediately instead of waiting for the full response.

Current streaming support:

* plain text responses
* synchronous iteration
* provider-level streaming through `stream_text()`

Not yet supported:

* structured streaming
* async streaming
* token usage metadata during streaming

Structured responses should still use:

```python
ai.ask(..., response_type=...)
```

`ai.stream(...)` returns streamed text chunks as an iterator, not a full `AIResult`.

---

## Async AI Client

For async Python applications, use `AsyncAIClient`.

```python
import asyncio

from ai.async_client import AsyncAIClient


async def main() -> None:
    ai = AsyncAIClient()

    result = await ai.ask(
        "Explain dependency injection in one short paragraph."
    )

    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
```

Structured responses also work with the async client.

```python
import asyncio

from pydantic import BaseModel

from ai.async_client import AsyncAIClient


class Summary(BaseModel):
    title: str
    key_point: str


async def main() -> None:
    ai = AsyncAIClient()

    result = await ai.ask(
        prompt="Summarize dependency injection.",
        response_type=Summary,
    )

    print(result.data.title)
    print(result.data.key_point)


if __name__ == "__main__":
    asyncio.run(main())
```

Use `AIClient` for synchronous applications.

Use `AsyncAIClient` for asynchronous applications, such as FastAPI apps, async workers, or other event-loop based systems.

Current async support:

* plain text requests
* structured responses
* retry for structured responses
* full `AIResult` return values

Not yet supported:

* async streaming
* async fluent request builder
* async tool calling

---

## Tool Calling

Tool calling allows the model to request external capabilities, such as searching documents, checking weather, querying a database, or calling an application service.

The toolkit defines tools in a provider-independent way.

```python
from ai.client import AIClient
from ai.tools import ToolDefinition

ai = AIClient()

weather_tool = ToolDefinition(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, for example Paris or London.",
            }
        },
        "required": ["location"],
        "additionalProperties": False,
    },
)

response = ai.ask_with_tools(
    prompt="What is the weather in Paris?",
    tools=[weather_tool],
)

for tool_call in response.tool_calls:
    print(tool_call.name)
    print(tool_call.arguments)
```

Tool calling currently returns requested tool calls to the application.

The toolkit does **not** automatically execute tools.

That means application code remains responsible for deciding whether and how to run a requested tool.

```python
for tool_call in response.tool_calls:
    if tool_call.name == "get_weather":
        location = tool_call.arguments["location"]
        # Application decides what to do next.
```

Current tool-calling support:

* provider-independent `ToolDefinition`
* provider-independent `ToolCall`
* provider-independent `ToolResponse`
* OpenAI tool-call adapter
* requested tool calls returned to the application

Not yet supported:

* automatic tool execution
* submitting tool results back to the model
* multi-step agent loops
* parallel tool execution
* async tool calling

Automatic tool execution belongs later in the Agents and Workflows roadmap.


---

## Image Inputs

Image inputs allow the toolkit to send one or more images together with a text prompt.

The public API uses provider-independent `ImageInput` objects.

```python
from ai.client import AIClient
from ai.images import ImageInput

ai = AIClient()

image = ImageInput(
    source=(
        "https://api.nga.gov/iiif/"
        "a2e6da57-3cd1-4235-b20e-95dcaefed6c8/"
        "full/!800,800/0/default.jpg"
    ),
)

result = ai.ask_with_images(
    prompt="Describe this image in one short paragraph.",
    images=[image],
)

print(result.data)
```

Structured responses are also supported.

```python
from pydantic import BaseModel

from ai.client import AIClient
from ai.images import ImageInput


class ImageDescription(BaseModel):
    subject: str
    colors: list[str]
    visible_text: str | None = None


ai = AIClient()

result = ai.ask_with_images(
    prompt="Extract structured information from this image.",
    images=[
        ImageInput(
            source=(
                "https://api.nga.gov/iiif/"
                "a2e6da57-3cd1-4235-b20e-95dcaefed6c8/"
                "full/!800,800/0/default.jpg"
            ),
        )
    ],
    response_type=ImageDescription,
)

print(result.data.subject)
print(result.data.colors)
```

Current image-input support:

- image URL input
- Base64 data URL input
- multiple images
- plain text responses
- structured Pydantic responses
- OpenAI Responses API adapter

Not yet supported:

- local file helper
- OpenAI file ID helper
- async image input
- streaming image input
- image generation
- image editing

### Note about image URLs

When using image URLs, the model provider must be able to download the image.

Some public image hosts block automated downloads, redirects, or hotlinking. If a URL fails with an error like `Error while downloading file`, try another public image URL or use a Base64 data URL instead.


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
