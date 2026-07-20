# ADR-0015

## Status

Accepted

---

## Date

2026-07-20

---

## Context

The toolkit needs a command-line interface that allows developers to make simple AI requests without writing a Python script.

The first CLI task must support plain-text requests while preserving the existing provider-independent architecture.

A later roadmap task, `INTEGRATION-004`, will add configuration-oriented CLI commands. The initial design should allow those commands to be added without restructuring the CLI.

The CLI must provide useful error messages without exposing unnecessary tracebacks for expected toolkit errors.

---

## Decision

The toolkit will expose a console command named:

```text
ai-toolkit
```

The first supported subcommand will be:

```text
ai-toolkit ask "<prompt>"
```

The CLI will use Python's standard-library `argparse` module.

The CLI implementation will be located in:

```text
ai/cli/main.py
```

The package entry point will call:

```python
ai.cli.main:main
```

The `ask` command will:

1. Parse the prompt.
2. Create `AIClient` using the existing configuration system.
3. Call `AIClient.ask()`.
4. Print `AIResult.data`.
5. Return exit code `0`.

Expected toolkit errors derived from `AIError` will be printed to standard error and return exit code `1`.

Invalid command syntax will use `argparse`'s standard behavior and exit code `2`.

Unexpected exceptions will not be silently converted into user-facing errors because they may represent programming defects.

The initial CLI will not manage configuration. API-key setup, environment-file editing, and configuration inspection belong to `INTEGRATION-004`.

---

## Alternatives Considered

* Use Click.

  Rejected because the initial command structure is small and does not justify another runtime dependency.

* Use Typer.

  Rejected because it would add dependencies and additional framework behavior for a CLI that currently needs only one simple subcommand.

* Implement only `python -m ai`.

  Rejected because an installed `ai-toolkit` command provides a clearer public interface. Module execution may be added later if required.

* Add provider, model, and API-key arguments to the `ask` command.

  Rejected because configuration management belongs to `INTEGRATION-004` and should not expand the current task.

* Catch every exception and print a friendly message.

  Rejected because unexpected exceptions may represent toolkit defects that should remain visible during development.

---

## Consequences

Positive

* Developers can make AI requests without creating a Python file.
* The CLI reuses `AIClient` and the existing provider architecture.
* No new runtime dependency is required.
* Standard exit codes support scripts and automation.
* The package structure can support future configuration subcommands.
* Expected toolkit failures produce concise error messages.

Negative

* The first CLI supports only plain-text requests.
* Configuration must already exist in environment variables or `.env`.
* `argparse` provides less advanced CLI functionality than dedicated CLI frameworks.
* Each CLI invocation creates a new client and provider instance.

---

## Related Files

* `ai/cli/__init__.py`
* `ai/cli/main.py`
* `ai/client.py`
* `ai/exceptions.py`
* `tests/test_cli.py`
* `pyproject.toml`
* `README.md`
* `docs/development/roadmap.md`
