# ADR-0001

## Title

Return AIResult instead of raw responses

---

## Status

Accepted

---

## Date

2026-07-06

---

## Context

Initially the toolkit could have returned only the raw model output.

Example

```python
text = ai.ask(...)
```

As the toolkit grows, applications need additional metadata such as:

- request duration
- request id
- token usage
- retry count
- estimated cost

Returning only a string would require future breaking API changes.

---

## Decision

All requests return an AIResult object.

The generated content is available through:

```python
result.data
```

Metadata is exposed through additional properties.

---

## Alternatives Considered

### Return plain strings

Simple but difficult to extend.

Rejected.

### Return dictionaries

Flexible but lacks type safety and autocomplete.

Rejected.

---

## Consequences

Positive

- Stable public API
- Extensible
- Better developer experience

Negative

- Slightly more verbose

---

## Related Files

- ai/schemas.py
- ai/client.py