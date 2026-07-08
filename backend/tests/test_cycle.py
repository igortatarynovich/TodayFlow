"""Tests for cycle intelligence endpoints."""


def _auth_headers(client):
    email = "cycle_user@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_cycle_insights_summary(client):
    headers = _auth_headers(client)
    client.post(
        "/calendar/cycle",
        json={
            "date": "2026-02-01",
            "cycle_day": 3,
            "period_intensity": "medium",
            "ovulation": False,
            "fertile_window": False,
            "symptoms": {"fatigue": True, "mood": 4},
        },
        headers=headers,
    )
    client.post(
        "/calendar/cycle",
        json={
            "date": "2026-02-10",
            "cycle_day": 12,
            "period_intensity": "light",
            "ovulation": True,
            "fertile_window": True,
            "symptoms": {"focus": 4},
        },
        headers=headers,
    )

    response = client.get(
        "/calendar/cycle/insights?from_date=2026-02-01&to_date=2026-02-15",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tracked_days"] == 2
    assert data["ovulation_days"] == 1
    assert data["fertile_window_days"] == 1
    assert isinstance(data["recommendations"], list)
