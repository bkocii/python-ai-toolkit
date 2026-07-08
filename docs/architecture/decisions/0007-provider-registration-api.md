# ADR-0007

## Title

Introduce provider registration API

---

## Status

Accepted

---

## Date

2026-07-07

---

## Context

The toolkit already has a provider registry used by `ProviderFactory`.

Initially, the registry existed only as an internal lookup table.

That allowed provider lookup, but did not provide a clean way to register additional providers.

Future providers should be addable without modifying `AIClient`.

---

## Decision

Add a provider registration API to `ProviderFactory`.

Providers can be registered using:

```python
ProviderFactory.register("custom", CustomProvider)
```

The factory also exposes:

```python
ProviderFactory.available_providers()
```

to list registered providers.

The registry is owned by `ProviderFactory` as class-level state.

---

## Alternatives Considered

### Automatic provider discovery

Rejected for now because it adds unnecessary complexity.

Automatic discovery is more useful for plugin ecosystems. The current project only needs explicit provider registration.

### Keep registry as module-level dictionary

Rejected because provider registration and lookup should be encapsulated by the factory.

---

## Consequences

### Positive

- Providers can be registered explicitly.
- Provider lookup remains centralized.
- `AIClient` remains unchanged when providers are added.
- The design prepares the toolkit for future plugin-style extensions.

### Negative

- The factory now manages class-level state.
- Tests that register providers must clean up after themselves.

---

## Related Files

- `ai/providers/factory.py`
- `tests/test_provider_factory.py`