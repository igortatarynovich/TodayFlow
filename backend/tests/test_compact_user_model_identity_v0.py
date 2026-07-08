"""Identity slice + profile identity atoms in compact_user_model_v0."""

from datetime import date

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User
from todayflow_backend.services.compact_user_model_v0 import (
    PROFILE_IDENTITY_ATOM_CONTRACT,
    _identity_atoms_from_core_profile,
    _identity_from_core_profile,
    build_compact_user_model_v0,
)


@pytest.fixture
def test_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="cum-identity@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_build_compact_user_model_identity_atoms(db_session: Session, test_user: User):
    core_profile = {
        "person": {"display_name": "Igor"},
        "astro": {"sun_sign": "Aquarius"},
        "numerology": {"life_path": 7},
        "baseline": {"archetype_seed": "Sage"},
        "interpretation": {
            "identity": "Ты лучше всего раскрываешься там, где есть понимание смысла и свобода мысли.",
            "strengths": ["системное мышление", "спокойствие под давлением"],
            "watchouts": ["перегруз задачами", "хаос без структуры"],
        },
    }

    payload = build_compact_user_model_v0(
        db_session,
        user_id=test_user.id,
        core_profile=core_profile,
        reference_date=date(2026, 7, 3),
    )

    identity = payload["identity"]
    assert identity["display_name"] == "Igor"
    assert identity["sun_sign"] == "Aquarius"
    assert identity["life_path"] == 7
    assert identity["archetype"] == "Sage"
    assert identity["strengths"] == ["системное мышление", "спокойствие под давлением"]
    assert identity["constraints"] == ["перегруз задачами", "хаос без структуры"]

    atoms = payload["knowledge_atoms_top_k"]
    assert any(atom.get("knowledge_id") == "profile-identity-summary" for atom in atoms)
    assert any(atom.get("knowledge_id") == "profile-archetype" for atom in atoms)
    assert any(atom.get("contract_version") == PROFILE_IDENTITY_ATOM_CONTRACT for atom in atoms)
    assert atoms[0]["data_class"] == "identity"


def test_identity_moon_rising_from_natal_summary():
    identity = _identity_from_core_profile(
        {
            "person": {},
            "astro": {"sun_sign": "Aquarius"},
            "numerology": {},
            "baseline": {},
            "interpretation": {},
            "natal_summary": {
                "available": True,
                "angles": {"ascendant_sign": "Virgo"},
                "luminaries": [
                    {"name": "Sun", "sign": "Aquarius"},
                    {"name": "Moon", "sign": "Pisces"},
                ],
            },
        }
    )
    assert identity["moon_sign"] == "Pisces"
    assert identity["rising_sign"] == "Virgo"

    atoms = _identity_atoms_from_core_profile(
        {
            "baseline": {"archetype_seed": "Sage"},
            "interpretation": {},
            "natal_summary": {
                "angles": {"ascendant_sign": "Virgo"},
                "luminaries": [{"name": "Moon", "sign": "Pisces"}],
            },
        }
    )
    summaries = [a.get("claim_summary") for a in atoms]
    assert "Луна в Pisces" in summaries
    assert "Асцендент в Virgo" in summaries
