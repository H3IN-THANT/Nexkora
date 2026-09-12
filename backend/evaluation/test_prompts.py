from app.prompts.registry import PROMPT_REGISTRY
from evaluation.prompt_cases import PROMPT_CASES


EXPECTED_MODES = {
    "explain_code",
    "debug_code",
    "generate_code",
    "refactor_code",
    "generate_documentation",
    "explain_errors",
    "document_qa",
}


def test_all_prompt_modes_are_registered():
    assert set(PROMPT_REGISTRY.keys()) == EXPECTED_MODES


def test_all_prompts_have_system_prompts():
    for system_prompt, builder in PROMPT_REGISTRY.values():
        assert system_prompt.strip()
        assert callable(builder)


def test_all_evaluation_modes_are_registered():
    for case in PROMPT_CASES:
        assert case.mode in PROMPT_REGISTRY


def test_all_evaluation_cases_have_required_fields():
    for case in PROMPT_CASES:
        assert case.case_id.strip()
        assert case.mode.strip()
        assert case.input_data
        assert case.expected_behavior


def test_evaluation_case_ids_are_unique():
    case_ids = [case.case_id for case in PROMPT_CASES]

    assert len(case_ids) == len(set(case_ids))

def test_all_prompt_builders_return_non_empty_prompts():
    for mode, (system_prompt, builder) in PROMPT_REGISTRY.items():
        assert system_prompt.strip()

        if mode == "document_qa":
            prompt = builder(
                question="What does this code do?",
                context="The code adds two numbers.",
            )
        else:
            prompt = builder(
                "Test input for prompt evaluation."
            )

        assert isinstance(prompt, str)
        assert prompt.strip()

def test_system_and_user_prompts_are_separate():
    for mode, (system_prompt, builder) in PROMPT_REGISTRY.items():
        assert system_prompt.strip()

        if mode == "document_qa":
            user_prompt = builder(
                question="What does this document say?",
                context="This document describes a Python API.",
            )
        else:
            user_prompt = builder(
                "Explain this test input."
            )

        assert user_prompt.strip()
        assert user_prompt != system_prompt