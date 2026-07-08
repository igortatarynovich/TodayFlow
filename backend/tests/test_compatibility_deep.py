"""POST /compatibility/compare, synastry, composite, davison, psych, group; GET business-partnership — фаза 4; не smoke."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from sqlalchemy.orm.attributes import flag_modified

from todayflow_backend.db.models import CachedCompatibility, User


@pytest.fixture
def paid_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="deep_compat@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def deep_compat_headers(client: TestClient, paid_user: User) -> dict[str, str]:
    r = client.post(
        "/auth/login",
        json={"email": paid_user.email, "password": "testpassword123"},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _create_astro(client: TestClient, headers: dict[str, str], *, label: str) -> int:
    r = client.post(
        "/account/astro-data",
        json={
            "label": label,
            "relation": "close_person",
            "birth_date": "1990-06-15",
            "birth_time": "14:30:00",
            "timezone_name": "UTC",
            "location_name": "Berlin",
            "latitude": 52.52,
            "longitude": 13.405,
            "is_primary": label == "A",
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return int(r.json()["id"])


@pytest.fixture
def two_astro_ids(client: TestClient, deep_compat_headers: dict[str, str]) -> tuple[int, int]:
    id_a = _create_astro(client, deep_compat_headers, label="A")
    id_b = _create_astro(client, deep_compat_headers, label="B")
    return id_a, id_b


@pytest.fixture
def three_astro_ids(client: TestClient, deep_compat_headers: dict[str, str]) -> tuple[int, int, int]:
    return (
        _create_astro(client, deep_compat_headers, label="A"),
        _create_astro(client, deep_compat_headers, label="B"),
        _create_astro(client, deep_compat_headers, label="C"),
    )


def test_compare_requires_auth(client: TestClient):
    assert (
        client.post(
            "/compatibility/compare",
            json={"profile_id_1": 1, "profile_id_2": 2},
        ).status_code
        == 401
    )


@pytest.mark.parametrize(
    "path",
    [
        "/compatibility/composite",
        "/compatibility/davison",
        "/compatibility/psych",
    ],
)
def test_composite_davison_psych_require_auth(client: TestClient, path: str):
    assert (
        client.post(path, json={"profile_id_1": 1, "profile_id_2": 2}).status_code == 401
    )


def test_group_requires_auth(client: TestClient):
    assert (
        client.post("/compatibility/group", json={"profile_ids": [1, 2, 3]}).status_code
        == 401
    )


def test_business_partnership_requires_auth(client: TestClient):
    assert (
        client.get("/compatibility/business-partnership?profile1_id=1&profile2_id=2").status_code
        == 401
    )


def test_synastry_requires_auth(client: TestClient):
    assert (
        client.post(
            "/compatibility/synastry",
            json={"profile_id_1": 1, "profile_id_2": 2},
        ).status_code
        == 401
    )


def test_synastry_profile_not_found(client: TestClient, deep_compat_headers: dict[str, str]):
    r = client.post(
        "/compatibility/synastry",
        json={"profile_id_1": 99999, "profile_id_2": 88888},
        headers=deep_compat_headers,
    )
    assert r.status_code == 404


def test_compare_quick_two_profiles(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    id_a, id_b = two_astro_ids
    r = client.post(
        "/compatibility/compare",
        json={
            "profile_id_1": id_a,
            "profile_id_2": id_b,
            "relation_mode": "romantic",
        },
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["profile_1"]["id"] == id_a
    assert data["profile_2"]["id"] == id_b
    comp = data.get("compatibility") or {}
    assert isinstance(comp.get("overall_score"), int)
    assert 0 <= comp["overall_score"] <= 100
    ed = comp.get("editorial")
    assert isinstance(ed, dict)
    assert isinstance(ed.get("pair_thesis"), str)
    fa = data.get("funnel_artifact")
    assert isinstance(fa, dict)
    assert fa.get("pipeline_version") == "funnel-v1"
    assert fa.get("accuracy_tier") == "birth_dates"
    assert isinstance(fa.get("domain_scores"), list) and len(fa["domain_scores"]) > 0
    assert isinstance(fa.get("dynamic_core"), dict)


def test_composite_two_profiles(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    id_a, id_b = two_astro_ids
    r = client.post(
        "/compatibility/composite",
        json={"profile_id_1": id_a, "profile_id_2": id_b},
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data.get("positions"), list) and len(data["positions"]) > 0
    assert isinstance(data.get("houses"), dict)
    assert isinstance(data.get("aspects"), list)
    interp = data.get("interpretation")
    assert isinstance(interp, dict)
    assert isinstance(interp.get("strengths"), list)


def test_davison_two_profiles(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    id_a, id_b = two_astro_ids
    r = client.post(
        "/compatibility/davison",
        json={"profile_id_1": id_a, "profile_id_2": id_b},
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data.get("midpoint_date"), str) and len(data["midpoint_date"]) > 0
    assert isinstance(data.get("midpoint_time"), str)
    assert isinstance(data.get("description"), str)


def test_psych_two_profiles(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    id_a, id_b = two_astro_ids
    r = client.post(
        "/compatibility/psych",
        json={"profile_id_1": id_a, "profile_id_2": id_b},
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    cs = data.get("conflict_styles") or {}
    assert isinstance(cs.get("person1_style"), str)
    assert isinstance(cs.get("person2_style"), str)
    ca = data.get("closeness_autonomy") or {}
    assert isinstance(ca.get("person1_style"), str)
    assert isinstance(data.get("communication_recommendations"), list)


def test_group_less_than_three_profiles_400(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    id_a, id_b = two_astro_ids
    r = client.post(
        "/compatibility/group",
        json={"profile_ids": [id_a, id_b]},
        headers=deep_compat_headers,
    )
    assert r.status_code == 400


def test_group_three_profiles(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    three_astro_ids: tuple[int, int, int],
):
    id_a, id_b, id_c = three_astro_ids
    r = client.post(
        "/compatibility/group",
        json={"profile_ids": [id_a, id_b, id_c]},
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("group_size") == 3
    assert len(data.get("profile_labels") or []) == 3
    assert len(data.get("pairwise_synastry") or []) == 3  # C(3,2)
    assert isinstance(data.get("group_dynamics"), dict)
    assert isinstance(data.get("recommendations"), list)


def test_group_profile_not_found_404(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    three_astro_ids: tuple[int, int, int],
):
    id_a, id_b, _ = three_astro_ids
    r = client.post(
        "/compatibility/group",
        json={"profile_ids": [id_a, id_b, 999_999]},
        headers=deep_compat_headers,
    )
    assert r.status_code == 404


@pytest.mark.parametrize("relation_mode", ["romantic", "family", "parent_child", "business"])
def test_synastry_two_profiles_deep_payload(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
    relation_mode: str,
):
    id_a, id_b = two_astro_ids
    r = client.post(
        "/compatibility/synastry",
        json={
            "profile_id_1": id_a,
            "profile_id_2": id_b,
            "relation_mode": relation_mode,
        },
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data.get("overall_score"), int)
    assert isinstance(data.get("summary"), str) and len(data["summary"]) > 0
    assert isinstance(data.get("synastry"), dict)
    assert data.get("deep_dive") is not None
    dd = data["deep_dive"]
    assert isinstance(dd.get("relationship_archetype"), str)
    assert isinstance(dd.get("dimensions"), list) and len(dd["dimensions"]) > 0
    ed = data.get("editorial")
    assert isinstance(ed, dict)
    assert isinstance(ed.get("pair_thesis"), str) and len(ed["pair_thesis"]) > 0
    fa = data.get("funnel_artifact")
    assert isinstance(fa, dict)
    assert fa.get("pipeline_version") == "funnel-v1"
    assert fa.get("accuracy_tier") == "full_profile"
    assert isinstance(fa.get("domain_scores"), list) and len(fa["domain_scores"]) > 0
    assert isinstance(fa.get("dynamic_core"), dict)


def test_synastry_recomputes_funnel_when_cached_payload_missing_funnel_artifact(
    client: TestClient,
    db_session: Session,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    """Если в записи кеша убрать funnel_artifact, следующий ответ снова отдаёт воронку (дозаполнение в обработчике)."""
    id_a, id_b = two_astro_ids
    body = {
        "profile_id_1": id_a,
        "profile_id_2": id_b,
        "relation_mode": "romantic",
    }
    r1 = client.post("/compatibility/synastry", json=body, headers=deep_compat_headers)
    assert r1.status_code == 200, r1.text
    assert isinstance(r1.json().get("funnel_artifact"), dict)

    row = (
        db_session.query(CachedCompatibility)
        .filter(CachedCompatibility.compatibility_type == "synastry")
        .order_by(CachedCompatibility.updated_at.desc())
        .first()
    )
    assert row is not None
    wrapped = dict(row.result_data) if isinstance(row.result_data, dict) else {}
    inner = dict(wrapped.get("payload") or wrapped)
    inner.pop("funnel_artifact", None)
    if "payload" in wrapped:
        wrapped["payload"] = inner
        row.result_data = wrapped
    else:
        row.result_data = inner
    flag_modified(row, "result_data")
    db_session.add(row)
    db_session.commit()

    r2 = client.post("/compatibility/synastry", json=body, headers=deep_compat_headers)
    assert r2.status_code == 200, r2.text
    fa = r2.json().get("funnel_artifact")
    assert isinstance(fa, dict)
    assert fa.get("accuracy_tier") == "full_profile"


def test_business_partnership_two_profiles(
    client: TestClient,
    deep_compat_headers: dict[str, str],
    two_astro_ids: tuple[int, int],
):
    id_a, id_b = two_astro_ids
    r = client.get(
        "/compatibility/business-partnership",
        params={"profile1_id": id_a, "profile2_id": id_b},
        headers=deep_compat_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data.get("role_compatibility"), list)
    assert isinstance(data.get("structural_recommendations"), list)
    assert isinstance(data.get("communication_approach"), list)
    assert isinstance(data.get("division_of_responsibilities"), list)
    assert isinstance(data.get("risk_factors"), list)
    assert data.get("decision_making_style") is None or isinstance(
        data["decision_making_style"], str
    )
    assert data.get("growth_potential") is None or isinstance(data["growth_potential"], str)


def test_business_partnership_profile_not_found(
    client: TestClient, deep_compat_headers: dict[str, str]
):
    r = client.get(
        "/compatibility/business-partnership",
        params={"profile1_id": 99999, "profile2_id": 88888},
        headers=deep_compat_headers,
    )
    assert r.status_code == 404
