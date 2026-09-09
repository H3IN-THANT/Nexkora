from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.prompts.registry import get_prompt
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService


load_dotenv()


app = FastAPI(
    title="Nexkora API",
    description=(
        "Backend API for the Nexkora "
        "AI Developer Productivity Assistant."
    ),
    version="0.5.0",
)


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