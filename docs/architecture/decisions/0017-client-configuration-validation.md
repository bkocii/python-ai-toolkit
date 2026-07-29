# ADR-0017

## Status

Accepted

---

## Date

2026-07-29

---

## Context

Environment-based configuration returned by `get_ai_config()` is validated
before use. A manually constructed `AIConfig`, however, could previously be
passed directly to `AIClient` or `AsyncAIClient` without the same structural
validation.

That difference allowed blank provider names, API keys, models, embedding
models, invalid dimensions, negative repair counts, and invalid logging
settings to reach later construction steps. Depending on the selected provider,
the resulting failure could be less helpful, occur after side effects such as
logger setup, or be accepted accidentally by a custom provider.

Client construction is the public boundary shared by environment-based,
framework-integration, and explicitly supplied configuration. Version 1.0
needs one predictable invariant at that boundary.

---

## Decision

`AIClient` and `AsyncAIClient` will call
`ConfigValidator.validate(resolved_config)` before creating a provider,
configuring logging, or creating an executor.

The rule applies whether configuration was loaded from the environment or
supplied explicitly. Environment-based configuration may therefore be
validated once by `get_ai_config()` and again at the client boundary. The
validation is structural, deterministic, and free of provider or network side
effects, so the duplicate check is acceptable in exchange for a single client
invariant.

Validation does not verify credentials, model availability, provider
capabilities, network access, account permissions, regions, or quotas. Those
remain provider-request concerns.

The constructor signature remains unchanged.

---

## Alternatives Considered

* Keep validation as an application responsibility for explicit configuration.

  Rejected because two inputs to the same public constructor would have
  different safety guarantees, and callers could bypass validation
  accidentally.

* Validate only explicitly supplied configuration.

  Rejected because client construction should enforce one invariant regardless
  of configuration source, including custom environment resolvers used in
  tests or integrations.

* Move validation into `AIConfig.__post_init__()`.

  Rejected because configuration construction and validation are already
  separate responsibilities, and changing dataclass construction would affect
  tests and applications that intentionally create invalid values for
  validation or error-reporting workflows.

* Validate inside `ProviderFactory.create()`.

  Rejected because `ProviderFactory` owns provider registration and
  construction, not logging or other provider-independent client
  configuration.

---

## Consequences

Positive

* Explicit and environment-based configuration receive the same validation.
* Invalid configuration fails before provider, logger, or executor creation.
* Sync and async clients share the same construction guarantee.
* The Version 1.0 client contract has one clear validation boundary.

Negative

* Environment-based client construction performs a small duplicate structural
  validation.
* Applications that previously passed invalid explicit configuration will now
  receive `AIConfigurationError` during client construction.

---

## Related Files

* `ai/client.py`
* `ai/async_client.py`
* `ai/config_validator.py`
* `tests/test_client.py`
* `tests/test_async_client.py`
* `docs/api_reference.md`
* `docs/configuration.md`
* `docs/providers.md`
