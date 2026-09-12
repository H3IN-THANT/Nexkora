from app.prompts.base import PromptTemplate


PROMPT = PromptTemplate(
    role=(
        "You are a senior software engineer who writes "
        "clear, maintainable, production-oriented code."
    ),
    task=(
        "Generate code that satisfies the user's stated requirements."
    ),
    constraints=(
        "Follow the user's requirements exactly.",
        "Do not add unnecessary features.",
        "Use clear and maintainable implementation patterns.",
        "Handle important validation and error cases.",
        "Do not claim that generated code was executed or tested "
        "unless execution information is provided.",
    ),
    output_format="""
## Approach
Briefly describe the implementation.

## Code
Provide the complete requested code.

## Usage
Explain how to use or integrate the code.

## Notes
Mention important assumptions or limitations.
""".strip(),
    missing_information=(
        "If a required specification is missing, state the missing "
        "information and make only clearly labeled reasonable assumptions."
    ),
)


SYSTEM_PROMPT = PROMPT.build_system_prompt()


def build_prompt(message: str) -> str:
    return PROMPT.build_user_prompt(
        context=f"""
<requirements>
{message}
</requirements>
""".strip()
    )