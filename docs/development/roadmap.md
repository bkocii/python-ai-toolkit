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

## PROD-001 — Benchmark Suite

### Goal

Create deterministic benchmarks that measure toolkit overhead without depending on live AI providers.

### Tasks

* [x] BENCH-001 Add benchmark development tooling
* [x] BENCH-002 Create reusable fake providers and benchmark fixtures
* [x] BENCH-003 Benchmark the plain-text request lifecycle
* [x] BENCH-004 Benchmark structured-output parsing
* [x] BENCH-005 Benchmark structured-output retry repair
* [x] BENCH-006 Benchmark in-memory vector search
* [x] BENCH-007 Benchmark RAG pipeline orchestration
* [x] BENCH-008 Benchmark workflow execution overhead
* [ ] BENCH-009 Document benchmark commands and comparison workflow

### Benchmark Rules

* Benchmarks must not contact live AI providers by default.
* Benchmarks must not require real API keys.
* Benchmarks must use deterministic fake providers and fixed test data.
* Benchmarks must be stored separately from functional tests.
* Normal `python -m pytest` execution must not run the benchmark suite.
* Benchmark results must not use strict timing assertions initially.
* Machine-specific benchmark result files must not be committed.
* Functional correctness remains covered by the normal test suite.

### Initial Benchmark Groups

#### Request Lifecycle

Measure the overhead of:

```text
AIClient
    ↓
RequestExecutor
    ↓
Fake provider
    ↓
AIResult
```

The fake provider should return immediately so the result measures toolkit overhead rather than network latency.

#### Structured Output

Measure:

* valid JSON parsing
* Pydantic model validation
* structured prompt construction
* one failed response followed by a successful repair response

#### Vector Search

Measure similarity search using fixed vector dimensions and dataset sizes such as:

* 100 records
* 1,000 records
* 10,000 records, only if runtime remains practical

The benchmark should use deterministic vectors.

#### RAG Pipeline

Measure orchestration overhead using:

* a fake retriever
* fixed retrieved contexts
* a fake AI client
* no embedding API call
* no network request

#### Workflow Engine

Measure sequential execution using fixed workflow sizes such as:

* 5 steps
* 25 steps
* 100 steps

Workflow functions should perform small deterministic state updates.

### Exit Criteria

* [ ] Benchmark suite runs with one documented command
* [ ] No benchmark makes a live provider request
* [ ] No API key is required
* [ ] Major toolkit layers have representative benchmarks
* [ ] Benchmark results include timing and operation-rate statistics
* [ ] Benchmark comparison instructions are documented
* [ ] Normal test execution remains unchanged

---

## PROD-002 — Performance Profiling

### Goal

Profile measured benchmark hotspots and improve performance only where evidence justifies changes.

### Tasks

* [ ] PERF-001 Review benchmark results
* [ ] PERF-002 Select the highest-impact toolkit hotspots
* [ ] PERF-003 Profile selected paths with `cProfile`
* [ ] PERF-004 Document time and allocation hotspots
* [ ] PERF-005 Implement focused optimizations
* [ ] PERF-006 Compare before-and-after benchmark results
* [ ] PERF-007 Confirm no public API regressions

### Profiling Rules

* Do not optimize based on assumptions.
* Do not refactor unrelated modules.
* Do not optimize provider network latency.
* Preserve provider independence.
* Preserve public APIs unless a release-blocking reason is documented.
* Every optimization must have benchmark evidence.

### Likely Profiling Candidates

Potential candidates include:

* structured-response parsing
* repeated prompt construction
* vector similarity calculations
* metadata filtering
* workflow state copying
* conversation-memory formatting

These are candidates only. Benchmark evidence determines the actual work.

### Exit Criteria

* [ ] Important hotspots are identified with evidence
* [ ] Optimizations have before-and-after measurements
* [ ] Functional tests still pass
* [ ] Public API behavior remains stable
* [ ] Performance findings are documented

---

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