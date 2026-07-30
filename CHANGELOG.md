# Changelog

All notable changes to this project will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - Unreleased

Version 1.0.0 is the first stable API release. The package metadata remains
`1.0.0`, but this release has not yet been tagged or published.

The former `0.7.0.dev0` development line was never a separate stable release.
Its agent, workflow, orchestration, and configuration-CLI work is included
here rather than duplicated in a second release section.

### Added

* Conversation messages, in-memory conversation memory, and message-count
  history limits
* Memory-backed agents with typed responses
* Sequential workflows with explicit context, state updates, step results,
  execution history, and fail-fast behavior
* Explicit multi-agent registration, named execution, sequential handoff, and
  per-agent result collection
* Explicit `AIConfig` injection for synchronous and asynchronous clients
* Optional Django settings and client helpers
* Optional FastAPI client dependencies and dependency-override support
* The `ai-toolkit` command with `ask`, `config show`, and `config validate`
  subcommands
* Configurable toolkit log level, file path, and file-logging switch
* MIT licensing and installable core, Django, FastAPI, development, and
  benchmark dependency groups
* A documented and regression-tested Version 1.0 public API of 71 symbols
  across 25 explicit module paths
* Focused guides for configuration, providers, requests, advanced requests,
  retrieval and RAG, orchestration, integrations, error handling, security,
  compatibility, installation, and releases
* Deterministic examples for explicit configuration, custom providers,
  application testing, batch retrieval, end-to-end RAG, and structured
  application services
* Deterministic benchmarks and profiling for request execution, structured
  parsing and repair, vector search, RAG, and workflows

### Changed

* Both client constructors now validate resolved configuration before creating
  a provider, logger, or executor
* Explicit configuration is a complete replacement for environment loading;
  omitted values use `AIConfig` defaults rather than values from `.env`
* Configuration validation now enforces documented runtime types, whole-number
  retry and embedding-dimension values, and complete finite non-negative custom
  token pricing
* Valid OpenAI embedding batches are restored to input order before text and
  metadata are attached
* Agent prompts include the current user message exactly once
* Multi-agent sequences validate every requested agent name before the first
  agent runs, and an empty `MultiAgentResponse` is unsuccessful
* Python 3.11, 3.12, 3.13, and 3.14 are the verified release matrix
* Core metadata now declares minimum compatible OpenAI and Pydantic versions,
  while Django and FastAPI remain optional extras
* The frozen API uses documented module imports; the top-level `ai` package
  intentionally provides no Version 1 re-exports

### Fixed

* Invalid explicit configuration now consistently raises
  `AIConfigurationError` instead of leaking incidental `AttributeError` or
  `TypeError`
* Tool-call arguments that decode to a JSON value other than an object now
  raise `AIProviderError`
* Invalid, duplicate, or missing embedding indices now raise
  `AIProviderError` instead of misassociating input text and metadata
* Structured parse and schema errors no longer include raw provider responses
  that could be copied into application logs
* `RequestExecutor` uses Python 3.11-compatible multiple-exception handling
* Distribution README validation accepts Windows and Unix line endings while
  still rejecting content differences
* Documented example commands, imports, and Base64 structured-image behavior
  now match the executable examples

### Security

* Configuration CLI output masks API keys and avoids accepting secrets as
  command arguments
* Repository safeguards ignore local `.env.*` files while preserving the
  shareable `.env.example`
* Release publishing uses short-lived PyPI Trusted Publishing credentials,
  with identity-token permission isolated to the protected publishing job
* Branches, pull requests, manual rehearsals, unvalidated artifacts, source
  rebuilds, and stored PyPI passwords or API tokens cannot reach publication

### Compatibility and upgrade notes

* Python 3.11 or newer is required; the release is verified on Python
  3.11–3.14
* Continue importing from documented modules such as `ai.client`,
  `ai.config`, and `ai.schemas`; imports such as `from ai import AIClient` are
  not part of the Version 1 contract
* Applications that construct invalid `AIConfig` objects may now fail earlier
  during client construction with `AIConfigurationError`
* A registered provider confirms construction only. It does not prove that a
  selected provider/model supports streaming, tools, images, embeddings, or
  another optional capability
* Streaming returns `Iterator[str]`, tool calling returns `ToolResponse`, and
  embedding methods return `EmbeddingResponse`; these APIs do not return
  `AIResult`
* Tool calls are returned to the application and are never executed
  automatically
* Image inputs accept URLs and Base64 data URLs, not local paths directly
* `AsyncAIClient` supports plain and structured requests; advanced async
  streaming, tools, images, and embeddings remain outside Version 1
* Install Django or FastAPI support explicitly with the `django` or `fastapi`
  extra; neither framework is installed by the core package
* The built-in provider is OpenAI. Custom providers remain available through
  the documented `BaseAIProvider` and `ProviderFactory` extension contracts

### Maintainer release readiness

* Continuous integration runs dependency checks, Black, Ruff, and the complete
  test suite independently on Python 3.11–3.14
* Clean builds produce one wheel and one source distribution and validate both
  with strict Twine checks and the offline archive validator
* Core-only, Django-only, and FastAPI-only clean-install smoke tests verify
  installed imports, CLI behavior, and deterministic request paths
* The production release workflow validates the exact tag and tagged commit,
  re-runs all quality and distribution gates, retains the validated artifacts,
  and publishes only after protected-environment approval
* A manual rehearsal exercises the production workflow without creating a tag,
  requesting an identity token, entering the protected environment, or
  publishing
* The maintainer release guide separates the release commit, tag trigger,
  protected publication, PyPI installation verification, deterministic
  installed-package smoke tests, and GitHub release notes into explicit gates

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
