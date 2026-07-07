# Project State

## Project

Python AI Toolkit

## Current Version

0.3.0-dev

## Current Milestone

Core AI Infrastructure

## Current Goal

Build a reusable AI engineering toolkit for Python developers.

The toolkit should provide reusable infrastructure for:

- AI client abstraction
- Provider integrations
- Structured responses
- Validation
- Retry handling
- Logging
- Token tracking
- Cost tracking
- Tool calling
- Embeddings
- RAG
- Agents
- Django integration

## Implemented

- Provider-based architecture
- OpenAI provider
- `AIClient`
- `RequestExecutor`
- Prompt builder
- Pydantic schema-based responses
- `AIResult`
- `ProviderResponse`
- `TokenUsage`
- Custom exceptions
- JSON parser
- Retry once for invalid structured responses
- Request duration tracking
- Request IDs
- Token usage tracking
- Token usage aggregation across retries
- Estimated cost scaffold
- Configurable token pricing through `.env`
- Basic file logging
- Drink recommender example
- Parser tests
- Prompt builder tests
- Request executor tests
- Retry behavior test

## Current Architecture

```text
Application
    ↓
AIClient
    ↓
RequestExecutor
    ↓
Provider
    ↓
LLM
    ↓
ProviderResponse
    ↓
Parser / Validator
    ↓
AIResult
    ↓
Application