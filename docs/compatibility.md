# Compatibility

Python AI Toolkit separates package compatibility from provider and model
availability. A successful installation proves that Python and the resolved
dependencies can load the toolkit; it does not prove that credentials, an
account, a region, a model, or every optional capability is available.

## Compatibility layers

Use the narrowest applicable compatibility claim:

| Layer | What it establishes | What it does not establish |
| --- | --- | --- |
| Python metadata | The installer may select the package for that Python version | That the full suite has run on that version |
| Dependency resolution | A set of package versions can be installed together | That every future dependency release will remain compatible |
| Toolkit adapter | The registered provider implements a toolkit capability | That the configured model supports it |
| Provider SDK | The adapter can call the SDK interface it was written against | That credentials, service access, or quotas are valid |
| Account and region | The provider permits the request in that environment | That the selected model exposes every capability |
| Model capability | A specific model accepts a specific request type | That another model from the same provider behaves identically |

Compatibility failures should be diagnosed at the layer where they occur.
Changing a Python constraint cannot fix an unavailable model, and registering a
provider cannot add a capability its adapter or selected model does not support.

## Python versions

`pyproject.toml` declares:

```toml
requires-python = ">=3.11"
```

This is the authoritative installation floor:

- Python 3.10 and earlier are unsupported and should be rejected by installers.
- Python 3.11 and newer satisfy the current package metadata.
- The planned Version 1.0 continuous-integration matrix is Python 3.11 through
  Python 3.14.
- A newer Python version being accepted by the open-ended metadata is not, by
  itself, evidence that the project has verified that version.

The source intentionally uses Python 3.11-era language and standard-library
features, including `enum.StrEnum`, built-in generic types, and `|` union
annotations. Backports for older Python versions are not part of the current
architecture.

### Declared support versus verification

The current evidence must be read precisely:

| Python | Current status | Evidence |
| --- | --- | --- |
| 3.11 | Declared and planned for Version 1.0 CI | Source parsed with Python 3.11 grammar; runtime suite not run during `DOC-012` |
| 3.12 | Declared and verified | Full `DOC-012` suite on Linux with CPython 3.12.13 |
| 3.13 | Declared and planned for Version 1.0 CI | Not run during `DOC-012` |
| 3.14 | Declared and planned for Version 1.0 CI | Historical deterministic benchmark evidence on Windows with CPython 3.14.4; not the full current suite |

Only CPython environments are currently recorded. The package metadata does not
exclude another Python implementation, but compatibility with PyPy or another
implementation is unverified.

`RELEASE-002 — Test supported Python versions` owns the automated 3.11–3.14
matrix. Until that task is complete, documentation should not describe all four
versions as continuously tested.

## Dependency compatibility

`pyproject.toml` is the supported dependency contract. The repository's
`requirements.txt` is an environment snapshot and is not a lock file or an
installation interface.

| Installation area | Declared constraint | Compatibility boundary |
| --- | --- | --- |
| Core provider SDK | `openai>=1.66.0` | The minimum includes the Responses API used by the built-in adapter; resolved versions must still pass the suite |
| Data models | `pydantic>=2.4.2` | The toolkit uses Pydantic v2 APIs; this floor also provides a Python 3.12 wheel, and resolved versions must pass the suite |
| Environment files | `python-dotenv` | Used only for environment and `.env` loading |
| Django extra | `django>=5.0` | The installed Django release must also support the active Python |
| FastAPI extra | `fastapi>=0.100,<1` | FastAPI, Starlette, Pydantic, and the active Python must resolve compatibly |
| Development extra | Pytest, Black, Ruff, Django, FastAPI, and `httpx2` | Contributor tooling; not part of a core user installation |
| Benchmark extra | Pytest and pytest-benchmark | Performance tooling; not part of runtime use |

The core dependency declarations intentionally allow compatible releases to be
resolved instead of reproducing the development snapshot. Therefore:

- test a clean resolution before release, not only a long-lived virtual
  environment
- record exact resolved versions when reporting a compatibility problem
- add or tighten a constraint only from reproduced incompatibility evidence
- do not infer support for an untested dependency combination from a broad
  version specifier

The `django` and `fastapi` extras are additive. Core installation must continue
to work without importing either framework.

## Verified `DOC-012` environment

The complete documentation-task verification used:

| Component | Version |
| --- | --- |
| Operating environment | Linux 64-bit |
| Python implementation | CPython |
| Python | 3.12.13 |
| OpenAI SDK | 2.48.0 |
| Pydantic | 2.13.4 |
| python-dotenv | 1.2.2 |
| Django | 6.0.7 |
| FastAPI | 0.140.0 |
| HTTPX2 | 2.9.1 |
| Pytest | 9.1.1 |

These versions describe one successful resolution on July 26, 2026. They do
not replace the constraints in `pyproject.toml`, and they do not promise that
only these exact versions work.

## Built-in OpenAI provider

