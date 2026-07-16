import pytest

from ai.documents import (
    DirectoryLoader,
    Document,
    MarkdownFileLoader,
    TextFileLoader,
    documents_to_embedding_inputs,
    normalize_path,
)


def test_document_stores_text_and_metadata():
    document = Document(
        text="Refunds are available within 14 days.",
        metadata={
            "source": "refund_policy.md",
            "type": "policy",
        },
    )

    assert document.text == "Refunds are available within 14 days."
    assert document.metadata == {
        "source": "refund_policy.md",
        "type": "policy",
    }


def test_documents_to_embedding_inputs_preserves_text_and_metadata():
    documents = [
        Document(
            text="Redis is often used as a cache.",
            metadata={"topic": "redis"},
        ),
        Document(
            text="PostgreSQL is a relational database.",
            metadata={"topic": "postgres"},
        ),
    ]

    inputs = documents_to_embedding_inputs(documents)

    assert len(inputs) == 2
    assert inputs[0].text == "Redis is often used as a cache."
    assert inputs[0].metadata == {"topic": "redis"}
    assert inputs[1].text == "PostgreSQL is a relational database."
    assert inputs[1].metadata == {"topic": "postgres"}


def test_normalize_path_expands_path():
    path = normalize_path(".")

    assert path.exists()


def test_text_file_loader_loads_text_file(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text(
        "Django is a Python web framework.",
        encoding="utf-8",
    )

    documents = TextFileLoader(file_path).load()

    assert len(documents) == 1
    assert documents[0].text == "Django is a Python web framework."
    assert documents[0].metadata["source"] == str(file_path)
    assert documents[0].metadata["filename"] == "notes.txt"
    assert documents[0].metadata["extension"] == ".txt"
    assert documents[0].metadata["loader"] == "TextFileLoader"


def test_text_file_loader_returns_empty_list_for_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ", encoding="utf-8")

    documents = TextFileLoader(file_path).load()

    assert documents == []


def test_text_file_loader_rejects_missing_file(tmp_path):
    file_path = tmp_path / "missing.txt"

    with pytest.raises(
        FileNotFoundError,
        match="Text file not found",
    ):
        TextFileLoader(file_path).load()


def test_text_file_loader_rejects_directory(tmp_path):
    with pytest.raises(
        ValueError,
        match="Path is not a file",
    ):
        TextFileLoader(tmp_path).load()


def test_markdown_file_loader_loads_markdown_file(tmp_path):
    file_path = tmp_path / "notes.md"
    file_path.write_text(
        "# Notes\n\nRedis is often used as a cache.",
        encoding="utf-8",
    )

    documents = MarkdownFileLoader(file_path).load()

    assert len(documents) == 1
    assert documents[0].text == "# Notes\n\nRedis is often used as a cache."
    assert documents[0].metadata["filename"] == "notes.md"
    assert documents[0].metadata["extension"] == ".md"
    assert documents[0].metadata["loader"] == "MarkdownFileLoader"


def test_directory_loader_loads_txt_and_md_files(tmp_path):
    txt_path = tmp_path / "notes.txt"
    md_path = tmp_path / "guide.md"
    ignored_path = tmp_path / "data.json"

    txt_path.write_text("Text notes.", encoding="utf-8")
    md_path.write_text("# Guide", encoding="utf-8")
    ignored_path.write_text('{"ignored": true}', encoding="utf-8")

    documents = DirectoryLoader(tmp_path).load()

    assert len(documents) == 2

    filenames = {document.metadata["filename"] for document in documents}

    assert filenames == {"notes.txt", "guide.md"}


def test_directory_loader_loads_recursively_when_enabled(tmp_path):
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    root_file = tmp_path / "root.txt"
    nested_file = nested_dir / "nested.txt"

    root_file.write_text("Root text.", encoding="utf-8")
    nested_file.write_text("Nested text.", encoding="utf-8")

    documents = DirectoryLoader(
        tmp_path,
        recursive=True,
    ).load()

    filenames = {document.metadata["filename"] for document in documents}

    assert filenames == {"root.txt", "nested.txt"}


def test_directory_loader_does_not_load_recursively_by_default(tmp_path):
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    root_file = tmp_path / "root.txt"
    nested_file = nested_dir / "nested.txt"

    root_file.write_text("Root text.", encoding="utf-8")
    nested_file.write_text("Nested text.", encoding="utf-8")

    documents = DirectoryLoader(tmp_path).load()

    filenames = {document.metadata["filename"] for document in documents}

    assert filenames == {"root.txt"}


def test_directory_loader_supports_custom_extensions(tmp_path):
    rst_path = tmp_path / "notes.rst"
    txt_path = tmp_path / "notes.txt"

    rst_path.write_text("RST notes.", encoding="utf-8")
    txt_path.write_text("Text notes.", encoding="utf-8")

    documents = DirectoryLoader(
        tmp_path,
        extensions={".rst"},
    ).load()

    assert len(documents) == 1
    assert documents[0].metadata["filename"] == "notes.rst"


def test_directory_loader_rejects_missing_directory(tmp_path):
    missing_dir = tmp_path / "missing"

    with pytest.raises(
        FileNotFoundError,
        match="Directory not found",
    ):
        DirectoryLoader(missing_dir).load()


def test_directory_loader_rejects_file_path(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Text notes.", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Path is not a directory",
    ):
        DirectoryLoader(file_path).load()
