# Python AI Toolkit — Session Handoff

## Project

**Project:** Python AI Toolkit  
**Current version:** `0.7.0-dev`  
**Current milestone:** Sprint 9 — Production Readiness  
**Active roadmap item:** `PROD-003 — Complete Documentation`  
**Next task:** `DOC-013 — Create a stable public API reference`

---

## Goal

Continue developing the project according to the existing architecture, roadmap, architectural decisions, and engineering workflow.

Do not redesign the project, skip roadmap steps, or introduce unrelated backlog work unless there is a strong architectural reason.

Before changing code:

1. Read the relevant current implementation.
2. Read the applicable roadmap and architecture sections.
3. Confirm that the proposed task is still the correct next task.
4. Explain the design before implementation.

Do not rely only on conversation memory. The project files are the source of truth.

---

## Authoritative Documents

The following documents are the source of truth:

1. `docs/development/project_state.md`
2. `docs/development/roadmap.md`
3. `docs/architecture/architecture.md` or the project's current architecture document
4. `docs/development/future_backlog.md`, or the Future Backlog section inside `roadmap.md`

Reference documents, only when needed:

- `README.md`
- `CHANGELOG.md`
- `docs/development/performance_profiling.md`
- Architecture Decision Records:
  - `0001-airesult.md`
  - `0002-provider-response.md`
  - `0003-request-executor.md`
  - `0004-retry-repair.md`
  - `0005-provider-factory.md`
  - `0006-provider-configuration.md`
  - `0007-provider-registration-api.md`
  - `0008-separate-async-client.md`
  - `0009-tool-calling-without-auto-execution.md`
  - `0010-provider-independent-rag-abstractions.md`
  - `0011-document-loaders-separate-from-embedding.md`
  - `0012-memory-agent-workflow-separation.md`
  - `0013-explicit-multi-agent-orchestration.md`
  - `0014-explicit-configuration-injection-for-framework-integrations.md`
  - `0015-command-line-interface-architecture.md`

When document content conflicts with old conversation context, the current repository document wins.

---

## Completed Sprints

The project has completed:

- Sprint 2 — Core Architecture
- Sprint 3 — Provider Infrastructure
- Sprint 4 — Developer Experience
- Sprint 5 — Advanced Requests
- Sprint 6 — Retrieval & Knowledge
- Sprint 7 — Agents & Workflows
- Sprint 8 — Framework Integrations

Sprint 9 — Production Readiness is active.

---

## Current Architecture Summary

Primary request flow:

```text
Application
    ↓
AIClient / AsyncAIClient
    ↓
RequestExecutor / AsyncRequestExecutor
    ↓
ProviderFactory
    ↓
BaseAIProvider implementation
    ↓
LLM provider
```

Major implemented capabilities:

- Synchronous and asynchronous AI clients
- Provider factory, registry, and custom provider registration
- Environment-based and explicitly injected configuration
- Plain text and structured Pydantic responses
- Structured response repair and retry handling
- Request IDs, token usage, estimated cost, duration, and retry metadata
- Streaming responses
- Tool calling without automatic application-side execution
- Image inputs
- Fluent request builder and prompt templates
- Embeddings, in-memory vector storage, retrieval, and RAG
- Text, Markdown, and directory document loaders
- Conversation memory
- Agents
- Workflow engine
- Explicit multi-agent orchestration
- Django and FastAPI integrations
- Command-line interface
- Configurable logging with test- and benchmark-safe behavior

Important existing design decisions:

- `AIClient.ask()` is the simple public API.
- `AIClient.request()` is the fluent advanced-request API.
- `AsyncAIClient` is a separate explicit async client.
- Tool calls are exposed to the application and are not automatically executed.
- Structured response handling remains provider-independent.
- The in-memory vector store is a reference implementation for tests, examples, and small local applications.
- Public API stability is preferred over small performance gains.

---

# Sprint 9 — Production Readiness

## PROD-001 — Benchmark Suite

**Status:** Completed with documented pre-existing quality-check exceptions

Benchmark source directory:

```text
benchmarks/
```

Generated benchmark results:

```text
.benchmarks/
```

`.benchmarks/` should remain ignored by Git.

Expected benchmark verification:

```powershell
python -m pytest benchmarks --benchmark-only
```

Expected result:

```text
9 passed, 4 skipped
```

Correctness-only benchmark run:

```powershell
python -m pytest benchmarks --benchmark-disable -v
```

Expected result:

```text
13 passed
```

The benchmark suite covers:

1. smoke execution
2. plain request lifecycle
3. structured parsing
4. retry repair
5. vector search
6. vector search with metadata filtering
7. RAG orchestration
8. one-step workflow
9. five-step workflow

Benchmark rules:

- deterministic
- no network calls
- no API keys
- no file logging
- no fixed machine-performance thresholds

---

## PROD-002 — Performance Profiling

**Status:** Completed with documented pre-existing quality-check exceptions

Roadmap tasks:

- [x] `PROF-001` — Establish baseline
- [x] `PROF-002` — Profile plain request execution
- [x] `PROF-003` — Profile structured parsing and repair
- [x] `PROF-004` — Profile vector search
- [x] `PROF-005` — Profile RAG orchestration
- [x] `PROF-006` — Profile workflow execution
- [x] `PROF-007` — Review optimization candidates
- [x] `PROF-008` — Implement approved optimizations
- [x] `PROF-009` — Complete profiling documentation

Consolidated report:

```text
docs/development/performance_profiling.md
```

The next task is `DOC-013`.

---

## PROF-001 — Baseline

**Status:** Completed

Baseline environment:

- Windows 11 64-bit
- CPython 3.14.4
- Intel i5-1135G7
- 8 logical processors
- baseline commit: `91fed29585de55836b640798c754434d3c7f8733`

Baseline benchmark file previously used:

```text
benchmarks/prod-002-before.json
```

The original baseline reported a dirty working tree. Preserve that fact in final profiling documentation rather than silently presenting it as a clean baseline.

Logging-isolation verification:

```powershell
Remove-Item logs -Recurse -Force -ErrorAction SilentlyContinue
python -m pytest benchmarks --benchmark-only -q
Test-Path logs
```

Expected result:

```text
False
```

---

## PROF-004 — Vector Search

**Status:** Completed

Relevant files:

```text
ai/vector_store.py
tests/test_vector_store.py
profiling/profile_vector_search.py
profiling/profile_vector_scaling.py
```

### Initial finding

Cosine similarity dominated vector-search execution.

The original implementation recalculated the query-vector magnitude for every candidate and used three generator-based `sum()` passes per similarity calculation.

### Accepted optimization

- calculate the query-vector norm once per search
- calculate candidate dot product and candidate squared norm in one direct loop
- preserve the public vector-store API
- retain the existing private two-vector cosine helper interface
- do not persistently cache stored-vector norms while vectors remain mutable

### Benchmark result

Unfiltered vector search:

- baseline mean: approximately `18.984 ms`
- optimized mean average: approximately `12.363 ms`
- average improvement: approximately `34.9%`

Metadata-filtered vector search:

- baseline mean: approximately `10.875 ms`
- optimized mean average: approximately `6.574 ms`
- average improvement: approximately `39.5%`

### Scaling result

Unfiltered:

- approximately `8.2513 ms` per 1,000 scanned records
- linear-fit `R² = 0.999993`

Metadata-filtered:

- approximately `4.5470 ms` per 1,000 scanned records
- linear-fit `R² = 0.999295`

Both paths scale approximately linearly with the number of stored records.

The filtered path is cheaper per scanned record because nonmatching records do not proceed to cosine calculation, result-model construction, or sorting.

Rejected changes:

- top-k heap, because sorting was negligible
- bypassing Pydantic validation, because it would weaken the result contract
- persistent norm caching, because mutable vectors could make cached norms stale
- introducing an external numerical dependency for the current reference implementation

---

## PROF-002 — Plain Request Execution

**Status:** Completed from a design, implementation, targeted-test, profile, and benchmark perspective.

Before treating the task as fully closed in Git, verify the full project checks and commit status listed below.

Relevant files:

```text
ai/cost.py
ai/executor.py
ai/async_executor.py
ai/client.py
ai/async_client.py
tests/test_cost.py
profiling/profile_request_lifecycle.py
benchmarks/test_request_lifecycle.py
```

### Initial finding

`estimate_cost_usd()` called `get_ai_config()` for every completed request.

For 100,000 local requests, this caused:

- 100,000 full configuration resolutions
- repeated configuration validation
- repeated logging-configuration resolution
- approximately 1.1 million environment-variable lookups

Initial profile:

- approximately `19.1 million` function calls
- approximately `11.443 seconds` total profile time
- cost estimation: approximately `5.808 seconds`
- repeated configuration resolution: approximately `5.384 seconds`
- success logging: approximately `4.093 seconds`

### Accepted cost optimization

`ai/cost.py` now separates:

- pricing resolution
- pure request-time cost arithmetic
- compatibility behavior for direct callers

Intended interfaces:

```python
resolve_cost_rates(...)
calculate_cost_usd(...)
estimate_cost_usd(...)
```

Executors resolve model/custom pricing once during construction and store it for request-time arithmetic.

`AIClient` and `AsyncAIClient` pass configured custom pricing to their executors.

Directly constructed executors continue using built-in model pricing and do not require API configuration merely to calculate cost.

### Accepted logging optimization

`RequestExecutor._log_success()` and `AsyncRequestExecutor._log_success()` check:

```python
logger.isEnabledFor(logging.INFO)
```

before serializing token metadata or creating an INFO log record.

This preserves complete INFO logging while avoiding unnecessary work when INFO logging is disabled.

### Tests added

`tests/test_cost.py` covers:

- explicit pricing resolution
- unknown-model pricing
- pre-resolved cost arithmetic
- missing usage
- missing pricing
- compatibility configuration-based pricing
- synchronous executor custom pricing
- asynchronous executor custom pricing
- synchronous disabled-INFO logging guard
- asynchronous disabled-INFO logging guard

Because the project does not use a native async pytest plugin for these tests, the async cost test uses `asyncio.run()`.

### Results

Post-optimization profile with INFO logging enabled:

- function calls reduced from approximately `19.1 million` to `8.1 million`
- profile time reduced from approximately `11.443 seconds` to `4.153 seconds`
- profile-time reduction: approximately `63.7%`
- configuration and environment access disappeared from the request hot path
- INFO logging became the largest remaining contributor

Benchmark with the benchmark logger set to CRITICAL:

Before:

- mean: approximately `27.292 µs`
- median: approximately `25.800 µs`
- throughput: approximately `36,640 operations/second`

After:

- mean: approximately `4.551 µs`
- median: approximately `4.400 µs`
- throughput: approximately `219,756 operations/second`

Measured improvement:

- mean overhead reduced by approximately `83.3%`
- median overhead reduced by approximately `82.9%`
- throughput increased by approximately six times

