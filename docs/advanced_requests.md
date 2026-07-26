# Advanced Requests

This guide covers the request surfaces whose execution and return contracts
differ from the ordinary synchronous `AIClient.ask()` path:

- synchronous streaming
- asynchronous plain and structured requests
- tool calling
- image inputs

These capabilities are provider-independent at the toolkit interface. A
registered provider and the selected model must still support the capability
used by an application.

## Capability matrix

| Capability | Public call | Return value | Current client |
| --- | --- | --- | --- |
| Plain streaming | `AIClient.stream()` | `Iterator[str]` | Synchronous only |
| Async plain request | `await AsyncAIClient.ask()` | `AIResult[str]` | Asynchronous |
| Async text shortcut | `await AsyncAIClient.ask_text()` | `str` | Asynchronous |
| Async structured request | `await AsyncAIClient.ask(..., response_type=Model)` | `AIResult[Model]` | Asynchronous |
| Tool request | `AIClient.ask_with_tools()` | `ToolResponse` | Synchronous only |
| Plain image request | `AIClient.ask_with_images()` | `AIResult[str]` | Synchronous only |
| Structured image request | `AIClient.ask_with_images(..., response_type=Model)` | `AIResult[Model]` | Synchronous only |

`AsyncAIClient` does not currently expose streaming, tool-calling, image-input,
or embedding methods. `AIClient` does not turn synchronous streaming into async
streaming.

## Synchronous streaming

`AIClient.stream()` returns an iterator of text chunks:

```python
from ai.client import AIClient

client = AIClient()

for chunk in client.stream("Explain Python generators briefly."):
    print(chunk, end="", flush=True)

print()
```

The provider request begins when the iterator is consumed. Keep the iteration
inside error handling if the application needs to handle provider failures:

```python
from ai.exceptions import AIProviderError

try:
    for chunk in client.stream("Summarize the report."):
        print(chunk, end="", flush=True)
except AIProviderError as exc:
    print(f"Streaming failed: {exc}")
```

Chunks are provider-produced text fragments. Do not assume that one chunk is
one token, word, sentence, or complete JSON value. A provider can also fail
after some chunks have already been emitted, so an application may have
received partial output before the exception.

### Streaming return and metadata boundary

Streaming prioritizes immediate delivery and does not build an `AIResult`.
Application code receives:

```text
Iterator[str]
```

It does not receive the following through the public streaming return value:

- a request ID
- duration
- token usage
- estimated cost
- retry count
- a complete raw response

The executor records success or failure through configured logging, but that
internal operational record does not change the public return contract.
Streaming currently supports plain text only. Structured streaming, response
repair, and partial Pydantic validation are not implemented.

## Asynchronous requests

`AsyncAIClient` is a separate public client for applications that already use
an event loop:

```python
import asyncio

from ai.async_client import AsyncAIClient


async def main() -> None:
    client = AsyncAIClient()
    result = await client.ask("Explain dependency injection briefly.")

    print(result.data)
    print(result.request_id)


if __name__ == "__main__":
    asyncio.run(main())
```

Inside an asynchronous framework endpoint or task, await the client directly
instead of starting another event loop:

```python
async def summarize(client: AsyncAIClient, text: str) -> str:
    result = await client.ask(f"Summarize this text:\n\n{text}")
    return result.data
```

Use `await client.ask_text(prompt)` when only the response string is needed:

```python
text = await client.ask_text("Explain dependency injection briefly.")
```

### Async structured responses

The async client supports the same Pydantic parsing, validation, repair,
metadata, and configured `max_retries` behavior as synchronous `ask()`:

```python
from pydantic import BaseModel


class Summary(BaseModel):
    title: str
    points: list[str]


async def create_summary(client: AsyncAIClient) -> Summary:
    result = await client.ask(
        prompt="Summarize why dependency injection improves testing.",
        response_type=Summary,
    )
    return result.data
```

The provider must implement `ask_text_async()`. A provider that implements only
`ask_text()` remains sync-only and raises `AIProviderError` when used through
`AsyncAIClient`.

Async requests avoid blocking on the provider's network call. They do not make
CPU-bound application work parallel, and they do not add the advanced
capabilities absent from `AsyncAIClient`.

## Tool calling

A `ToolDefinition` tells the model which operation it may request:

```python
from ai.client import AIClient
from ai.tools import ToolDefinition

weather_tool = ToolDefinition(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, for example Paris.",
            }
        },
        "required": ["location"],
        "additionalProperties": False,
    },
)

client = AIClient()
response = client.ask_with_tools(
    prompt="What is the weather in Paris?",
    tools=[weather_tool],
)
```

`ToolDefinition.parameters` is a provider-independent JSON-schema-shaped
dictionary. The built-in OpenAI provider translates it into its provider SDK
format.

The result is a `ToolResponse`:

| Field | Meaning |
| --- | --- |
| `text` | Optional model text |
| `tool_calls` | Zero or more requested `ToolCall` objects |

Each `ToolCall` contains:

| Field | Meaning |
| --- | --- |
| `name` | Requested tool name |
| `arguments` | Provider-returned arguments parsed into a dictionary |
| `call_id` | Optional provider correlation identifier |

