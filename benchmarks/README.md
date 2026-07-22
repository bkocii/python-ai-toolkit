# Benchmark Suite

This directory contains isolated performance benchmarks for Python AI Toolkit.

The benchmark suite measures toolkit overhead independently from provider latency, network conditions, API availability, and real model execution.

Benchmarks are intentionally separate from the normal unit test suite.

---

## Directory Structure

```text
benchmarks/
├── __init__.py
├── conftest.py
├── README.md
└── test_benchmark_smoke.py
```

Additional benchmark files will be added as Sprint 9 progresses.

Planned benchmark areas include:

* plain request lifecycle
* structured response parsing
* structured response repair and retries
* vector similarity search
* RAG orchestration
* workflow execution overhead

---

## Install Benchmark Dependencies

Install the project in editable mode with the benchmark dependency group:

```bash
python -m pip install -e ".[benchmark]"
```

The benchmark dependencies are defined separately from runtime dependencies.

This keeps benchmarking tools out of normal production installations.

---

## Run Normal Tests

Run the standard test suite with:

```bash
python -m pytest
```

Normal pytest discovery is configured to search only:

```text
tests/
```

The `benchmarks/` directory is therefore excluded from normal test execution.

This keeps the standard test suite fast and deterministic.

---

## Confirm Benchmark Isolation

To inspect normal test discovery:

```bash
python -m pytest --collect-only -q
```

Benchmark tests from `benchmarks/` should not appear in the collected tests.

---

## Run All Benchmarks

Run the benchmark suite explicitly:

```bash
python -m pytest benchmarks --benchmark-only
```

This executes only tests that use the `pytest-benchmark` fixture and displays timing statistics.

---

## Run Benchmarks Verbosely

```bash
python -m pytest benchmarks -v
```

This is useful when checking benchmark discovery and test names.

---

## Debug Benchmarks Without Timing Statistics

```bash
python -m pytest benchmarks --benchmark-disable
```

This executes benchmark functions as normal test functions without collecting benchmark statistics.

Use this mode when debugging:

* fake providers
* fixtures
* benchmark setup
* assertions
* request results
* test failures

---

## Run One Benchmark File

```bash
python -m pytest benchmarks/test_benchmark_smoke.py --benchmark-only
```

---

## Run One Benchmark

```bash
python -m pytest benchmarks/test_benchmark_smoke.py::test_benchmark_tooling_is_available --benchmark-only
```

---

## Logging

Toolkit-managed file logging is disabled automatically for benchmark execution.

The benchmark fixture sets:

```env
AI_FILE_LOGGING_ENABLED=false
```

This prevents benchmark runs from:

* creating `logs/ai_toolkit.log`
* writing request metadata to disk
* including file-system logging overhead in measured results
* requiring a writable logging directory

Application-level logging behavior remains unchanged outside benchmark execution.

---

## Benchmark Rules

All benchmarks must follow these rules.

### Deterministic execution

Benchmarks must use deterministic inputs and predictable outputs.

Repeated runs should execute the same logical operation.

### No network calls

Benchmarks must not call:

* OpenAI
* Anthropic
* Google
* local HTTP services
* external APIs
* remote vector databases

Network latency would measure external systems rather than toolkit overhead.

### No real API keys

Benchmarks must not require real provider credentials.

Fake keys may be used only when configuration objects require a non-empty value.

### Use fake providers

Provider behavior must be simulated using deterministic fake providers or fixtures.

Fake providers should return known `ProviderResponse` objects without sleeping or performing I/O.

### No artificial provider latency

Do not use `time.sleep()` or async sleeps to imitate provider calls.

Artificial delays would dominate the benchmark and hide toolkit overhead.

### No toolkit-managed file logging

File logging must remain disabled during benchmark execution.

### Measure one operation at a time

Each benchmark should have a clearly defined scope.

For example:

```text
Good:
Measure structured-response parsing.

Avoid:
Measure configuration loading, provider creation, request execution,
structured parsing, vector search, and file output in one benchmark.
```

### Keep setup outside the measured function

Objects that are not part of the operation being measured should be created before benchmark timing begins.

For example:

```python
provider = FakeProvider()
executor = RequestExecutor(
    provider=provider,
    model="fake-model",
)


def run_request():
    return executor.execute("Hello")


result = benchmark(run_request)
```

Do not repeatedly construct unrelated fixtures inside the measured function unless object construction is the specific benchmark target.

### Preserve correctness assertions

Every benchmark must verify that the measured operation still returns the correct result.

Performance measurements without correctness checks can hide broken implementations.

### Avoid strict timing assertions

Do not write assertions such as:

```python
assert duration < 0.001
```

Execution time varies across:

* operating systems
* Python versions
* processors
* virtual machines
* continuous integration runners
* background system load

Benchmark output should support comparison and profiling, not machine-specific pass/fail thresholds.

---

## Deterministic Fake Providers

Benchmark requests use fake providers from:

```text
benchmarks/fakes.py
```

These providers implement only the behavior required by the benchmarked toolkit component.

They do not:

* access the network
* require provider credentials
* call external APIs
* sleep or simulate model latency
* write files
* generate random responses
* perform application logging

### Synchronous fake provider

`FakeTextProvider` returns one prebuilt `ProviderResponse` for every request.

```python
from benchmarks.fakes import FakeTextProvider


provider = FakeTextProvider(
    response_text="Benchmark response",
)
```

The response object is created before benchmark timing begins. This reduces fake-provider construction overhead inside the measured request lifecycle.

### Asynchronous fake provider

`FakeAsyncTextProvider` provides deterministic async request behavior:

```python
from benchmarks.fakes import FakeAsyncTextProvider


provider = FakeAsyncTextProvider(
    response_text="Benchmark response",
)
```

It performs no asynchronous I/O. The async method exists only to satisfy the asynchronous provider interface.

### Sequence provider

`SequenceTextProvider` returns predefined responses in order:

```python
from benchmarks.fakes import SequenceTextProvider


provider = SequenceTextProvider(
    responses=[
        "Invalid response",
        '{"name": "Valid response"}',
    ]
)
```

This provider is intended for deterministic retry and structured-response repair benchmarks.

It raises an error when all configured responses have been consumed. Unexpected additional provider calls therefore fail visibly instead of silently reusing a response.

### Shared token usage

Benchmark fixtures use deterministic token metadata:

```python
TokenUsage(
    input_tokens=10,
    output_tokens=5,
    total_tokens=15,
)
```

This allows request-result construction and cost calculation to run without depending on provider-generated usage data.

### Benchmark logger

Directly constructed executors receive an isolated logger:

```python
executor = RequestExecutor(
    provider=provider,
    model="benchmark-model",
    logger=benchmark_logger,
)
```

The benchmark logger:

* uses a `NullHandler`
* does not propagate records
* creates no file handler
* performs no console output
* prevents logging I/O from affecting benchmark measurements

The environment fixture also sets:

```env
AI_FILE_LOGGING_ENABLED=false
```

The environment setting protects configuration-loaded clients. Explicit logger injection protects directly constructed executors.

### Correctness tests

Fake-provider correctness tests are stored under:

```text
tests/test_benchmark_fakes.py
```

These tests run as part of the normal test suite.

Benchmark fixture checks are stored under:

```text
benchmarks/test_benchmark_fixtures.py
```

Correctness tests verify the benchmark infrastructure before it is used for performance measurement.

