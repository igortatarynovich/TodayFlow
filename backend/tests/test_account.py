"""Tests for account API endpoints."""

import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.api import account as account_api
from todayflow_backend.db.models import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    """Get auth token for test user."""
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


def test_get_core_profile_requires_auth(client: TestClient):
    """GET /account/core-profile требует авторизацию."""
    response = client.get("/account/core-profile")
    assert response.status_code == 401


@pytest.mark.smoke
def test_put_profile_then_core_profile_person(client: TestClient, test_user: User, auth_token: str):
    """Фаза 1: имя в настройках → core-profile отражает person и недостающие астро-поля."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    put = client.put(
        "/account/profile",
        json={"first_name": "Mira", "last_name": "Flow", "locale": "ru_RU"},
        headers=headers,
    )
    assert put.status_code == 200

    core = client.get("/account/core-profile", headers=headers)
    assert core.status_code == 200
    data = core.json()
    assert data.get("person", {}).get("first_name") == "Mira"
    assert isinstance(data.get("missing_fields"), list)
    missing = set(data["missing_fields"])
    assert "gender" in missing
    assert "astro_birth_date" in missing or "astro_location_name" in missing
    assert data.get("is_ready") is False


def test_profile_astro_then_core_profile_numerology_gap(
    client: TestClient, test_user: User, auth_token: str
):
    """Профиль + полный astro-data без numerology: core-profile не is_ready, астро заполнено."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    assert (
        client.put(
            "/account/profile",
            json={"first_name": "Nika", "last_name": "Star", "locale": "en_US", "gender": "unspecified"},
            headers=headers,
        ).status_code
        == 200
    )

    astro = client.post(
        "/account/astro-data",
        json={
            "label": "Я",
            "relation": "self",
            "birth_date": "1992-03-20",
            "birth_time": "09:15:00",
            "timezone_name": "UTC",
            "location_name": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "is_primary": True,
        },
        headers=headers,
    )
    assert astro.status_code == 200

    core = client.get("/account/core-profile", headers=headers)
    assert core.status_code == 200
    body = core.json()
    assert body["person"]["first_name"] == "Nika"
    astro_ctx = body.get("astro") or {}
    assert astro_ctx.get("birth_date") == "1992-03-20"
    assert astro_ctx.get("location_name") == "Paris"
    assert "numerology_life_path" in (body.get("missing_fields") or [])
    assert body.get("is_ready") is False


def test_core_setup_then_core_profile_ready(client: TestClient, test_user: User, auth_token: str):
    """POST /account/core-setup создаёт/обновляет профиль, нумерологию и отдаёт is_ready в core_profile."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "first_name": "Alex",
        "last_name": "Chart",
        "label": "Я",
        "birth_date": "1988-11-08",
        "birth_time": "16:45:00",
        "time_unknown": False,
        "timezone_name": "UTC",
        "location_name": "London",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "gender": "female",
    }
    r = client.post("/account/core-setup", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    out = r.json()
    assert out.get("status") == "ok"
    cp = out.get("core_profile") or {}
    assert cp.get("is_ready") is True
    assert cp.get("missing_fields") == []

    again = client.get("/account/core-profile", headers=headers)
    assert again.status_code == 200
    body = again.json()
    assert body.get("is_ready") is True
    assert body.get("person", {}).get("first_name") == "Alex"
    assert body.get("person", {}).get("gender") == "female"
    num = body.get("numerology") or {}
    assert num.get("life_path") is not None


def test_get_profile_requires_auth(client: TestClient):
    """Test that getting profile requires authentication."""
    response = client.get("/account/profile")
    assert response.status_code == 401


def test_get_profile_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting profile for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/account/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "email" in data
    assert data["email"] == test_user.email
    assert "greeting" in data
    assert "first_name" in data
    assert "last_name" in data
    assert "country" in data
    assert "language" in data
    assert "locale" in data
    assert "subscriptions" in data
    assert "gender" in data


def test_update_profile_requires_auth(client: TestClient):
    """Test that updating profile requires authentication."""
    response = client.put("/account/profile", json={})
    assert response.status_code == 401


def test_free_user_cannot_set_today_narrative_depth_to_deep(client: TestClient, test_user: User, auth_token: str):
    """DE-8: режим deep только при insight_depth_tier != free."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.put(
        "/account/profile",
        json={"today_narrative_depth_level": "deep"},
        headers=headers,
    )
    assert r.status_code == 400
    assert "deep" in r.json().get("detail", "").lower() or "подписк" in r.json().get("detail", "").lower()


