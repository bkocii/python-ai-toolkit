# ADR-0008

## Title

Introduce separate async AI client

---

## Status

Accepted

---

## Date

2026-07-19

---

## Context

The toolkit originally exposed a synchronous `AIClient`.

Sprint 5 added async request support.

There were two possible public API directions:

- add async methods directly to `AIClient`
- introduce a separate `AsyncAIClient`

Async behavior affects how applications call the toolkit, how providers are implemented, and how request execution is tested.

Mixing sync and async methods inside one client would make the public API less clear and could encourage incorrect usage in event-loop based applications.

---

## Decision

Introduce a separate `AsyncAIClient`.

Synchronous applications use:

```python
from ai.client import AIClient

ai = AIClient()
result = ai.ask("Hello")
```

Asynchronous applications use:

```python
from ai.async_client import AsyncAIClient

ai = AsyncAIClient()
result = await ai.ask("Hello")
```

Async execution is handled by `AsyncRequestExecutor`.

Providers that support async requests implement:

```python
async def ask_text_async(self, prompt: str) -> ProviderResponse:
    ...
```

The synchronous `AIClient` remains unchanged for existing users.

---

## Alternatives Considered

### Add `ask_async()` to `AIClient`

Rejected because it would mix sync and async usage in one public client.

That would make the API less obvious and could lead to confusing application code.

### Make all client methods async

Rejected because many scripts, examples, tests, and simple applications do not need async behavior.

Forcing async everywhere would make simple use cases more complex.

### Keep async support provider-only

Rejected because applications need a clean public async entry point.

Exposing async only at the provider level would bypass the client and executor architecture.

---

## Consequences

### Positive

- Sync and async APIs are clearly separated.
- Existing `AIClient` usage remains stable.
- Async applications have a dedicated client.
- Async request lifecycle can evolve independently.
- Tests can verify sync and async behavior separately.

### Negative

- Some logic is duplicated between `RequestExecutor` and `AsyncRequestExecutor`.
- Documentation must explain when to use each client.
- Future features may need both sync and async implementations.

---

## Related Files

- `ai/client.py`
- `ai/async_client.py`
- `ai/executor.py`
- `ai/async_executor.py`
- `ai/providers/base.py`
- `ai/providers/openai_provider.py`
- `tests/test_async_client.py`
