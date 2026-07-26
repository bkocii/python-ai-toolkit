# Security and Secret Handling

Python AI Toolkit provides request, provider, retrieval, and orchestration
primitives. It does not replace an application's security architecture.

The toolkit supplies a few defensive defaults:

- environment-based credential loading
- API-key masking in `ai-toolkit config show`
- operational request logs that omit prompts and provider responses
- application-owned tool execution

Applications still own secret storage, access control, data classification,
provider governance, output handling, tool authorization, retention, and
incident response.

## Responsibility boundaries

| Concern | Toolkit behavior | Application or deployment responsibility |
| --- | --- | --- |
| API-key loading | Reads provider-specific or generic environment values | Store, inject, scope, rotate, and revoke credentials |
| Configuration display | Masks the full key and shows at most its final four characters | Restrict terminal and CI output containing operational configuration |
| Request logging | Logs request metadata, not prompt or response bodies | Configure file access, retention, handlers, and centralized log redaction |
| Provider requests | Sends the supplied prompt, image, or embedding input | Decide which data may be sent and which provider settings are acceptable |
| Structured output | Parses and validates response shape | Verify facts, permissions, policy, and safe use |
| Tool calling | Returns requested calls without executing them | Allow-list, validate, authorize, execute, audit, and rate-limit tools |
| Memory and retrieval | Stores or returns application-supplied content | Enforce tenant isolation, encryption, deletion, and retention |
| Framework adapters | Construct clients and propagate failures | Authenticate callers and map failures to safe public responses |

## Choose secret sources by environment

### Local development

Use a local `.env` file or process environment:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=replace_with_a_local_development_key
OPENAI_MODEL=gpt-5.4-mini
```

Copy `.env.example` to `.env`; do not put a real value in `.env.example`.
The repository ignores `.env` and `.env.*` while keeping `.env.example`
trackable. Restrict local file access, use a development-only key with the
smallest practical permissions and budget, and remove old copies from shell
scripts, notes, screenshots, and exported terminal history.

Git ignore rules reduce accidental staging; they do not protect a secret that
was already committed. Review staged changes and use a secret scanner in the
development or repository workflow.

### Automated tests

Use fake providers and fake values such as `test-key`. Normal unit,
integration, benchmark, and documentation tests should not require a live
credential or provider network call.

If a separate opt-in live test is necessary:

- keep it outside the default test path
- use a restricted non-production account
- set a strict cost or quota limit
- never print prompts, responses, or the credential
- skip it when the required secret is unavailable

### Continuous integration

Store live-test credentials in the CI platform's protected secret store and
inject them only into the trusted job that requires them. Do not place a secret
in workflow YAML, command arguments, cache keys, build artifacts, test reports,
or repository variables intended for public output.

Avoid exposing secrets to untrusted pull-request code. Prefer short-lived or
regularly rotated credentials, narrow job permissions, protected environments,
and fake-provider checks for ordinary CI.

### Production

Prefer an application or platform secret manager and inject the resolved value
at runtime. An application may then construct `AIConfig` explicitly:

```python
from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator


def build_ai_client(api_key: str) -> AIClient:
    config = AIConfig(
        provider="openai",
        api_key=api_key,
        model="gpt-5.4-mini",
        file_logging_enabled=False,
    )
    ConfigValidator.validate(config)
    return AIClient(config=config)
