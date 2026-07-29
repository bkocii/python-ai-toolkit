# Release Procedure

This guide is the maintainer checklist for publishing Python AI Toolkit. It
describes the current automated path from an approved source commit to PyPI.
It does not replace the [roadmap](development/roadmap.md), which decides when a
release should happen and which version should be released.

The current workflow is intentionally simple:

```text
approved release commit
        ↓
exact version tag
        ↓
Python 3.11–3.14 checks
        ↓
wheel and source build
        ↓
Twine and archive validation
        ↓
protected PyPI approval
        ↓
trusted publication
        ↓
clean installation smoke test
```

Pushing a matching version tag starts this process. An ordinary branch push or
pull request cannot publish.

## Important release boundary

Do not create or push a version tag merely to test the workflow. Follow the
active roadmap task and complete the non-production rehearsal before the first
real release.

Before a tag is pushed, release preparation is reversible. After a tag is
pushed, treat that tag as immutable. After a file is published to PyPI, its
filename cannot be reused; a correction requires a new package version.

The automated workflow:

- publishes from `.github/workflows/release.yml`
- accepts tags matching `v*.*.*`
- accepts a manual rehearsal with a tag-shaped label but creates no Git tag
- requires the tag to equal `v` plus the version in `pyproject.toml`
- rebuilds from the exact selected commit
- publishes no GitHub Release
- uses no stored PyPI API token or password

## Non-production workflow rehearsal

Run this rehearsal after the rehearsal support is present on the repository's
default branch and before the first real release:

1. Open the repository's **Actions** tab.
2. Select **Release candidate**.
3. Select **Run workflow**.
4. Select the reviewed `main` branch.
5. Enter a rehearsal label that exactly matches the current package version:

   ```text
   v0.7.0.dev0
   ```

6. Select **Run workflow**.

The label is input to the existing release-tag validator. It does not create or
push a Git tag. The run must show:

- **Validate release identity** — passed
- **Tests (Python 3.11)** — passed
- **Tests (Python 3.12)** — passed
- **Tests (Python 3.13)** — passed
- **Tests (Python 3.14)** — passed
- **Build release distributions** — passed
- **Publish distributions to PyPI** — skipped

Download `python-package-distributions-v0.7.0.dev0` from the run summary and
confirm that it contains exactly one wheel and one source distribution. The
build job has already run strict Twine validation and the offline archive
validator against those exact files.

The skipped publishing job is the critical result. Manual runs cannot satisfy
the job's tag-push condition, so they do not enter the `pypi` environment,
request an OIDC identity token, or contact PyPI. Do not approve a deployment:
a rehearsal should not create one.

The rehearsal creates no tag, PyPI project, package version, GitHub Release, or
stored credential. Its temporary workflow artifact can expire normally or be
deleted from the run after inspection.

This proves the GitHub-hosted quality, build, validation, artifact, and
event-gating path. It intentionally does not prove the PyPI trusted-publisher
identity or upload, because invoking those production capabilities would defeat
the rehearsal's safety goal. Those checks remain part of the first
roadmap-authorized release.

## One-time account setup

Complete this setup once before the first real release. The non-production
rehearsal above does not require it because its publishing job is skipped.

### GitHub environment

In repository **Settings → Environments**:

1. Create an environment named exactly `pypi`.
2. Add a required reviewer when the repository plan supports it.
3. If the maintainer must approve their own release, do not enable a rule that
   prevents self-review.
4. Restrict deployment tags to `v*` when tag restrictions are available.
5. Do not add a PyPI password, username, or API-token secret.

The environment protects only the final publishing job. Tests and builds run
without publishing authority.

### PyPI trusted publisher

If the PyPI project does not exist, add a pending GitHub publisher from the
PyPI account **Publishing** page. If it already exists, use the project's
**Manage → Publishing** page.

Use these exact values:

