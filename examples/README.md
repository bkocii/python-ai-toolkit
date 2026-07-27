# Example Gallery

This gallery is the numbered learning path for the Python AI Toolkit. Each
entry uses the same description fields:

- **File or command** identifies what to open.
- **Demonstrates** states the toolkit behavior shown.
- **Requirements** lists credentials, network access, optional dependencies,
  or provider capabilities needed for a normal run.
- **Run** gives the command or application entry point.
- **Boundary** states what the example deliberately does not provide or prove.

Run module commands from the repository root. Unless an entry says it is
offline, valid [provider configuration](../docs/configuration.md) and network
access are required. Never put a real credential in an example file.

The [verification record](../docs/development/example_verification.md) explains
how provider-dependent examples are tested with deterministic substitutes.

## Catalog Conventions

- Entries 01–20 and 23–28 are Python modules.
- Entries 21–22 are command workflows, so no Python module is missing between
  20 and 23.
- `09_1_structured_image_with_helper.py` is a local-file variant of example 09,
  not a separate learning-path number.
- `hello_ai.py` and `drink_recommender.py` are older supplementary examples.
  They remain unnumbered to preserve existing module paths.

These exceptions are explicit compatibility choices. Renaming them would
change runnable module paths without improving toolkit behavior.

## 01 — Plain Text Request

**File:** [`01_plain_text.py`](01_plain_text.py)

**Demonstrates:** Creating `AIClient`, sending one plain-text request with
`ask()`, and reading text plus model and request-ID metadata from `AIResult`.

**Requirements:** Core installation, valid text-generation provider
configuration, and network access.

**Run:** `python -m examples.01_plain_text`

**Boundary:** Shows one synchronous request; it does not cover streaming,
structured output, or retries.

## 02 — Extract Structured Data

**File:** [`02_extract_structured_data.py`](02_extract_structured_data.py)

**Demonstrates:** Defining a Pydantic response model, passing `response_type`,
and receiving validated structured data through `AIResult`.

**Requirements:** Core installation, valid text-generation provider
configuration, network access, and a selected model that can follow
structured-output instructions.

**Run:** `python -m examples.02_extract_structured_data`

**Boundary:** Validates response shape; it does not verify whether extracted
facts are true.

## 03 — Fluent Request Builder

**File:** [`03_builder_usage.py`](03_builder_usage.py)

**Demonstrates:** Building a structured request through `request()`, chained
builder methods, and `execute()`.

**Requirements:** Core installation, valid text-generation provider
configuration, network access, and a model that can follow structured-output
instructions.

**Run:** `python -m examples.03_builder_usage`

**Boundary:** The builder collects one request; it is not a reusable immutable
request definition.

## 04 — Prompt Template

**File:** [`04_prompt_templates.py`](04_prompt_templates.py)

**Demonstrates:** Defining a reusable `PromptTemplate`, substituting named
variables, and sending the rendered prompt through `AIClient`.

**Requirements:** Core installation, valid text-generation provider
configuration, and network access.

**Run:** `python -m examples.04_prompt_templates`

**Boundary:** Template rendering formats strings; it does not sanitize,
authorize, or validate untrusted prompt content.

Examples 01–04 are supported by the
[plain and structured request guide](../docs/requests.md).

## 05 — Streaming Response

**File:** [`05_streaming_response.py`](05_streaming_response.py)

**Demonstrates:** Requesting synchronous plain-text streaming, consuming chunks,
and printing output as it arrives.

**Requirements:** Core installation, valid provider configuration, network
access, and a provider/model combination that supports streaming.

**Run:** `python -m examples.05_streaming_response`

**Boundary:** `stream()` returns `Iterator[str]`, not `AIResult`, so final
request metadata is not returned by this interface.

## 06 — Async Client

**File:** [`06_async_client.py`](06_async_client.py)

**Demonstrates:** Constructing `AsyncAIClient`, awaiting `ask()`, and starting
the coroutine with `asyncio.run()`.

