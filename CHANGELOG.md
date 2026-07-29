# Changelog

All notable changes to this project will be documented here.

The format loosely follows Keep a Changelog.

---
### Fixed

* Explicit configuration now rejects wrong runtime field types, incomplete or
  invalid custom token pricing, and other structurally invalid values as
  `AIConfigurationError` before client side effects
* OpenAI tool responses now reject JSON arguments that are not objects
* OpenAI embedding responses now reject invalid, duplicate, or missing indices
  and restore valid batches to input order before attaching text and metadata
* Provider-factory tests no longer construct live SDK transports or depend on
  ambient proxy settings, and unsupported-provider coverage now exercises the
  intended failure path
* Both clients now reject invalid supplied `AIConfig` values before provider,
  logger, or executor construction
* Agent prompts include the current user message once while preserving the
  message-count memory limit and partial-memory failure behavior
* Multi-agent sequences validate every requested agent name before execution,
  preventing lookup errors from occurring after earlier agents have run
* Empty `MultiAgentResponse` objects now report `success=False`
* Made distribution README validation independent of Windows `CRLF` versus
  Unix `LF` line endings while continuing to reject real content differences
* Normalized the development package version to `0.7.0.dev0` instead of
  declaring the in-progress code as a final `0.7.0` distribution
* Added minimum compatible OpenAI and Pydantic versions to the core dependency
  metadata
* Python 3.11-compatible multiple-exception handling in `RequestExecutor`
* Structured parse and schema errors no longer include raw provider responses
  that could be copied into exception logs
* Corrected the example-gallery command to use the existing
  `examples.01_plain_text` module
* Added the missing `Document` import to the retrieval-guide example
* Aligned the Base64 image-helper example with its documented structured-image
  behavior

### Added
* Installed-core release verification now executes deterministic plain and
  structured `AIClient` requests in addition to import, dependency, prompt,
  vector-store, and optional-framework checks
* Version 1.0 release-blocker audit documenting reproduced defects, fixes,
  excluded backlog work, and required evidence
* Approved Version 1.0 public API contract covering supported module imports,
  call signatures, data models, enum values, exceptions, extension interfaces,
  return boundaries, orchestration semantics, and compatibility policy
* Permanent public-contract regressions for the frozen symbol inventory,
  callable parameters, model fields, enums, exception hierarchy, and abstract
  extension methods
* ADR-0017 establishing automatic client-boundary configuration validation
* ADR-0018 approving the complete Version 1.0 compatibility boundary
* Manual non-production release-workflow rehearsal that runs tag-shaped version
  validation, the Python 3.11–3.14 matrix, distribution construction, both
  artifact validators, and artifact retention while structurally skipping the
  PyPI publishing job
* Rehearsal documentation and regressions covering the expected GitHub job
  results, validated artifact identity, cleanup, limitations, and the
  production-only OIDC boundary
* Complete maintainer release procedure covering one-time trusted-publisher
  setup, version preparation, local and CI gates, exact tagged-commit
  verification, protected PyPI approval, clean installation smoke testing, and
  failure recovery
* Release-documentation regressions preserving the tag, quality, artifact,
  identity, approval, and immutable-version safety boundaries
* Tokenless PyPI trusted publishing from validated version-tag artifacts,
  isolated in a protected `pypi` environment with identity-token permission
  granted only to the publishing job
* Release-workflow regressions preventing branch, pull-request, secret-based,
  unvalidated-artifact, source-checkout, and rebuild paths from reaching PyPI
* One-time PyPI pending-publisher and GitHub environment configuration guidance
* Tag-only release-candidate workflow that verifies the package version,
  repeats the Python 3.11–3.14 quality matrix, and builds and validates both
  distributions from the exact tagged commit without publishing
* Reusable release-tag validator and regression coverage for exact
  tag-to-package-version agreement, tagged-source identity, read-only
  permissions, quality gates, artifact validation, and publishing exclusion
* CI validation gates that run strict Twine and project-specific offline
  archive checks against the exact built wheel and source distribution before
  artifact upload
* CI regressions preserving build-before-validation, validation-before-upload,
  read-only permissions, and separation from package publishing
