# Python AI Toolkit

A reusable AI engineering toolkit for Python developers.

The goal of this project is to provide clean, reusable building blocks for integrating Large Language Models (LLMs) into Python applications.

Instead of scattering AI code across projects, this toolkit centralizes configuration, provider integrations, validation, logging, and future AI capabilities behind a consistent interface.

---

## Philosophy

The LLM is only one part of an AI application.

Business logic should remain in Python.

```text
Application
        │
        ▼
 AI Toolkit
        │
        ▼
 AI Provider
        │
        ▼
 Language Model
```

The toolkit is responsible for:

- communicating with AI providers
- validating responses
- tracking usage
- handling retries
- exposing a clean developer API

Applications remain responsible for business logic.

---

# Current Features

## AI Client

Single entry point for all AI requests.

```python
from ai.client import AIClient

ai = AIClient()

response = ai.ask(...)
```

---

## Fluent Request Builder

For simple requests, use `AIClient.ask()`:

```python
from ai.client import AIClient

ai = AIClient()

result = ai.ask("Explain dependency injection in one paragraph.")
```

For advanced requests, use the fluent request builder:

```python
from ai.client import AIClient

ai = AIClient()

result = (
    ai.request()
    .prompt("Explain dependency injection in one paragraph.")
    .execute()
)

print(result.data)
```

Structured responses also work through the builder:

```python
from pydantic import BaseModel

from ai.client import AIClient


class Recommendation(BaseModel):
    title: str
    reason: str


ai = AIClient()

result = (
    ai.request()
    .prompt("Recommend one beginner Python project.")
    .response_type(Recommendation)
    .execute()
)

print(result.data.title)
```

The builder is intentionally mutable. Each method updates the current builder and returns `self`, which allows method chaining.

Request execution is still handled by `RequestExecutor`.

---

## Prompt Templates

Prompt templates provide a reusable way to build prompts by substituting named variables into a template.

```python
from ai.client import AIClient
from ai.prompts import PromptTemplate

template = PromptTemplate(
    "Summarize this article in {language}: {article}"
)

prompt = template.render(
    language="English",
    article="Python is popular.",
)

ai = AIClient()

result = ai.ask(prompt)

print(result.data)
```

Prompt templates are ideal for reusable prompts that differ only by input values.

For prompts assembled dynamically from multiple sections, use `PromptBuilder`.

---

---

## Structured Outputs

Structured outputs allow the toolkit to return validated Pydantic models instead of plain text.

```python
from pydantic import BaseModel

from ai.client import AIClient


class Answer(BaseModel):
    summary: str
    confidence: float


ai = AIClient()

result = ai.ask(
    prompt="Summarize dependency injection in one sentence.",
    response_type=Answer,
)

print(result.data.summary)
print(result.data.confidence)
```

When `response_type` is provided, the toolkit:

- builds a schema-aware prompt
- asks the model to return valid JSON
- parses the raw response
- validates the response with Pydantic
- retries once when JSON parsing or schema validation fails, depending on `AI_MAX_RETRIES`

The structured-output logic is centralized in:

```text
ai/structured.py
```

This keeps structured prompt construction and structured response parsing separate from request execution.

The same structured-output behavior is used by:

- `AIClient.ask(...)`
- `AsyncAIClient.ask(...)`
- `AIClient.ask_with_images(...)`

Example with image input:

```python
from pydantic import BaseModel

from ai.client import AIClient
from ai.images import ImageInput


class ImageDescription(BaseModel):
    subject: str
    colors: list[str]
    visible_text: str | None = None


ai = AIClient()

result = ai.ask_with_images(
    prompt="Extract structured information from this image.",
    images=[
        ImageInput(
            source=(
                "https://api.nga.gov/iiif/"
                "a2e6da57-3cd1-4235-b20e-95dcaefed6c8/"
                "full/!800,800/0/default.jpg"
            ),
        )
    ],
    response_type=ImageDescription,
)

print(result.data.subject)
print(result.data.colors)
```

Current structured-output support:

- Pydantic response models
- schema-aware prompt generation
- JSON parsing
- Pydantic validation
- repair retry for invalid JSON or schema mismatch
- sync requests
- async requests
- image requests with structured responses

Not yet supported:

- provider-native strict structured output
- OpenAI `response_format` integration
- streaming structured output
- partial structured validation while streaming