**Requirements:** Core installation, valid text-generation provider
configuration, network access, and asynchronous provider support.

**Run:** `python -m examples.06_async_client`

**Boundary:** Uses the separate async client for one request; it does not make
the synchronous client asynchronous.

## 07 — Tool Calling

**File:** [`07_tool_calling.py`](07_tool_calling.py)

**Demonstrates:** Defining a provider-independent `ToolDefinition`, sending it
with `ask_with_tools()`, and inspecting requested tool calls.

**Requirements:** Core installation, valid provider configuration, network
access, and a provider/model combination that supports tool calling.

**Run:** `python -m examples.07_tool_calling`

**Boundary:** The toolkit returns `ToolResponse`; the application must
authorize, execute, and return results for requested tools.

## 08 — Image Input

**File:** [`08_image_inputs.py`](08_image_inputs.py)

**Demonstrates:** Combining a prompt with a remote image URL and receiving a
plain-text image description.

**Requirements:** Core installation, valid provider configuration, network
access, an image-capable model, and a provider that can access the example URL.

**Run:** `python -m examples.08_image_inputs`

**Boundary:** A valid image URL does not prove that every provider or model can
retrieve or analyze it.

## 09 — Structured Image Input

**File:** [`09_structured_image_input.py`](09_structured_image_input.py)

**Demonstrates:** Sending a remote image URL, requesting a Pydantic
`ImageDescription`, and reading validated structured image analysis.

**Requirements:** Core installation, valid provider configuration, network
access, and a provider/model combination supporting image input and structured
responses.

**Run:** `python -m examples.09_structured_image_input`

**Boundary:** Structured validation checks response shape, not the factual
accuracy of the image analysis.

### 09 Local Base64 Variant

**File:** [`09_1_structured_image_with_helper.py`](09_1_structured_image_with_helper.py)

**Demonstrates:** Reading the included `sketch.jpg`, converting supported local
image bytes to a Base64 data URL, and requesting the same structured response.

**Requirements:** Core installation, valid provider configuration, network
access, and a provider/model combination supporting Base64 image input and
structured responses.

**Run:** `python -m examples.09_1_structured_image_with_helper`

**Boundary:** The conversion helper is application code. `ImageInput` does not
read local paths, and the helper accepts only JPEG, PNG, and WebP files.

Examples 05–09 are supported by the
[advanced request guide](../docs/advanced_requests.md).

## 10 — Embeddings

**File:** [`10_embeddings.py`](10_embeddings.py)

**Demonstrates:** Embedding one text, embedding a batch, preserving metadata,
and inspecting the returned model and vector dimensions.

**Requirements:** Core installation, valid provider configuration, network
access, and an embedding-capable provider/model.

**Run:** `python -m examples.10_embeddings`

**Boundary:** Produces vectors only; it does not store, search, or evaluate
them.

## 11 — In-Memory Vector Store

**File:** [`11_vector_store.py`](11_vector_store.py)

**Demonstrates:** Embedding a small knowledge set, creating `VectorRecord`
objects, storing them in `InMemoryVectorStore`, and running cosine-similarity
search.

**Requirements:** Core installation, valid embedding-provider configuration,
network access, and an embedding-capable model.

**Run:** `python -m examples.11_vector_store`

**Boundary:** The store is process-local and non-persistent; similarity scores
are ranking signals, not confidence probabilities.

## 12 — Retriever

**File:** [`12_retriever.py`](12_retriever.py)

**Demonstrates:** Building an in-memory knowledge index, embedding a query
through `VectorStoreRetriever`, retrieving relevant contexts, and formatting
them for a prompt.

**Requirements:** Core installation, valid embedding-provider configuration,
network access, and an embedding-capable model.

**Run:** `python -m examples.12_retriever`

**Boundary:** Retrieval returns context; it does not generate an answer or
guarantee relevance.

## 13 — RAG Pipeline

**File:** [`13_rag_pipeline.py`](13_rag_pipeline.py)

