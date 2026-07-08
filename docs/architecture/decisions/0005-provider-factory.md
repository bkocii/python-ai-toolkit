# ADR-0005

## Title

Introduce ProviderFactory for provider creation

---

## Status

Accepted

---

## Date

2026-07-07

---

## Context

`AIClient` previously selected the provider directly.

This worked while only one provider existed, but it would cause `AIClient` to grow every time a new provider was added.

Example:

```python
if provider == "openai":
    ...
elif provider == "anthropic":
    ...
elif provider == "gemini":
    ...
```

That would violate the Single Responsibility Principle and make `AIClient`
responsible for provider construction.

---

## Decision

Introduce `ProviderFactory`.

`AIClient` now delegates provider creation to:

```python
ProviderFactory.create(config)
```

The factory returns an object implementing `BaseAIProvider`.

---

## Alternatives Considered

### Keep provider selection inside AIClient

Rejected because it would make `AIClient` grow as providers are added.

### Instantiate providers directly in application code

Rejected because applications should depend on the toolkit API, not provider implementations.

---

## Consequences

### Positive

- `AIClient` remains small.
- Provider construction is centralized.
- Adding providers becomes easier.
- The architecture better follows the Open/Closed Principle.

### Negative

- Adds one more internal abstraction.

---

## Related Files

- `ai/client.py`
- `ai/providers/factory.py`
- `ai/providers/base.py`
