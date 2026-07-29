# Python AI Toolkit — Session Handoff

## Project

**Project:** Python AI Toolkit  
**Current version:** `1.0.0`  
**Current milestone:** Sprint 9 — Production Readiness  
**Active roadmap item:** `PROD-007 — Version 1.0.0 Release`  
**Next task:** `V1-005 — Update project state`

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

The current next task is `V1-002`.

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

# DOC-013 — Stable Public API Reference

**Status:** Completed

Completed work:

1. inspected package exports, public classes, functions, methods, typed models,
   abstract extension interfaces, exceptions, integrations, CLI entry points,
   tests, and focused capability guides
2. added `docs/api_reference.md`
3. defined 71 supported symbols across current module-level import paths
4. documented exact client methods, configuration dataclasses, typed results,
   provider and application extension interfaces, framework exports, CLI
   commands, exception boundaries, and important lifecycle behavior
5. retained `parse_json_response()` as the documented low-level parsing helper
   and `estimate_cost_usd()` as the preserved compatibility helper
6. explicitly excluded request executors, structured-prompt and repair
   plumbing, pre-resolved cost helpers, logger construction, direct built-in
   adapter construction, and private provider translation helpers
7. recorded the empty top-level `ai` namespace, builder constructor,
   client implementation attributes, direct adapter imports, and other
   importable-but-undocumented names for the Version 1.0 API freeze
8. linked the reference from the README and every focused public capability
   guide
9. changed no runtime API, import path, implementation, dependency, test,
   example, benchmark, or ADR

Completion verification:

```text
71 documented public symbols imported
key runtime signatures, enum values, defaults, and result properties matched
239 focused public-surface tests passed
80 Python blocks across README and focused public guides parsed
130 repository-relative Markdown links passed
271 normal tests passed on Linux with CPython 3.12.13
```

---

# DOC-014 Completion

`DOC-014 — Verify every documented example` is complete, which also completes
`PROD-003 — Complete Documentation`.

Completed work:

1. inventoried 201 fenced blocks across the README, focused guides, API
   reference, and example gallery
2. executed all 80 Python blocks in document order, including asserted failure
   examples
3. verified numbered examples 01 through 20, the Base64 helper variant, and
   the two existing unnumbered examples with deterministic provider behavior
4. verified Django service use, FastAPI dependency overrides, CLI
   configuration commands, Uvicorn target loading, and clean core/framework
   installations
5. added permanent regression tests for examples, Python blocks, relative
   links, gallery references, and numbered modules
6. corrected the wrong example 01 run command and title
7. made the Base64 helper's behavior match its structured-image name
8. corrected the async `ask_text()` fragment and retrieval `Document` import
9. kept live provider verification explicit because deterministic substitutes
   do not prove credentials, account access, regions, or model capabilities
10. recorded the complete classification and boundaries in
    `docs/development/example_verification.md`

Completion verification:

```text
201 fenced blocks inventoried
80 Python documentation blocks executed
40 focused documentation and example tests passed
core, Django, and FastAPI clean installations passed
CLI configuration and Uvicorn target checks passed
9 benchmarks passed; 4 infrastructure tests skipped
311 normal tests passed on Linux with CPython 3.12.13
136 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, package dependency, public import
path, benchmark, or ADR changed.

---

# EXAMPLE-001 Completion

`EXAMPLE-001 — Explicit AIConfig injection` is complete.

Completed work:

1. added `examples/23_explicit_config.py`
2. preserved the existing gallery numbering: 21 and 22 remain CLI workflows
3. accepted an application-supplied key and constructed the full configuration
   explicitly
4. called `ConfigValidator.validate(config)` before `AIClient(config=config)`
5. kept provider, model, embedding, retry, and logging values separate from
   environment-based toolkit resolution
6. documented development-secret injection and application-owned
   secret-manager use
7. linked example 23 from the gallery, learning path, README, and configuration
   guide
8. added deterministic regression coverage proving conflicting environment
   values are not merged and invalid configuration is rejected before provider
   construction

Completion verification:

```text
42 focused example and documentation tests passed
313 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
204 fenced documentation blocks inventoried
80 Python documentation blocks compiled
138 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or ADR
changed.

---

# EXAMPLE-002 Completion

`EXAMPLE-002 — Custom provider registration` is complete.

Completed work:

1. added `examples/24_custom_provider.py`
2. preserved all existing gallery numbers and assigned the next Python example
   number
3. implemented `LocalEchoProvider` with the factory's required constructor and
   the abstract synchronous plain-text method
4. registered `local_echo` before client construction
5. selected it with an explicit `AIConfig` validated before `AIClient`
   construction
6. returned deterministic response and token-usage metadata without a
   credential or network request
7. documented that registration is process-local and does not prove optional
   capabilities or live provider/model support
8. added isolated regression coverage for registry state, validation order,
   factory construction, and the complete plain-text client path

Completion verification:

```text
49 focused example, documentation, and provider-factory tests passed
314 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
206 fenced documentation blocks inventoried
80 Python documentation blocks compiled
140 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or ADR
changed.

---

# EXAMPLE-003 Completion

`EXAMPLE-003 — Testing application code with a fake provider` is complete.

Completed work:

1. added `examples/25_testing_with_fake_provider.py`
2. kept application logic dependent only on `AIClient`
3. added a deterministic `BaseAIProvider` fake with controlled structured
   output, token metadata, and prompt capture
4. patched `ProviderFactory.create()` only during client construction and let
   the patch restore automatically
5. exercised the real client, request executor, structured prompt builder, and
   Pydantic parser without credentials or network access
6. proved that explicit test configuration bypasses conflicting environment
   values
7. proved that no provider registration or registry-state leak occurs
8. linked example 25 from the gallery, learning path, README, and provider
   guide
9. added permanent focused regressions for application output, prompt
   forwarding, provider identity, environment bypass, and registry isolation

Completion verification:

```text
50 focused example, documentation, and provider-factory tests passed
315 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
209 fenced documentation blocks inventoried
81 Python documentation blocks compiled
142 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or ADR
changed.

