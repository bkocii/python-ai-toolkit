# ADR-0012

## Title

Separate memory, agents, and workflows

---

## Status

Accepted

---

## Date

2026-07-19

---

## Context

Sprint 7 added agents and workflow capabilities.

It would be possible to build one large agent class that stores memory, builds prompts, runs tools, executes workflows, and coordinates other agents.

That approach can work for demos, but it tends to become difficult to test, reason about, and extend.

The toolkit needs reusable primitives that applications can compose.

Conversation memory, agents, and workflows solve different problems.

---

## Decision

Keep memory, agents, and workflows as separate layers.

Memory stores conversation messages:

```text
ConversationMemory
```

Agent handles one conversational turn:

```text
message
    ↓
Agent
    ↓
AIClient
    ↓
AgentResponse
```

Workflow engine composes multiple steps:

```text
input
    ↓
WorkflowStep
    ↓
WorkflowStep
    ↓
WorkflowRunResult
```

The first implementations are:

```python
InMemoryConversationMemory
Agent
WorkflowEngine
FunctionWorkflowStep
```

Agents can use memory.

Workflows can use agents.

But memory, agents, and workflows remain independently testable.

---

## Alternatives Considered

### Build one full-featured Agent class

Rejected because it would combine too many responsibilities.

A single class handling memory, tools, retrieval, workflows, and orchestration would become hard to maintain.

### Make workflows part of Agent

Rejected because workflows can include non-agent steps, such as validation, retrieval, formatting, indexing, or ordinary Python functions.

### Make memory internal to Agent only

Rejected because applications and future components may need to inspect, persist, summarize, or replace memory.

---

## Consequences

### Positive

- Each layer has one clear responsibility.
- Memory can be replaced later with persistent or database-backed memory.
- Agents remain simple and testable.
- Workflows can compose agents and non-agent steps.
- Future orchestration can build on top of these primitives.

### Negative

- Applications must wire components together.
- There are more concepts to document.
- Some convenience helpers may be needed later.

---

## Related Files

- `ai/memory.py`
- `ai/agent.py`
- `ai/workflow.py`
- `tests/test_memory.py`
- `tests/test_agent.py`
- `tests/test_workflow.py`
- `examples/15_conversation_memory.py`
- `examples/16_agent.py`
- `examples/17_workflow_engine.py`
