# Roadmap

## Vision

Build a reusable, provider-independent AI engineering toolkit for Python.

The toolkit should provide production-quality infrastructure for integrating
Large Language Models (LLMs) into applications while keeping business logic
outside the toolkit.

---

# Current Version

0.7.0-dev

---

# Development Workflow

Every task follows the same lifecycle.

1. Design
2. Code
3. Tests
4. Documentation
5. Review
6. Git
7. Roadmap Update
8. Project State Update (only when milestone changes)

A task is not complete until every step has been completed.

---

# Sprint 2 – Core Infrastructure Refinement

## Goal

Refine the existing architecture without introducing new user-facing features.

### Completed

- [x] CORE-001 Create architecture documentation
- [x] CORE-002 Create Architecture Decision Records (ADRs)
- [x] CORE-003 Create project roadmap
- [x] CORE-004 Remove duplicate success logging
- [x] CORE-005 Extract retry prompt helper
- [x] CORE-006 Configurable retry count

### Remaining

Exit Criteria

- [x] Core architecture documented
- [x] RequestExecutor cleaned up
- [x] Retry configurable
- [x] Sprint documentation complete

---

# Sprint 3 – Provider Infrastructure

## Goal

Support multiple AI providers without changing application code.

Tasks

- [x] PROVIDER-001 ProviderFactory
- [x] PROVIDER-002 Provider registry
- [x] PROVIDER-003 Provider Registration API
- [x] PROVIDER-004 Provider configuration cleanup

Exit Criteria

- [x] Adding a new provider requires no changes to AIClient.

---

# Sprint 4 – Developer Experience

## Goal

Improve usability for developers.

Tasks

- [x] DX-001 Fluent Request Builder
- [x] DX-002 Prompt templates
- [x] DX-003 Example gallery
- [x] DX-004 Configuration validation improvements
- [x] DX-005 Better error messages

Exit Criteria

- [x] Building prompts should require minimal boilerplate.

---

# Sprint 5 – Advanced Requests

## Goal

Support advanced LLM capabilities.

Tasks

- [x] REQUEST-001 Streaming responses
- [x] REQUEST-002 Async AIClient
- [x] REQUEST-003 Tool Calling
- [x] REQUEST-004 Image inputs
- [x] REQUEST-005 Structured output improvements

Exit Criteria

- [x] Modern provider capabilities fully supported.

---

# Sprint 6 – Retrieval & Knowledge

## Goal

Support Retrieval-Augmented Generation (RAG).

Tasks

- [x] RAG-001 Embeddings
- [x] RAG-002 Vector Store abstraction
- [x] RAG-003 Retriever interface
- [x] RAG-004 RAG Pipeline
- [x] RAG-005 Document loaders

Exit Criteria

- [x] Toolkit supports end-to-end RAG workflows.

---

# Sprint 7 – Agents & Workflows

## Goal

Build reusable autonomous AI workflows.

Tasks

- [x] AGENT-001 Conversation memory
- [x] AGENT-002 Agent abstraction
- [x] AGENT-003 Workflow engine
- [x] AGENT-004 Multi-agent orchestration

Exit Criteria

- [x] Complex AI workflows can be composed from reusable components.

---

# Sprint 8 – Framework Integrations

## Goal

Integrate with common Python ecosystems.

Tasks

- [x] INTEGRATION-001 Django integration
- [x] INTEGRATION-002 FastAPI integration
- [x] INTEGRATION-003 Command Line Interface
- [x] INTEGRATION-004 Configuration CLI

Exit Criteria

- [x] Toolkit easily integrates into existing Python applications.

---

# Sprint 9 – Production Readiness

## Goal

Prepare the toolkit for a stable Version 1.0 release.

Sprint 9 is a stabilization sprint.

It should improve:

* performance visibility
* test and benchmark coverage
* documentation completeness
* packaging reliability
* release automation
* public API stability

Sprint 9 should not introduce new feature areas unless they are required to fix a release-blocking problem.
---

### BENCH-000 — Test-Safe and Benchmark-Safe Logging

#### Goal

Prevent file logging from distorting benchmarks, creating test artifacts, or
writing unexpectedly during clean package verification.

#### Tasks

- [x] LOG-001 Add configurable log level
- [x] LOG-002 Add configurable log file path
- [x] LOG-003 Add an option to disable file logging
- [x] LOG-004 Disable file logging in benchmark execution
- [x] LOG-005 Support test-safe logging without modifying application behavior
- [x] LOG-006 Add logging configuration tests
- [x] LOG-007 Document logging environment variables

#### Requirements

- Existing application logging behavior remains the default.
- Tests and benchmarks can disable file logging explicitly.
- Importing the toolkit must not create a log file unnecessarily.
- Disabling file logging must not disable all logging unless requested.
- Console and file handlers must remain separate concerns.
- Prompts and model responses must remain excluded from logs.
- Invalid log levels must produce helpful configuration errors.

#### Exit Criteria

- [x] Benchmarks can run without writing to `logs/ai_toolkit.log`
- [x] Tests do not require a writable `logs` directory
- [x] Log path and level are configurable
- [x] Existing request metadata logging remains functional
- [x] Logging tests, Black, Ruff, and the full test suite pass

---

### PROD-001 — Benchmark Suite

Status: Completed

Goal:

Establish deterministic performance baselines for the toolkit's main internal execution paths before Version 1.0.

The benchmark suite must measure toolkit overhead rather than network latency, model execution, provider availability, or machine-specific external services.

#### BENCH-000 — Make Logging Safe for Tests and Benchmarks

* [x] Add configurable log level
* [x] Add configurable log file path
* [x] Add an option to disable toolkit-managed file logging
* [x] Disable file logging during benchmark execution
* [x] Preserve application-owned logging handlers
* [x] Support synchronous and asynchronous executor logger injection
* [x] Add logging configuration and behavior tests
* [x] Document logging configuration

#### BENCH-001 — Add Benchmark Tooling

* [x] Add a separate benchmark dependency group
* [x] Add `pytest-benchmark`
* [x] Create the isolated `benchmarks/` directory
* [x] Add benchmark-specific fixtures
* [x] Exclude benchmarks from normal test discovery
* [x] Ignore generated benchmark result files
* [x] Add a benchmark smoke test
* [x] Document benchmark execution

#### BENCH-002 — Add Deterministic Fake Providers and Fixtures

* [x] Add a deterministic synchronous provider
* [x] Add a deterministic asynchronous provider
* [x] Add a sequential retry provider
* [x] Add shared token-usage fixtures
* [x] Add shared provider-response fixtures
* [x] Add a no-output benchmark logger
* [x] Add fake-provider correctness tests
* [x] Add benchmark fixture correctness tests

#### BENCH-003 — Benchmark Plain Request Lifecycle

* [x] Benchmark synchronous plain-text request execution
* [x] Use a deterministic fake provider
* [x] Exclude executor and provider construction
* [x] Exclude file and console logging I/O
* [x] Verify returned `AIResult`

#### BENCH-004 — Benchmark Structured Response Parsing

* [x] Add deterministic valid JSON input
* [x] Add a representative Pydantic schema
* [x] Benchmark JSON decoding and schema validation
* [x] Exclude provider and request lifecycle overhead
* [x] Verify parsed-model correctness

#### BENCH-005 — Benchmark Retry and Repair Lifecycle

* [x] Add deterministic invalid and repaired responses
* [x] Reset provider state before each measured round
* [x] Benchmark one successful retry and repair cycle
* [x] Include repair prompt construction
* [x] Include token-usage aggregation
* [x] Verify original response, repaired response, and retry metadata

#### BENCH-006 — Benchmark Vector Search

* [x] Add 1,000 deterministic vector records
* [x] Use 64-dimensional vectors
* [x] Benchmark unfiltered similarity search
* [x] Benchmark metadata-filtered similarity search
* [x] Exclude dataset and vector-store construction
* [x] Verify ranking, result limits, and metadata filtering

#### BENCH-007 — Benchmark RAG Orchestration

* [x] Add deterministic retrieved contexts
* [x] Add a no-I/O retriever
* [x] Add a no-I/O AI client
* [x] Benchmark context formatting
* [x] Benchmark grounded prompt construction
* [x] Benchmark RAG response assembly
* [x] Exclude vector search and provider execution
* [x] Verify returned answer, contexts, and metadata

#### BENCH-008 — Benchmark Workflow Execution Overhead

* [x] Benchmark a one-step workflow
* [x] Benchmark a five-step workflow
* [x] Prebuild workflow engines and steps
* [x] Include fresh context creation
* [x] Include state propagation
* [x] Include step and workflow result construction
* [x] Verify step order, state, success, and final output

#### BENCH-009 — Document and Review the Benchmark Suite

* [x] Add a complete benchmark catalog
* [x] Document measured and excluded operations
* [x] Document normal-test and benchmark-test isolation
* [x] Document benchmark-only expected behavior
* [x] Document clean-run verification
* [x] Document local result saving and comparison
* [x] Document benchmark interpretation
* [x] Document benchmark stability policy
* [x] Document rules for future benchmarks
* [x] Review benchmark correctness and deterministic behavior
* [x] Complete benchmark-suite validation

#### Exit Criteria

* [x] Normal tests do not automatically execute benchmarks
* [x] Performance benchmarks run explicitly through `pytest-benchmark`
* [x] Benchmarks require no real API keys
* [x] Benchmarks perform no network calls
* [x] Benchmarks perform no provider or model execution
* [x] Toolkit-managed file logging is disabled during benchmarks
* [x] Benchmark inputs and responses are deterministic
* [x] Unrelated setup work is excluded from timing
* [x] Every benchmark contains correctness assertions
* [x] No strict machine-specific timing thresholds are used
* [x] Generated benchmark results are ignored by Git
* [x] Benchmark usage and interpretation are documented
* [x] The normal test suite passes
* [x] All benchmark correctness checks pass
* [x] All performance benchmarks pass
* [x] Black passes
* [x] Ruff passes

