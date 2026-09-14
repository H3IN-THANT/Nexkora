from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class EmbeddingService:
    """Generate local embeddings for document retrieval."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            DEFAULT_EMBEDDING_MODEL
        )

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

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_document(
        self,
        text: str,
        title: str | None = None,
    ) -> list[float]:
        """Embed a document chunk for retrieval."""

        title = title or "none"

        formatted_text = (
            f"title: {title} | text: {text}"
        )

        return self._embed(formatted_text)

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """Embed a user question for retrieval."""

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