No additional plain-request optimization is currently justified.

Rejected changes:

- removing request IDs
- bypassing Pydantic `AIResult` validation
- disabling success logging globally
- globally caching complete environment-derived `AIConfig`

---

# PROF-005 — RAG Orchestration

**Status:** Completed

Relevant files:

```text
ai/rag.py
ai/retriever.py
benchmarks/test_rag_orchestration.py
profiling/profile_rag_orchestration.py
```

Profile method:

- five prebuilt retrieved contexts
- one prebuilt `AIResult`
- 100,000 repeated component operations
- 50,000 repeated complete orchestration calls
- retrieval, embedding, vector search, provider execution, network access,
  logging, and file I/O excluded

Primary finding:

- retrieved-context formatting accounted for approximately `64%` of complete
  orchestration profile time
- `RAGResponse` construction accounted for approximately `12%`
- grounded-prompt construction accounted for approximately `3%`
- adding instructions changed prompt-building cost only negligibly

Complete `RAGPipeline.ask()` execution took approximately `8.16 µs` per call
under `cProfile`. The focused benchmark median was approximately `5.268 µs`.

Decision:

No RAG-specific runtime optimization is recommended. The orchestration overhead
is already very small and will normally be dominated by retrieval and provider
execution. Context formatting remains a contributor for `PROF-007` review, but
its current absolute cost does not justify extra caching, less readable output,
or bypassing Pydantic validation.

No runtime file changed during `PROF-005`.

---

# PROF-006 — Workflow Execution

**Status:** Completed

Relevant files:

```text
ai/workflow.py
benchmarks/test_workflow_execution.py
profiling/profile_workflow_execution.py
tests/test_workflow.py
```

Profile method:

- deterministic one-step and five-step workflows
- step functions performing only small arithmetic operations
- 100,000 repeated component operations
- 50,000 repeated complete executions for each workflow size
- workflow construction, reusable inputs, metadata, contexts, and result
  fixtures excluded from measured operations where applicable
- provider execution, network access, logging, and file I/O excluded

Component findings:

- `WorkflowContext` construction: approximately `1.36 µs` per operation under
  `cProfile`
- `WorkflowStepResult` construction: approximately `1.62 µs`
- state propagation through `dict.update()`: approximately `0.09 µs`
- final-result construction with one prebuilt step: approximately `1.18 µs`
- final-result construction with five prebuilt steps: approximately `1.21 µs`

Complete `WorkflowEngine.run()` profile:

- one-step workflow: approximately `5.20 µs` per execution
- five-step workflow: approximately `15.08 µs` per execution
- five steps took approximately `2.9` times the one-step profile time because
  context and final-result construction occur once per workflow

Focused benchmark:

- one-step median: approximately `2.839 µs`
- five-step median: approximately `7.367 µs`
- four added steps increased the median by approximately `4.528 µs`, or
  approximately `1.132 µs` per additional step

Primary finding:

Pydantic model construction and validation are the largest reusable
contributors. State propagation and step-list maintenance are negligible.
Final-result construction changes very little between one and five prebuilt
step results because those nested models are already validated.

Decision:

No workflow-specific runtime optimization is recommended. The absolute
orchestration cost is already only a few microseconds and preserves clear,
typed workflow contracts. Pydantic construction remains visible for the
cross-path review in `PROF-007`, but bypassing validation or adding specialized
construction paths is not justified by this evidence.

No runtime file changed during `PROF-006`.

---

# PROF-007 — Optimization Candidate Review

**Status:** Completed

The review ranked remaining costs by representative absolute impact while
keeping measurements from different environments non-comparable:

1. optimized vector search remains the largest internal path at millisecond
   scale, but its remaining cost is the intentional linear-scan architecture
2. repeated Pydantic JSON-schema generation is the largest removable repeat at
   approximately `0.4 ms` per structured prompt under `cProfile`
3. structured repair is tens of microseconds and represents required retry,
   parsing, provider, and token-accounting behavior
4. workflow construction, RAG formatting, request IDs, and typed result
   construction are microsecond-scale
5. INFO logging remains intentional and configurable observability overhead

Decisions:

- no additional vector optimization, because replacing the linear scan is an
  architectural storage/indexing change rather than a local hot-path change
- no structured-schema cache, because model-class caching can become stale
  after Pydantic `model_rebuild()`; safe invalidation would add dependency
  coupling or public caller responsibility for a small real-request gain
- no retry optimization that weakens validation, configured retry behavior, or
  token accounting
- no RAG or workflow micro-optimization that weakens formatting clarity or
  typed Pydantic contracts
- no removal of request IDs or configurable logging

No optimization candidate was approved for runtime implementation.

No runtime file, public API, ADR, README, changelog, or project-state file
changed during `PROF-007`.

---

# PROF-008 — Approved Optimization Implementation Gate

**Status:** Completed without implementation

`PROF-007` approved no remaining candidate for runtime implementation.
`PROF-008` therefore completed as the roadmap's explicit no-change gate.

Confirmed:

1. no file under `ai/` required modification
2. correctness behavior and provider-independent interfaces remain unchanged
3. no correctness test required addition or modification
4. no before-and-after benchmark was applicable because no implementation was
   attempted
5. no ADR, README, changelog, or project-state update was required

This decision is evidence-driven. The remaining costs are part of the
intentional reference architecture, dependency-dominated, required for
correctness or observability, or negligible in absolute terms.

---

# PROF-009 — Profiling Documentation

**Status:** Completed

