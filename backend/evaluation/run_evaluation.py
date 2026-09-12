from app.prompts.registry import get_prompt
from evaluation.prompt_cases import PROMPT_CASES


def build_evaluation_prompt(case):
    _, builder = get_prompt(case.mode)

    if case.mode == "document_qa":
        return builder(
            question=case.input_data["question"],
            context=case.input_data["context"],
        )

    return builder(case.input_data["message"])


def main():
    for case in PROMPT_CASES:
        prompt = build_evaluation_prompt(case)

        print("=" * 80)
        print(f"CASE: {case.case_id}")
        print(f"MODE: {case.mode}")
        print()
        print("EXPECTED BEHAVIOR:")
        
        for behavior in case.expected_behavior:
            print(f"- {behavior}")

        print()
        print("PROMPT:")
        print(prompt)
        print()


if __name__ == "__main__":
    main()