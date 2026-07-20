# ADR-0014

## Status

Accepted

---

## Date

2026-07-20

---

## Context

`AIClient` and `AsyncAIClient` currently load configuration directly from environment variables through `get_ai_config()`.

This works for standalone Python applications, but framework integrations may use their own configuration systems. Django applications commonly define application configuration through `django.conf.settings`.

A Django integration must be able to construct toolkit clients from Django settings without mutating process-wide environment variables, duplicating provider creation logic, or introducing Django dependencies into the core toolkit.

The same configuration boundary may later be reused by other integrations, tests, command-line applications, and explicitly configured application instances.

---

## Decision

`AIClient` and `AsyncAIClient` will accept an optional `AIConfig` instance through their constructors.

When no configuration is provided, the clients will preserve their current behavior and load configuration through `get_ai_config()`.

```python
client = AIClient()
```

Explicit configuration may be provided when configuration originates outside environment variables.

```python
client = AIClient(config=config)
```

Framework integrations will translate framework-specific settings into the provider-independent `AIConfig` model.

The Django integration will:

* read configuration from Django settings,
* construct an `AIConfig`,
* validate it through `ConfigValidator`,
* pass it into `AIClient` or `AsyncAIClient`.

Core modules will not import Django or other application frameworks.

Framework integrations will not modify environment variables.

---

## Alternatives Considered

* Modify `get_ai_config()` to read Django settings.

  Rejected because it would make core configuration dependent on an optional web framework and violate separation of concerns.

* Temporarily write Django settings into `os.environ`.

  Rejected because environment variables are process-global, create hidden side effects, complicate tests, and are unsafe when multiple configurations are used.

* Create a separate Django-specific client implementation.

  Rejected because it would duplicate client construction and request behavior already owned by `AIClient` and `AsyncAIClient`.

* Require Django applications to configure all toolkit values through environment variables.

  Rejected because it would not provide a meaningful Django integration and would prevent applications from using Django's established settings mechanism.

---

## Consequences

Positive

* Existing `AIClient()` and `AsyncAIClient()` behavior remains compatible.
* Framework integrations remain outside the core architecture.
* Configuration can be injected explicitly in applications and tests.
* Django, FastAPI, CLI, and future integrations can reuse the same boundary.
* Provider creation remains centralized in `ProviderFactory`.
* Configuration validation remains centralized in `ConfigValidator`.
* No process-global environment mutation is required.

Negative

* The public client constructors gain an additional parameter.
* Client construction now has two supported configuration sources.
* Documentation must clearly explain environment-based and explicit configuration.
* Framework adapters must translate their settings into `AIConfig`.

---

## Related Files

* `ai/config.py`
* `ai/config_validator.py`
* `ai/client.py`
* `ai/async_client.py`
* `ai/integrations/django/config.py`
* `ai/integrations/django/client.py`
* `tests/test_client.py`
* `tests/test_async_client.py`
* `tests/test_django_integration.py`
