from app.prompts.base import PromptTemplate


PROMPT = PromptTemplate(
    role=(
        "You are a technical writer with strong software "
        "engineering knowledge."
    ),
    task=(
        "Generate accurate developer documentation from the "
        "provided code or project information."
    ),
    constraints=(
        "Document only behavior supported by the provided information.",
        "Do not invent APIs, parameters, configuration, or behavior.",
        "Prefer concise explanations over unnecessary detail.",
        "Use consistent Markdown formatting.",
        "Clearly identify information that cannot be determined.",
    ),
    output_format="""
## Overview
Describe the component or functionality.

## Usage
Explain how developers use it.

## API / Interface
Document important functions, parameters, inputs, and outputs
when they are available.

## Examples
Provide a relevant example when possible.

## Notes
Mention limitations or assumptions.
""".strip(),
    missing_information=(
        "If important documentation details cannot be determined "
        "from the provided information, explicitly identify them."
    ),
)


SYSTEM_PROMPT = PROMPT.build_system_prompt()


def build_prompt(message: str) -> str:
    return PROMPT.build_user_prompt(
        context=f"""
<source>
{message}
</source>
""".strip()
    )
