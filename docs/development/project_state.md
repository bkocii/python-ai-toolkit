# Project State

## Project

Python AI Toolkit

## Current Version

```text
0.7.0-dev
```

## Current Milestone

```text
Sprint 9 — Production Readiness
```

## Current Sprint Status

Sprint 9 is in progress.

Completed Sprint 9 tasks:

* PROD-001 Benchmark Suite
* PROD-002 Performance Profiling
* PROD-003 Complete Documentation
* PROD-004 Additional Examples
* PROD-005 PyPI Package

Completed PROD-001 benchmark tasks:

* BENCH-000 Test-safe and benchmark-safe logging
* BENCH-001 Benchmark tooling
* BENCH-002 Deterministic fake providers and fixtures
* BENCH-003 Plain request lifecycle benchmark
* BENCH-004 Structured response parsing benchmark
* BENCH-005 Retry and repair benchmark
* BENCH-006 Vector search benchmark
* BENCH-007 RAG orchestration benchmark
* BENCH-008 Workflow execution overhead benchmark
* BENCH-009 Benchmark documentation and completion review

Completed PROD-002 profiling tasks:

* PROF-001 Capture the performance baseline
* PROF-002 Profile plain request execution
* PROF-003 Profile structured responses and repair
* PROF-004 Profile vector search
* PROF-005 Profile RAG orchestration
* PROF-006 Profile workflow execution
* PROF-007 Review optimization candidates
* PROF-008 Complete the approved-optimization implementation gate
* PROF-009 Document profiling results

Completed PROD-003 documentation tasks:

* DOC-001 Review README structure and remove duplication
* DOC-002 Document installation and optional extras
* DOC-003 Document environment and explicit configuration
* DOC-004 Document provider registration
* DOC-005 Document plain and structured requests
* DOC-006 Document streaming, async, tools, and image inputs
* DOC-007 Document embeddings, retrieval, and RAG
* DOC-008 Document memory, agents, workflows, and orchestration
* DOC-009 Document Django, FastAPI, and CLI integrations
* DOC-010 Document exceptions and error handling
* DOC-011 Document security and secret-handling guidance
* DOC-012 Document Python-version and provider compatibility
* DOC-013 Create a stable public API reference
* DOC-014 Verify every documented example

Completed PROD-004 example tasks:

* EXAMPLE-001 Explicit `AIConfig` injection
* EXAMPLE-002 Custom provider registration
* EXAMPLE-003 Testing application code with a fake provider
* EXAMPLE-004 Batch embedding and retrieval
* EXAMPLE-005 End-to-end document indexing and RAG
* EXAMPLE-006 Structured application service example
* EXAMPLE-007 Review and normalize all example descriptions
* EXAMPLE-008 Verify all examples against current APIs

Completed PROD-005 package tasks:

* PACKAGE-001 Review package metadata
* PACKAGE-002 Add package classifiers
* PACKAGE-003 Confirm license metadata and license file
* PACKAGE-004 Verify optional dependency groups
* PACKAGE-005 Verify console entry points
* PACKAGE-006 Build source distribution and wheel
* PACKAGE-007 Validate distributions
* PACKAGE-008 Test installation in a clean virtual environment
* PACKAGE-009 Test core installation without optional frameworks
* PACKAGE-010 Test Django and FastAPI extras separately

Next active task:

```text
PROD-006 — Release Automation
```

Next roadmap task:

```text
RELEASE-001 — Add continuous-integration workflow
```

---

## Implemented Capabilities

### Core Client

* `AIClient`
* `AsyncAIClient`
* plain-text requests
* structured Pydantic responses
* request metadata through `AIResult`
* request IDs
* token usage tracking
* estimated cost tracking
* retry tracking
* explicit `AIConfig` injection
* environment-based default configuration

### Providers

* provider-independent `BaseAIProvider`
* OpenAI provider implementation
* `ProviderFactory`
* provider registry
* custom provider registration
* provider-aware configuration through `AI_PROVIDER`

