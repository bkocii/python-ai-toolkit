# ADR-0016

## Status

Accepted

---

## Date

2026-07-21

---

## Context

`RequestExecutor` and `AsyncRequestExecutor` currently create the toolkit logger internally through `get_ai_logger()`.

The logger always:

* creates a `logs` directory,
* opens `logs/ai_toolkit.log`,
* uses the `INFO` level,
* retains a process-wide file handler.

This behavior is reasonable for normal application usage, but it causes problems for tests, benchmarks, continuous integration, and clean package verification.

File logging during benchmarks adds file-system I/O to the measured request lifecycle. This makes the benchmark measure logging overhead in addition to toolkit request overhead.

Tests and clean installations should also not require a writable `logs` directory.

Applications may need to choose a different log level or file location, or disable toolkit-managed file logging while retaining their own logging handlers.

---

## Decision

Toolkit logging will become configurable.

The following environment variables will be supported:

```env
AI_LOG_LEVEL=INFO
AI_LOG_FILE_PATH=logs/ai_toolkit.log
AI_FILE_LOGGING_ENABLED=true
```

`AIConfig` will include:

```python
log_level: str = "INFO"
log_file_path: str = "logs/ai_toolkit.log"
file_logging_enabled: bool = True
```

Logging configuration loaded directly from the environment will be represented by a dedicated `AILoggingConfig`.

`AIClient` and `AsyncAIClient` will configure the toolkit logger and inject it into their request executors.

`RequestExecutor` and `AsyncRequestExecutor` will accept an optional `logging.Logger`.

When no logger is supplied, executors will preserve backward-compatible behavior by creating the normal toolkit logger.

Toolkit-managed handlers will be identified separately from application-managed handlers.

Reconfiguring the toolkit logger may replace toolkit-managed handlers, but it must not remove handlers added by an application.

When toolkit file logging is disabled:

* the toolkit will not create a logging directory,
* the toolkit will not open a log file,
* application-provided handlers will remain usable,
* a `NullHandler` will be used only when no other handler exists.

The toolkit logger will not propagate records to the root logger by default, preventing duplicate output.

Prompts and provider responses will remain excluded from logs.

---

## Alternatives Considered

* Remove logging from request executors during benchmarks.

  Rejected because benchmark-specific behavior should not be embedded inside production request logic.

* Monkeypatch logging only inside benchmark tests.

  Rejected because normal tests and clean package checks would still depend on file logging behavior.

* Read logging environment variables directly throughout the executors.

  Rejected because it would duplicate configuration logic and make explicit `AIConfig` injection inconsistent.

* Disable all logging when file logging is disabled.

  Rejected because applications may provide their own handlers and still require request metadata logs.

* Clear all handlers whenever logging is configured.

  Rejected because it would remove handlers owned by the embedding application.

---

## Consequences

Positive

* Benchmarks can run without file-system logging overhead.
* Tests do not require a writable `logs` directory.
* Applications can configure log level and file location.
* Applications can disable toolkit-managed file logging.
* Sync and async request paths use consistent logging.
* Application-owned handlers remain intact.
* Existing logging remains enabled by default.

Negative

* Logging configuration becomes part of `AIConfig`.
* Logger handler ownership must be tracked.
* Client and executor construction gain additional internal wiring.
* Logging tests must reset the process-wide logger between tests.
* Documentation and `.env.example` require updates.

---

## Related Files

* `ai/config.py`
* `ai/config_validator.py`
* `ai/logger.py`
* `ai/client.py`
* `ai/async_client.py`
* `ai/executor.py`
* `ai/async_executor.py`
* `tests/test_config.py`
* `tests/test_config_validator.py`
* `tests/test_logger.py`
* `.env.example`
* `README.md`