---

# EXAMPLE-004 Completion

`EXAMPLE-004 — Batch embedding and retrieval` is complete.

Completed work:

1. added `examples/26_batch_embedding_and_retrieval.py`
2. submitted three metadata-bearing knowledge items in one
   `AIClient.embed_texts()` request
3. used `EmbeddingVector.index` to restore input order when provider results
   arrive out of order
4. preserved stable record IDs, sources, and topics in `VectorRecord`
5. stored the batch in `InMemoryVectorStore`
6. embedded a separate query and retrieved filtered contexts with
   `VectorStoreRetriever`
7. kept document loading, RAG prompt construction, and answer generation out
   of the focused workflow
8. linked example 26 from the gallery, complete learning path, README, and
   retrieval guide
9. added deterministic regressions for batching, order, metadata, storage,
   query embedding, and relevant-context ranking

Completion verification:

```text
79 focused embedding, vector-store, retriever, example, and documentation tests passed
317 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
211 fenced documentation blocks inventoried
81 Python documentation blocks compiled
144 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or ADR
changed.

---

# EXAMPLE-005 Completion

`EXAMPLE-005 — End-to-end document indexing and RAG` is complete.

Completed work:

1. added `examples/27_document_indexing_and_rag.py`
2. loaded the existing `.txt` and `.md` sample files through
   `DirectoryLoader` using a module-relative path
3. explicitly added stable application-owned IDs and collection metadata
4. converted prepared documents through `documents_to_embedding_inputs()`
5. embedded all documents in one batch and restored input order from
   `EmbeddingVector.index`
6. preserved loader, source, filename, record, and collection metadata in
   `VectorRecord`
7. indexed records in `InMemoryVectorStore`, retrieved the Redis document,
   and generated one grounded answer through `RAGPipeline`
8. kept chunking, persistent storage, access policy, citation verification,
   and indexing orchestration out of toolkit scope
9. linked example 27 from the gallery, complete learning path, README, and
   retrieval guide
10. added deterministic regression coverage for the complete loader-to-answer
    workflow, including reversed embedding results and grounded prompt contents

Completion verification:

```text
104 focused document, embedding, vector-store, retriever, RAG, example, and documentation tests passed
319 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
214 fenced documentation blocks inventoried
81 Python documentation blocks compiled
147 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or ADR
changed.

---

# EXAMPLE-006 Completion

`EXAMPLE-006 — Structured application service example` is complete.

Completed work:

1. added `examples/28_structured_application_service.py`
2. defined constrained application-owned `FeedbackAnalysis` and
   `FeedbackOutcome` Pydantic models
3. injected `AIClient` into a framework-independent
   `CustomerFeedbackService`
4. validated and normalized application input before any provider request
5. kept the prompt, queue selection, and human-review rules in application
   code
6. translated expected `AIError` failures into
   `FeedbackServiceUnavailable` while preserving the original exception cause
7. preserved the toolkit request ID in the stable application result
8. linked example 28 from the gallery, complete learning path, README, and
   request guide
9. added deterministic regression coverage for structured execution, prompt
   forwarding, input validation, routing, metadata, and error translation

Completion verification:

