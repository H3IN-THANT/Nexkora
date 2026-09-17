from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
}


@dataclass
class Document:
    document_id: str
    filename: str
    text: str
    chunks: list[str]
    metadata: dict[str, str] | None = None


class DocumentService:
    """Handle document validation, extraction, and chunking."""

    def validate_file(
        self,
        filename: str,
        content: bytes,
    ) -> None:
        """Validate document input before processing."""

        if not filename:
            raise ValueError(
                "A filename is required."
            )

        safe_filename = Path(filename).name

        if safe_filename != filename:
            raise ValueError(
                "Invalid filename."
            )

        extension = Path(safe_filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. "
                "Only .txt and .md files are allowed."
            )

        if len(safe_filename) > 255:
            raise ValueError(
                "Filename is too long."
            )

        if not content:
            raise ValueError(
                "The uploaded file is empty."
            )

        if len(content) > MAX_FILE_SIZE:
            raise ValueError(
                "File is too large. "
                "Maximum size is 2 MB."
            )

    def extract_text(
        self,
        content: bytes,
    ) -> str:
        """Decode UTF-8 text from document content."""

        try:
            text = content.decode(
                "utf-8",
                errors="strict",
            )

        except UnicodeDecodeError as exc:
            raise ValueError(
                "The document must be a valid UTF-8 text file."
            ) from exc

        text = text.strip()

        if not text:
            raise ValueError(
                "The document does not contain readable text."
            )

        return text

    def chunk_text(
        self,
        text: str,
    ) -> list[str]:
        """Split text into overlapping chunks."""

        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(
                start + CHUNK_SIZE,
                text_length,
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = end - CHUNK_OVERLAP

        return chunks

    def create_document(
        self,
        filename: str,
        content: bytes,
        document_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Document:
        """Validate, extract, and chunk a text document."""

        self.validate_file(
            filename,
            content,
        )

        text = self.extract_text(content)

        chunks = self.chunk_text(text)

        if not chunks:
            raise ValueError(
                "Unable to create document chunks."
            )

        return Document(
            document_id=document_id or str(uuid4()),
            filename=Path(filename).name,
            text=text,
            chunks=chunks,
            metadata=metadata,
        )