The final report documents:

1. deterministic profiling method and measurement boundaries
2. local environments and cross-machine comparison limits
3. bottlenecks across every profiled execution path
4. accepted optimizations with before-and-after evidence
5. explicitly rejected optimizations
6. remaining performance risks and architectural limits

Completion verification:

```text
269 normal tests passed
13 benchmark correctness checks passed
9 timed benchmarks passed, 4 infrastructure-only tests skipped
benchmark execution created no logs/ directory
```

Repository-wide Black and Ruff checks were run with current unpinned tool
versions. Black 26.5.1 identified two pre-existing formatting findings, and
Ruff 0.16.0 identified 62 pre-existing repository-wide findings. `PROF-009`
changed no Python implementation or test file, so those findings remain
separate release-quality work rather than being silently combined with this
documentation task.

`benchmarks/README.md` remains the operational benchmark guide. Stable
profiling conclusions belong in
`docs/development/performance_profiling.md`, while machine-specific JSON and
text outputs remain ignored under `.benchmarks/`.

---

# DOC-001 — README Structure Review

**Status:** Completed

The root README now serves as the onboarding and repository-navigation page
rather than duplicating every feature guide and development document.

Completed work:

1. mapped the original 2,922-line README before editing
2. moved installation, configuration, and quick-start guidance near the top
3. grouped capabilities into requests, retrieval, orchestration, integrations,
   logging, and errors
4. retained concise examples for the main public entry points
5. removed duplicated summaries, the stale project tree, and the copied roadmap
6. removed stale forward-looking lists that contradicted implemented features
7. added direct navigation to examples and authoritative documentation
8. changed no runtime API, implementation, dependency, or executable behavior

The detailed content audits remain assigned to `DOC-002` through `DOC-014`.

---

# DOC-002 — Installation and Optional Extras

**Status:** Completed

Completed work:

1. reviewed `pyproject.toml`, `requirements.txt`, package metadata, integration
   imports, and the CLI entry point
2. corrected the README so virtual-environment activation precedes installation
3. documented the current local-source boundary without implying a PyPI release
4. added `docs/installation.md`
5. separated normal non-editable use from editable contributor installation
6. documented the core, `django`, `fastapi`, `dev`, and `benchmark` paths
7. updated stale Django and FastAPI example installation commands
8. confirmed that `httpx2` is the intended current FastAPI test-client
   dependency and is distinct from OpenAI's `httpx` dependency
9. changed no runtime implementation, public API, package dependency, or
   architecture

Clean-environment verification:

```text
normal source installation passed
core AIClient import passed
CLI help passed
core installation excluded Django and FastAPI
django extra installation and import passed
fastapi extra installation and import passed
benchmark extra installation and import passed
combined dev and benchmark installation passed
269 normal tests passed
```

---

# DOC-003 — Environment and Explicit Configuration

**Status:** Completed

Completed work:

1. reviewed `ai/config.py`, `ai/config_validator.py`, both client constructors,
   provider creation, CLI configuration commands, `.env.example`, and relevant
   tests
2. added `docs/configuration.md`
3. inventoried every supported environment variable and default
4. documented provider-specific lookup and generic fallback precedence
5. documented process-environment precedence over `.env`
6. documented explicit `AIConfig` construction for `AIClient` and
   `AsyncAIClient`
7. made explicit that supplied configuration replaces environment loading and
   that omitted fields use dataclass defaults
8. documented manual `ConfigValidator.validate()` use for directly constructed
   configurations
9. separated structural validation, provider availability, and live
   credential/model verification
10. documented the read-only, non-network Configuration CLI boundary
11. expanded `.env.example` comments and corrected related README,
    installation, and example-gallery guidance
12. changed no runtime implementation, public API, dependency, provider
    registration, or architecture

Completion verification:

```text
provider-specific and generic fallback precedence passed
process-environment precedence over .env passed
explicit AIConfig environment-bypass behavior passed
4 configuration Python examples executed
15 Python blocks in the changed guides parsed
repository-relative documentation links passed
45 focused configuration and CLI tests passed
269 normal tests passed
```

---

# DOC-004 — Provider Registration

**Status:** Completed

Completed work:

1. reviewed `BaseAIProvider`, `OpenAIProvider`, `ProviderFactory`, provider
   tests, architecture, and provider ADRs
2. added `docs/providers.md`
3. documented the built-in provider and registered-provider inspection
4. documented exact-name registration and process-local lifecycle
5. documented the provider constructor contract and conditional embedding
   configuration
6. separated required plain-text behavior from optional capabilities
7. documented duplicate, unsupported, constructor, and capability errors
8. separated structural validation, provider availability, and live
   verification
9. recorded explicit-config auto-validation for the Version 1.0 API review
10. changed no runtime implementation, public API, dependency, test, or ADR

Completion verification:

```text
custom provider registration and client execution passed
22 Python blocks in the affected guides parsed
repository-relative Markdown links passed
269 normal tests passed
```

---

# DOC-005 — Plain and Structured Requests

**Status:** Completed

Completed work:

1. reviewed `AIClient`, `RequestExecutor`, `AIResult`, prompt construction,
   parsing, Pydantic validation, repair behavior, tests, and examples
2. added `docs/requests.md`
3. documented `ask()`, `ask_text()`, and their return-value difference
4. documented plain and Pydantic-structured request behavior
5. documented all `AIResult` metadata and raw-response semantics
6. documented strict parsing, schema validation, provider-backed repair, and
   configured retry boundaries