def test_update_profile_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test updating profile for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(
        "/account/profile",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "country": "US",
            "language": "en",
            "locale": "en_US",
            "gender": "male",
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["country"] == "US"
    assert data["language"] == "en"
    assert data["locale"] == "en_US"
    assert data["gender"] == "male"


def test_put_profile_gender_reflected_in_core_profile(client: TestClient, test_user: User, auth_token: str):
    """Смена gender в настройках сразу видна в person.gender у core-profile."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.put(
        "/account/profile",
        json={"first_name": "Rita", "gender": "female"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    core = client.get("/account/core-profile", headers=headers)
    assert core.status_code == 200
    body = core.json()
    assert body.get("person", {}).get("gender") == "female"


def test_invalidate_morning_cache_for_user_clears_only_that_user():
    """Сброс morning-ritual кэша по user_id (используется после PUT /account/profile)."""
    import time

    from todayflow_backend.api.today import _MORNING_RITUAL_CACHE, invalidate_morning_cache_for_user

    uid = 990_001
    key_a = (uid, "2099-01-01", "ru")
    key_b = (uid + 1, "2099-01-01", "ru")
    now = time.time()
    _MORNING_RITUAL_CACHE[key_a] = (now, None)  # type: ignore[arg-type]
    _MORNING_RITUAL_CACHE[key_b] = (now, None)  # type: ignore[arg-type]
    try:
        invalidate_morning_cache_for_user(uid)
        assert key_a not in _MORNING_RITUAL_CACHE
        assert key_b in _MORNING_RITUAL_CACHE
    finally:
        _MORNING_RITUAL_CACHE.pop(key_a, None)
        _MORNING_RITUAL_CACHE.pop(key_b, None)


def test_update_profile_email(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test updating email."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(
        "/account/profile",
        json={
            "email": "newemail@example.com"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "newemail@example.com"
    
    # Verify in database
    db_session.refresh(test_user)
    assert test_user.email == "newemail@example.com"


def test_list_astro_profiles_requires_auth(client: TestClient):
    """Test that listing astro profiles requires authentication."""
    response = client.get("/account/astro-data")
    assert response.status_code == 401


def test_list_astro_profiles_empty(client: TestClient, test_user: User, auth_token: str):
    """Test listing astro profiles when none exist."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/account/astro-data", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "profiles" in data
    assert isinstance(data["profiles"], list)
    assert len(data["profiles"]) == 0
    assert "max_profiles" in data
    assert "current_count" in data
    assert "can_create_more" in data


def test_create_astro_profile_requires_auth(client: TestClient):
    """Test that creating astro profile requires authentication."""
    response = client.post("/account/astro-data", json={})
    assert response.status_code == 401


def test_create_astro_profile(client: TestClient, test_user: User, auth_token: str):
    """Test creating an astro profile."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/account/astro-data",
        json={
            "label": "My Profile",
            "relation": "partner",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "timezone_name": "UTC",
            "location_name": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["label"] == "My Profile"
    assert data["relation"] == "partner"
    assert data["birth_date"] == "1990-01-01"
    assert data["birth_time"] == "12:00:00"
    assert data["location_name"] == "New York"
    assert data.get("birth_facts_corrections_remaining") == 3
    assert "core_profile" in data
    assert data["core_profile"].get("profile_version") == "core-v2"
    assert isinstance(data["core_profile"].get("missing_fields"), list)


def test_update_astro_profile_requires_auth(client: TestClient):
    """Test that updating astro profile requires authentication."""
    response = client.put("/account/astro-data/1", json={})
    assert response.status_code == 401


def test_birth_facts_correction_limit(
    client: TestClient, test_user: User, auth_token: str, monkeypatch: pytest.MonkeyPatch
):
    """После MAX правок даты/места/времени PUT с изменением фактов рождения возвращает 403."""
    monkeypatch.setattr(account_api, "ASTRO_BIRTH_FACTS_COOLDOWN_SECONDS", 0)
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_response = client.post(
        "/account/astro-data",
        json={
            "label": "Limited edits",
            "birth_date": "1990-01-01",
            "location_name": "Berlin",
            "latitude": 52.52,
            "longitude": 13.405,
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    body = create_response.json()
    pid = body["id"]
    assert body.get("birth_facts_corrections_remaining") == 3

    for next_date in ("1990-02-01", "1990-03-01", "1990-04-01"):
        up = client.put(
            f"/account/astro-data/{pid}",
            json={"birth_date": next_date},
            headers=headers,
        )
        assert up.status_code == 200, up.text

    blocked = client.put(
        f"/account/astro-data/{pid}",
        json={"birth_date": "1990-05-01"},
        headers=headers,
    )
    assert blocked.status_code == 403

    label_ok = client.put(
        f"/account/astro-data/{pid}",
        json={"label": "Renamed only"},
        headers=headers,
    )
    assert label_ok.status_code == 200


def test_birth_facts_cooldown_blocks_second_put(
    client: TestClient, test_user: User, auth_token: str, monkeypatch: pytest.MonkeyPatch
):
    """После изменения фактов рождения повторное изменение блокируется до истечения паузы."""
    monkeypatch.setattr(account_api, "ASTRO_BIRTH_FACTS_COOLDOWN_SECONDS", 999_999)
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_response = client.post(
        "/account/astro-data",
        json={
            "label": "Cooldown",
            "birth_date": "1990-01-01",
            "location_name": "Berlin",
            "latitude": 52.52,
            "longitude": 13.405,
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    pid = create_response.json()["id"]

    first = client.put(
        f"/account/astro-data/{pid}",
        json={"birth_date": "1990-02-01"},
        headers=headers,
    )
    assert first.status_code == 200

    blocked = client.put(
        f"/account/astro-data/{pid}",
        json={"birth_date": "1990-03-01"},
        headers=headers,
    )
    assert blocked.status_code == 403

    label_ok = client.put(
        f"/account/astro-data/{pid}",
        json={"label": "Renamed only"},
        headers=headers,
    )
    assert label_ok.status_code == 200


def test_core_setup_cooldown_blocks_third_birth_change(
    client: TestClient, test_user: User, auth_token: str, monkeypatch: pytest.MonkeyPatch
):
    """Вторая смена даты через core-setup ок; третья — в пределах паузы запрещена."""
    monkeypatch.setattr(account_api, "ASTRO_BIRTH_FACTS_COOLDOWN_SECONDS", 999_999)
    headers = {"Authorization": f"Bearer {auth_token}"}
    base = {
        "first_name": "Alex",
        "last_name": "Chart",
        "label": "Я",
        "birth_time": "16:45:00",
        "time_unknown": False,
        "timezone_name": "UTC",
        "location_name": "London",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "gender": "unspecified",
    }
    r1 = client.post(
        "/account/core-setup",
        json={**base, "birth_date": "1988-11-08"},
        headers=headers,
    )
    assert r1.status_code == 200, r1.text

    r2 = client.post(
        "/account/core-setup",
        json={**base, "birth_date": "1987-11-08"},
        headers=headers,
    )
    assert r2.status_code == 200, r2.text

    r3 = client.post(
        "/account/core-setup",
        json={**base, "birth_date": "1986-11-08"},
        headers=headers,
    )
    assert r3.status_code == 403


def test_update_astro_profile(client: TestClient, test_user: User, auth_token: str):
    """Test updating an astro profile."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First create a profile
    create_response = client.post(
        "/account/astro-data",
        json={
            "label": "Original Label",
            "birth_date": "1990-01-01"
        },
        headers=headers
    )
    assert create_response.status_code == 200
    profile_id = create_response.json()["id"]
    
    # Then update it
    update_response = client.put(
        f"/account/astro-data/{profile_id}",
        json={
            "label": "Updated Label",
            "relation": "child",
            "location_name": "Moscow"
        },
        headers=headers
    )
    assert update_response.status_code == 200
    data = update_response.json()
    
    assert data["label"] == "Updated Label"
    assert data["relation"] == "child"
    assert data["location_name"] == "Moscow"
    assert "core_profile" in data
    assert data["core_profile"].get("profile_version") == "core-v2"


def test_delete_astro_profile_requires_auth(client: TestClient):
    """Test that deleting astro profile requires authentication."""
    response = client.delete("/account/astro-data/1")
    assert response.status_code == 401


def test_delete_astro_profile(client: TestClient, test_user: User, auth_token: str):
    """Test deleting an astro profile."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First create a profile
    create_response = client.post(
        "/account/astro-data",
        json={
            "label": "To Delete",
            "birth_date": "1990-01-01"
        },
        headers=headers
    )
    assert create_response.status_code == 200
    profile_id = create_response.json()["id"]
    
    # Then delete it
    delete_response = client.delete(
        f"/account/astro-data/{profile_id}",
        headers=headers
    )
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["status"] == "deleted"
    
    # Verify it's gone
    list_response = client.get("/account/astro-data", headers=headers)
    assert list_response.status_code == 200
    profiles = list_response.json()["profiles"]
    assert len([p for p in profiles if p["id"] == profile_id]) == 0


def test_set_primary_astro_profile_requires_auth(client: TestClient):
    """Test that setting primary astro profile requires authentication."""
    response = client.post("/account/astro-data/1/primary")
    assert response.status_code == 401


def test_set_primary_astro_profile(
    client: TestClient, test_user: User, auth_token: str, db_session: Session
):
    """Test setting an astro profile as primary."""
    # Бесплатный план — один профиль; для двух профилей нужен повышенный лимит.
    test_user.is_paid = True
    db_session.commit()

    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create two profiles
    profile1_response = client.post(
        "/account/astro-data",
        json={
            "label": "Profile 1",
            "birth_date": "1990-01-01",
            "is_primary": True
        },
        headers=headers
    )
    assert profile1_response.status_code == 200
    profile1_id = profile1_response.json()["id"]
    
    profile2_response = client.post(
        "/account/astro-data",
        json={
            "label": "Profile 2",
            "birth_date": "1995-05-15"
        },
        headers=headers
    )
    assert profile2_response.status_code == 200
    profile2_id = profile2_response.json()["id"]
    
    # Set profile2 as primary
    set_primary_response = client.post(
        f"/account/astro-data/{profile2_id}/primary",
        headers=headers
    )
    assert set_primary_response.status_code == 200
    data = set_primary_response.json()
    assert data["is_primary"] is True
    assert "core_profile" in data
    assert data["core_profile"].get("profile_version") == "core-v2"
    assert data["core_profile"].get("astro", {}).get("profile_id") == profile2_id

    # Verify profile1 is no longer primary
    list_response = client.get("/account/astro-data", headers=headers)
    assert list_response.status_code == 200
    profiles = list_response.json()["profiles"]
    profile1 = next(p for p in profiles if p["id"] == profile1_id)
    assert profile1["is_primary"] is False
    assert profile1["relation"] == "close_person"
    profile2 = next(p for p in profiles if p["id"] == profile2_id)
    assert profile2["is_primary"] is True
    assert profile2["relation"] == "self"