Result:

Python AI Toolkit now has a deterministic internal performance baseline covering request execution, structured parsing, response repair, vector search, RAG orchestration, and workflow execution.

### PROD-002 — Performance Profiling

Status: Completed with documented pre-existing quality-check exceptions

Goal:

Profile the toolkit's benchmarked execution paths, identify meaningful internal bottlenecks, and document evidence before making performance-related implementation changes.

Performance work must remain evidence-driven.

Implementation code should not be changed merely because a function appears complex. A bottleneck must first be measured, reproduced, profiled, and reviewed against correctness and architectural tradeoffs.

#### PROF-001 — Capture the Performance Baseline

* [x] Run the complete benchmark suite
* [x] Save a local pre-optimization benchmark baseline
* [x] Record the Python version and operating environment
* [x] Confirm that benchmarks require no API keys
* [x] Confirm that benchmark execution creates no toolkit log files
* [x] Identify the slowest benchmarked execution paths
* [x] Keep machine-specific benchmark files out of Git

Baseline environment:

* Operating system: Windows 11, 64-bit
* Python implementation: CPython
* Python version: 3.14.4
* Processor: 11th Gen Intel Core i5-1135G7
* Logical processors: 8
* Benchmark commit: `91fed29585de55836b640798c754434d3c7f8733`
* Working tree during capture: dirty

Slowest measured paths:

1. Unfiltered in-memory vector similarity search — approximately `19.407 ms`
2. Metadata-filtered vector similarity search — approximately `8.889 ms`
3. Structured-response retry and repair — approximately `0.304 ms`

Logging verification:

* the `logs/` directory was removed before isolated benchmark execution
* the complete benchmark suite was executed with `--benchmark-only`
* `Test-Path logs` returned `False`
* toolkit-managed file logging remained disabled

Decision:

Begin detailed profiling with `InMemoryVectorStore.similarity_search()` because vector search dominates the deterministic benchmark suite.

The baseline must be repeated from a clean Git working tree before final before-and-after comparisons are accepted.

#### PROF-002 — Profile Plain Request Execution

* [x] Profile the plain request lifecycle
* [x] Measure request ID generation
* [x] Measure provider-call overhead
* [x] Measure cost estimation
* [x] Measure success-logging overhead
* [x] Measure `AIResult` construction
* [x] Identify repeated configuration loading
* [x] Implement pre-resolved request pricing
* [x] Avoid unnecessary logging metadata serialization
* [x] Verify synchronous and asynchronous behavior
* [x] Verify performance with repeated benchmarks

Profiling environment:

* deterministic local provider
* no network requests
* fixed provider response
* fixed token usage
* 100,000 repeated plain requests
* executor, provider, logger, and response created before profiling
* INFO-level logger with `NullHandler` used to retain logging overhead without console or file output

Initial profile:

* approximately `19.1 million` function calls
* approximately `11.443 seconds` total profile time
* approximately `11.583 seconds` cumulative time inside `RequestExecutor.execute()`
* approximately `5.808 seconds` inside cost estimation
* approximately `5.384 seconds` repeatedly resolving `AIConfig`
* approximately `4.093 seconds` inside success logging
* approximately `0.531 seconds` constructing `AIResult`
* approximately `0.404 seconds` generating request UUIDs

Primary finding:

The plain request lifecycle repeatedly loaded and validated the complete toolkit configuration while estimating request cost.

For 100,000 requests, this caused:

* 100,000 complete configuration resolutions
* repeated logging-configuration resolution
* repeated configuration validation
* approximately 1.1 million environment-variable lookups
* unnecessary request-time API-key and model resolution

Accepted cost optimization:

* separate pricing resolution from cost arithmetic
* resolve model or custom token prices when an executor is constructed
* store resolved prices on `RequestExecutor` and `AsyncRequestExecutor`
* perform only token-cost arithmetic during request execution
* pass custom pricing from `AIClient` and `AsyncAIClient`
* retain `estimate_cost_usd()` as a compatibility wrapper for direct callers
* preserve model-price fallback for directly constructed executors
* avoid requiring API configuration for direct executor construction

Accepted logging optimization:

* check `logger.isEnabledFor(logging.INFO)` before creating logging metadata
* avoid calling `TokenUsage.model_dump()` when INFO logging is disabled
* apply the same behavior to synchronous and asynchronous executors
* retain complete success metadata when INFO logging is enabled

Post-optimization profile:

* function calls reduced from approximately `19.1 million` to `8.1 million`
* total profile time reduced from approximately `11.443 seconds` to `4.153 seconds`
* reduction in total profile time: approximately `63.7%`
* configuration loading and environment lookup disappeared from the request hot path
* INFO logging became the largest remaining contributor
* `AIResult` construction, UUID generation, and cost arithmetic remained comparatively small

Benchmark verification:

The benchmark logger uses a CRITICAL level, which exercises the early logging guard and measures the normal low-overhead request path.

Before optimization:

* mean: approximately `27.292 µs`
* median: approximately `25.800 µs`
* throughput: approximately `36,640` operations per second

After optimization:

* mean: approximately `4.551 µs`
* median: approximately `4.400 µs`
* throughput: approximately `219,756` operations per second

Measured improvement:

* mean request overhead reduced by approximately `83.3%`
* median request overhead reduced by approximately `82.9%`
* throughput increased by approximately six times

Correctness coverage added:

* explicit pricing resolution
* unknown-model pricing
* cost arithmetic using pre-resolved prices
* missing token usage
* missing pricing
* compatibility configuration-based pricing
* synchronous executor custom pricing
* asynchronous executor custom pricing
* synchronous disabled-INFO logging guard
* asynchronous disabled-INFO logging guard

Conclusion:

The optimization removed configuration and environment access from the request hot path while preserving request IDs, cost tracking, logging, token metadata, synchronous execution, asynchronous execution, and the existing public cost-estimation function.

No additional plain-request optimization is currently justified.

Remaining INFO-level logging cost is intentional observability overhead. Applications that disable INFO logging now avoid log-record creation and token-metadata serialization.

Rejected optimization candidates:

* removing request UUID generation, because request IDs are valuable observability metadata and represent a small portion of total execution time
* bypassing Pydantic `AIResult` validation, because its cost is small and it protects the public result contract
* disabling success logging globally, because logging behavior should remain configurable
* caching complete `AIConfig` inside the cost compatibility wrapper, because executors already avoid that path and global caching could create stale environment-dependent behavior


#### PROF-003 — Profile Structured Responses and Repair

* [x] Profile successful structured-response parsing
* [x] Profile JSON decoding
* [x] Profile Pydantic validation
* [x] Profile failed parsing and repair prompt construction
* [x] Profile token-usage aggregation
* [x] Compare successful parsing with one-retry repair
* [x] Document meaningful call-time contributors

Profiling environment:

* Linux 64-bit
* CPython 3.12.13
* Pydantic 2.13.4
* deterministic local providers
* no network requests
* INFO-level logger with `NullHandler`
* explicit token pricing to retain cost-calculation work
* 50,000 repeated component operations
* 25,000 repeated successful structured requests
* 25,000 repeated one-retry repair requests
* providers, responses, executors, logger, and input data created before profiling

Profiling artifacts:

* `profiling/profile_structured_execution.py`
* `.benchmarks/profile-structured-execution.txt`
* `.benchmarks/prof-003-baseline.json`

Component profile:

* structured-prompt construction: approximately `20.125 seconds` cumulative
  for 50,000 operations
* Pydantic `model_json_schema()`: approximately `19.9 seconds` cumulative
  inside prompt construction
* JSON decoding: approximately `0.129 seconds` cumulative for 50,000
  operations
* Pydantic model validation: approximately `0.051 seconds` cumulative for
  50,000 operations
* combined JSON decoding and Pydantic validation: approximately `0.236 seconds`
  cumulative for 50,000 operations
* repair-prompt construction: approximately `0.005 seconds` cumulative for
  50,000 operations
* token-usage aggregation: approximately `0.053 seconds` cumulative for
  50,000 operations
* `AIResult` model construction: approximately `0.054 seconds` cumulative for
  50,000 operations

Successful structured lifecycle:

* approximately `11.824 seconds` cumulative inside `RequestExecutor.execute()`
  for 25,000 requests
* approximately `10.536 seconds` in structured-prompt construction
* structured-prompt construction represented approximately `89.1%` of
  executor time
* success logging represented approximately `5.1%`
* combined structured parsing represented approximately `2.1%`
* result construction and cost calculation were each below `1%`
* the deterministic provider call was negligible

One-retry repair lifecycle:

* approximately `12.195 seconds` cumulative inside `RequestExecutor.execute()`
  for 25,000 requests
* approximately `10.576 seconds` in structured-prompt construction
* structured-prompt construction represented approximately `86.7%` of
  executor time
* success logging represented approximately `5.1%`
* two parse attempts represented approximately `3.4%`
* token aggregation represented approximately `0.6%`
* result construction, retry-provider calls, repair-prompt construction, and
  cost calculation were each below `1%`

Focused benchmark verification:

* successful structured parsing median: approximately `2.544 µs`
* one-retry repair median: approximately `99.838 µs`
* benchmark results were captured on the profiling environment and are not
  directly comparable with the earlier Windows baseline

Primary finding:

`build_structured_prompt()` regenerates the complete Pydantic JSON schema for
the same response model on every request. This dependency work dominates both
the normal structured path and the one-retry repair path.

