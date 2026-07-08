"""Tests for habits API endpoints."""

from datetime import date


def _auth_headers(client):
    email = "habits_user@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_habit_and_log_entry(client):
    headers = _auth_headers(client)
    create_resp = client.post(
        "/habits",
        json={
            "name": "Morning breathing",
            "category": "breathwork",
            "target_frequency": "daily",
            "target_per_period": 1,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    habit_id = create_resp.json()["id"]

    entry_resp = client.post(
        f"/habits/{habit_id}/entries",
        json={
            "date": date.today().isoformat(),
            "completed": True,
            "intensity": 4,
            "note": "Done before work",
        },
        headers=headers,
    )
    assert entry_resp.status_code == 201
    assert entry_resp.json()["completed"] is True


def test_habits_overview(client):
    headers = _auth_headers(client)
    create_resp = client.post(
        "/habits",
        json={
            "name": "Daily stretch",
            "category": "body",
            "target_frequency": "daily",
            "target_per_period": 1,
        },
        headers=headers,
    )
    habit_id = create_resp.json()["id"]

    client.post(
        f"/habits/{habit_id}/entries",
        json={"date": date.today().isoformat(), "completed": True},
        headers=headers,
    )

    overview_resp = client.get("/habits/overview/summary", headers=headers)
    assert overview_resp.status_code == 200
    data = overview_resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["habit_id"] == habit_id


def test_update_habit_rename_and_pause(client):
    email = "habits_update_user@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    create_resp = client.post(
        "/habits",
        json={"name": "Water first", "target_frequency": "daily", "target_per_period": 1},
        headers=headers,
    )
    assert create_resp.status_code == 201
    habit_id = create_resp.json()["id"]

    rename = client.put(
        f"/habits/{habit_id}",
        json={"name": "Water before coffee"},
        headers=headers,
    )
    assert rename.status_code == 200
    assert rename.json()["name"] == "Water before coffee"

    pause = client.put(f"/habits/{habit_id}", json={"is_active": False}, headers=headers)
    assert pause.status_code == 200
    assert pause.json()["is_active"] is False