7. distinguished toolkit validation from application factual, authorization,
   policy, and business validation
8. linked the guide from the README and example gallery
9. changed no runtime implementation, public API, dependency, test, or ADR

Completion verification:

```text
4 request-guide Python examples executed
2 existing plain and structured example scripts executed
16 focused request-lifecycle tests passed
repository-relative documentation links passed
269 normal tests passed
```

---

# DOC-006 — Streaming, Async, Tools, and Image Inputs

**Status:** Completed

Completed work:

1. reviewed both clients and executors, provider capability methods, tool and
   image models, OpenAI adapters, tests, and examples 05 through 09
2. added `docs/advanced_requests.md`
3. documented streaming iteration, chunk and partial-output behavior, and its
   non-`AIResult` metadata boundary
4. documented async plain and structured requests and the current absence of
   async streaming, tools, images, and embeddings
5. documented tool definitions and responses plus application-owned
   allow-listing, validation, authorization, execution, and continuation
6. documented image URLs, Base64 data URLs, local-file helper boundaries,
   optional detail, multiple images, and structured responses
7. documented provider-method versus model/account support and capability
   errors
8. changed no runtime implementation, public API, dependency, test, or ADR

Completion verification:

```text
31 Python documentation blocks parsed
40 repository-relative documentation links passed
6 advanced-request example scripts executed with deterministic offline clients
26 focused streaming, async, tool, and image tests passed
269 normal tests passed
```

---

# DOC-007 — Embeddings, Retrieval, and RAG

**Status:** Completed

Completed work:

1. reviewed embedding models and client methods, provider capability behavior,
   vector-store abstraction, retriever, RAG pipeline, document loaders, tests,
   examples 10 through 14, and ADRs 0010 and 0011
2. added `docs/retrieval.md`
3. documented single and batch embeddings, model/dimension configuration,
   metadata, provider ordering, and the non-`AIResult` return boundary
4. documented vector records, ID replacement, cosine-similarity scores, exact
   metadata filters, dimension errors, zero vectors, and result ordering
5. documented the volatile linear-scan reference boundary of
   `InMemoryVectorStore`
6. documented `VectorStoreRetriever`, `RetrievedContext`, and prompt-ready
   context formatting
7. documented text, Markdown, and directory loaders plus the explicit
   loading/chunking/embedding/indexing separation
8. documented RAG prompt construction, returned contexts, response metadata,
   omitted `AIResult` fields, and current sync/plain-text limits
9. documented that similarity is not factual confidence, returned contexts are
   not verified citations, and grounding instructions cannot guarantee a
   grounded answer
10. recorded advanced-request metadata, image-aware repair, safe tool-loop, and
    provider/model capability discovery as explicit release-review or Future
    Backlog candidates
11. changed no runtime implementation, public API, dependency, test, or ADR

Completion verification:

```text
5 retrieval-guide workflows executed offline
5 retrieval example scripts executed with a deterministic offline client
56 focused embedding, vector-store, retriever, RAG, and document tests passed
38 Python blocks in the affected documents parsed
58 repository-relative Markdown links passed
269 normal tests passed
```

---

# DOC-008 — Memory, Agents, Workflows, and Orchestration

**Status:** Completed

Completed work:

1. reviewed memory, agent, workflow, and orchestrator implementations, tests,
   examples 15 through 18, architecture, and ADRs 0012 and 0013
2. added `docs/orchestration.md`
3. documented message roles, metadata and timestamp contracts, memory
   operations, recent-message counting, formatting, and volatile storage
4. documented the agent lifecycle, prompt construction, memory updates,
   selected response metadata, and failure-without-rollback behavior
5. documented workflow context, shallow state updates, step and run results,
   execution history, fail-fast behavior, exception conversion, and partial
   state
6. documented exact-name agent registration, inventory ordering, individual
   execution, sequential string handoff, result collection, and failures
7. documented synchronous, sequential, in-process boundaries and
   application-owned routing, tools, permissions, transactions, and resource
   control
8. recorded agent prompt construction and partial-execution result semantics for
   the Version 1.0 public API review
9. changed no runtime implementation, public API, dependency, test, or ADR

Completion verification:

```text
4 orchestration-guide workflows executed offline
4 existing example scripts executed with a deterministic offline client
61 focused memory, agent, workflow, and orchestrator tests passed
22 Python blocks in the affected documents parsed
67 repository-relative Markdown links passed
269 normal tests passed
```

---

# DOC-009 — Django, FastAPI, and CLI Integrations

**Status:** Completed

Completed work:

1. reviewed the Django and FastAPI adapters, configuration system, CLI
   implementation, package entry point, ADRs 0014 and 0015, tests, and examples
   19 through 22
2. added `docs/integrations.md`
3. documented optional extras and the separation between installation,
   configuration, provider creation, and live requests
4. documented Django's complete `AI_TOOLKIT` mapping, defaults, normalization,
   validation, custom setting names, and non-merging environment boundary
5. documented synchronous and asynchronous Django helpers plus new-client-per-
   call behavior
6. documented FastAPI dependency factories, `Annotated` aliases, endpoint
   usage, dependency overrides, and application-owned lifecycle
7. clarified that the FastAPI extra does not choose an ASGI server or provide
   application test dependencies, and corrected example 20's Uvicorn setup
8. documented CLI commands, configuration masking, output streams, exit codes,
   handled `AIError` failures, and visible unexpected exceptions
9. documented that framework adapters do not own HTTP exception mapping,
   authentication, authorization, rate limits, transactions, or business policy