JSON decoding is the largest part of successful response parsing, but complete
parsing remains small compared with repeated JSON-schema generation.

The additional repair work is measurable but secondary. Repair-prompt string
construction itself is negligible; the extra parse attempt, exception path,
provider call, and token aggregation account for most of the difference.

Optimization candidate for `PROF-007`:

* review safe caching of the response model's serialized schema instruction
* preserve `build_structured_prompt()` and all public request APIs
* define cache invalidation behavior for dynamically rebuilt Pydantic models
  before approving implementation
* benchmark the candidate separately before and after any runtime change

Conclusion:

No runtime implementation was changed during `PROF-003`. The profiling task
collected and documented evidence, while optimization approval remains deferred
to `PROF-007` and implementation remains deferred to `PROF-008`.

#### PROF-004 — Profile Vector Search

* [x] Profile unfiltered vector similarity search
* [x] Profile metadata-filtered vector search
* [x] Measure candidate collection and metadata-filter contribution
* [x] Measure cosine similarity calculations
* [x] Measure `VectorSearchResult` construction
* [x] Measure result sorting and limiting
* [x] Confirm scaling behavior of the linear scan
* [x] Document meaningful call-time contributors
* [x] Implement and verify an approved optimization

Profiling environment:

* 1,000 vector records
* 64 dimensions per vector
* result limit of 5
* 100 repeated searches per profile
* dataset construction excluded from profiling

Initial unfiltered profile:

* approximately `20.7 million` function calls
* approximately `6.309 seconds` inside `similarity_search()`
* approximately `5.729 seconds` inside `_cosine_similarity()`
* approximately `5.342 seconds` inside the three generator-based `sum()` operations
* approximately `0.320 seconds` constructing Pydantic search-result models
* approximately `0.045 seconds` sorting results

Initial metadata-filtered profile:

* approximately `10.8 million` function calls
* approximately `3.681 seconds` inside `similarity_search()`
* approximately `3.113 seconds` inside `_cosine_similarity()`
* approximately `2.902 seconds` inside the three generator-based `sum()` operations
* approximately `0.233 seconds` applying metadata filters
* approximately `0.175 seconds` constructing Pydantic search-result models
* approximately `0.025 seconds` sorting results

Primary finding:

Cosine similarity calculation was the dominant vector-search cost.

The original implementation recalculated the following values for every candidate:

* query-vector magnitude
* stored-vector magnitude
* dot product

Each value was calculated through a separate generator expression and `sum()` pass.

Accepted optimization:

* calculate the query-vector norm once per search
* calculate the candidate dot product and squared norm in one direct loop
* preserve the existing public vector-store API
* retain the original private two-vector cosine helper interface
* avoid persistent stored-vector norm caching while `VectorRecord.vector` remains mutable

Post-optimization profile:

Unfiltered search:

* function calls reduced from approximately `20.7 million` to `807,102`
* total profile time reduced from approximately `6.356 seconds` to `1.453 seconds`
* cosine calculation time reduced from approximately `5.729 seconds` to `0.819 seconds`

Metadata-filtered search:

* function calls reduced from approximately `10.8 million` to `857,102`
* total profile time reduced from approximately `3.707 seconds` to `0.982 seconds`
* cosine calculation time reduced from approximately `3.113 seconds` to `0.424 seconds`

Benchmark verification:

The optimized implementation was benchmarked twice against the original `prod-002-before` baseline.

Unfiltered vector search:

* baseline mean: approximately `18.984 ms`
* optimized run 1 mean: approximately `11.690 ms`
* optimized run 2 mean: approximately `13.037 ms`
* improvement range: approximately `31.3%` to `38.4%`
* average optimized mean: approximately `12.363 ms`
* average improvement: approximately `34.9%`

Metadata-filtered vector search:

* baseline mean: approximately `10.875 ms`
* optimized run 1 mean: approximately `6.852 ms`
* optimized run 2 mean: approximately `6.296 ms`
* improvement range: approximately `37.0%` to `42.1%`
* average optimized mean: approximately `6.574 ms`
* average improvement: approximately `39.5%`

Throughput improvement:

* unfiltered search increased from approximately `52.68` operations per second to between `76.71` and `85.54`
* filtered search increased from approximately `91.95` operations per second to between `145.94` and `158.84`

Scaling verification:

Unfiltered search:

* tested from `100` to `5,000` stored records
* estimated cost: approximately `8.2513 ms` per 1,000 scanned records
* linear-fit `R²`: `0.999993`

Metadata-filtered search:

* tested from `100` to `5,000` stored records
* all records were scanned
* approximately half of the records matched the filter and were scored
* estimated cost: approximately `4.5470 ms` per 1,000 scanned records
* linear-fit `R²`: `0.999295`

Conclusion:

Both search paths scale linearly with the number of stored records.

The filtered path has a lower cost per scanned record because nonmatching records do not proceed to cosine calculation, Pydantic result construction, or sorting.

The optimization consistently improved performance while preserving behavior and the public API.

Rejected optimization candidates:

* replacing complete sorting with a top-k heap, because sorting remained a negligible portion of execution time
* bypassing Pydantic result validation, because construction remained secondary and the change would weaken the public model contract
* persistent stored-vector norm caching, because mutable stored vectors could make cached magnitudes stale
* adding an external numeric dependency, because the current reference implementation remains intended for tests, demos, and small local applications



#### PROF-005 — Profile RAG Orchestration

* [x] Profile retrieved-context formatting
* [x] Profile grounded prompt construction
* [x] Profile additional-instruction formatting
* [x] Profile `RAGResponse` construction
* [x] Keep retrieval and provider execution excluded
* [x] Document meaningful call-time contributors

Profiling environment:

* deterministic local retriever returning five prebuilt contexts
* deterministic local AI client returning one prebuilt `AIResult`
* no embeddings, vector search, network requests, provider execution, logging,
  or file I/O inside the measured operations
* 100,000 repeated component operations
* 50,000 repeated complete RAG orchestration calls
* contexts, results, clients, and pipeline created before profiling

Component profile:

* retrieved-context formatting: approximately `0.452 seconds` for 100,000
  operations, or `4.52 µs` per operation under `cProfile`
* grounded-prompt construction without instructions: approximately
  `0.013 seconds` for 100,000 operations, or `0.13 µs` per operation
* grounded-prompt construction with instructions: approximately `0.016 seconds`
  for 100,000 operations, or `0.16 µs` per operation
* `RAGResponse` construction: approximately `0.078 seconds` for 100,000
  operations, or `0.78 µs` per operation
* Pydantic validation inside response construction: approximately
  `0.061 seconds` for 100,000 operations

Complete orchestration profile:

* approximately `0.408 seconds` inside `RAGPipeline.ask()` for 50,000 calls
* approximately `8.16 µs` per call under `cProfile`
* retrieved-context formatting accounted for approximately `64%` of cumulative
  orchestration time
* `RAGResponse` construction accounted for approximately `12%`
* grounded-prompt construction accounted for approximately `3%`
* deterministic retriever and AI-client stubs together accounted for less than
  `2%`

Focused benchmark verification:

* median RAG orchestration time: approximately `5.268 µs`
* mean RAG orchestration time: approximately `5.424 µs`
* approximately `184,373` operations per second
* benchmark measurements were captured on the profiling environment and are not
  directly comparable with the earlier Windows baseline

Primary finding:

Retrieved-context formatting is the largest internal contributor because it
formats the ID, score, optional metadata, and text for every returned context.
`RAGResponse` validation is secondary. Grounded-prompt construction and
additional-instruction formatting are negligible.

Conclusion:

No RAG-specific runtime optimization is recommended from this profile. Complete
toolkit orchestration takes only a few microseconds in the deterministic
benchmark and will normally be dominated by embedding, retrieval, network, and
provider execution.

Context formatting should remain visible during `PROF-007`, but its current
absolute cost does not justify weakening formatting clarity, bypassing Pydantic
validation, or adding caching complexity. No runtime implementation changed
during `PROF-005`.

#### PROF-006 — Profile Workflow Execution

* [x] Profile one-step workflow execution
* [x] Profile five-step workflow execution
* [x] Measure `WorkflowContext` construction
* [x] Measure workflow step-result construction
* [x] Measure state propagation
* [x] Measure final workflow-result construction
* [x] Compare one-step and five-step overhead
* [x] Document meaningful call-time contributors

Profiling environment:

* Linux 64-bit
* CPython 3.12.13
* Pydantic 2.13.4
* deterministic local workflow steps performing only small arithmetic operations
* no provider execution, network requests, logging, or file I/O inside the
  measured operations
* 100,000 repeated component operations
* 50,000 repeated complete one-step workflow executions
* 50,000 repeated complete five-step workflow executions
* workflows, inputs, metadata, contexts, and reusable result fixtures created
  before profiling where applicable

Profiling artifacts:

* `profiling/profile_workflow_execution.py`
* `.benchmarks/profile-workflow-execution.txt`
* `.benchmarks/prof-006-baseline.json`

Component profile:

* `WorkflowContext` construction: approximately `0.136 seconds` for 100,000
  operations, or `1.36 µs` per operation under `cProfile`
* `WorkflowStepResult` construction: approximately `0.162 seconds` for 100,000
  operations, or `1.62 µs` per operation
* state propagation through `dict.update()`: approximately `0.009 seconds` for
  100,000 updates, or `0.09 µs` per update
* `WorkflowRunResult` construction with one prebuilt step result:
  approximately `0.118 seconds` for 100,000 operations, or `1.18 µs` per
  operation
* `WorkflowRunResult` construction with five prebuilt step results:
  approximately `0.121 seconds` for 100,000 operations, or `1.21 µs` per
  operation