Provider-native strict structured output may be added later without changing the public `response_type` API.

---

## Streaming Responses

For plain text responses, you can stream chunks as they arrive.

```python
from ai.client import AIClient

ai = AIClient()

for chunk in ai.stream("Explain dependency injection in one short paragraph."):
    print(chunk, end="", flush=True)

print()
```

Streaming is useful when you want to show output immediately instead of waiting for the full response.

Current streaming support:

* plain text responses
* synchronous iteration
* provider-level streaming through `stream_text()`

Not yet supported:

* structured streaming
* async streaming
* token usage metadata during streaming

Structured responses should still use:

```python
ai.ask(..., response_type=...)
```

`ai.stream(...)` returns streamed text chunks as an iterator, not a full `AIResult`.

---

## Async AI Client

For async Python applications, use `AsyncAIClient`.

```python
import asyncio

from ai.async_client import AsyncAIClient


async def main() -> None:
    ai = AsyncAIClient()

    result = await ai.ask(
        "Explain dependency injection in one short paragraph."
    )

    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
```

Structured responses also work with the async client.

```python
import asyncio

from pydantic import BaseModel

from ai.async_client import AsyncAIClient


class Summary(BaseModel):
    title: str
    key_point: str


async def main() -> None:
    ai = AsyncAIClient()

    result = await ai.ask(
        prompt="Summarize dependency injection.",
        response_type=Summary,
    )

    print(result.data.title)
    print(result.data.key_point)


if __name__ == "__main__":
    asyncio.run(main())
```

Use `AIClient` for synchronous applications.

Use `AsyncAIClient` for asynchronous applications, such as FastAPI apps, async workers, or other event-loop based systems.

Current async support:

* plain text requests
* structured responses
* retry for structured responses
* full `AIResult` return values

Not yet supported:

* async streaming
* async fluent request builder
* async tool calling

---

## Tool Calling

Tool calling allows the model to request external capabilities, such as searching documents, checking weather, querying a database, or calling an application service.

The toolkit defines tools in a provider-independent way.

```python
from ai.client import AIClient
from ai.tools import ToolDefinition

ai = AIClient()

weather_tool = ToolDefinition(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, for example Paris or London.",
            }
        },
        "required": ["location"],
        "additionalProperties": False,
    },
)

response = ai.ask_with_tools(
    prompt="What is the weather in Paris?",
    tools=[weather_tool],
)

for tool_call in response.tool_calls:
    print(tool_call.name)
    print(tool_call.arguments)
```

Tool calling currently returns requested tool calls to the application.

The toolkit does **not** automatically execute tools.

That means application code remains responsible for deciding whether and how to run a requested tool.

```python
for tool_call in response.tool_calls:
    if tool_call.name == "get_weather":
        location = tool_call.arguments["location"]
        # Application decides what to do next.
```

Current tool-calling support:

* provider-independent `ToolDefinition`
* provider-independent `ToolCall`
* provider-independent `ToolResponse`
* OpenAI tool-call adapter
* requested tool calls returned to the application

Not yet supported:

* automatic tool execution
* submitting tool results back to the model
* multi-step agent loops
* parallel tool execution
* async tool calling

Automatic tool execution belongs later in the Agents and Workflows roadmap.


---

## Image Inputs

Image inputs allow the toolkit to send one or more images together with a text prompt.

The public API uses provider-independent `ImageInput` objects.

```python
from ai.client import AIClient
from ai.images import ImageInput

ai = AIClient()

image = ImageInput(
    source=(
        "https://api.nga.gov/iiif/"
        "a2e6da57-3cd1-4235-b20e-95dcaefed6c8/"
        "full/!800,800/0/default.jpg"
    ),
)

result = ai.ask_with_images(
    prompt="Describe this image in one short paragraph.",
    images=[image],
)

print(result.data)
```

Structured responses are also supported.

```python
from pydantic import BaseModel

from ai.client import AIClient
from ai.images import ImageInput


class ImageDescription(BaseModel):
    subject: str
    colors: list[str]
    visible_text: str | None = None


ai = AIClient()

result = ai.ask_with_images(
    prompt="Extract structured information from this image.",
    images=[
        ImageInput(
            source=(
                "https://api.nga.gov/iiif/"
                "a2e6da57-3cd1-4235-b20e-95dcaefed6c8/"
                "full/!800,800/0/default.jpg"
            ),
        )
    ],
    response_type=ImageDescription,
)

print(result.data.subject)
print(result.data.colors)
```