10. changed no executable runtime implementation, public API, dependency, test,
    or ADR

Completion verification:

```text
Django configuration, sync/async helpers, and example 19 executed offline
FastAPI dependency injection, override, and example 20 executed offline
Separate Uvicorn installation and example 20 app import target verified
CLI ask, config show, and config validate workflows executed offline
66 focused integration, configuration, and CLI tests passed
27 Python blocks in the affected documents parsed
50 repository-relative Markdown links passed
269 normal tests passed
```

---

# DOC-010 — Exceptions and Error Handling

**Status:** Completed

Completed work:

1. reviewed `ai/exceptions.py` and every production raise/catch boundary
2. reviewed exception-focused tests, architecture, and developer error-message
   guidance
3. added `docs/error_handling.md`
4. documented the complete `AIError` hierarchy and specific-versus-base catch
   boundaries
5. documented configuration timing, provider translation, exception chaining,
   structured repair exhaustion, and provider-aware retry decisions
6. documented ordinary Python, Pydantic, file-system, custom-provider, and
   application-policy failures outside the toolkit hierarchy
7. documented streaming failures during iteration and possible partial output
8. documented raised exceptions versus workflow and orchestration failure
   result objects
9. documented framework propagation, CLI exit behavior, logging, and
   application-owned error mapping
10. updated the maintainer error-message guide and documentation navigation
11. changed no runtime implementation, public API, dependency, test, example,
    benchmark, or ADR

Completion verification:

```text
offline error-contract workflows passed
226 focused error-surface tests passed
33 Python blocks in the affected documents parsed
51 repository-relative Markdown links passed
269 normal tests passed
```

---

# DOC-011 — Security and Secret Handling

**Status:** Completed

Completed work:

1. reviewed configuration, `.env`, logging, CLI masking, provider errors,
   requests, structured repair, tools, images, retrieval, memory,
   orchestration, framework, example, packaging, and repository surfaces
2. added `docs/security.md`
3. documented local, test, CI, and production secret sources
4. documented repository, history, artifact, terminal, logging, error, prompt,
   provider, result, persistence, and retention boundaries
5. documented application ownership of data classification, provider
   governance, tenant access, tool authorization, and incident response
6. expanded `.gitignore` to exclude `.env.*` while preserving `.env.example`
7. added a placeholder-only warning to `.env.example`
8. linked the guide from the README and relevant capability guides
9. removed raw provider responses from parse and schema exception messages so
   executor traceback logging cannot disclose them
10. added regression coverage for redacted exceptions and failure logs
11. preserved the public exception hierarchy, provider API, dependencies,
    examples, benchmarks, and ADRs

Completion verification:

```text
security explicit-configuration example executed offline
.env and .env.* ignore behavior passed with .env.example retained
credential-pattern scan found no likely real secrets in maintained files
94 focused security and request-lifecycle tests passed
focused Black and Ruff checks passed
70 Python blocks in the affected guides parsed
95 repository-relative Markdown links passed
271 normal tests passed
```

---

# DOC-012 — Python-Version and Provider Compatibility

**Status:** Completed

Completed work:

1. reviewed package metadata, dependency declarations and resolved metadata,
   provider interfaces and adapters, framework integrations, tests,
   installation guidance, and runtime evidence
2. added `docs/compatibility.md`
3. separated the declared Python `>=3.11` installation floor from verified
   environments and the planned Python 3.11–3.14 release matrix
4. recorded the current full-suite environment as Linux with CPython 3.12.13
5. retained the historical Windows CPython 3.14.4 deterministic benchmark
   result without presenting it as a current full-suite result
6. verified all 113 maintained Python files against the Python 3.11 grammar
   while preserving the distinction between syntax and runtime compatibility
7. documented dependency-resolution and `requirements.txt` snapshot boundaries
8. documented the built-in OpenAI adapter's SDK mappings and separated them
   from credentials, accounts, regions, quotas, and model capabilities
9. documented custom-provider dependency ownership
10. documented Django and FastAPI version intersections, separate clean
    installation checks, and application-owned server and testing dependencies
11. documented capability-specific live provider smoke testing separately from
    deterministic compatibility tests
12. documented the application-owned SOCKS proxy transport boundary
13. linked compatibility guidance from the README, installation, provider, and
    integration guides
14. changed no runtime API, implementation, dependency, test, example,
    benchmark, or ADR

Completion verification:

```text
Python 3.11 grammar parsed 113 Python files
pip check passed for the clean contributor resolution
core, CLI, Django, and FastAPI imports passed
64 focused provider and integration tests passed
9 timed benchmarks passed and 4 infrastructure-only tests skipped
30 Python blocks in the affected documents parsed
57 repository-relative Markdown links passed
271 normal tests passed on Linux with CPython 3.12.13
```

---

# Exact Next Task — DOC-013

Create a stable public API reference without changing the runtime API and
without expanding into the separate final example-verification task.

Required work:

1. inspect package exports, public classes, functions, methods, typed models,
   protocols or abstract bases, exceptions, integrations, and CLI entry points
2. define the intended public surface rather than documenting every internal
   implementation helper
3. document signatures, parameters, return types, raised toolkit exceptions,
   important state and lifecycle behavior, and capability-specific limits
4. preserve the distinctions already established in the focused guides instead
   of duplicating their tutorials
5. identify any ambiguous or accidentally public surface for the Version 1.0
   API-freeze review rather than silently changing it in a documentation task
6. link the reference from the README and relevant guides
7. keep final execution of every documented example for `DOC-014`

