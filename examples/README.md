# Example Gallery

This directory contains small, self-contained examples demonstrating how to use the Python AI Toolkit.

## 01 – Summarize Text
- creating an AIClient
- simple AI request
- AIResult metadata

## 02 – Extract Structured Data
- Pydantic models
- response_type
- validated output

## 03 – Builder Usage
- fluent builder
- method chaining
- execute()

## 04 – Prompt Templates
- reusable prompts
- variable substitution

---

## 05 – Streaming Response

Demonstrates:

- streaming plain text responses
- consuming response chunks
- printing streamed output immediately

---

## 06 – Async Client

Demonstrates:

- using AsyncAIClient
- awaiting async AI requests
- running async examples with asyncio.run()

---

## 07 – Tool Calling

**File**

```text
07_tool_calling.py
```

Demonstrates:

- defining provider-independent tools
- passing tools to AIClient
- receiving requested tool calls
- keeping tool execution inside the application

---

## 08 – Image Inputs

**File**

```text
08_image_inputs.py
```
Demonstrates:

- sending an image URL to the model
- combining text and image input
- receiving a plain text response

## 09 – Structured Image Input

**FIle**
```text
09_structured_image_input.py
```
Demonstrates:

- sending image input
- using response_type
- validating structured image analysis with Pydantic

## Running
```bash
python -m examples.01_summarize_text
```

## Learning Path
1. Summarize Text
2. Extract Structured Data
3. Builder Usage
4. Prompt Templates
5. Streaming Response
6. Async Client
7. Tool Calling
8. Image Inputs
9. Structured Image Input