* CI distribution-build job that waits for every supported-version quality job,
  builds the wheel and source distribution, and retains both as a GitHub Actions
  artifact without publishing
* CI regressions preserving the build job's quality dependency, expected
  distribution formats, read-only permissions, and separation from validation
  and publishing
* Repository-wide Black and Ruff enforcement in every supported-version CI job
* Narrow Ruff configuration preserving the numbered example-gallery filenames
  while continuing to lint all example content
* CI regressions requiring formatting, linting, tests, and dependency checks
  without granting build, artifact, or publishing responsibilities
* Python 3.11–3.14 continuous-integration matrix with independent jobs,
  fail-fast disabled, full tests, and dependency validation on every supported
  interpreter
* Python 3.11–3.14 package classifiers backed by full-suite verification
* Windows PowerShell instructions for repeating the supported-version matrix
  locally
* Initial read-only GitHub Actions continuous-integration workflow for pushes
  and pull requests, installing the project from `pyproject.toml`, validating
  dependencies, and running the normal test suite on Python 3.11
* Regression coverage preserving the initial CI triggers, permissions,
  installation source, checks, and separation from later release tasks
* Local commands equivalent to the initial continuous-integration checks
* Separate clean-wheel verification for the Django and FastAPI extras, proving
  each adapter works while the unselected framework remains absent
* Reusable installed-extra verifier covering metadata, import origin, complete
  adapter modules, supported framework versions, and offline client behavior
* Windows PowerShell guidance for testing the Django and FastAPI wheel extras in
  independent virtual environments
* Core-only wheel installation verification proving that Django and FastAPI
  remain absent while all 35 non-framework toolkit modules import successfully
* Reusable installed-environment verifier covering core requirements, import
  origin, optional-framework absence, and offline prompt and vector behavior
* Windows PowerShell guidance for repeating the core-only installation check
* Clean virtual-environment installation verification from both the wheel and
  source distribution, including installed-path, version, offline public API,
  console-command, configuration, and dependency checks
* Windows PowerShell guidance for installing and checking each built artifact
  outside the source checkout
* Strict Twine validation for the wheel and source distribution, including the
  rendered Markdown long description and modern license metadata
* Reusable offline distribution validator covering archive safety, exact source
  contents, metadata agreement, wheel RECORD hashes, and unintended files
* Windows PowerShell guidance for validating both artifacts and removing an
  older generated `python_ai_toolkit.egg-info/` directory from Git tracking
* Reproducible local construction of the `0.7.0.dev0` wheel and source
  distribution with the standard `python -m build` workflow
* Windows PowerShell guidance for cleaning older generated package output,
  building both distribution formats, and inspecting the resulting filenames
* Regression coverage keeping `build/`, `dist/`, and `*.egg-info/` out of
  source control
* Clean-install verification that the `ai-toolkit` executable is generated,
  loads `ai.cli.main:main`, routes supported commands, and preserves exit codes
* Focused regressions keeping console-script metadata and the installed entry
  point aligned with the supported CLI implementation
* Windows PowerShell steps for locating and testing the installed console
  command without making a provider request
* Clean-environment verification for the core, Django, FastAPI, development,
  and benchmark installation shapes
* Focused regressions preserving the exact optional groups, keeping optional
  packages out of core metadata, and isolating framework imports
* MIT license text and current SPDX license metadata for source and binary
  distributions
* Focused regressions keeping the declared license, distributed license file,
  copyright owner, and compatible build backend aligned
* PyPI classifiers for the beta development status, developer audience,
  console environment, framework integrations, platform, language, and project
  topics
* Focused regressions preventing package classifiers from overstating stable
  status, unverified Python-minor support, or unresolved license metadata
* Focused package-metadata regressions for project identity, README metadata,
  runtime dependencies, and complete `ai*` package discovery
* Regression coverage requiring every example module to have a deterministic
  execution path
* Regression coverage preventing examples from importing undocumented toolkit
  modules or symbols
* Framework-independent structured application service example with injected
  `AIClient`, local input validation, application-owned routing, error mapping,
  and request traceability
* Deterministic regression coverage for the complete structured service
  workflow without credentials or network access
