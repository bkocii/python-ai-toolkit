# Installation

Python AI Toolkit requires Python 3.11 or newer.

The project is currently installed from a local source checkout. It is not yet
published on PyPI, so commands such as `pip install python-ai-toolkit` are
reserved for the later package-release milestone.

The [compatibility guide](compatibility.md) distinguishes this declared
installation floor from the versions currently verified by the full suite, the
planned Version 1.0 test matrix, dependency compatibility, and live
provider/model availability.

## Package identity

Python packaging uses different names for the distribution, import package,
and terminal command:

| Purpose | Name | Where it is used |
| --- | --- | --- |
| Distribution | `python-ai-toolkit` | `pip` and, after release, PyPI |
| Import package | `ai` | Python imports such as `from ai.client import AIClient` |
| Console command | `ai-toolkit` | Terminal commands such as `ai-toolkit --help` |

The current machine-readable package version is `0.7.0.dev0`. Project
documentation displays the same development line as `0.7.0-dev`;
`0.7.0.dev0` is the normalized Python-package spelling that sorts before a
future final `0.7.0` release.

The author name is recorded in the package metadata. Canonical repository,
documentation, and issue-tracker URLs have not yet been confirmed, so the
metadata intentionally contains no placeholder links.

## PyPI classifiers

Classifiers are standardized labels that package indexes use to categorize a
project. They help a developer understand what the package is before
installing it; they do not install dependencies or change runtime behavior.

The current classifiers describe the toolkit as:

| Area | Classifier meaning |
| --- | --- |
| Maturity | Beta: the main feature set exists, but the Version 1.0 API and release are not yet final |
| Audience | A library intended for developers |
| Interface | A Python library that also supplies a console command |
| Frameworks | Optional Django and FastAPI integrations are implemented |
| Platform | Pure Python code without an operating-system-specific implementation |
| Language | Python 3 only |
| Topics | Artificial intelligence and reusable Python modules |

The metadata intentionally omits individual Python 3.11–3.14 classifiers until
the Version 1.0 CI matrix verifies the intended release range. The
`requires-python = ">=3.11"` field remains the installer-enforced version
boundary.

No license classifier is declared because current packaging standards use
dedicated license metadata instead. The package declares the SPDX expression
`MIT`, and `license-files = ["LICENSE"]` tells build tools to include the
complete legal text in distributions.

## License

Python AI Toolkit uses the permissive MIT License. It permits private,
commercial, and open-source use, modification, and redistribution. Anyone who
copies or distributes the toolkit or a substantial portion of it must preserve
the copyright and license notice.

MIT does not require an application that uses the toolkit to publish its own
source code. It also provides the toolkit without warranty. The complete terms
are in the repository's [`LICENSE`](../LICENSE) file.

The build backend requires `setuptools>=77.0.3` because that is the first
setuptools release supporting the current PEP 639 license expression and
`license-files` metadata used here. This affects package construction only; it
does not add a runtime dependency for toolkit users.

## Create a virtual environment

Run these commands from the project root:

```bash
python -m venv .venv
```

Activate the environment before installing the toolkit:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux or macOS
source .venv/bin/activate
```

Confirm that `python` now points to the virtual environment:

```bash
python -c "import sys; print(sys.executable)"
```

Using `python -m pip` keeps installation tied to that same interpreter.

## Install for normal use

Install the core toolkit from the current source tree:

```bash
python -m pip install .
```

The core installation includes:

- the `ai` Python package
- the built-in OpenAI provider
- Pydantic models and validation
- `.env` file loading
- the `ai-toolkit` command

Django and FastAPI are not installed by the core package.

Verify the installation without making a provider request:

```bash
python -c "from ai.client import AIClient; print('Python AI Toolkit installed')"
ai-toolkit --help
```

Configuration and provider credentials are covered separately in the
[configuration guide](configuration.md). The import and help checks above do
not need an API key or network request.

### Verify the console command on Windows

After activating the virtual environment in PowerShell, confirm that Windows
finds the command inside that environment:

```powershell
Get-Command ai-toolkit
ai-toolkit --help
$LASTEXITCODE
```

`Get-Command` should display a path ending in
`.venv\Scripts\ai-toolkit.exe`. Help should return exit code `0`.

The configuration command can also be tested without contacting OpenAI. The
key and model below are temporary structural-test values, not real
credentials:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "local-structure-check"
$env:OPENAI_MODEL = "test-model"
$env:AI_FILE_LOGGING_ENABLED = "false"

ai-toolkit config validate
$LASTEXITCODE
```