### Configuration

* `.env`-based configuration
* provider-specific API keys and models
* generic fallback API key and model
* separate embedding model configuration
* optional embedding dimensions configuration
* configurable retry count
* configurable toolkit log level
* configurable toolkit log file path
* option to disable toolkit-managed file logging
* configuration validation through `ConfigValidator`
* helpful configuration error messages
* read-only configuration inspection through the CLI
* structural configuration validation through the CLI

### Logging

* toolkit logger named `ai_toolkit`
* configurable log level
* configurable log file path
* optional toolkit-managed file logging
* preservation of application-owned logging handlers
* prevention of duplicate toolkit-managed handlers
* non-propagating toolkit logger
* `NullHandler` support when file logging is disabled
* logger injection into synchronous request execution
* logger injection into asynchronous request execution
* request metadata logging
* prompts and provider responses excluded from logs
* test-safe logging
* benchmark-safe logging

### Request Execution

* synchronous request execution
* asynchronous request execution
* structured-output retry repair
* centralized structured-output helpers in `ai/structured.py`
* streaming text responses
* image-input requests
* tool-aware requests

### Developer Experience

* fluent request builder
* prompt templates
* example gallery
* improved README documentation
* error-message guidelines
* public exception and error-handling guide
* console command
* configuration inspection commands
* isolated benchmark suite
* benchmark execution documentation

### Advanced Requests

* synchronous streaming text responses
* asynchronous AI client
* provider-independent tool definitions
* provider-independent tool-call responses
* OpenAI tool-call adapter
* provider-independent image inputs
* OpenAI image-input adapter
* structured-output support for text, async, and image requests

### Retrieval and Knowledge

* provider-independent embedding models
* OpenAI embedding adapter
* embedding metadata preservation
* vector-store abstraction
* in-memory vector store
* cosine similarity search
* metadata filtering
* retriever interface
* vector-store-backed retriever
* prompt-ready retrieved-context formatting
* RAG prompt builder
* RAG pipeline
* answer generation with returned sources
* document model
* text-file loader
* Markdown-file loader
* directory loader
* document-to-embedding conversion helper

### Agents and Workflows

* provider-independent conversation message model
* conversation memory interface
* in-memory conversation memory
* conversation formatting helper
* memory-backed agent abstraction
* agent response model
* system instructions
* recent-memory limit
* sequential workflow engine
* workflow context
* workflow step results
* function-backed workflow steps
* workflow state passing
* workflow execution history
* fail-fast workflow behavior
* multi-agent orchestration
* named agent registration
* single-agent execution by name
* sequential multi-agent execution
* multi-agent result collection
* multi-agent failure handling

### Framework Integrations

* optional Django integration
* Django settings-to-`AIConfig` adapter
* Django logging configuration support
* synchronous Django client helper
* asynchronous Django client helper
* optional FastAPI integration
* synchronous FastAPI client dependency
* asynchronous FastAPI client dependency
* reusable FastAPI dependency aliases
* FastAPI dependency-override testing support
* `ai-toolkit` console command
* plain-text `ask` command
* read-only configuration inspection
* structural configuration validation
* masked API-key output
* logging configuration output
* predictable CLI exit codes

### Benchmarking

* separate `benchmark` optional dependency group
* `pytest-benchmark` integration
* isolated `benchmarks/` source directory
* generated `.benchmarks/` results excluded from Git
* normal tests isolated from benchmark discovery
* deterministic synchronous fake provider
* deterministic asynchronous fake provider
* deterministic sequential retry provider
* fixed token-usage fixtures
* prebuilt provider-response fixtures
* no-output benchmark logger
* benchmark fixture correctness tests
* fake-provider correctness tests
* benchmark execution documentation
* benchmark stability policy
* benchmark interpretation guidance
* local benchmark result comparison support
* deterministic `cProfile` instruments for benchmarked execution paths
* consolidated performance-profiling report

