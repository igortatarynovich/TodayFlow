"""Provenance: Tarot spread context generation logs include core_profile_snapshot_id."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.core import models as api_models
from todayflow_backend.db import models as db_models
from todayflow_backend.main import app
from todayflow_backend.services.auth import hash_password
from todayflow_backend.services.core_profile import get_core_profile_service


@pytest.fixture
def user_with_birth(db_session: Session) -> db_models.User:
    user = db_models.User(
        email="tarot-spread-prov@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.add(
        db_models.UserSettings(
            user_id=user.id,
            first_name="Anna",
            locale="ru",
            gender="unspecified",
        )
    )
    db_session.add(
        db_models.AstroProfile(
            user_id=user.id,
            label="Я",
            birth_date=date(1990, 5, 15),
            time_unknown=True,
            location_name="Moscow",
            latitude=55.75,
            longitude=37.61,
            is_primary=True,
            relation="self",
        )
    )
    db_session.commit()
    return user


@pytest.mark.smoke
def test_tarot_spread_context_logs_core_profile_snapshot_id(
    client: TestClient, db_session: Session, user_with_birth: db_models.User
) -> None:
    """POST /tarot/spread/context must record the core profile snapshot id in the generation log."""

    class FakeCoreProfileService:
        def build_cached_or_baseline(self, db, user, astro_profile_id=None):
            return {"snapshot_id": 123, "astro": {}, "numerology": {}}

    app.dependency_overrides[get_core_profile_service] = lambda: FakeCoreProfileService()
    try:
        login = client.post(
            "/auth/login",
            json={"email": user_with_birth.email, "password": "testpassword123"},
        )
        assert login.status_code == 200
        token = login.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        reading = api_models.TarotSpreadReading(meaning="test meaning")
        reading._engine_meta = {"llm_model": "mock-model", "prompt_version": "v1"}
        tarot_answer = {"synthesis_mode": "tarot_llm_v1", "meaning": "test"}

        with (
            patch(
                "todayflow_backend.api.tarot.compose_tarot_answer_v1",
                return_value=(reading, tarot_answer),
            ),
            patch("todayflow_backend.api.tarot.assemble_experience_slice", return_value={}),
            patch(
                "todayflow_backend.services.person_meaning_from_core_v0.person_sot_label",
                return_value="person_sot",
            ),
        ):
            response = client.post("/tarot/spread/context", json={}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "tarot_answer_v1" in data
        gen_id_str = data["tarot_answer_v1"].get("generation_id")
        assert gen_id_str

        log = (
            db_session.query(db_models.GenerationLog)
            .filter(db_models.GenerationLog.id == int(gen_id_str))
            .first()
        )
        assert log is not None
        assert log.core_profile_snapshot_id == 123
    finally:
        app.dependency_overrides.pop(get_core_profile_service, None)
