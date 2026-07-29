# Version 1.0 Release-Blocker Audit

## Scope

`V1-002 — Resolve release-blocking defects` reviewed the frozen Version 1.0
contract, normal tests, package metadata, clean-install verifiers,
documentation, and release evidence.

The audit accepted a change only when a failure was reproduced or an existing
release claim was shown not to exercise its stated behavior. It did not add
features, expand the public API, change dependencies, change the package
version, create a tag, or publish.

## Confirmed blockers and resolutions

### Explicit configuration could bypass typed failure handling

`AIConfig` is a frozen dataclass, but dataclass annotations do not enforce
runtime types. Before this task, values such as `api_key=None` and
`max_retries="1"` reached `.strip()` or numeric comparison and raised
`AttributeError` or `TypeError`. A floating-point embedding dimension was
accepted. Invalid or one-sided custom pricing was accepted by validation and
either ignored or failed later during decimal conversion.

Resolution:

- validate every runtime type used by the client boundary
- require whole-number retry and embedding-dimension values
- require both custom prices together
- require configured prices to be finite, non-negative decimal strings
- preserve `AIConfigurationError` as the configuration-failure contract
- retain all frozen fields and client signatures unchanged

### Malformed provider data could become application data

The OpenAI tool-argument parser accepted valid JSON values that were not
objects, despite the public `ToolCall.arguments` contract being a dictionary.
Embedding response index validation rejected only indices beyond the end of a
batch. Negative indices therefore selected an unrelated Python list item, and
duplicate, missing, or out-of-order indices were not handled as a complete
batch-integrity boundary.

Resolution:

- require tool arguments to decode to a JSON object
- reject non-integer, Boolean, negative, out-of-range, and duplicate embedding
  indices
- reject incomplete embedding batches
- restore validated embeddings to input order before attaching text and
  metadata
- report malformed provider output as `AIProviderError`

### Release tests were not fully isolated or aligned with their names

The OpenAI factory test constructed SDK transports and therefore depended on
ambient proxy configuration. In an environment using a SOCKS proxy without the
optional SOCKS transport, the otherwise offline suite failed. The test named
for unsupported-provider rejection never called `ProviderFactory.create()` for
the unsupported provider.

Resolution:

- replace SDK client constructors inside the factory unit test
- keep the test offline under ambient proxy configuration
- execute and assert the actual unsupported-provider creation failure
- isolate process-local registry changes

### Installed-core verification omitted required request paths

The roadmap requires clean release evidence for a basic request and a
structured request. The installed-core verifier previously checked imports,
prompt templates, and vector search, but did not execute either client request
path.

Resolution:

- register a deterministic local provider in the installed environment
- execute one plain `AIClient` request
- execute one Pydantic-structured `AIClient` request
- keep the verification offline and disable toolkit-managed file logging
- retain separate CLI-help and optional-integration verification

## Reviewed items that were not blockers

The following remain outside `V1-002`:

- new providers and automatic provider discovery
- model capability preflight or live health checks
- async streaming, tools, images, and embeddings
- common metadata wrappers for advanced requests
- package version `1.0.0`, stable classifiers, release tags, and publication
- live provider smoke tests inside the normal unit suite
- application-owned tool execution, authorization, and business validation

These are accepted architecture boundaries, later Version 1 release tasks, or
Future Backlog work. Their absence is not a defect in the frozen Version 1
contract.

## Verification requirements

Completion requires:

1. focused configuration, provider-output, factory, and package-verifier tests
2. the complete normal suite on Python 3.11, 3.12, 3.13, and 3.14
3. `pip check`, Black, and Ruff on every supported interpreter
4. strict Twine and offline validation of a clean wheel and source archive
5. clean installed-core verification from the built wheel
6. no package-version, workflow, tag, credential, or publication change

The measured results are recorded in the roadmap and session handoff when the
task is completed.
