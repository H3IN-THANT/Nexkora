from app.services.document_service import (
    Document,
    DocumentService,
)
from app.services.github_document_service import (
    GitHubDocumentService,
)
from app.services.github_service import GitHubService
from app.services.rag_service import RAGService


class GitHubRAGService:
    """Index and retrieve information from GitHub repositories."""

    def __init__(
        self,
        github_service: GitHubService,
        github_document_service: GitHubDocumentService,
        document_service: DocumentService,
        rag_service: RAGService,
    ) -> None:
        self.github_service = github_service
        self.github_document_service = (
            github_document_service
        )
        self.document_service = document_service
        self.rag_service = rag_service

    def index_repository(
        self,
        repository_url: str,
    ) -> dict:
        repository = self.github_service.get_repository(
            repository_url
        )

        supported_files = (
            self.github_document_service.filter_files(
                repository.files
            )
        )

        repository_name = (
            f"{repository.owner}/{repository.name}"
        )

        indexed_files = 0
        indexed_chunks = 0

        for file in supported_files:
            try:
                text = (
                    self.github_document_service.extract_text(
                        file
                    )
                )
            except (ValueError, RuntimeError):
                continue

            if not text:
                continue

            document = Document(
    document_id=(
        f"github:"
        f"{repository.owner}/"
        f"{repository.name}:"
        f"{file.path}"
    ),
    filename=file.path,
    text=text,
    chunks=self.document_service.chunk_text(text),
    metadata={
        "repository": repository_name,
        "path": file.path,
    },
)

           

            chunk_count = self.rag_service.index_document(
                document
            )

            indexed_files += 1
            indexed_chunks += chunk_count

        return {
            "repository": repository_name,
            "default_branch": repository.default_branch,
            "files_discovered": len(repository.files),
            "files_supported": len(supported_files),
            "files_indexed": indexed_files,
            "chunks_indexed": indexed_chunks,
        }

    def retrieve_repository(
        self,
        repository: str,
        question: str,
        top_k: int = 6,
    ) -> list[dict]:
        """Retrieve relevant chunks from a specific GitHub repository."""

        repository_key = repository.strip()

        if "/" not in repository_key:
            raise ValueError(
                "Invalid repository format. Expected owner/name."
            )

        query_embedding = self.rag_service.embedding_service.embed_query(
            question
        )

        results = self.rag_service.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "repository": {
                    "$eq": repository_key
                }
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

        retrieved_chunks: list[dict] = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved_chunks.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return retrieved_chunks