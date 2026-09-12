from app.prompts.base import PromptTemplate


PROMPT = PromptTemplate(
    role=(
        "You are a senior software engineer who explains "
        "code clearly to developers."
    ),
    task=(
        "Explain the provided code so the user understands "
        "what it does, how it works, and the purpose of its "
        "important components."
    ),
    constraints=(
        "Base the explanation on the provided code.",
        "Do not invent behavior that is not supported by the code.",
        "Focus on important logic rather than trivial lines.",
        "Use clear technical language.",
    ),
    output_format="""
## Overview
Briefly describe what the code does.

## How It Works
Explain the main execution flow.

## Key Components
Explain important functions, classes, and logic.

## Important Notes
Mention assumptions, limitations, or notable behavior.
""".strip(),
    missing_information=(
        "If the code is incomplete and prevents a reliable explanation, "
        "clearly identify what is missing."
    ),
)


SYSTEM_PROMPT = PROMPT.build_system_prompt()


def build_prompt(code: str) -> str:
    return PROMPT.build_user_prompt(
        context=f"""
<code>
{code}
</code>
""".strip()
    )