Implemented performance benchmarks:

* benchmark tooling smoke test
* plain synchronous request lifecycle
* structured JSON parsing and Pydantic validation
* structured-response retry and repair
* unfiltered in-memory vector similarity search
* metadata-filtered vector similarity search
* RAG orchestration
* one-step workflow execution
* five-step workflow execution and state propagation

---

## Current Architecture

### Main Request Flow

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

### Configuration Flow

```text
Environment variables or explicit AIConfig
    ↓
ConfigValidator
    ↓
AIClient / AsyncAIClient
    ↓
ProviderFactory and request executor
```

### Logging Flow

```text
Environment variables or explicit AIConfig
    ↓
AILoggingConfig / AIConfig
    ↓
ConfigValidator
    ↓
get_ai_logger()
    ↓
AIClient / AsyncAIClient
    ↓
RequestExecutor / AsyncRequestExecutor
```

When toolkit-managed file logging is enabled:

```text
Configured log file path
    ↓
Create parent directory
    ↓
Create toolkit-managed FileHandler
    ↓
Write request metadata
```

When toolkit-managed file logging is disabled:

```text
File logging disabled
    ↓
Do not create log directory
    ↓
Do not create log file
    ↓
Preserve application handlers
    ↓
Use NullHandler when no other handler exists
```

### Advanced Request Builder Flow

```text
AIClient.request()
    ↓
AIRequestBuilder
    ↓
RequestExecutor
```

### Structured-Output Flow

```text
response_type
    ↓
ai.structured.build_structured_prompt()
    ↓
provider request
    ↓
ai.structured.parse_structured_response()
    ↓
AIResult[data]
```

### Structured Repair Flow

```text
invalid structured response
    ↓
parse_structured_response()
    ↓
AIJSONParseError / AISchemaValidationError
    ↓
build_json_repair_prompt()
    ↓
provider retry
    ↓
validated structured result
```

### Embedding Flow

```text
text / EmbeddingInput
    ↓
AIClient.embed_text() / AIClient.embed_texts()
    ↓
Provider.embed_texts()
    ↓
EmbeddingResponse
```

### Vector Search Flow

```text
query vector
    ↓
InMemoryVectorStore.similarity_search()
    ↓
optional metadata filtering
    ↓
cosine similarity calculation
    ↓
score sorting
    ↓
VectorSearchResult list
```

### Retriever and RAG Flow

```text
question
    ↓
RAGPipeline
    ↓
BaseRetriever.retrieve()
    ↓
format_retrieved_context()
    ↓
build_rag_prompt()
    ↓
AIClient.ask()
    ↓
RAGResponse(answer, contexts)
```

### Agent Flow

```text
user message
    ↓
Agent
    ↓
ConversationMemory
    ↓
AIClient.ask()
    ↓
AgentResponse
```

### Workflow Flow

```text
input
    ↓
WorkflowEngine
    ↓
WorkflowContext
    ↓
WorkflowStep
    ↓
WorkflowStepResult
    ↓
WorkflowContext.state
    ↓
WorkflowRunResult
```

### Multi-Agent Flow

```text
message
    ↓
MultiAgentOrchestrator
    ↓
agent 1
    ↓
agent 2
    ↓
agent 3
    ↓
MultiAgentResponse
```

### Benchmark Flow

```text
Deterministic benchmark input
    ↓
Prebuilt fake provider / retriever / client / workflow
    ↓
One defined toolkit operation
    ↓
pytest-benchmark timing
    ↓
Correctness assertions
    ↓
Local performance result
```

Benchmarks explicitly exclude:

```text
network access
real API credentials
real model execution
external provider latency
external databases
file logging
unrelated object construction
machine-specific timing assertions
```

---

## Completed Milestones

### Sprint 2 — Core Architecture

Completed:

