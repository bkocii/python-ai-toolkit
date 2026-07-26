# Providers

Python AI Toolkit keeps application code independent of a provider SDK through
three components:

- `BaseAIProvider` defines the provider-facing contract.
- `ProviderFactory` owns the process-local provider registry and creates the
  selected implementation.
- `AIClient` and `AsyncAIClient` use the created provider through the common
  interface.

The built-in provider is `openai`.

## Inspect registered providers

`ProviderFactory.available_providers()` returns registered names as a sorted
tuple:

```python
from ai.providers.factory import ProviderFactory

print(ProviderFactory.available_providers())
```

In an unmodified process, the result includes:

```text
('openai',)
```

This reports implementations registered in the current Python process. It does
not inspect installed packages, contact a provider, or validate credentials.

## Register a custom provider

Register a provider class before constructing a client that selects it:

```python
from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.schemas import ProviderResponse


class EchoProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text=f"{self.model}: {prompt}")


ProviderFactory.register("echo", EchoProvider)

config = AIConfig(
    provider="echo",
    api_key="not-used-by-echo",
    model="echo-v1",
    file_logging_enabled=False,
)
ConfigValidator.validate(config)

client = AIClient(config=config)
result = client.ask("Hello")

print(result.data)
```

This example is deterministic and makes no network request.

For the same workflow as a complete runnable module, see
[`examples/24_custom_provider.py`](../examples/24_custom_provider.py). It uses
the real factory and client request lifecycle while keeping the provider local
and deterministic.

Registration changes the factory registry, not environment configuration.
Applications using environment-based configuration must both register the
implementation and select the same name:

```env
AI_PROVIDER=echo
AI_API_KEY=not-used-by-echo
AI_MODEL=echo-v1
AI_FILE_LOGGING_ENABLED=false
```

Provider-specific environment variables such as `ECHO_API_KEY` take precedence
over the generic fallbacks. See the
[configuration guide](configuration.md) for the full resolution order.

## Provider names and registration lifecycle

Provider names are exact registry keys:

- register a provider before creating a client that selects it
- use a stable lowercase name such as `echo` or `acme`
- use the same exact name in registration and an explicit `AIConfig`
- treat registration as application-startup work, not per-request work

Environment-based provider names are stripped and converted to lowercase.
Explicit `AIConfig.provider` values and names passed to
`ProviderFactory.register()` are used as supplied, so lowercase names avoid
surprising mismatches.

The registry is class-level, process-local state. A registration remains
available until the Python process ends or internal state is changed. There is
currently no public unregister or replacement API.

Tests should isolate registry changes with fixtures such as pytest's
`monkeypatch` rather than allowing a test registration to leak into later
tests.

## Constructor contract

`ProviderFactory` constructs a registered provider with keyword arguments.

Every custom provider constructor must accept:

```python
api_key: str
model: str
```

The factory also passes these settings when the constructor explicitly accepts
them or accepts `**kwargs`:

```python
embedding_model: str
embedding_dimensions: int | None
```

A provider supporting embeddings can therefore use:

```python
class EmbeddingProvider(BaseAIProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        embedding_model: str,
        embedding_dimensions: int | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text=prompt)
```

`ProviderFactory` does not pass retry, logging, or token-pricing configuration
into provider constructors. Those settings belong to the client and request
executor layers.

Python type annotations describe the intended registration API, but
`ProviderFactory.register()` does not perform a runtime subclass check. Custom
implementations should inherit `BaseAIProvider`; constructor or interface
mistakes otherwise fail later during provider creation or use.

## Required and optional capabilities

Only synchronous plain-text execution is abstract and required:

| Capability | Provider method | Contract |
| --- | --- | --- |
| Plain text | `ask_text()` | Required; return `ProviderResponse` |
| Async plain text | `ask_text_async()` | Optional |
| Streaming | `stream_text()` | Optional |
| Async streaming | `stream_text_async()` | Optional |
| Tool calling | `ask_with_tools()` | Optional |
| Image input | `ask_with_images()` | Optional |
| Embeddings | `embed_texts()` | Optional |

`BaseAIProvider.embed_text()` already delegates a single input to
`embed_texts()`, so a provider normally implements only the batch embedding
method.

Default optional methods raise `AIProviderError` with a capability-specific
message. Registration therefore means that the provider can be constructed; it
does not claim that every toolkit feature is supported.

The built-in `OpenAIProvider` currently implements synchronous and asynchronous
plain-text requests, synchronous streaming, tool calling, image inputs, and
embeddings. Detailed model and SDK compatibility is handled separately from
the registration contract in the [compatibility guide](compatibility.md).

## Errors and validation boundaries

Registering an existing name raises `AIConfigurationError`. The built-in
`openai` name cannot be replaced through the public registration API:

```python
ProviderFactory.register("openai", EchoProvider)
```

Selecting an unregistered provider raises `AIConfigurationError` when
`ProviderFactory.create()` runs during client construction. The error lists the
currently available provider names.

These checks are separate:

1. `ConfigValidator` checks provider-independent configuration structure.
2. `ProviderFactory` checks whether the selected provider name is registered.
3. A live request checks credentials, connectivity, and model access.

For a manually constructed `AIConfig`, call
`ConfigValidator.validate(config)` before passing it to a client. This manual
step should be reconsidered at the Version 1.0 public-API review so invalid
explicit configuration cannot accidentally bypass the normal validation path.

## What registration does not provide

Provider registration is explicit by design. It does not currently provide:

- automatic provider discovery
- entry-point or plugin loading
- provider replacement or unregistering
- live health checks
- capability negotiation

Those concerns should not be inferred from a name appearing in
`available_providers()`. Registration also does not prove SDK compatibility,
credential validity, account or regional access, or support for a capability
by the selected model.

See the [public API reference](api_reference.md) for the supported provider
extension interface, factory signatures, and direct-adapter boundary.