---

# DOC-012 Verification and Repository State

Changed project files:

```text
README.md
CHANGELOG.md
docs/compatibility.md
docs/installation.md
docs/providers.md
docs/integrations.md
docs/development/roadmap.md
docs/development/project_state.md
docs/development/session_handoff.md
```

No runtime API, executable implementation, dependency, test, example,
benchmark, or ADR changed.

Suggested focused commit:

```powershell
git add `
    README.md `
    CHANGELOG.md `
    docs\compatibility.md `
    docs\installation.md `
    docs\providers.md `
    docs\integrations.md `
    docs\development\roadmap.md `
    docs\development\project_state.md `
    docs\development\session_handoff.md

git diff --cached
git commit -m "docs: document compatibility"
```

---

# PROF-003 Verification and Repository State

Completed verification in the transferred project:

```text
269 normal tests passed
13 benchmark correctness checks passed
2 focused structured benchmarks passed
focused Black check passed
focused Ruff check passed
```

Focused profiling artifacts:

```text
profiling/profile_structured_execution.py
.benchmarks/profile-structured-execution.txt
.benchmarks/prof-003-baseline.json
```

The transferred ZIP did not include `.git`, so Git status, history, and commit
creation could not be completed in this session.

The full repository was not Black- or Ruff-clean before `PROF-003`. Those
unrelated existing findings were not changed. Recheck them in the original
repository with its normal tool versions and configuration.

Suggested focused commit after restoring the changes to the Git repository:

```powershell
git add `
    profiling\profile_structured_execution.py `
    docs\development\roadmap.md `
    docs\development\session_handoff.md

git commit -m "perf: profile structured response execution"
```

---

# PROF-005 Verification and Repository State

Completed verification in the transferred project:

```text
269 normal tests passed
13 benchmark correctness checks passed
9 timed benchmarks passed
4 fixture-only benchmarks skipped
focused RAG benchmark passed
focused Black check passed
focused Ruff check passed
```

Focused profiling artifacts:

```text
profiling/profile_rag_orchestration.py
.benchmarks/profile-rag-orchestration.txt
.benchmarks/prof-005-baseline.json
```

The `.benchmarks/` results are local machine evidence and remain ignored by
Git. They should not be staged.

The transferred project still contains no `.git` directory, so Git status,
history, and commit creation must be completed in the original repository.

Suggested focused commit after restoring the changes to the Git repository:

```powershell
git add `
    profiling\profile_rag_orchestration.py `
    docs\development\roadmap.md `
    docs\development\session_handoff.md

git commit -m "perf: profile RAG orchestration"
```

---

# PROF-006 Verification and Repository State

Completed verification in the transferred project:

```text
269 normal tests passed
13 benchmark correctness checks passed
9 timed benchmarks passed
4 fixture-only benchmarks skipped
2 focused workflow benchmarks passed
focused Black check passed
focused Ruff check passed
```

Focused profiling artifacts:

```text
profiling/profile_workflow_execution.py
.benchmarks/profile-workflow-execution.txt
.benchmarks/prof-006-baseline.json
```

The `.benchmarks/` results are local machine evidence and remain ignored by
Git. They should not be staged.

The transferred project still contains no `.git` directory, so Git status,
history, and commit creation must be completed in the original repository.

Suggested focused commit after restoring the changes to the Git repository:

```powershell
git add `
    profiling\profile_workflow_execution.py `
    docs\development\roadmap.md `
    docs\development\session_handoff.md

git commit -m "perf: profile workflow execution"
```

---

# PROF-007 Verification and Repository State

This was a documentation-only review task. Existing profiling and benchmark
evidence was inspected; no runtime or test file changed, so rerunning the full
suite was not required to validate new behavior.

Changed project files:

```text
docs/development/roadmap.md
docs/development/session_handoff.md
```

The transferred project still contains no `.git` directory. Complete the
focused commit in the original repository:

```powershell
git add `
    docs\development\roadmap.md `
    docs\development\session_handoff.md

git diff --cached --stat
git diff --cached
git commit -m "docs: review performance optimization candidates"
```

---

# PROF-008 Verification and Repository State

This was a documentation-only implementation gate. `PROF-007` approved no
runtime optimization, so no executable or test file changed and no additional
test run was required.

Changed project files:

```text
docs/development/roadmap.md
docs/development/session_handoff.md
```

The transferred project still contains no `.git` directory. Complete the
focused commit in the original repository:

```powershell
git add `
    docs\development\roadmap.md `
    docs\development\session_handoff.md

git diff --cached --stat
git diff --cached
git commit -m "docs: close performance optimization gate"
```

---

# Minor Issue Discovered

`ai/config_validator.py` contains the same `embedding_dimensions` validation block twice.

This did not block `PROF-009` and should not derail the active documentation
roadmap.

Handle it as one of the following:

- a tiny cleanup in a separately scoped commit, or
- a Future Backlog / maintenance note

Do not silently combine it with unrelated performance work unless the roadmap explicitly allows that cleanup.

---

# Workflow

Every roadmap task follows this sequence:

1. Design
2. Code
3. Tests
4. Documentation
5. Review
6. Git
7. Roadmap update
8. Project-state update, only when the milestone changes

A task is not complete until every applicable step is complete.

After each completed roadmap task, perform:

- Design review
- Code review
- Test review
- Documentation review
- Git commit suggestion
- Roadmap update
- Sprint-status check

Only then continue to the next roadmap item.

---

# Roadmap Rules

