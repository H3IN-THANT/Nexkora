from fastapi import APIRouter, HTTPException

from app.schemas.github import (
    GitHubIndexRequest,
    GitHubIndexResponse,
    GitHubQuestionRequest,
    GitHubQuestionResponse,
)
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.github_document_service import (
    GitHubDocumentService,
)
from app.services.github_rag_service import GitHubRAGService
from app.services.github_service import GitHubService
from app.services.rag_service import RAGService
from app.services.vector_store import VectorStore
from app.services.ai_service import AIService


router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
)


@router.post(
    "/index",
    response_model=GitHubIndexResponse,
)
def index_github_repository(
    request: GitHubIndexRequest,
) -> GitHubIndexResponse:
    github_service = GitHubService()
    github_document_service = GitHubDocumentService()

    try:
        document_service = DocumentService()
        embedding_service = EmbeddingService()
        vector_store = VectorStore()

        rag_service = RAGService(
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        github_rag_service = GitHubRAGService(
            github_service=github_service,
            github_document_service=github_document_service,
            document_service=document_service,
            rag_service=rag_service,
        )

        result = github_rag_service.index_repository(
            repository_url=request.repository_url,
        )

        return GitHubIndexResponse(
            **result,
            status="indexed",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    finally:
        github_service.close()
        github_document_service.close()

@router.post(
    "/ask",
    response_model=GitHubQuestionResponse,
)
def ask_github_repository(
    request: GitHubQuestionRequest,
) -> GitHubQuestionResponse:
    github_service = GitHubService()
    github_document_service = GitHubDocumentService()

    try:
        document_service = DocumentService()
        embedding_service = EmbeddingService()
        vector_store = VectorStore()

        rag_service = RAGService(
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        github_rag_service = GitHubRAGService(
            github_service=github_service,
            github_document_service=github_document_service,
            document_service=document_service,
            rag_service=rag_service,
        )

        chunks = github_rag_service.retrieve_repository(
            repository=request.repository,
            question=request.question,
            top_k=6,
        )

        if not chunks:
            return GitHubQuestionResponse(
                repository=request.repository,
                question=request.question,
                answer=(
                    "I couldn't find relevant information "
                    "in the indexed repository."
                ),
                sources=[],
                status="no_relevant_context",
            )

        context_parts = []

        for chunk in chunks:
            metadata = chunk["metadata"]

            file_path = metadata.get(
                "filename",
                "unknown file",
            )

            context_parts.append(
                f"Source file: {file_path}\n"
                f"{chunk['text']}"
            )

        context = "\n\n---\n\n".join(
            context_parts
        )

        ai_service = AIService()

        answer = ai_service.answer_document_question(
            question=request.question,
            context=context,
        )

        sources = list(
            dict.fromkeys(
                chunk["metadata"].get(
                    "filename",
                    "unknown file",
                )
                for chunk in chunks
            )
        )

        return GitHubQuestionResponse(
            repository=request.repository,
            question=request.question,
            answer=answer,
            sources=sources,
            status="success",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    finally:
        github_service.close()
        github_document_service.close()