`openai` is the only built-in provider name. `OpenAIProvider` currently maps
toolkit operations to the OpenAI Python SDK:

| Toolkit capability | Adapter behavior |
| --- | --- |
| Synchronous text | `OpenAI.responses.create(...)` |
| Asynchronous text | `AsyncOpenAI.responses.create(...)` |
| Streaming text | Streaming Responses API events |
| Tool calling | Responses API function-tool definitions and returned function calls |
| Image input | Responses API user content with image URLs or Base64 data URLs |
| Embeddings | `OpenAI.embeddings.create(...)` |

This table documents adapter implementation, not universal model support.
Before using a capability in production, verify the selected model and provider
environment support it.

The toolkit does not currently perform a live capability-discovery or preflight
request. Failures such as invalid credentials, unavailable models, unsupported
parameters, account restrictions, regional availability, quotas, and provider
service errors appear when the SDK performs the request and are translated to
`AIProviderError` where the adapter handles them.

The OpenAI SDK also follows standard proxy environment configuration through
its HTTP client. An application that requires a SOCKS proxy must install and
test the HTTP client's optional SOCKS transport support; the toolkit does not
add that deployment-specific extra to every core installation.

Provider documentation and account controls remain authoritative for live
availability. Applications should treat model names and capability assumptions
as deployment configuration, not as permanent toolkit guarantees.

## Custom providers

Registering a custom provider proves only that its class is available under a
process-local name. Compatibility also requires:

1. a constructor compatible with `ProviderFactory`
2. a working `ask_text()` implementation
3. explicit implementations for every optional capability the application uses
4. a provider SDK version compatible with that adapter
5. credentials, account access, regional availability, and a suitable model

The toolkit does not install, constrain, or test third-party SDKs used only by a
custom provider. The application or provider package owns those dependencies
and their compatibility tests.

## Django and FastAPI

Framework compatibility is the intersection of the toolkit's Python range, the
extra's dependency constraint, and the framework release's own Python support.

For Django:

- install `.[django]`
- use Django 5.0 or newer
- let the resolver select a Django release compatible with the active Python
- test the `AI_TOOLKIT` mapping and the sync or async helper used by the
  application

For FastAPI:

- install `.[fastapi]`
- use FastAPI 0.100 or newer and below 1.0
- verify the resolved FastAPI, Starlette, and Pydantic combination
- declare an application-owned ASGI server and test-client dependencies when
  needed

The FastAPI extra does not install Uvicorn or another ASGI server. The
development extra's `httpx2` dependency supports this repository's current
FastAPI endpoint tests; applications own their testing stack.

The adapters do not promise compatibility with every Django or FastAPI plugin,
middleware package, server, deployment platform, or application lifecycle
design.

## Verify another Python version

Use a fresh environment for each Python version and installation shape. A
contributor environment containing every extra can hide an accidental optional
import in the core package.

On Windows, select the interpreter explicitly:

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,benchmark]"
python -m pip check
python -m pytest
python -m pytest benchmarks --benchmark-only
```

Use `py -3.12`, `py -3.13`, or `py -3.14` for the other planned versions.

On Linux or macOS, use the matching interpreter executable:

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,benchmark]"
python -m pip check
python -m pytest
python -m pytest benchmarks --benchmark-only
```

For release-quality compatibility evidence, also use separate clean
environments to verify:

```bash
python -m pip install .
python -c "from ai.client import AIClient; print('core import passed')"
ai-toolkit --help
```

```bash
python -m pip install ".[django]"
python -c "from ai.integrations.django import get_ai_client; print('Django import passed')"
```

```bash
python -m pip install ".[fastapi]"
python -c "from ai.integrations.fastapi import get_ai_client; print('FastAPI import passed')"
```

Package build and wheel/source-distribution checks belong to the later
packaging and release-automation roadmap tasks.

## Live provider smoke tests

Normal compatibility tests use deterministic fakes and must not require API
keys or network access. A live provider smoke test is separate and should:

1. use an explicitly approved test account and secret source
2. record the provider SDK version, configured model, account or project,
   region when relevant, and capability being tested
3. start with a small plain-text request
4. test each advanced capability separately
5. avoid placing credentials or sensitive response content in logs or reports

A successful plain-text request does not verify streaming, tools, images, or
embeddings. Record each result at the capability level.

## Report compatibility problems

Include:

- operating system and architecture
- Python implementation and exact version
- installation command and selected extras
- `python -m pip check` output
- exact direct and relevant transitive dependency versions
- toolkit provider name and provider SDK version
- configured model and requested capability, without credentials
- whether the failure occurs during installation, import, client construction,
  or a live request
- the smallest reproducible traceback or provider error with sensitive data
  removed

This evidence distinguishes a toolkit defect from a resolver, framework, SDK,
account, region, or model-capability problem.

See the [public API reference](api_reference.md) for the exact supported
imports and signatures whose compatibility the release matrix must protect.
