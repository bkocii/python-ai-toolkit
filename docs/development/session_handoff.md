# Python AI Toolkit - Session Handoff

## Project

Python AI Toolkit

Current Version: 0.7.0-dev

---

# Goal

Continue developing this project following the existing architecture, roadmap, decisions, and workflow.

Do NOT redesign or skip ahead unless there is a strong architectural reason.

The project has completed:

* Sprint 4 – Developer Experience
* Sprint 5 – Advanced Requests
* Sprint 6 – Retrieval & Knowledge
* Sprint 7 – Agents & Workflows
* Sprint 8 – Framework Integrations

The next roadmap milestone is Sprint 9 – Production Readiness.

Before implementation, inspect the current roadmap and architecture, then design the correct scope for `PROD-001 Benchmark suite`.

---

# Documents Included

The following documents are the source of truth.

1. `project_state.md`
2. `roadmap.md`
3. `architecture.md`
4. `future_backlog.md` or the Future Backlog section inside `roadmap.md`

Reference documents, only if needed:

* `README.md`
* `CHANGELOG.md`
* Architecture Decision Records:

  * `0001-airesult.md`
  * `0002-provider-response.md`
  * `0003-request-executor.md`
  * `0004-retry-repair.md`
  * `0005-provider-factory.md`
  * `0006-provider-configuration.md`
  * `0007-provider-registration-api.md`
  * `0008-separate-async-client.md`
  * `0009-tool-calling-without-auto-execution.md`
  * `0010-provider-independent-rag-abstractions.md`
  * `0011-document-loaders-separate-from-embedding.md`
  * `0012-memory-agent-workflow-separation.md`
  * `0013-explicit-multi-agent-orchestration.md`
  * `0014-explicit-configuration-injection-for-framework-integrations.md`
  * `0015-command-line-interface-architecture.md`


---

# Workflow

Every roadmap task follows this order:

1. Design
2. Code
3. Tests
4. Documentation
5. Review
6. Git
7. Roadmap update
8. Project state update, only if milestone changes

A task is NOT complete until every applicable step is complete.

---

# Roadmap Rules

* Only one sprint is active.
* Before starting the next task, verify it is still the correct next task.
* If a better architectural decision exists:

  * explain why
  * update the roadmap
  * then continue
* Never silently change the roadmap.
* New ideas go into Future Backlog.
* Future Backlog items should not interrupt the active roadmap unless they:

  * block the current sprint
  * fix a design issue
  * prevent important technical debt
  * are required by the next roadmap task

---

# Coding Rules

Before changing existing code:

* Read the current implementation.
* Never assume the current implementation.
* Verify the file first.
* Minimize unnecessary refactoring.
* Preserve existing public APIs unless there is a documented architectural reason.
* If changing public APIs, create an ADR.

When suggesting changes:

* Prefer showing only the changed lines.
* Do not rewrite entire files unless necessary.
* Keep each roadmap task as a separate commit.

---

# Documentation Rules

Architecture changes:

→ Add ADR.

Public API changes:

→ Update README.

Completed roadmap task:

→ Update ROADMAP immediately.

Completed sprint or version-level feature set:

→ Update CHANGELOG.

Project milestone changes:

→ Update PROJECT_STATE.

Important future ideas:

→ Add to Future Backlog.

Do not create ADRs for every small feature. Create ADRs only when the decision affects architecture, public API, provider independence, safety, extensibility, or many files.

---

# Engineering Principles

Follow these principles:

* Single Responsibility Principle
* Dependency Inversion
* Composition over inheritance
* Strong typing
* Explicit interfaces
* Small public API
* Provider independence

Business logic belongs in applications, not in the toolkit.

---

# Communication Style

Act as a senior software architect and mentor.

Always explain:

* What we are building
* Why we are building it
* Why this approach was chosen
* Why alternatives were rejected, when relevant

Do not simply provide code.

Teach the engineering decisions behind the code.

---

# Review Process

After every completed roadmap task, perform:

✓ Design Review

✓ Code Review

✓ Test Review

✓ Documentation Review

✓ Git Commit Suggestion

✓ Roadmap Update

✓ Sprint Status

Only after this continue to the next roadmap item.

---

# Current State

Read the attached `project_state.md`.

Do not rely only on memory. The current project state file is the source of truth.

---

# Current Roadmap

Read the attached `roadmap.md`.

Verify the next sprint/task before continuing.

---

# Current Architecture

Read the attached `architecture.md`.

Check architecture consistency before adding new features.

---

# Current Future Backlog Notes

The Future Backlog is a parking lot, not the active implementation plan.

Known backlog ideas include:

* Local LLM support
* Metrics dashboard
* Plugin system
* Web dashboard
* Automatic model benchmarking
* AI evaluation framework
* MCP support
* Additional providers
* Automatic provider discovery
* Immutable / reusable request builders
* DX-006 Add local image file helper
* Persistent conversation memory
* Database-backed conversation memory
* Token-aware memory trimming
* Conversation summarization memory
* Vector-based long-term memory
* PDF document loader
* DOCX document loader
* HTML document loader
* Database document loader
* Automatic document chunking
* Markdown section-aware loader
* File watching and re-indexing
* Configurable document loader registry by file extension
* High-level document indexing helper
* RAG streaming responses
* Async RAG pipeline
* Structured RAG responses
* RAG citations formatter
* RAG reranking
* RAG evaluation framework
* Hybrid keyword + vector retrieval
* Agent prompt template customization
* Streaming agent responses
* Async agent
* RAG-aware agent
* Tool-using agent
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
* Autonomous multi-agent planning
* Test-safe logging configuration
* Configurable log file path and log level
* Option to disable file logging during tests

Do not implement Future Backlog items unless they become part of the active roadmap or are required to unblock the current task.

---

# Important

If anything is unclear:

Read the project files first.

Do not guess.

If a previous implementation might have changed, inspect it before proposing modifications.

Architecture consistency is more important than adding new features quickly.