Current image-input support:

- image URL input
- Base64 data URL input
- multiple images
- plain text responses
- structured Pydantic responses
- OpenAI Responses API adapter

Not yet supported:

- local file helper
- OpenAI file ID helper
- async image input
- streaming image input
- image generation
- image editing

### Note about image URLs

When using image URLs, the model provider must be able to download the image.

Some public image hosts block automated downloads, redirects, or hotlinking. If a URL fails with an error like `Error while downloading file`, try another public image URL or use a Base64 data URL instead.


## Provider Architecture

Current:

- OpenAI

Planned:

- Anthropic
- Google Gemini
- Ollama
- Azure OpenAI
- Custom providers

---

---

## Embeddings

Embeddings convert text into vectors of numbers.

Those vectors can later be stored and searched to build Retrieval-Augmented Generation workflows.

Typical uses include:

- semantic search
- document search
- product search
- support knowledge search
- FAQ matching
- RAG pipelines

The toolkit exposes embeddings through `AIClient`.

```python
from ai.client import AIClient

ai = AIClient()

response = ai.embed_text(
    "Django is a Python web framework."
)

embedding = response.embeddings[0]

print(embedding.text)
print(len(embedding.vector))
print(response.model)
```

Batch embedding is also supported.

```python
from ai.client import AIClient

ai = AIClient()

response = ai.embed_texts(
    [
        "Django is a Python web framework.",
        "Redis is often used as a cache.",
        "PostgreSQL is a relational database.",
    ]
)

print(response.texts)
print(len(response.vectors))
```

Use `EmbeddingInput` when you need metadata.

```python
from ai.client import AIClient
from ai.embeddings import EmbeddingInput

ai = AIClient()

response = ai.embed_texts(
    [
        EmbeddingInput(
            text="Django is a Python web framework.",
            metadata={
                "source": "notes.md",
                "topic": "django",
            },
        )
    ]
)

embedding = response.embeddings[0]

print(embedding.text)
print(embedding.metadata)
print(len(embedding.vector))
```

Embedding configuration uses a separate model setting from normal AI requests.

```env
AI_PROVIDER=openai

OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Optional generic fallback
AI_EMBEDDING_MODEL=

# Optional custom embedding vector size
AI_EMBEDDING_DIMENSIONS=
```

The embedding model is separate because normal text requests and embedding requests use different provider capabilities.

```env
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Current embedding support:

- embed one text
- embed multiple texts
- preserve metadata
- provider-independent embedding models
- OpenAI embeddings adapter
- optional embedding dimensions
- token usage when reported by the provider

Not yet supported:

- vector store
- retriever
- RAG pipeline
- document loaders
- database loaders
- embedding cache
- async embeddings

Embeddings are the first building block for RAG.

A later RAG flow will look like this:

```text
Documents / database rows
    ↓
Embeddings
    ↓
Vector store
    ↓
Retriever
    ↓
Relevant context
    ↓
AI answer
```

---

## Vector Store

A vector store saves embedded text records and allows similarity search.

This is the second building block for Retrieval-Augmented Generation.

The basic flow is:

```text
Text
    ↓
Embedding vector
    ↓
VectorRecord
    ↓
Vector store
    ↓
Similarity search
    ↓
Relevant results
```

The toolkit includes a dependency-free in-memory vector store.

```python
from ai.vector_store import InMemoryVectorStore, VectorRecord

store = InMemoryVectorStore()

store.add(
    [
        VectorRecord(
            id="doc-1",
            text="Django is a Python web framework.",
            vector=[1.0, 0.0, 0.0],
            metadata={
                "topic": "django",
            },
        ),
        VectorRecord(
            id="doc-2",
            text="Redis is often used as a cache.",
            vector=[0.0, 1.0, 0.0],
            metadata={
                "topic": "redis",
            },
        ),
    ]
)

results = store.similarity_search(
    query_vector=[0.0, 0.9, 0.1],
    limit=1,
)

for result in results:
    print(result.text)
    print(result.score)
    print(result.metadata)
```

A more realistic example uses embeddings from `AIClient`.

```python
from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.vector_store import InMemoryVectorStore, VectorRecord

