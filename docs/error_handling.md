# Exceptions and Error Handling

Python AI Toolkit uses a small exception hierarchy for failures that the
toolkit can classify consistently. It does not replace every Python,
Pydantic, file-system, framework, or application exception with a toolkit
exception.

This guide explains:

- which toolkit exception is raised for each supported failure category
- when to catch a specific exception or the common `AIError` base class
- which failures may be repaired or retried
- which APIs return failed result objects instead of raising
- which errors remain owned by the application

## Exception hierarchy

Import public toolkit exceptions from `ai.exceptions`:

```python
from ai.exceptions import (
    AIConfigurationError,
    AIError,
    AIJSONParseError,
    AIProviderError,
    AISchemaValidationError,
)
```

The hierarchy is:

```text
AIError
├── AIConfigurationError
├── AIProviderError
├── AIJSONParseError
└── AISchemaValidationError
```

All four concrete exceptions inherit from `AIError`.

| Exception | Meaning | Typical source |
| --- | --- | --- |
| `AIError` | Common base class for classified toolkit failures | Application or CLI catch boundary |
| `AIConfigurationError` | Missing, invalid, duplicate, or unsupported toolkit configuration | Environment loading, `ConfigValidator`, Django settings, provider factory |
| `AIProviderError` | Provider request, provider response, or unsupported provider capability failure | OpenAI adapter or default optional `BaseAIProvider` methods |
| `AIJSONParseError` | A structured response is not valid JSON | Structured-response parser after repair attempts are exhausted |
| `AISchemaValidationError` | Valid JSON does not match the requested Pydantic model | Structured-response parser after repair attempts are exhausted |

Use the most specific exception when the application has a different recovery
path for that failure. Use `AIError` at a boundary where all expected toolkit
failures receive the same treatment.

## Catch expected toolkit failures

Catch subclasses before the base class:

```python
from ai.client import AIClient
from ai.exceptions import (
    AIConfigurationError,
    AIError,
    AIJSONParseError,
    AIProviderError,
    AISchemaValidationError,
)


def generate_summary(text: str) -> str:
    try:
        result = AIClient().ask(f"Summarize this text:\n\n{text}")
        return result.data
    except AIConfigurationError:
        # Deployment or startup configuration needs correction.
        raise
    except AIProviderError:
        # The application decides whether this particular provider failure
        # is transient, user-visible, or terminal.
        raise
    except (AIJSONParseError, AISchemaValidationError):
        # These occur only for structured requests after configured repair
        # attempts are exhausted.
        raise
    except AIError:
        # Future toolkit exception subclasses still reach this boundary.
        raise
```

This example re-raises after classification because the correct HTTP response,
task retry, fallback, alert, or user message belongs to the application.

Do not use `except Exception: pass`. It hides programming defects and can make a
failed AI operation look successful.

## Configuration errors

`AIConfigurationError` is raised before a live provider request when the
toolkit can identify invalid local configuration.

Examples include:

- a missing environment API key
- non-string or blank provider, API key, request model, or embedding model
  values
- a non-integer or negative retry count
- non-integer or non-positive embedding dimensions
- incomplete, non-numeric, negative, or non-finite custom token pricing
- an unsupported logging level
- an empty log path while file logging is enabled
- an unsupported or duplicate provider registration name
- invalid Django `AI_TOOLKIT` settings

Environment configuration returned by `get_ai_config()` is structurally
validated automatically:

```python
from ai.config import get_ai_config
from ai.exceptions import AIConfigurationError

try:
    config = get_ai_config()
except AIConfigurationError as exc:
    raise RuntimeError("AI configuration must be corrected before startup.") from exc
```

A manually constructed `AIConfig` is validated automatically by both client
constructors. It can also be validated earlier, without constructing a client:

```python
from ai.config import AIConfig
from ai.config_validator import ConfigValidator

config = AIConfig(
    provider="openai",
    api_key="application-supplied-value",
    model="gpt-5.4-mini",
    max_retries=1,
)

ConfigValidator.validate(config)
```

Structural validation does not authenticate credentials, contact the provider,
confirm model access, check quota, or prove that a model supports a requested
capability. Those checks occur only when the corresponding provider operation
runs.

Configuration errors normally require a deployment, settings, or application
fix. Repeating the same request with unchanged configuration is not a useful
retry strategy.

Malformed provider-returned tool arguments and embedding index sets are
reported separately as `AIProviderError`. They are provider-response failures,
not local configuration failures; the built-in adapter rejects them before
returning incorrectly typed tool data or misassociated embedding metadata.

## Provider errors

`AIProviderError` represents provider-side operations that the toolkit adapter
can classify, including:

- provider SDK request failures
- authentication, quota, connectivity, or model-access failures reported by
  the provider SDK
- unsupported optional capabilities
- invalid tool-call arguments returned by the provider
- invalid embedding inputs or provider-returned embedding indices

