# Documented Example Verification

## Purpose

This document records the `DOC-014` audit of user-facing examples and commands.
It distinguishes behavior verified without a network from behavior that still
requires a real provider environment.

The audit covers:

- `README.md`
- all focused public guides under `docs/`
- `docs/api_reference.md`
- `examples/README.md`
- numbered example files 01 through 20
- the Base64 image-helper variant
- the command-line workflows

It does not add the new example topics assigned to `PROD-004`.

## Classification

| Classification | Meaning |
| --- | --- |
| Executable | Runs without a provider, network, or external application |
| Provider-dependent | Requires provider behavior; verified with a deterministic substitute |
| Environment-dependent | Requires a particular shell, Python version, framework, server, or credentialed provider |
| Illustrative | Shows output, a signature, a schema fragment, or an intentional failure rather than a standalone workflow |

## Documentation Inventory

The 14 user-facing Markdown files contain 201 fenced blocks.

| Block type | Count | Verification |
| --- | ---: | --- |
| Python | 80 | Executed in document order; intentional failure examples asserted |
| Shell | 41 | Safe commands executed in isolated Linux environments; provider commands substituted |
| PowerShell | 4 | Classified as Windows-dependent and inspected against the corresponding Linux workflow |
| Environment configuration | 8 | Parsed and exercised through configuration and CLI tests |
| TOML | 1 | Matched against `pyproject.toml` |
| Output, signatures, and diagrams | 67 | Compared with current behavior and public contracts |

All repository-relative links in the user-facing documentation resolve.

## Example Files

| Examples | Classification | Verification |
| --- | --- | --- |
| 01–04 | Provider-dependent | Complete `main()` workflows ran with deterministic text and structured responses |
| 05 | Provider-dependent | Streaming chunks were consumed and printed |
| 06 | Provider-dependent | The asynchronous `main()` workflow was awaited |
| 07 | Provider-dependent | Tool definition and returned tool call were exercised without executing the tool |
| 08–09 | Provider-dependent | Plain and structured image requests ran with deterministic image responses |
| 09 Base64 helper | Executable plus provider-dependent | Local JPEG conversion and structured image validation ran |
| 10–14 | Provider-dependent | Embedding, vector search, retrieval, document loading, and RAG workflows ran |
| 15 | Executable | Conversation-memory operations ran without a provider |
| 16–18 | Provider-dependent | Agent, workflow, and multi-agent sequences ran with deterministic responses |
| 19 | Environment- and provider-dependent | Django settings conversion and the service function ran with isolated settings and a fake provider |
| 20 | Environment- and provider-dependent | FastAPI dependency override and endpoint response validation ran through `TestClient` |
| `hello_ai.py` and `drink_recommender.py` | Provider-dependent | Existing unnumbered examples also ran offline |

The permanent regression tests live in:

- `tests/test_examples.py`
- `tests/test_documentation_examples.py`

They prevent numbered modules, gallery references, relative links, Python code
blocks, and deterministic example execution from silently drifting.

## Command Workflows

Verified in isolated CPython 3.12 environments:

- core installation
- Django extra installation
- FastAPI extra installation
- combined development and benchmark installation
- `pip check`
- core, Django, and FastAPI imports
- `ai-toolkit --help`
- `ai-toolkit config show`
- `ai-toolkit config validate`
- deterministic `ai-toolkit ask` behavior through the CLI tests
- Uvicorn's `examples.20_fastapi_integration:app` import target
- normal Pytest execution
- benchmark-only Pytest execution
- Black formatting in a temporary project copy
- Ruff auditing
- package uninstallation in a temporary environment

The Windows PowerShell commands and Python 3.11-specific environment commands
remain environment-dependent. They were not reported as runtime-verified on
this Linux CPython 3.12 host. The release matrix remains responsible for the
declared Python-version set.

## Live Provider Boundary

No live provider request was made during `DOC-014`.

A live smoke test requires:

- a real provider credential
- account and regional access
- a selected model supporting the requested capability
- acceptance of provider cost, retention, and governance implications

Deterministic substitutes prove toolkit control flow and documented return
contracts. They do not prove provider authentication, rate-limit behavior,
network access, or a model's live support for streaming, tools, images, or
embeddings.

## Corrections From Execution

The audit corrected:

- the gallery command from the nonexistent `examples.01_summarize_text` module
  to `examples.01_plain_text`
- the example 01 title so it matches its plain-request behavior
- the Base64 image-helper example so its structured name and grouping match its
  actual structured response
- the async `ask_text()` guide fragment so it is valid inside an async function
- the missing `Document` import in the retrieval guide

No production runtime API, provider adapter, dependency, architectural
decision, benchmark, or public import path changed.

## Known Quality Findings

The documented quality commands are valid, but the repository-wide quality
gate was already not clean:

- Black identifies `profiling/profile_vector_search.py` and
  `tests/test_logger.py` as requiring formatting.
- Ruff reports existing repository-wide findings, including `N999` for the
  numbered example module names.

The Python files added by `DOC-014` pass focused Black and Ruff checks. The
edited `09_1_structured_image_with_helper.py` content passes Ruff when the
pre-existing numbered-module `N999` naming rule is excluded.

Repository-wide cleanup and example naming normalization remain later roadmap
work; they were not mixed into this documentation-verification task.
