# Roadmap

## Vision

Build a reusable, provider-independent AI engineering toolkit for Python.

The toolkit should provide production-quality infrastructure for integrating
Large Language Models (LLMs) into applications while keeping business logic
outside the toolkit.

---

# Current Version

0.3.0-dev

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
- [ ] RAG-002 Vector Store abstraction
- [ ] RAG-003 Retriever interface
- [ ] RAG-004 RAG Pipeline
- [ ] RAG-005 Document loaders

Exit Criteria

- Toolkit supports end-to-end RAG workflows.

---

# Sprint 7 – Agents & Workflows

## Goal

Build reusable autonomous AI workflows.

Tasks

- [ ] AGENT-001 Conversation memory
- [ ] AGENT-002 Agent abstraction
- [ ] AGENT-003 Workflow engine
- [ ] AGENT-004 Multi-agent orchestration

Exit Criteria

- Complex AI workflows can be composed from reusable components.

---

# Sprint 8 – Framework Integrations

## Goal

Integrate with common Python ecosystems.

Tasks

- [ ] INTEGRATION-001 Django integration
- [ ] INTEGRATION-002 FastAPI integration
- [ ] INTEGRATION-003 Command Line Interface
- [ ] INTEGRATION-004 Configuration CLI

Exit Criteria

- Toolkit easily integrates into existing Python applications.

---

# Sprint 9 – Production Readiness

## Goal

Prepare Version 1.0.

Tasks

- [ ] PROD-001 Benchmark suite
- [ ] PROD-002 Performance profiling
- [ ] PROD-003 Complete documentation
- [ ] PROD-004 Additional examples
- [ ] PROD-005 PyPI package
- [ ] PROD-006 Release automation
- [ ] PROD-007 Version 1.0.0 release

Exit Criteria

- Stable public API
- Complete documentation
- Published package
- Version 1.0.0

---

# Future Backlog

These items are intentionally excluded from the current roadmap.

Ideas

- Local LLM support
- Metrics dashboard
- Plugin system
- Web dashboard
- Automatic model benchmarking
- AI evaluation framework
- MCP support
- Additional providers
- Automatic provider discovery
- Immutable / reusable request builders
- - [ ] DX-006 Add local image file helper

Future backlog items may become roadmap tasks after the completion of a sprint.

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