The built-in OpenAI adapter converts `OpenAIError` into `AIProviderError` and
preserves the SDK exception as `__cause__` through Python exception chaining.
Provider-facing text is still provider-specific; applications should depend on
the toolkit exception type rather than parsing its message.

Custom providers should perform the same translation for expected SDK
failures:

```python
from ai.exceptions import AIProviderError
from ai.providers.base import BaseAIProvider
from ai.schemas import ProviderResponse


class VendorSDKError(Exception):
    pass


class ExampleProvider(BaseAIProvider):
    def ask_text(self, prompt: str) -> ProviderResponse:
        try:
            raise VendorSDKError("request rejected")
        except VendorSDKError as exc:
            raise AIProviderError("Example provider request failed.") from exc
```

The request executors log and re-raise `AIError`. They do not wrap every
unexpected exception raised by a custom provider. A `TypeError`, `AttributeError`,
or another unclassified exception may therefore propagate unchanged, which
keeps provider implementation defects visible.

### Decide retries from the actual failure

`AIProviderError` does not mean that a retry is always safe or useful.
Authentication failures, unsupported capabilities, invalid inputs, and unknown
models usually require correction. Timeouts, rate limits, or temporary service
failures may be retryable according to provider guidance and application
policy.

`AIConfig.max_retries` does not retry provider transport failures. It controls
only structured-response repair requests. A provider SDK may also apply its own
transport retries independently.

## Structured-response errors and repair

Structured requests distinguish two output failures:

- `AIJSONParseError`: the model text cannot be decoded as JSON
- `AISchemaValidationError`: JSON decoding succeeds, but Pydantic validation
  fails

```python
from pydantic import BaseModel

from ai.exceptions import AIJSONParseError, AISchemaValidationError
from ai.parser import parse_json_response


class Product(BaseModel):
    name: str
    price: float


try:
    product = parse_json_response(
        '{"name": "Espresso"}',
        Product,
    )
except AIJSONParseError:
    print("The response was not JSON.")
except AISchemaValidationError:
    print("The JSON did not contain a valid product.")
```

For `AIClient.ask()`, `AsyncAIClient.ask()`, and structured image requests, the
executor catches these two exceptions and may request a corrected response.
When `max_retries` is exhausted, the final parse or schema exception is
re-raised and no `AIResult` is returned.

The parse and schema exception messages identify the failure category without
including the raw provider response. This prevents the executor's exception
logging from copying a malformed response body into the normal toolkit log.
Because JSON and Pydantic validation failures hold the rejected response, the
toolkit suppresses those content-bearing lower-level causes at this boundary.
Applications should preserve that boundary in their own exception mapping.

Repair does not apply to:

- plain-text requests
- streaming
- tool calls
- embeddings
- provider authentication or transport failures
- application business rules

A structured image repair uses a plain-text repair request and does not resend
the image.

## Errors outside the toolkit hierarchy

Public APIs also use ordinary exceptions when a problem belongs to Python input,
data-model, file-system, or application behavior.

| Failure | Current behavior |
| --- | --- |
| Missing request-builder prompt | `ValueError` |
| Blank prompt-template input or missing template variable | `ValueError` |
| Blank agent, retriever, RAG, workflow, or orchestrator input | `ValueError` |
| Vector dimension mismatch | `ValueError` |
| Missing document file or directory | `FileNotFoundError` |
| Wrong document path kind | `ValueError` |
| File decoding or reading failure | Native file-system exception |
| Invalid Pydantic model construction in application code | Pydantic `ValidationError` |
| Custom provider constructor or implementation defect | Original Python exception may propagate |
| Application business or authorization rule | Application-defined exception |

These exceptions are not subclasses of `AIError`, so a catch for `AIError` will
not hide them.

For example, vector dimensions are application data, not provider transport:

```python
from ai.vector_store import InMemoryVectorStore, VectorRecord

store = InMemoryVectorStore()
store.add(
    [
        VectorRecord(
            id="doc-1",
            text="Redis is an in-memory data store.",
            vector=[1.0, 0.0, 0.0],
        )
    ]
)

try:
    store.similarity_search([1.0, 0.0])
except ValueError as exc:
    print(f"Vector input is invalid: {exc}")
```

Do not convert every ordinary exception into `AIProviderError`. Keeping input,
provider, and business failures distinct allows the application to choose the
correct recovery.

## Raised exceptions versus failed result objects

Not every failure is represented by a raised exception.

| API | Failure contract |
| --- | --- |
| `AIClient` / `AsyncAIClient` request methods | Classified toolkit failures are raised |
| `AIClient.stream()` | Failure is raised while the iterator is consumed; partial output may already exist |
| `Agent.run()` | Underlying exceptions propagate; the user message already added to memory remains |
| `WorkflowEngine.run()` | Step exceptions are converted to `WorkflowStepResult(success=False, error=...)` |
| `MultiAgentOrchestrator.run_agent()` | Known-agent execution exceptions become `AgentRunResult(success=False, error=...)` |
| `MultiAgentOrchestrator.run_sequence()` | Stops after a failed known agent; an unknown agent name raises `ValueError` |