Complete execution profile:

* one-step `WorkflowEngine.run()`: approximately `0.260 seconds` for 50,000
  executions, or `5.20 µs` per execution under `cProfile`
* five-step `WorkflowEngine.run()`: approximately `0.754 seconds` for 50,000
  executions, or `15.08 µs` per execution
* five-step execution took approximately `2.9` times the one-step profile time,
  rather than five times, because context and final-result construction occur
  once per workflow
* Pydantic model initialization accounted for approximately `54%` of one-step
  engine time and `46%` of five-step engine time
* Pydantic core validation alone accounted for approximately `41%` of one-step
  engine time and `35%` of five-step engine time
* state updates accounted for approximately `2%` of one-step engine time and
  `4%` of five-step engine time
* list appends accounted for approximately `2%` of one-step engine time and
  `4%` of five-step engine time

Focused benchmark verification:

* one-step workflow median: approximately `2.839 µs`
* five-step workflow median: approximately `7.367 µs`
* five-step median was approximately `2.60` times the one-step median
* the four additional workflow steps added approximately `4.528 µs` in total,
  or approximately `1.132 µs` per additional step in this deterministic
  scenario
* benchmark measurements were captured on the profiling environment and are
  not directly comparable with the earlier Windows baseline

Primary finding:

Pydantic construction and validation of the workflow context, individual step
results, and final workflow result are the largest reusable contributors.
State propagation and executed-step list maintenance are negligible.

Final-result construction changes very little between one and five prebuilt
step results because the nested items are already validated Pydantic model
instances.

Conclusion:

No workflow-specific runtime optimization is recommended. The deterministic
one-step and five-step overhead is already measured in microseconds, and real
workflow application work will normally dominate it.

Pydantic construction should remain visible during `PROF-007`, but bypassing
validation, replacing the public result models, or adding specialized internal
construction paths would weaken clear typed contracts for a very small
absolute gain. No runtime implementation changed during `PROF-006`.

#### PROF-007 — Review Optimization Candidates

* [x] Rank identified bottlenecks by measurable impact
* [x] Separate implementation overhead from dependency overhead
* [x] Identify changes that preserve public APIs
* [x] Reject premature or low-value optimizations
* [x] Document architectural tradeoffs
* [x] Select only justified optimization candidates
* [x] Record cases where no change is recommended

Review method:

* compare representative absolute timings instead of ranking functions only by
  their percentage inside one profile
* treat measurements from different operating systems and Python versions as
  order-of-magnitude evidence rather than direct benchmark comparisons
* separate toolkit-controlled repeated work from Pydantic, logging, and
  application or provider work
* reject changes that weaken typed contracts, observability, correctness, or
  provider independence for microsecond-scale gains

Ranked remaining costs:

1. Optimized in-memory vector search remains the largest measured internal
   path, with representative means of approximately `13.037 ms` unfiltered and
   `6.296 ms` metadata-filtered for 1,000 64-dimensional records. This is
   toolkit implementation work, but the remaining cost is primarily the
   intentional linear scan and per-candidate cosine calculation.
2. Structured-schema generation costs approximately `0.4 ms` per structured
   prompt under `cProfile`. This is Pydantic dependency work repeatedly invoked
   by toolkit prompt construction and is the largest potentially removable
   repeated cost.
3. One-retry structured repair has a representative median of approximately
   `99.838 µs`. This is mixed toolkit and dependency work, but most of the
   additional work represents required retry behavior: another parse attempt,
   exception handling, provider call, token aggregation, and result handling.
4. Five-step workflow orchestration has a representative median of
   approximately `7.367 µs`; Pydantic construction and validation are the
   largest contributors.
5. Complete RAG orchestration has a representative median of approximately
   `5.268 µs`; retrieved-context formatting is its largest internal contributor.
6. Plain request overhead has a representative post-optimization median of
   approximately `4.400 µs` when INFO logging is disabled. Request IDs and typed
   result construction are small, while enabled INFO logging is intentional,
   configurable observability overhead.

Candidate decisions:

* **No additional vector-search change approved.** Replacing the reference
  linear scan requires a different storage or indexing architecture, not a
  local hot-path optimization. The current in-memory store remains appropriate
  for tests, examples, and small local datasets.
* **Structured-schema caching is not approved.** It would remove the largest
  repeated structured-prompt cost, but a cache keyed only by model class can
  become stale after Pydantic `model_rebuild()`. Automatic invalidation would
  couple the toolkit to Pydantic implementation details, while explicit
  invalidation would add public API and caller responsibility. Approximately
  `0.4 ms` does not justify that correctness and maintenance risk in request
  paths normally dominated by provider execution.
* **No retry-path change approved.** Removing validation, reducing configured
  retry behavior, or omitting token aggregation would change correctness or
  result semantics.
* **No RAG formatting change approved.** Its complete orchestration cost is
  already a few microseconds and will normally be dominated by embedding,
  retrieval, and provider execution.
* **No workflow construction change approved.** Bypassing Pydantic validation
  or using specialized construction paths would weaken typed workflow
  contracts for a microsecond-scale gain.
* **No observability change approved.** Request IDs and configurable logging
  remain deliberate production features; disabled INFO logging already uses
  the optimized low-overhead path.

Conclusion:

No candidate is justified for runtime implementation in `PROF-008`. The two
previously approved changes—pre-resolved request pricing with guarded logging,
and query-norm reuse in vector search—captured the meaningful low-risk gains.
The remaining costs are either inherent to the reference architecture,
dependency-dominated, required for correctness, or negligible in absolute
terms.

`PROF-008` should therefore be completed without runtime changes, as explicitly
allowed by its task definition. No public API, ADR, README, changelog, or
project-state update is required for this review.

#### PROF-008 — Implement Approved Optimizations

* [x] Review the candidates approved by `PROF-007`
* [x] Confirm that no candidate was approved for runtime implementation
* [x] Complete the implementation gate without runtime changes
* [x] Preserve correctness behavior
* [x] Preserve provider-independent interfaces
* [x] Confirm that no correctness-test change is required
* [x] Confirm that no before-and-after benchmark is required
* [x] Document the intentional no-change decision

This task may be completed without implementation changes if profiling shows that current overhead is acceptable or dominated by dependencies.

Implementation decision:

No runtime optimization was implemented. `PROF-007` rejected every remaining
candidate because the expected benefit did not justify its correctness,
maintenance, architectural, or public-API cost.

The gate confirmed:

* the current vector-search cost belongs to the intentional linear-scan
  reference architecture
* structured-schema caching lacks a safe, simple invalidation contract for
  dynamically rebuilt Pydantic models
* structured repair work preserves validation, retries, provider execution,
  token aggregation, and result semantics
* RAG and workflow overhead is already measured in microseconds
* request IDs and configurable logging preserve production observability

Because no executable behavior changed, no new correctness test,
before-and-after benchmark, ADR, README entry, changelog entry, or project-state
update was required.

Conclusion:

`PROF-008` is complete without implementation. This is an evidence-based
decision, not an omitted optimization step. `PROF-009` subsequently
consolidated the profiling method, results, decisions, and remaining risks.

#### PROF-009 — Document Profiling Results

* [x] Document the profiling method
* [x] Document the local environment
* [x] Document measured bottlenecks
* [x] Document approved optimizations
* [x] Document rejected optimizations
* [x] Document benchmark comparisons
* [x] Document remaining performance risks
* [x] Update project state and changelog

Consolidated report:

```text
docs/development/performance_profiling.md
```

Documentation decision:

* `benchmarks/README.md` remains the stable guide to benchmark execution,
  scope, comparison, and interpretation
* the consolidated report records profiling evidence and engineering decisions
* generated JSON results and text profiles remain under ignored
  `.benchmarks/`
* machine-specific measurements are not presented as universal thresholds

#### Exit Criteria

* [x] A local benchmark baseline has been captured
* [x] Main benchmarked execution paths have been profiled
* [x] Profiling results are based on deterministic scenarios
* [x] Provider and network latency remain excluded
* [x] Machine-specific profile artifacts are ignored by Git
* [x] Meaningful bottlenecks are documented
* [x] Optimization candidates are ranked by evidence
* [x] Public API compatibility is preserved
* [x] Every accepted optimization has before-and-after measurements
* [x] Low-value optimizations are explicitly rejected
* [x] Normal tests pass
* [x] Benchmark correctness checks pass
* [x] Performance benchmarks pass
* [ ] Black passes
* [ ] Ruff passes

Quality-check exception:

* Black 26.5.1 reports two pre-existing files that require formatting
* Ruff 0.16.0 reports 62 pre-existing repository-wide findings
* `PROF-009` changed no Python implementation or test file
* these findings are recorded rather than silently mixed into the profiling
  documentation commit
* repository-wide cleanup and quality-tool version constraints remain required
  before the Sprint 9 full-quality exit

Result:

Python AI Toolkit has an evidence-based understanding of its internal performance characteristics and documented optimization decisions before Version 1.0.


## PROD-003 — Complete Documentation

### Goal

Make the toolkit understandable and usable without reading its implementation.

### Tasks

* [x] DOC-001 Review README structure and remove duplication
* [x] DOC-002 Document installation and optional extras
* [x] DOC-003 Document environment and explicit configuration
* [x] DOC-004 Document provider registration
* [x] DOC-005 Document plain and structured requests
* [x] DOC-006 Document streaming, async, tools, and image inputs
* [x] DOC-007 Document embeddings, retrieval, and RAG
* [x] DOC-008 Document memory, agents, workflows, and orchestration
* [x] DOC-009 Document Django, FastAPI, and CLI integrations
* [x] DOC-010 Document exceptions and error handling
* [x] DOC-011 Document security and secret-handling guidance
* [x] DOC-012 Document Python-version and provider compatibility
* [x] DOC-013 Create a stable public API reference
* [x] DOC-014 Verify every documented example

