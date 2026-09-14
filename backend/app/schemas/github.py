from pydantic import BaseModel, Field


class GitHubIndexRequest(BaseModel):
    repository_url: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Public GitHub repository URL.",
    )


class GitHubIndexResponse(BaseModel):
    repository: str
    default_branch: str
    files_discovered: int
    files_supported: int
    files_indexed: int
    chunks_indexed: int
    status: str

class GitHubQuestionRequest(BaseModel):
    repository: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Repository in owner/name format.",
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Question about the GitHub repository.",
    )


class GitHubQuestionResponse(BaseModel):
    repository: str
    question: str
    answer: str
    sources: list[str]
    status: str