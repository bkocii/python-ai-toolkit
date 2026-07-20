# ADR-0009

## Title

Return tool calls without automatic tool execution

---

## Status

Accepted

---

## Date

2026-07-19

---

## Context

Sprint 5 added tool calling support.

Modern LLM providers can return tool call requests, such as:

```python
ToolCall(
    name="get_weather",
    arguments={"location": "Paris"},
)
```

The toolkit needed to decide whether it should only expose requested tool calls or also automatically execute Python functions.

Automatic tool execution would move the toolkit closer to an agent framework, but it would also introduce safety, authorization, side-effect, and application-control concerns.

Applications may need to approve tool calls, restrict allowed tools, log tool use, validate arguments, or prevent certain actions.

---

## Decision

The toolkit returns requested tool calls to the application, but does not automatically execute tools.

Tool definitions are represented with provider-independent models:

```python
ToolDefinition
ToolCall
ToolResponse
```

Applications call:

```python
response = ai.ask_with_tools(
    prompt="What is the weather in Paris?",
    tools=[weather_tool],
)
```

The application inspects:

```python
response.tool_calls
```

and decides whether and how to execute the requested tool.

Tool execution, approval, authorization, and side effects remain application responsibilities.

---

## Alternatives Considered

### Automatically execute Python functions

Rejected for the first implementation because automatic execution can produce side effects and requires application-specific authorization rules.

Examples include sending emails, modifying databases, calling paid APIs, or exposing private data.

### Build a full agent loop immediately

Rejected because agent loops require multiple additional decisions:

- tool execution policy
- maximum iterations
- tool result submission
- failure handling
- audit logging
- human approval

These belong in a later agent or workflow layer.

### Ignore tool calling until agents exist

Rejected because exposing requested tool calls is useful on its own and provides a foundation for later agent features.

---

## Consequences

### Positive

- Tool calling remains safe and explicit.
- Applications keep control over side effects.
- Provider-specific tool formats are hidden behind toolkit models.
- Agent and workflow features can build on top of the tool-call layer later.
- The implementation is testable without executing external services.

### Negative

- Applications must implement tool execution themselves.
- The toolkit does not yet support complete tool-use loops.
- Users may expect automatic execution and need documentation explaining the current scope.

---

## Related Files

- `ai/tools.py`
- `ai/client.py`
- `ai/executor.py`
- `ai/providers/base.py`
- `ai/providers/openai_provider.py`
- `tests/test_tool_calling.py`
- `examples/07_tool_calling.py`
