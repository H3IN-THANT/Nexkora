from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The user's chat message.",
    )


class ChatResponse(BaseModel):
    message: str
    response: str
    status: str