# Installation

Python AI Toolkit requires Python 3.11 or newer.

The project is currently installed from a local source checkout. It is not yet
published on PyPI, so commands such as `pip install python-ai-toolkit` are
reserved for the later package-release milestone.

The [compatibility guide](compatibility.md) distinguishes this declared
installation floor from the Python 3.11–3.14 versions continuously tested for
Version 1.0, dependency compatibility, and live provider/model availability.

## Package identity

Python packaging uses different names for the distribution, import package,
and terminal command:

| Purpose | Name | Where it is used |
| --- | --- | --- |
| Distribution | `python-ai-toolkit` | `pip` and, after release, PyPI |
| Import package | `ai` | Python imports such as `from ai.client import AIClient` |
| Console command | `ai-toolkit` | Terminal commands such as `ai-toolkit --help` |

The current machine-readable package version is `1.0.0`. The stable API is
frozen, but the release has not yet been tagged or published.

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
| Maturity | Production/Stable: the Version 1.0 public API is frozen |
| Audience | A library intended for developers |
| Interface | A Python library that also supplies a console command |
| Frameworks | Optional Django and FastAPI integrations are implemented |
| Platform | Pure Python code without an operating-system-specific implementation |
| Language | Python 3 only; versions 3.11 through 3.14 are tested |
| Topics | Artificial intelligence and reusable Python modules |

The metadata includes individual Python 3.11–3.14 classifiers because the
Version 1.0 CI matrix now tests the complete range. The
`requires-python = ">=3.11"` field remains the installer-enforced version
boundary; accepting a newer version is not the same as having tested it.

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
provider request, or replace the independent Python-version CI jobs.

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

## Build distributions locally

A package build converts the source checkout into two standard files:

| Format | Purpose |
| --- | --- |
| Wheel (`.whl`) | Ready-to-install pure-Python package used by `pip` |
| Source distribution (`.tar.gz`) | Source and build metadata from which a wheel can be rebuilt |

Install the standard build frontend in the active development environment:

```powershell
python -m pip install build
```

On Windows PowerShell, remove only older generated package output before a
release build:

```powershell
Remove-Item build, dist -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Directory -Filter "*.egg-info" |
    Remove-Item -Recurse -Force
```

Then build both formats from the project root:

```powershell
python -m build
Get-ChildItem dist
```

For version `1.0.0`, the expected filenames are:

```text
python_ai_toolkit-1.0.0-py3-none-any.whl
python_ai_toolkit-1.0.0.tar.gz
```

The `py3-none-any` wheel tag means that the wheel contains pure Python and is
not restricted to one operating system or CPU architecture. The build frontend
reads `pyproject.toml`, creates an isolated build environment, asks setuptools
to construct the source distribution, and then builds the wheel from that
source distribution.

### Build distributions in CI

Every push and pull request runs the supported Python quality matrix first.
Only after all four Python jobs succeed, the `Build distributions` job runs
`python -m build` from the checked-out source. It then validates the exact
built files with:

```text
python -m twine check --strict dist/*
python scripts/validate_distributions.py
```

Only after both validation commands pass does the job upload:

```text
dist/*.whl
dist/*.tar.gz
```

The files are retained together under the GitHub Actions artifact name
`python-package-distributions`. They can be downloaded from the completed
workflow run's summary page.

This job has read-only repository access and does not publish anything. A
failed build, Twine check, or archive check prevents artifact upload.

### Rehearse or publish with the release workflow

The separate `.github/workflows/release.yml` workflow supports two events:

- a manual non-production rehearsal from a selected commit
- a real release when a tag matching `v*.*.*` is pushed

Both paths compare a tag-shaped release identity with the authoritative package
version in `pyproject.toml`. The values must match exactly:

```text
pyproject.toml version 1.0.0
required tag          v1.0.0
```

Before creating a tag, run the same validation locally:

```powershell
python scripts\validate_release_tag.py v1.0.0
```

After the identity gate passes, both paths:

1. check out the exact selected commit by its GitHub event SHA
2. repeats dependency, Black, Ruff, and test checks on Python 3.11–3.14
3. builds the wheel and source distribution from that same commit
4. runs strict Twine and offline archive validation
5. retains both files under an artifact name containing the tag

