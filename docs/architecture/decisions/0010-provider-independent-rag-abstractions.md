# ADR-0010

## Title

Use provider-independent RAG abstractions

---

## Status

Accepted

---

## Date

2026-07-19

---

## Context

Sprint 6 added Retrieval-Augmented Generation support.

RAG requires several connected capabilities:

- embeddings
- vector storage
- retrieval
- prompt construction
- answer generation

A simple implementation could directly couple the toolkit to OpenAI embeddings and a single vector database.

That would work for early examples, but it would make the toolkit harder to extend to other embedding providers, vector stores, or retrieval strategies.

The project goal is to keep the toolkit provider-independent and reusable across applications.

---

## Decision

Build RAG from separate provider-independent abstractions.

The main layers are:

```text
EmbeddingInput / EmbeddingResponse
    ↓
BaseVectorStore
    ↓
BaseRetriever
    ↓
RAGPipeline
```

Embeddings are exposed through `AIClient`:

```python
ai.embed_text(...)
ai.embed_texts(...)
```

Vector storage is abstracted behind:

```python
BaseVectorStore
```

Retrieval is abstracted behind:

```python
BaseRetriever
```

The first concrete implementations are:

```python
InMemoryVectorStore
VectorStoreRetriever
RAGPipeline
```

OpenAI-specific embedding behavior remains inside `OpenAIProvider`.

---

## Alternatives Considered

### Couple RAG directly to OpenAI embeddings

Rejected because the toolkit should support additional providers later without rewriting RAG code.

### Couple RAG directly to one vector database

Rejected because different applications may use in-memory search, PostgreSQL with pgvector, Chroma, Pinecone, FAISS, Qdrant, or another store.

### Combine embedding, retrieval, and answering into one class

Rejected because it would make the RAG system harder to test, customize, and extend.

Separate layers make each part reusable.

---

## Consequences

### Positive

- RAG is not tied to OpenAI.
- Vector storage can be replaced without changing the RAG pipeline.
- Retrieval strategies can evolve independently.
- Tests can isolate embeddings, vector storage, retrieval, and answer generation.
- Applications can reuse only the layers they need.

### Negative

- More classes and files are required.
- Users must understand several RAG concepts.
- Early examples require some manual wiring.

---

## Related Files

- `ai/embeddings.py`
- `ai/vector_store.py`
- `ai/retriever.py`
- `ai/rag.py`
- `ai/client.py`
- `ai/providers/base.py`
- `ai/providers/openai_provider.py`
- `tests/test_embeddings.py`
- `tests/test_vector_store.py`
- `tests/test_retriever.py`
- `tests/test_rag.py`
