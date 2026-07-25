# Plain and Structured Requests

`AIClient` exposes two simple synchronous request styles:

- plain requests return model text
- structured requests parse model text into a validated Pydantic model

Both styles use the same provider-independent execution path and can return
request metadata through `AIResult`.

Streaming, asynchronous requests, tool calling, and image inputs are documented
separately because their return types and execution boundaries differ.

## Choose the request method

| Call | Return value | Use when |
| --- | --- | --- |
| `client.ask(prompt)` | `AIResult[str]` | You want plain text and request metadata |
| `client.ask_text(prompt)` | `str` | You want only plain text |
| `client.ask(prompt, response_type=MyModel)` | `AIResult[MyModel]` | You want parsed and Pydantic-validated data |

`ask_text()` is a backward-compatible convenience method. It calls `ask()` and
returns only `result.data`; the request still goes through the normal executor,
but its metadata is not returned to the caller.

Prefer `ask()` for application code that needs request IDs, timing, token usage,
cost estimates, retry information, or raw responses.

## Plain request

```python
from ai.client import AIClient

client = AIClient()
result = client.ask("Explain dependency injection in one short paragraph.")

print(result.data)
print(result.request_id)
print(result.duration_ms)
```

For a plain request:

- `result.data` is the provider's response text
- no JSON parsing or Pydantic response validation occurs
- structured-response repair retries do not apply
- `result.retries_used` is `0`

Use `ask_text()` when the text is the only value the application needs:

```python
from ai.client import AIClient

client = AIClient()
text = client.ask_text("Give one benefit of dependency injection.")

print(text)
```

## Structured request

Pass a Pydantic model class—not a model instance—as `response_type`:

```python
from pydantic import BaseModel, Field

from ai.client import AIClient


class ProductSummary(BaseModel):
    name: str
    category: str
    confidence: float = Field(ge=0, le=1)


client = AIClient()
result = client.ask(
    prompt=(
        "Extract a product summary: "
        "Genius Green is a kiwi mocktail with confidence 0.92."
    ),
    response_type=ProductSummary,
)

summary = result.data
print(summary.name)
print(summary.category)
print(summary.confidence)
```

The return type is `AIResult[ProductSummary]`, and `result.data` is an actual
`ProductSummary` instance.

## What `response_type` does

The structured request path is provider-independent:

1. The toolkit obtains the model's JSON schema with
   `response_type.model_json_schema()`.
2. It adds that schema and a JSON-only instruction to the prompt.
3. The provider returns text.
4. The toolkit parses the complete text with `json.loads()`.
5. Pydantic validates the parsed value with `response_type.model_validate()`.
6. The validated model is returned in `AIResult.data`.

The parser expects the complete response to be valid JSON. Markdown code fences,
commentary around the JSON, malformed JSON, or data that violates the Pydantic
model is not accepted as a successful structured response.

Pydantic behavior still applies. Field types, required fields, constraints,
nested models, aliases, and custom validators can all participate in response
validation.

## `AIResult` reference

| Field | Meaning |
| --- | --- |
| `data` | Plain `str` or the validated Pydantic model |
| `model` | Request model configured on the client |
| `request_id` | Unique identifier generated for this toolkit request |
| `duration_ms` | Executor time from the first provider call through text handling, including structured parsing and any repair attempts |
| `retries_used` | Number of structured-response repair requests after the initial request |
| `token_usage` | Provider-reported input, output, and total tokens when available |
| `estimated_cost_usd` | Estimated cost when token usage and usable price information are available |
| `original_raw_response` | Text from the first provider response |
| `raw_response` | Final response text used for the returned result |

When no structured repair occurs, `original_raw_response` and `raw_response`
contain the same text. After a successful repair, the original field preserves
the invalid first response while `raw_response` contains the accepted repaired
response.

Token usage is optional because not every provider response supplies it. When a
structured request is repaired, available usage from the initial and repair
responses is aggregated. A cost estimate is metadata, not a billing guarantee;
the provider's billing records remain authoritative.

`duration_ms` does not represent complete application latency. It excludes
client construction and application work performed before or after `ask()`.

## Parsing, validation, and repair

Two structured-response failures are distinguished:

- `AIJSONParseError`: the response is not valid JSON
- `AISchemaValidationError`: the JSON is valid but does not match the Pydantic
  model

When either failure occurs and a retry is available, the toolkit sends a repair
prompt containing:

- the original schema-aware prompt
- the invalid response
- an instruction to return only corrected JSON

The provider produces a new response, which is parsed and validated again. This
is a provider request, not a local JSON-rewriting algorithm.

`AI_MAX_RETRIES` or `AIConfig.max_retries` controls how many repair requests are
allowed after the initial structured request:

| Value | Maximum provider calls for one structured request |
| --- | --- |
| `0` | 1 initial call, no repair |
| `1` | 1 initial call and up to 1 repair call |
| `2` | 1 initial call and up to 2 repair calls |

If the final allowed response still fails, the corresponding parse or schema
validation exception is raised. No `AIResult` is returned.

Repair retries are only for structured response parsing and schema validation.
They do not retry plain-text requests, authenticate invalid credentials, select
a different model, restore network connectivity, or correct application
business rules. Provider SDKs may have their own transport retry behavior; that
is separate from `AIConfig.max_retries`.

## Toolkit validation versus business validation

Pydantic validation proves that returned data has the shape and constraints the
application requested. It does not prove that the model's claims are true or
that an action is allowed.

```python
from decimal import Decimal

from pydantic import BaseModel, Field

from ai.client import AIClient


class RefundSuggestion(BaseModel):
    approve: bool
    amount: Decimal = Field(ge=0)
    reason: str


client = AIClient()
result = client.ask(
    prompt=(
        "Suggest whether to approve a refund. "
        "The customer requested USD 45 for a delayed order."
    ),
    response_type=RefundSuggestion,
)

suggestion = result.data
refundable_balance = Decimal("30.00")

if suggestion.approve and suggestion.amount > refundable_balance:
    raise ValueError("Suggested refund exceeds the refundable balance.")
```

The toolkit can validate that `amount` is a non-negative decimal. The
application must still verify the order, customer identity, permissions,
refund policy, available balance, and whether human approval is required.

Treat structured output as validated input to business logic—not as permission
to perform an external action.

## Choosing plain or structured output

Use plain text for:

- explanations and summaries intended for people
- drafts and conversational responses
- cases where the exact prose is the product

Use structured output for:

- extraction into application fields
- classification into known categories
- scores with explicit ranges
- data passed to deterministic Python logic

Structured output improves shape consistency, but it does not guarantee factual
accuracy. Add application checks whenever correctness depends on external data,
permissions, money, security, or irreversible actions.

## Related documentation

- [Advanced requests](advanced_requests.md) covers streaming, async requests,
  tool calling, image inputs, and their different return contracts.
- [Configuration](configuration.md) explains retry configuration and client
  construction.
- [Providers](providers.md) explains provider registration and capability
  boundaries.
- [Example gallery](../examples/README.md) starts with plain and structured
  request scripts.
- [Architecture](architecture/architecture.md) describes the request layers.
