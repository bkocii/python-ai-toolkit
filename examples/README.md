# Example Gallery

This directory contains small, self-contained examples demonstrating how to use the Python AI Toolkit.

## 01 – Summarize Text
- creating an AIClient
- simple AI request
- AIResult metadata

## 02 – Extract Structured Data
- Pydantic models
- response_type
- validated output

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

**FIle**
```text
09_structured_image_input.py
```
Demonstrates:

- sending image input
- using response_type
- validating structured image analysis with Pydantic

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


## 19. Django Integration

File:

```text
examples/19_django_integration.py
```

This example shows how an existing Django application can create a configured
AIClient from the Django AI_TOOLKIT setting.

The example analyzes a support ticket and returns a validated Pydantic model.

Install Django integration support:
```python
pip install python-ai-toolkit[django]
```
Configure the Django project:
```python
AI_TOOLKIT = {
    "provider": "openai",
    "api_key": os.environ["OPENAI_API_KEY"],
    "model": "gpt-5.4-mini",
    "embedding_model": "text-embedding-3-small",
    "max_retries": 1,
}
```
Use the integration inside a Django service:
```python
from ai.integrations.django import get_ai_client

client = get_ai_client()
result = client.ask("Summarize this support ticket.")
```
The Django integration only creates the configured client. Views, models,
Celery tasks, prompts, and application decisions remain the responsibility
of the Django project.

## 20. FastAPI Integration

File:

```text
examples/20_fastapi_integration.py
```
This example shows how an existing FastAPI application can inject an
AsyncAIClient into an asynchronous API endpoint.

The endpoint accepts a customer support ticket and returns a validated
TicketAnalysis model.

Install FastAPI integration support:
```python
pip install python-ai-toolkit[fastapi]
```
Use the dependency alias:
```python
from ai.integrations.fastapi import AsyncAIClientDependency

@app.post("/analyze-ticket")
async def analyze_ticket(
    request: TicketRequest,
    client: AsyncAIClientDependency,
):
    result = await client.ask(
        prompt=f"Analyze this ticket:\n\n{request.message}",
        response_type=TicketAnalysis,
    )

    return result.data
```

FastAPI handles dependency injection. The toolkit handles client creation,
provider communication, structured parsing, and validation.

Application routes, prompts, schemas, and business decisions remain inside
the FastAPI application.


FastAPI also supports replacing dependencies through `app.dependency_overrides`, which is why the integration can be tested without making real provider calls. :contentReference[oaicite:1]{index=1}


## Running
```bash
python -m examples.01_summarize_text
```

## Learning Path
1. Summarize Text
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