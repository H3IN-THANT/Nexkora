from dataclasses import dataclass, field
from typing import Literal


EvaluationCategory = Literal[
    "relevance",
    "factuality",
    "code_explanation",
    "debugging",
    "rag",
    "hallucination",
    "failure_handling",
]

Difficulty = Literal[
    "easy",
    "medium",
    "hard",
]


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    category: EvaluationCategory
    question: str

    mode: str | None = None
    context: str | None = None

    expected_answer: str | None = None
    expected_facts: tuple[str, ...] = ()

    forbidden_facts: tuple[str, ...] = ()

    expected_sources: tuple[str, ...] = ()

    expected_http_status: int | None = None

    difficulty: Difficulty = "medium"
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    category: str
    response: str

    latency_ms: float | None

    scores: dict[str, float] = field(default_factory=dict)

    passed: bool = False

    notes: tuple[str, ...] = ()

    error: str | None = None


@dataclass(frozen=True)
class JudgeResult:
    score: float
    reason: str


@dataclass(frozen=True)
class RetrievalResult:
    retrieved_sources: tuple[str, ...]
    relevant_sources: tuple[str, ...]

    precision_at_k: float
    recall_at_k: float