# Memory, Agents, Workflows, and Orchestration

Python AI Toolkit keeps conversation memory, agents, workflows, and
multi-agent orchestration as separate, composable layers:

```text
ConversationMessage
    ↓
BaseConversationMemory
    ↓
Agent
    ↓
WorkflowEngine or MultiAgentOrchestrator
```

Each layer has a distinct responsibility. Memory stores messages, an agent
handles one conversational turn, a workflow runs application-defined steps,
and the orchestrator runs named agents in an application-selected order.

These APIs are currently synchronous and in-process. They do not provide
durable execution, automatic routing, parallelism, rollback, or autonomous
loops.

## Capability and return-value map

| Layer | Main public API | Return value |
| --- | --- | --- |
| Conversation memory | `BaseConversationMemory` | Stored `ConversationMessage` objects |
| One agent turn | `BaseAgent.run()` | `AgentResponse` |
| Sequential workflow | `WorkflowEngine.run()` | `WorkflowRunResult` |
| One named agent | `MultiAgentOrchestrator.run_agent()` | `AgentRunResult` |
| Named agent sequence | `MultiAgentOrchestrator.run_sequence()` | `MultiAgentResponse` |

These result types are not `AIResult`. `AgentResponse` preserves only selected
metadata from the underlying plain request, while workflow and orchestration
results describe application-level execution.

## Conversation messages

`ConversationMessage` is the provider-independent message model:

```python
from ai.memory import ConversationMessage, MessageRole

message = ConversationMessage(
    role=MessageRole.USER,
    content="What is Redis?",
    metadata={
        "user_id": "customer-42",
        "source": "support-chat",
    },
)
```

The fields are:

| Field | Meaning |
| --- | --- |
| `role` | `system`, `user`, `assistant`, or `tool` |
| `content` | Message text |
| `metadata` | Application-owned `dict[str, str]` |
| `created_at` | Unix timestamp assigned when the model is created |

`metadata` can hold identifiers and trace information, but the toolkit does not
interpret, authorize, encrypt, or persist those values. Do not place secrets or
unnecessary sensitive data in prompt-bound message metadata.

The `created_at` field is useful for ordering and debugging. It is not a
database ID, monotonic sequence number, or cross-system clock guarantee.

## In-memory conversation memory

`InMemoryConversationMemory` provides convenience methods for each role:

```python
from ai.memory import InMemoryConversationMemory

memory = InMemoryConversationMemory()

memory.add_system_message("Answer concisely.")
memory.add_user_message(
    "What is Redis?",
    metadata={"conversation_id": "conversation-123"},
)
memory.add_assistant_message(
    "Redis is an in-memory data store.",
    metadata={"request_id": "request-123"},
)
memory.add_tool_message(
    '{"status": "available"}',
    metadata={"tool_name": "service_status"},
)

all_messages = memory.messages()
recent_messages = memory.recent_messages(limit=2)
```

The base memory contract contains:

| Method | Contract |
| --- | --- |
| `add_message(message)` | Append one `ConversationMessage` |
| `messages()` | Return all messages in insertion order |
| `recent_messages(limit)` | Return at most the last `limit` messages |
| `clear()` | Remove all stored messages |

`InMemoryConversationMemory.messages()` returns a new list, so changing that
list does not add or remove stored entries. The returned message objects are
ordinary Pydantic models; applications should treat stored messages as
conversation records rather than mutating them in place.

`recent_messages()` counts individual messages, not user/assistant turns or
tokens:

- `limit <= 0` returns an empty list
- a limit larger than the history returns the complete history
- no token-budget calculation or summarization is performed

To replace volatile storage, implement `BaseConversationMemory`. A custom
implementation remains responsible for persistence, tenant isolation,
concurrency, retention, encryption, and failure handling.

### Format messages for a prompt

`format_conversation_messages()` creates the plain-text format used by
`Agent`:

```python
from ai.memory import format_conversation_messages

formatted = format_conversation_messages(memory.recent_messages(limit=2))
print(formatted)
```

Each role is rendered in uppercase. Non-empty metadata is rendered with its
Python dictionary representation. An empty message list becomes:

```text
No previous conversation.
```

Formatting does not escape instructions, redact metadata, enforce a token
limit, or preserve provider-native message roles. The result is ordinary text
inserted into a larger prompt. Applications should validate and minimize
untrusted metadata or content before using it in sensitive prompt workflows.

### In-memory boundary

`InMemoryConversationMemory` is intended for tests, examples, demos, and
short-lived local processes. It has no:

- persistence across process restarts
- shared state across workers
- database transactions
- tenant or user access control
- automatic expiration
- token-aware trimming or summarization
- built-in thread or process coordination

For a web application, create separate memory per conversation or user and use
a persistent `BaseConversationMemory` implementation when durability or
cross-worker access is required.

## Run a memory-backed agent

`Agent` combines an `AIClient`, instructions, memory, and a recent-message
limit:

```python
from ai.agent import Agent
from ai.client import AIClient
from ai.memory import InMemoryConversationMemory

agent = Agent(
    ai_client=AIClient(),
    instructions="You are a concise technical assistant.",
    memory=InMemoryConversationMemory(),
    memory_limit=10,
)

response = agent.run(
    "How can Redis help a Django application?",
    metadata={"conversation_id": "conversation-123"},
)

print(response.output)
print(response.request_id)
```

Instructions must be non-blank, `memory_limit` must be greater than zero, and
each input message must be non-blank.

One `Agent.run()` performs this lifecycle:

1. append the user message and its metadata to memory
2. select the most recent `memory_limit` messages
3. format those messages as plain text
4. build a prompt containing instructions, recent conversation, and the
   current user message
5. call `AIClient.ask()` without a structured response type
6. append the assistant text to memory with its request ID and model
7. return `AgentResponse`

The current user message is appended before the recent-memory slice is built.
It is excluded from the formatted conversation and appears once in the prompt's
separate `Current user message` section.

Because `memory_limit` counts messages and includes the newly appended user
message, a small limit can exclude an older system or assistant message. Agent
instructions remain in their separate prompt section and are not taken from
memory.

### Agent response metadata

`AgentResponse` contains:

| Field | Meaning |
| --- | --- |
| `output` | Final plain assistant text |
| `model` | Model from the underlying `AIResult` |
| `request_id` | Request ID from the underlying `AIResult` |
| `messages` | Complete memory snapshot after the successful turn |

The assistant message stored in memory also receives `request_id` and `model`
metadata.

`AgentResponse` does not expose the underlying request's duration, token usage,
estimated cost, retry count, or raw responses. Applications that require the
complete `AIResult` contract should use `AIClient` directly or introduce an
application-level agent abstraction with the required metadata.

### Agent failure and autonomy boundaries

If the underlying request raises an exception, `Agent.run()` does not return an
`AgentResponse`. The user message was already appended and remains in memory;
no assistant message is added and no automatic rollback occurs.

`Agent` does not:

- stream or run asynchronously
- request structured output
- execute tools
- retrieve RAG context automatically
- route to another agent
- run a workflow
- persist memory

Applications compose those behaviors explicitly and remain responsible for
permissions, tool execution, routing, retries outside the request lifecycle,
and recovery after partial work.

## Build a sequential workflow

A workflow step receives one shared `WorkflowContext` and returns a
`WorkflowStepResult`:

```python
from ai.workflow import (
    FunctionWorkflowStep,
    WorkflowContext,
    WorkflowEngine,
    WorkflowStepResult,
)


def normalize(context: WorkflowContext) -> WorkflowStepResult:
    normalized = context.input["text"].strip().lower()

    return WorkflowStepResult(
        step_name="normalize",
        output=normalized,
        state_updates={"normalized": normalized},
    )


def summarize(context: WorkflowContext) -> WorkflowStepResult:
    normalized = context.state["normalized"]

    return WorkflowStepResult(
        step_name="summarize",
        output=f"Processed: {normalized}",
        state_updates={"completed": True},
    )


workflow = WorkflowEngine(
    steps=[
        FunctionWorkflowStep("normalize", normalize),
        FunctionWorkflowStep("summarize", summarize),
    ]
)

result = workflow.run(
    input_data={"text": "  Redis Cache  "},
    metadata={"workflow_id": "workflow-123"},
)

print(result.success)
print(result.final_output)
print(result.context.state)
```

`WorkflowEngine` requires at least one step and executes steps synchronously in
the supplied order.

### Workflow context

`WorkflowContext` separates three kinds of data:

| Field | Purpose |
| --- | --- |
| `input` | Initial application input |
| `state` | Shared mutable state accumulated during the run |
| `metadata` | Application-owned string metadata |

The engine initializes `state` as an empty dictionary. A step may read input,
state, and metadata. After a step returns, the engine applies
`state_updates` with a shallow `dict.update()`, so a later value replaces an
earlier value with the same key.

Steps receive the same context object and can mutate it directly, but returning
explicit `state_updates` makes state transitions easier to inspect and test.
The engine does not copy, serialize, validate, or transactionally protect
arbitrary values stored in `input`, `state`, or step output.

### Step and run results

`WorkflowStepResult` contains:

| Field | Meaning |
| --- | --- |
| `step_name` | Registered step name |
| `output` | Arbitrary step output |
| `state_updates` | Values merged into shared state |
| `metadata` | Step-specific application metadata |
| `success` | Whether execution may continue |
| `error` | Optional error text |

If a function returns a different `step_name`, `FunctionWorkflowStep` rewrites
it to the registered name. The function must return a
`WorkflowStepResult`; other return types do not satisfy the public contract.

`WorkflowRunResult` contains the final success flag, shared context, and
ordered results for every executed step. `final_output` is the last executed
step's output, or `None` if the result has no steps.

### Workflow failure behavior

When a step returns `success=False`, the engine:

1. records the failed step
2. applies that step's `state_updates`
3. stops before later steps
4. returns `WorkflowRunResult(success=False, ...)`