ai = AIClient()
store = InMemoryVectorStore()

texts = [
    EmbeddingInput(
        text="Django is a Python web framework.",
        metadata={"topic": "django"},
    ),
    EmbeddingInput(
        text="Redis is often used as a cache and message broker.",
        metadata={"topic": "redis"},
    ),
    EmbeddingInput(
        text="PostgreSQL is a relational database.",
        metadata={"topic": "postgres"},
    ),
]

embedding_response = ai.embed_texts(texts)

records = [
    VectorRecord(
        id=f"doc-{embedding.index}",
        text=embedding.text,
        vector=embedding.vector,
        metadata=embedding.metadata,
    )
    for embedding in embedding_response.embeddings
]

store.add(records)

query_response = ai.embed_text(
    "Which technology should I use for caching?"
)

query_vector = query_response.embeddings[0].vector

results = store.similarity_search(
    query_vector=query_vector,
    limit=2,
)

for result in results:
    print(result.text)
    print(result.score)
    print(result.metadata)
```

The in-memory vector store supports metadata filtering.

```python
results = store.similarity_search(
    query_vector=query_vector,
    limit=5,
    metadata_filter={
        "topic": "redis",
    },
)
```

Current vector store support:

- provider-independent `VectorRecord`
- provider-independent `VectorSearchResult`
- `BaseVectorStore` interface
- dependency-free `InMemoryVectorStore`
- cosine similarity search
- metadata preservation
- metadata filtering
- record replacement by ID
- count and clear operations

Not yet supported:

- persistent storage
- PostgreSQL / pgvector
- Chroma
- Pinecone
- FAISS
- Qdrant
- retriever interface
- full RAG pipeline
- document loaders

The in-memory store is best for tests, examples, demos, and small local workflows.

Production applications should later use a persistent vector store implementation behind the same `BaseVectorStore` interface.

## Retriever

A retriever connects embeddings and a vector store.

It takes a user query, embeds it, searches the vector store, and returns relevant context.

The basic flow is:

```text
User question
    ↓
Query embedding
    ↓
Vector store similarity search
    ↓
Retrieved context
```

The toolkit includes `VectorStoreRetriever`.

```python
from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.retriever import VectorStoreRetriever, format_retrieved_context
from ai.vector_store import InMemoryVectorStore, VectorRecord

ai = AIClient()
store = InMemoryVectorStore()

knowledge = [
    EmbeddingInput(
        text="Redis is often used as a cache and message broker.",
        metadata={"topic": "redis"},
    ),
    EmbeddingInput(
        text="PostgreSQL is a relational database.",
        metadata={"topic": "postgres"},
    ),
    EmbeddingInput(
        text="Django is a Python web framework.",
        metadata={"topic": "django"},
    ),
]

embedding_response = ai.embed_texts(knowledge)

records = [
    VectorRecord(
        id=f"doc-{embedding.index}",
        text=embedding.text,
        vector=embedding.vector,
        metadata=embedding.metadata,
    )
    for embedding in embedding_response.embeddings
]

store.add(records)

retriever = VectorStoreRetriever(
    ai_client=ai,
    vector_store=store,
)

contexts = retriever.retrieve(
    query="Which technology should I use for caching?",
    limit=2,
)

context_text = format_retrieved_context(contexts)

print(context_text)
```

`RetrievedContext` contains only the information needed by higher-level RAG code.

```python
context.id
context.text
context.score
context.metadata
```

The raw vector is not exposed by the retriever result.

Metadata filtering is supported.

```python
contexts = retriever.retrieve(
    query="How should I cache data?",
    limit=5,
    metadata_filter={
        "topic": "redis",
    },
)
```

Retrieved context can be inserted into a prompt.

```python
prompt = f"""
Answer the question using only the context below.

Context:
{context_text}

Question:
Which technology should I use for caching?
"""
```

Current retriever support:

- provider-independent `RetrievedContext`
- `BaseRetriever` interface
- `VectorStoreRetriever`
- query embedding through `AIClient`
- vector store similarity search
- metadata filtering
- prompt-ready context formatting

Not yet supported:

- full RAG answer pipeline
- reranking
- hybrid keyword and vector search
- retrieval evaluation
- document loaders
- database loaders

The retriever finds relevant context. It does not generate the final answer yet.

Answer generation is added by the RAG pipeline.

## RAG Pipeline

The RAG pipeline combines retrieval and answer generation.

RAG means Retrieval-Augmented Generation.

Instead of asking the model to answer only from general knowledge, the application first retrieves relevant context from its own stored knowledge, then sends that context to the model.

The basic flow is:

```text
User question
    ↓
