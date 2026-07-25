# Configuration

Python AI Toolkit supports two configuration paths:

1. environment-based configuration for normal standalone use
2. an explicit `AIConfig` object for application factories, framework adapters,
   tests, and applications that already have their own configuration system

The two paths are alternatives. Passing an explicit configuration does not
merge it with environment values.

## Environment-based configuration

Copy the repository template and replace its placeholders:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# Linux or macOS
cp .env.example .env
```

A minimal OpenAI configuration is:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

The toolkit loads `.env` through `python-dotenv` when `ai.config` is imported.
Existing process environment variables take precedence over values from
`.env`.

Creating a client without a configuration object calls `get_ai_config()`:

```python
from ai.client import AIClient

client = AIClient()
```

`AsyncAIClient()` follows the same configuration rules.

## Resolution order

The selected provider controls the names of the provider-specific variables.
For example, `AI_PROVIDER=openai` produces `OPENAI_API_KEY`,
`OPENAI_MODEL`, and `OPENAI_EMBEDDING_MODEL`.

| Setting | Resolution order |
| --- | --- |
| Provider | `AI_PROVIDER` → `openai` |
| API key | `<PROVIDER>_API_KEY` → `AI_API_KEY` → configuration error |
| Request model | `<PROVIDER>_MODEL` → `AI_MODEL` → `gpt-5.4-mini` |
| Embedding model | `<PROVIDER>_EMBEDDING_MODEL` → `AI_EMBEDDING_MODEL` → `text-embedding-3-small` |
| Embedding dimensions | `AI_EMBEDDING_DIMENSIONS` → provider default |
| Maximum retries | `AI_MAX_RETRIES` → `1` |
| Input token price | `AI_INPUT_COST_PER_1M_TOKENS` → built-in model price when available |
| Output token price | `AI_OUTPUT_COST_PER_1M_TOKENS` → built-in model price when available |
| Log level | `AI_LOG_LEVEL` → `INFO` |
| Log file | `AI_LOG_FILE_PATH` → `logs/ai_toolkit.log` |
| File logging | `AI_FILE_LOGGING_ENABLED` → `true` |

Provider names loaded from the environment are stripped and converted to
lowercase. Provider-specific variables take precedence over their generic
fallbacks even when both are set.

The provider registry is a separate concern: resolving values for a provider
does not register its implementation. Provider registration is covered by the
provider documentation task.

## Environment variable reference

| Variable | Meaning | Accepted value or default |
| --- | --- | --- |
| `AI_PROVIDER` | Provider selected by `ProviderFactory` | Non-empty name; default `openai` |
| `<PROVIDER>_API_KEY` | Credential for the selected provider | Non-empty string; preferred over `AI_API_KEY` |
| `AI_API_KEY` | Provider-independent credential fallback | Non-empty string; no default |
| `<PROVIDER>_MODEL` | Request model for the selected provider | Non-empty string; preferred over `AI_MODEL` |
| `AI_MODEL` | Provider-independent request-model fallback | Non-empty string; default `gpt-5.4-mini` |
| `<PROVIDER>_EMBEDDING_MODEL` | Embedding model for the selected provider | Non-empty string; preferred over `AI_EMBEDDING_MODEL` |
| `AI_EMBEDDING_MODEL` | Provider-independent embedding-model fallback | Non-empty string; default `text-embedding-3-small` |
| `AI_EMBEDDING_DIMENSIONS` | Requested embedding vector size | Positive whole number; blank means provider default |
| `AI_MAX_RETRIES` | Retries after the initial structured-response attempt | Whole number zero or greater; default `1` |
| `AI_INPUT_COST_PER_1M_TOKENS` | Custom input-token price in USD | Decimal-compatible string; optional |
| `AI_OUTPUT_COST_PER_1M_TOKENS` | Custom output-token price in USD | Decimal-compatible string; optional |
| `AI_LOG_LEVEL` | Toolkit logger level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`; default `INFO` |
| `AI_LOG_FILE_PATH` | Toolkit-managed log destination | Non-empty path when file logging is enabled; default `logs/ai_toolkit.log` |
| `AI_FILE_LOGGING_ENABLED` | Enables the toolkit-managed file handler | `1`, `true`, `yes`, `on`, `0`, `false`, `no`, or `off`; default `true` |