```text
51 focused example and documentation tests passed
322 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
217 fenced documentation blocks inventoried
82 Python documentation blocks compiled
149 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or ADR
changed.

---

# EXAMPLE-007 Completion

`EXAMPLE-007 — Review and normalize all example descriptions` is complete.

Completed work:

1. inspected every numbered and unnumbered example, both CLI workflows, the
   example-09 Base64 variant, and the existing gallery
2. defined one description format covering file or command, behavior,
   requirements, run instructions, and an important boundary
3. normalized headings, wording, labels, links, lists, and spacing across the
   complete catalog
4. reconciled every description with its implementation and the focused
   public guides
5. documented the intentional numbering exceptions for CLI entries 21–22,
   `09_1`, and the two unnumbered supplementary modules
6. preserved provider, credential, network, optional-dependency, platform, and
   model-capability requirements
7. added permanent regressions requiring complete module coverage and all five
   description fields
8. preserved example behavior, runnable module paths, production runtime APIs,
   dependencies, and architectural decisions

Focused verification:

```text
54 focused example and documentation tests passed
325 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
184 fenced documentation blocks inventoried
82 Python documentation blocks compiled
176 repository-relative user-documentation links passed
```

---

# EXAMPLE-008 Completion

`EXAMPLE-008 — Verify all examples against current APIs` is complete.

Completed work:

1. inspected the current public API reference, runtime interfaces, and every
   numbered, variant, framework, command, and supplementary example
2. executed all Python workflows deterministically and both command workflows
   through the real CLI dispatcher
3. verified framework, image, embedding, retrieval, RAG, agent, workflow,
   orchestration, and structured-response examples through real public entry
   points
4. confirmed that every toolkit import used by an example is documented and
   importable
5. added permanent execution-coverage and public-import completeness
   regressions
6. found no stale API use, return contract, expected output, or setup
   instruction requiring correction
7. preserved all example module paths, normalized descriptions, numbering
   compatibility decisions, runtime APIs, dependencies, and architectural
   decisions
8. retained live-provider behavior as an explicit smoke-test boundary

Focused verification:

```text
56 focused example and documentation tests passed
67 focused tests passed including CLI workflows
327 normal tests passed on Linux with CPython 3.12.13
clean source installation with development and benchmark extras passed
pip check passed in the clean environment
focused Black and Ruff checks passed
184 fenced documentation blocks inventoried
82 Python documentation blocks compiled
179 repository-relative user-documentation links passed
```

`PROD-004 — Additional Examples` is complete.

---

# PACKAGE-001 — Package Metadata Review

**Status:** Completed

Completed work:

1. reviewed `pyproject.toml`, the README metadata source, package discovery,
   source packages, console entry point, and optional groups
2. retained the intended distribution name, `ai` import package, description,
   Python floor, README source, and author name
3. normalized the in-progress distribution version to `0.7.0.dev0`
4. declared `openai>=1.66.0` for the Responses API and `pydantic>=2.4.2` for
   Pydantic v2 validation and schema methods with Python 3.12 wheel support
5. confirmed that `ai*` discovery covers all six current package directories
6. documented the distribution, import, and terminal-command names
7. left project URLs absent because no canonical repository, documentation,
   or issue-tracker locations have been confirmed
8. added focused metadata regressions
9. preserved the classifiers, license, optional groups, console entry point,
   build process, distribution validation, and installation checks for their
   assigned later tasks

Final verification:

```text
4 focused package-metadata regressions passed
25 package-metadata and documentation tests passed
62 core and provider tests passed with openai 1.66.0 and pydantic 2.4.2
331 normal tests passed on Linux with CPython 3.12.13
pip check passed in the current complete environment
setuptools accepted the updated pyproject metadata
focused Black and Ruff checks passed
```

No runtime API, provider implementation, optional dependency, console entry
point, benchmark, example, or architectural decision changed.

---

# PACKAGE-002 — Package Classifiers

**Status:** Completed

Completed work:

1. reviewed the intended audience, maturity, Python support, operating-system
   scope, optional framework integrations, console interface, and project
   topics against the current implementation and documentation
2. classified the project as Beta rather than Alpha or Production/Stable
3. added canonical classifiers for console use, Django, FastAPI, developers,
   operating-system independence, Python 3-only support, artificial
   intelligence, and Python modules
4. initially omitted individual Python 3.11–3.14 classifiers until the
   Version 1.0 release matrix verified the intended range; `RELEASE-002`
   subsequently added them
5. deliberately omitted license classifiers because `PACKAGE-003` owns the
   license decision and current packaging metadata uses a license expression
6. verified every selected value against the canonical PyPI classifier list
7. documented classifier meaning and non-goals in the installation guide
8. added focused regressions for the exact selected set and its non-overclaim
   boundaries

Final verification:

```text
6 focused package-metadata regressions passed
27 package-metadata and documentation tests passed
10 selected classifiers passed canonical Trove validation
333 normal tests passed on Linux with CPython 3.12.13
pip check passed in the current complete environment
setuptools accepted the updated pyproject metadata
focused Black and Ruff checks passed
```

No runtime API, provider implementation, dependency, optional group, console
entry point, benchmark, example, license decision, or architectural decision
changed.

---

# PACKAGE-003 — License Metadata and License File

**Status:** Completed

Completed work:

1. confirmed MIT as the owner-selected license already stated in the README
2. added the complete standard MIT text under
   `Copyright (c) 2026 Burim Koci`
3. declared the SPDX expression `license = "MIT"`
4. declared `license-files = ["LICENSE"]`
5. raised the build-backend floor to `setuptools>=77.0.3` for current PEP 639
   metadata support without changing runtime dependencies
6. preserved the existing classifier set without deprecated `License ::`
   values
7. documented commercial use, closed-source use, redistribution, notice
   preservation, and the warranty disclaimer
8. added focused regressions keeping the metadata, repository file, owner, and
   build backend aligned

Final verification:

```text
8 focused package-metadata regressions passed
29 package-metadata and documentation tests passed
335 normal tests passed on Linux with CPython 3.12.13
pip check passed in the current complete environment
setuptools 77.0.3 accepted the PEP 639 license metadata
focused Black and Ruff checks passed
184 fenced documentation blocks inventoried
82 Python documentation blocks compiled
181 repository-relative user-documentation links passed
```

No runtime API, provider implementation, runtime dependency, optional group,
console entry point, benchmark, example, build output, or architectural
decision changed.

---

# PACKAGE-004 — Optional Dependency Groups

**Status:** Completed

Completed work:

1. reviewed the core, Django, FastAPI, development, and benchmark dependency
   declarations against their implementation and documented workflows
2. installed each of the five shapes in a separate clean virtual environment
3. proved that core imports without Django, FastAPI, HTTPX2, Pytest, or
   pytest-benchmark
4. proved that the Django and FastAPI extras install and import independently
5. proved that the development extra supports the complete normal suite,
   Black, Ruff, both framework integrations, and the current HTTPX2-backed
   FastAPI tests
6. proved that the benchmark extra supports benchmark fixtures and
   pytest-benchmark independently of the development extra
7. retained every existing dependency declaration because no missing, invalid,
   or misplaced package was demonstrated
8. added focused regressions for exact optional groups, core metadata
   boundaries, and framework-import isolation
9. documented the verified installation boundaries

Final verification:

```text
11 focused package-metadata regressions passed
338 normal tests passed from the clean development-extra environment
5 benchmark fixture and tooling smoke tests passed
core, Django, FastAPI, development, and benchmark clean installations passed
pip check passed in all five clean environments
focused Black and Ruff checks passed
184 fenced documentation blocks inventoried
82 Python documentation blocks compiled
181 repository-relative user-documentation links passed
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 68 pre-existing findings outside this task
```

No runtime API, provider implementation, dependency declaration, console entry
point, license metadata, benchmark implementation, example, build output, or
architectural decision changed.

---

# PACKAGE-005 — Console Entry Points

**Status:** Completed

Completed work:

1. inspected the `ai-toolkit = "ai.cli.main:main"` declaration against the
   current CLI implementation and in-process behavior tests
2. installed the core package into a new virtual environment and proved that
   installation creates the console executable
3. ran the command from outside the source tree with `PYTHONPATH` removed and
   confirmed that it loads `ai.cli.main` from the installed package
4. verified help, command and subcommand routing, masked configuration display,
   offline structural validation, and an expected configuration failure
5. verified process exit codes `0`, `1`, and `2`
6. confirmed through installed metadata that the command resolves the same
   supported `main()` function used by direct tests
7. added permanent regressions for both the script declaration and resolved
   installed entry point
8. documented local Windows PowerShell checks for command location, help,
   offline validation, exit codes, and temporary environment cleanup
9. retained the existing metadata and runtime implementation because no defect
   was demonstrated

Final verification:

```text
13 focused package-metadata regressions passed
45 package-metadata, CLI, and documentation tests passed
340 normal tests passed on Linux with CPython 3.12.13
clean core installation generated the ai-toolkit executable
installed metadata and executable resolved ai.cli.main:main from site-packages
help, routing, masking, offline validation, and exit codes 0, 1, and 2 passed
pip check passed in the clean and complete environments
focused Black and Ruff checks passed
188 fenced documentation blocks inventoried
82 Python documentation blocks compiled
182 repository-relative user-documentation links passed
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 96 pre-existing findings outside this task
```

No runtime API, CLI implementation, provider implementation, dependency
declaration, optional group, license metadata, benchmark, example, build
output, or architectural decision changed.

---

# PACKAGE-006 — Source Distribution and Wheel

**Status:** Completed

Completed work:

1. separated older generated build output before constructing the release
   artifacts
2. ran the standard isolated `python -m build` workflow
3. built `python_ai_toolkit-0.7.0.dev0.tar.gz`
4. built `python_ai_toolkit-0.7.0.dev0-py3-none-any.whl`
5. confirmed at a basic level that the wheel contains all six `ai` package
   areas, metadata, the console entry point, and the MIT license
6. confirmed at a basic level that the source distribution contains package
   source, `pyproject.toml`, README, MIT license, and tests
7. added `build/`, `dist/`, and `*.egg-info/` to `.gitignore`
8. added a regression preserving the generated-output exclusions
9. documented the Windows PowerShell clean-build workflow, expected filenames,
   and meaning of the pure-Python wheel tag
10. preserved detailed archive, metadata, rendered-README, and `twine`
    validation for `PACKAGE-007`

Final verification:

```text
wheel and source distribution built successfully with python -m build
wheel contains 46 entries and is tagged py3-none-any
source distribution contains 94 entries
14 focused package-metadata regressions passed
35 package-metadata and documentation tests passed
341 normal tests passed on Linux with CPython 3.12.13
pip check passed in the complete environment
focused Black and Ruff checks passed
193 fenced documentation blocks inventoried
82 Python documentation blocks compiled
183 repository-relative user-documentation links passed
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 68 pre-existing findings outside this task
```

No runtime API, CLI implementation, provider implementation, dependency
declaration, optional group, license metadata, benchmark, example, or
architectural decision changed.

---

# PACKAGE-007 — Distribution Validation

**Status:** Completed

Completed work:

1. ran strict Twine validation on the wheel and source distribution
2. verified matching identity, version, dependency, extra, Python, README,
   entry-point, and MIT license metadata
3. confirmed the complete UTF-8 README and exact license text in both formats
4. compared every packaged `ai` Python module with the reviewed source
5. confirmed the source distribution contains the complete current test suite
6. verified safe normalized paths, regular filesystem entries, wheel tag, and
   all wheel `RECORD` hashes and sizes
7. confirmed no secrets, environment files, caches, compiled Python, logs,
   deliverables, or nested build output are packaged
8. added a reusable offline archive validator and local Windows instructions
9. documented how to untrack older generated `*.egg-info/` output safely
10. recorded that Twine validates Markdown rendering but not link destinations;
    canonical public project URLs and PyPI-page links remain unresolved until
    a real public repository location is confirmed

Validation evidence:

```text
twine 6.2.0 --strict: PASSED for wheel and source distribution
wheel: 46 safe entries
source distribution: 94 safe entries
wheel SHA-256: 68cbc49d66523eb8473b19a73a4ecf2e8fe5f0281d850d330f651f08aa76eb06
source SHA-256: 6c39b39402fb622770a271b1e69202485604618463fab65988434cbd508ca3d2
```

No runtime API, CLI implementation, provider implementation, dependency,
optional group, package metadata, README, license, benchmark, example, build
artifact, or architectural decision changed.

---

# PACKAGE-008 — Clean Artifact Installation

**Status:** Completed

Completed work:

1. installed the wheel and source distribution in separate isolated
   environments outside the source checkout
2. confirmed both installations report version `0.7.0.dev0`
3. confirmed imports resolve from each environment's `site-packages`
4. ran offline prompt and vector-store API smoke checks
5. verified installed CLI help and offline configuration validation
6. ran `pip check` successfully for both installations
7. fixed Windows distribution validation by normalizing textual newline forms
   without weakening README content comparison
8. added the cross-platform regression and Windows PowerShell instructions

Verification evidence:

```text
wheel and source-distribution clean installations passed
both installed paths resolved from isolated site-packages
offline public-API smoke checks passed
installed CLI and structural configuration checks passed
pip check passed in both environments
Windows CRLF distribution validation passed
15 focused package-metadata regressions passed
36 package-metadata and documentation tests passed
342 normal tests passed on Linux with CPython 3.12.13
Twine strict and offline distribution validation passed
focused Black and Ruff checks passed
198 fenced documentation blocks inventoried
82 Python documentation blocks compiled
183 repository-relative user-documentation links passed
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 68 pre-existing findings outside this task
```

No runtime API, CLI implementation, provider implementation, dependency,
optional group, package metadata, license, benchmark, example, or
architectural decision changed.

---

# PACKAGE-009 — Core Installation Without Optional Frameworks

**Status:** Completed

Completed work:

1. rebuilt and validated the current distribution artifacts
2. installed only the wheel, without extras, in a new environment outside the
   source checkout
3. confirmed the installed core requirements are `openai`, `pydantic`, and
   `python-dotenv`
4. confirmed Django and FastAPI are neither installed nor importable
5. imported all 35 non-framework toolkit modules from isolated `site-packages`
6. exercised prompt templates and in-memory vector search offline
7. passed `pip check` and inspected the resolved installation
8. added `scripts/verify_core_installation.py` for repeatable release checks
9. added regressions keeping the verifier aligned with core metadata and source
   modules
10. documented the Windows PowerShell workflow

Verification evidence:

```text
core-only wheel installation passed on Linux with CPython 3.12.13
python-ai-toolkit 0.7.0.dev0 imported from isolated site-packages
core requirements matched openai, pydantic, and python-dotenv
Django and FastAPI distributions and modules were absent
35 non-framework toolkit modules imported successfully
offline prompt and vector-store checks passed
pip check passed
17 focused package-metadata regressions passed
38 package-metadata and documentation tests passed
344 normal tests passed on Linux with CPython 3.12.13
Twine strict and offline distribution validation passed
focused Black and Ruff checks passed
200 fenced documentation blocks inventoried
82 Python documentation blocks compiled
183 repository-relative user-documentation links passed
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 68 pre-existing findings outside this task
```

No runtime API, CLI implementation, provider implementation, dependency,
optional group, package metadata, license, benchmark, example, or
architectural decision changed.

---

# PACKAGE-010 — Django and FastAPI Extras Separately

**Status:** Completed

Completed work:

1. rebuilt and validated the current distribution artifacts
2. installed the wheel with only the Django extra in a clean environment
3. confirmed Django `6.0.7` and every Django adapter module loaded from isolated
   `site-packages`
4. confirmed FastAPI was neither installed nor importable in the Django
   environment
5. installed the wheel with only the FastAPI extra in a second clean environment
6. confirmed FastAPI `0.140.7` and every FastAPI adapter module loaded from
   isolated `site-packages`
7. confirmed Django was neither installed nor importable in the FastAPI
   environment
8. exercised both adapters through a deterministic offline provider and passed
   `pip check` in both environments
9. added `scripts/verify_framework_extra_installation.py` for repeatable release
   checks
10. added regressions keeping the verifier aligned with optional-dependency
    metadata and every framework adapter module
11. documented the Windows PowerShell workflow

Verification evidence:

```text
Django-only wheel installation passed on Linux with CPython 3.12.13
Django 6.0.7 installed; FastAPI distribution and module were absent
FastAPI-only wheel installation passed on Linux with CPython 3.12.13
FastAPI 0.140.7 installed; Django distribution and module were absent
both toolkit imports resolved from isolated site-packages
both installed adapter module sets imported successfully
both offline integration behavior checks passed
pip check passed in both environments
19 focused package-metadata regressions passed
40 package-metadata and documentation tests passed
346 normal tests passed on Linux with CPython 3.12.13
Twine strict and offline distribution validation passed
focused Black and Ruff checks passed
202 fenced documentation blocks inventoried
82 Python documentation blocks compiled
183 repository-relative user-documentation links passed
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 68 pre-existing findings outside this task
```

No runtime API, CLI implementation, provider implementation, dependency,
optional group, package metadata, license, benchmark, example, or
architectural decision changed.

---

# RELEASE-001 — Continuous-Integration Workflow

**Status:** Completed

Implemented:

1. added `.github/workflows/ci.yml`
2. configured push and pull-request triggers
3. restricted the workflow to read-only repository-content permission
4. disabled checkout credential persistence
5. selected Python 3.11 as the single initial interpreter because it is the
   package's declared minimum
6. installed the editable `dev` extra from authoritative `pyproject.toml`
7. ran `python -m pip check` and the existing normal test suite
8. disabled toolkit-managed file logging during CI tests
9. added regression coverage for triggers, permissions, action versions,
   package installation, checks, and exclusions owned by later release tasks
10. documented the equivalent local commands

Scope retained for later tasks:

* `RELEASE-002` — Python 3.11, 3.12, 3.13, and 3.14 matrix
* `RELEASE-003` — test, Black, and Ruff enforcement
* `RELEASE-004` — distribution builds
* `RELEASE-005` — built-distribution validation
* `RELEASE-006` through `RELEASE-009` — tags, secure publishing,
  documentation, and non-production workflow rehearsal

No runtime API, dependency metadata, provider behavior, package build,
publishing permission, credential, benchmark, or ADR changed.

Completion verification:

```text
workflow YAML parsed successfully
5 CI-workflow regressions passed
45 focused CI, documentation, and package-metadata tests passed
351 normal tests passed
clean editable dev installation passed
pip check passed
changed Python test passed Black and Ruff
repository-wide Black retained 2 older files outside this task
repository-wide Ruff retained 68 pre-existing findings outside this task
```

---

# RELEASE-002 — Supported Python Versions

**Status:** Completed

Implemented:

1. expanded the CI test job into independent Python 3.11, 3.12, 3.13, and
   3.14 matrix jobs
2. disabled matrix fail-fast so every supported interpreter reports its result
3. retained one authoritative `.[dev]` installation, `pip check`, and normal
   test command in every job
4. reviewed and freshly resolved all core and development dependencies across
   the target range
5. added Python 3.11–3.14 package classifiers after full-suite verification
6. added workflow and metadata regressions
7. documented the verified matrix and Windows test procedure

Completion verification:

```text
Python 3.11.15: pip check passed; 351 normal tests passed
Python 3.12.13: pip check passed; 351 normal tests passed
Python 3.13.14: pip check passed; 351 normal tests passed
Python 3.14.6: pip check passed; 351 normal tests passed
workflow YAML parsed successfully
5 CI-workflow regressions passed
19 package-metadata regressions passed
45 focused CI, package-metadata, and documentation tests passed
focused Black and Ruff checks passed
strict Twine and offline distribution validation passed
```

Python 3.11 resolved Django 5.2.16; Python 3.12–3.14 resolved Django 6.0.7.
No runtime dependency constraint, API, provider behavior, build workflow,
publishing permission, or ADR changed.

The repository-wide `RELEASE-003` starting scope was 2 files requiring Black
formatting and 68 Ruff findings. The task below resolved the complete baseline.

---

# RELEASE-003 — Tests, Black, and Ruff in CI

**Status:** Completed

Implemented:

1. resolved the recorded repository-wide baseline of 2 Black files and 68 Ruff
   findings
2. applied Black formatting and safe import/modernization fixes
3. documented the intentional agent and workflow exception boundaries
4. preserved the numbered example gallery with a narrow Ruff `N999` exception
5. added Black and Ruff checks to every Python 3.11–3.14 matrix job
6. expanded workflow regressions and local verification documentation

Completion verification:

```text
Python 3.11.15: pip check, Ruff, and 351 normal tests passed
Python 3.12.13: pip check, Ruff, and 351 normal tests passed
Python 3.13.14: pip check, Ruff, and 351 normal tests passed
Python 3.14.6: pip check, Ruff, and 351 normal tests passed
repository-wide Black check passed
repository-wide Ruff check passed
5 CI-workflow regressions passed
workflow YAML parsed successfully
```

No public runtime API, provider contract, dependency declaration, package
build, publishing permission, benchmark contract, or architectural decision
changed.

---

# RELEASE-004 — Build Package Distributions in CI

**Status:** Completed

Implemented:

1. added a `Build distributions` job that depends on the complete test matrix
2. used Python 3.11 and the standard `python -m build` workflow
3. uploaded only the wheel and source distribution as the
   `python-package-distributions` workflow artifact
4. kept repository permissions read-only and checkout credentials disabled
5. preserved strict validation for `RELEASE-005`
6. added CI regressions and local build documentation

Completion verification:

```text
clean source build produced python_ai_toolkit-0.7.0.dev0-py3-none-any.whl
clean source build produced python_ai_toolkit-0.7.0.dev0.tar.gz
7 CI-workflow regressions passed
353 normal tests passed
workflow YAML parsed successfully
repository-wide Black check passed
repository-wide Ruff check passed
```

No runtime API, dependency declaration, provider behavior, strict distribution
validation, publishing permission, credential, or architectural decision
changed.

---

# RELEASE-005 — Validate Built Distributions

**Status:** Completed

Implemented:

1. installed `build` and Twine together in the existing build job
2. ran strict Twine validation against the exact files produced by
   `python -m build`
3. ran the existing offline archive validator against those same files
4. ordered both validation gates before artifact upload
5. retained the complete quality-matrix dependency, read-only repository
   access, disabled checkout credentials, and publishing exclusion
6. added CI regressions and local validation documentation

Completion verification:

```text
clean source build produced python_ai_toolkit-0.7.0.dev0-py3-none-any.whl
clean source build produced python_ai_toolkit-0.7.0.dev0.tar.gz
strict Twine validation passed for both distributions
offline archive validation passed for both distributions
8 CI-workflow regressions passed
354 normal tests passed
workflow YAML parsed successfully
repository-wide Black check passed
repository-wide Ruff check passed
```

No runtime API, dependency declaration, package metadata, provider behavior,
publishing permission, credential, benchmark contract, or architectural
decision changed.

---

# RELEASE-006 — Add Release Workflow for Version Tags

**Status:** Completed

Implemented:

1. added a separate workflow triggered only by tags matching `v*.*.*`
2. added exact tag-to-`pyproject.toml` version validation
3. checked out the tagged event SHA explicitly in every job
4. repeated all supported-version dependency, Black, Ruff, and test gates
5. built, strictly validated, and retained the wheel and source distribution
   only after the complete matrix passed
6. preserved read-only permissions and excluded publishing credentials,
   publishing steps, and GitHub Release creation
7. added permanent regressions and local Windows validation guidance

Completion verification:

```text
current package tag v0.7.0.dev0 passed exact version validation
incorrect v1.0.0 tag failed before quality or build work
18 release-workflow regressions passed
26 combined CI and release-workflow regressions passed
66 focused release, CI, package-metadata, and documentation tests passed
372 normal tests passed
both workflow YAML files parsed successfully
all 128 Python files passed Black
repository-wide Ruff check passed
strict Twine and offline archive validation passed for the clean-source build
```

No runtime API, dependency declaration, package metadata, provider behavior,
publishing permission, credential, benchmark contract, or architectural
decision changed.

---

# RELEASE-007 — Configure Secure PyPI Publishing

**Status:** Completed

Implemented:

1. added a publishing job that runs only after the validated tagged build
2. passed only the tag-specific retained artifact into that job
3. configured PyPI trusted publishing without a stored password or API token
4. granted `id-token: write` only to the publishing job
5. bound publishing to the protected GitHub environment named `pypi`
6. kept checkout, Python setup, project execution, building, and validation out
   of the identity-enabled job
7. documented the exact GitHub and PyPI account-side configuration
8. added permanent security and ordering regressions

Trusted-publisher identity:

```text
PyPI project: python-ai-toolkit
GitHub owner: bkocii
GitHub repository: python-ai-toolkit
Workflow: release.yml
Environment: pypi
```

Completion verification:

```text
21 release-workflow regressions passed
29 combined CI and release-workflow regressions passed
69 focused release, CI, package-metadata, and documentation tests passed
375 normal tests passed
both workflow YAML files parsed successfully
all 128 Python files passed Black
repository-wide Ruff check passed
strict Twine and offline archive validation passed for the clean-source build
```

No production tag was created and no package was uploaded. The documented
one-time GitHub environment and PyPI publisher setup must be completed before
the first release.

No runtime API, dependency declaration, package metadata, provider behavior,
benchmark contract, example behavior, or architectural decision changed.

---

# RELEASE-008 — Document Release Procedure

**Status:** Completed

Implemented:

1. added `docs/releasing.md` as the authoritative maintainer checklist
2. documented one-time GitHub and PyPI trusted-publisher configuration
3. documented version/changelog preparation, local quality, clean builds,
   validation, artifact installation, review, and final-main verification
4. documented annotated tag creation and exact tag-to-commit comparison
5. documented protected publishing approval and clean PyPI installation smoke
   testing
6. documented recovery without moving pushed tags or reusing PyPI filenames
7. linked the guide from the README and installation documentation
8. added permanent release-documentation regressions

Completion verification:

```text
6 release-documentation regressions passed
57 focused release, CI, and documentation tests passed
76 focused release, CI, package-metadata, and documentation tests passed
382 normal tests passed
both workflow YAML files parsed successfully
all 129 Python files passed Black
repository-wide Ruff check passed
strict Twine and offline archive validation passed for the clean-source build
```

No tag, workflow release run, GitHub deployment approval, PyPI project
creation, distribution upload, or GitHub Release occurred.

No runtime API, dependency declaration, package metadata, workflow permission,
provider behavior, benchmark contract, example behavior, or architectural
decision changed.

---

# RELEASE-009 Completion

`RELEASE-009 — Test Release Workflow Without Publishing Production Artifacts`
is complete.

The existing release workflow now supports a manual rehearsal with a validated
tag-shaped label. It runs the exact release identity, Python 3.11–3.14 quality,
build, Twine, archive, and artifact jobs from the selected commit without
creating a Git tag.

The publishing job remains restricted to a real tag push. Manual rehearsals
therefore skip the entire job before the protected `pypi` environment or OIDC
permission can be used. The release guide documents the expected green jobs,
skipped publish result, artifact inspection, cleanup, and the deliberate
exclusion of a real PyPI upload.

Completion evidence:

```text
23 release-workflow regressions passed
8 release-documentation regressions passed
80 focused release, CI, package-metadata, and documentation tests passed
386 normal tests passed independently on Python 3.11, 3.12, 3.13, and 3.14
pip check, Black, and Ruff passed on all four supported interpreters
both workflow YAML files parsed successfully
wheel and source distribution passed strict Twine and offline validation
```

No Git tag, GitHub deployment, PyPI project, distribution upload, or GitHub
Release was created.

---

# V1-001 — Version 1.0 Public API Freeze

`V1-001` is complete.

The task approved 71 public symbols, explicit module import paths, callable
parameters, model fields, enums, exceptions, extension interfaces, advanced
return boundaries, mutability, and partial-execution semantics.

It also:

1. added automatic structural configuration validation to both client
   construction paths
2. retained an empty top-level `ai` namespace
3. kept direct executor, request-builder wiring, built-in adapters, and
   low-level helpers internal
4. removed duplicate current-message content from agent prompts
5. added complete multi-agent name preflight
6. made empty multi-agent responses unsuccessful
7. added ADR-0017 and ADR-0018
8. added permanent public-contract and behavior tests

Completion evidence:

```text
62 focused public API, client, agent, and orchestration tests passed
409 normal tests passed on each supported Python version
```

No package version, release tag, GitHub deployment, PyPI project, distribution
upload, or publication changed.

---

# V1-002 — Release-Blocking Defects

`V1-002` is complete.

The task reproduced and corrected:

1. explicit configuration values that escaped structural type validation or
   raised raw Python exceptions
2. incomplete, invalid, negative, or non-finite custom pricing
3. non-object provider tool arguments
4. invalid, duplicate, missing, or out-of-order embedding indices
5. provider-factory tests that depended on ambient SDK transport/proxy setup
6. unsupported-provider coverage that did not execute its named failure path
7. installed-core verification that omitted plain and structured client
   requests

The complete scope and excluded non-blockers are recorded in:

```text
docs/development/release_blocker_audit.md
```

Completion evidence:

```text
166 focused configuration, provider, package, and documentation checks passed
440 normal tests passed on Python 3.11, 3.12, 3.13, and 3.14
Black, Ruff, and pip check passed on every supported Python version
clean wheel and source archive passed strict Twine and offline validation
core-only, Django-only, and FastAPI-only clean wheel checks passed
```

The 71-symbol frozen public API, dependency set, package version, classifiers,
release workflows, Git tags, GitHub deployments, and PyPI state did not change.

---

# V1-003 — Complete Changelog

`V1-003` is complete.

The anonymous unreleased change list and never-released `0.7.0.dev0` milestone
were consolidated into one `1.0.0 — Unreleased` section. It now separates
additions, behavior changes, fixes, security, compatibility and upgrade notes,
and maintainer release readiness.

The changelog records the frozen import and return boundaries, explicit
configuration upgrade impact, provider capability limits, optional framework
extras, asynchronous limits, and every confirmed `V1-002` fix. The released
`0.1.0` through `0.6.0` history remains intact.

Completion evidence:

```text
6 focused changelog regressions passed
446 normal tests passed on Python 3.11, 3.12, 3.13, and 3.14
Black and Ruff passed all 132 Python files on every supported interpreter
dependency validation passed on every supported interpreter
```

No runtime API, dependency, package version, classifier, workflow, tag,
deployment, PyPI project, distribution upload, or publication changed.

---

# V1-004 — Update Project Version to 1.0.0

`V1-004` is complete.

The authoritative package version is now `1.0.0`, and the maturity classifier
is Production/Stable. Current status text, release-rehearsal identity,
distribution filenames, clean-install assertions, release-tag examples, and
core/framework installation verifiers all use the same version.

The Version 1 changelog remains `Unreleased` with no release date. Historical
`0.7.0.dev0` task, artifact, installation, and workflow evidence remains
unchanged.

Completion evidence:

```text
64 focused version, package, changelog, release-guide, and workflow checks passed
453 normal tests passed on Python 3.11, 3.12, 3.13, and 3.14
Black passed all 133 Python files on every supported interpreter
Ruff and dependency validation passed on every supported interpreter
release tag v1.0.0 matched package version 1.0.0
strict Twine and offline validation passed the 46-entry wheel and 101-entry source archive
core wheel and source-archive installation checks passed
Django-only and FastAPI-only wheel installation checks passed
```

No runtime API, dependency, release workflow, Git tag, GitHub deployment, PyPI
project, distribution upload, or publication changed.

---

# Exact Next Task — V1-005

Update the project state for the `1.0.0` release-preparation stage.

Required work:

1. reconcile the project-state summary with completed `V1-001` through
   `V1-004` work
2. remove stale next-task and pre-Version-1 status language
3. preserve detailed historical completion evidence
4. point the authoritative project state to
   `V1-006 — Complete release documentation`
5. do not create `v1.0.0`, approve a deployment, or publish

---

# EXAMPLE-008 Verification and Repository State

Changed project files:

```text
README.md
CHANGELOG.md
docs/development/example_verification.md
docs/development/roadmap.md
docs/development/project_state.md
docs/development/session_handoff.md
examples/README.md
tests/test_documentation_examples.py
tests/test_examples.py
```

No production runtime API, example implementation, provider adapter, package
dependency, benchmark, or ADR changed.

Suggested focused commit:

```powershell
git add `
    README.md `
    CHANGELOG.md `
    docs\development\example_verification.md `
    docs\development\roadmap.md `
    docs\development\project_state.md `
    docs\development\session_handoff.md `
    examples\README.md `
    tests\test_documentation_examples.py `
    tests\test_examples.py

git diff --cached
git commit -m "test: verify examples against public APIs"
```