## Plain Request Lifecycle Benchmark

The plain request lifecycle benchmark measures the synchronous internal request path through `RequestExecutor`.

Benchmark file:

```text
benchmarks/test_request_lifecycle.py
```

### What It Measures

The benchmark measures the following operations:

* request ID generation
* synchronous fake-provider invocation
* request duration calculation
* token-cost estimation
* metadata logging through a no-output benchmark logger
* `AIResult` construction

The measured execution path is:

```text
RequestExecutor.execute()
        │
        ▼
Generate request ID
        │
        ▼
Call deterministic fake provider
        │
        ▼
Read response and token usage
        │
        ▼
Calculate duration
        │
        ▼
Estimate request cost
        │
        ▼
Log request metadata through NullHandler
        │
        ▼
Construct AIResult
```

### What It Excludes

The benchmark intentionally excludes:

* network requests
* real model execution
* API authentication
* provider latency
* provider factory construction
* environment-variable loading
* configuration validation
* executor construction
* logger construction
* toolkit-managed file logging
* console logging

These operations are excluded so the benchmark measures the toolkit's internal request lifecycle rather than external provider or setup overhead.

### Deterministic Provider

The benchmark uses `FakeTextProvider`.

The fake provider:

* performs no network calls
* requires no API key
* returns a prebuilt `ProviderResponse`
* returns deterministic token usage
* performs no sleeping or simulated latency
* performs no file access

The response object is created before benchmark timing begins.

### Benchmark Logger

The executor receives the shared `benchmark_logger` fixture:

```python
executor = RequestExecutor(
    provider=fake_text_provider,
    model="benchmark-model",
    logger=benchmark_logger,
)
```

The benchmark logger:

* uses `logging.NullHandler`
* creates no log file
* produces no console output
* does not propagate records to the root logger

The metadata logging call remains part of the request lifecycle, but no logging I/O is performed.

### Benchmark Implementation

```python
from ai.executor import RequestExecutor


def test_plain_request_lifecycle(
    benchmark,
    fake_text_provider,
    benchmark_logger,
):
    executor = RequestExecutor(
        provider=fake_text_provider,
        model="benchmark-model",
        logger=benchmark_logger,
    )

    result = benchmark(
        executor.execute,
        "Benchmark prompt",
    )

    assert result.data == "Benchmark response"
    assert result.raw_response == "Benchmark response"
    assert result.original_raw_response == "Benchmark response"
    assert result.model == "benchmark-model"
    assert result.retries_used == 0
    assert result.request_id
    assert result.duration_ms is not None
    assert result.duration_ms >= 0
    assert result.token_usage is not None
    assert result.token_usage.input_tokens == 10
    assert result.token_usage.output_tokens == 5
    assert result.token_usage.total_tokens == 15
```

Executor construction happens before `benchmark(...)` is called and is therefore excluded from timing.

### Run the Benchmark

Run only the plain request lifecycle benchmark:

```bash
python -m pytest benchmarks/test_request_lifecycle.py --benchmark-only
```

On Windows PowerShell, this may also be written as:

```powershell
python -m pytest benchmarks\test_request_lifecycle.py --benchmark-only
```

### Debug Without Timing Statistics

Run the benchmark as a normal correctness test:

```bash
python -m pytest benchmarks/test_request_lifecycle.py --benchmark-disable -v
```

This mode is useful when debugging:

* fixture loading
* fake-provider behavior
* executor behavior
* returned `AIResult`
* correctness assertions

### Run All Performance Benchmarks

```bash
python -m pytest benchmarks --benchmark-only
```

After BENCH-003, the benchmark table should contain:

```text
test_benchmark_tooling_is_available
test_plain_request_lifecycle
```

Infrastructure-only tests that do not use the `benchmark` fixture are expected to be skipped when `--benchmark-only` is used.

### Correctness Verification

The benchmark verifies the resulting `AIResult` after timing completes.

It confirms:

* the expected response text is returned
* raw and original responses are preserved
* the configured model is recorded
* no retry is reported
* a request ID is generated
* duration metadata is present
* token usage is preserved

These assertions ensure that benchmark results cannot hide broken request behavior.

### Timing Policy

The benchmark does not contain a strict timing assertion.

Do not add checks such as:

```python
assert result.duration_ms < 1
```

Timing varies across:

* processors
* operating systems
* Python versions
* virtual machines
* continuous integration runners
* background system load

The benchmark is intended for profiling and comparison, not machine-specific pass or fail thresholds.

## Benchmark Results

`pytest-benchmark` may store local result files under:

```text
.benchmarks/
```

This directory is different from the source directory:

```text
benchmarks/
```

The source directory contains committed benchmark code:

```text
benchmarks/
```

The generated results directory contains machine-specific measurements:

```text
.benchmarks/
```

Generated benchmark results are ignored by Git because measurements from different machines are not directly comparable.

---

## Structured Response Parsing Benchmark

The structured response parsing benchmark measures conversion of a valid JSON response into a validated Pydantic model.

Benchmark file:

```text
benchmarks/test_structured_parsing.py
```

### What It Measures

The benchmark measures:

* JSON decoding
* Pydantic model validation
* Python model construction
* primitive field validation
* list-field validation

The measured path is:

```text
Valid JSON response
        │
        ▼
parse_structured_response()
        │
        ▼
Decode JSON object
        │
        ▼
Validate fields with Pydantic
        │
        ▼
Construct BenchmarkContact
```

### What It Excludes

The benchmark intentionally excludes:

* structured prompt construction
* AI provider calls
* network access
* model execution
* API credentials
* response repair
* retry execution
* request ID generation
* request duration calculation
* token-cost estimation
* logging
* `AIResult` construction

These operations are measured separately so the result represents structured parsing and validation rather than the complete request lifecycle.

### Benchmark Schema

The benchmark validates the response against:

```python
class BenchmarkContact(BaseModel):
    name: str
    email: str
    age: int
    active: bool
    tags: list[str]
```

This schema includes:

* string fields
* an integer field
* a Boolean field
* a list of strings

It provides a small but representative structured response without adding unrelated model complexity.

### Benchmark Input

The benchmark uses a deterministic valid JSON response:

```json
{
    "name": "Benchmark User",
    "email": "benchmark@example.com",
    "age": 35,
    "active": true,
    "tags": [
        "python",
        "automation",
        "ai"
    ]
}
```

The same response and schema are used for every benchmark iteration.

No random data or provider-generated content is involved.

### Benchmark Implementation

```python
from pydantic import BaseModel

from ai.structured import parse_structured_response


class BenchmarkContact(BaseModel):
    name: str
    email: str
    age: int
    active: bool
    tags: list[str]


STRUCTURED_RESPONSE = """
{
    "name": "Benchmark User",
    "email": "benchmark@example.com",
    "age": 35,
    "active": true,
    "tags": [
        "python",
        "automation",
        "ai"
    ]
}
""".strip()


def test_structured_response_parsing(benchmark):
    result = benchmark(
        parse_structured_response,
        STRUCTURED_RESPONSE,
        BenchmarkContact,
    )

    assert isinstance(result, BenchmarkContact)
    assert result.name == "Benchmark User"
    assert result.email == "benchmark@example.com"
    assert result.age == 35
    assert result.active is True
    assert result.tags == [
        "python",
        "automation",
        "ai",
    ]
```

The schema class and JSON response are defined before timing begins.

The measured operation is only the call to `parse_structured_response()`.