**Demonstrates:** Composing embeddings, in-memory vector search, retrieval, and
`RAGPipeline` to generate an answer with returned source contexts.

**Requirements:** Core installation, valid provider configuration, network
access, and models supporting both embeddings and text generation.

**Run:** `python -m examples.13_rag_pipeline`

**Boundary:** Returned contexts provide traceability but are not verified
citations, and the in-memory index is not persistent.

## 14 — Directory Loader RAG

**File:** [`14_document_loader_rag.py`](14_document_loader_rag.py)

**Demonstrates:** Loading `.txt` and `.md` files, converting documents to
embedding inputs, storing their vectors, retrieving context, and generating an
answer through `RAGPipeline`.

**Requirements:** Run from the repository root with the included
`examples/sample_docs` directory, valid provider configuration, network access,
and models supporting embeddings and text generation.

**Run:** `python -m examples.14_document_loader_rag`

**Boundary:** Each file remains one document. The example does not add
chunking, stable production IDs, persistent storage, or citation verification.

Examples 10–14 are supported by the
[retrieval and RAG guide](../docs/retrieval.md).

## 15 — Conversation Memory

**File:** [`15_conversation_memory.py`](15_conversation_memory.py)

**Demonstrates:** Adding system, user, and assistant messages to
`InMemoryConversationMemory`, reading all or recent messages, and formatting
them for prompts.

**Requirements:** Core installation only; no credential or network access.

**Run:** `python -m examples.15_conversation_memory`

**Boundary:** Memory is process-local, non-persistent, and not automatically
trimmed by token count.

## 16 — Agent

**File:** [`16_agent.py`](16_agent.py)

**Demonstrates:** Combining `AIClient`, instructions, and conversation memory
inside an `Agent`, then running two sequential turns.

**Requirements:** Core installation, valid text-generation provider
configuration, and network access.

**Run:** `python -m examples.16_agent`

**Boundary:** The agent wraps explicit request and memory behavior; it does not
autonomously use tools, plan loops, or persist memory.

## 17 — Workflow Engine

**File:** [`17_workflow_engine.py`](17_workflow_engine.py)

**Demonstrates:** Defining function-backed retrieve and answer steps, passing
shared `WorkflowContext` state, and running a sequential workflow.

**Requirements:** Core installation, valid provider configuration, network
access, and models supporting embeddings and text generation.

**Run:** `python -m examples.17_workflow_engine`

**Boundary:** Execution is synchronous, sequential, fail-fast, and
non-persistent.

## 18 — Multi-Agent Orchestration

**File:** [`18_multi_agent_orchestration.py`](18_multi_agent_orchestration.py)

**Demonstrates:** Registering specialized agents, running them in an explicit
sequence, and passing each output to the next agent.

**Requirements:** Core installation, valid text-generation provider
configuration, and network access.

**Run:** `python -m examples.18_multi_agent_orchestration`

**Boundary:** Orchestration is explicit and sequential; it does not provide
automatic routing, parallel execution, debate, or autonomous planning.

Examples 15–18 are supported by the
[memory, agent, workflow, and orchestration guide](../docs/orchestration.md).

## 19 — Django Integration

**File:** [`19_django_integration.py`](19_django_integration.py)

**Demonstrates:** Resolving `AIConfig` from Django's `AI_TOOLKIT` setting,
creating a synchronous client with `get_ai_client()`, and returning a validated
support-ticket model from an application service function.

**Requirements:** Install `.[django]`; use an existing configured Django
application with valid text-generation provider settings and network access.

**Run:** Import and call `analyze_support_ticket()` from a Django view, Celery
task, management command, shell, or service.

**Boundary:** This is an integration module, not a standalone Django project;
the application owns views, persistence, authorization, tasks, and business
logic.

## 20 — FastAPI Integration

**File:** [`20_fastapi_integration.py`](20_fastapi_integration.py)

