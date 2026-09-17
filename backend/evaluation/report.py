from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median


def load_results(
    path: Path,
) -> list[dict]:

    results = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                results.append(
                    json.loads(line)
                )

    return results


def calculate_report(
    results: list[dict],
) -> dict:

    total = len(results)

    if total == 0:
        return {
            "total_cases": 0,
            "message": "No evaluation results found.",
        }

    passed = sum(
        1
        for result in results
        if result.get("passed")
    )

    failed = total - passed

    latencies = [
        result["latency_ms"]
        for result in results
        if result.get("latency_ms") is not None
    ]

    report = {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "pass_rate": passed / total,
    }

    if latencies:

        sorted_latencies = sorted(
            latencies
        )

        p95_index = min(
            len(sorted_latencies) - 1,
            int(
                len(sorted_latencies) * 0.95
            ),
        )

        report["latency_ms"] = {
            "average": mean(latencies),
            "median": median(latencies),
            "p95": sorted_latencies[
                p95_index
            ],
            "minimum": min(latencies),
            "maximum": max(latencies),
        }

    metric_values: dict[
        str,
        list[float],
    ] = {}

    for result in results:

        for metric, value in (
            result.get("scores", {})
            .items()
        ):

            if not isinstance(
                value,
                (int, float),
            ):
                continue

            metric_values.setdefault(
                metric,
                [],
            ).append(
                float(value)
            )

    report["metrics"] = {}

    for metric, values in metric_values.items():

        report["metrics"][metric] = {
            "average": mean(values),
            "minimum": min(values),
            "maximum": max(values),
        }

    categories: dict[
        str,
        list[dict],
    ] = {}

    for result in results:

        categories.setdefault(
            result["category"],
            [],
        ).append(result)

    report["categories"] = {}

    for category, category_results in (
        categories.items()
    ):

        category_total = len(
            category_results
        )

        category_passed = sum(
            1
            for result in category_results
            if result.get("passed")
        )

        category_report = {
            "total": category_total,
            "passed": category_passed,
            "failed": (
                category_total
                - category_passed
            ),
            "pass_rate": (
                category_passed
                / category_total
            ),
        }

        report["categories"][
            category
        ] = category_report

    return report


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Generate a Nexkora evaluation report."
        )
    )

    parser.add_argument(
        "--input",
        default=(
            "evaluation/results/"
            "evaluation.jsonl"
        ),
    )

    parser.add_argument(
        "--output",
        default=(
            "evaluation/results/"
            "report.json"
        ),
    )

    args = parser.parse_args()

    input_path = Path(
        args.input
    )

    output_path = Path(
        args.output
    )

    results = load_results(
        input_path
    )

    report = calculate_report(
        results
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()