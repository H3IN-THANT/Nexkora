from collections.abc import Callable

from app.prompts.code_explanation import (
    SYSTEM_PROMPT as CODE_EXPLANATION_SYSTEM_PROMPT,
    build_prompt as build_code_explanation_prompt,
)
from app.prompts.debugging import (
    SYSTEM_PROMPT as DEBUGGING_SYSTEM_PROMPT,
    build_prompt as build_debugging_prompt,
)
from app.prompts.code_generation import (
    SYSTEM_PROMPT as CODE_GENERATION_SYSTEM_PROMPT,
    build_prompt as build_code_generation_prompt,
)
from app.prompts.refactor_code import (
    SYSTEM_PROMPT as REFACTOR_CODE_SYSTEM_PROMPT,
    build_prompt as build_refactor_code_prompt,
)
from app.prompts.documentation import (
    SYSTEM_PROMPT as DOCUMENTATION_SYSTEM_PROMPT,
    build_prompt as build_documentation_prompt,
)
from app.prompts.explain_errors import (
    SYSTEM_PROMPT as EXPLAIN_ERRORS_SYSTEM_PROMPT,
    build_prompt as build_explain_errors_prompt,
)
from app.prompts.rag_qa import (
    SYSTEM_PROMPT as RAG_QA_SYSTEM_PROMPT,
    build_prompt as build_rag_qa_prompt,
)


PromptBuilder = Callable[..., str]


PROMPT_REGISTRY = {
    "explain_code": (
        CODE_EXPLANATION_SYSTEM_PROMPT,
        build_code_explanation_prompt,
    ),
    "debug_code": (
        DEBUGGING_SYSTEM_PROMPT,
        build_debugging_prompt,
    ),
    "generate_code": (
        CODE_GENERATION_SYSTEM_PROMPT,
        build_code_generation_prompt,
    ),
    "refactor_code": (
        REFACTOR_CODE_SYSTEM_PROMPT,
        build_refactor_code_prompt,
    ),
    "generate_documentation": (
        DOCUMENTATION_SYSTEM_PROMPT,
        build_documentation_prompt,
    ),
    "explain_errors": (
        EXPLAIN_ERRORS_SYSTEM_PROMPT,
        build_explain_errors_prompt,
    ),
    "document_qa": (
        RAG_QA_SYSTEM_PROMPT,
        build_rag_qa_prompt,
    ),
}


def get_prompt(mode: str) -> tuple[str, PromptBuilder]:
    try:
        return PROMPT_REGISTRY[mode]
    except KeyError as exc:
        raise ValueError(f"Unsupported prompt mode: {mode}") from exc