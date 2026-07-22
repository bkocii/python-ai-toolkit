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