#### DOC-001 — README Structure Review

Status: Completed

The root README was reduced from a duplicated long-form manual to an onboarding
and navigation document.

Completed work:

* moved installation, configuration, and first-request guidance near the top
* grouped implemented capabilities by user goal
* retained concise public-API examples for the major feature areas
* added a clear path to examples, architecture, benchmarks, profiling, roadmap,
  project-state, and changelog documents
* removed the duplicated structured-response, validation, retry, logging,
  usage, cost, and exception summaries
* removed the stale copied project tree and copied roadmap
* removed forward-looking capability lists that contradicted later implemented
  features
* preserved detailed topic audits for `DOC-002` through `DOC-014`

No runtime API, implementation, dependency, or executable behavior changed.

Following task at completion:

```text
DOC-002 — Document installation and optional extras
```

#### DOC-002 — Installation and Optional Extras

Status: Completed

Installation behavior was reviewed against `pyproject.toml`, the current import
boundaries, package metadata, and clean temporary environments.

Completed work:

* corrected the README sequence so the virtual environment is activated before
  package installation
* removed the placeholder repository URL and documented the current
  source-installation boundary honestly
* added `docs/installation.md` as the focused installation guide
* separated normal non-editable installation from editable contributor setup
* documented the core, `django`, `fastapi`, `dev`, and `benchmark` installation
  paths
* documented `pyproject.toml` as the authoritative dependency source and
  `requirements.txt` as an environment snapshot
* updated Django and FastAPI example commands so they no longer imply that the
  package is already available from PyPI
* verified that the core package installs and exposes the CLI without installing
  Django or FastAPI
* verified each optional group and the combined `dev,benchmark` contributor
  installation
* confirmed that `httpx2` is intentional for the current FastAPI test client,
  while the OpenAI dependency separately installs `httpx`
* passed the complete 269-test suite from the clean contributor environment

No runtime API, implementation, package dependency, or architectural contract
changed.

Next task:

```text
DOC-003 — Document environment and explicit configuration
```

#### DOC-003 — Environment and Explicit Configuration

Status: Completed

Configuration behavior was reviewed against `ai/config.py`,
`ai/config_validator.py`, the client constructors, provider factory, CLI
configuration commands, `.env.example`, and configuration tests.

Completed work:

* added `docs/configuration.md` as the focused configuration guide
* documented every supported environment variable and current default
* documented dynamic provider-specific variable names and generic fallback
  behavior
* documented `.env`, process-environment, provider-specific, and generic-value
  precedence
* documented explicit `AIConfig` construction for synchronous and asynchronous
  clients
* made clear that explicit configuration replaces rather than merges with
  environment configuration
* documented that omitted explicit fields use dataclass defaults
* distinguished automatic environment-config validation from validation of a
  manually constructed `AIConfig`
* distinguished structural validation, provider registration, and live
  credential/model verification
* documented CLI configuration inspection and its non-network boundary
* expanded `.env.example` comments without adding real credentials
* corrected stale README, installation, and CLI-example guidance
* verified environment resolution, explicit precedence, examples, links, and
  the complete normal test suite

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

No runtime API, implementation, package dependency, provider registration, or
architectural contract changed.

Next task:

```text
DOC-004 — Document provider registration
```

#### DOC-004 — Provider Registration

Status: Completed

Provider registration behavior was reviewed against `BaseAIProvider`,
`OpenAIProvider`, `ProviderFactory`, provider tests, architecture, and the
accepted provider ADRs.

Completed work:

* added `docs/providers.md` as the focused provider guide
* documented the built-in OpenAI provider and registered-provider inspection
* documented explicit, process-local registration and exact-name matching
* documented the required `api_key` and `model` constructor keywords
* documented conditional forwarding of embedding configuration
* separated required `ask_text()` behavior from optional provider capabilities
* documented duplicate-registration, unsupported-provider, constructor, and
  unsupported-capability failures
* distinguished configuration validation, provider availability, and live
  credential/model verification
* linked provider guidance from the README and configuration guide
* verified provider examples without network access

Completion verification:

```text
custom provider registration and client execution passed
22 Python blocks in the affected guides parsed
repository-relative Markdown links passed
269 normal tests passed
```

No runtime API, implementation, dependency, test, or architectural contract
changed.

Release-review note:

* `AIClient` and `AsyncAIClient` should be reviewed during the Version 1.0 API
  freeze to decide whether supplied `AIConfig` objects should be structurally
  validated automatically at client construction
* until that decision is implemented, applications should call
  `ConfigValidator.validate(config)` for manually constructed configuration

Next task:

```text
DOC-005 — Document plain and structured requests
```

#### DOC-005 — Plain and Structured Requests

Status: Completed

Request behavior was reviewed against `AIClient`, `RequestExecutor`,
`AIResult`, structured prompt construction, JSON parsing, Pydantic validation,
repair prompting, configuration, tests, and the first two examples.

Completed work:

* added `docs/requests.md` as the focused synchronous request guide
* documented the return-value difference between `ask()` and `ask_text()`
* documented plain `AIResult[str]` and structured `AIResult[T]` behavior
* documented the `response_type` model-class contract and provider-independent
  schema-prompting path
* documented every current `AIResult` field and the first-versus-final raw
  response distinction
* documented strict JSON parsing and Pydantic schema validation
* documented provider-backed repair attempts and `max_retries` semantics
* distinguished structured repair retries from provider transport retries
* distinguished toolkit schema validation from application factual,
  authorization, policy, and business validation
* linked the focused guide from the README and example gallery
* verified the exact guide examples with a deterministic in-memory provider
* verified the plain and structured example scripts and focused lifecycle tests

Completion verification:

```text
4 request-guide Python examples executed
2 existing plain and structured example scripts executed
16 focused client, executor, parser, retry, and structured tests passed
repository-relative documentation links passed
269 normal tests passed
```

No runtime API, implementation, dependency, test, or architectural contract
changed.

Next task:

```text
DOC-006 — Document streaming, async, tools, and image inputs
```

#### DOC-006 — Streaming, Async, Tools, and Image Inputs

Status: Completed

Advanced request behavior was reviewed against the synchronous and asynchronous
clients and executors, provider capability methods, tool and image models,
OpenAI adapters, tests, examples 05 through 09, and the accepted async-client
and tool-execution ADRs.

Completed work:

* added `docs/advanced_requests.md` as the focused advanced-request guide
* documented synchronous streaming iteration, lazy execution, partial-output
  errors, chunk semantics, and the non-`AIResult` metadata boundary
* documented async plain and structured requests, `ask_text()`, repair
  consistency, event-loop usage, and the current async capability limits
* documented `ToolDefinition`, `ToolResponse`, and `ToolCall`
* documented allow-listing, argument validation, authorization, and
  application-owned tool execution
* documented image URL and Base64 data-URL inputs, optional detail, multiple
  images, and plain or structured responses
* documented that local image reading and encoding remain application helpers
* documented the text-only formatting-repair boundary after an invalid
  structured image response
* distinguished provider registration, provider method support, and selected
  model/account capability support
* linked the guide from the README, request guide, and example gallery
* verified the guide examples, examples 05 through 09, focused tests, links,
  and the complete normal test suite

Completion verification:

```text
31 Python documentation blocks parsed
40 repository-relative documentation links passed
6 advanced-request example scripts executed offline
26 focused streaming, async, tool, and image tests passed
269 normal tests passed
```

No runtime API, implementation, dependency, test, or architectural contract
changed.

Next task:

```text
DOC-007 — Document embeddings, retrieval, and RAG
```

#### DOC-007 — Embeddings, Retrieval, and RAG

Status: Completed

Retrieval behavior was reviewed against the embedding models and client
methods, provider capability contract, vector-store abstraction, retriever,
RAG pipeline, document loaders, accepted retrieval ADRs, tests, and examples
10 through 14.

Completed work:

* added `docs/retrieval.md` as the focused retrieval and RAG guide
* documented single and batch embeddings, configuration, metadata, provider
  ordering, and the non-`AIResult` return boundary
* documented vector records, replacement by ID, cosine-similarity scores,
  exact metadata filtering, dimension errors, and zero-vector behavior
* documented the volatile linear-scan boundary of `InMemoryVectorStore`
* documented retriever composition, `RetrievedContext`, and prompt formatting
* documented text, Markdown, and directory loaders plus the explicit
  loading/chunking/embedding/indexing separation
* documented RAG prompt construction, response fields, omitted `AIResult`
  metadata, synchronous plain-text limits, and returned-context behavior
* distinguished ranking scores from probabilities, returned contexts from
  verified citations, and prompt grounding from factual guarantees
* linked the guide from the README and example gallery
* verified the guide examples, examples 10 through 14, focused tests, links,
  and the complete normal test suite

Completion verification:

```text
5 retrieval-guide workflows executed offline
5 retrieval example scripts executed with a deterministic offline client
56 focused embedding, vector-store, retriever, RAG, and document tests passed
38 Python blocks in the affected documents parsed
58 repository-relative Markdown links passed
269 normal tests passed
```

No runtime API, implementation, dependency, test, or architectural contract
changed.

Next task:

```text
DOC-008 — Document memory, agents, workflows, and orchestration
```

#### DOC-008 — Memory, Agents, Workflows, and Orchestration

Status: Completed

Orchestration behavior was reviewed against the conversation-memory, agent,
workflow, and multi-agent implementations; their tests; examples 15 through
18; the architecture; and ADRs 0012 and 0013.

Completed work:

