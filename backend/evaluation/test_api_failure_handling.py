from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_rejects_empty_message():

    response = client.post(
        "/api/v1/chat",
        json={
            "mode": "explain_code",
            "message": "",
        },
    )

    assert response.status_code == 422


def test_chat_rejects_invalid_mode():

    response = client.post(
        "/api/v1/chat",
        json={
            "mode": "invalid_mode",
            "message": "Explain Python.",
        },
    )

    assert response.status_code == 422


def test_document_question_requires_document():

    response = client.post(
        "/api/v1/documents/ask",
        json={
            "document_id": "does-not-exist",
            "question": "What is this?",
        },
    )

    assert response.status_code == 404


def test_github_index_rejects_non_github_url():

    response = client.post(
        "/api/v1/github/index",
        json={
            "repository_url": (
                "https://example.com/not-github"
            ),
        },
    )

    assert response.status_code == 400


def test_github_index_rejects_empty_url():

    response = client.post(
        "/api/v1/github/index",
        json={
            "repository_url": "",
        },
    )

    assert response.status_code == 422