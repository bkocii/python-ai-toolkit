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

Status: In Progress

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

* [ ] Profile successful structured-response parsing
* [ ] Profile JSON decoding
* [ ] Profile Pydantic validation
* [ ] Profile failed parsing and repair prompt construction
* [ ] Profile token-usage aggregation
* [ ] Compare successful parsing with one-retry repair
* [ ] Document meaningful call-time contributors

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

* [ ] Profile retrieved-context formatting
* [ ] Profile grounded prompt construction
* [ ] Profile additional-instruction formatting
* [ ] Profile `RAGResponse` construction
* [ ] Keep retrieval and provider execution excluded
* [ ] Document meaningful call-time contributors

#### PROF-006 — Profile Workflow Execution

* [ ] Profile one-step workflow execution
* [ ] Profile five-step workflow execution
* [ ] Measure `WorkflowContext` construction
* [ ] Measure workflow step-result construction
* [ ] Measure state propagation
* [ ] Measure final workflow-result construction
* [ ] Compare one-step and five-step overhead
* [ ] Document meaningful call-time contributors

#### PROF-007 — Review Optimization Candidates

* [ ] Rank identified bottlenecks by measurable impact
* [ ] Separate implementation overhead from dependency overhead
* [ ] Identify changes that preserve public APIs
* [ ] Reject premature or low-value optimizations
* [ ] Document architectural tradeoffs
* [ ] Select only justified optimization candidates
* [ ] Record cases where no change is recommended

#### PROF-008 — Implement Approved Optimizations

* [ ] Make one optimization at a time
* [ ] Preserve correctness behavior
* [ ] Preserve provider-independent interfaces
* [ ] Run normal tests after every change
* [ ] Compare benchmarks before and after every change
* [ ] Revert changes that provide no meaningful benefit
* [ ] Add or update correctness tests when behavior is touched

This task may be completed without implementation changes if profiling shows that current overhead is acceptable or dominated by dependencies.

#### PROF-009 — Document Profiling Results

* [ ] Document the profiling method
* [ ] Document the local environment
* [ ] Document measured bottlenecks
* [ ] Document approved optimizations
* [ ] Document rejected optimizations
* [ ] Document benchmark comparisons
* [ ] Document remaining performance risks
* [ ] Update project state and changelog

#### Exit Criteria

* [ ] A local benchmark baseline has been captured
* [ ] Main benchmarked execution paths have been profiled
* [ ] Profiling results are based on deterministic scenarios
* [ ] Provider and network latency remain excluded
* [ ] Machine-specific profile artifacts are ignored by Git
* [ ] Meaningful bottlenecks are documented
* [ ] Optimization candidates are ranked by evidence
* [ ] Public API compatibility is preserved
* [ ] Every accepted optimization has before-and-after measurements
* [ ] Low-value optimizations are explicitly rejected
* [ ] Normal tests pass
* [ ] Benchmark correctness checks pass
* [ ] Performance benchmarks pass
* [ ] Black passes
* [ ] Ruff passes

Result:

Python AI Toolkit has an evidence-based understanding of its internal performance characteristics and documented optimization decisions before Version 1.0.


## PROD-003 — Complete Documentation

### Goal

Make the toolkit understandable and usable without reading its implementation.

### Tasks

* [ ] DOC-001 Review README structure and remove duplication
* [ ] DOC-002 Document installation and optional extras
* [ ] DOC-003 Document environment and explicit configuration
* [ ] DOC-004 Document provider registration
* [ ] DOC-005 Document plain and structured requests
* [ ] DOC-006 Document streaming, async, tools, and image inputs
* [ ] DOC-007 Document embeddings, retrieval, and RAG
* [ ] DOC-008 Document memory, agents, workflows, and orchestration
* [ ] DOC-009 Document Django, FastAPI, and CLI integrations
* [ ] DOC-010 Document exceptions and error handling
* [ ] DOC-011 Document security and secret-handling guidance
* [ ] DOC-012 Document Python-version and provider compatibility
* [ ] DOC-013 Create a stable public API reference
* [ ] DOC-014 Verify every documented example

### Documentation Rules

* Documentation must match the implemented public API.
* Examples must be executable or clearly marked as illustrative.
* API keys must never appear in documentation.
* Deferred capabilities must not be described as implemented.
* Provider-specific behavior must be clearly distinguished from provider-independent behavior.

### Exit Criteria

* [ ] New users can install and make a first request
* [ ] Advanced users can find all major capabilities
* [ ] Integrations and optional dependencies are documented
* [ ] Public APIs and exceptions are documented
* [ ] All documented code is verified

---

## PROD-004 — Additional Examples

### Goal

Fill important example gaps required for a Version 1.0 release.

### Tasks

* [ ] EXAMPLE-001 Explicit `AIConfig` injection
* [ ] EXAMPLE-002 Custom provider registration
* [ ] EXAMPLE-003 Testing application code with a fake provider
* [ ] EXAMPLE-004 Batch embedding and retrieval
* [ ] EXAMPLE-005 End-to-end document indexing and RAG
* [ ] EXAMPLE-006 Structured application service example
* [ ] EXAMPLE-007 Review and normalize all example descriptions
* [ ] EXAMPLE-008 Verify all examples against current APIs

### Example Rules

* Examples must focus on toolkit behavior.
* Business logic must remain small and illustrative.
* Examples must not require undocumented setup.
* Network-dependent examples must clearly state their requirements.
* Examples must not contain real credentials.

### Exit Criteria

* [ ] Important public APIs have examples
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
* Immutable / reusable request builders
* DX-006 Add local image file helper

## Observability, Benchmarking, and Evaluation

* Metrics dashboard
* Web dashboard
* Automatic model benchmarking
* AI evaluation framework

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