* End-to-end document indexing and grounded RAG example with explicit document
  preparation, stable IDs, batch-order restoration, retrieval, and source
  contexts
* Deterministic regression coverage for the complete loader-to-answer workflow
  without credentials or network access
* Batch embedding and retrieval example with input-order restoration, stable
  record IDs, metadata preservation, vector storage, and filtered retrieval
* Deterministic regression coverage for one-request batch embedding,
  out-of-order provider results, query embedding, and relevant-context ranking
* Fake-provider application testing example with scoped factory substitution
* Regression coverage for deterministic structured application behavior,
  captured prompts, explicit test configuration, and registry isolation
* Custom provider registration example with a deterministic local provider
* Regression coverage for process-local registration, factory construction,
  and plain-text execution through `AIClient`
* Explicit `AIConfig` injection example with application-owned secret lookup
* Deterministic regression coverage for explicit configuration precedence and
  pre-client validation
* Explicit `AIConfig` injection for `AIClient`
* Explicit `AIConfig` injection for `AsyncAIClient`
* Optional Django integration
* Django settings-to-`AIConfig` adapter
* Synchronous Django client helper
* Asynchronous Django client helper
* Django support ticket analysis example
* Optional FastAPI integration
* Synchronous FastAPI client dependency
* Asynchronous FastAPI client dependency
* Reusable FastAPI `Annotated` dependency aliases
* FastAPI endpoint testing with dependency overrides
* FastAPI support ticket analysis example
* Command-line interface
* `ai-toolkit` console command
* Plain-text `ask` subcommand
* CLI subcommand-handler architecture
* Standard CLI exit codes
* Clean command-line handling for expected toolkit errors
* Configurable toolkit log level
* Configurable toolkit log file path
* Option to disable toolkit-managed file logging
* Logger injection for synchronous and asynchronous request executors
* Benchmark-safe and test-safe logging behavior
* Isolated benchmark suite powered by pytest-benchmark
* Separate benchmark optional dependency group
* Benchmark smoke test
* Benchmark-specific configuration and fixtures
* Benchmark development documentation
* Deterministic synchronous and asynchronous benchmark providers 
* Sequential fake provider for retry and response-repair benchmarks 
* Shared benchmark token-usage and provider-response fixtures 
* Isolated no-output logger for direct executor benchmarks 
* Structured JSON response parsing and Pydantic validation benchmark 
* Structured-response retry and JSON repair lifecycle benchmark 
* In-memory vector similarity search benchmark 
* Metadata-filtered vector search benchmark 
* Retrieval-Augmented Generation orchestration benchmark
* Single-step workflow execution benchmark 
* Five-step sequential workflow and state-propagation benchmark 
* Complete deterministic benchmark suite for request execution, structured parsing, retry repair, vector search, RAG orchestration, and workflow execution 
* Version 1.0 internal performance baseline documentation
* Deterministic profiling instruments for request, structured-response, vector-search, RAG, and workflow execution paths
* Consolidated performance-profiling report with optimization decisions and remaining risks
* Focused configuration guide covering environment and explicit configuration
* Focused provider guide covering registration, constructor contracts,
  capabilities, lifecycle, and errors
* Focused request guide covering plain and structured requests, `AIResult`
  metadata, Pydantic validation, and response repair
* Focused advanced-request guide covering streaming, asynchronous requests,
  tool calling, image inputs, return contracts, and provider capability limits
* Focused retrieval and RAG guide covering embeddings, vector search,
  retrievers, document loading, response contracts, and grounding boundaries
* Focused orchestration guide covering conversation memory, agents, workflows,
  multi-agent sequencing, result contracts, and failure boundaries
* Focused integration guide covering Django settings and client helpers,
  FastAPI dependencies and test overrides, and CLI commands and exit behavior
* Focused exception and error-handling guide covering the toolkit hierarchy,
  application catch boundaries, retry decisions, ordinary Python exceptions,
  result-based failures, framework propagation, and CLI behavior
* Focused security and secret-handling guide covering environment-specific
  credential sources, sensitive request and result data, provider governance,
  logging, tool authorization, multi-tenant boundaries, and incident response
* Focused compatibility guide covering declared and verified Python versions,
  dependency resolution, provider SDK and model boundaries, optional
  frameworks, and contributor verification
* Stable public API reference covering supported import paths, signatures,
  typed models, extension interfaces, exceptions, lifecycle boundaries, and
  Version 1.0 API-freeze review items
* Documented-example verification record and deterministic example regression
  tests


### Improved
* Replaced every deferred Version 1.0 API-review item with an explicit decision
  while keeping internal executors, provider adapters, low-level helpers, and
  top-level package re-exports outside the supported surface
* Installation and compatibility guidance for the distribution name, import
  package, console command, development version, dependency floors, and
  intentionally unconfirmed project URLs
* Final current-public-API verification for every numbered, variant,
  framework, command, and supplementary example
* Normalized every numbered and supplementary example description around one
  file/command, behavior, requirements, run, and boundary format
* Explicit example numbering guidance for CLI workflows 21–22, the example-09
  Base64 variant, and preserved unnumbered module paths
* Regression coverage requiring every example module to appear in the gallery
  with the normalized description fields
* Installation guidance for local users, optional integrations, contributors,
  and benchmark environments
* Configuration reference for defaults, precedence, validation, and CLI checks
* Framework integration architecture
* Configuration flexibility for applications and tests
* Django configuration without process-wide environment mutation
* Framework integration coverage
* FastAPI endpoint integration with less dependency boilerplate
* Testability through FastAPI dependency overrides
* Toolkit accessibility from terminal environments
* Error reporting for command-line usage
* Reuse of the existing `AIClient` request lifecycle from the CLI
* Configuration visibility and troubleshooting
* Clear distinction between structural validation and live credential verification
* Clear distinction between configuration validation, provider registration,
  and live provider verification
* Clear distinction between structured response validation and application
  business validation
* Clear distinction between advanced-request return values, application-owned
  tool execution, and provider/model capability support
* Clear distinction between similarity ranking, factual confidence, returned
  contexts, and verified citations
* Clear distinction between message-count memory limits, agent request
  metadata, workflow state, partial failures, and application-owned
  orchestration
* Clear distinction between framework configuration sources, client
  lifetimes, dependency overrides, structural CLI checks, and live provider
  requests
* Clear distinction between classified toolkit exceptions, ordinary Python
  failures, structured repair, provider retries, and failure-bearing result
  objects
* Repository safeguards for local `.env.*` files while keeping
  `.env.example` tracked
* Clear distinction between toolkit safeguards and application-owned secret
  storage, data access, provider policy, output filtering, and incident
  response
* Clear distinction between package installation, tested Python environments,
  dependency compatibility, provider adapters, SDKs, accounts, regions, and
  model capabilities
* Clear distinction between supported public imports, compatibility helpers,
  extension interfaces, implementation details, and importable names awaiting
  Version 1.0 API-freeze decisions
* Verified user-facing Python snippets, numbered examples, installation paths,
  framework workflows, CLI commands, and documentation links
* Made the asynchronous `ask_text()` example independently valid inside an
  async function
* Clear ownership boundary between the FastAPI runtime extra, application-chosen
  ASGI servers, and test-client dependencies
* Command-line secret-handling safeguards
* Reuse of the existing configuration loader and validator from the CLI
* Logging behavior in tests, benchmarks, and continuous integration
* Preservation of application-owned logging handlers
* Synchronous and asynchronous logging consistency
* Configuration CLI output for logging settings
* Separation between correctness tests and performance benchmarks
* Benchmark reproducibility through deterministic execution rules
* Benchmark safety by disabling toolkit-managed file logging 
* Benchmark independence from network access and provider credentials 
* Detection of unexpected additional provider calls in retry benchmarks 
* Separation between benchmark infrastructure correctness tests and timing measurements
* Performance visibility for structured-response parsing independent of provider and request lifecycle overhead 
* Performance visibility for response repair, retry handling, and token-usage aggregation 
* Performance visibility for cosine similarity ranking and metadata filtering
* Performance visibility for context formatting, grounded prompt construction, and RAG response assembly
* Performance visibility for workflow context creation, sequential step execution, state updates, and result assembly 
* Benchmark execution, interpretation, comparison, and extension guidance
* Benchmark completion verification without network access, provider credentials, or toolkit-managed file logging
* Request-time cost estimation through pre-resolved pricing
* Disabled-INFO request logging by avoiding unnecessary metadata serialization
* In-memory vector search through query-norm reuse and combined candidate-vector calculations


