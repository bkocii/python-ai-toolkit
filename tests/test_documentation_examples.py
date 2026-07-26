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
    }

    for filename in expected_modules.values():
        assert (PROJECT_ROOT / "examples" / filename).is_file()