### Run the Benchmark

Run only the structured parsing benchmark:

```bash
python -m pytest benchmarks/test_structured_parsing.py --benchmark-only
```

On Windows PowerShell:

```powershell
python -m pytest benchmarks\test_structured_parsing.py --benchmark-only
```

### Debug Without Timing Statistics

```bash
python -m pytest benchmarks/test_structured_parsing.py --benchmark-disable -v
```

This runs the benchmark as a normal correctness test without collecting timing statistics.

Use this mode when debugging:

* JSON input
* Pydantic schema definitions
* parsing behavior
* validation behavior
* correctness assertions

### Run All Benchmarks

```bash
python -m pytest benchmarks --benchmark-only
```

After BENCH-004, the measured benchmark table should contain:

```text
test_benchmark_tooling_is_available
test_plain_request_lifecycle
test_structured_response_parsing
```

Infrastructure tests that do not use the benchmark fixture remain skipped when `--benchmark-only` is used.

### Correctness Verification

After timing, the benchmark verifies:

* the result is a `BenchmarkContact`
* string fields contain the expected values
* the integer field is correct
* the Boolean field is correct
* the list field contains the expected values

These assertions ensure that performance results cannot hide parsing or validation errors.

### Benchmark Scope

This benchmark represents the successful structured-response path.

It does not measure invalid JSON, schema validation failures, or repair retries.

Invalid-response repair and retry overhead are measured separately by:

```text
BENCH-005 — Retry and Repair Benchmark
```

### Timing Policy

The benchmark does not enforce a fixed maximum duration.

Results may vary depending on:

* Python version
* Pydantic version
* processor
* operating system
* virtual machine environment
* continuous integration hardware
* background system activity

Results should be used for profiling and comparisons under similar conditions, not machine-specific pass or fail thresholds.

## Retry and Repair Benchmark

The retry and repair benchmark measures the synchronous structured-response recovery path through `RequestExecutor`.

Benchmark file:

```text
benchmarks/test_retry_repair.py
```

### What It Measures

The benchmark measures a structured request that receives one invalid response and then successfully repairs it with one retry.

Measured operations include:

* structured prompt construction
* initial deterministic provider invocation
* failed JSON parsing
* JSON parsing error handling
* repair prompt construction
* retry decision logic
* second deterministic provider invocation
* repaired JSON parsing
* Pydantic model validation
* token-usage aggregation
* request duration calculation
* token-cost estimation
* metadata logging through a no-output logger
* `AIResult` construction

The measured execution path is:

```text
RequestExecutor.execute()
        │
        ▼
Build structured prompt
        │
        ▼
Receive invalid response
        │
        ▼
Attempt structured parsing
        │
        ▼
Catch parsing failure
        │
        ▼
Check retry allowance
        │
        ▼
Build JSON repair prompt
        │
        ▼
Receive valid repaired response
        │
        ▼
Parse and validate response
        │
        ▼
Aggregate token usage
        │
        ▼
Construct AIResult
```

### What It Excludes

The benchmark intentionally excludes:

* network access
* real model execution
* API authentication
* provider latency
* provider factory construction
* environment loading
* configuration validation
* toolkit-managed file logging
* console logging
* persistent benchmark result storage

The provider and executor are created by benchmark setup before each measured round.

### Deterministic Responses

The first provider response is intentionally invalid:

```text
This is not valid JSON.
```

The second response is valid:

```json
{
    "name": "Recovered User",
    "age": 35,
    "active": true
}
```

The same two responses are used for every benchmark round.

No random content or provider-generated output is involved.

### Response Schema

The repaired response is validated against:

```python
class RepairedContact(BaseModel):
    name: str
    age: int
    active: bool
```

The benchmark therefore measures both JSON recovery and Pydantic model validation.

### Fresh State Per Round

`SequenceTextProvider` consumes its configured responses in order.

A fresh provider and executor must therefore be created before every measured execution.

The benchmark uses pedantic setup:

```python
def setup():
    provider = make_sequence_text_provider(
        [
            INVALID_RESPONSE,
            VALID_RESPONSE,
        ]
    )

    executor = RequestExecutor(
        provider=provider,
        model="benchmark-model",
        max_retries=1,
        logger=benchmark_logger,
    )

    return (executor,), {}
```

Setup executes outside the measured request function.

Each measured round receives a fresh executor backed by a fresh sequential provider.

The benchmark uses:

```python
rounds=100
iterations=1
```

One iteration is used per round because one request consumes the complete two-response sequence.

### Benchmark Implementation

```python
from pydantic import BaseModel

from ai.executor import RequestExecutor

BENCHMARK_ROUNDS = 100

INVALID_RESPONSE = "This is not valid JSON."

VALID_RESPONSE = """
{
    "name": "Recovered User",
    "age": 35,
    "active": true
}
""".strip()


class RepairedContact(BaseModel):
    name: str
    age: int
    active: bool


def execute_repair_request(
    executor: RequestExecutor,
):
    return executor.execute(
        prompt="Return contact information.",
        response_type=RepairedContact,
    )


def test_structured_response_retry_and_repair(
    benchmark,
    make_sequence_text_provider,
    benchmark_logger,
):
    def setup():
        provider = make_sequence_text_provider(
            [
                INVALID_RESPONSE,
                VALID_RESPONSE,
            ]
        )

        executor = RequestExecutor(
            provider=provider,
            model="benchmark-model",
            max_retries=1,
            logger=benchmark_logger,
        )

        return (executor,), {}

    result = benchmark.pedantic(
        execute_repair_request,
        setup=setup,
        rounds=BENCHMARK_ROUNDS,
        iterations=1,
    )

    assert isinstance(result.data, RepairedContact)
    assert result.data.name == "Recovered User"
    assert result.data.age == 35
    assert result.data.active is True

    assert result.original_raw_response == INVALID_RESPONSE
    assert result.raw_response == VALID_RESPONSE
    assert result.retries_used == 1

    assert result.token_usage is not None
    assert result.token_usage.input_tokens == 20
    assert result.token_usage.output_tokens == 10
    assert result.token_usage.total_tokens == 30

    assert result.request_id
    assert result.duration_ms is not None
    assert result.duration_ms >= 0
```

### Token-Usage Aggregation

Each fake provider response contains:

```text
Input tokens:  10
Output tokens: 5
Total tokens:  15
```

One initial request and one retry therefore produce:

```text
Input tokens:  20
Output tokens: 10
Total tokens:  30
```

The correctness assertions verify this aggregation.

This ensures that the benchmark exercises real retry metadata behavior rather than only parsing the second response.

### Run the Benchmark

Run only the retry and repair benchmark:

```bash
python -m pytest benchmarks/test_retry_repair.py --benchmark-only
```

On Windows PowerShell:

```powershell
python -m pytest benchmarks\test_retry_repair.py --benchmark-only
```

### Debug Without Timing Statistics

```bash
python -m pytest benchmarks/test_retry_repair.py --benchmark-disable -v
```

Use this mode when debugging:

* sequential response order
* structured parsing failures
* repair prompt execution
* retry counts
* token aggregation
* returned model values
* `AIResult` metadata

### Run All Benchmarks

```bash
python -m pytest benchmarks --benchmark-only
```

After BENCH-005, the benchmark table should contain:

```text
test_benchmark_tooling_is_available
test_plain_request_lifecycle
test_structured_response_parsing
test_structured_response_retry_and_repair
```