Retriever
    ↓
Relevant context
    ↓
Grounded prompt
    ↓
AI answer
    ↓
Answer + sources
```

The toolkit includes `RAGPipeline`.

```python
from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.rag import RAGPipeline
from ai.retriever import VectorStoreRetriever
from ai.vector_store import InMemoryVectorStore, VectorRecord

ai = AIClient()
store = InMemoryVectorStore()

knowledge = [
    EmbeddingInput(
        text="Redis is often used as a cache and message broker.",
        metadata={
            "topic": "redis",
            "source": "technical_notes",
        },
    ),
    EmbeddingInput(
        text="PostgreSQL is a relational database used for structured data.",
        metadata={
            "topic": "postgres",
            "source": "technical_notes",
        },
    ),
    EmbeddingInput(
        text="Django is a Python web framework for building web applications.",
        metadata={
            "topic": "django",
            "source": "technical_notes",
        },
    ),
]

embedding_response = ai.embed_texts(knowledge)

records = [
    VectorRecord(
        id=f"doc-{embedding.index}",
        text=embedding.text,
        vector=embedding.vector,
        metadata=embedding.metadata,
    )
    for embedding in embedding_response.embeddings
]

store.add(records)

retriever = VectorStoreRetriever(
    ai_client=ai,
    vector_store=store,
)

rag = RAGPipeline(
    ai_client=ai,
    retriever=retriever,
)

response = rag.ask(
    question="Which technology should I use for caching?",
    limit=2,
    instructions="Answer in one short paragraph.",
)

print(response.answer)

for context in response.contexts:
    print(context.id)
    print(context.score)
    print(context.metadata)
    print(context.text)
```

`RAGPipeline.ask(...)` returns a `RAGResponse`.

```python
response.answer
response.contexts
response.model
response.request_id
response.raw_response
```

The answer is generated from retrieved context.

The contexts are returned so the application can show sources, debug retrieval quality, or inspect which records were used.

Example source display:

```python
for context in response.contexts:
    print(f"Source: {context.metadata}")
    print(f"Score: {context.score:.4f}")
    print(context.text)
```

Additional instructions can be passed to the RAG prompt.

```python
response = rag.ask(
    question="Which technology should I use for caching?",
    instructions="Answer briefly and mention only technologies found in the context.",
)
```

Metadata filtering is also supported.

```python
response = rag.ask(
    question="How should I cache data?",
    metadata_filter={
        "topic": "redis",
    },
)
```

Current RAG pipeline support:

- `RAGResponse`
- grounded RAG prompt builder
- `RAGPipeline`
- retrieval through `BaseRetriever`
- answer generation through `AIClient`
- returned answer and retrieved contexts
- metadata filtering
- additional prompt instructions

Not yet supported:

- streaming RAG responses
- async RAG pipeline
- structured RAG responses
- citation formatting
- reranking
- retrieval evaluation
- hybrid keyword and vector search
- document loaders
- database loaders

The RAG pipeline is the first complete end-to-end Retrieval-Augmented Generation workflow in the toolkit.

At this stage, knowledge must still be added manually or through application code.

Document loading is added later in the Sprint 6 roadmap.

## Document Loaders

Document loaders turn files into `Document` objects that can be embedded, stored, retrieved, and used in RAG workflows.

The basic flow is:

```text
File / directory
    ↓
Document loader
    ↓
Document
    ↓
EmbeddingInput
    ↓
Embeddings
    ↓
Vector store
    ↓
Retriever
    ↓
RAG pipeline
```

The toolkit includes simple dependency-free loaders for text and Markdown files.

```python
from ai.documents import TextFileLoader, MarkdownFileLoader

text_documents = TextFileLoader("notes.txt").load()
markdown_documents = MarkdownFileLoader("guide.md").load()
```

Each loader returns a list of `Document` objects.

```python
document.text
document.metadata
```

Example metadata:

```python
{
    "source": "examples/sample_docs/redis.md",
    "filename": "redis.md",
    "extension": ".md",
    "loader": "MarkdownFileLoader",
}
```

A directory can be loaded with `DirectoryLoader`.

```python
from ai.documents import DirectoryLoader