Custom token prices override the built-in model-price table only when both the
input and output values are configured. Prices are resolved once when a client
is constructed.

`AI_MAX_RETRIES=0` disables retry attempts; the initial request still runs.

## Generic fallback example

Generic names allow an application to select a registered custom provider
without defining provider-specific variable names:

```env
AI_PROVIDER=custom
AI_API_KEY=your_api_key_here
AI_MODEL=custom-chat-model
AI_EMBEDDING_MODEL=custom-embedding-model
AI_FILE_LOGGING_ENABLED=false
```

If `CUSTOM_API_KEY`, `CUSTOM_MODEL`, or `CUSTOM_EMBEDDING_MODEL` are also set,
those provider-specific values win.

## Explicit `AIConfig`

Use an explicit configuration when values originate outside `.env` or when an
application needs isolated client instances:

```python
import os

from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator

config = AIConfig(
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-5.4-mini",
    embedding_model="text-embedding-3-small",
    max_retries=1,
    log_level="INFO",
    file_logging_enabled=False,
)

ConfigValidator.validate(config)
client = AIClient(config=config)
```

The same object can be passed to the asynchronous client:

```python
from ai.async_client import AsyncAIClient

async_client = AsyncAIClient(config=config)
```

### Explicit configuration precedence

| Client construction | Configuration source |
| --- | --- |
| `AIClient()` or `AsyncAIClient()` | `get_ai_config()` loads and validates environment-based configuration |
| `AIClient(config=config)` or `AsyncAIClient(config=config)` | The supplied object is used; environment configuration is not loaded or merged |

`AIConfig` is a frozen dataclass. Constructing it does not perform validation,
and the core clients do not call `ConfigValidator` for a supplied object.
Applications that construct `AIConfig` directly should validate it before
client construction, as shown above.

Fields omitted from explicit construction use `AIConfig` defaults. They do not
fall back to `.env`. For example, omitting `model` uses `gpt-5.4-mini` even if
`OPENAI_MODEL` is set.

Environment loading normalizes the provider name, log level, and configured log
path. Explicit values are used as supplied, so explicit configurations should
use a lowercase registered provider name and an uppercase supported log level.

## Structural validation

`get_ai_config()` calls `ConfigValidator.validate()` automatically. Structural
validation checks that:

- provider, API key, request model, and embedding model are not blank
- maximum retries is zero or greater
- embedding dimensions are positive when supplied
- file logging is a Boolean value
- the log level is supported
- the log path is not blank when file logging is enabled

Structural validation does not:

- contact a provider
- authenticate the API key
- confirm model access
- test network connectivity
- register or confirm availability of a provider implementation

Provider availability is checked later by `ProviderFactory` when a client is
constructed. Credentials and model access are exercised only by a live
provider request.

## Configuration CLI

Inspect the resolved environment-based configuration:

```bash
ai-toolkit config show
```

The API key is masked in the output.

Validate the resolved structure without contacting the provider:

```bash
ai-toolkit config validate
```

These commands read the environment configuration path. They do not inspect an
`AIConfig` object created inside application code, modify `.env`, save secrets,
or perform a live provider health check.

## Choosing a configuration path

Use environment-based configuration when one process uses one toolkit
configuration and a `.env` or deployment environment already owns the values.

Use explicit configuration when:

- a framework or application settings object owns the values
- tests need deterministic configuration without process-wide mutation
- one process needs multiple clients with different settings
- an application factory constructs dependencies explicitly

Keep credential storage outside source code. Detailed secret handling belongs
to the separate security guide.
