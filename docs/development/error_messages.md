# Error Message Guidelines

Errors are part of the toolkit's developer experience.

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