* added `docs/orchestration.md` as the focused orchestration guide
* documented conversation roles, message metadata and timestamps, memory
  operations, recent-message counting, formatting, and volatile storage limits
* documented the agent run lifecycle, prompt construction, memory updates,
  selected response metadata, and partial-memory behavior after request failure
* documented workflow context, shallow state updates, step and run results,
  execution history, exception conversion, fail-fast behavior, and lack of
  rollback
* documented exact-name agent registration, inventory ordering, individual
  execution, sequential output handoff, result collection, and failure behavior
* documented synchronous, sequential, in-process limits and application-owned
  routing, tool execution, permissions, transactions, and resource control
* recorded the current agent-prompt duplication and orchestration result
  boundaries for explicit Version 1.0 API review
* linked the guide from the README and examples 15 through 18
* verified the guide examples, examples 15 through 18, focused tests, links,
  and the complete normal test suite

Completion verification:

```text
4 orchestration-guide workflows executed offline
4 existing example scripts executed with a deterministic offline client
61 focused memory, agent, workflow, and orchestrator tests passed
22 Python blocks in the affected documents parsed
67 repository-relative Markdown links passed
269 normal tests passed
```

No runtime API, implementation, dependency, test, or architectural contract
changed.

Next task:

```text
DOC-009 — Document Django, FastAPI, and CLI integrations
```

#### DOC-009 — Django, FastAPI, and CLI Integrations

Status: Completed

Integration behavior was reviewed against the Django and FastAPI adapters,
configuration system, CLI implementation and packaging entry point, ADRs 0014
and 0015, integration and configuration tests, and examples 19 through 22.

Completed work:

* added `docs/integrations.md` as the focused framework and CLI guide
* documented optional Django and FastAPI installation boundaries
* documented the complete Django `AI_TOOLKIT` mapping, normalization,
  validation, defaults, custom setting names, and non-merging environment
  boundary
* documented synchronous and asynchronous Django client helpers, construction
  lifecycle, and application-owned exception behavior
* documented synchronous and asynchronous FastAPI dependency factories,
  reusable `Annotated` aliases, endpoint usage, and dependency overrides
* documented FastAPI client lifetime, explicit custom-dependency option, and
  application-owned HTTP concerns
* clarified that the FastAPI extra does not select an ASGI server or supply
  application test dependencies, and corrected the example's Uvicorn setup
* documented CLI request, configuration-display, and structural-validation
  commands
* documented CLI standard output, standard error, masking, exit codes, handled
  toolkit errors, and visible unexpected exceptions
* distinguished local configuration and client construction from provider
  registration, credential checks, model access, and live network requests
* linked the guide from the README, installation and configuration guides, and
  examples 19 through 22
* verified guide workflows, examples 19 and 20, focused tests, Python blocks,
  links, and the complete normal test suite

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

No runtime API, executable implementation, dependency, test, or architectural
contract changed. Example 20 received documentation-only setup guidance.

Next task:

```text
DOC-010 — Document exceptions and error handling
```

#### DOC-010 — Exceptions and Error Handling

Status: Completed

Error behavior was reviewed against the public exception hierarchy, every
production raise/catch boundary, request executors, provider adapters,
configuration paths, structured parsing and repair, retrieval and document
operations, orchestration primitives, framework integrations, CLI behavior,
tests, architecture, and developer error-message guidance.

Completed work:

* added `docs/error_handling.md` as the focused public error-handling guide
* documented the `AIError` hierarchy and the operation categories represented
  by each concrete toolkit exception
* documented narrow exception handling versus the common application boundary
* documented configuration validation timing, unsupported provider behavior,
  provider SDK translation, and preserved exception causes
* distinguished structured-output repair from provider transport retries and
  application recovery policy
* documented ordinary `ValueError`, `FileNotFoundError`, file-system, Pydantic,
  custom-provider, and business-policy exceptions outside `AIError`
* documented lazy streaming failures and the possibility of partial output
* documented raised request failures versus workflow and orchestration failure
  result objects
* documented framework propagation, CLI exit behavior, executor logging, and
  application-owned exception-to-response mapping
* updated the maintainer error-message guide with ordinary-exception and
  exception-chaining rules
* linked the guide from the README and integration documentation
* verified guide examples, offline failure contracts, focused tests, Python
  blocks, links, and the complete normal test suite

Completion verification:

```text
Offline hierarchy, configuration, provider, parsing, vector, and workflow
failure contracts passed
226 focused error-surface tests passed
33 Python blocks in the affected documents parsed
51 repository-relative Markdown links passed
269 normal tests passed
```

No runtime API, executable implementation, dependency, test, example,
benchmark, or architectural contract changed.

Next task:

```text
DOC-011 — Document security and secret-handling guidance
```

#### DOC-011 — Security and Secret Handling

Status: Completed

Security boundaries were reviewed across configuration, `.env` handling,
repository ignores, logging, CLI output, provider exceptions, requests,
structured repair, image and tool inputs, embeddings, retrieval, memory,
orchestration, framework adapters, examples, tests, packaging, and deployment
guidance.

Completed work:

* added `docs/security.md` as the focused public security guide
* distinguished local-development, automated-test, CI, and production secret
  sources
* documented environment and application-owned secret-manager injection
* documented repository, history, build-artifact, terminal, logging, and
  exception-output exposure
* documented provider-bound data for requests, structured repair, streaming,
  tools, images, embeddings, RAG, agents, and multi-agent handoffs
* documented sensitive fields in result, retrieval, memory, workflow, and
  orchestration objects
* documented provider retention, residency, training, subprocessor, encryption,
  and regulated-data review as application governance
* documented allow-listing, argument validation, caller authorization,
  least-privileged execution, confirmation, audit, and prompt-injection
  boundaries for tools
* documented web and multi-tenant access-control responsibilities
* added an incident-response sequence and production checklist
* expanded `.gitignore` to exclude `.env.*` while preserving `.env.example`
* added an explicit placeholder-only warning to `.env.example`
* linked the security guide from the README and capability guides
* verified maintained files contain no likely real credentials
* removed raw provider responses from JSON parse and schema-validation
  exception messages so executor traceback logging does not disclose them
* added regression coverage for exception messages and structured-failure logs

Completion verification:

```text
Security explicit-configuration example executed without network access
.env and .env.* ignore behavior passed with .env.example retained
Credential-pattern scan found no likely real secrets in maintained files
94 focused security and request-lifecycle tests passed
Focused Black and Ruff checks passed
70 Python blocks in the affected guides parsed
95 repository-relative Markdown links passed
271 normal tests passed
```

The release-blocking response-disclosure path was corrected without changing
the public exception hierarchy, provider API, dependency set, example code,
benchmark suite, or architectural contract.

Next task:

```text
DOC-012 — Document Python-version and provider compatibility
```

#### DOC-012 — Python-Version and Provider Compatibility

Status: Completed

Compatibility was reviewed against package metadata, dependency declarations
and resolved metadata, Python syntax, provider interfaces and adapters,
framework integrations, tests, installation guidance, and the planned release
matrix.

Completed work:

* added `docs/compatibility.md` as the focused compatibility guide
* distinguished the open-ended `requires-python = ">=3.11"` installer metadata
  from the planned Python 3.11–3.14 Version 1.0 test matrix
* recorded Python 3.12.13 as the current full-suite verification environment
* retained Python 3.14.4 as historical deterministic benchmark evidence without
  presenting it as a current full-suite result
* parsed production, test, example, benchmark, and profiling sources with the
  Python 3.11 grammar without labeling that syntax check as runtime verification
* documented direct dependency constraints, clean resolution behavior, and the
  non-contract status of `requirements.txt`
* documented core, Django, FastAPI, development, and benchmark dependency
  boundaries
* documented the built-in OpenAI adapter's exact SDK mappings
* distinguished provider registration and adapter methods from SDK, credential,
  account, region, quota, and selected-model capability availability
* documented custom-provider dependency ownership
* documented optional-framework Python and dependency intersections
* documented separate clean-environment verification for core, Django, and
  FastAPI installations
* documented capability-specific live smoke testing separately from normal
  deterministic tests
* documented the application-owned SOCKS proxy transport dependency boundary
* linked compatibility guidance from the README, installation, provider, and
  integration guides

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

The full deterministic suite was run with workspace-injected proxy variables
removed. The initial run confirmed that a SOCKS proxy needs the HTTP client's
optional SOCKS transport package; this deployment-specific dependency was
documented instead of being added to every core installation.

No runtime API, executable implementation, package dependency, test, example,
benchmark, or architectural contract changed.

Next task:

```text
DOC-013 — Create a stable public API reference
```

#### DOC-013 — Stable Public API Reference

Status: Completed

The supported public surface was reviewed against package exports, all
application-facing classes and functions, typed models, abstract extension
interfaces, exceptions, framework integrations, CLI entry points, focused
guides, and contract tests.

Completed work:

* added `docs/api_reference.md` as the authoritative public-surface inventory
* documented the current module-level import contract and the empty top-level
  `ai` namespace
* defined 71 supported symbols across clients, configuration, results, request
  and prompt helpers, advanced inputs, retrieval, orchestration, providers,
  integrations, exceptions, parsing, cost compatibility, and the CLI
* documented signatures, parameters, return types, defaults, result fields,
  raised toolkit exceptions, ordinary Python exceptions, lifecycle behavior,
  mutable and volatile state, partial failures, and capability limits
* retained `parse_json_response()` as the supported low-level parsing helper
  already used by the error guide
* retained `estimate_cost_usd()` as the compatibility function preserved by
  the profiling work
* explicitly excluded executors, structured-prompt and repair plumbing,
  pre-resolved cost helpers, logger construction, direct built-in adapter use,
  provider-SDK translation helpers, and private names