```

The example assumes `api_key` was already obtained through an
application-owned secure source. The toolkit does not fetch, cache, renew, or
rotate secret-manager values. Do not hard-code the value or use a production
secret as a constructor default.

Use separate credentials for development, CI, staging, and production. Apply
provider-supported least privilege, quotas, budget alerts, and rotation. When
the provider offers workload identity or temporary credentials, adoption and
renewal remain application concerns.

## Keep secrets out of repositories and artifacts

Do not commit:

- real API keys, access tokens, passwords, private keys, or signed URLs
- populated `.env`, `.env.local`, `.env.production`, or similar files
- production Django settings or deployment manifests containing plaintext
  credentials
- log files, debug dumps, notebooks, screenshots, recordings, or test fixtures
  containing sensitive request data
- exported vector records, conversation histories, or provider responses
  unless their storage is explicitly approved

Use placeholders in documentation and examples. Before publishing a branch,
package, ZIP, container image, or support bundle, scan both current files and
version-control history. Build output can preserve content that has already
been removed from source, so regenerate artifacts after remediation.

If a secret was committed, deleting the line in a later commit is not enough.
Revoke or rotate the credential first, then remove it from current files and
history according to repository policy.

## Understand what is sent to the provider

Treat every provider-bound value as a disclosure outside the application
boundary:

| Feature | Data sent or resent |
| --- | --- |
| Plain or structured request | Complete prompt; structured requests also include the generated schema |
| Structured repair | Original schema-aware prompt plus the invalid provider response |
| Streaming | Complete prompt before chunks are returned |
| Tool calling | Prompt plus tool names, descriptions, and parameter schemas |
| Image request | Prompt plus every image URL or Base64 data URL |
| Embeddings | Complete text of every embedding input |
| RAG | Question, selected context text, metadata formatting, and additional instructions |
| Agent | Instructions, formatted recent messages and metadata, and current message |
| Multi-agent sequence | Each successful agent output becomes the next agent's input |

Minimize data before sending it. Remove credentials, session identifiers,
unnecessary personal data, internal-only metadata, and fields the task does not
need. Prefer stable internal IDs over sensitive descriptive metadata, while
remembering that even identifiers may be personal or confidential.

Structured repair is another provider request. It can resend both the original
prompt and the invalid model response up to `max_retries` times. A structured
image repair does not resend the image, but it does send the schema-aware
prompt and invalid response through the plain-text provider path.

Image data URLs contain the complete image bytes and may be large. Image URLs
can reveal paths, identifiers, query parameters, or temporary access tokens.
Use approved sources and short-lived URLs without unnecessary secrets.

## Provider governance

Configuration validation proves only that local values are structurally valid.
It does not establish that a provider is approved for the data.

Before production use, review the selected provider, model, account, and region
for:

- retention and deletion behavior
- training or secondary-use settings
- data residency and cross-border transfer
- subprocessors and contractual requirements
- encryption and access controls
- regulated-data eligibility
- abuse monitoring and provider-side logs

These choices can change independently of the toolkit and should be verified
against current provider documentation and the application's legal and
security requirements.

## Logging, terminal output, and errors

The toolkit's normal request executors intentionally omit prompts and provider
responses from success and failure logs. Structured parse and schema exception
messages also omit the raw provider response. The executors log operational
fields such as request ID, model, duration, retry count, token usage, and
estimated cost.

This does not make every log automatically safe:

- provider exception text and tracebacks can contain provider or request
  metadata, even though structured parse and schema errors are redacted
- custom providers may log request content
- application-owned handlers and middleware may serialize arguments or result
  objects
- application logs may add user IDs, tenant IDs, filenames, or other sensitive
  fields
- the configured model name, log path, usage, cost, and request IDs may be
  operationally sensitive

Set file permissions, destination, rotation, retention, and centralized
redaction according to deployment policy. Disable toolkit-managed file logging
when the application owns logging or when a writable local log is inappropriate.

`ai-toolkit config show` masks the full API key but reveals its final four
characters for keys longer than four characters. Treat the complete command
output as sensitive operational data and do not publish it in tickets or CI
logs. Masking is for accidental-display reduction, not proof that output is
safe to share.

`ai-toolkit ask` prints the model response to standard output. Shell history
may retain the prompt, and redirected output may persist the response. Do not
use the CLI for sensitive prompts unless the terminal, history, process list,
and output destination meet the application's security requirements.

Provider errors and unexpected exceptions should be logged only at a trusted
boundary. Return a stable application-defined message to an untrusted HTTP,
task, or CLI caller; do not expose raw provider messages or tracebacks.

## Treat returned objects as sensitive

The toolkit returns useful debugging and traceability fields that may duplicate
sensitive content:

- `AIResult.data`, `raw_response`, and `original_raw_response`
- `ToolResponse.text` and every `ToolCall.arguments` mapping
- `EmbeddingVector.text` and metadata
- `RetrievedContext.text` and metadata
- `RAGResponse.answer`, `contexts`, and `raw_response`
- `ConversationMessage.content` and metadata
- `AgentResponse.output` and messages
- workflow state and orchestration error strings

Do not blindly call `model_dump()`, serialize complete objects into logs, or
return them from public endpoints. Select only the fields the destination is
authorized to receive. Apply field-level redaction before persistence and
define deletion and retention rules for every durable store.

In-memory storage is not encryption. It avoids an automatic persistent copy,
but content can still appear in process dumps, traces, error reports, or a
compromised worker.

## Authorize tool use and external actions

Model-requested tool calls are untrusted proposals. Before execution:

1. match the requested name against an application-owned allow-list
2. validate arguments with an application schema
3. authenticate the caller and authorize the exact user, tenant, resource, and
   operation
4. apply fixed server-side constraints instead of trusting model-supplied
   destinations, paths, URLs, or permission scopes
5. use least-privileged credentials and enforce time, cost, and rate limits
6. require confirmation or human review for destructive, financial,
   privileged, or irreversible actions
7. audit the decision and result without recording unnecessary sensitive data

Retrieved documents, user messages, image text, tool outputs, and prior model
responses can contain prompt-injection instructions. Treat them as data, not
authority. System prompts and Pydantic schemas do not replace access control.

## Web and multi-tenant applications

Django and FastAPI adapters do not install authentication, authorization,
tenant isolation, rate limits, CORS policy, CSRF policy, output filtering, or
security headers.

Before calling the toolkit:

- authenticate the caller
- authorize access to every source document and requested operation
- scope retrieval filters to the caller's tenant and permissions
- limit prompt, image, output, and request sizes
- apply abuse, cost, and concurrency controls

After the call, validate the result for its destination and expose only
authorized fields. A model answer must never grant access or bypass a
deterministic application permission check.

## Incident response

If a credential or sensitive payload may have been exposed:

1. revoke or rotate the affected credential immediately
2. stop or isolate the leaking job, service, log sink, or artifact
3. inspect provider usage, audit logs, repository history, CI output, build
   artifacts, caches, tickets, and shared files
4. invalidate signed URLs, sessions, or downstream credentials present in the
   exposed data
5. remove or redact stored copies using the owning system's procedures
6. redeploy with a clean secret and confirm that the exposure path is closed
7. follow organizational notification, legal, and post-incident requirements

Assume a committed or publicly printed secret is compromised even if it was
removed quickly.

## Production checklist

- [ ] No real secrets exist in source, examples, tests, history, or artifacts
- [ ] Credentials are separated by environment, scoped, monitored, and rotated
- [ ] The provider and selected data-handling settings are approved
- [ ] Sensitive input is minimized before prompts, embeddings, images, or RAG
- [ ] Retrieval enforces tenant and document permissions
- [ ] Logs and CLI output have approved access, redaction, and retention
- [ ] Public responses hide raw exceptions and internal result fields
- [ ] Tool calls are allow-listed, validated, authorized, constrained, and
      audited
- [ ] High-impact model output receives deterministic checks or human review
- [ ] Incident-response ownership and credential-revocation steps are known

## Related documentation

- [Configuration](configuration.md) explains credential resolution and
  explicit configuration.
- [Advanced requests](advanced_requests.md) covers tools, images, and repair
  boundaries.
- [Retrieval and RAG](retrieval.md) covers context and tenant-filtering
  boundaries.
- [Orchestration](orchestration.md) covers memory, state, and partial failures.
- [Framework and CLI integrations](integrations.md) covers propagation and
  command output.
- [Exceptions and error handling](error_handling.md) covers safe catch
  boundaries and provider error chaining.
