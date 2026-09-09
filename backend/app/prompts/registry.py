from collections.abc import Callable

from app.prompts.debug_code import (
    SYSTEM_PROMPT as DEBUG_CODE_SYSTEM_PROMPT,
    build_debug_code_prompt,
)
from app.prompts.explain_code import (
    SYSTEM_PROMPT as EXPLAIN_CODE_SYSTEM_PROMPT,
    build_explain_code_prompt,
)
from app.prompts.explain_errors import (
    SYSTEM_PROMPT as EXPLAIN_ERRORS_SYSTEM_PROMPT,
    build_explain_errors_prompt,
)
from app.prompts.generate_code import (
    SYSTEM_PROMPT as GENERATE_CODE_SYSTEM_PROMPT,
    build_generate_code_prompt,
)
from app.prompts.generate_documentation import (
    SYSTEM_PROMPT as GENERATE_DOCUMENTATION_SYSTEM_PROMPT,
    build_generate_documentation_prompt,
)
from app.prompts.refactor_code import (
    SYSTEM_PROMPT as REFACTOR_CODE_SYSTEM_PROMPT,
    build_refactor_code_prompt,
)


PromptBuilder = Callable[[str], str]


PROMPT_REGISTRY: dict[
    str,
    tuple[str, PromptBuilder],
] = {
    "explain_code": (
        EXPLAIN_CODE_SYSTEM_PROMPT,
        build_explain_code_prompt,
    ),
    "debug_code": (
        DEBUG_CODE_SYSTEM_PROMPT,
        build_debug_code_prompt,
    ),
    "generate_code": (
        GENERATE_CODE_SYSTEM_PROMPT,
        build_generate_code_prompt,
    ),
    "refactor_code": (
        REFACTOR_CODE_SYSTEM_PROMPT,
        build_refactor_code_prompt,
    ),
    "generate_documentation": (
        GENERATE_DOCUMENTATION_SYSTEM_PROMPT,
        build_generate_documentation_prompt,
    ),
    "explain_errors": (
        EXPLAIN_ERRORS_SYSTEM_PROMPT,
        build_explain_errors_prompt,
    ),
}


def get_prompt(
    mode: str,
) -> tuple[str, PromptBuilder]:
    """
    Return the system prompt and user prompt builder
    for a supported developer mode.
    """

    try:
        return PROMPT_REGISTRY[mode]

    except KeyError as exc:
        raise ValueError(
            f"Unsupported developer mode: {mode}"
        ) from exc