**Demonstrates:** Injecting `AsyncAIClient` with
`AsyncAIClientDependency`, validating request and response models, and
overriding the dependency in application tests.

**Requirements:** Install `.[fastapi]` and a separate ASGI server such as
Uvicorn; provide valid text-generation provider configuration and network
access.

**Run:** `uvicorn examples.20_fastapi_integration:app --reload`

**Boundary:** The FastAPI extra does not choose or install an ASGI server and
does not own application routes, client-lifetime policy, authorization, or
business logic.

## 21 — Command-Line Request

**Command:** `ai-toolkit ask`

**Demonstrates:** Sending a plain-text prompt with the installed console
command, printing the response, and returning predictable exit codes.

**Requirements:** Installed package, valid text-generation provider
configuration, and network access.

**Run:** `ai-toolkit ask "Explain dependency injection simply."`

**Boundary:** The command supports plain text only; it does not expose
structured responses, streaming, tools, images, embeddings, or interactive
chat.

## 22 — Configuration CLI

**Commands:** `ai-toolkit config show` and `ai-toolkit config validate`

**Demonstrates:** Inspecting resolved configuration with masked keys and
validating configuration structure from the terminal.

**Requirements:** Installed package. Provider credentials and network access
are not required for read-only inspection itself.

**Run:** `ai-toolkit config show`, then `ai-toolkit config validate`

**Boundary:** These commands do not modify `.env`, save secrets, contact a
provider, or prove that credentials and selected model capabilities work.

Examples 19–22 are supported by the
[Django, FastAPI, and CLI integration guide](../docs/integrations.md).

## 23 — Explicit Configuration

**File:** [`23_explicit_config.py`](23_explicit_config.py)

**Demonstrates:** Constructing a complete `AIConfig` from an
application-supplied secret, validating it explicitly, and injecting it into
`AIClient` without merging toolkit environment settings.

**Requirements:** Core installation, `EXAMPLE_AI_API_KEY` containing a
restricted development credential, network access, and access to the model
selected in the example.

**Run:**

```bash
export EXAMPLE_AI_API_KEY="replace_with_a_development_key"
python -m examples.23_explicit_config
```

```powershell
$env:EXAMPLE_AI_API_KEY = "replace_with_a_development_key"
python -m examples.23_explicit_config
```

**Boundary:** Manual `AIConfig` construction does not validate itself. The
application owns secret lookup and must call `ConfigValidator.validate()`
before client construction.

