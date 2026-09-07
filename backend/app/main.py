from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.chat import ChatRequest, ChatResponse


app = FastAPI(
    title="Nexkora API",
    description="Backend API for the Nexkora AI Developer Productivity Assistant.",
    version="0.2.0",
)


# Local development frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    mock_response = (
        "This response came from the FastAPI backend. "
        "OpenAI is not connected yet."
    )

    return ChatResponse(
        message=request.message,
        response=mock_response,
        status="success",
    )