- Only one sprint is active.
- Verify the next task before starting it.
- Do not silently change roadmap order or scope.
- If a better architectural decision is required:
  1. explain the reason
  2. update the roadmap
  3. continue with the corrected plan
- New ideas belong in Future Backlog.
- Future Backlog items should not interrupt active work unless they:
  - block the current sprint
  - correct an architecture or safety issue
  - prevent important technical debt
  - are required by the next roadmap task

---

# Coding Rules

Before changing existing code:

- Read the current implementation.
- Never assume a file still matches an older conversation excerpt.
- Verify interfaces and callers first.
- Minimize unrelated refactoring.
- Preserve public APIs unless there is a documented architectural reason.
- Create an ADR when a public or architectural contract changes.
- Keep each roadmap task in a focused commit.

When suggesting code:

- Prefer changed sections over complete files when the change is small.
- Provide complete files only when partial edits would be error-prone.
- Include formatting, linting, focused tests, full tests, and Git commands at the appropriate stage.
- Do not claim commands were run by the assistant; the user runs them locally.

---

# Documentation Rules

Architecture change:

- add an ADR

Public API change:

- update README

Completed roadmap task:

- update ROADMAP immediately

Completed sprint or version-level feature set:

- update CHANGELOG

Project milestone change:

- update PROJECT_STATE

Important future idea:

- add it to Future Backlog

Do not create ADRs for small local implementation details. ADRs are for decisions affecting architecture, public APIs, provider independence, safety, extensibility, or many files.

---

# Engineering Principles

Apply:

- Single Responsibility Principle
- Dependency Inversion
- Composition over inheritance
- Strong typing
- Explicit interfaces
- Small public API
- Provider independence

Business logic belongs in applications, not in the toolkit.

Performance changes must be evidence-driven and must not weaken contracts for minor gains.

---

# Communication Style

Act as a senior software architect and mentor.

Explain:

- what is being built
- why it is being built
- why the approach fits the architecture
- why meaningful alternatives were rejected

Proceed in small, explicit steps.

Do not skip directly to a large implementation without first inspecting the relevant files.

For complete Markdown sections intended for the repository, return the entire reusable section in one block so it can be pasted safely.

---

# Environment Notes

Recorded user environment:

- Windows
- PowerShell
- PyCharm

The historical benchmark baseline used Windows with CPython 3.14.4. The
transferred project used for `DOC-012` verification ran on Linux with CPython
3.12.13.

Package metadata accepts Python `>=3.11`; the planned Version 1.0 test matrix is
Python 3.11 through 3.14.

`ripgrep` (`rg`) is not installed in the recorded Windows environment.

Use PowerShell search when needed:

```powershell
Get-ChildItem -Recurse -File -Filter *.py |
    Select-String -Pattern "SEARCH_PATTERN" |
    ForEach-Object {
        "$($_.Path):$($_.LineNumber): $($_.Line.Trim())"
    }
```

---

# Future Backlog Rules

The Future Backlog is a parking lot, not the active implementation plan.

Known categories include:

- local LLM support
- additional providers and provider discovery
- plugin system and MCP
- metrics and web dashboards
- model benchmarking and evaluation
- immutable or reusable request builders
- local image-file helper
- persistent and database-backed memory
- token-aware memory trimming and summarization
- PDF, DOCX, HTML, and database loaders
- automatic chunking and indexing helpers
- streaming, async, structured, cited, reranked, evaluated, and hybrid RAG
- configurable agent prompts
- streaming, async, RAG-aware, and tool-using agents
- branching, parallel, retryable, async, durable, and visual workflows
- AI-based routing, debate, shared memory, recursive loops, and tool-using multi-agent systems
- CLI diagnostics and provider health checks

Read the actual Future Backlog document for the complete current list.

Do not implement backlog items unless they are promoted into the active roadmap or are required to unblock the current task.

---

# Recommended New-Chat File Package

Upload or paste these first:

Required:

1. `session_handoff.md`
2. `project_state.md`
3. `roadmap.md`
4. `architecture.md`
5. `future_backlog.md`, if separate

For the immediate next task, also provide:

6. `README.md`
7. `pyproject.toml`
8. all focused public guides under `docs/`
9. `ai/__init__.py`
10. client, configuration, result, request-builder, and exception modules
11. tool, image, embedding, vector-store, retriever, RAG, document, memory,
    agent, workflow, and orchestrator modules
12. provider base class, factory, and built-in adapter
13. Django and FastAPI integration exports and implementations
14. tests that assert public signatures, return types, and error contracts

Profiling evidence and generated benchmark artifacts are not required for
`DOC-013`.

Do not upload the entire repository unless necessary. Provide the authoritative documents and the current files relevant to the next task.

---

# Suggested First Message in the New Chat

```text
Continue the Python AI Toolkit project using the attached session handoff and source-of-truth documents.

First:
1. Read session_handoff.md.
2. Read project_state.md, roadmap.md, architecture.md, and future_backlog.md.
3. Verify the repository's current state and confirm that DOC-013 is still the correct next task.
4. Confirm that PROD-002 closed with its profiling report and no public API change.

Do not redesign the project, skip roadmap order, or assume older file contents.
Follow the workflow: design → code → tests → documentation → review → git → roadmap update.
```

---

# Final Instruction

If anything is unclear, inspect the project files first.

Do not guess.

If a previous implementation might have changed, request or inspect the current file before proposing modifications.

Architecture consistency, correctness, and evidence-driven decisions are more important than adding features quickly.
