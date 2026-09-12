import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


DEFAULT_EMBEDDING_MODEL = "gemini-embedding-2"
DEFAULT_OUTPUT_DIMENSIONALITY = 768


class EmbeddingService:
    """Generate embeddings for document retrieval."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        model = os.getenv(
            "GEMINI_EMBEDDING_MODEL",
            DEFAULT_EMBEDDING_MODEL,
        )

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def _embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate one embedding."""

        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot generate an embedding for empty text."
            )

        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=(
                    DEFAULT_OUTPUT_DIMENSIONALITY
                ),
            ),
        )

        if not result.embeddings:
            raise RuntimeError(
                "Gemini returned no embedding."
            )

        embedding = result.embeddings[0].values

        if not embedding:
            raise RuntimeError(
                "Gemini returned an empty embedding."
            )

        return list(embedding)

    def embed_document(
        self,
        text: str,
        title: str | None = None,
    ) -> list[float]:
        """Embed a document chunk for question-answering retrieval."""

        title = title or "none"

        formatted_text = (
            f"title: {title} | text: {text}"
        )

        return self._embed(formatted_text)

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """Embed a user question for question-answering retrieval."""

        formatted_query = (
            f"task: question answering | query: {query}"
        )

        return self._embed(formatted_query)

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """Generic embedding helper."""

        return self._embed(text)