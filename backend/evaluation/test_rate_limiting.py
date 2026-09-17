from fastapi.testclient import TestClient

from app.main import app, rate_limiter, ai_service


client = TestClient(app)


def setup_function():
    rate_limiter.reset()


def test_chat_rate_limit_returns_429(monkeypatch):
    def fake_generate_response(user_input: str, system_instruction: str) -> str:
        return "Mocked AI response."

    monkeypatch.setattr(
        ai_service,
        "generate_response",
        fake_generate_response,
    )

    for _ in range(20):
        response = client.post(
            "/api/v1/chat",
            json={
                "mode": "explain_code",
                "message": "Explain Python lists.",
            },
        )

        assert response.status_code != 429

    response = client.post(
        "/api/v1/chat",
        json={
            "mode": "explain_code",
            "message": "Explain Python lists.",
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Too many requests. Please try again later."
    )
    assert "Retry-After" in response.headers


def test_health_endpoint_is_not_rate_limited():
    for _ in range(25):
        response = client.get("/health")
        assert response.status_code == 200


def test_upload_has_stricter_rate_limit():
    for _ in range(5):
        response = client.post(
            "/api/v1/documents/upload",
            files={
                "file": (
                    "test.txt",
                    b"test content",
                    "text/plain",
                )
            },
        )

        assert response.status_code != 429

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "test.txt",
                b"test content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_rate_limit_is_per_endpoint(monkeypatch):
    def fake_generate_response(user_input: str, system_instruction: str) -> str:
        return "Mocked AI response."

    monkeypatch.setattr(
        ai_service,
        "generate_response",
        fake_generate_response,
    )

    for _ in range(20):
        response = client.post(
            "/api/v1/chat",
            json={
                "mode": "explain_code",
                "message": "Explain Python lists.",
            },
        )

        assert response.status_code != 429

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "test.txt",
                b"test content",
                "text/plain",
            )
        },
    )

    assert response.status_code != 429