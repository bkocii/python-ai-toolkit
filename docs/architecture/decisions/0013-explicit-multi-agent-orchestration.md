# ADR-0013

## Title

Use explicit sequential multi-agent orchestration

---

## Status

Accepted

---

## Date

2026-07-19

---

## Context

Sprint 7 added multi-agent orchestration.

Multi-agent systems can be designed in many ways:

- explicit sequential pipelines
- AI-based routing
- agent-to-agent debate
- recursive loops
- parallel execution
- shared memory systems

More autonomous designs can be powerful, but they also make behavior harder to predict, test, and control.

The toolkit needed a first multi-agent layer that is useful, safe, and easy to reason about.

---

## Decision

Introduce an explicit sequential `MultiAgentOrchestrator`.

Applications register named agents:

```python
orchestrator.register_agent("technical", technical_agent)
orchestrator.register_agent("reviewer", reviewer_agent)
```

Applications can run one selected agent:

```python
orchestrator.run_agent(
    agent_name="technical",
    message="Explain Redis.",
)
```

Applications can run a named sequence:

```python
orchestrator.run_sequence(
    agent_names=["technical", "reviewer", "summary"],
    message="Explain Redis for Django.",
)
```

In a sequence, each successful agent output becomes the next agent input.

The orchestrator does not perform autonomous routing, debate, recursion, or parallel execution.

---

## Alternatives Considered

### AI-based agent routing

Rejected for the first implementation because it adds unpredictability and requires routing evaluation.

Explicit routing is easier to test and debug.

### Agent-to-agent debate

Rejected because debate-style systems can increase cost, latency, and complexity.

They also require rules for stopping, judging, and merging outputs.

### Parallel multi-agent execution

Rejected for now because the current workflow and agent layers are synchronous and sequential.

Parallel orchestration can be added later.

### Shared global memory

Rejected for the first implementation because shared memory introduces ownership and contamination questions between agents.

Each agent can have its own memory for now.

---

## Consequences

### Positive

- Multi-agent behavior is explicit and predictable.
- Tests can verify exact agent order.
- Failures are easy to inspect.
- Applications control which agents run.
- The design avoids recursive or uncontrolled loops.

### Negative

- No automatic agent selection.
- No parallel speedup.
- More advanced collaboration patterns are deferred.
- Applications must define the sequence manually.

---

## Related Files

- `ai/orchestrator.py`
- `ai/agent.py`
- `tests/test_orchestrator.py`
- `examples/18_multi_agent_orchestration.py`
