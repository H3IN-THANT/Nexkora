from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from dotenv import load_dotenv

from app.prompts.registry import get_prompt
from app.services.ai_service import AIService

from evaluation.datasets.evaluation_cases import (
    get_evaluation_cases,
)

from evaluation.evaluators.deterministic import (
    contains_expected_facts,
    contains_forbidden_facts,
)

from evaluation.evaluators.llm_judge import (
    LLMJudge,
)

from evaluation.models import (
    EvaluationCase,
    EvaluationResult,
)


RESULTS_DIR = (
    Path(__file__).resolve().parents[1]
    / "results"
)


JUDGE_DIMENSIONS = {
    "relevance": "relevance",
    "factuality": "factuality",
    "code_explanation": "code_explanation",
    "debugging": "debugging",
    "rag": "rag",
    "hallucination": "hallucination",
}


class EvaluationRunner:
    def __init__(
        self,
        ai_service: AIService | None = None,
        judge: LLMJudge | None = None,
        enable_judge: bool = True,
    ) -> None:
        self.ai_service = (
            ai_service
            or AIService()
        )

        self.judge = None

        if enable_judge:
            self.judge = (
                judge
                or LLMJudge(
                    ai_service=self.ai_service
                )
            )

    def _run_developer_case(
        self,
        case: EvaluationCase,
    ) -> tuple[str, float]:

        if not case.mode:
            raise ValueError(
                f"Case {case.case_id} has no developer mode."
            )

        system_prompt, prompt_builder = (
            get_prompt(case.mode)
        )

        user_prompt = prompt_builder(
            case.question
        )

        start = time.perf_counter()

        response = (
            self.ai_service.generate_response(
                user_input=user_prompt,
                system_instruction=system_prompt,
            )
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return response, latency_ms

    def _run_document_qa_case(
        self,
        case: EvaluationCase,
    ) -> tuple[str, float]:

        if not case.context:
            raise ValueError(
                f"Case {case.case_id} requires context."
            )

        start = time.perf_counter()

        response = (
            self.ai_service.answer_document_question(
                question=case.question,
                context=case.context,
            )
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return response, latency_ms

    def evaluate_case(
        self,
        case: EvaluationCase,
    ) -> EvaluationResult:

        # Failure handling cases are tested at HTTP/API level
        # rather than by sending them to the LLM.
        if case.category == "failure_handling":
            return EvaluationResult(
                case_id=case.case_id,
                category=case.category,
                response="HTTP endpoint test case.",
                latency_ms=None,
                scores={},
                passed=False,
                notes=(
                    "Requires API-level integration test.",
                ),
            )

        try:
            # -------------------------------------------------
            # Generate response
            # -------------------------------------------------

            if case.category in {
                "rag",
                "hallucination",
            }:
                response, latency_ms = (
                    self._run_document_qa_case(
                        case
                    )
                )
            else:
                response, latency_ms = (
                    self._run_developer_case(
                        case
                    )
                )

            scores: dict[str, float] = {}
            notes: list[str] = []

            # -------------------------------------------------
            # Expected fact coverage
            # -------------------------------------------------

            expected_fact_score = 1.0

            if case.expected_facts:
                fact_score, matched = (
                    contains_expected_facts(
                        response=response,
                        expected_facts=case.expected_facts,
                    )
                )

                expected_fact_score = fact_score

                scores["expected_fact_coverage"] = (
                    fact_score
                )

                notes.append(
                    "Matched facts: "
                    + ", ".join(matched)
                )

            # -------------------------------------------------
            # Forbidden facts / hallucination
            # -------------------------------------------------

            hallucination = False

            if case.forbidden_facts:
                forbidden_score, found = (
                    contains_forbidden_facts(
                        response=response,
                        forbidden_facts=case.forbidden_facts,
                    )
                )

                hallucination = bool(found)

                scores["forbidden_fact_rate"] = (
                    forbidden_score
                )

                if found:
                    notes.append(
                        "Forbidden claims found: "
                        + ", ".join(found)
                    )

            scores["hallucination_free"] = (
                0.0
                if hallucination
                else 1.0
            )

            # -------------------------------------------------
            # LLM Judge
            # -------------------------------------------------

            dimension = JUDGE_DIMENSIONS.get(
                case.category
            )

            if (
                self.judge is not None
                and dimension
            ):
                judge_result = (
                    self.judge.evaluate(
                        dimension=dimension,
                        question=case.question,
                        answer=response,
                        context=case.context,
                    )
                )

                scores["llm_judge"] = (
                    judge_result.score / 5.0
                )

                notes.append(
                    "Judge: "
                    + judge_result.reason
                )

            # -------------------------------------------------
            # Pass condition
            # -------------------------------------------------

            if self.judge is not None and dimension:
                # When LLM-as-a-Judge is enabled,
                # use the judge score together with
                # hallucination detection.
                judge_score = scores.get(
                    "llm_judge",
                    0.0,
                )

                passed = (
                    judge_score >= 0.60
                    and not hallucination
                )

            else:
                # When the judge is disabled,
                # use deterministic evaluation only.
                passed = (
                    expected_fact_score >= 0.60
                    and not hallucination
                )

            return EvaluationResult(
                case_id=case.case_id,
                category=case.category,
                response=response,
                latency_ms=round(
                    latency_ms,
                    2,
                ),
                scores=scores,
                passed=passed,
                notes=tuple(notes),
            )

        except Exception as exc:
            # API/model/runtime errors are recorded separately
            # from normal evaluation failures.
            return EvaluationResult(
                case_id=case.case_id,
                category=case.category,
                response="",
                latency_ms=None,
                scores={},
                passed=False,
                notes=(
                    "Evaluation could not be completed "
                    "because the model/API request failed.",
                ),
                error=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )


def _result_to_dict(
    result: EvaluationResult,
) -> dict:

    return {
        "case_id": result.case_id,
        "category": result.category,
        "response": result.response,
        "latency_ms": result.latency_ms,
        "scores": result.scores,
        "passed": result.passed,
        "notes": list(result.notes),
        "error": result.error,
    }


def run_evaluation(
    cases: list[EvaluationCase],
    output_path: Path,
    enable_judge: bool = True,
) -> None:

    runner = EvaluationRunner(
        enable_judge=enable_judge,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for index, case in enumerate(
            cases,
            start=1,
        ):

            print(
                f"[{index}/{len(cases)}] "
                f"{case.case_id}"
            )

            result = runner.evaluate_case(
                case
            )

            file.write(
                json.dumps(
                    _result_to_dict(result),
                    ensure_ascii=False,
                )
                + "\n"
            )

            status = (
                "PASS"
                if result.passed
                else "FAIL"
            )

            print(
                f"    {status}"
            )

            if result.latency_ms is not None:
                print(
                    f"    latency: "
                    f"{result.latency_ms:.2f} ms"
                )

            if result.error:
                print(
                    f"    error: "
                    f"{result.error}"
                )


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "Run Nexkora evaluation dataset."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Run only the first N evaluation cases."
        ),
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=(
            "Output JSONL file path."
        ),
    )

    parser.add_argument(
        "--skip-judge",
        action="store_true",
        help=(
            "Skip LLM-as-a-Judge evaluation "
            "to reduce Gemini API usage."
        ),
    )

    args = parser.parse_args()

    cases = list(
        get_evaluation_cases()
    )

    if args.limit is not None:
        if args.limit <= 0:
            parser.error(
                "--limit must be greater than 0."
            )

        cases = cases[:args.limit]

    output_path = (
        Path(args.output)
        if args.output
        else RESULTS_DIR / "evaluation.jsonl"
    )

    judge_enabled = not args.skip_judge

    print(
        f"Running {len(cases)} evaluation cases."
    )

    print(
        f"Results will be written to: "
        f"{output_path}"
    )

    print(
        "LLM Judge: "
        + (
            "DISABLED"
            if not judge_enabled
            else "ENABLED"
        )
    )

    run_evaluation(
        cases=cases,
        output_path=output_path,
        enable_judge=judge_enabled,
    )

    print(
        "\nEvaluation complete."
    )


if __name__ == "__main__":
    main()