* architecture documentation
* decision documentation
* roadmap documentation
* retry helper
* configurable retry behavior
* duplicate logging cleanup

### Sprint 3 — Provider Infrastructure

Completed:

* provider interface
* OpenAI provider implementation
* provider factory
* provider registry
* provider configuration cleanup

### Sprint 4 — Developer Experience

Completed:

* fluent request builder
* prompt templates
* example gallery
* configuration validation improvements
* better error messages

### Sprint 5 — Advanced Requests

Completed:

* streaming responses
* asynchronous client
* tool calling
* image inputs
* structured-output improvements

### Sprint 6 — Retrieval and Knowledge

Completed:

* embeddings
* vector-store abstraction
* retriever interface
* RAG pipeline
* document loaders

### Sprint 7 — Agents and Workflows

Completed:

* conversation memory
* agent abstraction
* workflow engine
* multi-agent orchestration

### Sprint 8 — Framework Integrations

Completed:

* Django integration
* FastAPI integration
* command-line interface
* configuration CLI

---

## Current Milestone Progress

### Sprint 9 — Production Readiness

Status:

```text
In Progress
```

Completed:

* PROD-001 Benchmark Suite
* PROD-002 Performance Profiling
* PROD-003 Complete Documentation
* PROD-004 Additional Examples
* PROD-005 PyPI Package

Remaining:

* PROD-006 Release Automation
* PROD-007 Version 1.0 Release

---

## PyPI Package Status

`PACKAGE-001 — Review Package Metadata`,
`PACKAGE-002 — Add Package Classifiers`,
`PACKAGE-003 — Confirm License Metadata and License File`,
`PACKAGE-004 — Verify Optional Dependency Groups`,
`PACKAGE-005 — Verify Console Entry Points`,
`PACKAGE-006 — Build Source Distribution and Wheel`,
`PACKAGE-007 — Validate Distributions`,
`PACKAGE-008 — Test Installation in a Clean Virtual Environment`,
`PACKAGE-009 — Test Core Installation Without Optional Frameworks`, and
`PACKAGE-010 — Test Django and FastAPI Extras Separately` are complete.

The current metadata now:

* identifies the distribution as `python-ai-toolkit`
* identifies the development build as `0.7.0.dev0`
* requires Python `>=3.11`
* uses `README.md` as the long description
* records Burim Koci as the author
* declares `openai>=1.66.0`, `pydantic>=2.4.2`, and `python-dotenv`
* discovers all six current `ai*` package directories
* omits unconfirmed project URLs instead of publishing placeholders
* uses ten valid PyPI classifiers for beta status, console use, optional Django
  and FastAPI integrations, developer audience, operating-system independence,
  Python 3-only support, artificial intelligence, and Python modules
* omits Python-minor classifiers until the Version 1.0 CI matrix verifies the
  intended release range
* keeps Django, FastAPI, development, and benchmark dependencies in separate
  additive groups
* keeps optional framework imports isolated from core modules
* applies the MIT License under Burim Koci's 2026 copyright
* declares the current SPDX expression `MIT`
* includes the complete `LICENSE` text through `license-files`
* requires `setuptools>=77.0.3` for current PEP 639 metadata support
* omits deprecated license classifiers
* declares `ai-toolkit = "ai.cli.main:main"` as the only console script
* generates a working installed command with documented exit codes `0`, `1`,
  and `2`
* builds `python_ai_toolkit-0.7.0.dev0.tar.gz` and
  `python_ai_toolkit-0.7.0.dev0-py3-none-any.whl` with the isolated
  `python -m build` workflow
* keeps reproducible `build/`, `dist/`, and `*.egg-info/` output outside source
  control

The wheel and source distribution build successfully. Twine strict validation
accepts both artifacts, including the UTF-8 Markdown long description and
modern MIT metadata. The reusable offline validator confirms safe paths, exact
agreement with all reviewed `ai` modules, matching metadata and required files,
valid wheel `RECORD` hashes, and no secret, cache, compiled, log, deliverable,
or nested build content.

