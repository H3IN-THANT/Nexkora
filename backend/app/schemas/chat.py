from typing import Literal

from pydantic import BaseModel, Field, field_validator


ChatMode = Literal[
    "explain_code",
    "debug_code",
    "generate_code",
    "refactor_code",
    "generate_documentation",
    "explain_errors",
]


class ChatRequest(BaseModel):
    mode: ChatMode = Field(
        ...,
        description="Developer task mode.",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=12000,
        description="User input, source code, or error information.",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        return value


class ChatResponse(BaseModel):
    mode: ChatMode
    message: str
    response: str
    status: str