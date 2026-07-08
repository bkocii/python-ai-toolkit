# ADR-0006

## Title

Introduce provider registry for provider lookup

---

## Status

Accepted

---

## Date

2026-07-07

---

## Context

`ProviderFactory` originally selected providers using conditional logic.

Example:

```python
if config.provider == "openai":
    return OpenAIProvider(...)
```

This works for one provider, but it does not scale well as additional providers are added.

A long `if/elif/else` chain would make provider lookup harder to maintain.

---

## Decision

Introduce a provider registry.

Providers are mapped by name:

```python
PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
}
```

`ProviderFactory` now looks up the provider class in the registry and instantiates it.

---

## Alternatives Considered

### Keep conditional logic

Rejected because it becomes harder to maintain as providers grow.

### Dynamic import by string

Rejected for now because it adds complexity before it is needed.

---

## Consequences

### Positive

- Provider lookup is centralized.
- Adding providers becomes simpler.
- Factory logic becomes smaller.
- Prepares the project for future provider auto-discovery.

### Negative

- Adds another internal concept developers need to understand.

---

## Related Files

- `ai/providers/factory.py`
- `tests/test_provider_factory.py`