Infrastructure-only tests remain skipped when `--benchmark-only` is used.

### Correctness Verification

After timing, the benchmark confirms:

* the repaired response becomes a `RepairedContact`
* all structured fields contain the expected values
* the original invalid response is preserved
* the final valid response is preserved
* exactly one retry is recorded
* token usage from both provider calls is combined
* a request ID is generated
* duration metadata is present

These checks ensure that performance results cannot hide broken retry or repair behavior.

### Benchmark Scope

This benchmark measures the successful one-retry recovery path.

It does not measure:

* repeated invalid responses
* retry exhaustion
* terminal parsing failures
* provider exceptions
* exponential backoff
* network retry behavior

Failure paths remain covered by normal correctness tests.

The benchmark suite focuses on stable successful operations rather than using timing results as assertions for exceptional behavior.

### Timing Policy

The benchmark has no fixed maximum-duration assertion.

Its results should be used to:

* compare changes on the same machine
* identify performance regressions
* support profiling
* understand the cost of response repair relative to successful parsing

Results from unrelated machines or environments should not be treated as directly equivalent.

## Vector Search Benchmarks

The vector search benchmarks measure similarity search performance in `InMemoryVectorStore`.

Benchmark file:

```text
benchmarks/test_vector_search.py
```

Two search paths are measured:

* similarity search across all stored records
* similarity search with a metadata filter

### Benchmark Dataset

The benchmark uses:

```text
Records:          1,000
Vector dimensions:   64
Returned results:     5
```

The records are created before benchmark timing begins.

Every record contains:

* a stable ID
* deterministic text
* a deterministic 64-dimensional vector
* source metadata
* group metadata

Example metadata:

```python
{
    "source": "even",
    "group": "0",
}
```

The benchmark performs no embedding requests and does not require an embedding model.

### Deterministic Vectors

Vectors are generated using deterministic arithmetic:

```python
def build_deterministic_vector(
    record_index: int,
) -> list[float]:
    vector = []

    for dimension_index in range(VECTOR_DIMENSIONS):
        value = (
            ((record_index + 1) * (dimension_index + 3)) % 101
        ) / 100.0

        if dimension_index == record_index % VECTOR_DIMENSIONS:
            value += 1.0

        vector.append(value)

    return vector
```

This approach provides stable benchmark data without:

* randomness
* external embedding providers
* API credentials
* network access
* stored fixture files

The same vectors are generated on every benchmark run.

### Dataset Construction

The benchmark dataset is created through a module-scoped fixture:

```python
@pytest.fixture(scope="module")
def vector_search_dataset():
    records = [
        VectorRecord(
            id=f"record-{record_index}",
            text=f"Benchmark document {record_index}",
            vector=build_deterministic_vector(record_index),
            metadata={
                "source": (
                    "even"
                    if record_index % 2 == 0
                    else "odd"
                ),
                "group": str(record_index % 10),
            },
        )
        for record_index in range(RECORD_COUNT)
    ]

    store = InMemoryVectorStore()
    store.add(records)

    query_vector = list(records[TARGET_INDEX].vector)

    return store, query_vector
```

The following operations happen before timing begins:

* deterministic vector generation
* `VectorRecord` construction
* metadata construction
* vector-store construction
* insertion of records into the store
* selection of the query vector

The benchmark therefore measures search, not dataset preparation.

### Unfiltered Similarity Search

The unfiltered benchmark searches across all 1,000 records.

Measured operations include:

* candidate collection
* cosine similarity calculation
* vector dot-product calculation
* vector norm calculation
* `VectorSearchResult` construction
* score sorting
* result limiting

The measured execution path is:

```text
Query vector
        │
        ▼
InMemoryVectorStore.similarity_search()
        │
        ▼
Collect all 1,000 records
        │
        ▼
Calculate cosine similarity for every record
        │
        ▼
Construct VectorSearchResult objects
        │
        ▼
Sort by descending score
        │
        ▼
Return the best five results
```

Benchmark implementation:

```python
def test_vector_similarity_search(
    benchmark,
    vector_search_dataset,
):
    store, query_vector = vector_search_dataset

    results = benchmark(
        store.similarity_search,
        query_vector=query_vector,
        limit=RESULT_LIMIT,
    )

    assert len(results) == RESULT_LIMIT
    assert results[0].id == f"record-{TARGET_INDEX}"
    assert results[0].score == pytest.approx(1.0)
    assert results[0].vector == query_vector

    assert all(
        results[index].score >= results[index + 1].score
        for index in range(len(results) - 1)
    )
```

### Metadata-Filtered Search

The metadata-filtered benchmark searches using:

```python
metadata_filter={"source": "even"}
```

The target record uses the matching `even` source value.

Measured operations include:

* metadata comparison for all stored records
* candidate selection
* cosine similarity calculation for matching records
* `VectorSearchResult` construction
* score sorting
* result limiting

The measured execution path is:

```text
Query vector and metadata filter
        │
        ▼
Check metadata on every stored record
        │
        ▼
Keep records with source="even"
        │
        ▼
Calculate cosine similarity
        │
        ▼
Sort matching results
        │
        ▼
Return the best five results
```

Benchmark implementation:

```python
def test_vector_similarity_search_with_metadata_filter(
    benchmark,
    vector_search_dataset,
):
    store, query_vector = vector_search_dataset

    results = benchmark(
        store.similarity_search,
        query_vector=query_vector,
        limit=RESULT_LIMIT,
        metadata_filter={"source": "even"},
    )

    assert len(results) == RESULT_LIMIT
    assert results[0].id == f"record-{TARGET_INDEX}"
    assert results[0].score == pytest.approx(1.0)

    assert all(
        result.metadata["source"] == "even"
        for result in results
    )

    assert all(
        results[index].score >= results[index + 1].score
        for index in range(len(results) - 1)
    )
```

### What the Benchmarks Exclude

The vector search benchmarks intentionally exclude:

* embedding generation
* provider calls
* API authentication
* network latency
* vector-store construction
* record construction
* adding records to the store
* disk persistence
* database queries
* external vector databases
* file logging
* benchmark result storage

These benchmarks measure only the current in-memory reference implementation.

They should not be interpreted as performance measurements for services such as:

* Pinecone
* Weaviate
* Qdrant
* Chroma
* PostgreSQL with pgvector
* managed cloud vector databases

### Correctness Verification

The unfiltered benchmark verifies:

* exactly five results are returned
* the exact query record ranks first
* the top score is approximately `1.0`
* the returned vector matches the query
* results are ordered by descending score

The metadata-filtered benchmark additionally verifies:

* every returned record matches the requested metadata
* the target record remains ranked first

These assertions ensure that performance measurements cannot hide incorrect ranking or filtering behavior.

### Run Both Vector Search Benchmarks

```bash
python -m pytest benchmarks/test_vector_search.py --benchmark-only
```

On Windows PowerShell:

```powershell
python -m pytest benchmarks\test_vector_search.py --benchmark-only
```

### Debug Without Timing Statistics

```bash
python -m pytest benchmarks/test_vector_search.py --benchmark-disable -v
```

This mode is useful when debugging:

* deterministic vector generation
* record construction
* query-vector selection
* cosine similarity behavior
* result ranking
* metadata filtering
* correctness assertions

### Run All Benchmarks

```bash
python -m pytest benchmarks --benchmark-only
```

After BENCH-006, the benchmark table should contain:

```text
test_benchmark_tooling_is_available
test_plain_request_lifecycle
test_structured_response_parsing
test_structured_response_retry_and_repair
test_vector_similarity_search
test_vector_similarity_search_with_metadata_filter
```

Infrastructure tests that do not use the `benchmark` fixture remain skipped when `--benchmark-only` is used.

### Benchmark Interpretation

The in-memory implementation performs a linear scan.

For an unfiltered search, every stored record is inspected and scored.

As the number of stored records grows, search work also grows because the current implementation does not use an approximate-nearest-neighbor index.

The benchmark provides a Version 1.0 baseline for the reference implementation.

It can later help identify:

* accidental performance regressions
* slower result construction
* slower metadata filtering
* changes in cosine similarity calculations
* changes in sorting overhead

It is not intended to establish a universal maximum search time.

### Timing Policy

No fixed timing threshold is enforced.

Results vary based on:

* processor performance
* Python version
* Pydantic version
* operating system
* memory availability
* continuous integration hardware
* background system activity

Use benchmark results for comparison under similar conditions rather than machine-specific pass or fail rules.

## RAG Orchestration Benchmark

The RAG orchestration benchmark measures the internal coordination performed by `RAGPipeline`.

Benchmark file:

```text
benchmarks/test_rag_orchestration.py
```

RAG means Retrieval-Augmented Generation.

The pipeline:

1. retrieves relevant context,
2. formats that context,
3. builds a grounded prompt,
4. asks the AI client for an answer,
5. returns the answer together with the contexts used.

### Benchmark Scope

The benchmark measures the orchestration layer rather than external retrieval or AI provider performance.

The measured execution path is:

```text
RAGPipeline.ask()
        │
        ▼
Validate question
        │
        ▼
Call deterministic fake retriever
        │
        ▼
Receive five prebuilt contexts
        │
        ▼
Format retrieved context
        │
        ▼
Build grounded RAG prompt
        │
        ▼
Include additional instructions
        │
        ▼
Call deterministic fake AI client
        │
        ▼
Receive prebuilt AIResult
        │
        ▼
Construct RAGResponse
```

### What It Measures

Measured operations include:

* question validation
* retriever method invocation
* retrieved-context formatting
* context numbering and text assembly
* grounded prompt construction
* additional-instruction formatting
* AI client method invocation
* extraction of AI result metadata
* `RAGResponse` construction
* Pydantic validation of the response object

### What It Excludes

The benchmark intentionally excludes:

* embedding generation
* vector similarity search
* database retrieval
* external vector databases
* provider factory construction
* real AI provider requests
* model execution
* API authentication
* network latency
* retry and repair execution
* toolkit-managed file logging
* pipeline construction
* fake retriever construction
* fake AI client construction
* context construction
* AI result construction

Vector search performance is measured separately by the vector search benchmarks.

Provider-independent request execution is measured separately by the plain request lifecycle benchmark.

### Retrieved Contexts

The benchmark uses five deterministic contexts:

```text
django
postgresql
redis
celery
nginx
```

Each context contains:

* a stable ID
* deterministic text
* a deterministic relevance score
* source metadata
* topic metadata

Example:

```python
RetrievedContext(
    id="redis",
    text="Redis can be used for caching and messaging.",
    score=0.91,
    metadata={
        "source": "documentation",
        "topic": "cache",
    },
)
```

The contexts are created before benchmark timing begins.

### Fake Retriever

The benchmark retriever returns the prebuilt contexts without performing retrieval work:

```python
class BenchmarkRetriever:
    def __init__(
        self,
        contexts: list[RetrievedContext],
    ):
        self.contexts = contexts

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedContext]:
        return self.contexts
```

The fake retriever performs no:

* embedding generation
* vector search
* metadata filtering work
* network access
* database access
* file access

The method call remains part of the orchestration benchmark, but actual retrieval performance does not.

### Fake AI Client

The benchmark AI client returns a prebuilt `AIResult`:

```python
class BenchmarkAIClient:
    def __init__(
        self,
        result: AIResult,
    ):
        self.result = result

    def ask(
        self,
        _prompt: str,
    ) -> AIResult:
        return self.result
```

The fake client performs no:

* provider request
* model execution
* API authentication
* retry handling
* network access
* token calculation
* logging

The RAG pipeline still builds and passes the complete prompt to the client method.

### Pipeline Fixture

The pipeline is created before benchmark timing:

```python
@pytest.fixture(scope="module")
def rag_orchestration_pipeline() -> RAGPipeline:
    contexts = [
        RetrievedContext(
            id="django",
            text="Django is a Python web framework.",
            score=0.99,
            metadata={
                "source": "documentation",
                "topic": "web",
            },
        ),
        RetrievedContext(
            id="postgresql",
            text="PostgreSQL is a relational database.",
            score=0.95,
            metadata={
                "source": "documentation",
                "topic": "database",
            },
        ),
        RetrievedContext(
            id="redis",
            text="Redis can be used for caching and messaging.",
            score=0.91,
            metadata={
                "source": "documentation",
                "topic": "cache",
            },
        ),
        RetrievedContext(
            id="celery",
            text="Celery processes background tasks.",
            score=0.87,
            metadata={
                "source": "documentation",
                "topic": "tasks",
            },
        ),
        RetrievedContext(
            id="nginx",
            text="Nginx can proxy requests to a Python application.",
            score=0.82,
            metadata={
                "source": "documentation",
                "topic": "deployment",
            },
        ),
    ]

    ai_result = AIResult(
        data=(
            "Django can provide the web application, PostgreSQL can "
            "store relational data, Redis can support caching and "
            "messaging, Celery can process background tasks, and "
            "Nginx can proxy incoming requests."
        ),
        model="benchmark-model",
        raw_response=(
            "Django can provide the web application, PostgreSQL can "
            "store relational data, Redis can support caching and "
            "messaging, Celery can process background tasks, and "
            "Nginx can proxy incoming requests."
        ),
        original_raw_response=(
            "Django can provide the web application, PostgreSQL can "
            "store relational data, Redis can support caching and "
            "messaging, Celery can process background tasks, and "
            "Nginx can proxy incoming requests."
        ),
        request_id="benchmark-request",
    )

    return RAGPipeline(
        ai_client=BenchmarkAIClient(ai_result),
        retriever=BenchmarkRetriever(contexts),
    )
```

The following setup work is excluded from timing:

* context construction
* `AIResult` construction
* fake retriever construction
* fake AI client construction
* `RAGPipeline` construction

### Benchmark Implementation

```python
def test_rag_orchestration(
    benchmark,
    rag_orchestration_pipeline,
):
    response = benchmark(
        rag_orchestration_pipeline.ask,
        question=QUESTION,
        limit=RESULT_LIMIT,
        metadata_filter={"source": "documentation"},
        instructions=INSTRUCTIONS,
    )

    assert response.answer.startswith(
        "Django can provide the web application"
    )
    assert len(response.contexts) == RESULT_LIMIT
    assert [context.id for context in response.contexts] == [
        "django",
        "postgresql",
        "redis",
        "celery",
        "nginx",
    ]
    assert response.model == "benchmark-model"
    assert response.request_id == "benchmark-request"
    assert response.raw_response == response.answer
```

### Grounded Prompt Construction

The pipeline builds a prompt containing:

* grounding rules
* all retrieved contexts
* the user question
* additional instructions

