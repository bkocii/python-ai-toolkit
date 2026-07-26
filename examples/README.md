# Example Gallery

This directory contains small, self-contained examples demonstrating how to use the Python AI Toolkit.

The [documented example verification record](../docs/development/example_verification.md)
explains which workflows run offline, which use deterministic provider
substitutes, and which still require a real provider or platform-specific
environment.

## 01 – Plain Text Request

- file: `01_plain_text.py`
- creating an AIClient
- simple AI request
- AIResult metadata

## 02 – Extract Structured Data

- file: `02_extract_structured_data.py`
- Pydantic models
- response_type
- validated output

The [request guide](../docs/requests.md) explains the difference between
`ask()` and `ask_text()`, all `AIResult` fields, and the structured-response
repair lifecycle used by these examples.

## 03 – Builder Usage
- fluent builder
- method chaining
- execute()

## 04 – Prompt Templates
- reusable prompts
- variable substitution

---

## 05 – Streaming Response

Demonstrates:

- streaming plain text responses
- consuming response chunks
- printing streamed output immediately

Examples 05 through 09 are supported by the
[advanced request guide](../docs/advanced_requests.md), which documents their
different return values, metadata boundaries, provider requirements, and
current sync/async limits.

---

## 06 – Async Client

Demonstrates:

- using AsyncAIClient
- awaiting async AI requests
- running async examples with asyncio.run()

---

## 07 – Tool Calling

**File**

```text
07_tool_calling.py
```

Demonstrates:

- defining provider-independent tools
- passing tools to AIClient
- receiving requested tool calls
- keeping tool execution inside the application

---

## 08 – Image Inputs

**File**

```text
08_image_inputs.py
```
Demonstrates:

- sending an image URL to the model
- combining text and image input
- receiving a plain text response

## 09 – Structured Image Input

**File**
```text
09_structured_image_input.py
```
Demonstrates:

- sending image input
- using response_type
- validating structured image analysis with Pydantic

The local-file variant is:

```text
09_1_structured_image_with_helper.py
```

It demonstrates converting a local JPEG, PNG, or WebP file into a Base64 data
URL before constructing `ImageInput`, then validating a structured
`ImageDescription`. Local-path reading is example application code, not a
built-in `ImageInput` feature.

---

## 10 – Embeddings

**File**

```text
10_embeddings.py
```
Demonstrates:

- embedding one text
- embedding multiple texts
- preserving metadata
- reading vector length
- using embeddings as preparation for RAG

Examples 10 through 14 are supported by the
[retrieval and RAG guide](../docs/retrieval.md), which documents embedding
ordering and metadata, vector-score semantics, the in-memory storage boundary,
document preparation, RAG response metadata, and grounding limits.

---

## 11 – Vector Store

**File**

```text
11_vector_store.py
```
Demonstrates:

- embedding multiple texts
- converting embeddings into vector records
- storing records in InMemoryVectorStore
- embedding a search query
- running similarity search
- reading search scores and metadata

---

## 12 – Retriever

**File**

```text
12_retriever.py
```
Demonstrates:

- embedding knowledge text
- storing vectors in InMemoryVectorStore
- creating VectorStoreRetriever
- retrieving relevant context for a query
- formatting retrieved context for prompts

---

## 13 – RAG Pipeline

**File**

```text
13_rag_pipeline.py
```
Demonstrates:

- embedding knowledge text
- storing embeddings in InMemoryVectorStore
- retrieving relevant context
- generating an answer with RAGPipeline
- returning both answer and sources

---

## 14 – Document Loader RAG

**File**

```text
14_document_loader_rag.py
```
Demonstrates:

- loading .txt and .md files from a directory
- converting documents to embedding inputs
- embedding loaded documents
- storing document vectors
- retrieving relevant context
- answering with RAGPipeline

---

## 15 – Conversation Memory

**File**

```text
15_conversation_memory.py
```
Demonstrates:

- creating in-memory conversation memory
- adding system, user, and assistant messages
- retrieving all messages
- retrieving recent messages
- formatting memory for prompts