| Field | Value |
| --- | --- |
| PyPI project | `python-ai-toolkit` |
| Owner | `bkocii` |
| Repository | `python-ai-toolkit` |
| Workflow | `release.yml` |
| Environment | `pypi` |

The workflow filename is only `release.yml`, not its complete repository path.
All five identity values are case- and spelling-sensitive configuration
boundaries. A pending publisher can create the PyPI project on first use, but
it does not reserve the project name.

Official references:

- [PyPI trusted publishers](https://docs.pypi.org/trusted-publishers/)
- [Creating a PyPI project with a pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
- [GitHub deployment environments](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment)

## Roles of the release files

| File | Responsibility |
| --- | --- |
| [`pyproject.toml`](../pyproject.toml) | Authoritative package version and metadata |
| [`CHANGELOG.md`](../CHANGELOG.md) | User-visible changes in the release |
| [`release.yml`](../.github/workflows/release.yml) | Tag validation, quality checks, build, validation, and publication |
| [`validate_release_tag.py`](../scripts/validate_release_tag.py) | Exact tag-to-version validation |
| [`validate_distributions.py`](../scripts/validate_distributions.py) | Offline wheel and source-archive inspection |
| [`installation.md`](installation.md) | Detailed local artifact and clean-install checks |
| [`project_state.md`](development/project_state.md) | Current milestone and completed work |

## Phase 1 — Prepare the release

### 1. Confirm release authority and scope

Before changing the version:

- confirm that the roadmap names the release as the current task
- confirm the intended version
- confirm all release blockers are closed
- review the public API and compatibility decisions required by that milestone
- ensure the changelog describes the changes users will receive
- ensure no unrelated or unreviewed working-tree changes are included

Version examples:

| Release kind | Package version | Tag |
| --- | --- | --- |
| Development | `0.7.0.dev0` | `v0.7.0.dev0` |
| Release candidate | `1.0.0rc1` | `v1.0.0rc1` |
| Stable | `1.0.0` | `v1.0.0` |

Use the version required by the roadmap. Do not publish the current
development version merely as a workflow test.

### 2. Update the release source

Set the authoritative version in `pyproject.toml`. Update the changelog and
the roadmap/project-state records required by the active release task.

For a Version 1.0 release, for example:

```toml
[project]
version = "1.0.0"
```

Do not create the tag yet. First review the complete change:

```powershell
git status --short
git diff --check
git diff
```

Generated `build\`, `dist\`, and `*.egg-info\` content must remain untracked.
Real `.env` files, credentials, logs, caches, and local benchmark output must
not be included.

### 3. Define and validate the intended tag

Use a PowerShell variable so later commands refer to one value:

```powershell
$version = "1.0.0"
$tag = "v$version"

python scripts\validate_release_tag.py $tag
```

Expected:

```text
release tag v1.0.0 matches package version 1.0.0: PASSED
```

If it fails, correct `pyproject.toml` or the intended tag. Never bypass the
validator.

### 4. Run the local quality gate

From an active development environment:

```powershell
python -m pip install -e ".[dev]"
python -m pip install build twine

python -m pip check
python -m black --check .
python -m ruff check .
python -m pytest -q
```

No provider API key or live provider request is required. Stop on any failure.
Do not create a release commit or tag while a check is red.

GitHub will independently repeat the complete suite on Python 3.11, 3.12,
3.13, and 3.14. One successful local interpreter does not replace that matrix.

### 5. Build and validate locally

Remove only reproducible package output, then build fresh distributions:

```powershell
Remove-Item build, dist -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Directory -Filter "*.egg-info" |
    Remove-Item -Recurse -Force

python -m build
python -m twine check --strict dist\*
python scripts\validate_distributions.py
Get-ChildItem dist
```

Expect exactly one wheel and one source archive for the intended version. The
validator prints SHA-256 values identifying the local files it inspected.

Complete the clean wheel and source-distribution installation checks in the
[installation guide](installation.md#test-each-artifact-in-a-clean-windows-environment).
Those checks must import the installed package outside the source checkout,
exercise the console command, and pass `pip check`.

## Phase 2 — Approve the exact commit

### 6. Commit and review the release changes

Create a normal branch commit and push it for review:

```powershell
git add pyproject.toml CHANGELOG.md README.md docs
git diff --cached
git commit -m "release: prepare $version"
git push
```

Adjust the `git add` targets to the files actually changed by the release task.
Never use a broad add command without reviewing its scope.

The pull request or protected-branch process must complete successfully:

- all required reviews are approved
- the CI matrix is green on Python 3.11–3.14
- the CI build and both distribution validators are green
- the release commit is merged into `main`

### 7. Verify the final `main` commit

After merge, use a clean, up-to-date `main` checkout:

```powershell
git switch main
git pull --ff-only origin main
git status --short

$version = "1.0.0"
$tag = "v$version"

python scripts\validate_release_tag.py $tag
git log -1 --oneline
```

`git status --short` must print nothing. Record the commit shown by
`git log -1`; that is the source commit the tag should identify.

## Phase 3 — Create and push the tag

### 8. Create one annotated tag

Create the tag only after the exact `main` commit is approved:

```powershell
git tag -a $tag -m "Release $version"
git show --no-patch --decorate $tag
```

Confirm the tag points to the current commit:

```powershell
if ((git rev-list -n 1 $tag) -ne (git rev-parse HEAD)) {
    throw "Release tag does not point to the current commit."
}
```

If the local tag is wrong and has not been pushed, delete it locally, correct
the source or selected commit, and recreate it:

```powershell
git tag -d $tag
```

This local correction is safe only before the tag is pushed.

### 9. Push only the intended tag

This is the release trigger:

```powershell
git push origin $tag
```

Do not use `git push --tags`; it can publish unrelated local tags. After this
command, treat the tag as immutable and make any source correction in a new
commit with a new version and tag.

## Phase 4 — Monitor and approve publication

### 10. Inspect the GitHub Actions run

Open the repository **Actions** page and select the run named
**Release candidate** for the exact tag.

Jobs must pass in this order:

1. `Validate version tag`
2. four `Tests (Python …)` jobs
3. `Build tagged distributions`
4. `Publish distributions to PyPI`

Before approval, confirm:

- the run was triggered by the intended tag
- the commit SHA matches the recorded release commit
- all four Python jobs passed
- the build job passed both validators
- the retained artifact name includes the exact tag
- the artifact contains the expected wheel and source archive

If the `pypi` environment requires review, the publishing job waits. Select
**Review deployments**, choose `pypi`, and approve only after the checks above.
Reject or cancel the deployment if anything is unexpected.

The final job obtains a short-lived identity from PyPI and publishes the
already validated artifacts. It does not rebuild them.

## Phase 5 — Verify the published release

### 11. Inspect PyPI

Open the
[Python AI Toolkit project page](https://pypi.org/project/python-ai-toolkit/)
and confirm:

- the exact version is present
- both wheel and source distribution are present
- metadata, Python requirement, dependencies, extras, license, and README
  render as expected
- the project identifies the expected trusted-publishing source

Do not assume a green upload step proves that users can install the package.

### 12. Install from PyPI in a clean environment

Run the smoke test outside the source checkout:

```powershell
$version = "1.0.0"
$projectRoot = (Get-Location).Path
$smokeRoot = Join-Path (Split-Path $projectRoot) "python-ai-toolkit-pypi-smoke"

Remove-Item $smokeRoot -Recurse -Force -ErrorAction SilentlyContinue
py -m venv $smokeRoot

Push-Location (Split-Path $projectRoot)

& "$smokeRoot\Scripts\python.exe" -m pip install --no-cache-dir `
    --index-url https://pypi.org/simple/ "python-ai-toolkit==$version"
& "$smokeRoot\Scripts\python.exe" -m pip check
& "$smokeRoot\Scripts\python.exe" -c `
    "from importlib.metadata import version; from ai.prompts import PromptTemplate; assert version('python-ai-toolkit') == '$version'; assert PromptTemplate('Hello {name}').render(name='Burim') == 'Hello Burim'; print('PyPI smoke: PASSED')"
& "$smokeRoot\Scripts\ai-toolkit.exe" --help

Pop-Location
```

Expected:

- installation resolves the exact requested version from PyPI
- `pip check` reports no broken requirements
- the offline smoke test prints `PyPI smoke: PASSED`
- `ai-toolkit --help` succeeds

This smoke test does not need provider credentials or make a network request
after installation.

### 13. Record completion

After verification:

- record the released version, tag, and commit in project state
- mark the roadmap release tasks complete
- record the CI run and PyPI verification result
- ensure the changelog and README show the published status
- preserve any release hashes or evidence required by the release milestone

The current workflow does not create a GitHub Release. Adding release notes or
assets on GitHub is a separate future decision and must not be assumed complete
by this procedure.

## Failure and recovery

Stop publication whenever the source, version, tag, artifact, identity, or
approval is uncertain.

| Failure point | Safe response |
| --- | --- |
| Local check fails | Fix the source and rerun every affected check; do not tag |
| Local tag is wrong and unpushed | Delete the local tag, correct the source or target commit, and recreate it |
| Pushed tag fails version, test, or build validation | Fix in a new commit, choose a new version, and create a new tag; do not move or reuse the pushed tag |
| Publishing waits for approval unexpectedly | Reject or cancel it and inspect the tag, commit, artifact, and environment |
| Trusted Publishing identity fails before upload | Check owner, repository, workflow filename, and `pypi` environment; rerun only if PyPI shows that no file was uploaded and the tagged source remains correct |
| PyPI shows only part of the release | Do not blindly rerun; inspect which filenames exist, treat the version as used, and prepare a corrected new version |
| Published release is defective | Yank the defective release when appropriate, document the problem, fix it, and publish a new version |
| A release or file was deleted from PyPI | Treat deletion as permanent; do not expect to restore or reuse its filename |

PyPI does not allow an existing filename to be overwritten, including after
deletion. Never delete a release as an attempt to repair and republish the same
version. Prefer yanking when a published version should no longer be selected
normally, then publish a corrected version.

GitHub can rerun failed jobs against the same tagged commit when the failure was
transient or account-side and no file reached PyPI. A rerun is not a way to
substitute different source code for an existing tag.

Official recovery references:

- [PyPI Trusted Publishing troubleshooting](https://docs.pypi.org/trusted-publishers/troubleshooting/)
- [PyPI help and irreversible deletion rules](https://pypi.org/help/)
- [Re-running GitHub Actions jobs](https://docs.github.com/actions/managing-workflow-runs/re-run-workflows-and-jobs)
- [Canceling a GitHub Actions run](https://docs.github.com/actions/managing-workflow-runs/cancel-a-workflow-run)

## Final checklist

### Before tag

- [ ] Roadmap authorizes the release and version
- [ ] Version and changelog are correct
- [ ] Working tree contains only reviewed source changes
- [ ] Tag validator passes
- [ ] Local dependency, Black, Ruff, and test checks pass
- [ ] Fresh wheel and source distribution pass both validators
- [ ] Clean artifact installation checks pass
- [ ] Release commit is reviewed, merged, and green on all supported Pythons
- [ ] GitHub `pypi` environment and matching PyPI publisher are configured

### Before PyPI approval

- [ ] Tag and package version match
- [ ] Workflow commit matches the approved release commit
- [ ] All release-workflow quality and build jobs pass
- [ ] Artifact name and both files match the intended tag
- [ ] No unexpected source, permission, or identity change exists

### After publication

- [ ] Exact version and both files appear on PyPI
- [ ] PyPI metadata and README render correctly
- [ ] Clean exact-version installation succeeds
- [ ] `pip check`, offline import smoke, and console help pass
- [ ] Roadmap, project state, and changelog record completion