For a manual rehearsal, the final publishing job is skipped. The input
`v1.0.0` is only a validated label: it creates no Git tag and cannot enter
the protected `pypi` environment. Follow the
[non-production rehearsal](releasing.md#non-production-workflow-rehearsal) and
verify that all four matrix jobs plus the build pass while publication is
reported as skipped.

For a real tag push, the validated files pass to an isolated PyPI publishing
job. The validation jobs have read-only repository permission and do not
persist checkout credentials. Only the final publishing job receives
`id-token: write`, which lets PyPI exchange the workflow identity for a
short-lived project-scoped token. That job does not check out source, install
Python, execute project code, or rebuild artifacts. It creates no GitHub
Release and uses no stored PyPI password or API token.

### Configure trusted PyPI publishing

The workflow source is configured, but PyPI and GitHub each require one
account-side setup before the first real release.

In the GitHub repository:

1. Open **Settings → Environments**.
2. Create an environment named exactly `pypi`.
3. Add a required reviewer when that protection is available for the
   repository.

In PyPI, sign in and open the account **Publishing** page. If the project does
not exist yet, add a pending GitHub publisher with these exact values:

| Field | Value |
| --- | --- |
| PyPI project name | `python-ai-toolkit` |
| GitHub owner | `bkocii` |
| GitHub repository | `python-ai-toolkit` |
| Workflow filename | `release.yml` |
| Environment name | `pypi` |

If the PyPI project already exists, add the same values from that project's
**Manage → Publishing** page instead. The environment name, repository owner,
repository name, and workflow filename must match exactly on both services.

A pending publisher does not reserve the package name. It becomes a normal
publisher after the first successful upload. Do not add `PYPI_API_TOKEN`,
`password`, or username inputs to the workflow: trusted publishing creates a
short-lived credential only when the protected publishing job runs.

Complete account setup is only the prerequisite. The
[release procedure](releasing.md) covers the maintainer preflight, version
change, tag creation, protected approval, PyPI smoke test, and failure recovery.
Do not create a production tag until that checklist and the roadmap-authorized
rehearsal are complete.

The generated `build/`, `dist/`, and `*.egg-info/` paths are ignored because
they are reproducible outputs rather than source files. Do not upload these
development artifacts to PyPI. Building proves that both files can be created;
the validation gates check their metadata, rendered README, and archive
contents before CI retains them. Clean-environment installation behavior
remains a separate release check.

If an `*.egg-info/` directory was committed before the ignore rule was added,
the ignore rule does not remove it from Git automatically. Check and untrack it
once from the project root:

```powershell
git ls-files python_ai_toolkit.egg-info
git rm -r --cached python_ai_toolkit.egg-info
git commit -m "chore: stop tracking generated package metadata"
```

The first command prints nothing when the directory is already untracked. The
local directory may also be deleted safely; setuptools recreates it during a
build or editable installation.

Keep the wheel and source distribution together in the local `dist\` directory
while validating them. They are ignored build outputs, not normal Git source
files. A later release process uploads the final validated files to the package
index or attaches them to a release.

### Validate both distributions on Windows

Install Twine in the active build environment, then run its strict metadata and
long-description check:

```powershell
python -m pip install twine
python -m twine check --strict dist\*
```

Both files must report `PASSED`. Then run the repository's offline archive
validator:

```powershell
python scripts\validate_distributions.py
```

The validator does not install or execute toolkit code. It checks:

* safe, normalized archive paths with no links or special filesystem entries
* exact agreement between packaged `ai` modules and the reviewed source
* source-distribution coverage for tests and required project files
* matching wheel and source metadata, dependencies, extras, README, and license
* the `ai-toolkit` console entry point and `py3-none-any` wheel tag
* every file size and SHA-256 digest recorded by the wheel
* absence of secrets, caches, compiled Python, logs, and nested build output

It prints the final archive SHA-256 hashes so the exact validated files can be
identified later. This validates archive construction only. Installation and
imports from each artifact must still be tested in a clean virtual environment.

The README comparison treats Windows `CRLF` and Unix `LF` line endings as the
same text. This is necessary because package metadata may serialize line
endings differently from a Windows checkout. Every character other than those
line-ending forms must still match.

Twine proves that the long description is valid, renderable Markdown; it does
not visit link destinations. The current README intentionally uses
repository-relative documentation links, while the canonical public repository
URL is still unconfirmed. Before publishing Version 1.0 to PyPI, configure the
confirmed project URLs and convert or otherwise verify those links for the PyPI
page rather than inventing placeholder destinations during local validation.

### Test each artifact in a clean Windows environment

Run these commands from the project root after rebuilding and validating
`dist\`. The environments are created beside the source checkout so importing
from the project directory cannot hide a missing packaged module:

```powershell
$projectRoot = (Get-Location).Path
$testRoot = Join-Path (Split-Path $projectRoot) "python-ai-toolkit-package008"
$wheel = (Resolve-Path "dist\*.whl").Path
$sdist = (Resolve-Path "dist\*.tar.gz").Path

Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item $testRoot -ItemType Directory | Out-Null

py -m venv "$testRoot\wheel-env"
py -m venv "$testRoot\sdist-env"

& "$testRoot\wheel-env\Scripts\python.exe" -m pip install $wheel
& "$testRoot\sdist-env\Scripts\python.exe" -m pip install $sdist
```

For each environment, work from the temporary directory and verify that the
installed distribution is used:

```powershell
Push-Location $testRoot

& "$testRoot\wheel-env\Scripts\python.exe" -c `
    "from pathlib import Path; import ai.client; print(Path(ai.client.__file__).resolve())"
& "$testRoot\wheel-env\Scripts\python.exe" -c `
    "from importlib.metadata import version; from ai.prompts import PromptTemplate; assert version('python-ai-toolkit') == '1.0.0'; assert PromptTemplate('Hello {name}').render(name='Burim') == 'Hello Burim'; print('wheel smoke: PASSED')"
& "$testRoot\wheel-env\Scripts\ai-toolkit.exe" --help
& "$testRoot\wheel-env\Scripts\python.exe" -m pip check

& "$testRoot\sdist-env\Scripts\python.exe" -c `
    "from pathlib import Path; import ai.client; print(Path(ai.client.__file__).resolve())"
& "$testRoot\sdist-env\Scripts\python.exe" -c `
    "from importlib.metadata import version; from ai.prompts import PromptTemplate; assert version('python-ai-toolkit') == '1.0.0'; assert PromptTemplate('Hello {name}').render(name='Burim') == 'Hello Burim'; print('source smoke: PASSED')"
& "$testRoot\sdist-env\Scripts\ai-toolkit.exe" --help
& "$testRoot\sdist-env\Scripts\python.exe" -m pip check

Pop-Location
```

Both printed module paths must be inside their environment's
`Lib\site-packages\ai\` directory, not the project checkout. `pip check` must
report `No broken requirements found`. The environments can be deleted after
the check.

### Test the core installation without frameworks on Windows

This release check is narrower than installing both artifact formats. It
installs only the wheel without extras and proves that the core dependency
boundary remains valid.

Run from the project root after building and validating `dist\`:

```powershell
$projectRoot = (Get-Location).Path
$testRoot = Join-Path (Split-Path $projectRoot) "python-ai-toolkit-package009"
$wheel = (Resolve-Path "dist\*.whl").Path

Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue
py -m venv "$testRoot\core-env"

& "$testRoot\core-env\Scripts\python.exe" -m pip install $wheel

Push-Location $testRoot
& "$testRoot\core-env\Scripts\python.exe" `
    "$projectRoot\scripts\verify_core_installation.py"
& "$testRoot\core-env\Scripts\python.exe" -m pip check
& "$testRoot\core-env\Scripts\python.exe" -m pip list
Pop-Location
```

The verifier must report:

```text
Core installation verification: PASSED
Optional frameworks absent: django, fastapi
Core modules imported: 35
Offline prompt and vector-store checks: PASSED
Offline plain and structured client requests: PASSED
```

The printed import path must be inside
`core-env\Lib\site-packages\ai\`, and `pip check` must report no broken
requirements. `pip list` may include `httpx`, because it is a dependency of the
core OpenAI SDK. It must not include Django or FastAPI.

The wheel includes the toolkit's optional adapter source code so one
distribution supports every extra. Importing
`ai.integrations.django` or `ai.integrations.fastapi` without the corresponding
extra is not a supported core operation. Normal core modules must remain
importable without either framework; the verifier checks every one. It also
registers a deterministic local provider and exercises installed plain and
structured `AIClient` requests without credentials or network access.

### Test the framework extras separately on Windows

This release check installs each optional framework into its own environment.
It proves that selecting one extra does not silently install the other and that
the installed adapter can construct a toolkit client and complete an offline
request.

Run from the project root after building and validating `dist\`:

```powershell
$projectRoot = (Get-Location).Path
$testRoot = Join-Path (Split-Path $projectRoot) "python-ai-toolkit-package010"
$wheel = (Resolve-Path "dist\*.whl").Path

Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue
py -m venv "$testRoot\django-env"
py -m venv "$testRoot\fastapi-env"

& "$testRoot\django-env\Scripts\python.exe" -m pip install "${wheel}[django]"
& "$testRoot\fastapi-env\Scripts\python.exe" -m pip install "${wheel}[fastapi]"

Push-Location $testRoot
& "$testRoot\django-env\Scripts\python.exe" `
    "$projectRoot\scripts\verify_framework_extra_installation.py" django
& "$testRoot\django-env\Scripts\python.exe" -m pip check

& "$testRoot\fastapi-env\Scripts\python.exe" `
    "$projectRoot\scripts\verify_framework_extra_installation.py" fastapi
& "$testRoot\fastapi-env\Scripts\python.exe" -m pip check
Pop-Location
```

Expected output includes:

```text
Django extra verification: PASSED
Unselected framework absent: fastapi
Offline integration behavior: PASSED

FastAPI extra verification: PASSED
Unselected framework absent: django
Offline integration behavior: PASSED
```

Both toolkit paths must resolve inside the corresponding environment's
`Lib\site-packages\ai\` directory, and both dependency checks must report no
broken requirements.

The FastAPI runtime extra does not include a test-client dependency. Application
testing belongs to the `dev` extra, which includes `httpx2`; the runtime verifier
checks the dependency aliases, route registration, and client construction
without expanding the supported `[fastapi]` installation.

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