## [0.7.0] - In Development

### Added

* Conversation memory
* Message roles for system, user, assistant, and tool messages
* In-memory conversation memory
* Conversation formatting helper
* Agent abstraction
* Memory-backed agent implementation
* Agent response model
* Recent memory limit for agents
* Workflow engine
* Workflow context
* Workflow step results
* Function-backed workflow steps
* Sequential workflow execution
* Workflow state passing
* Workflow execution history
* Multi-agent orchestration
* Named agent registration
* Single-agent execution by name
* Sequential multi-agent execution
* Multi-agent result collection
* Multi-agent failure handling
* Read-only Configuration CLI
* `ai-toolkit config show` command
* `ai-toolkit config validate` command
* API-key masking for configuration output
* Structural configuration validation from the terminal
* Safe formatting for optional configuration values


### Improved

* Agent and workflow composability
* Multi-turn conversation support
* Reusable AI workflow primitives
* Separation between agents, memory, workflows, and orchestration

---

## [0.6.0]

### Added

* Embedding support
* Provider-independent embedding models
* OpenAI embedding adapter
* Embedding metadata preservation
* Separate embedding model configuration
* Optional embedding dimensions configuration
* Vector store abstraction
* In-memory vector store
* Cosine similarity search
* Metadata filtering for vector search
* Retriever interface
* Vector-store-backed retriever
* Retrieved context model
* Retrieved context formatting helper
* RAG response model
* RAG prompt builder
* RAG pipeline
* Answer generation with returned sources
* Document model
* Base document loader interface
* Text file loader
* Markdown file loader
* Directory loader
* Document-to-embedding conversion helper

### Improved

* Retrieval-Augmented Generation support
* Provider-independent retrieval architecture
* Document-based knowledge workflows
* Source metadata preservation
* End-to-end RAG examples

---

## [0.5.0]

### Added

* Streaming text responses
* Async AI client
* Async request executor
* Async provider method support
* Tool calling models
* Provider-independent tool definitions
* Provider-independent tool call responses
* OpenAI tool-call adapter
* Image input models
* Provider-independent image inputs
* OpenAI image-input adapter
* Image requests with plain text responses
* Image requests with structured responses
* Centralized structured-output helpers

### Improved

* Structured-output prompt construction
* Structured-response parsing
* Sync and async request consistency
* Advanced provider capability support
* Public API coverage for streaming, async, tools, and image inputs

---

## [0.4.0]

### Added

* Fluent request builder
* `AIClient.request()`
* Prompt templates
* Example gallery
* Configuration validator
* Error message guidelines

### Improved

* Developer experience
* Configuration validation
* Helpful error messages
* README documentation
* Example coverage

---

## [0.3.0]

### Added

* Provider abstraction layer
* Base provider interface
* OpenAI provider implementation
* Provider factory
* Provider registry
* Custom provider registration
* Provider-aware configuration
* Provider-specific API key and model settings
* Generic provider fallback settings
* Configurable retry count
* Provider response wrapper
* Token usage model
* Cost estimation support
* Request IDs
* Request duration tracking
* File logging
* Custom exception hierarchy

### Improved

* Provider independence
* Request traceability
* Logging quality
* Error reporting
* Configuration cleanup

---

## [0.2.0]

### Added

* Core `AIClient`
* Request executor
* Structured Pydantic responses
* `AIResult` wrapper
* Automatic JSON parsing
* Schema validation
* Automatic retry for structured responses
* Retry repair prompt helper
* Prompt builder
* Environment configuration
* Architecture documentation
* Development roadmap
* Project state documentation
* Initial test coverage

### Improved

* Core request lifecycle
* Structured response validation
* Retry behavior
* Project documentation

---

## [0.1.0]

### Added

* Repository initialization
* Initial project structure
* Virtual environment setup
* Git configuration
* Initial README
