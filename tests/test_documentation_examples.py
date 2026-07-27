import ast
import importlib
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTATION_FILES = [
    PROJECT_ROOT / "README.md",
    *sorted((PROJECT_ROOT / "docs").glob("*.md")),
    PROJECT_ROOT / "examples" / "README.md",
]


def fenced_blocks(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0

    while index < len(lines):
        opening_line = lines[index]

        if not opening_line.startswith("```"):
            index += 1
            continue

        language = opening_line[3:].strip()
        start_line = index + 1
        index += 1
        body = []

        while index < len(lines) and not lines[index].startswith("```"):
            body.append(lines[index])
            index += 1

        yield language, start_line, "\n".join(body)
        index += 1


@pytest.mark.parametrize("path", DOCUMENTATION_FILES, ids=lambda path: path.name)
def test_documented_python_blocks_compile(path):
    for language, start_line, body in fenced_blocks(path):
        if language != "python":
            continue

        compile(
            body,
            f"{path.relative_to(PROJECT_ROOT)}:{start_line}",
            "exec",
        )


def test_documented_relative_links_resolve():
    link_pattern = re.compile(r"(?<!!)\[[^]]*]\(([^)]+)\)")

    for path in DOCUMENTATION_FILES:
        content = path.read_text(encoding="utf-8")

        for target in link_pattern.findall(content):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue

            relative_target = target.split("#", 1)[0]

            if not relative_target:
                continue

            resolved_target = (path.parent / relative_target).resolve()

            assert resolved_target.exists(), (
                f"{path.relative_to(PROJECT_ROOT)} links to missing "
                f"path: {relative_target}"
            )


def test_gallery_references_existing_python_files():
    gallery = (PROJECT_ROOT / "examples" / "README.md").read_text(encoding="utf-8")
    referenced_files = set(re.findall(r"`([^`]+\.py)`", gallery))

    assert referenced_files

    for filename in referenced_files:
        assert (PROJECT_ROOT / "examples" / filename).is_file()


def test_gallery_describes_every_example_module():
    gallery = (PROJECT_ROOT / "examples" / "README.md").read_text(encoding="utf-8")
    example_files = {
        path.name
        for path in (PROJECT_ROOT / "examples").glob("*.py")
        if path.name != "__init__.py"
    }
    referenced_files = set(re.findall(r"`([^`]+\.py)`", gallery))

    assert referenced_files == example_files


def test_gallery_entries_use_normalized_description_fields():
    gallery = (PROJECT_ROOT / "examples" / "README.md").read_text(encoding="utf-8")
    headings = [
        "## 01 — Plain Text Request",
        "## 02 — Extract Structured Data",
        "## 03 — Fluent Request Builder",
        "## 04 — Prompt Template",
        "## 05 — Streaming Response",
        "## 06 — Async Client",
        "## 07 — Tool Calling",
        "## 08 — Image Input",
        "## 09 — Structured Image Input",
        "### 09 Local Base64 Variant",
        "## 10 — Embeddings",
        "## 11 — In-Memory Vector Store",
        "## 12 — Retriever",
        "## 13 — RAG Pipeline",
        "## 14 — Directory Loader RAG",
        "## 15 — Conversation Memory",
        "## 16 — Agent",
        "## 17 — Workflow Engine",
        "## 18 — Multi-Agent Orchestration",
        "## 19 — Django Integration",
        "## 20 — FastAPI Integration",
        "## 21 — Command-Line Request",
        "## 22 — Configuration CLI",
        "## 23 — Explicit Configuration",
        "## 24 — Custom Provider Registration",
        "## 25 — Testing with a Fake Provider",
        "## 26 — Batch Embedding and Retrieval",
        "## 27 — End-to-End Document Indexing and RAG",
        "## 28 — Structured Application Service",
        "### Minimal `ask_text()` Check",
        "### Structured Drink Recommendation",
    ]

    for heading in headings:
        start = gallery.index(heading)
        remaining = gallery[start + len(heading) :]
        next_heading = re.search(r"\n#{2,3} ", remaining)
        body = remaining[: next_heading.start()] if next_heading else remaining

        assert re.search(r"\*\*(?:File|Command|Commands):\*\*", body), heading
        assert "**Demonstrates:**" in body, heading
        assert "**Requirements:**" in body, heading
        assert "**Run:**" in body, heading
        assert "**Boundary:**" in body, heading


def test_gallery_documents_numbering_compatibility_exceptions():
    gallery = (PROJECT_ROOT / "examples" / "README.md").read_text(encoding="utf-8")

    assert "Entries 21–22 are command workflows" in gallery
    assert "`09_1_structured_image_with_helper.py` is a local-file variant" in gallery
    assert "`hello_ai.py` and `drink_recommender.py` are older supplementary" in gallery


def test_numbered_example_modules_exist():
    expected_modules = {
        1: "01_plain_text.py",
        2: "02_extract_structured_data.py",
        3: "03_builder_usage.py",
        4: "04_prompt_templates.py",
        5: "05_streaming_response.py",
        6: "06_async_client.py",
        7: "07_tool_calling.py",
        8: "08_image_inputs.py",
        9: "09_structured_image_input.py",
        10: "10_embeddings.py",
        11: "11_vector_store.py",
        12: "12_retriever.py",
        13: "13_rag_pipeline.py",
        14: "14_document_loader_rag.py",
        15: "15_conversation_memory.py",
        16: "16_agent.py",
        17: "17_workflow_engine.py",
        18: "18_multi_agent_orchestration.py",
        19: "19_django_integration.py",
        20: "20_fastapi_integration.py",
        23: "23_explicit_config.py",
        24: "24_custom_provider.py",
        25: "25_testing_with_fake_provider.py",
        26: "26_batch_embedding_and_retrieval.py",
        27: "27_document_indexing_and_rag.py",
        28: "28_structured_application_service.py",
    }

    for filename in expected_modules.values():
        assert (PROJECT_ROOT / "examples" / filename).is_file()


def test_examples_import_only_documented_public_ai_symbols():
    api_reference = (PROJECT_ROOT / "docs" / "api_reference.md").read_text(
        encoding="utf-8"
    )
    surface_index = api_reference.split("## Surface index", 1)[1].split("\n## ", 1)[0]
    supported_modules = set()
    public_symbols = set()

    for line in surface_index.splitlines():
        cells = line.split("|")

        if len(cells) < 5:
            continue

        supported_modules.update(re.findall(r"`(ai(?:\.[a-z_]+)+)`", cells[2]))
        public_symbols.update(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", cells[3]))

    assert supported_modules
    assert public_symbols

    for path in sorted((PROJECT_ROOT / "examples").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue

            if node.module is None or not node.module.startswith("ai."):
                continue

            assert (
                node.module in supported_modules
            ), f"{path.name} imports undocumented module {node.module}"

            module = importlib.import_module(node.module)

            for alias in node.names:
                assert alias.name in public_symbols, (
                    f"{path.name} imports undocumented symbol "
                    f"{node.module}.{alias.name}"
                )
                assert hasattr(module, alias.name), (
                    f"{path.name} imports unavailable symbol "
                    f"{node.module}.{alias.name}"
                )
