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