See the [explicit configuration guide](../docs/configuration.md#explicit-aiconfig).

## 24 — Custom Provider Registration

**File:** [`24_custom_provider.py`](24_custom_provider.py)

**Demonstrates:** Implementing the minimum `BaseAIProvider` contract,
registering it before client construction, selecting it through validated
explicit configuration, and using it through the normal client lifecycle.

**Requirements:** Core installation only; no credential or network access.

**Run:** `python -m examples.24_custom_provider`

**Boundary:** Registration is process-local. The example implements synchronous
plain text only, so registration does not prove streaming, tools, images,
embeddings, live connectivity, or model support.

See the [custom provider guide](../docs/providers.md).

## 25 — Testing with a Fake Provider

**File:** [`25_testing_with_fake_provider.py`](25_testing_with_fake_provider.py)

**Demonstrates:** Keeping application code dependent on `AIClient`, substituting
a deterministic provider during test-client construction, capturing the
prompt, and exercising real structured parsing.

**Requirements:** Core installation only; no real credential, live model, or
network access.

**Run:** `python -m examples.25_testing_with_fake_provider`

**Boundary:** The factory patch is test-only and scoped to client construction.
It does not register a provider or create a general mocking framework.

See the
[fake-provider testing guide](../docs/providers.md#testing-application-code-with-a-fake-provider).

## 26 — Batch Embedding and Retrieval

**File:** [`26_batch_embedding_and_retrieval.py`](26_batch_embedding_and_retrieval.py)

**Demonstrates:** Sending several metadata-bearing texts in one embedding
request, restoring input order from `EmbeddingVector.index`, preserving stable
application IDs, storing vectors, and retrieving filtered contexts.

**Requirements:** Core installation, valid embedding-provider configuration,
network access, and an embedding-capable model.

**Run:** `python -m examples.26_batch_embedding_and_retrieval`

**Boundary:** Indexes an in-code batch and returns contexts only; it does not
load files, generate an answer, or provide persistent storage.

## 27 — End-to-End Document Indexing and RAG

**File:** [`27_document_indexing_and_rag.py`](27_document_indexing_and_rag.py)

**Demonstrates:** Loading sample files with a module-relative path, assigning
stable application IDs, batch embedding with index restoration, storing and
retrieving documents, and generating one grounded answer with returned source
contexts.

**Requirements:** Core installation, the included sample documents, valid
provider configuration, network access, and models supporting embeddings and
text generation.

**Run:** `python -m examples.27_document_indexing_and_rag`

**Boundary:** Each file remains one document. Chunking, persistent storage,
access policy, production ID design, and citation verification remain
application responsibilities.

Examples 26–27 are supported by the
[retrieval and RAG guide](../docs/retrieval.md).

## 28 — Structured Application Service

**File:** [`28_structured_application_service.py`](28_structured_application_service.py)

**Demonstrates:** Injecting `AIClient` into a framework-independent service,
validating input locally, requesting a constrained Pydantic result, applying
application routing rules, translating expected toolkit failures, and
preserving the request ID.

**Requirements:** Core installation, valid text-generation provider
configuration, network access, and a model that can follow structured-output
instructions.

**Run:** `python -m examples.28_structured_application_service`

**Boundary:** The service does not authorize or perform refunds, write to a
database, or contact another system; those side effects remain application
responsibilities.

See the
[application-service request guide](../docs/requests.md#put-structured-requests-behind-an-application-service).

## Supplementary Examples

### Minimal `ask_text()` Check

**File:** [`hello_ai.py`](hello_ai.py)

**Demonstrates:** Calling the convenience `ask_text()` method and printing its
string result.

**Requirements:** Core installation, valid text-generation provider
configuration, and network access.

**Run:** `python -m examples.hello_ai`

**Boundary:** Returns plain `str`, not `AIResult`, so it omits request metadata.
Start with example 01 when learning the standard result contract.

### Structured Drink Recommendation

**File:** [`drink_recommender.py`](drink_recommender.py)

**Demonstrates:** Supplying a small application-owned product list in a prompt,
requesting one constrained Pydantic recommendation, and printing token usage.

**Requirements:** Core installation, valid text-generation provider
configuration, network access, and a model that can follow structured-output
instructions.

**Run:** `python -m examples.drink_recommender`

**Boundary:** The model recommends only from prompt data; application code must
still enforce price, availability, alcohol, age, safety, and business rules.

## Verification

Every Python module in this catalog has deterministic regression coverage
through its real public entry point. Django and FastAPI examples run through
their integration boundaries, CLI workflows run through the console
dispatcher, and provider-dependent behavior uses controlled substitutes
without credentials or network requests.

The verification also checks that every `ai.*` import used by an example is
listed in the [public API reference](../docs/api_reference.md) and remains
importable. These checks prove toolkit control flow and return contracts; they
do not prove live credentials, account access, regional availability, provider
network behavior, cost, or model capabilities.

## Learning Path

| Stage | Examples | Focus |
| --- | --- | --- |
| 1 | 01–04 | Plain requests, structured output, builder, and prompts |
| 2 | 05–09 | Streaming, async, tools, and images |
| 3 | 10–14 | Embeddings, vector search, retrieval, and RAG |
| 4 | 15–18 | Memory, agents, workflows, and orchestration |
| 5 | 19–22 | Django, FastAPI, requests from the CLI, and configuration inspection |
| 6 | 23–25 | Explicit configuration, provider extension, and application testing |
| 7 | 26–28 | Batch retrieval, document RAG, and an application service |
