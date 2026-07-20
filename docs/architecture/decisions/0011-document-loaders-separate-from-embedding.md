# ADR-0011

## Title

Keep document loading separate from embedding and indexing

---

## Status

Accepted

---

## Date

2026-07-19

---

## Context

Sprint 6 added document loaders for RAG workflows.

Document loading, embedding, and indexing are related, but they are not the same responsibility.

A document loader extracts text and metadata from a source.

Embedding converts text into vectors.

Indexing stores vectors in a vector store.

Combining all of these into one loader would make simple workflows convenient, but it would also make the design less flexible.

Future loaders may handle PDFs, DOCX files, HTML, database rows, APIs, or large documents that need chunking.

---

## Decision

Document loaders produce `Document` objects only.

A `Document` contains:

```python
Document(
    text="...",
    metadata={...},
)
```

Embedding happens separately by converting documents into `EmbeddingInput` objects:

```python
documents_to_embedding_inputs(documents)
```

The indexing flow remains explicit:

```text
DocumentLoader
    ↓
Document
    ↓
EmbeddingInput
    ↓
EmbeddingResponse
    ↓
VectorRecord
    ↓
VectorStore
```

The first loaders are dependency-free:

```python
TextFileLoader
MarkdownFileLoader
DirectoryLoader
```

---

## Alternatives Considered

### Make loaders automatically embed documents

Rejected because loaders would need access to `AIClient`, embedding configuration, batching behavior, and provider errors.

That would couple file loading to AI provider logic.

### Make loaders automatically store vectors

Rejected because loaders should not know which vector store is being used.

Applications may use in-memory storage, PostgreSQL, Chroma, Pinecone, or another store.

### Add chunking immediately

Rejected for the first version because chunking introduces additional decisions:

- chunk size
- overlap
- metadata propagation
- section boundaries
- token counting

Chunking is deferred.

---

## Consequences

### Positive

- Loading, embedding, and indexing stay separate.
- Loaders are easy to test.
- Applications control when and how documents are embedded.
- Future loaders can reuse the same `Document` model.
- Chunking can be added later without redesigning embeddings.

### Negative

- Early examples require manual wiring.
- Users need to understand the document-to-embedding flow.
- A high-level indexing helper may be needed later for convenience.

---

## Related Files

- `ai/documents.py`
- `ai/embeddings.py`
- `ai/vector_store.py`
- `tests/test_documents.py`
- `examples/14_document_loader_rag.py`