* recorded top-level re-exports, automatic explicit-config validation, builder
  construction, public client implementation attributes, direct provider
  adapter imports, compatibility helpers, and importable undocumented names
  for the Version 1.0 API-freeze review
* linked the reference from the README and every focused public capability
  guide

Completion verification:

```text
71 documented public symbols imported
key runtime signatures, enum values, defaults, and result properties matched
239 focused public-surface tests passed
80 Python blocks across README and focused public guides parsed
130 repository-relative Markdown links passed
271 normal tests passed on Linux with CPython 3.12.13
```

No runtime API, import path, executable implementation, package dependency,
test, example, benchmark, or architectural contract changed.

Next task:

```text
DOC-014 — Verify every documented example
```

#### DOC-014 — Documented Example Verification

Status: Completed

Every user-facing code and command block was inventoried across the README,
focused guides, API reference, and example gallery. The results and execution
boundaries are recorded in
`docs/development/example_verification.md`.

Completed work:

* classified 201 fenced blocks as executable, provider-dependent,
  environment-dependent, or intentionally illustrative
* executed all 80 Python blocks in document order with deterministic provider
  behavior where required
* added offline regression coverage for numbered examples 01 through 20, the
  Base64 helper variant, the two existing unnumbered examples, Django, and
  FastAPI
* verified core, Django, FastAPI, contributor, benchmark, CLI, and Uvicorn
  command workflows in isolated environments
* kept live provider verification explicit instead of treating fake responses
  as proof of credentials, account access, or model capability
* corrected the gallery's nonexistent `examples.01_summarize_text` command
* aligned example 01's title with its plain-request behavior
* made the Base64 image-helper example validate a structured response
* made the async `ask_text()` snippet independently valid
* added the missing `Document` import to the retrieval guide
* added permanent Python-block, link, gallery-reference, and deterministic
  example regression tests
* preserved the later `PROD-004` scope for new example topics and naming
  normalization

Completion verification:

```text
201 documented fenced blocks inventoried
80 Python documentation blocks executed
40 focused documentation and example tests passed
core, Django, and FastAPI clean installations passed
CLI configuration and Uvicorn target checks passed
9 benchmarks passed; 4 infrastructure tests skipped
311 normal tests passed on Linux with CPython 3.12.13
136 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, package dependency, public import
path, benchmark, or architectural decision changed.

Following task at completion:

```text
EXAMPLE-001 — Explicit AIConfig injection
```

### Documentation Rules

* Documentation must match the implemented public API.
* Examples must be executable or clearly marked as illustrative.
* API keys must never appear in documentation.
* Deferred capabilities must not be described as implemented.
* Provider-specific behavior must be clearly distinguished from provider-independent behavior.

### Exit Criteria

* [x] New users can install and make a first request
* [x] Advanced users can find all major capabilities
* [x] Integrations and optional dependencies are documented
* [x] Public APIs and exceptions are documented
* [x] All documented code is verified

---

## PROD-004 — Additional Examples

### Goal

Fill important example gaps required for a Version 1.0 release.

### Tasks

* [x] EXAMPLE-001 Explicit `AIConfig` injection
* [x] EXAMPLE-002 Custom provider registration
* [x] EXAMPLE-003 Testing application code with a fake provider
* [x] EXAMPLE-004 Batch embedding and retrieval
* [x] EXAMPLE-005 End-to-end document indexing and RAG
* [x] EXAMPLE-006 Structured application service example
* [ ] EXAMPLE-007 Review and normalize all example descriptions
* [ ] EXAMPLE-008 Verify all examples against current APIs

### Example Rules

* Examples must focus on toolkit behavior.
* Business logic must remain small and illustrative.
* Examples must not require undocumented setup.
* Network-dependent examples must clearly state their requirements.
* Examples must not contain real credentials.

#### EXAMPLE-001 — Explicit `AIConfig` Injection

Status: Completed

Completed work:

* added `examples/23_explicit_config.py` without renaming or reassigning the
  existing 01 through 22 gallery entries
* accepted an application-supplied API key and constructed a complete,
  immutable `AIConfig`
* called `ConfigValidator.validate(config)` before constructing `AIClient`
* kept provider, model, embedding, retry, and logging values independent from
  environment-based toolkit resolution
* documented safe development-secret injection and secret-manager ownership
* linked the example from the gallery, learning path, README, and configuration
  guide
* extended deterministic regression coverage for example execution,
  environment precedence, resolver bypass, and validation before provider
  construction

Completion verification:

```text
42 focused example and documentation tests passed
313 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
80 Python documentation blocks compiled
138 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or
architectural decision changed.

Next task:

```text
EXAMPLE-002 — Custom provider registration
```

#### EXAMPLE-002 — Custom Provider Registration

Status: Completed

Completed work:

* added `examples/24_custom_provider.py` without renaming or reassigning the
  existing 01 through 23 gallery entries
* implemented a deterministic `LocalEchoProvider` with the required
  `api_key`, `model`, and synchronous `ask_text()` contracts
* registered the exact `local_echo` name before client construction
* selected the custom provider with an explicit, structurally validated
  `AIConfig`
* exercised the real factory, client, executor, `ProviderResponse`, and token
  metadata path without credentials or network access
* documented process-local registry lifetime and the distinction between
  registration and optional or live capability support
* linked the example from the gallery, learning path, README, and provider
  guide
* added isolated regression coverage for registration, validation order,
  provider construction, response data, model metadata, and token usage

Completion verification:

```text
49 focused example, documentation, and provider-factory tests passed
314 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
80 Python documentation blocks compiled
140 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or
architectural decision changed.

Next task:

```text
EXAMPLE-003 — Testing application code with a fake provider
```

#### EXAMPLE-003 — Testing Application Code with a Fake Provider

Status: Completed

Completed work:

* added `examples/25_testing_with_fake_provider.py` without renaming or
  reassigning the existing 01 through 24 gallery entries
* kept production application logic dependent on `AIClient`, not a provider
  SDK or test double
* implemented a deterministic `BaseAIProvider` fake that records prompts and
  returns controlled structured JSON plus token metadata
* patched `ProviderFactory.create()` only while constructing the test client,
  then exercised the real request executor and structured parser
* used validated explicit test configuration with a non-secret placeholder
  while proving environment provider, model, and key values are ignored
* asserted application output, prompt forwarding, selected provider identity,
  and an unchanged process-local provider registry
* linked the example from the gallery, learning path, README, and provider
  guide
* added permanent regression coverage for the no-credential, no-network, and
  state-isolation contracts

Completion verification:

```text
50 focused example, documentation, and provider-factory tests passed
315 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
81 Python documentation blocks compiled
142 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or
architectural decision changed.

Next task:

```text
EXAMPLE-004 — Batch embedding and retrieval
```

#### EXAMPLE-004 — Batch Embedding and Retrieval

Status: Completed

Completed work:

* added `examples/26_batch_embedding_and_retrieval.py` without renaming or
  reassigning the existing 01 through 25 gallery entries
* submitted three metadata-bearing knowledge items through one
  `AIClient.embed_texts()` request
* restored input order from `EmbeddingVector.index` rather than trusting
  provider result-list position
* preserved application-owned record IDs, source metadata, and topics in
  `VectorRecord`
* stored the batch in `InMemoryVectorStore` and retrieved filtered,
  prompt-ready contexts through `VectorStoreRetriever`
* kept file loading, document preparation, RAG prompt construction, and answer
  generation reserved for `EXAMPLE-005`
* linked the example from the gallery, complete learning path, README, and
  retrieval guide
* added deterministic regression coverage for one-request batching,
  out-of-order provider results, query embedding, metadata preservation,
  vector storage, and relevant-context ranking

Completion verification:

```text
79 focused embedding, vector-store, retriever, example, and documentation tests passed
317 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
211 fenced documentation blocks inventoried
81 Python documentation blocks compiled
144 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or
architectural decision changed.

Next task:

```text
EXAMPLE-005 — End-to-end document indexing and RAG
```

#### EXAMPLE-005 — End-to-End Document Indexing and RAG

Status: Completed

Completed work:

* added `examples/27_document_indexing_and_rag.py` without renaming or
  reassigning the existing 01 through 26 gallery entries
* loaded the existing `.txt` and `.md` sample files through `DirectoryLoader`
  using a module-relative path that works independently of the current working
  directory
* kept document preparation explicit by adding application-owned stable IDs
  and collection metadata before `documents_to_embedding_inputs()`
* submitted all prepared documents in one embedding batch and restored input
  order from `EmbeddingVector.index`
* preserved loader, filename, source, record, and collection metadata in
  `VectorRecord`
* composed `InMemoryVectorStore`, `VectorStoreRetriever`, and `RAGPipeline` to
  retrieve Redis context and generate one grounded answer
* kept chunking, persistent storage, access policy, citation verification, and
  high-level indexing orchestration application-owned
* linked the example from the gallery, complete learning path, README, and
  retrieval guide
* added deterministic regression coverage for the complete loader-to-answer
  workflow, reversed embedding results, grounded prompt contents, answer data,
  and returned source metadata

Completion verification:

```text
104 focused document, embedding, vector-store, retriever, RAG, example, and documentation tests passed
319 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
214 fenced documentation blocks inventoried
81 Python documentation blocks compiled
147 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or
architectural decision changed.

Next task:

```text
EXAMPLE-006 — Structured application service example
```

#### EXAMPLE-006 — Structured Application Service Example

Status: Completed

Completed work:

* added `examples/28_structured_application_service.py` without renaming or
  reassigning the existing 01 through 27 gallery entries
* defined constrained application-owned `FeedbackAnalysis` and
  `FeedbackOutcome` Pydantic models
