# Embeddings, Retrieval, and RAG

Python AI Toolkit keeps retrieval-augmented generation (RAG) as a set of
separate, provider-independent layers:

```text
Document loading
    ↓
Embedding
    ↓
Vector storage
    ↓
Retrieval
    ↓
Prompt construction and answer generation
```

Applications may use the complete pipeline or replace any layer behind its
public interface. OpenAI-specific embedding behavior remains inside
`OpenAIProvider`; vector storage, retrieval, document loading, and RAG
orchestration do not depend on the OpenAI SDK.

## Capability and return-value map

| Layer | Main public API | Return value |
| --- | --- | --- |
| Single embedding | `AIClient.embed_text()` | `EmbeddingResponse` |
| Batch embedding | `AIClient.embed_texts()` | `EmbeddingResponse` |
| Vector storage | `BaseVectorStore` | Store-specific state |
| Similarity search | `BaseVectorStore.similarity_search()` | `list[VectorSearchResult]` |
| Retrieval | `BaseRetriever.retrieve()` | `list[RetrievedContext]` |
| Document loading | `BaseDocumentLoader.load()` | `list[Document]` |
| RAG answer | `RAGPipeline.ask()` | `RAGResponse` |

These return types are intentionally different. Embedding calls do not return
`AIResult`, and `RAGResponse` exposes only part of the metadata from the
underlying text-generation request.

The current retrieval stack is synchronous. `AsyncAIClient` does not expose
embedding methods, and `RAGPipeline` is not asynchronous or streaming.

## Configure embeddings

The embedding model is configured separately from the text-generation model:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
AI_EMBEDDING_DIMENSIONS=
```

Embedding-model resolution follows this order:

```text
<PROVIDER>_EMBEDDING_MODEL
    ↓
AI_EMBEDDING_MODEL
    ↓
text-embedding-3-small
```

`AI_EMBEDDING_DIMENSIONS` is optional. When it is blank, the provider chooses
the vector size. When set, it must be a positive whole number, and the selected
provider and embedding model must support that dimension.

Configuration proves only that a value is structurally valid. It does not
prove that the provider implements embeddings or that the selected account and
model accept the request.

See [Configuration](configuration.md) for environment precedence and explicit
`AIConfig` construction.

## Create embeddings

### One text

`embed_text()` accepts text plus optional string metadata:

```python
from ai.client import AIClient

client = AIClient()

response = client.embed_text(
    "Redis is often used as a cache.",
    metadata={
        "source": "architecture-notes",
        "topic": "redis",
    },
)

embedding = response.embeddings[0]

print(response.model)
print(embedding.text)
print(embedding.vector)
print(embedding.metadata)
```

### A batch of texts

Plain strings are convenient when no metadata is needed:

```python
response = client.embed_texts(
    [
        "Redis is often used as a cache.",
        "PostgreSQL is a relational database.",
    ]
)

print(response.texts)
print(response.vectors)
```

Use `EmbeddingInput` to preserve application metadata:

```python
from ai.embeddings import EmbeddingInput

response = client.embed_texts(
    [
        EmbeddingInput(
            text="Redis is often used as a cache.",
            metadata={"id": "redis", "source": "notes"},
        ),
        EmbeddingInput(
            text="PostgreSQL is a relational database.",
            metadata={"id": "postgres", "source": "notes"},
        ),
    ]
)
```

`EmbeddingResponse` contains:

| Field | Meaning |
| --- | --- |
| `embeddings` | Provider-returned embedding items |
| `model` | Embedding model reported or selected by the provider |
| `token_usage` | Optional provider-reported embedding token usage |
| `texts` | Convenience property returning the embedded texts |
| `vectors` | Convenience property returning only the vectors |

Each `EmbeddingVector` contains:

| Field | Meaning |
| --- | --- |
| `text` | Original input text |
| `vector` | Floating-point embedding vector |
| `index` | Index of the corresponding original input |
| `metadata` | Original application metadata |

Use `EmbeddingVector.index` to correlate a result with the original batch
input. The built-in OpenAI adapter validates the provider's returned index and
uses it to restore the matching text and metadata. It does not sort provider
results before returning them, so application code should not use result-list
position as the only correlation key.

### Embedding metadata boundary

`EmbeddingResponse` is not `AIResult`. It does not expose:

- a toolkit request ID
- request duration
- retry count
- estimated cost
- a raw provider response

`token_usage` is optional because not every provider reports embedding usage.
Embedding requests also bypass the ordinary text `RequestExecutor`; structured
response repair settings do not apply to them.

A provider that does not implement `embed_texts()` raises `AIProviderError`.
The built-in OpenAI provider also rejects an empty batch, blank input text, and
invalid provider-returned indices.

## Store vectors

`VectorRecord` is the provider-independent storage input:

```python
from ai.vector_store import InMemoryVectorStore, VectorRecord