The benchmark uses:

```text
Question:
Which technologies can support a Python web application?

Additional instructions:
Answer in one concise paragraph.
```

Prompt construction is included in the measured operation because it is part of RAG orchestration.

### Metadata Filter

The benchmark calls the pipeline with:

```python
metadata_filter={
    "source": "documentation",
}
```

The RAG pipeline passes this filter to the retriever.

The fake retriever does not perform filtering because metadata-filter performance belongs to the vector-search benchmark.

This benchmark measures only the orchestration required to pass the filter through the pipeline.

### Correctness Verification

After timing, the benchmark verifies:

* the expected answer is returned
* exactly five contexts are preserved
* contexts remain in the expected order
* the correct model is recorded
* the request ID is preserved
* the raw response matches the returned answer

These assertions ensure that performance measurements cannot hide broken RAG response assembly.

Detailed prompt-content behavior remains covered by normal unit tests in:

```text
tests/test_rag.py
```

### Run the Benchmark

Run only the RAG orchestration benchmark:

```bash
python -m pytest benchmarks/test_rag_orchestration.py --benchmark-only
```

On Windows PowerShell:

```powershell
python -m pytest benchmarks\test_rag_orchestration.py --benchmark-only
```

### Debug Without Timing Statistics

```bash
python -m pytest benchmarks/test_rag_orchestration.py --benchmark-disable -v
```

Use this mode when debugging:

* fake retriever behavior
* context formatting
* prompt construction
* fake AI client behavior
* `RAGResponse` construction
* output assertions

### Run All Benchmarks

```bash
python -m pytest benchmarks --benchmark-only
```

After BENCH-007, the benchmark table should contain:

```text
test_benchmark_tooling_is_available
test_plain_request_lifecycle
test_structured_response_parsing
test_structured_response_retry_and_repair
test_vector_similarity_search
test_vector_similarity_search_with_metadata_filter
test_rag_orchestration
```

Infrastructure-only tests remain skipped when `--benchmark-only` is used.

### Benchmark Interpretation

The benchmark establishes a Version 1.0 performance baseline for RAG orchestration.

It can help detect regressions caused by changes to:

* retrieved-context formatting
* prompt construction
* instruction handling
* metadata-filter forwarding
* AI result processing
* `RAGResponse` construction

It does not indicate how fast a complete production RAG request will be.

Production speed will also depend on:

* embedding provider latency
* vector-store performance
* document count
* network latency
* model response time
* provider availability

### Timing Policy

No fixed duration threshold is enforced.

Use results to compare similar runs on the same or comparable environments.

Do not compare unrelated machines as if their benchmark values were directly equivalent.

## Workflow Execution Benchmarks

The workflow execution benchmarks measure the internal overhead of the sequential `WorkflowEngine`.

Benchmark file:

```text
benchmarks/test_workflow_execution.py
```

Two workflow sizes are measured:

* a one-step workflow representing the minimum successful execution path
* a five-step workflow representing sequential execution with shared state

### Benchmark Scope

The benchmarks measure the workflow engine itself.

They include:

* creation of a fresh `WorkflowContext`
* sequential step invocation
* `WorkflowStepResult` construction
* collection of executed step results
* state updates between steps
* success checks after every step
* `WorkflowRunResult` construction
* final-output access during correctness verification

They exclude:

* workflow-engine construction
* workflow-step construction
* AI provider execution
* network access
* database access
* file access
* asynchronous execution
* workflow retries
* workflow persistence
* branching
* parallel execution
* failure and exception paths

Those excluded capabilities are either covered by normal correctness tests or remain Future Backlog items.

### One-Step Workflow

The one-step benchmark establishes the minimum successful workflow baseline.

Its execution path is:

```text
WorkflowEngine.run()
        │
        ▼
Create WorkflowContext
        │
        ▼
Execute one FunctionWorkflowStep
        │
        ▼
Construct WorkflowStepResult
        │
        ▼
Append step result
        │
        ▼
Apply state update
        │
        ▼
Construct WorkflowRunResult
```

The step reads the initial input value, increments it, and stores the result in workflow state:

```python
def run_single_step(
    context: WorkflowContext,
) -> WorkflowStepResult:
    value = context.input["value"] + 1

    return WorkflowStepResult(
        step_name="single",
        output=value,
        state_updates={
            "value": value,
        },
    )
```

The benchmark starts with:

```python
INPUT_DATA = {
    "value": 5,
}
```

The expected output and final state are:

```text
Output: 6
State:  {"value": 6}
```

Benchmark implementation:

```python
def test_single_step_workflow_execution(
    benchmark,
    single_step_workflow,
):
    result = benchmark(
        single_step_workflow.run,
        input_data=INPUT_DATA,
        metadata=WORKFLOW_METADATA,
    )

    assert result.success is True
    assert len(result.steps) == 1
    assert result.steps[0].step_name == "single"
    assert result.steps[0].output == 6
    assert result.context.state == {
        "value": 6,
    }
    assert result.final_output == 6
```

### Five-Step Workflow

The five-step benchmark measures sequential state propagation across multiple workflow steps.

The workflow contains:

```text
initialize
double
increment
square
finalize
```

Its calculation is:

```text
Initial value: 5
        │
        ▼
Double
        │
        ▼
10
        │
        ▼
Add 3
        │
        ▼
13
        │
        ▼
Square
        │
        ▼
169
```

The final step returns:

```python
{
    "result": 169,
    "source": "benchmark",
}
```

The measured execution path is:

```text
Create WorkflowContext
        │
        ▼
Run initialize step
        │
        ▼
Apply state update
        │
        ▼
Run double step
        │
        ▼
Apply state update
        │
        ▼
Run increment step
        │
        ▼
Apply state update
        │
        ▼
Run square step
        │
        ▼
Apply state update
        │
        ▼
Run finalize step
        │
        ▼
Construct WorkflowRunResult
```

Benchmark implementation:

```python
def test_five_step_workflow_execution(
    benchmark,
    five_step_workflow,
):
    result = benchmark(
        five_step_workflow.run,
        input_data=INPUT_DATA,
        metadata=WORKFLOW_METADATA,
    )

    assert result.success is True
    assert len(result.steps) == 5

    assert [
        step.step_name
        for step in result.steps
    ] == [
        "initialize",
        "double",
        "increment",
        "square",
        "finalize",
    ]

    assert result.context.state == {
        "value": 169,
    }

    assert result.final_output == {
        "result": 169,
        "source": "benchmark",
    }

    assert all(
        step.success
        for step in result.steps
    )
```

### Fresh Context Per Run

`WorkflowEngine.run()` creates a new `WorkflowContext` for every execution.

The same prebuilt workflow engine can therefore be benchmarked repeatedly without reusing state from a previous run.

Each benchmark iteration starts with:

```python
input_data={
    "value": 5,
}
```

and:

```python
metadata={
    "source": "benchmark",
}
```

State created during one workflow run does not carry into the next run.

### Prebuilt Workflow Engines

The workflow engines and `FunctionWorkflowStep` objects are created through module-scoped fixtures before timing begins.

Example:

```python
@pytest.fixture(scope="module")
def five_step_workflow() -> WorkflowEngine:
    return WorkflowEngine(
        steps=[
            FunctionWorkflowStep(
                name="initialize",
                function=initialize_value,
            ),
            FunctionWorkflowStep(
                name="double",
                function=double_value,
            ),
            FunctionWorkflowStep(
                name="increment",
                function=increment_value,
            ),
            FunctionWorkflowStep(
                name="square",
                function=square_value,
            ),
            FunctionWorkflowStep(
                name="finalize",
                function=finalize_value,
            ),
        ]
    )
```