Separate clean environments now prove that both the wheel and source
distribution install successfully, report version `0.7.0.dev0`, import the
toolkit from isolated `site-packages` directories, run representative offline
prompt and vector-store operations, generate the working console command, and
pass dependency validation. The archive validator now handles Windows and Unix
README line endings consistently without accepting real text differences.

A separate core-only environment now proves that installing the wheel without
extras does not install or expose Django or FastAPI. The installed metadata
retains exactly the three intended core requirements, all 35 non-framework
toolkit modules import from isolated `site-packages`, representative offline
prompt and vector-store behavior passes, and `pip check` reports no broken
requirements. The reusable verifier and metadata regressions keep that boundary
explicit as the package evolves.

Two additional clean environments prove each framework extra independently.
The Django-only installation loads Django `6.0.7` and every Django adapter
module while FastAPI remains absent. The FastAPI-only installation loads
FastAPI `0.140.7` and every FastAPI adapter module while Django remains absent.
Both adapters construct clients through a deterministic offline provider,
complete an offline request, and pass `pip check`. The reusable verifier keeps
the installed metadata and adapter-module inventory aligned.

Twine proves that the packaged Markdown is renderable but does not visit link
destinations. The README's repository-relative documentation links remain
appropriate for the source checkout; confirmed public project URLs and
PyPI-page link behavior must be resolved before Version 1.0 publication.

`PROD-005 — PyPI Package` is complete. The next milestone item must add the
continuous-integration workflow that will repeat the supported checks
automatically. The later full-quality release gate still owns the older
repository-wide formatting and lint findings; `PACKAGE-010` introduced none of
them.

`PACKAGE-010` completion verification passed the separate Django and FastAPI
wheel installations, 19 focused package-metadata regressions, 40
package-metadata/documentation tests, 346 normal tests, strict Twine and offline
distribution validation, and focused Black and Ruff checks. Both installed
environments loaded only their selected framework, imported every corresponding
adapter module, completed an offline integration request, and passed dependency
validation. Documentation verification inventoried 202 fenced blocks, compiled
82 Python blocks, and validated 183 repository-relative links.

---

## Benchmark Suite Status

The initial Version 1.0 benchmark suite is complete.

It provides deterministic measurements for:

* plain synchronous request execution
* structured JSON parsing
* Pydantic schema validation
* response repair and retry
* token-usage aggregation
* in-memory vector similarity search
* metadata-filtered vector search
* RAG orchestration
* one-step workflow execution
* five-step workflow execution
* workflow state propagation

The benchmark suite:

* requires no real API keys
* performs no network calls
* performs no real model execution
* performs no external database access
* performs no file access during measured operations
* disables toolkit-managed file logging
* uses deterministic input and responses
* excludes unrelated setup from timing
* verifies correctness after every measurement
* uses no strict machine-specific timing thresholds

Current expected benchmark-only result:

```text
9 passed, 4 skipped
```

The four skipped tests are benchmark infrastructure tests that do not use the `benchmark` fixture.

Current expected benchmark-directory result with timing disabled:

```text
13 passed
```

The benchmark suite establishes an observational performance baseline.

It does not yet enforce automatic regression thresholds.

---

## Performance Profiling Status

`PROD-002 — Performance Profiling` is complete.

The profiling work:

* measured plain requests, structured responses, repair, vector search, RAG,
  and workflows with deterministic local scenarios
* removed repeated configuration resolution from request-time cost estimation
* avoided unnecessary INFO logging metadata construction when INFO is disabled
* reused the query-vector norm and combined candidate-vector calculations
  during in-memory vector search
* preserved every public API and typed result contract
* rejected low-value optimizations that would add correctness, maintenance, or
  architectural risk