When a step raises an `Exception`, the engine converts it into a failed result
whose `error` is `str(exc)`, then stops. This convenience keeps an execution
history, but it also means the returned error string is not a typed exception
contract.

The workflow engine does not roll back:

- prior state updates
- direct context mutations
- memory changes
- files, database writes, network calls, or other external side effects

Design steps to be idempotent where practical, validate before destructive
work, and add application-owned compensation or transaction boundaries when
partial execution matters. Step retries, branching, parallelism, async
execution, cancellation, timeouts, and durable resumption are not currently
implemented.

## Orchestrate named agents

`MultiAgentOrchestrator` registers agents under exact, application-owned names:

```python
from ai.agent import Agent
from ai.client import AIClient
from ai.memory import InMemoryConversationMemory
from ai.orchestrator import MultiAgentOrchestrator

client = AIClient()

technical = Agent(
    ai_client=client,
    instructions="Explain the topic accurately.",
    memory=InMemoryConversationMemory(),
)

reviewer = Agent(
    ai_client=client,
    instructions="Improve the supplied answer. Return only the improved answer.",
    memory=InMemoryConversationMemory(),
)

orchestrator = MultiAgentOrchestrator(
    agents={
        "technical": technical,
        "reviewer": reviewer,
    }
)

response = orchestrator.run_sequence(
    agent_names=["technical", "reviewer"],
    message="Explain Redis caching for Django.",
    metadata={"workflow_id": "review-123"},
)

print(response.success)
print(response.final_output)
```

Registration rejects blank or duplicate names. `agent_names()` returns the
registered names in sorted order; it is an inventory method, not execution
order.

Run one selected agent with:

```python
result = orchestrator.run_agent(
    agent_name="technical",
    message="Explain Redis caching.",
)
```

An unknown name raises `ValueError`. If a known agent raises during execution,
`run_agent()` returns a failed `AgentRunResult` instead of re-raising that
agent exception.

### Sequential handoff

`run_sequence()` requires a non-empty name list and non-blank initial message.
It:

1. passes the initial message to the first named agent
2. passes each successful agent's output as the next agent's complete input
3. passes the same metadata values to every agent
4. records results in execution order
5. stops after the first failed agent result

The orchestrator does not merge prompts, conversation histories, or structured
state between agents. Each agent keeps its own configured memory. The only
automatic handoff is the previous successful output string.

The orchestrator validates every requested name before execution. An unknown
name therefore raises `ValueError` without running any earlier agent in the
sequence.

### Orchestration results

`AgentRunResult` contains:

| Field | Meaning |
| --- | --- |
| `agent_name` | Registered name used for the run |
| `response` | `AgentResponse` on success, otherwise `None` |
| `success` | Whether that agent completed |
| `error` | Captured agent error text on failure |

`MultiAgentResponse.results` preserves execution order.
`MultiAgentResponse.success` is true only when at least one result exists and
every recorded result succeeds. An empty response is unsuccessful.
`final_output` returns the last successful agent output, including when a later
agent failed; it returns `None` when no agent succeeded.

Inspect `success` and individual results before treating `final_output` as a
fully completed pipeline result.

## Application-owned control

The orchestration stack deliberately leaves control with application code:

| Decision | Owner |
| --- | --- |
| Which memory belongs to a user or conversation | Application |
| Which agents exist and may run | Application |
| Agent order and stopping policy | Application |
| Tool allow-listing, validation, authorization, and execution | Application |
| Retrieval and context policy | Application |
| Workflow input and state schema | Application |
| External transactions, compensation, and idempotency | Application |
| Timeouts, quotas, cancellation, and cost limits | Application |

The current toolkit does not perform AI-based routing, recursive loops,
agent-to-agent debate, parallel agent execution, shared global memory, or
automatic tool execution. These limits are intentional parts of the explicit,
testable first architecture.

## Version 1.0 boundary and future work

Version 1.0 approves the message-count memory limit, current `AgentResponse`
metadata, shallow workflow state updates, failed-step stop behavior,
unknown-agent `ValueError`, and known-agent partial-execution result contracts
documented above. Exact prompt wording remains an implementation detail, but
the current user message must not be duplicated.

Future Backlog candidates include persistent and token-aware memory,
configurable agent prompts, streaming and async agents, RAG- and tool-aware
agents, branching and durable workflows, and more advanced multi-agent
patterns.

Future orchestration helpers must preserve application control over external
actions, authorization, resource limits, and stopping conditions.

See the [approved public API](api_reference.md#version-10-freeze-decisions) and
[Future Backlog](development/roadmap.md#future-backlog).

## Related documentation

- [Public API reference](api_reference.md) lists exact memory, agent, workflow,
  orchestrator, result-model, and extension-interface contracts.
- [Plain and structured requests](requests.md)
- [Advanced requests](advanced_requests.md)
- [Embeddings, retrieval, and RAG](retrieval.md)
- [Security and secret handling](security.md)
- [Examples 15 through 18](../examples/README.md#15--conversation-memory)
- [Architecture](architecture/architecture.md#agents-and-workflows-architecture)
- [Roadmap](development/roadmap.md)