The following operations are excluded from benchmark timing:

* validating workflow step names
* constructing `FunctionWorkflowStep` objects
* constructing the `WorkflowEngine`
* building the workflow step list

This keeps the measurement focused on workflow execution.

### State Propagation

The five-step benchmark exercises the workflow engine's shared-state behavior.

Each successful step may return:

```python
state_updates={
    "value": value,
}
```

The workflow engine applies these updates using:

```python
context.state.update(result.state_updates)
```

The next step then reads the updated value from:

```python
context.state["value"]
```

This means the benchmark includes real state propagation rather than five unrelated function calls.

### Correctness Verification

The one-step benchmark verifies:

* successful workflow completion
* exactly one executed step
* the expected step name
* the expected output
* the expected final state
* the expected final output

The five-step benchmark verifies:

* successful workflow completion
* exactly five executed steps
* correct execution order
* successful status for every step
* the expected final state
* the expected final output
* preservation of workflow metadata

These assertions ensure that performance measurements cannot hide broken workflow behavior.

### Failure Paths

The benchmarks measure successful execution only.

They do not measure:

* a step returning `success=False`
* workflow termination after failure
* exceptions raised by workflow steps
* conversion of exceptions into failed step results
* failed-step state updates

Those behaviors remain covered by normal unit tests in:

```text
tests/test_workflow.py
```

Successful execution provides a more stable performance baseline than exceptional control flow.

### Run Both Workflow Benchmarks

```bash
python -m pytest benchmarks/test_workflow_execution.py --benchmark-only
```

On Windows PowerShell:

```powershell
python -m pytest benchmarks\test_workflow_execution.py --benchmark-only
```

### Debug Without Timing Statistics

```bash
python -m pytest benchmarks/test_workflow_execution.py --benchmark-disable -v
```

Use this mode when debugging:

* workflow fixture construction
* step execution order
* state updates
* workflow metadata
* final output
* correctness assertions

### Run All Benchmarks

```bash
python -m pytest benchmarks --benchmark-only
```

After BENCH-008, the benchmark table should contain:

```text
test_benchmark_tooling_is_available
test_plain_request_lifecycle
test_structured_response_parsing
test_structured_response_retry_and_repair
test_vector_similarity_search
test_vector_similarity_search_with_metadata_filter
test_rag_orchestration
test_single_step_workflow_execution
test_five_step_workflow_execution
```

Infrastructure-only tests remain skipped when `--benchmark-only` is used.

### Benchmark Interpretation

The one-step benchmark provides the minimum workflow execution baseline.

The five-step benchmark provides a representative sequential workflow baseline with shared state.

Comparing them helps show the additional work introduced by:

* more step calls
* more `WorkflowStepResult` objects
* more state updates
* more result-list entries
* additional success checks

The benchmarks can help detect regressions caused by changes to:

* workflow context creation
* sequential execution
* state propagation
* step-result handling
* final workflow-result construction

They do not represent workflows that perform real AI, network, database, or file operations.

### Timing Policy

No fixed execution-time threshold is enforced.

Benchmark timing may vary based on:

* processor
* Python version
* Pydantic version
* operating system
* available memory
* continuous integration hardware
* background system activity

Use results for comparisons under similar conditions rather than machine-specific pass or fail rules.

## Benchmark Suite Completion Review

The initial Python AI Toolkit benchmark suite is complete.

It establishes a deterministic Version 1.0 performance baseline for the toolkit's main internal execution paths.

The suite measures toolkit behavior independently from:

* external AI providers
* model response speed
* network latency
* API authentication
* real embedding generation
* external vector databases
* database access
* file access
* toolkit-managed file logging

The benchmark suite is intended to detect internal performance regressions as the toolkit evolves.

---

## Benchmark Catalog

The suite currently contains nine measured benchmarks.

| Benchmark                    | File                         | Primary Measurement                                        |
| ---------------------------- | ---------------------------- | ---------------------------------------------------------- |
| Benchmark tooling smoke test | `test_benchmark_smoke.py`    | Confirms that benchmark tooling works                      |
| Plain request lifecycle      | `test_request_lifecycle.py`  | Synchronous `RequestExecutor` overhead                     |
| Structured response parsing  | `test_structured_parsing.py` | JSON decoding and Pydantic validation                      |
| Retry and repair lifecycle   | `test_retry_repair.py`       | One failed parse followed by successful repair             |
| Vector similarity search     | `test_vector_search.py`      | Unfiltered in-memory vector ranking                        |
| Filtered vector search       | `test_vector_search.py`      | Metadata filtering and vector ranking                      |
| RAG orchestration            | `test_rag_orchestration.py`  | Context formatting, prompt building, and response assembly |
| One-step workflow            | `test_workflow_execution.py` | Minimum sequential workflow overhead                       |
| Five-step workflow           | `test_workflow_execution.py` | Sequential execution and shared-state propagation          |

The smoke benchmark validates benchmark infrastructure. It should not be interpreted as toolkit application performance.

---

## Measured Toolkit Areas

### Request Execution

The request lifecycle benchmark measures:

* request ID generation
* deterministic provider invocation
* request duration calculation
* token-cost estimation
* metadata logging through a no-output logger
* `AIResult` construction

### Structured Responses

The structured parsing benchmark measures:

* JSON decoding
* schema validation
* Pydantic model construction

The retry and repair benchmark additionally measures:

* parsing failure handling
* repair prompt construction
* retry execution
* repaired-response validation
* token-usage aggregation

### Vector Search

The vector search benchmarks measure:

* metadata filtering
* cosine similarity calculation
* vector dot products and norms
* `VectorSearchResult` construction
* score sorting
* result limiting

The benchmark dataset contains:

```text
1,000 records
64 dimensions per vector
5 returned results
```

### RAG Orchestration

The RAG benchmark measures:

* question validation
* retriever invocation
* context formatting
* grounded prompt construction
* additional-instruction handling
* AI client invocation
* `RAGResponse` construction

Retrieval and provider execution are represented by deterministic no-I/O fakes.

### Workflow Execution

The workflow benchmarks measure:

* workflow context creation
* sequential step execution
* workflow step-result construction
* shared-state updates
* executed-step collection
* workflow result construction

Both a minimum one-step workflow and a representative five-step workflow are included.

---

## Benchmark Infrastructure

Shared benchmark infrastructure is located in:

```text
benchmarks/conftest.py
benchmarks/fakes.py
```

It provides:

* deterministic synchronous provider responses
* deterministic asynchronous provider responses
* sequential retry responses
* deterministic token usage
* prebuilt provider results
* a no-output benchmark logger
* automatic disabling of toolkit-managed file logging

Fake-provider correctness is verified by:

```text
tests/test_benchmark_fakes.py
```

Benchmark fixture correctness is verified by:

```text
benchmarks/test_benchmark_fixtures.py
```

---

## Run the Normal Test Suite

```bash
python -m pytest
```

Normal test discovery is restricted to:

```text
tests/
```

The benchmark suite is therefore excluded from ordinary test execution.

---

## Run All Benchmark-Directory Tests

Run benchmark tests and infrastructure checks:

```bash
python -m pytest benchmarks -v
```

