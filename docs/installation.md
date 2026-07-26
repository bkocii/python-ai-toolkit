# Installation

Python AI Toolkit requires Python 3.11 or newer.

The project is currently installed from a local source checkout. It is not yet
published on PyPI, so commands such as `pip install python-ai-toolkit` are
reserved for the later package-release milestone.

The [compatibility guide](compatibility.md) distinguishes this declared
installation floor from the versions currently verified by the full suite, the
planned Version 1.0 test matrix, dependency compatibility, and live
provider/model availability.

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

## Optional extras

Extras are additive. Choose only the groups needed by the application or
development workflow.

| Extra | Install command | Adds |
| --- | --- | --- |
| Django | `python -m pip install ".[django]"` | Django integration dependencies |
| FastAPI | `python -m pip install ".[fastapi]"` | FastAPI integration dependencies |
| Development | `python -m pip install -e ".[dev]"` | Pytest, Black, Ruff, Django, FastAPI, and HTTPX2 |
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
