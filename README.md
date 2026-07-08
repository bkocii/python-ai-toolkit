# Python AI Toolkit

A reusable AI engineering toolkit for Python developers.

The goal of this project is to provide clean, reusable building blocks for integrating Large Language Models (LLMs) into Python applications.

Instead of scattering AI code across projects, this toolkit centralizes configuration, provider integrations, validation, logging, and future AI capabilities behind a consistent interface.

---

## Philosophy

The LLM is only one part of an AI application.

Business logic should remain in Python.

```
Application
        │
        ▼
 AI Toolkit
        │
        ▼
 AI Provider
        │
        ▼
 Language Model
```

The toolkit is responsible for:

- communicating with AI providers
- validating responses
- tracking usage
- handling retries
- exposing a clean developer API

Applications remain responsible for business logic.

---

# Current Features

## AI Client

Single entry point for all AI requests.

```python
ai = AIClient()

response = ai.ask(...)
```

---

## Provider Architecture

Current:

- OpenAI

Planned:

- Anthropic
- Google Gemini
- Ollama
- Azure OpenAI
- Custom providers

---

## Structured Responses

Supports returning validated Pydantic models instead of raw text.

```python
recommendation = ai.ask(
    prompt=prompt,
    response_type=DrinkRecommendation
)

print(recommendation.data.recommended_item)
```

---

## Automatic Validation

Responses are validated using Pydantic schemas.

Invalid JSON and schema mismatches raise custom exceptions.

---

## Retry

Structured responses are automatically retried once if validation fails.

---

## Logging

Each request is logged with:

- request id
- model
- duration
- retry count
- token usage
- estimated cost

---

## Token Usage

Provider token usage is tracked and returned with every request.

---

## Cost Estimation

Supports configurable token pricing for estimating request cost.

---

## Custom Exceptions

Includes dedicated exception hierarchy.

Examples:

- AIConfigurationError
- AIProviderError
- AIJSONParseError
- AISchemaValidationError

---

# Current Project Structure

```
python-ai-toolkit/

├── ai/
│   ├── client.py
│   ├── config.py
│   ├── parser.py
│   ├── prompts.py
│   ├── schemas.py
│   ├── logger.py
│   ├── cost.py
│   ├── exceptions.py
│   └── providers/
│       ├── base.py
│       └── openai_provider.py
│
├── examples/
│
├── tests/
│
├── logs/
│
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/python-ai-toolkit.git
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env`

```env
AI_PROVIDER=openai

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.4-mini

# Optional generic fallback for custom providers
AI_API_KEY=
AI_MODEL=

AI_MAX_RETRIES=1

AI_INPUT_COST_PER_1M_TOKENS=
AI_OUTPUT_COST_PER_1M_TOKENS=
```

---

# Development

Run tests

```bash
python -m pytest
```

Format

```bash
python -m black .
```

Lint

```bash
python -m ruff check .
```

---

# Roadmap

## Core

- [x] Configuration management
- [x] Provider abstraction
- [x] OpenAI provider
- [x] AI client
- [x] Prompt builder
- [x] Structured responses
- [x] Schema validation
- [x] Retry
- [x] Logging
- [x] Token tracking
- [x] Cost estimation
- [x] Request IDs

---

## Planned

- [ ] Prompt Builder v2
- [ ] Better parser architecture
- [ ] Streaming responses
- [ ] Async client
- [ ] Tool calling
- [ ] Conversation memory
- [ ] Embeddings
- [ ] Vector store abstraction
- [ ] RAG pipeline
- [ ] Agent framework
- [ ] Workflow engine
- [ ] Django integration
- [ ] FastAPI integration
- [ ] PyPI package

---

# Design Principles

- Single Responsibility Principle
- Dependency Inversion
- Composition over inheritance
- Strong typing
- Reusable components
- Clear interfaces
- Production-oriented architecture

---

# License

MIT