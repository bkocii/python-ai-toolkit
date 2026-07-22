# Changelog

All notable changes to this project will be documented here.

The format loosely follows Keep a Changelog.

---
### Fixed

* Python 3.11-compatible multiple-exception handling in `RequestExecutor`

### Added
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


### Improved
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
