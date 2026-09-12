from pydantic import BaseModel, Field, field_validator


class DocumentQuestion(BaseModel):
    document_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    @field_validator("document_id", "question")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty."
            )

        return value


class DocumentAnswer(BaseModel):
    document_id: str
    question: str
    answer: str
    status: str