from app.services.document_service import Document
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

MAX_DISTANCE = 0.65

class RAGService:
    """Coordinate document indexing and vector retrieval."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_document(
        self,
        document: Document,
    ) -> int:
        """Embed and store every chunk of a document."""

        if not document.chunks:
            raise ValueError(
                "Cannot index a document without chunks."
            )

        self.vector_store.delete_document(
            document.document_id
        )

        ids: list[str] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict] = []

        for index, chunk in enumerate(document.chunks):
            chunk_id = (
                f"{document.document_id}:{index}"
            )

            embedding = (
                self.embedding_service.embed_document(
                    text=chunk,
                    title=document.filename,
                )
            )

            ids.append(chunk_id)
            documents.append(chunk)
            embeddings.append(embedding)

            metadatas.append(
                {
                    "document_id": document.document_id,
                    "filename": document.filename,
                    "chunk_index": index,
                }
            )

        self.vector_store.upsert_chunks(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(documents)

    def retrieve(
        self,
        question: str,
        document_id: str,
        top_k: int = 4,
    ) -> list[dict]:
        """Retrieve relevant chunks using vector similarity."""

        query_embedding = (
            self.embedding_service.embed_query(
                question
            )
        )

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "document_id": document_id,
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            if distance > MAX_DISTANCE:
              continue
            retrieved_chunks.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return retrieved_chunks