A response may contain text, tool calls, both, or neither. Tool requests return
`ToolResponse`, not `AIResult`, so request metadata is not exposed through this
public return value.

### Execution belongs to the application

The toolkit never executes a requested tool:

```python
allowed_tools = {"get_weather"}

for call in response.tool_calls:
    if call.name not in allowed_tools:
        raise ValueError(f"Tool is not allowed: {call.name}")

    location = call.arguments.get("location")

    if not isinstance(location, str) or not location.strip():
        raise ValueError("A non-empty location is required.")

    # Application code may now call its own approved weather service.
```

Application code must:

1. allow-list the tool
2. validate arguments against application rules
3. check identity, permissions, policy, and resource limits
4. request confirmation for sensitive or destructive actions
5. execute the approved operation
6. decide how its result continues the conversation

The toolkit parses provider arguments into a dictionary, but it does not prove
that they are truthful, authorized, safe, or suitable for the application's
business rules. It also does not currently provide an automatic tool loop or a
provider-independent API for submitting tool results back to the model.

## Image inputs

`ImageInput` accepts a remote image URL or a Base64 data URL:

```python
from ai.client import AIClient
from ai.images import ImageInput

client = AIClient()
result = client.ask_with_images(
    prompt="Describe this image in one short paragraph.",
    images=[
        ImageInput(
            source="https://example.com/image.jpg",
        )
    ],
)

print(result.data)
```

`ask_with_images()` accepts a list, so one request can contain multiple images
when the provider and selected model support them.

### Base64 data URLs

`ImageInput` expects an already prepared data URL. It does not read or encode a
local path:

```python
import base64
from pathlib import Path

from ai.images import ImageInput, ImageInputType


def jpeg_to_data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


image = ImageInput(
    source=jpeg_to_data_url(Path("examples/sketch.jpg")),
    type=ImageInputType.BASE64,
)
```

`ImageInputType` describes how the source was supplied. The `source` itself must
still be a complete URL or data URL. The current toolkit does not validate that
the URL is reachable, infer the MIME type, verify Base64 bytes, resize images,
or enforce provider size and format limits.

The optional `detail` value is forwarded to providers that support it:

```python
image = ImageInput(
    source="https://example.com/image.jpg",
    detail="low",
)
```

Accepted detail values and their effects are provider- and model-specific.

### Structured image responses

Pass a Pydantic class as `response_type`:

```python
from pydantic import BaseModel


class ImageDescription(BaseModel):
    subject: str
    colors: list[str]
    visible_text: str | None = None


result = client.ask_with_images(
    prompt="Extract structured information from this image.",
    images=[image],
    response_type=ImageDescription,
)

print(result.data.subject)
```

The return value is `AIResult[ImageDescription]`, with the same metadata and
structured parsing contract described in the
[request guide](requests.md).

If the initial image response contains malformed or schema-invalid JSON, a
configured repair attempt sends the invalid text and schema-aware prompt
through the provider's plain-text request method. The image is not resent
during that formatting repair. If the image needs to be analyzed again rather
than merely reformatted, the application should make a new image request.

## Provider and model support

Registration proves only that a provider can be selected and constructed. It
does not prove support for every advanced capability.

| Toolkit call | Provider method required |
| --- | --- |
| `AIClient.stream()` | `stream_text()` |
| `AsyncAIClient.ask()` | `ask_text_async()` |
| `AIClient.ask_with_tools()` | `ask_with_tools()` |
| `AIClient.ask_with_images()` | `ask_with_images()` |

The default `BaseAIProvider` implementations raise `AIProviderError` with a
capability-specific message. Even when a provider implements the method, its
SDK, selected model, account, image format, tool schema, or regional
availability can still reject the request.

The built-in `OpenAIProvider` implements the synchronous streaming, asynchronous
text, tool-calling, and image-input methods described here. Availability for a
specific model should be verified against current provider documentation.

## Future review boundaries

The current contracts are documented for the Version 1.0 API review and future
improvement work. The roadmap tracks:

- metadata-bearing alternatives for streaming and tool responses
- async streaming, tools, images, and embeddings
- an opt-in structured-image re-analysis path that explicitly resends images
- provider/model capability discovery separate from registration
- application-controlled tool-loop helpers

Application-owned tool execution is an accepted safety boundary, not an
accidental omission. Future helpers must preserve application allow-listing,
argument validation, authorization, and control of external actions rather
than silently executing model-requested tools.

See the [Version 1.0 review and Future Backlog](development/roadmap.md#future-backlog).

## Related documentation

- [Request guide](requests.md) explains `AIResult`, structured validation, and
  repair behavior.
- [Provider guide](providers.md) explains registration and optional capability
  methods.
- [Configuration guide](configuration.md) explains sync and async client
  construction.
- [Security and secret handling](security.md) explains tool authorization,
  image URL and data-URL exposure, CLI safety, and provider governance.
- [Example gallery](../examples/README.md) links the runnable examples numbered
  05 through 09.
- [Architecture](architecture/architecture.md) explains why synchronous and
  asynchronous clients are separate.
