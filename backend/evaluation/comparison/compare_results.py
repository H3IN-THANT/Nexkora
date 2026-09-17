from __future__ import annotations

import argparse
import json
from pathlib import Path


COMPARISON_METRICS = (
    "llm_judge",
    "expected_fact_coverage",
    "hallucination_free",
    "forbidden_fact_rate",
)


def load_results(
    path: Path,
) -> dict[str, dict]:
    results: dict[str, dict] = {}

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            result = json.loads(line)

            case_id = result["case_id"]

            results[case_id] = result

    return results


def compare_results(
    baseline: dict[str, dict],
    candidate: dict[str, dict],
) -> list[dict]:

    case_ids = sorted(
        set(baseline) | set(candidate)
    )

    comparisons: list[dict] = []

    for case_id in case_ids:

        baseline_result = baseline.get(
            case_id
        )

        candidate_result = candidate.get(
            case_id
        )

        if not baseline_result:
            comparisons.append({
                "case_id": case_id,
                "status": "candidate_only",
            })
            continue

        if not candidate_result:
            comparisons.append({
                "case_id": case_id,
                "status": "baseline_only",
            })
            continue

        metric_changes: dict[str, float | None] = {}

        for metric in COMPARISON_METRICS:

            baseline_value = (
                baseline_result
                .get("scores", {})
                .get(metric)
            )

            candidate_value = (
                candidate_result
                .get("scores", {})
                .get(metric)
            )

            if (
                baseline_value is None
                or candidate_value is None
            ):
                metric_changes[metric] = None
            else:
                metric_changes[metric] = (
                    candidate_value
                    - baseline_value
                )

        baseline_latency = (
            baseline_result.get("latency_ms")
        )

        candidate_latency = (
            candidate_result.get("latency_ms")
        )

        latency_change = None

        if (
            baseline_latency is not None
            and candidate_latency is not None
        ):
            latency_change = (
                candidate_latency
                - baseline_latency
            )

        if (
            candidate_result.get("passed")
            and not baseline_result.get("passed")
        ):
            status = "improved"

        elif (
            baseline_result.get("passed")
            and not candidate_result.get("passed")
        ):
            status = "regressed"

        else:
            status = "unchanged"

        comparisons.append({
            "case_id": case_id,
            "status": status,
            "metric_changes": metric_changes,
            "latency_change_ms": latency_change,
            "baseline_passed": baseline_result.get(
                "passed"
            ),
            "candidate_passed": candidate_result.get(
                "passed"
            ),
        })

    return comparisons


def summarise_comparison(
    comparisons: list[dict],
) -> dict:

    summary = {
        "total_cases": len(comparisons),
        "improved": 0,
        "regressed": 0,
        "unchanged": 0,
        "candidate_only": 0,
        "baseline_only": 0,
    }

    for comparison in comparisons:

        status = comparison["status"]

        if status in summary:
            summary[status] += 1

    metric_summary: dict[str, dict] = {}

    for metric in COMPARISON_METRICS:

        changes = [
            item["metric_changes"][metric]
            for item in comparisons
            if (
                item.get("metric_changes")
                and item["metric_changes"].get(metric)
                is not None
            )
        ]

        if changes:

            metric_summary[metric] = {
                "average_change": (
                    sum(changes)
                    / len(changes)
                ),
                "improved_cases": sum(
                    1 for value in changes
                    if value > 0
                ),
                "regressed_cases": sum(
                    1 for value in changes
                    if value < 0
                ),
                "unchanged_cases": sum(
                    1 for value in changes
                    if value == 0
                ),
            }

    summary["metrics"] = metric_summary

    return summary


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Compare two Nexkora evaluation runs."
        )
    )

    parser.add_argument(
        "--baseline",
        required=True,
        help="Baseline JSONL file.",
    )

    parser.add_argument(
        "--candidate",
        required=True,
        help="Candidate JSONL file.",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON comparison output.",
    )

    args = parser.parse_args()

    baseline_path = Path(
        args.baseline
    )

    candidate_path = Path(
        args.candidate
    )

    baseline = load_results(
        baseline_path
    )

    candidate = load_results(
        candidate_path
    )

    comparisons = compare_results(
        baseline=baseline,
        candidate=candidate,
    )

    summary = summarise_comparison(
        comparisons
    )

    output = {
        "summary": summary,
        "cases": comparisons,
    }

    if args.output:

        output_path = Path(
            args.output
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()