from app.services.github_document_service import (
    GitHubDocumentService,
)
from app.services.github_service import GitHubFile


def test_supported_python_file():
    service = GitHubDocumentService()

    try:
        file = GitHubFile(
            path="app/main.py",
            download_url="https://example.com/main.py",
            size=1000,
        )

        assert service.is_supported_file(file) is True

    finally:
        service.close()


def test_unsupported_binary_file():
    service = GitHubDocumentService()

    try:
        file = GitHubFile(
            path="assets/image.png",
            download_url="https://example.com/image.png",
            size=1000,
        )

        assert service.is_supported_file(file) is False

    finally:
        service.close()


def test_ignored_node_modules_file():
    service = GitHubDocumentService()

    try:
        file = GitHubFile(
            path="node_modules/package/index.js",
            download_url="https://example.com/index.js",
            size=1000,
        )

        assert service.is_supported_file(file) is False

    finally:
        service.close()


def test_oversized_file_is_rejected():
    service = GitHubDocumentService()

    try:
        file = GitHubFile(
            path="large.py",
            download_url="https://example.com/large.py",
            size=512 * 1024 + 1,
        )

        assert service.is_supported_file(file) is False

    finally:
        service.close()