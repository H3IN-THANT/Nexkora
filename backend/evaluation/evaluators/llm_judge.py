from __future__ import annotations

import json
import re

from app.services.ai_service import AIService
from evaluation.models import JudgeResult


JUDGE_SYSTEM_PROMPT = """
You are an evaluation judge for an AI developer productivity assistant.

Evaluate the assistant's answer against the user's question and,
when provided, the supplied context.

Return ONLY valid JSON in this exact structure:

{
  "score": 1,
  "reason": "brief explanation"
}

The score must be an integer from 1 to 5.

Scoring rubric:

1 = Incorrect, irrelevant, or seriously misleading.
2 = Partially correct but has major problems.
3 = Mostly correct but incomplete or has noticeable issues.
4 = Correct, relevant, useful, and has only minor issues.
5 = Correct, highly relevant, clear, complete, and technically strong.

Evaluation dimensions:

relevance:
- Does the answer directly address the question?
- Avoid unrelated information.

factuality:
- Are technical claims correct?
- Penalize unsupported or incorrect claims.

code_explanation:
- Is the code explained correctly?
- Does the explanation cover important behavior?
- Is the explanation clear and precise?

debugging:
- Does it identify the likely cause?
- Does it provide a correct fix?
- Is the fix actionable?
- Does it explain why the fix works?

rag:
- Is the answer grounded in the supplied context?
- Does it avoid unsupported claims?

hallucination:
- Does the assistant acknowledge when the context
  does not contain enough information?
- Penalize invented implementation details.

Do not reward confident guessing.
""".strip()


def _extract_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
        )
        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM judge returned invalid JSON."
        ) from exc


class LLMJudge:

    def __init__(
        self,
        ai_service: AIService | None = None,
    ) -> None:
        self.ai_service = (
            ai_service
            or AIService()
        )

    def evaluate(
        self,
        dimension: str,
        question: str,
        answer: str,
        context: str | None = None,
    ) -> JudgeResult:

        prompt = f"""
<dimension>
{dimension}
</dimension>

<question>
{question}
</question>

<context>
{context or "No additional context was provided."}
</context>

<assistant_answer>
{answer}
</assistant_answer>

Evaluate the assistant answer according to the rubric.
Return JSON only.
""".strip()

        response = self.ai_service.generate_response(
            user_input=prompt,
            system_instruction=JUDGE_SYSTEM_PROMPT,
        )

        data = _extract_json(response)

        score = data.get("score")
        reason = data.get("reason")

        if not isinstance(score, int):
            raise ValueError(
                "LLM judge score must be an integer."
            )

        if score < 1 or score > 5:
            raise ValueError(
                "LLM judge score must be between 1 and 5."
            )

        if not isinstance(reason, str):
            raise ValueError(
                "LLM judge reason must be a string."
            )

        return JudgeResult(
            score=float(score),
            reason=reason.strip(),
        )