The command should say that the configuration is structurally valid and return
`0`. It does not authenticate the placeholder key or send a model request.

To verify the invalid-command contract, run the command without a subcommand:

```powershell
ai-toolkit
$LASTEXITCODE
```

The usage error is expected, and the exit code should be `2`. Close the
PowerShell window after this check, or remove the temporary variables with:

```powershell
Remove-Item Env:AI_PROVIDER
Remove-Item Env:OPENAI_API_KEY
Remove-Item Env:OPENAI_MODEL
Remove-Item Env:AI_FILE_LOGGING_ENABLED
```

If `Get-Command` cannot find `ai-toolkit`, confirm that the intended virtual
environment is active and rerun `python -m pip install .`. If it finds a
command outside `.venv\Scripts`, a different installation is being executed.

## Optional extras

Extras are additive. Choose only the groups needed by the application or
development workflow.

| Extra | Install command | Adds |
| --- | --- | --- |
| Django | `python -m pip install ".[django]"` | `django>=5.0` |
| FastAPI | `python -m pip install ".[fastapi]"` | `fastapi>=0.100,<1` |
| Development | `python -m pip install -e ".[dev]"` | Pytest, Black, Ruff, both framework extras, and HTTPX2 |
| Benchmark | `python -m pip install -e ".[benchmark]"` | Pytest and pytest-benchmark |

Multiple extras can be installed together:

```bash
python -m pip install ".[django,fastapi]"
```

The development extra intentionally includes `httpx2` for the current FastAPI
test client. The core OpenAI dependency separately installs `httpx`; these are
different packages and should not be substituted for one another.

Installing an extra makes its dependencies available; it does not configure the
framework or provider. Framework-specific configuration, client lifetimes,
testing, and CLI behavior are documented in the
[framework and CLI integration guide](integrations.md) and the existing
[Django](../examples/README.md#19--django-integration) and
[FastAPI](../examples/README.md#20--fastapi-integration) examples.

### Verified installation boundaries

Each installation shape was resolved and checked in a separate clean virtual
environment on CPython 3.12.13:

| Installation | Verified boundary |
| --- | --- |
| Core | The toolkit and CLI import without Django, FastAPI, HTTPX2, Pytest, or pytest-benchmark |
| `django` | The Django adapter imports; FastAPI remains absent |
| `fastapi` | The FastAPI adapter and an application instance import; Django remains absent |
| `dev` | The complete normal test suite, Black, and Ruff run without the benchmark extra |
| `benchmark` | Benchmark fixtures and the pytest-benchmark smoke test run without the development extra |

All five environments passed `python -m pip check`. These checks prove the
current dependency boundaries; they do not configure a provider, make a live
provider request, or replace the planned multi-version release matrix.

## Install for contribution

Contributors should install the project in editable mode so source changes are
used without reinstalling:

```bash
python -m pip install -e ".[dev,benchmark]"
```

This combined installation supports the normal test suite, framework
integration tests, formatting, linting, and performance benchmarks:

```bash
python -m pytest
python -m black --check .
python -m ruff check .
python -m pytest benchmarks --benchmark-only
```

`pyproject.toml` is the authoritative package and optional-dependency
definition. The repository's `requirements.txt` is an environment snapshot; it
is not the supported installation interface and does not replace the extras
above. A fresh dependency resolution can therefore differ from that snapshot;
record the exact resolved versions when diagnosing compatibility.

## Change an existing installation

After changing extras or pulling package-metadata updates, rerun the appropriate
installation command. For example:

```bash
python -m pip install -e ".[dev,benchmark]"
```

To remove the toolkit from the active environment:

```bash
python -m pip uninstall python-ai-toolkit
```

These commands affect only the currently active Python environment.