Completion verification passed all functional and benchmark checks. Current
unpinned Black and Ruff versions still report pre-existing repository-wide
quality findings; those findings were not mixed into the documentation-only
`PROF-009` change and remain open before the Sprint 9 full-quality exit.

Representative comparable improvements:

* plain request mean overhead: approximately `27.292 µs` to `4.551 µs`
* unfiltered vector search mean: approximately `18.984 ms` to `12.363 ms`
* metadata-filtered vector search mean: approximately `10.875 ms` to `6.574 ms`

The consolidated evidence and remaining risks are documented in:

```text
docs/development/performance_profiling.md
```

---

## Next Milestone Task

The next active roadmap item is:

```text
PROD-006 — Release Automation
```

### Next Recommended Focus

Begin `RELEASE-001 — Add continuous-integration workflow`.

`PROD-005` proved that the distribution builds, validates, installs in core and
framework-specific forms, and preserves its optional dependency boundaries.
The next task must automate the first release checks in continuous integration.

---

## Important Design Decisions

* `AIClient.ask()` remains the main simple API.
* `AIClient.request()` is the fluent advanced API.
* `AsyncAIClient` remains separate from `AIClient`.
* `AIClient` and `AsyncAIClient` accept optional explicit `AIConfig`.
* Environment configuration remains the default when explicit configuration is not supplied.
* Tool calling intentionally leaves tool execution to the application.
* Image inputs support URLs and Base64 data URLs, not local paths directly.
* Structured output remains provider-independent.
* Provider-native strict structured output is deferred.
* Embeddings use a separate embedding-model configuration.
* Retrieval is provider-independent.
* Vector storage is abstracted behind `BaseVectorStore`.
* `InMemoryVectorStore` is intended for tests, examples, demos, and small local workflows.
* Production RAG should later use a persistent vector store.
* Document loaders produce `Document`; embedding happens separately.
* Automatic chunking is intentionally deferred.
* Agents are explicit and memory-backed.
* Multi-agent orchestration is explicit and sequential.
* Autonomous routing, recursive loops, and agent debate are deferred.
* Toolkit-managed logging remains enabled by default.
* Tests and benchmarks can disable toolkit-managed file logging.
* Application-owned logging handlers must be preserved.
* Prompts and provider responses are not logged.
* Structured parse and schema exception messages exclude raw provider
  responses.
* Benchmarks measure toolkit overhead rather than provider latency.
* Benchmarks use deterministic fake providers and fixtures.
* Existing benchmarks should remain stable when internal implementations are optimized.
* New capabilities should normally receive new benchmarks instead of replacing unrelated baselines.
* Benchmark timing is observational and does not currently fail builds based on fixed thresholds.
* Live model and provider comparisons remain post-Version-1.0 Future Backlog work.

---

## Current Testing Expectations

Before committing each normal roadmap task:

```bash
python -m pytest
python -m black --check .
python -m ruff check .
```

For benchmark-related tasks:

```bash
python -m pytest
python -m pytest benchmarks --benchmark-disable -v
python -m pytest benchmarks --benchmark-only
python -m black --check .
python -m ruff check .
```

Expected benchmark-only behavior:

```text
9 passed, 4 skipped
```

Expected benchmark-directory behavior with timing disabled:

```text
13 passed
```

Generated local benchmark results under:

```text
.benchmarks/
```

must not be committed.

Real API keys must never be required by the benchmark suite.

---

## Current Git Workflow

Each roadmap task should be committed separately.

Before committing:

```bash
git status --short
git diff
```

After staging:

```bash
git diff --cached
```

After committing:

```bash
git status
git log --oneline -5
```

Sprint and task completion updates should include the relevant files:

* `docs/development/roadmap.md`
* `docs/development/project_state.md`
* `CHANGELOG.md`
* relevant architecture documentation
* relevant README documentation
* relevant tests or benchmarks

Machine-specific benchmark result files must remain untracked.
