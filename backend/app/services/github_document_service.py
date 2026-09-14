from pathlib import Path

import httpx

from app.services.github_service import GitHubFile


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".kts",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".md",
    ".txt",
    ".rst",
    ".sql",
    ".sh",
    ".bash",
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "coverage",
}

MAX_FILE_SIZE = 512 * 1024
REQUEST_TIMEOUT = 20.0


class GitHubDocumentService:
    """Filter and download text files from GitHub."""

    def __init__(self) -> None:
        self.client = httpx.Client(
            timeout=REQUEST_TIMEOUT,
        )

    def is_supported_file(
        self,
        file: GitHubFile,
    ) -> bool:
        """Return whether a GitHub file should be indexed."""

        path = Path(file.path)

        # Ignore files that are too large.
        if file.size > MAX_FILE_SIZE:
            return False

        # Only index supported source/document extensions.
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            return False

        # Ignore generated, dependency, and repository metadata folders.
        if any(
            part in IGNORED_DIRECTORIES
            for part in path.parts
        ):
            return False

        return True

    def filter_files(
        self,
        files: list[GitHubFile],
    ) -> list[GitHubFile]:
        """Filter repository files to indexable files."""

        return [
            file
            for file in files
            if self.is_supported_file(file)
        ]

    def extract_text(
        self,
        file: GitHubFile,
    ) -> str:
        """Download and decode a GitHub text file."""

        if not file.download_url:
            raise ValueError(
                f"No download URL available for {file.path}."
            )

        response = self.client.get(
            file.download_url
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Unable to download {file.path}. "
                f"HTTP status: {response.status_code}."
            )

        try:
            text = response.content.decode(
                "utf-8",
                errors="strict",
            )

        except UnicodeDecodeError as exc:
            raise ValueError(
                f"File is not valid UTF-8 text: {file.path}"
            ) from exc

        text = text.strip()

        if not text:
            raise ValueError(
                f"File does not contain readable text: {file.path}"
            )

        return text

    def close(self) -> None:
        """Close the HTTP client."""

        self.client.close()