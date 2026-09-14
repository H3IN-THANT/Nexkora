from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


GITHUB_API_BASE_URL = "https://api.github.com"
REQUEST_TIMEOUT = 20.0


@dataclass(frozen=True)
class GitHubFile:
    path: str
    download_url: str | None
    size: int


@dataclass(frozen=True)
class GitHubRepository:
    owner: str
    name: str
    default_branch: str
    files: list[GitHubFile]


class GitHubService:
    """Service for reading public GitHub repositories."""

    def __init__(self) -> None:
        self.client = httpx.Client(
            base_url=GITHUB_API_BASE_URL,
            timeout=REQUEST_TIMEOUT,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    def parse_repository_url(
        self,
        repository_url: str,
    ) -> tuple[str, str]:
        """Extract owner and repository name from a GitHub URL."""

        value = repository_url.strip().rstrip("/")
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "Repository URL must use HTTP or HTTPS."
            )

        if parsed.netloc.lower() != "github.com":
            raise ValueError(
                "Only github.com repository URLs are supported."
            )

        parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if len(parts) < 2:
            raise ValueError(
                "Invalid GitHub repository URL. "
                "Expected format: "
                "https://github.com/owner/repository"
            )

        owner = parts[0]
        repository = parts[1]

        if repository.endswith(".git"):
            repository = repository[:-4]

        if not owner or not repository:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        return owner, repository

    def get_repository(
        self,
        repository_url: str,
    ) -> GitHubRepository:
        """Retrieve repository metadata and its file tree."""

        owner, repository = self.parse_repository_url(
            repository_url
        )

        response = self.client.get(
            f"/repos/{owner}/{repository}"
        )

        if response.status_code == 404:
            raise ValueError(
                "GitHub repository was not found."
            )

        if response.status_code != 200:
            raise RuntimeError(
                "GitHub API request failed with "
                f"status {response.status_code}."
            )

        data = response.json()

        default_branch = data.get("default_branch")

        if not default_branch:
            raise RuntimeError(
                "GitHub repository did not provide "
                "a default branch."
            )

        tree_response = self.client.get(
            f"/repos/{owner}/{repository}/git/trees/"
            f"{default_branch}",
            params={"recursive": "1"},
        )

        if tree_response.status_code != 200:
            raise RuntimeError(
                "Unable to retrieve repository tree. "
                "GitHub returned status "
                f"{tree_response.status_code}."
            )

        tree_data = tree_response.json()

        if tree_data.get("truncated"):
            raise RuntimeError(
                "The GitHub repository is too large "
                "to index in one request."
            )

        files: list[GitHubFile] = []

        for item in tree_data.get("tree", []):
            if item.get("type") != "blob":
                continue

            path = item.get("path")

            if not path:
                continue

            files.append(
                GitHubFile(
                    path=path,
                    download_url=(
                        "https://raw.githubusercontent.com/"
                        f"{owner}/{repository}/"
                        f"{default_branch}/{path}"
                    ),
                    size=item.get("size", 0),
                )
            )

        return GitHubRepository(
            owner=owner,
            name=repository,
            default_branch=default_branch,
            files=files,
        )

    def close(self) -> None:
        """Close the HTTP client."""

        self.client.close()