---

## 16 – Agent

**File**

```text
16_agent.py
```
Demonstrates:

- creating an Agent
- using system instructions
- using conversation memory
- running multiple turns
- reading the updated conversation messages

---

## 17 – Workflow Engine

**File**

```text
17_workflow_engine.py
```
Demonstrates:

- creating workflow steps
- passing shared workflow state
- composing retrieve and answer steps
- running a sequential workflow
- inspecting final output and workflow state


---

## 18 – Multi-Agent Orchestration

**File**

```text
18_multi_agent_orchestration.py
```
Demonstrates:

- creating multiple specialized agents
- registering agents in MultiAgentOrchestrator
- running agents sequentially
- passing one agent's output to the next agent
- inspecting multi-agent results

Examples 15 through 18 are supported by the
[memory, agents, workflows, and orchestration guide](../docs/orchestration.md),
which documents message and prompt behavior, memory persistence limits,
workflow state and failure semantics, sequential agent handoffs, result
contracts, and application-owned control.


## 19 – Django Integration

**File**

```text
19_django_integration.py
```

Demonstrates:

* configuring the toolkit through Django's `AI_TOOLKIT` setting
* creating an `AIClient` with `get_ai_client()`
* using the toolkit inside an existing Django application
* analyzing a support ticket
* returning a validated Pydantic model
* keeping views, models, Celery tasks, and business logic outside the toolkit

Install the optional Django integration:

```bash
python -m pip install ".[django]"
```

---

## 20 – FastAPI Integration

**File**

```text
20_fastapi_integration.py
```

Demonstrates:

* injecting `AsyncAIClient` into a FastAPI endpoint
* using `AsyncAIClientDependency`
* accepting a validated API request model
* returning a validated structured response
* using asynchronous AI requests inside an endpoint
* replacing the AI dependency during tests
* keeping routes, schemas, prompts, and business logic inside the application

Install the optional FastAPI integration:

```bash
python -m pip install ".[fastapi]"
```

The example's local `uvicorn` run command requires a separately installed ASGI
server:

```bash
python -m pip install uvicorn
```

---

## 21 – Command-Line Interface

**Command**

```text
ai-toolkit ask "<prompt>"
```

Demonstrates:

* sending a plain-text prompt from the terminal
* using the same environment configuration as `AIClient`
* printing the AI response directly to standard output
* returning predictable command exit codes
* showing clean configuration and provider errors
* using the toolkit without writing a Python script

Example:

```bash
ai-toolkit ask "Explain dependency injection simply."
```

The initial CLI supports plain-text requests only. Read-only configuration
inspection and structural validation are handled by the commands below.


## 22 – Configuration CLI

**Commands**

```text
ai-toolkit config show
ai-toolkit config validate
```

Demonstrates:

* inspecting the resolved toolkit configuration
* masking API keys in terminal output
* showing provider, model, embedding, retry, and cost settings
* validating configuration structure
* reporting configuration errors with predictable exit codes
* distinguishing structural validation from live credential verification

The commands do not modify `.env`, save secrets, or contact the configured provider.



Examples 19 through 22 are supported by the
[Django, FastAPI, and CLI integration guide](../docs/integrations.md), which
documents configuration sources, synchronous and asynchronous helpers,
dependency overrides, client lifetimes, CLI output, exit codes, and live
provider boundaries.

## Running
```bash
python -m examples.01_plain_text
```

## Learning Path
1. Plain Text Request
2. Extract Structured Data
3. Builder Usage
4. Prompt Templates
5. Streaming Response
6. Async Client
7. Tool Calling
8. Image Inputs
9. Structured Image Input
10. Embeddings
11. Vector Store
12. Retriever
13. RAG Pipeline
14. Document Loader RAG
15. Conversation Memory
16. Agent
17. Workflow Engine
18. Multi-Agent Orchestration
19. Django Integration
20. FastAPI Integration
21. Command-Line Interface
22. Configuration CLI
