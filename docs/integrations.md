# Django, FastAPI, and CLI Integrations

Python AI Toolkit provides optional adapters for Django and FastAPI plus an
installed `ai-toolkit` console command.

The integrations reuse the same provider-independent clients and request
lifecycle as ordinary Python code. They do not move application routes, views,
schemas, permissions, transactions, or business decisions into the toolkit.

## Capability summary

| Integration | Configuration source | Public entry points | Network use |
| --- | --- | --- | --- |
| Django | `AI_TOOLKIT` Django setting | `get_django_ai_config()`, `get_ai_client()`, `get_async_ai_client()` | Client creation is local; requests contact the provider |
| FastAPI | Environment or `.env` through the core clients | `AIClientDependency`, `AsyncAIClientDependency`, `get_ai_client()`, `get_async_ai_client()` | Dependency creation is local; requests contact the provider |
| CLI request | Environment or `.env` | `ai-toolkit ask` | Contacts the provider |
| CLI configuration | Environment or `.env` | `ai-toolkit config show`, `ai-toolkit config validate` | Does not contact the provider |

The Django setting and environment configuration paths are alternatives. The
Django adapter constructs an explicit `AIConfig`; it does not merge missing
values from `.env`.

## Installation

Install from the project root after activating a Python 3.11-or-newer virtual
environment.

Framework support is the intersection of the toolkit's Python range, the
extra's dependency constraint, and the selected framework release's own Python
support. See the [compatibility guide](compatibility.md) for the declared and
verified version boundaries.

For Django:

```bash
python -m pip install ".[django]"
```

For FastAPI:

```bash
python -m pip install ".[fastapi]"
```

Install both extras when one environment needs both integrations:

```bash
python -m pip install ".[django,fastapi]"
```

The core installation already provides the CLI:

```bash
python -m pip install .
ai-toolkit --help
```

Installing an extra provides the framework dependency. It does not create a
Django project, FastAPI application, provider account, API key, or model
access.

## Django

### Configure `AI_TOOLKIT`

Add an `AI_TOOLKIT` mapping to the Django settings module:

```python
import os

AI_TOOLKIT = {
    "provider": "openai",
    "api_key": os.environ["OPENAI_API_KEY"],
    "model": "gpt-5.4-mini",
    "embedding_model": "text-embedding-3-small",
    "max_retries": 1,
    "file_logging_enabled": False,
}
```

Keep credentials outside source control. Django may obtain the value from the
deployment environment or an application-owned secret manager.

`api_key` is the only field that the adapter requires to be present in the
mapping. Omitted fields use `AIConfig` defaults, not `.env` values.

Supported fields are:

| Field | Default when omitted |
| --- | --- |
| `api_key` | Required |
| `provider` | `openai` |
| `model` | `gpt-5.4-mini` |
| `embedding_model` | `text-embedding-3-small` |
| `embedding_dimensions` | Provider default |
| `input_cost_per_1m_tokens` | `None`; executor uses a built-in model price when available |
| `output_cost_per_1m_tokens` | `None`; executor uses a built-in model price when available |
| `max_retries` | `1` |
| `log_level` | `INFO` |
| `log_file_path` | `logs/ai_toolkit.log` |
| `file_logging_enabled` | `True` |

The adapter strips and lowercases a string `provider`, strips and uppercases a
string `log_level`, and strips a string `log_file_path`. It rejects unknown
fields rather than silently ignoring likely spelling mistakes.

Unlike direct `AIConfig` construction, `get_django_ai_config()` validates the
result before returning it:

```python
from ai.integrations.django import get_django_ai_config

config = get_django_ai_config()
```

This validates configuration structure. It does not construct a provider,
authenticate credentials, verify model access, or make a network request.

### Create a synchronous client

Use `get_ai_client()` in synchronous Django code such as a service function,
view, management command, or Celery task:

```python
from pydantic import BaseModel

from ai.integrations.django import get_ai_client


class TicketAnalysis(BaseModel):
    category: str
    priority: str
    summary: str


def analyze_support_ticket(message: str) -> TicketAnalysis:
    client = get_ai_client()
    result = client.ask(
        prompt=(
            "Analyze this support ticket and return its category, "
            f"priority, and summary:\n\n{message}"
        ),
        response_type=TicketAnalysis,
    )
    return result.data
```

