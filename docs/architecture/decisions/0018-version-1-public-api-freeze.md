# ADR-0018

## Status

Accepted

---

## Date

2026-07-29

---

## Context

Python AI Toolkit has completed its planned pre-release capabilities,
documentation, packaging, and release automation. Before Version 1.0, the
project must distinguish supported application contracts from names that are
merely importable because they exist in Python modules.

The existing API reference inventories 71 intended public symbols across
clients, configuration, results, advanced requests, retrieval, orchestration,
provider extensions, integrations, exceptions, parsing, and cost estimation.
It also records several unresolved questions about imports, validation,
implementation exposure, capability discovery, and partial-execution
semantics.

Version 1.0 requires an explicit compatibility boundary. It must remain small,
provider-independent, and honest about synchronous, in-process, mutable, and
partial-failure behavior.

---

## Decision

The 71 symbols listed in `docs/api_reference.md` are the Version 1.0 public
Python surface. Their documented module paths, signatures, model fields,
return contracts, and exception boundaries are compatibility promises.

The package root remains intentionally empty. Version 1.0 uses explicit imports
such as:

```python
from ai.client import AIClient
```

It does not add duplicate `from ai import ...` paths or define `ai.__all__`.

The following boundaries are approved:

* `AIClient` and `AsyncAIClient` remain separate public clients.
* Explicit `AIConfig` replaces rather than merges with environment
  configuration and is structurally validated during client construction, as
  established separately by ADR-0017.
* `AIRequestBuilder` is a public return type with public fluent methods, but
  direct construction with `RequestExecutor` is not a supported application
  contract. Applications construct builders through `AIClient.request()`.
* Visible client `provider` and `executor` attributes are implementation
  exposure, not supported extension points.
* `BaseAIProvider` and `ProviderFactory` are the stable provider-extension
  surface. The built-in `OpenAIProvider` is factory-owned implementation.
* Optional provider capabilities continue to fail when invoked if an adapter
  does not implement them. Capability discovery and live preflight checks are
  not part of Version 1.0.
* Streaming returns `Iterator[str]`, tool calling returns `ToolResponse`,
  image requests return `AIResult`, and embeddings return
  `EmbeddingResponse`. These advanced operations do not receive a new common
  metadata wrapper.
* `parse_json_response()` and `estimate_cost_usd()` remain supported
  compatibility helpers.
* `ImageRequest`, `normalize_path()`, request executors, structured-prompt and
  retry plumbing, logger construction, pre-resolved cost helpers, and
  provider-specific translation helpers remain internal even where Python can
  import them.
* Public Pydantic result and state models remain mutable. `AIConfig` and
  `AILoggingConfig` remain frozen dataclasses. `AIRequestBuilder`, in-memory
  stores, workflow state, and orchestrator registration remain intentionally
  mutable.
* Agent prompts contain the current user message once. `memory_limit` counts
  messages included in the prompt, including the dedicated current message.
* `AgentResponse` continues to expose only output, model, request ID, and the
  memory snapshot rather than the complete underlying `AIResult`.
* Workflow state updates are shallow, including updates returned by a failed
  step. Workflows stop on failure and do not roll back earlier work.
* Multi-agent sequences validate every requested agent name before executing
  any agent. After execution starts, agent failures remain typed partial
  results and stop the sequence.
* An empty `MultiAgentResponse` reports `success=False`; success requires at
  least one successful result and no failed results.
* Django, FastAPI, and CLI contracts remain the integration surface documented
  in the API reference.
* The documented `AIError` hierarchy covers expected toolkit failures but does
  not wrap every Python, framework, provider, or application exception.

No package version, release tag, or publication changes as part of this
decision.

---

## Alternatives Considered

* Re-export the complete public surface from `ai`.

  Rejected because it would duplicate 71 import paths, enlarge the root
  namespace, and make optional framework boundaries less obvious.

* Re-export only the clients and result models from `ai`.

  Rejected because two canonical import styles would still need permanent
  compatibility support while the existing explicit module paths are already
  documented and used by every example.

* Treat every importable non-private name as public.

  Rejected because implementation modules necessarily expose executors,
  adapters, helpers, and dependencies that applications should not couple to.

* Add capability discovery and a common advanced-request result wrapper before
  Version 1.0.

  Rejected because both would add new abstractions late in the release cycle
  without evidence that one provider-independent contract fits all adapters.

* Preserve the four mismatched behaviors as stable contracts.

  Rejected because they allow invalid configuration to progress too far,
  duplicate prompt content, permit avoidable partial execution after a lookup
  error, or describe no work as successful.

---

## Consequences

Positive

* Applications have one authoritative, test-protected Version 1.0 surface.
* Provider-independent extension points remain explicit.
* Internal implementation can evolve without promising compatibility for every
  importable name.
* Mutable state and partial-failure behavior are documented rather than hidden.
* Reviewed pre-release edge cases have explicit, tested behavior.

Negative

* Applications cannot rely on short top-level imports in Version 1.0.
* Direct builder, executor, or built-in adapter construction is unsupported.
* Public model fields and method shapes require compatibility review before
  future changes.
* Applications that relied on the corrected pre-release edge cases will
  observe different Version 1 behavior.

---

## Related Files

* `ai/__init__.py`
* `ai/client.py`
* `ai/async_client.py`
* `ai/agent.py`
* `ai/orchestrator.py`
* `docs/api_reference.md`
* `docs/compatibility.md`
* `tests/test_public_api_stability.py`
* `docs/development/roadmap.md`
* `docs/development/project_state.md`