store = InMemoryVectorStore()

records = [
    VectorRecord(
        id=f"doc-{embedding.index}",
        text=embedding.text,
        vector=embedding.vector,
        metadata=embedding.metadata,
    )
    for embedding in response.embeddings
]

store.add(records)
print(store.count())
```

Record IDs belong to the application. `InMemoryVectorStore.add()` replaces an
existing record when another record has the same ID.

The abstract `BaseVectorStore` contract contains four operations:

| Method | Contract |
| --- | --- |
| `add(records)` | Add or update application-owned records |
| `similarity_search(...)` | Return the closest records |
| `count()` | Return the number of stored records |
| `clear()` | Remove all records |

Applications may implement `BaseVectorStore` for a persistent database or
external vector service without changing `VectorStoreRetriever` or
`RAGPipeline`.

## Search by similarity

Embed the query with the same embedding model and dimensions used for stored
records:

```python
query = client.embed_text("Which technology should I use for caching?")

results = store.similarity_search(
    query_vector=query.embeddings[0].vector,
    limit=3,
    metadata_filter={"source": "notes"},
)

for result in results:
    print(result.id, result.score, result.text)
```

`VectorSearchResult` includes the record ID, text, vector, similarity score,
and metadata.

The in-memory implementation:

- calculates cosine similarity
- returns results from highest score to lowest
- returns at most `limit` items
- returns an empty list when `limit <= 0`
- applies every metadata-filter pair using exact string equality
- returns an empty list when the filter matches nothing
- returns a score of `0.0` for a zero vector
- raises `ValueError` when compared vector dimensions differ

Metadata filtering uses logical AND. For example:

```python
metadata_filter={
    "tenant": "customer-42",
    "document_type": "policy",
}
```

matches only records containing both exact values.

### What a similarity score means

A cosine-similarity score is a ranking signal, not a probability, factual
confidence, or proof that the text answers the question. Useful score ranges
can change with the embedding model, dimensions, document preparation, and
knowledge set.

The toolkit does not apply a minimum score threshold. Applications that need
one should calibrate it against representative data and still handle the
no-relevant-context case.

### In-memory reference boundary

`InMemoryVectorStore` keeps every record and vector in process memory and
performs a linear scan for each query. It has no persistence, database
transactions, access control, approximate-nearest-neighbor index, or
cross-process coordination.

It is intended for tests, examples, demos, and small local applications. Use a
`BaseVectorStore` implementation backed by suitable persistent infrastructure
for production-scale or durable retrieval.

## Retrieve prompt-ready context

`VectorStoreRetriever` composes an `AIClient` and a `BaseVectorStore`:

```python
from ai.retriever import VectorStoreRetriever

retriever = VectorStoreRetriever(
    ai_client=client,
    vector_store=store,
)

contexts = retriever.retrieve(
    query="Which technology should I use for caching?",
    limit=3,
    metadata_filter={"source": "notes"},
)
```

The retriever:

1. rejects a blank query
2. embeds the query
3. searches the vector store
4. converts results into `RetrievedContext`

`RetrievedContext` preserves `id`, `text`, `score`, and `metadata`, but does
not expose the raw vector. This keeps the higher-level RAG contract focused on
prompt context rather than storage details.

`format_retrieved_context(contexts)` converts contexts into the numbered text
format used by `RAGPipeline`. An empty list becomes:

```text
No relevant context found.
```

Formatting does not validate factual accuracy, sanitize instructions embedded
inside retrieved text, or decide whether a score is high enough. Those remain
application and retrieval-policy responsibilities.

## Load documents

Document loaders extract text and metadata only:

```python
from ai.documents import DirectoryLoader

