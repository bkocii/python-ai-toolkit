from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field

from ai.embeddings import EmbeddingInput


class Document(BaseModel):
    """
    Provider-independent document loaded from a source.

    text:
        Text content extracted from the source.

    metadata:
        Source information such as path, filename, extension, loader type,
        database table, row ID, or document type.
    """

    text: str
    metadata: dict[str, str] = Field(default_factory=dict)


class BaseDocumentLoader(ABC):
    """
    Base interface for document loaders.
    """

    @abstractmethod
    def load(self) -> list[Document]:
        """
        Load documents from a source.
        """
        raise NotImplementedError


def documents_to_embedding_inputs(
    documents: list[Document],
) -> list[EmbeddingInput]:
    """
    Convert loaded documents into embedding inputs.
    """
    return [
        EmbeddingInput(
            text=document.text,
            metadata=document.metadata,
        )
        for document in documents
    ]


def normalize_path(path: str | Path) -> Path:
    """
    Convert a string or Path into an expanded Path object.
    """
    return Path(path).expanduser()


class TextFileLoader(BaseDocumentLoader):
    """
    Load a plain text file into a Document.
    """

    def __init__(
        self,
        path: str | Path,
        encoding: str = "utf-8",
    ):
        self.path = normalize_path(path)
        self.encoding = encoding

    def load(self) -> list[Document]:
        if not self.path.exists():
            raise FileNotFoundError(f"Text file not found: {self.path}")

        if not self.path.is_file():
            raise ValueError(f"Path is not a file: {self.path}")

        text = self.path.read_text(encoding=self.encoding)

        if not text.strip():
            return []

        return [
            Document(
                text=text,
                metadata={
                    "source": str(self.path),
                    "filename": self.path.name,
                    "extension": self.path.suffix.lower(),
                    "loader": self.__class__.__name__,
                },
            )
        ]


class MarkdownFileLoader(TextFileLoader):
    """
    Load a Markdown file into a Document.

    Markdown is loaded as plain text for now.
    Markdown-specific parsing can be added later.
    """


class DirectoryLoader(BaseDocumentLoader):
    """
    Load supported documents from a directory.
    """

    def __init__(
        self,
        path: str | Path,
        recursive: bool = False,
        encoding: str = "utf-8",
        extensions: set[str] | None = None,
    ):
        self.path = normalize_path(path)
        self.recursive = recursive
        self.encoding = encoding
        self.extensions = extensions or {".txt", ".md"}

    def load(self) -> list[Document]:
        if not self.path.exists():
            raise FileNotFoundError(f"Directory not found: {self.path}")

        if not self.path.is_dir():
            raise ValueError(f"Path is not a directory: {self.path}")

        pattern = "**/*" if self.recursive else "*"

        documents: list[Document] = []

        for file_path in sorted(self.path.glob(pattern)):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.extensions:
                continue

            loader = self._loader_for_file(file_path)
            documents.extend(loader.load())

        return documents

    def _loader_for_file(
        self,
        file_path: Path,
    ) -> BaseDocumentLoader:
        extension = file_path.suffix.lower()

        if extension == ".md":
            return MarkdownFileLoader(
                path=file_path,
                encoding=self.encoding,
            )

        return TextFileLoader(
            path=file_path,
            encoding=self.encoding,
        )
