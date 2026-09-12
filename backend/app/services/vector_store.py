from pathlib import Path

try:
    import chromadb  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "ChromaDB is required for the vector store. Install it with "
        "'pip install chromadb'."
    ) from exc


VECTOR_DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "chroma"
)

COLLECTION_NAME = "nexkora_documents_v2"


class VectorStore:
    """Manage Nexkora's persistent ChromaDB collection."""

    def __init__(self) -> None:
        VECTOR_DB_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            configuration={
                "hnsw": {
                    "space": "cosine",
                }
            },
        )

    def count(self) -> int:
        """Return the number of stored document chunks."""

        return self.collection.count()

    def upsert_chunks(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """Store or update document chunks."""

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """Delete all indexed chunks belonging to a document."""

        self.collection.delete(
            where={
                "document_id": document_id,
            }
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 4,
    ) -> dict:
        """Find the nearest chunks for a query embedding."""

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )