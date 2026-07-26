# Error Message Guidelines

Errors are part of the toolkit's developer experience.

This is a maintainer guide for designing exception messages inside the
toolkit. Application users should begin with the
[exceptions and error-handling guide](../error_handling.md), which documents
the public hierarchy, catch boundaries, retry behavior, ordinary Python
exceptions, and result-based failures.

Every toolkit exception should help the developer understand:

1. what went wrong
2. which value caused the problem, when relevant
3. how to fix it

---

## Recommended Format

Use this format whenever possible:

```text
<Problem>. <Suggested fix>.
```

Example:
```text
Missing API key for provider 'openai'. Set OPENAI_API_KEY=your_api_key or AI_API_KEY=your_api_key in your .env file.
```

## Good Error Messages
Missing configuration
```text
Missing API key for provider 'anthropic'. Set ANTHROPIC_API_KEY=your_api_key or AI_API_KEY=your_api_key in your .env file.
```

Why this is good:

- identifies the missing setting
- includes the selected provider
- suggests exact environment variables to set

Unsupported provider

```text
Unsupported AI provider 'custom'. Available providers: openai. Set AI_PROVIDER to a registered provider or register a custom provider before creating AIClient.
```

## Avoid

Avoid vague messages:

```text
Invalid config.
```

```text
Provider error.
```

```text
Bad value.
```

These messages do not help the developer solve the issue.

## Exception Types

Use the existing toolkit exception hierarchy.

`AIError` is the common application catch boundary for classified toolkit
failures. The concrete subclasses below should be used when the toolkit can
identify the failure category.

### AIConfigurationError

Use for invalid or missing toolkit configuration.

Examples:

- missing API key
- empty model
- unsupported provider
- invalid retry count

### AIProviderError

Use for provider SDK or provider request failures.

Examples:

- OpenAI API failure
- provider timeout
- authentication failure returned by the provider

### AIJSONParseError

Use when the model response cannot be parsed as JSON.

### AISchemaValidationError

Use when parsed JSON does not match the expected Pydantic schema.

Structured-response exceptions may be written by executor exception logging.
Do not include the raw provider response in either exception message. The
caller can inspect `AIResult.raw_response` only after a successful request;
failed response bodies must not be copied into ordinary logs.

## Ordinary Python Exceptions

Not every public failure should become an `AIError`.

Keep ordinary exceptions when the failure belongs to ordinary Python or
application input rather than toolkit configuration, provider communication,
or structured response handling. Current examples include:

- `ValueError` for blank prompts, workflow inputs, agent names, and vector
  dimension mismatches
- `FileNotFoundError` for missing document paths
- native file-system exceptions for decoding, permissions, and reading
- Pydantic `ValidationError` when application code constructs an invalid model
- unexpected exceptions from defective custom provider implementations

Do not wrap programming defects merely to make every exception inherit from
`AIError`. A broad translation would hide the source of the problem and make
retry decisions less reliable.

## Preserve Causes

When translating a known lower-level exception, preserve it with exception
chaining unless that cause can expose protected request or response content:

```python
try:
    provider_sdk_call()
except ProviderSDKError as exc:
    raise AIProviderError("Provider request failed.") from exc
```

The public message should identify the operation and suggest a correction when
one is known. The chained cause keeps lower-level debugging context available.

JSON parsing and Pydantic response validation are deliberate exceptions to the
general chaining rule because their exception objects can retain or render the
rejected provider response. Raise the toolkit parse or schema exception
`from None` so ordinary executor traceback logging does not disclose that
content.

## Rule of Thumb

A developer should be able to read the exception and know what to try next without opening the source code.


## Why this file matters

This is not runtime code, but it protects quality.

As the toolkit grows, more errors will be added. Without a guideline, messages become inconsistent:

```text
Missing API key.
Bad provider.
Invalid config.
```
With a guideline, every error follows the same developer-friendly style.