Always inspect `result.success` for workflow and orchestration results. A
function returning a result object is not proof that the operation succeeded.
The returned `error` fields contain strings, not typed exceptions.

Workflow and orchestration failure handling does not roll back memory, shared
state, database writes, files, tool execution, or network side effects.
Applications own transaction and compensation behavior.

## Streaming errors

`AIClient.stream()` is lazy. Put the iteration itself inside the `try` block:

```python
from ai.client import AIClient
from ai.exceptions import AIProviderError

client = AIClient()

try:
    for chunk in client.stream("Summarize the report."):
        print(chunk, end="", flush=True)
except AIProviderError as exc:
    print(f"\nStreaming stopped: {exc}")
```

Creating the iterator does not consume the provider response. A failure may
occur before the first chunk or after partial text has already been emitted.
The stream does not return an `AIResult`, so application code does not receive
request metadata through the return value.

## Framework and CLI boundaries

Django and FastAPI helpers do not convert toolkit exceptions into HTTP
responses. Applications decide which failures become client errors, service
errors, task retries, or internal logs.

Avoid returning raw provider or configuration messages directly to untrusted
clients. Log diagnostic detail in an application-controlled channel and return
a stable public message appropriate to the framework. The dedicated security
guide covers secret-handling policy in more detail.

The command-line interface has a narrower boundary:

| CLI outcome | Behavior |
| --- | --- |
| Success | Exit code `0` |
| Exception derived from `AIError` | `Error: <message>` on standard error; exit code `1` |
| Invalid command syntax | `argparse` error; exit code `2` |
| Unexpected non-toolkit exception | Not swallowed; traceback remains visible |

## Logging and exception chaining

Synchronous and asynchronous request executors log classified `AIError`
failures with the generated request ID and model, then re-raise the same
exception. Prompt and response content are intentionally excluded from executor
logs.

When translating a lower-level exception, use `raise ... from exc`. Exception
chaining keeps the original cause available for debugging without changing the
public catch boundary:

```python
try:
    raise TimeoutError("provider timed out")
except TimeoutError as exc:
    raise AIProviderError("Provider request timed out.") from exc
```

Application logging should avoid duplicating the same traceback at every layer.
Choose one operational boundary to log a failure, then re-raise or convert it
according to application policy.

## Recovery guide

| Failure | Typical application response |
| --- | --- |
| `AIConfigurationError` | Correct settings; normally fail startup or deployment validation |
| `AIProviderError` | Classify the provider cause; retry only failures known to be transient |
| `AIJSONParseError` | Repair is already exhausted; use fallback behavior or report an output-format failure |
| `AISchemaValidationError` | Repair is already exhausted; review schema/prompt or use a safe fallback |
| Input `ValueError` | Correct caller input; do not retry unchanged input |
| File-system exception | Correct path, permissions, encoding, or file availability |
| Failed workflow/orchestration result | Inspect executed results and partial state; compensate application side effects if required |
| Business-policy failure | Enforce the application rule; do not ask toolkit schema validation to replace authorization |
| Unexpected exception | Keep it visible, investigate the defect, and avoid treating it as a normal provider outage |

## Testing error paths

Test exception types and result contracts, not only message text:

```python
import pytest

from ai.exceptions import AIJSONParseError
from ai.parser import parse_json_response
from pydantic import BaseModel


class Answer(BaseModel):
    value: str


def test_invalid_json_raises_toolkit_parse_error():
    with pytest.raises(AIJSONParseError):
        parse_json_response("not json", Answer)
```

Check exact text only when the wording is itself part of the developer
experience, such as a CLI message or a configuration correction. Provider SDK
messages can vary across versions and should not become an application
protocol.

## Related documentation

- [Public API reference](api_reference.md) lists the complete supported surface
  and its raised-versus-returned failure boundaries.
- [Configuration guide](configuration.md) explains structural validation and
  explicit configuration.
- [Provider guide](providers.md) explains registration and optional capability
  errors.
- [Request guide](requests.md) explains structured repair semantics.
- [Advanced request guide](advanced_requests.md) explains streaming and
  capability failures.
- [Retrieval and RAG guide](retrieval.md) explains embedding and vector
  boundaries.
- [Orchestration guide](orchestration.md) explains returned failure objects and
  partial state.
- [Framework and CLI guide](integrations.md) explains framework propagation and
  CLI exit codes.
- [Security and secret-handling guide](security.md) explains safe public error
  mapping, log exposure, secret rotation, and incident response.
- [Developer error-message guidelines](development/error_messages.md) define
  the style expected when toolkit maintainers add or change errors.