documents = DirectoryLoader(
    path="examples/sample_docs",
    recursive=True,
).load()

for document in documents:
    print(document.metadata["filename"])
    print(document.text[:100])
```

Loaded documents can be converted into embedding inputs.

```python
from ai.documents import DirectoryLoader, documents_to_embedding_inputs

documents = DirectoryLoader(
    path="examples/sample_docs",
    recursive=True,
).load()

embedding_inputs = documents_to_embedding_inputs(documents)
```

A full document-based RAG flow looks like this:

```python
from ai.client import AIClient
from ai.documents import DirectoryLoader, documents_to_embedding_inputs
from ai.rag import RAGPipeline
from ai.retriever import VectorStoreRetriever
from ai.vector_store import InMemoryVectorStore, VectorRecord

ai = AIClient()
store = InMemoryVectorStore()

documents = DirectoryLoader(
    path="examples/sample_docs",
    recursive=True,
).load()

embedding_inputs = documents_to_embedding_inputs(documents)

embedding_response = ai.embed_texts(embedding_inputs)

records = [
    VectorRecord(
        id=f"doc-{embedding.index}",
        text=embedding.text,
        vector=embedding.vector,
        metadata=embedding.metadata,
    )
    for embedding in embedding_response.embeddings
]

store.add(records)

retriever = VectorStoreRetriever(
    ai_client=ai,
    vector_store=store,
)

rag = RAGPipeline(
    ai_client=ai,
    retriever=retriever,
)

response = rag.ask(
    question="Which technology should I use for caching?",
    limit=2,
)

print(response.answer)

for context in response.contexts:
    print(context.metadata.get("filename"))
    print(context.score)
    print(context.text)
```

Current document-loader support:

- provider-independent `Document`
- `BaseDocumentLoader`
- `TextFileLoader`
- `MarkdownFileLoader`
- `DirectoryLoader`
- recursive directory loading
- configurable file extensions
- source metadata preservation
- conversion from documents to embedding inputs

Not yet supported:

- PDF loader
- DOCX loader
- HTML loader
- database loader
- automatic chunking
- Markdown section-aware loading
- file watching and re-indexing
- high-level document indexing helper

Document loaders complete the first end-to-end RAG workflow:

```text
Documents
    ↓
Embeddings
    ↓
Vector store
    ↓
Retriever
    ↓
RAG pipeline
    ↓
Answer with sources
```

## Conversation Memory

Conversation memory stores messages across turns.

Agents and workflows need memory because they often operate over multiple user and assistant messages, not one isolated prompt.

The basic flow is:

```text
User message
    ↓
Memory
    ↓
Assistant response
    ↓
Memory
    ↓
Next user message with previous context
```

The toolkit includes provider-independent memory models.

```python
from ai.memory import (
    InMemoryConversationMemory,
    format_conversation_messages,
)

memory = InMemoryConversationMemory()

memory.add_system_message("You are a helpful AI assistant.")
memory.add_user_message("What is Redis?")
memory.add_assistant_message(
    "Redis is often used as a cache and message broker."
)

conversation_text = format_conversation_messages(
    memory.messages()
)

print(conversation_text)
```

Output shape:

```text
SYSTEM:
You are a helpful AI assistant.

USER:
What is Redis?

ASSISTANT:
Redis is often used as a cache and message broker.
```

Memory supports system, user, assistant, and tool messages.

```python
memory.add_system_message("You are a concise assistant.")
memory.add_user_message("What is the weather?")
memory.add_assistant_message("I need to call a weather tool.")
memory.add_tool_message(
    '{"temperature": "18C"}',
    metadata={"tool_name": "get_weather"},
)
```

Recent messages can be retrieved for prompt context.

```python
recent = memory.recent_messages(limit=5)

conversation_text = format_conversation_messages(recent)
```

Memory can be cleared.

```python
memory.clear()
```

Current conversation memory support:

- provider-independent `ConversationMessage`
- `MessageRole`
- `BaseConversationMemory`
- `InMemoryConversationMemory`
- system messages
- user messages
- assistant messages
- tool messages
- metadata preservation
- recent message retrieval
- memory clearing
- prompt-ready conversation formatting

Not yet supported:

- persistent conversation memory
- database-backed conversation memory
- token-aware memory trimming
- conversation summarization memory
- vector-based long-term memory

Conversation memory is the first building block for agents and workflows.

## Structured Responses

Supports returning validated Pydantic models instead of raw text.

```python
recommendation = ai.ask(
    prompt=prompt,
    response_type=DrinkRecommendation,
)

