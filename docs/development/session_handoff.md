# Python AI Toolkit — Session Handoff

## Project

**Project:** Python AI Toolkit  
**Current version:** `0.7.0-dev`  
**Current milestone:** Sprint 9 — Production Readiness  
**Active roadmap item:** `PROD-002 — Performance Profiling`  
**Next task:** `PROF-007 — Review optimization candidates`

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

**Status:** Completed

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

**Status:** Active

Roadmap tasks:

- [x] `PROF-001` — Establish baseline
- [x] `PROF-002` — Profile plain request execution
- [x] `PROF-003` — Profile structured parsing and repair
- [x] `PROF-004` — Profile vector search
- [x] `PROF-005` — Profile RAG orchestration
- [x] `PROF-006` — Profile workflow execution
- [ ] `PROF-007` — Review optimization candidates
- [ ] `PROF-008` — Implement approved optimizations
- [ ] `PROF-009` — Complete profiling documentation

The next task is `PROF-007`.

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

# Exact Next Task — PROF-007

Review all measured optimization candidates before approving any additional
runtime implementation.

The review should:

1. rank bottlenecks by measurable absolute impact
2. separate toolkit implementation overhead from dependency overhead
3. identify candidates that preserve public APIs and typed contracts
4. reject premature or low-value changes explicitly
5. document architectural tradeoffs
6. select only candidates justified for `PROF-008`
7. record paths where no runtime change is recommended

At minimum, compare:

- repeated structured-schema generation from `PROF-003`
- remaining vector-search costs after the `PROF-004` optimization
- retrieved-context formatting from `PROF-005`
- workflow Pydantic model construction from `PROF-006`
- intentional observability overhead remaining after `PROF-002`

Do not implement candidates during `PROF-007`. Approved runtime changes, if
any, belong to `PROF-008`.

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

# Minor Issue Discovered

`ai/config_validator.py` contains the same `embedding_dimensions` validation block twice.

This is not a blocker for `PROF-007` and should not derail the active roadmap.

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

Known local environment:

- Windows
- PowerShell
- PyCharm
- CPython 3.14.4 for the current profiling session
- project supports Python `>=3.11`

`ripgrep` (`rg`) is not installed in the current environment.

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

6. `profiling/profile_request_lifecycle.py`
7. `profiling/profile_structured_execution.py`
8. `profiling/profile_vector_search.py`
9. `profiling/profile_rag_orchestration.py`
10. `profiling/profile_workflow_execution.py`

Useful profiling evidence, if the new session needs to audit prior conclusions:

- `.benchmarks/profile-request-lifecycle-before.txt`
- `.benchmarks/profile-request-lifecycle-after.txt`
- `.benchmarks/profile-vector-scaling.txt`
- `.benchmarks/profile-structured-execution.txt`
- `.benchmarks/profile-rag-orchestration.txt`
- `.benchmarks/profile-workflow-execution.txt`
- `.benchmarks/prof-003-baseline.json`
- `.benchmarks/prof-005-baseline.json`
- `.benchmarks/prof-006-baseline.json`
- original baseline benchmark JSON
- optimized plain-request benchmark JSON

Do not upload the entire repository unless necessary. Provide the authoritative documents and the current files relevant to the next task.

---

# Suggested First Message in the New Chat

```text
Continue the Python AI Toolkit project using the attached session handoff and source-of-truth documents.

First:
1. Read session_handoff.md.
2. Read project_state.md, roadmap.md, architecture.md, and future_backlog.md.
3. Verify the repository's current state and confirm that PROF-007 is still the correct next task.
4. Review the completed profiling evidence before ranking optimization candidates.

Do not redesign the project, skip roadmap order, or assume older file contents.
Follow the workflow: design → code → tests → documentation → review → git → roadmap update.
```

---

# Final Instruction

If anything is unclear, inspect the project files first.

Do not guess.

If a previous implementation might have changed, request or inspect the current file before proposing modifications.

Architecture consistency, correctness, and evidence-driven decisions are more important than adding features quickly.