* injected `AIClient` into a framework-independent `CustomerFeedbackService`
* validated and normalized feedback before any provider request
* kept the prompt, queue selection, and human-review rules in application code
* translated expected `AIError` failures into
  `FeedbackServiceUnavailable` while preserving the original cause
* returned the toolkit request ID in the stable application result
* linked the example from the gallery, complete learning path, README, and
  request guide
* added deterministic regression coverage for input validation, structured
  parsing, prompt forwarding, routing, metadata, and error translation

Completion verification:

```text
51 focused example and documentation tests passed
322 normal tests passed on Linux with CPython 3.12.13
focused Black and Ruff checks passed
217 fenced documentation blocks inventoried
82 Python documentation blocks compiled
149 repository-relative user-documentation links passed
```

No production runtime API, provider adapter, dependency, benchmark, or
architectural decision changed.

Next task:

```text
EXAMPLE-007 — Review and normalize all example descriptions
```

### Exit Criteria

* [x] Important public APIs have examples
* [ ] Example naming and numbering are consistent
* [ ] Example documentation follows one format
* [ ] Examples use current public APIs

---

## PROD-005 — PyPI Package

### Goal

Produce a valid, installable Python source distribution and wheel.

### Tasks

* [ ] PACKAGE-001 Review package metadata
* [ ] PACKAGE-002 Add package classifiers
* [ ] PACKAGE-003 Confirm license metadata and license file
* [ ] PACKAGE-004 Verify optional dependency groups
* [ ] PACKAGE-005 Verify console entry points
* [ ] PACKAGE-006 Build source distribution and wheel
* [ ] PACKAGE-007 Validate distributions
* [ ] PACKAGE-008 Test installation in a clean virtual environment
* [ ] PACKAGE-009 Test core installation without optional frameworks
* [ ] PACKAGE-010 Test Django and FastAPI extras separately

### Required Package Checks

```text
python -m build
python -m twine check dist/*
```

Clean-environment checks must verify:

```text
pip install python-ai-toolkit
pip install python-ai-toolkit[django]
pip install python-ai-toolkit[fastapi]
```

### Exit Criteria

* [ ] Wheel builds successfully
* [ ] Source distribution builds successfully
* [ ] Distribution validation passes
* [ ] Core installation does not require Django or FastAPI
* [ ] Console command is installed
* [ ] Package imports successfully in a clean environment

---

## PROD-006 — Release Automation

### Goal

Automate testing, package validation, and publishing.

### Tasks

* [ ] RELEASE-001 Add continuous-integration workflow
* [ ] RELEASE-002 Test supported Python versions
* [ ] RELEASE-003 Run tests, Black, and Ruff in CI
* [ ] RELEASE-004 Build package distributions in CI
* [ ] RELEASE-005 Validate built distributions
* [ ] RELEASE-006 Add release workflow for version tags
* [ ] RELEASE-007 Configure secure PyPI publishing
* [ ] RELEASE-008 Document release procedure
* [ ] RELEASE-009 Test release workflow without publishing production artifacts

### Python Test Matrix

The initial supported matrix should match:

```text
Python 3.11
Python 3.12
Python 3.13
Python 3.14
```

The matrix must be reviewed against actual dependency support before release.

### Release Security

* Do not store PyPI passwords in the repository.
* Prefer PyPI trusted publishing.
* Publishing must require an explicit version tag.
* Pull requests must never publish packages.
* Build artifacts must be generated from the tagged commit.

### Exit Criteria

* [ ] Pull requests run automated quality checks
* [ ] Supported Python versions are tested
* [ ] Package builds and validation run automatically
* [ ] Publishing is restricted to release tags
* [ ] Release steps are documented

---

## PROD-007 — Version 1.0.0 Release

### Goal

Publish the first stable release.

### Tasks

* [ ] V1-001 Freeze the Version 1.0 public API
* [ ] V1-002 Resolve release-blocking defects
* [ ] V1-003 Complete changelog
* [ ] V1-004 Update project version to `1.0.0`
* [ ] V1-005 Update project state
* [ ] V1-006 Complete release documentation
* [ ] V1-007 Create release commit
* [ ] V1-008 Create Git tag `v1.0.0`
* [ ] V1-009 Build and publish distributions
* [ ] V1-010 Verify installation from PyPI
* [ ] V1-011 Run post-release smoke tests
* [ ] V1-012 Publish release notes

### Public API Freeze

Before release, explicitly review:

* `AIClient`
* `AsyncAIClient`
* `AIConfig`
* `AIResult`
* provider interfaces
* request builder
* tool and image models
* embedding models
* vector-store interfaces
* retriever and RAG interfaces
* memory and agent interfaces
* workflow interfaces
* integration helpers
* CLI commands
* whether client constructors should automatically validate explicitly supplied
  `AIConfig` objects
* whether `ai.__init__` should provide curated top-level re-exports and
  `__all__`
* whether direct `AIRequestBuilder` construction should depend on the internal
  `RequestExecutor`
* whether visible client implementation attributes such as `provider` and
  `executor` are supported contracts
* whether built-in provider adapter classes are public or factory-only
* whether `ImageRequest`, `normalize_path()`, `estimate_cost_usd()`, and other
  importable low-level or compatibility names remain public in Version 1.0
* advanced-request return contracts and their current request-metadata
  boundaries
* whether capability discovery or preflight checks belong in the stable
  provider interface
* agent prompt construction, including whether the current message should
  appear in both recent conversation text and the dedicated current-message
  section
* message-count memory limits, agent metadata exposure, workflow state and
  failed-step semantics, unknown-agent sequence lookup, and partial-execution
  result contracts
* whether an empty `MultiAgentResponse` should report `success=True`

### Release Verification

A clean environment must successfully perform:

```text
install package
import core package
display CLI help
load configuration
make a basic request
run a structured request
use an optional integration
```

Live provider smoke tests must be explicit and must not run as normal unit tests.

### Exit Criteria

* [ ] Stable public API approved
* [ ] Full quality checks pass
* [ ] Documentation is complete
* [ ] Package is published
* [ ] Clean installation succeeds
* [ ] Version 1.0.0 is tagged and documented

---

## Sprint 9 Exit Criteria

* [ ] Representative benchmark coverage exists
* [ ] Performance findings are documented
* [ ] Documentation is complete and verified
* [ ] Important example gaps are closed
* [ ] Package distributions pass validation
* [ ] CI tests supported Python versions
* [ ] Release automation is operational
* [ ] Version 1.0.0 is published and smoke-tested


---

# Future Backlog

These items are intentionally excluded from the active roadmap.

They should be reconsidered after Sprint 9 and the Version 1.0 release unless an item becomes necessary to fix a release-blocking architectural, security, compatibility, or reliability problem.

## Providers and Ecosystem

* Local LLM support
* Plugin system
* MCP support
* Additional providers
* Automatic provider discovery
* Provider/model capability discovery and preflight validation separate from
  provider registration
* Immutable / reusable request builders
* DX-006 Add local image file helper

## Advanced Requests

* Metadata-bearing streaming API that preserves the existing simple iterator
  use case
* Request metadata for tool responses
* Async streaming, tool-calling, image-input, and embedding APIs
* Opt-in structured-image re-analysis that explicitly resends image inputs
* Application-controlled tool-loop helpers that preserve allow-listing,
  validation, authorization, and application-owned execution

## Observability, Benchmarking, and Evaluation

* Metrics dashboard
* Web dashboard
* Automatic model benchmarking
* AI evaluation framework
* Repository-wide Black and Ruff cleanup
* Black and Ruff version constraints for reproducible quality checks

## Retrieval and RAG

* RAG streaming responses
* Async RAG pipeline
* Structured RAG responses
* RAG citations formatter
* RAG reranking
* RAG evaluation framework
* Hybrid keyword + vector retrieval
* PDF document loader
* DOCX document loader
* HTML document loader
* Database document loader
* Automatic document chunking
* File watching and re-indexing
* Markdown section-aware loader
* Configurable document loader registry by file extension
* High-level document indexing helper

## Conversation Memory

* Persistent conversation memory
* Database-backed conversation memory
* Token-aware memory trimming
* Conversation summarization memory
* Vector-based long-term memory

## Agents

* Streaming agent responses
* Async agent
* RAG-aware agent
* Tool-using agent
* Agent prompt template customization

## Workflows and Multi-Agent Systems

* Branching workflow engine
* Parallel workflow execution
* Workflow step retries
* Async workflow engine
* Durable workflow persistence
* Visual workflow builder
* AI-based agent routing
* Parallel multi-agent execution
* Agent-to-agent debate
* Shared multi-agent memory
* Recursive agent loops
* Tool-using multi-agent workflows

## CLI Improvements

* Provider-independent CLI health check for credentials, connectivity, model access, and provider availability
* Configuration source and precedence diagnostics with secrets excluded
* Machine-readable CLI output such as `--json`
* Safe interactive configuration bootstrap without exposing secrets in command history
* CLI shell completion

Future backlog items should not interrupt the active roadmap unless they:

* block the current sprint,
* fix a significant architectural or security issue,
* prevent release-critical technical debt,
* or are required by the next active roadmap task.


---

# Roadmap Rules

1. Only one sprint may be active at a time.
2. New ideas go to the Future Backlog.
3. The active sprint cannot change without an explicit decision.
4. Every completed task updates the roadmap immediately.
5. Every architectural decision requires an ADR.
6. Every public API change updates the README.
7. Every released feature updates the CHANGELOG.
8. PROJECT_STATE.md is updated only when the project state meaningfully changes.

## Future Backlog Policy

Future backlog items are recorded when discovered, but they should not interrupt the active roadmap unless they block the current sprint, fix a design issue, or are required by the next roadmap task.