print(recommendation.data.recommended_item)
```

---

## Automatic Validation

Responses are validated using Pydantic schemas.

Invalid JSON and schema mismatches raise custom exceptions.

---

## Retry

Structured responses are automatically retried using the configured retry count if validation fails.

---

## Logging

Each request is logged with:

- request id
- model
- duration
- retry count
- token usage
- estimated cost

Prompts and model responses are not logged by default.

---

## Token Usage

Provider token usage is tracked and returned with every request.

---

## Cost Estimation

Supports configurable token pricing for estimating request cost.

---

## Custom Exceptions

Includes dedicated exception hierarchy.

Examples:

- `AIConfigurationError`
- `AIProviderError`
- `AIJSONParseError`
- `AISchemaValidationError`

---

# Current Project Structure

```text
python-ai-toolkit/

├── ai/
│   ├── client.py
│   ├── config.py
│   ├── cost.py
│   ├── exceptions.py
│   ├── executor.py
│   ├── logger.py
│   ├── parser.py
│   ├── prompts.py
│   ├── request_builder.py
│   ├── schemas.py
│   └── providers/
│       ├── base.py
│       ├── factory.py
│       └── openai_provider.py
│
├── docs/
│   ├── architecture/
│   └── development/
│
├── examples/
│
├── tests/
│
├── logs/
│
└── README.md
```

## Configuration Validation

Configuration is validated when `AIClient` loads the toolkit settings.

The toolkit fails early with `AIConfigurationError` when configuration is invalid.

Currently validated:

- provider is not empty
- API key is not empty
- model is not empty
- retry count is zero or greater

Example:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini
AI_MAX_RETRIES=1
```

Invalid configuration raises an error before an AI request is sent.

```python
from ai.client import AIClient
from ai.exceptions import AIConfigurationError

try:
    ai = AIClient()
except AIConfigurationError as exc:
    print(f"Invalid AI configuration: {exc}")
```


## Why this documentation matters

Configuration validation affects application startup behavior. Developers need to know that:

```python
AIClient()
```
may raise:
```python
AIConfigurationError
```
before any request is made.

That is intentional fail-fast behavior.

---

# Installation

Clone the repository.

```bash
git clone https://github.com/<your-username>/python-ai-toolkit.git
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env`.

```env
AI_PROVIDER=openai

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini

# Optional generic fallback for custom providers
AI_API_KEY=
AI_MODEL=

AI_MAX_RETRIES=1

AI_INPUT_COST_PER_1M_TOKENS=
AI_OUTPUT_COST_PER_1M_TOKENS=
```

---

# Development

Run tests.

```bash
python -m pytest
```

Format code.

```bash
python -m black .
```

Lint code.

```bash
python -m ruff check .
```

---

# Roadmap

## Core

- [x] Configuration management
- [x] Provider abstraction
- [x] Provider factory
- [x] Provider registry
- [x] Provider registration API
- [x] Provider configuration cleanup
- [x] OpenAI provider
- [x] AI client
- [x] Fluent request builder
- [x] Prompt builder
- [x] Prompt templates
- [x] Structured responses
- [x] Schema validation
- [x] Retry
- [x] Logging
- [x] Token tracking
- [x] Cost estimation
- [x] Request IDs

---

## Planned

- [ ] Example gallery
- [ ] Configuration validation improvements
- [ ] Better error messages
- [ ] Streaming responses
- [ ] Async client
- [ ] Tool calling
- [ ] Image inputs
- [ ] Conversation memory
- [ ] Embeddings
- [ ] Vector store abstraction
- [ ] RAG pipeline
- [ ] Agent framework
- [ ] Workflow engine
- [ ] Django integration
- [ ] FastAPI integration
- [ ] PyPI package

---

# Design Principles

- Single Responsibility Principle
- Dependency Inversion
- Composition over inheritance
- Strong typing
- Reusable components
- Clear interfaces
- Production-oriented architecture

---

# License

MIT