Run all benchmark-directory tests without collecting timing statistics:

```bash
python -m pytest benchmarks --benchmark-disable -v
```

After completion of the initial benchmark suite, this command should normally report:

```text
13 passed
```

This includes:

* nine measured benchmark tests
* four benchmark infrastructure tests

---

## Run Performance Benchmarks Only

```bash
python -m pytest benchmarks --benchmark-only
```

After completion of the initial suite, this command should normally report:

```text
9 passed, 4 skipped
```

The four skipped tests are infrastructure correctness tests that do not use the `benchmark` fixture.

Their exclusion from `--benchmark-only` execution is expected.

---

## Run Individual Benchmark Areas

Plain request lifecycle:

```bash
python -m pytest benchmarks/test_request_lifecycle.py --benchmark-only
```

Structured parsing:

```bash
python -m pytest benchmarks/test_structured_parsing.py --benchmark-only
```

Retry and repair:

```bash
python -m pytest benchmarks/test_retry_repair.py --benchmark-only
```

Vector search:

```bash
python -m pytest benchmarks/test_vector_search.py --benchmark-only
```

RAG orchestration:

```bash
python -m pytest benchmarks/test_rag_orchestration.py --benchmark-only
```

Workflow execution:

```bash
python -m pytest benchmarks/test_workflow_execution.py --benchmark-only
```

---

## Clean Benchmark Verification

Before a clean benchmark run, remove old generated artifacts:

```powershell
if (Test-Path logs) {
    Remove-Item logs -Recurse -Force
}

if (Test-Path .benchmarks) {
    Remove-Item .benchmarks -Recurse -Force
}
```

Run the benchmark suite:

```powershell
python -m pytest benchmarks --benchmark-only
```

Verify that toolkit logging did not create a log directory:

```powershell
Test-Path logs
```

Expected result:

```text
False
```

The `.benchmarks/` directory may be created only when benchmark results are explicitly saved.

---

## API-Key Independence

The benchmark suite must run without real provider credentials.

No benchmark may require:

* `OPENAI_API_KEY`
* Anthropic credentials
* Google credentials
* local model services
* external provider configuration

Fake configuration values may be used only where a non-empty value is structurally required.

---

## Save a Local Baseline

A developer may save machine-specific benchmark results locally:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-save=version-1-baseline
```

Generated results are stored under:

```text
.benchmarks/
```

This directory is excluded from Git.

Saved results are useful for comparisons made on the same or a closely comparable environment.

They should not be committed as universal project performance results.

---

## Compare Local Runs

Save an initial result:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-save=before-change
```

After modifying implementation code, save another result:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-save=after-change
```

Compare them:

```bash
python -m pytest-benchmark compare
```

A comparison is most meaningful when both runs use similar:

* hardware
* operating systems
* Python versions
* dependency versions
* background system conditions

---

## How to Interpret Results

Benchmark results can indicate that a toolkit operation became faster or slower.

They do not automatically explain why.

A meaningful regression should be investigated with profiling before implementation changes are made.

Possible causes include:

* additional object construction
* repeated validation
* unnecessary copying
* slower loops
* additional sorting
* expanded prompt formatting
* logging changes
* dependency-version changes

Small differences between individual runs may be normal measurement noise.

---

## Benchmark Stability Policy

Existing benchmarks should normally remain unchanged when internal implementation is optimized.

This allows the suite to compare the old and new implementations using the same measurement.

A benchmark should be changed only when:

* the public API changes intentionally
* the measured behavior changes intentionally
* the benchmark no longer represents the real execution path
* the benchmark contains an error
* setup work is incorrectly included in timing

New capabilities should usually receive separate benchmarks rather than replacing unrelated existing baselines.

---

## Adding Future Benchmarks

New benchmarks must:

* measure one clearly defined operation
* use deterministic input
* avoid network access
* avoid real API keys
* avoid artificial sleeps
* avoid file and console logging
* keep unrelated setup outside timing
* include correctness assertions
* avoid strict machine-specific timing thresholds
* document what is included and excluded

A future feature does not require every existing benchmark to change.

For example, adding a persistent vector store should normally result in a new persistent-store benchmark while preserving the existing `InMemoryVectorStore` baseline.

---

## Performance Threshold Policy

The benchmark suite does not currently fail builds based on fixed duration thresholds.

Checks such as the following are intentionally avoided:

```python
assert duration < 0.001
```

Fixed thresholds are unreliable across:

* developer laptops
* virtual machines
* operating systems
* supported Python versions
* continuous integration runners
* processors
* background workloads

The initial Version 1.0 benchmark suite provides observational baselines.

Automated regression thresholds may be considered later after enough stable measurement history exists.

---

## Version 1.0 Baseline

This suite represents the initial performance baseline for the path toward Python AI Toolkit Version 1.0.

It covers:

* plain request execution
* structured response parsing
* response repair and retry
* vector similarity search
* metadata-filtered vector search
* RAG orchestration
* minimum workflow execution
* multi-step workflow execution

Live provider and model comparisons are intentionally excluded.

Those remain part of the post-Version-1.0 Future Backlog under:

```text
Automatic model benchmarking
```


## Save Local Benchmark Results

To save a local benchmark run:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-save=baseline
```

The generated data is stored under `.benchmarks/`.

These files are local development artifacts and should not be committed.

---

## Compare Local Benchmark Runs

Create a baseline:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-save=baseline
```

After making a code change, save another run:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-save=updated
```

Compare saved runs:

```bash
python -m pytest-benchmark compare
```

Comparisons are meaningful only when runs use similar:

* hardware
* Python versions
* dependency versions
* operating conditions

---

## Benchmark Configuration

Benchmark defaults are defined in `pyproject.toml`:

```toml
[tool.pytest-benchmark]
disable_gc = false
min_rounds = 5
warmup = false
```

### `disable_gc = false`

Normal Python garbage collection remains enabled.

This more closely represents normal application behavior.

### `min_rounds = 5`

Each benchmark runs for at least five rounds.

This prevents results from being based on a single measurement.

### `warmup = false`

Automatic benchmark warmup is disabled initially.

Warmup behavior may be reconsidered later if profiling shows that it would improve benchmark reliability.

---

## Smoke Benchmark

The initial smoke benchmark verifies that benchmark tooling is installed and working:

```python
def increment(value: int) -> int:
    return value + 1


def test_benchmark_tooling_is_available(benchmark):
    result = benchmark(increment, 1)

    assert result == 2
```

This benchmark does not represent toolkit performance.

It only confirms:

* the benchmark plugin is installed
* the benchmark fixture is available
* benchmark discovery works
* benchmark execution works
* benchmark functions can return values
* correctness assertions still run

---

## Validation Commands

Run the normal test suite:

```bash
python -m pytest
```

Run benchmarks:

```bash
python -m pytest benchmarks --benchmark-only
```

Check benchmark formatting:

```bash
python -m black --check benchmarks
```

Check benchmark linting:

```bash
python -m ruff check benchmarks
```

Confirm that normal test discovery excludes benchmarks:

```bash
python -m pytest --collect-only -q
```

---

## Sprint 9 Benchmark Scope

The benchmark suite is intended to measure internal toolkit performance before Version 1.0.

It does not compare model quality, model intelligence, or provider response speed.

Model and provider comparisons remain part of the post-Version-1.0 Future Backlog under:

```text
Automatic model benchmarking
```
