from evaluation.datasets.evaluation_cases import (
    get_evaluation_cases,
)

from evaluation.evaluators.deterministic import (
    contains_expected_facts,
    contains_forbidden_facts,
    retrieval_precision_recall,
)

from evaluation.models import EvaluationCase


def test_dataset_has_unique_case_ids():

    cases = get_evaluation_cases()

    ids = [
        case.case_id
        for case in cases
    ]

    assert len(cases) == 30

    assert len(ids) == len(
        set(ids)
    )


def test_dataset_cases_use_valid_types():

    for case in get_evaluation_cases():

        assert isinstance(
            case,
            EvaluationCase,
        )

        assert case.case_id

        assert case.category

        assert case.question is not None


def test_expected_fact_coverage():

    score, matched = (
        contains_expected_facts(
            response=(
                "The function removes duplicate "
                "values and preserves insertion "
                "order. It returns a list."
            ),
            expected_facts=(
                "removes duplicate values",
                "preserves insertion order",
                "returns a list",
            ),
        )
    )

    assert score == 1.0

    assert len(matched) == 3


def test_forbidden_fact_detection():

    score, found = (
        contains_forbidden_facts(
            response=(
                "This implementation uses Auth0 "
                "for authentication."
            ),
            forbidden_facts=(
                "Auth0",
                "Firebase",
            ),
        )
    )

    assert score == 0.5

    assert found == ["Auth0"]


def test_retrieval_precision_and_recall():

    result = (
        retrieval_precision_recall(
            retrieved_sources=(
                "a",
                "b",
                "c",
            ),
            relevant_sources=(
                "a",
                "c",
            ),
        )
    )

    assert result.precision_at_k == 2 / 3

    assert result.recall_at_k == 1.0