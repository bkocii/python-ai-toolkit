# Performance Profiling Report

## Scope

This report closes `PROD-002 — Performance Profiling` for Python AI Toolkit
`0.7.0-dev`.

The profiling work measured the toolkit's internal overhead for:

* plain synchronous request execution
* structured prompt construction and response parsing
* one-retry structured-response repair
* in-memory vector similarity search
* Retrieval-Augmented Generation (RAG) orchestration
* one-step and five-step workflow execution

Provider latency, model execution, network access, real embedding generation,
external vector databases, application business logic, and file logging were
excluded. Those operations would hide the toolkit costs that this work was
designed to examine.

---

## Method

The profiling process used the completed deterministic benchmark suite as its
starting point:

1. Capture a local benchmark baseline.
2. Rank the slowest benchmarked paths.
3. Profile one execution path at a time with `cProfile`.
4. Create providers, responses, datasets, loggers, and other unrelated inputs
   before the measured operation.
5. Separate component measurements from complete lifecycle measurements.
6. Identify contributors by cumulative time and representative absolute cost.
7. Review correctness, public API, maintenance, and architectural tradeoffs
   before approving an optimization.
8. Re-run the unchanged benchmark scenario before and after every accepted
   optimization.

All scenarios used deterministic local fakes or in-memory data. They required
no API keys, made no network calls, and performed no real provider or model
execution. Toolkit-managed file logging remained disabled.

Percentages from `cProfile` show where time was spent within a scenario. They
do not replace `pytest-benchmark` measurements, because profiler
instrumentation adds overhead. Optimization decisions therefore considered
both relative profile contribution and absolute benchmark time.

---

## Environments

### Initial local benchmark baseline

* Windows 11, 64-bit
* CPython 3.14.4
* 11th Gen Intel Core i5-1135G7
* 8 logical processors
* benchmark commit: `91fed29585de55836b640798c754434d3c7f8733`
* working tree: dirty

The dirty working tree is retained as a limitation of the original baseline.
It must not be presented as a release-quality clean-tree measurement.

### Focused structured, RAG, and workflow profiling

* Linux 64-bit
* CPython 3.12.13
* Pydantic 2.13.4
* deterministic local inputs and fakes

Vector profiling used 1,000 in-memory records with 64 dimensions, a result
limit of five, and 100 repeated searches. Scaling checks covered 100 through
5,000 stored records.

Results captured on different operating systems, Python versions, hardware, or
dependency versions are not directly comparable. Cross-environment values in
this report describe each path and support prioritization; accepted
before-and-after percentages come from repeated comparable scenarios.

---

## Measured Bottlenecks

| Path | Main contributor | Representative evidence | Decision |
| --- | --- | --- | --- |
| Plain request | Repeated configuration resolution during cost estimation | Initial request mean `27.292 µs`; configuration and environment access appeared on every request | Optimize |
| Structured success | Repeated Pydantic JSON-schema generation | Prompt construction represented about `89.1%` of profiled executor time; parsing median `2.544 µs` | Do not cache |
| One-retry repair | Schema generation plus required retry work | Prompt construction represented about `86.7%`; focused median `99.838 µs` | Preserve behavior |
| Vector search | Per-candidate cosine calculation | Initial unfiltered search mean `18.984 ms`; cosine work dominated the profile | Optimize |
| RAG orchestration | Retrieved-context formatting | About `64%` of profiled orchestration; focused median `5.268 µs` | No change |
| Workflow execution | Pydantic model construction and validation | One-step median `2.839 µs`; five-step median `7.367 µs` | No change |

The table deliberately combines relative and absolute evidence. Context
formatting dominates the RAG path, for example, but the whole path costs only a
few microseconds. A large percentage of a tiny operation is not automatically
a worthwhile optimization.

---

## Approved Optimizations

### Request pricing and logging

The plain request lifecycle previously resolved the complete `AIConfig` during
cost estimation for every request. For 100,000 profiled requests this caused
100,000 configuration resolutions and approximately 1.1 million
environment-variable lookups.

The accepted changes:

* separate pricing resolution from request-time arithmetic
* resolve prices when an executor is constructed
* pass custom prices from synchronous and asynchronous clients
* retain `estimate_cost_usd()` as a compatibility wrapper
* skip INFO metadata serialization when INFO logging is disabled
* preserve full request logging when INFO logging is enabled

Comparable benchmark result:

| Metric | Before | After | Change |
| --- | ---: | ---: | ---: |
| Mean request overhead | `27.292 µs` | `4.551 µs` | `83.3%` lower |
| Median request overhead | `25.800 µs` | `4.400 µs` | `82.9%` lower |
| Throughput | `36,640 ops/s` | `219,756 ops/s` | about `6×` higher |

The profile time for 100,000 requests fell from approximately `11.443` seconds
to `4.153` seconds, a reduction of approximately `63.7%`.

### In-memory vector search

The original cosine implementation recalculated the query-vector norm for
every candidate and used three generator-based passes per comparison.

The accepted changes:

* calculate the query-vector norm once per search
* calculate each candidate dot product and squared norm in one direct loop
* preserve the public vector-store API
* preserve the existing private two-vector cosine helper
* avoid persistent stored-vector norm caching while vectors remain mutable

Comparable benchmark result:

| Path | Before mean | Average optimized mean | Improvement |
| --- | ---: | ---: | ---: |
| Unfiltered vector search | `18.984 ms` | `12.363 ms` | `34.9%` |
| Metadata-filtered search | `10.875 ms` | `6.574 ms` | `39.5%` |

Both search paths still scale linearly with stored-record count. The scaling
profile estimated approximately `8.2513 ms` per 1,000 scanned records for
unfiltered search and `4.5470 ms` per 1,000 scanned records for the test's
approximately half-matching metadata filter.

---

## Rejected Optimizations

### Structured-schema caching

Repeated Pydantic JSON-schema generation costs approximately `0.4 ms` per
structured prompt under `cProfile` and is the largest remaining removable
repeat cost.

Caching was rejected because a cache keyed only by model class can become stale
after Pydantic `model_rebuild()`. Automatic invalidation would couple the
toolkit to Pydantic internals; explicit invalidation would add public API and
caller responsibility. That correctness and maintenance cost is not justified
for request paths normally dominated by provider execution.

### Additional vector-search changes

The following were rejected:

* a top-k heap, because sorting was a negligible contributor
* bypassing Pydantic result validation, because it would weaken typed results
* persistent stored-vector norm caching, because mutable vectors could make
  cached values stale
* an external numerical dependency for a reference implementation intended for
  tests, examples, and small local datasets

Larger vector workloads require a different indexing or storage architecture,
not another local loop micro-optimization.

### Retry, RAG, and workflow shortcuts

Retry validation, configured repair behavior, provider invocation, token
aggregation, and result semantics were preserved.

RAG formatting and workflow model construction were not changed because their
complete measured overhead is already in the low-microsecond range. Bypassing
Pydantic validation or complicating formatting would trade away clear typed
contracts for negligible absolute savings.

### Observability removal

Request IDs and configurable success logging were retained. They are production
observability features, and their remaining cost is small. Applications that
disable INFO logging already use the guarded low-overhead path.

---

## Remaining Performance Risks

* `InMemoryVectorStore` performs an intentional linear scan. Latency and memory
  use will grow with record count, so it is not intended to replace a
  production vector index at large scale.
* Structured prompt construction still regenerates a Pydantic JSON schema for
  each request. This is an accepted tradeoff until a safe invalidation design
  exists.
* Benchmark and profile values can change with Python, Pydantic, operating
  system, processor, and background load.
* The original Windows baseline came from a dirty working tree.
* The suite uses observational baselines and does not yet enforce automatic
  performance-regression thresholds.
* Deterministic microbenchmarks exclude provider, network, embedding, database,
  and application latency. They describe toolkit overhead, not end-to-end
  production response time.
* Enabled INFO logging intentionally costs more than the disabled-INFO path.

These risks are documented constraints, not hidden failures. Future work should
start with new measurements rather than assuming that the current ranking
remains unchanged.

---

## Reproducing the Measurements

Install benchmark dependencies:

```bash
python -m pip install -e ".[dev,benchmark]"
```

Run normal correctness tests:

```bash
python -m pytest
```

Run benchmark-directory correctness checks without timing:

```bash
python -m pytest benchmarks --benchmark-disable -v
```

Run the timed suite:

```bash
python -m pytest benchmarks --benchmark-only
```

Run the profiling instruments:

```bash
python -m profiling.profile_request_lifecycle
python -m profiling.profile_structured_execution
python -m profiling.profile_vector_search
python -m profiling.profile_vector_scaling
python -m profiling.profile_rag_orchestration
python -m profiling.profile_workflow_execution
```

The benchmark source files and stable operating instructions belong under
`benchmarks/`. Generated JSON results and text profiles belong under
`.benchmarks/`, which is ignored by Git.

---

## Completion Verification

The transferred project copy was verified on Linux with CPython 3.12.13:

```text
269 normal tests passed
13 benchmark-directory correctness checks passed
9 timed benchmarks passed, 4 infrastructure-only tests skipped
benchmark execution did not create a logs/ directory
```

Repository-wide quality checks were also run:

* Black 26.5.1 reported two pre-existing files that would be reformatted:
  `profiling/profile_vector_search.py` and `tests/test_logger.py`.
* Ruff 0.16.0 reported 62 pre-existing findings across runtime, test,
  benchmark, and intentionally numbered example files.

`PROF-009` changed no Python implementation or test file. These existing
repository-wide findings were not silently combined with the
profiling-documentation commit. They remain a release-quality task, along with
pinning or constraining quality-tool versions so that the expected rules do not
change unexpectedly between environments.

---

## Conclusion

The profiling work found and fixed two meaningful low-risk bottlenecks:
request-time configuration resolution and repeated query-norm calculation
during vector search.

The remaining costs are dependency-dominated, required for correctness or
observability, inherent to the reference architecture, or negligible in
absolute terms. No public API change or architecture decision record was
required.
