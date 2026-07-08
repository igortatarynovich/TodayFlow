from __future__ import annotations

from fastapi.testclient import TestClient

from .conftest import login_bearer_token


def _auth_headers(client: TestClient) -> dict[str, str]:
    email = "today-guards@example.com"
    password = "testpassword123"
    signup = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup.status_code in (200, 201), signup.text
    token = login_bearer_token(client, email, password)
    return {"Authorization": f"Bearer {token}"}


def test_today_endpoints_return_uniform_400_for_invalid_target_date(client: TestClient):
    headers = _auth_headers(client)
    invalid = "2026-13-99"

    endpoints = [
        ("/today/opening", "get", {"target_date": invalid}),
        ("/today/checkin-prompt", "get", {"target_date": invalid}),
        ("/today/core", "get", {"target_date": invalid}),
        ("/today/scenarios", "get", {"target_date": invalid}),
        ("/today/bundle", "get", {"target_date": invalid}),
        ("/today/contract", "get", {"target_date": invalid}),
        ("/today/state-map", "get", {"target_date": invalid}),
        ("/today/evening", "get", {"target_date": invalid}),
        ("/today", "get", {"target_date": invalid}),
    ]

    for path, method, params in endpoints:
        response = getattr(client, method)(path, params=params, headers=headers)
        assert response.status_code == 400, f"{path} -> {response.status_code} {response.text}"
        assert response.json().get("detail") == "invalid target_date"


def test_day_connection_rejects_invalid_enum_values(client: TestClient):
    headers = _auth_headers(client)
    response = client.post(
        "/day-connection/2026-04-25",
        headers=headers,
        json={
            "ritual_feedback": "maybe",
            "quick_decision_answer": "later",
        },
    )
    assert response.status_code == 422, response.text