documents = DirectoryLoader(
    path="examples/sample_docs",
    recursive=True,
).load()
```

Available loaders are:

| Loader | Current behavior |
| --- | --- |
| `TextFileLoader` | Loads one non-empty text file as one `Document` |
| `MarkdownFileLoader` | Loads Markdown as plain text without section parsing |
| `DirectoryLoader` | Loads supported files in sorted path order |

`DirectoryLoader` is non-recursive by default and supports `.txt` and `.md`.
Its `extensions` argument can replace that set. Unsupported files are skipped,
and blank files produce no document.

Every loaded `Document` contains:

```python
Document(
    text="...",
    metadata={
        "source": "...",
        "filename": "...",
        "extension": "...",
        "loader": "...",
    },
)
```

Convert loaded documents explicitly:

```python
from ai.documents import documents_to_embedding_inputs

embedding_inputs = documents_to_embedding_inputs(documents)
embedding_response = client.embed_texts(embedding_inputs)
```

Loading, chunking, embedding, ID assignment, and indexing are separate
responsibilities:

```text
DocumentLoader
    ↓
Document
    ↓
application-owned chunking, if needed
    ↓
EmbeddingInput
    ↓
EmbeddingResponse
    ↓
VectorRecord
    ↓
BaseVectorStore
```

The toolkit does not currently split large files into chunks or provide a
one-call indexing helper. Embedding an entire file as one vector may reduce
retrieval quality or exceed a provider's input limit. Applications should
prepare appropriately sized text units before embedding.

## Build a RAG pipeline

`RAGPipeline` combines a text-generation client with any `BaseRetriever`:

```python
from ai.rag import RAGPipeline

rag = RAGPipeline(
    ai_client=client,
    retriever=retriever,
)

response = rag.ask(
    question="Which technology should I use for caching?",
    limit=3,
    metadata_filter={"source": "notes"},
    instructions="Answer in one short paragraph.",
)

print(response.answer)

for context in response.contexts:
    print(context.id, context.score)
```

The pipeline:

1. rejects a blank question
2. retrieves relevant contexts
3. formats those contexts
4. builds a prompt with grounding instructions
5. calls `AIClient.ask()` for a plain-text answer
6. returns the answer and the contexts used

`build_rag_prompt()` asks the model to use only the supplied context, admit when
the context is insufficient, and avoid inventing facts. Optional
`instructions` are included as additional instructions.

`RAGResponse` contains:

| Field | Meaning |
| --- | --- |
| `answer` | Plain-text model answer |
| `contexts` | Retrieved contexts inserted into the prompt |
| `model` | Text-generation model from the underlying `AIResult` |
| `request_id` | Request ID from the underlying `AIResult` |
| `raw_response` | Raw accepted answer text |

`RAGResponse` does not currently preserve the underlying request duration,
token usage, estimated cost, retry count, or original pre-repair response.

The current pipeline also does not provide structured answers, streaming,
async execution, reranking, citations, or automatic score thresholds. Those
capabilities must not be inferred from the plain `RAGResponse` contract.

## Grounding and source boundaries

RAG improves access to application-provided knowledge, but prompt instructions
cannot guarantee correctness.

In particular:

- similarity can retrieve irrelevant or incomplete text
- a model can ignore or misinterpret grounding instructions
- retrieved text can contain inaccurate or hostile instructions
- returned contexts show what was supplied, not which sentence actually
  supported each answer claim
- metadata is application-owned and is not verified by the toolkit
- the pipeline still calls the model when no contexts were found

Applications should enforce tenant and permission filters before retrieval,
calibrate relevance policy, validate high-impact answers, and treat returned
contexts as traceability data rather than verified citations.

## Related documentation

- [Public API reference](api_reference.md) lists exact embedding, vector-store,
  retriever, document-loader, and RAG contracts.
- [Configuration](configuration.md) covers embedding-model and dimension
  settings.
- [Providers](providers.md) explains optional provider capabilities.
- [Requests](requests.md) documents the underlying `AIResult` contract.
- [Security and secret handling](security.md) covers document authorization,
  tenant isolation, sensitive embeddings, retention, and provider policy.
- [Example gallery](../examples/README.md) contains examples 10 through 14.
- [Architecture](architecture/architecture.md) describes the retrieval layers.
- [ADR-0010](architecture/decisions/0010-provider-independent-rag-abstractions.md)
  records the provider-independent RAG design.
- [ADR-0011](architecture/decisions/0011-document-loaders-separate-from-embedding.md)
  records the document-loading boundary.
