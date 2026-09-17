from evaluation.models import EvaluationCase


EVALUATION_CASES: tuple[EvaluationCase, ...] = (

    # ---------------------------------------------------------
    # RELEVANCE
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="relevance-001",
        category="relevance",
        mode="explain_code",
        question=(
            "Explain what this Python expression does: "
            "list(dict.fromkeys(items))"
        ),
        expected_facts=(
            "removes duplicate values",
            "preserves insertion order",
            "returns a list",
        ),
        difficulty="easy",
        tags=("python", "collections"),
    ),

    EvaluationCase(
        case_id="relevance-002",
        category="relevance",
        mode="generate_code",
        question=(
            "Write a Python function that returns the largest "
            "number in a list without using max()."
        ),
        expected_facts=(
            "iterates through the list",
            "tracks the largest value",
            "does not use max",
        ),
        difficulty="easy",
        tags=("python", "algorithm"),
    ),

    EvaluationCase(
        case_id="relevance-003",
        category="relevance",
        mode="refactor_code",
        question=(
            "Refactor this condition while preserving its behavior:\n\n"
            "if user and user.is_active == True:"
        ),
        expected_facts=(
            "removes == True",
            "preserves the user check",
            "preserves the active check",
        ),
        difficulty="easy",
        tags=("python", "refactoring"),
    ),

    EvaluationCase(
        case_id="relevance-004",
        category="relevance",
        mode="generate_documentation",
        question=(
            "Write concise documentation for a function named "
            "parse_config(path) that reads a configuration file "
            "and returns a dictionary."
        ),
        expected_facts=(
            "describes the path parameter",
            "states that the function returns a dictionary",
        ),
        difficulty="easy",
        tags=("documentation",),
    ),

    EvaluationCase(
        case_id="relevance-005",
        category="relevance",
        mode="explain_errors",
        question="What does HTTP status code 404 mean?",
        expected_facts=(
            "resource not found",
        ),
        difficulty="easy",
        tags=("http", "errors"),
    ),

    # ---------------------------------------------------------
    # FACTUALITY
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="factuality-001",
        category="factuality",
        mode="explain_code",
        question=(
            "What is the result of this Python code?\n\n"
            "[x * 2 for x in [1, 2, 3]]"
        ),
        expected_facts=(
            "2",
            "4",
            "6",
            "creates a new list",
        ),
        forbidden_facts=(
            "modifies the original list",
        ),
        difficulty="easy",
        tags=("python", "list-comprehension"),
    ),

    EvaluationCase(
        case_id="factuality-002",
        category="factuality",
        mode="explain_code",
        question=(
            "In Python, what does dictionary.get('missing', 0) "
            "return when the key does not exist?"
        ),
        expected_facts=(
            "returns 0",
        ),
        forbidden_facts=(
            "raises KeyError",
        ),
        difficulty="easy",
        tags=("python", "dictionary"),
    ),

    EvaluationCase(
        case_id="factuality-003",
        category="factuality",
        mode="explain_errors",
        question=(
            "Why is this Python condition invalid?\n\n"
            "if x = 5:"
        ),
        expected_facts=(
            "assignment cannot be used as the condition",
            "== compares values",
        ),
        difficulty="easy",
        tags=("python", "syntax"),
    ),

    EvaluationCase(
        case_id="factuality-004",
        category="factuality",
        mode="explain_errors",
        question="What does HTTP 500 mean?",
        expected_facts=(
            "internal server error",
        ),
        forbidden_facts=(
            "unauthorized",
        ),
        difficulty="easy",
        tags=("http", "errors"),
    ),

    EvaluationCase(
        case_id="factuality-005",
        category="factuality",
        mode="explain_code",
        question=(
            "What does len({'a': 1, 'b': 2}) return in Python?"
        ),
        expected_facts=(
            "2",
            "number of keys",
        ),
        difficulty="easy",
        tags=("python", "dictionary"),
    ),

    # ---------------------------------------------------------
    # CODE EXPLANATION
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="code-001",
        category="code_explanation",
        mode="explain_code",
        question=(
            "Explain linear search and its worst-case time complexity."
        ),
        expected_facts=(
            "checks elements sequentially",
            "worst-case O(n)",
        ),
        difficulty="easy",
        tags=("algorithms",),
    ),

    EvaluationCase(
        case_id="code-002",
        category="code_explanation",
        mode="explain_code",
        question=(
            "Explain what this SQL query does:\n\n"
            "SELECT name FROM users "
            "WHERE active = TRUE "
            "ORDER BY name;"
        ),
        expected_facts=(
            "selects names",
            "filters active users",
            "orders by name",
        ),
        difficulty="easy",
        tags=("sql",),
    ),

    EvaluationCase(
        case_id="code-003",
        category="code_explanation",
        mode="explain_code",
        question=(
            "Explain what JavaScript Array.map() does and "
            "what this expression returns:\n\n"
            "[1, 2, 3].map(x => x * 2)"
        ),
        expected_facts=(
            "creates a new array",
            "2",
            "4",
            "6",
        ),
        difficulty="easy",
        tags=("javascript",),
    ),

    EvaluationCase(
        case_id="code-004",
        category="code_explanation",
        mode="explain_code",
        question=(
            "Explain why Python context managers are useful when "
            "working with files."
        ),
        expected_facts=(
            "manages setup and cleanup",
            "helps close the file",
        ),
        difficulty="medium",
        tags=("python", "files"),
    ),

    EvaluationCase(
        case_id="code-005",
        category="code_explanation",
        mode="explain_code",
        question=(
            "Explain the difference between a Python list and tuple."
        ),
        expected_facts=(
            "list is mutable",
            "tuple is immutable",
        ),
        difficulty="easy",
        tags=("python", "data-structures"),
    ),

    # ---------------------------------------------------------
    # DEBUGGING
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="debug-001",
        category="debugging",
        mode="debug_code",
        question=(
            "Find the bug and fix it:\n\n"
            "numbers = [1, 2, 3]\n"
            "total = sum['numbers']"
        ),
        expected_facts=(
            "sum should be called as a function",
            "sum(numbers)",
        ),
        difficulty="easy",
        tags=("python",),
    ),

    EvaluationCase(
        case_id="debug-002",
        category="debugging",
        mode="debug_code",
        question=(
            "This code raises an error when email is missing. "
            "Explain why and suggest a safer approach:\n\n"
            "email = user['email']"
        ),
        expected_facts=(
            "missing key causes KeyError",
            "get can be used",
        ),
        difficulty="easy",
        tags=("python", "dictionary"),
    ),

    EvaluationCase(
        case_id="debug-003",
        category="debugging",
        mode="debug_code",
        question=(
            "Why can this code raise ZeroDivisionError?\n\n"
            "result = total / count"
        ),
        expected_facts=(
            "count can be zero",
            "division by zero raises ZeroDivisionError",
        ),
        difficulty="easy",
        tags=("python", "errors"),
    ),

    EvaluationCase(
        case_id="debug-004",
        category="debugging",
        mode="debug_code",
        question=(
            "In JavaScript, why can accessing a missing property "
            "like user.profile.name fail, and what should I check?"
        ),
        expected_facts=(
            "an intermediate property may be undefined",
            "check whether the object exists",
        ),
        difficulty="medium",
        tags=("javascript",),
    ),

    EvaluationCase(
        case_id="debug-005",
        category="debugging",
        mode="debug_code",
        question=(
            "A FastAPI endpoint returns HTTP 422 when a required "
            "request field is missing. What should I inspect?"
        ),
        expected_facts=(
            "request validation",
            "Pydantic schema",
            "request JSON",
        ),
        difficulty="medium",
        tags=("fastapi", "validation"),
    ),

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="rag-001",
        category="rag",
        mode=None,
        context=(
            "Nexkora has a FastAPI backend. "
            "The frontend uses Next.js and TypeScript. "
            "The project uses ChromaDB for vector retrieval."
        ),
        question="Which vector database is used by Nexkora?",
        expected_facts=(
            "ChromaDB",
        ),
        expected_sources=(
            "architecture.md",
        ),
        difficulty="easy",
        tags=("rag", "architecture"),
    ),

    EvaluationCase(
        case_id="rag-002",
        category="rag",
        mode=None,
        context=(
            "Document uploads accept .txt and .md files. "
            "The maximum upload size is 2 MB."
        ),
        question="Which file extensions can the document uploader accept?",
        expected_facts=(
            ".txt",
            ".md",
        ),
        expected_sources=(
            "document_service.py",
        ),
        difficulty="easy",
        tags=("rag", "documents"),
    ),

    EvaluationCase(
        case_id="rag-003",
        category="rag",
        mode=None,
        context=(
            "The GitHub document service ignores these directories: "
            ".git, node_modules, __pycache__, .venv, venv, dist, "
            "build, .next, and coverage."
        ),
        question="Which directory is ignored for installed Node.js dependencies?",
        expected_facts=(
            "node_modules",
        ),
        expected_sources=(
            "github_document_service.py",
        ),
        difficulty="easy",
        tags=("rag", "github"),
    ),

    EvaluationCase(
        case_id="rag-004",
        category="rag",
        mode=None,
        context=(
            "The embedding service formats retrieval queries as: "
            "task: question answering | query: {query}"
        ),
        question="What task prefix is used for retrieval queries?",
        expected_facts=(
            "task: question answering",
        ),
        expected_sources=(
            "embedding_service.py",
        ),
        difficulty="easy",
        tags=("rag", "embeddings"),
    ),

    # ---------------------------------------------------------
    # HALLUCINATION
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="hallucination-001",
        category="hallucination",
        mode=None,
        context=(
            "The provided context describes a FastAPI backend "
            "but contains no authentication implementation."
        ),
        question="Which authentication library does the project use?",
        forbidden_facts=(
            "Auth0",
            "Firebase",
            "Clerk",
            "OAuth2",
        ),
        difficulty="medium",
        tags=("hallucination", "insufficient-context"),
    ),

    EvaluationCase(
        case_id="hallucination-002",
        category="hallucination",
        mode=None,
        context=(
            "The context only states that ChromaDB is used for "
            "vector storage. It does not describe cloud hosting."
        ),
        question="Which AWS service hosts the vector database?",
        forbidden_facts=(
            "EC2",
            "ECS",
            "RDS",
        ),
        difficulty="medium",
        tags=("hallucination", "cloud"),
    ),

    EvaluationCase(
        case_id="hallucination-003",
        category="hallucination",
        mode=None,
        context=(
            "The project exposes a GET /health endpoint that returns "
            "a simple health status."
        ),
        question="What JWT authentication mechanism protects /health?",
        forbidden_facts=(
            "JWT",
            "Bearer token",
            "API key",
        ),
        difficulty="medium",
        tags=("hallucination", "api"),
    ),

    EvaluationCase(
        case_id="hallucination-004",
        category="hallucination",
        mode=None,
        context=(
            "The context only states that PostgreSQL is used as the "
            "database. No PostgreSQL version is provided."
        ),
        question="Which exact PostgreSQL version does the project use?",
        forbidden_facts=(
            "PostgreSQL 14",
            "PostgreSQL 15",
            "PostgreSQL 16",
            "PostgreSQL 17",
        ),
        difficulty="hard",
        tags=("hallucination", "database"),
    ),

    # ---------------------------------------------------------
    # FAILURE HANDLING
    # ---------------------------------------------------------

    EvaluationCase(
        case_id="failure-001",
        category="failure_handling",
        question="",
        expected_http_status=400,
        difficulty="easy",
        tags=("validation",),
    ),

    EvaluationCase(
        case_id="failure-002",
        category="failure_handling",
        question="https://example.com/not-a-github-repository",
        expected_http_status=400,
        difficulty="easy",
        tags=("github", "validation"),
    ),
)


def get_evaluation_cases() -> tuple[EvaluationCase, ...]:
    return EVALUATION_CASES