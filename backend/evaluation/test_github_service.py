import pytest

from app.services.github_service import GitHubService


def test_parse_valid_github_url():
    service = GitHubService()

    try:
        owner, repository = (
            service.parse_repository_url(
                "https://github.com/example/project"
            )
        )

        assert owner == "example"
        assert repository == "project"

    finally:
        service.close()


def test_parse_github_url_with_git_suffix():
    service = GitHubService()

    try:
        owner, repository = (
            service.parse_repository_url(
                "https://github.com/example/project.git"
            )
        )

        assert owner == "example"
        assert repository == "project"

    finally:
        service.close()


def test_reject_non_github_url():
    service = GitHubService()

    try:
        with pytest.raises(ValueError):
            service.parse_repository_url(
                "https://gitlab.com/example/project"
            )

    finally:
        service.close()


def test_reject_invalid_repository_url():
    service = GitHubService()

    try:
        with pytest.raises(ValueError):
            service.parse_repository_url(
                "https://github.com/example"
            )

    finally:
        service.close()