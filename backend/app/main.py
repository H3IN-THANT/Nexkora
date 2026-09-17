from fastapi.responses import JSONResponse

from app.services.rag_service import RAGService
from app.services.vector_store import VectorStore

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.prompts.registry import get_prompt
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.services.document_service import DocumentService

from app.api.routes import github

from app.schemas.document import (
    DocumentAnswer,
    DocumentQuestion,
)
from app.services.document_service import (
    DocumentService,
    MAX_FILE_SIZE,
)
from app.services.embedding_service import EmbeddingService
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware

from app.utils.rate_limiter import (
    InMemoryRateLimiter,
    RateLimitRule,
)
load_dotenv()
document_service = DocumentService()

documents = {}

vector_store = VectorStore()
embedding_service = EmbeddingService()

rag_service = RAGService(
    embedding_service=embedding_service,
    vector_store=vector_store,
)

app = FastAPI(
    title="Nexkora API",
    description=(
        "Backend API for the Nexkora "
        "AI Developer Productivity Assistant."
    ),
    version="0.5.0",
)

app.include_router(
    github.router,
    prefix="/api/v1",
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

RATE_LIMIT_RULES = {
    "/api/v1/chat": RateLimitRule(
        max_requests=20,
        window_seconds=60,
    ),
    "/api/v1/documents/ask": RateLimitRule(
        max_requests=20,
        window_seconds=60,
    ),
    "/api/v1/documents/upload": RateLimitRule(
        max_requests=5,
        window_seconds=60,
    ),
    "/api/v1/github/ask": RateLimitRule(
        max_requests=20,
        window_seconds=60,
    ),
    "/api/v1/github/index": RateLimitRule(
        max_requests=3,
        window_seconds=600,
    ),
}

rate_limiter = InMemoryRateLimiter(
    rules=RATE_LIMIT_RULES,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def rate_limit_requests(
    request: Request,
    call_next,
):
    path = request.url.path

    if path in RATE_LIMIT_RULES:
        client_id = (
            request.client.host
            if request.client
            else "unknown"
        )

        allowed, retry_after = (
            rate_limiter.check(
                client_id=client_id,
                path=path,
            )
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Too many requests. "
                        "Please try again later."
                    )
                },
                headers={
                    "Retry-After": str(
                        retry_after
                    ),
                },
            )

    return await call_next(request)
rag_service = RAGService(
    embedding_service=embedding_service,
    vector_store=vector_store,
)

ai_service = AIService()

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Nexkora API",
    }


@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):
    try:
        system_prompt, prompt_builder = get_prompt(
            request.mode
        )

        user_prompt = prompt_builder(
            request.message
        )

        response = ai_service.generate_response(
            user_input=user_prompt,
            system_instruction=system_prompt,
        )

        return ChatResponse(
            mode=request.mode,
            message=request.message,
            response=response,
            status="success",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"AI service error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable.",
        ) from exc

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    try:
        filename = file.filename or "uploaded_document"

        content = await file.read(
            MAX_FILE_SIZE + 1
        )

        document = document_service.create_document(
            filename=filename,
            content=content,
        )

        documents[document.document_id] = document

        indexed_chunk_count = rag_service.index_document(
            document
        )

        return {
            "document_id": document.document_id,
            "filename": document.filename,
            "chunk_count": len(document.chunks),
            "indexed_chunk_count": indexed_chunk_count,
            "status": "success",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"Document upload error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process the document.",
        ) from exc

@app.post(
    "/api/v1/documents/ask",
    response_model=DocumentAnswer,
)
async def ask_document(
    request: DocumentQuestion,
):
    document = documents.get(
        request.document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload the document again.",
        )

    try:
        retrieved_chunks = rag_service.retrieve(
            question=request.question,
            document_id=request.document_id,
            top_k=4,
        )

        if not retrieved_chunks:
            return DocumentAnswer(
                document_id=document.document_id,
                question=request.question,
                answer=(
                    "I couldn't find enough relevant information "
                    "in the retrieved document context to answer "
                    "this question."
                ),
                status="no_relevant_context",
            )

        context = "\n\n---\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )
        answer = ai_service.answer_document_question(
            question=request.question,
            context=context,
        )

        return DocumentAnswer(
            document_id=document.document_id,
            question=request.question,
            answer=answer,
            status="success",
        )

    except Exception as exc:
        print(
            f"Document Q&A error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to answer the document question.",
        ) from exc