The helper reads and validates the Django setting, then passes the resulting
explicit configuration to `AIClient`.

### Create an asynchronous client

Use `get_async_ai_client()` only from async-aware application code:

```python
from ai.integrations.django import get_async_ai_client


async def summarize_message(message: str) -> str:
    client = get_async_ai_client()
    result = await client.ask(f"Summarize this message:\n\n{message}")
    return result.data
```

Choosing `AsyncAIClient` makes the provider request asynchronous. It does not
make synchronous Django code, ORM operations, or other blocking application
work asynchronous.

### Use a custom setting name

All three helpers accept a setting name:

```python
from ai.integrations.django import get_ai_client

client = get_ai_client("CUSTOM_AI_CONFIG")
```

The named Django setting must follow the same mapping and validation contract
as `AI_TOOLKIT`.

### Django lifecycle and errors

Every call to `get_ai_client()` or `get_async_ai_client()` reads the setting and
constructs a new client. The adapter does not cache a singleton or manage an
application-wide client lifecycle.

Invalid integration configuration raises `AIConfigurationError`. Examples
include:

- a missing setting
- a non-mapping value
- a missing `api_key`
- an unsupported field
- an invalid retry, embedding, logging, or required string value

Provider registration is checked later, during client construction. Credentials
and model access are checked only when the provider performs a request.

Django decides how exceptions become HTTP responses, task failures, retries, or
user-facing messages. Detailed toolkit exception guidance belongs to
the [exception and error-handling guide](error_handling.md).

## FastAPI

The FastAPI integration provides dependency factories and reusable `Annotated`
aliases:

| Entry point | Injected type | Configuration |
| --- | --- | --- |
| `get_ai_client()` | `AIClient` | Environment or `.env` |
| `get_async_ai_client()` | `AsyncAIClient` | Environment or `.env` |
| `AIClientDependency` | `Annotated[AIClient, Depends(get_ai_client)]` | Environment or `.env` |
| `AsyncAIClientDependency` | `Annotated[AsyncAIClient, Depends(get_async_ai_client)]` | Environment or `.env` |

### Asynchronous endpoint

Use `AsyncAIClientDependency` when the endpoint awaits the AI request:

```python
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from ai.integrations.fastapi import AsyncAIClientDependency

app = FastAPI()


class TicketRequest(BaseModel):
    message: str


class TicketAnalysis(BaseModel):
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str


@app.post("/analyze-ticket", response_model=TicketAnalysis)
async def analyze_ticket(
    request: TicketRequest,
    client: AsyncAIClientDependency,
) -> TicketAnalysis:
    result = await client.ask(
        prompt=f"Analyze this support ticket:\n\n{request.message}",
        response_type=TicketAnalysis,
    )
    return result.data
```

Set provider configuration before starting the application:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
```

Run the repository example from the project root:

```bash
python -m pip install uvicorn
uvicorn examples.20_fastapi_integration:app --reload
```

The `fastapi` extra does not select or install an ASGI server. Uvicorn is shown
for this local example; an application may choose another compatible server and
owns its production deployment configuration.

### Synchronous endpoint

`AIClientDependency` is available for a synchronous endpoint:

```python
from fastapi import FastAPI

from ai.integrations.fastapi import AIClientDependency

app = FastAPI()


@app.get("/summary")
def summary(client: AIClientDependency) -> dict[str, str]:
    result = client.ask("Summarize dependency injection in one sentence.")
    return {"summary": result.data}
```

Application code should deliberately choose the client matching its execution
model. The integration does not automatically convert between synchronous and
asynchronous calls.

### Override dependencies in tests

Override the dependency factory, not the `Annotated` alias:

Repository contributors receive the current compatible test-client dependency
through the `dev` extra:

```bash
python -m pip install -e ".[dev]"
```

Applications that use `TestClient` should declare their own compatible testing
dependency rather than assume the `fastapi` runtime extra supplies one.

```python
from types import SimpleNamespace

from fastapi.testclient import TestClient

from ai.integrations.fastapi import get_async_ai_client


class FakeAsyncAIClient:
    async def ask(self, prompt: str, response_type=None):
        return SimpleNamespace(
            data={
                "category": "technical",
                "priority": "low",
                "summary": "Deterministic test response",
            }
        )


app.dependency_overrides[get_async_ai_client] = FakeAsyncAIClient
test_client = TestClient(app)
```

For a structured endpoint, the fake should return data compatible with the
endpoint's declared response model. Tests can thereby verify routing, request
validation, prompt construction, and response mapping without credentials,
network access, or a provider call.

Clear overrides when a shared application object is reused across tests:

```python
app.dependency_overrides.clear()
```

### FastAPI lifecycle and errors

The supplied factories create environment-configured clients when FastAPI
resolves the dependency. They do not provide an application-wide singleton,
custom lifespan hook, or explicit shutdown behavior. Applications that need a
different lifetime or explicit configuration can define their own dependency
factory and still inject `AIClient` or `AsyncAIClient`.

FastAPI owns conversion of toolkit exceptions into HTTP responses. The adapter
does not install exception handlers, authentication, authorization, rate
limits, timeouts, retries for the HTTP caller, or background-job behavior.

## Command-line interface

Installing the core package exposes:

```text
ai-toolkit
```

The CLI uses the same environment and `.env` resolution path as `AIClient()`.
It does not read Django's `AI_TOOLKIT` setting.

### Send a plain-text request

```bash
ai-toolkit ask "Explain dependency injection simply."
```

`ask`:

1. joins the prompt arguments with spaces
2. constructs a synchronous `AIClient`
3. sends one plain-text request
4. prints only `AIResult.data` to standard output

The command does not expose structured-response selection, streaming, async
requests, tools, images, embeddings, or `AIResult` metadata.

Quote prompts containing spaces so the shell passes them predictably.

### Show resolved configuration

```bash
ai-toolkit config show
```

The output includes:

- provider and request model
- embedding model and optional dimensions
- maximum retries
- logging level, path, and file-logging state
- optional input and output token prices
- a masked API key

Keys of four characters or fewer are hidden completely. For longer keys, only
the final four characters are shown. Treat configuration output as sensitive
operational information even though the full key is not printed.

`config show` loads and structurally validates the environment configuration.
It does not construct a client, query the provider registry, or make a network
request.

### Validate resolved configuration

```bash
ai-toolkit config validate
```

Success prints:

```text
Configuration is structurally valid. Provider credentials were not verified.
```

The command checks the same structure as `get_ai_config()`. It does not:

- authenticate the API key
- confirm that the selected provider is registered
- confirm model access
- test connectivity
- send an AI request

It also cannot inspect a Django `AI_TOOLKIT` setting or an `AIConfig` object
constructed inside application code.

### Output and exit codes

| Situation | Standard output | Standard error | Exit code |
| --- | --- | --- | --- |
| Successful command | Response or configuration information | Empty | `0` |
| Expected `AIError` | Empty | `Error: <message>` | `1` |
| Invalid command syntax | `argparse` help may be displayed | `argparse` usage/error | `2` |

Expected toolkit errors are converted to concise CLI errors without a
traceback. Unexpected exceptions are not swallowed; they remain visible as
programming or integration defects.

This behavior makes exit codes usable in scripts, but the current CLI offers
human-readable output only. Machine-readable output, live provider health
checks, interactive setup, and shell completion remain future work.

## Boundaries shared by all integrations

- Framework installation does not configure credentials or verify model
  access.
- Client construction validates or consumes configuration and constructs a
  provider; only requests establish live connectivity.
- Provider registration and model capability support remain separate concerns.
- Framework adapters do not move business validation or policy into the
  toolkit.
- The application owns authentication, authorization, rate limits, transaction
  boundaries, exception-to-response mapping, and observability around the
  integration.
- The current helpers do not define an application-wide client lifecycle.

See the [installation guide](installation.md) for extras, the
[configuration guide](configuration.md) for precedence and validation, the
[provider guide](providers.md) for registration and capabilities, and the
[request guide](requests.md) for request and result contracts. The
[compatibility guide](compatibility.md) documents Python, dependency,
framework, provider SDK, account, region, and model-capability boundaries. The
[exception and error-handling guide](error_handling.md) documents framework
propagation, CLI behavior, retry boundaries, and failures returned as result
objects. The [security and secret-handling guide](security.md) covers
credential sources, terminal output, HTTP exposure, logging, tenant isolation,
and incident response.
