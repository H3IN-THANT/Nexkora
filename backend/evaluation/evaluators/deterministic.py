from __future__ import annotations

import re

from evaluation.models import RetrievalResult


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_expected_facts(
    response: str,
    expected_facts: tuple[str, ...],
) -> tuple[float, list[str]]:
    if not expected_facts:
        return 1.0, []

    normalized_response = _normalise(response)

    matched: list[str] = []

    for fact in expected_facts:
        normalized_fact = _normalise(fact).rstrip(".")

        if normalized_fact in normalized_response:
            matched.append(fact)

    score = len(matched) / len(expected_facts)

    return score, matched


def contains_forbidden_facts(
    response: str,
    forbidden_facts: tuple[str, ...],
) -> tuple[float, list[str]]:
    if not forbidden_facts:
        return 0.0, []

    normalized_response = _normalise(response)

    found: list[str] = []

    for fact in forbidden_facts:
        normalized_fact = _normalise(fact).rstrip(".")

        if normalized_fact in normalized_response:
            found.append(fact)

    score = len(found) / len(forbidden_facts)

    return score, found


def exact_or_contains_expected_answer(
    response: str,
    expected_answer: str | None,
) -> bool:
    if not expected_answer:
        return True

    return (
        _normalise(expected_answer)
        in _normalise(response)
    )


def retrieval_precision_recall(
    retrieved_sources: tuple[str, ...],
    relevant_sources: tuple[str, ...],
) -> RetrievalResult:

    retrieved = tuple(
        dict.fromkeys(retrieved_sources)
    )

    relevant = tuple(
        dict.fromkeys(relevant_sources)
    )

    if not relevant:
        return RetrievalResult(
            retrieved_sources=retrieved,
            relevant_sources=relevant,
            precision_at_k=(
                1.0 if not retrieved else 0.0
            ),
            recall_at_k=1.0,
        )

    retrieved_set = set(retrieved)
    relevant_set = set(relevant)

    hits = len(
        retrieved_set & relevant_set
    )

    precision = (
        hits / len(retrieved_set)
        if retrieved_set
        else 0.0
    )

    recall = hits / len(relevant_set)

    return RetrievalResult(
        retrieved_sources=retrieved,
        relevant_sources=relevant,
        precision_at_k=precision,
        recall_at_k=recall,
    )


def response_hallucinates(
    response: str,
    forbidden_facts: tuple[str, ...],
) -> bool:
    _, found = contains_forbidden_facts(
        response=response,
        forbidden_facts=forbidden_facts,
    )

    return bool(found)


def has_non_empty_response(
    response: str,
) -> bool:
    return bool(
        response and response.strip()
    )


def validate_http_status(
    actual_status: int,
    expected_status: int,
) -> bool:
    return actual_status == expected_status