---

# EXAMPLE-007 Verification and Repository State

Changed project files:

```text
README.md
CHANGELOG.md
docs/development/example_verification.md
docs/development/roadmap.md
docs/development/project_state.md
docs/development/session_handoff.md
examples/README.md
tests/test_documentation_examples.py
```

No production runtime API, example implementation, provider adapter, package
dependency, benchmark, or ADR changed.

Suggested focused commit:

```powershell
git add `
    README.md `
    CHANGELOG.md `
    docs\development\example_verification.md `
    docs\development\roadmap.md `
    docs\development\project_state.md `
    docs\development\session_handoff.md `
    examples\README.md `
    tests\test_documentation_examples.py

git diff --cached
git commit -m "docs: normalize example descriptions"
```

---

# DOC-014 Verification and Repository State

Changed project files:

```text
CHANGELOG.md
docs/advanced_requests.md
docs/retrieval.md
docs/development/example_verification.md
docs/development/roadmap.md
docs/development/project_state.md
docs/development/session_handoff.md
examples/09_1_structured_image_with_helper.py
examples/README.md
tests/test_documentation_examples.py
tests/test_examples.py
```

No production runtime API, provider adapter, package dependency, public import
path, benchmark, or ADR changed.

Suggested focused commit:

```powershell
git add `
    README.md `
    CHANGELOG.md `
    docs\api_reference.md `
    docs\advanced_requests.md `
    docs\compatibility.md `
    docs\configuration.md `
    docs\error_handling.md `
    docs\integrations.md `
    docs\orchestration.md `
    docs\providers.md `
    docs\requests.md `
    docs\retrieval.md `
    docs\security.md `
    docs\development\roadmap.md `
    docs\development\project_state.md `
    docs\development\session_handoff.md

git diff --cached
git commit -m "docs: add public API reference"
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

Package metadata accepts Python `>=3.11`; the Version 1.0 CI matrix tests Python
3.11 through 3.14 independently.

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
7. `CHANGELOG.md`
8. `pyproject.toml`
9. `docs/installation.md`
10. `docs/compatibility.md`
11. `docs/releasing.md`
12. version-coupled scripts and tests
13. current completed roadmap records

Profiling evidence, generated benchmark artifacts, release artifacts,
deliverable ZIPs, caches, example media, and future-backlog implementation
files are not required for `V1-004`. Package metadata, current-status
documentation, installation examples, release commands, and version-coupled
verifiers are required so the version update is complete without rewriting
historical evidence.

Do not upload the entire repository unless necessary. Provide the authoritative documents and the current files relevant to the next task.

---

# Suggested First Message in the New Chat

```text
Continue the Python AI Toolkit project using the attached session handoff and source-of-truth documents.

First:
1. Read session_handoff.md.
2. Read project_state.md, roadmap.md, architecture.md, and future_backlog.md.
3. Verify the repository's current state and confirm that V1-004 is still the correct next task.
4. Read pyproject.toml, CHANGELOG.md, README.md, docs/installation.md, docs/compatibility.md, and docs/releasing.md.
5. Update the project version to 1.0.0 and every current-version coupling without creating a tag or publishing.

Do not redesign the project, skip roadmap order, or assume older file contents.
Follow the workflow: design → code → tests → documentation → review → git → roadmap update.
```

---

# Final Instruction

If anything is unclear, inspect the project files first.

Do not guess.

If a previous implementation might have changed, request or inspect the current file before proposing modifications.

Architecture consistency, correctness, and evidence-driven decisions are more important than adding features quickly.
