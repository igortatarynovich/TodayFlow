"""Acceptance: Profile Availability Matrix 3.1 against real payload shapes.

Invariant: one interpretation from all available data; tariff only reveals.

Contradiction rules under test:
1. Access-gated slot → must exist in profile_matrix_v0.slots (full result).
2. Data-omitted slot → must NOT appear in slots (not generated / not projected).
3. revealed_slots ⊆ slots; access_gated ∩ revealed = ∅.
4. Free and Trial share data_eligible and the same slots keys for equal inputs.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

import pytest

from todayflow_backend.services.capability_resolver_v0 import (
    L2_STRUCTURE_SLOTS,
    L3_SLOTS,
    NAME_SLOTS,
    SLOT_HELPS,
    SLOT_HOME,
    SLOT_IDENTITY,
    SLOT_LIMITATIONS,
    SLOT_NAME_NUMEROLOGY,
    SLOT_NATAL_STRUCTURE,
    SLOT_WORK,
    resolve_capability,
)
from todayflow_backend.services.natal_facts_contract_v1 import (
    date_only_fallback,
    validate_natal_facts,
)
from todayflow_backend.services.profile_matrix_adapter_v0 import project_profile_slots_v0

BIRTH = date(1990, 5, 15)

CONTENT_SLOTS = frozenset(
    {
        SLOT_IDENTITY,
        SLOT_NAME_NUMEROLOGY,
        SLOT_NATAL_STRUCTURE,
        SLOT_HELPS,
        SLOT_HOME,
        SLOT_WORK,
        "sun_element_numerology",
        "cultural_catalog",
        "emotional_style",
        "decision_style",
        "relationship_style",
        "money_patterns",
        "strengths",
        "tensions_growth",
    }
)


# Rich saved-profile contract (same personality for Free/Trial).
FULL_CONTRACT: dict[str, Any] = {
    "recognition_line": "Вы держите ясность через спокойный ритм.",
    "identity_core": "Устойчивость и точность.",
    "decision_style": "Сначала тело, потом структура.",
    "relationship_style": "Сначала доверие, потом открытость.",
    "emotional_style": "Чувствует глубже, чем показывает.",
    "work_style": "Доводит контур до конца.",
    "money_style": "Копит через систему, не через импульс.",
    "home_style": "База важнее скорости.",
    "strengths": ["Выдержка", "Ясный фокус"],
    "growth_zones": ["Спешка ломает точность"],
    "recurring_patterns": ["Нужна тишина перед решением"],
    "helps": ["Утренний ритуал без экрана", "Один закрытый контур в день"],
    "element": "earth",
    "life_path": 7,
}


def _full_natal_facts() -> dict[str, Any]:
    return validate_natal_facts(
        {
            "provider": "acceptance_fixture",
            "provider_version": "v1",
            "mode": "full",
            "confidence": 0.7,
            "planets": [{"id": "sun", "sign": "taurus", "degree": 24.0, "house": 10}],
            "angles": {
                "ascendant": {"sign": "virgo", "degree": 12.0, "absolute_longitude": 162.0},
                "mc": {"sign": "gemini", "degree": 5.0, "absolute_longitude": 65.0},
            },
            "houses": [{"house": 1, "sign": "virgo", "degree": 12.0}],
            "unavailable_facts": [],
        },
        expected_mode="full",
    )


def _date_only_facts(*, reason: str) -> dict[str, Any]:
    return date_only_fallback(BIRTH, structure_unavailable_reason=reason)


def _name_pack() -> dict[str, Any]:
    return {
        "expression_number": 5,
        "soul_urge_number": 3,
        "personality_number": 2,
    }


def _assert_no_slot_contradictions(proj: dict[str, Any], *, access: str) -> None:
    """Core acceptance: no reveal/data contradictions."""
    cap = proj["capability"]
    slots_meta = cap["profile_slots"]
    data_eligible = set(slots_meta["data_eligible"])
    revealed = set(slots_meta["revealed"])
    access_gated = set(slots_meta["access_gated"])
    omitted = set(slots_meta["omitted"])

    slots = proj["slots"]
    revealed_slots = proj["revealed_slots"]
    gated_ids = set(proj["access_gated_slot_ids"])
    omitted_slots = proj["omitted_slots"]

    # Partition integrity
    assert revealed.isdisjoint(access_gated)
    assert revealed | access_gated == data_eligible
    assert data_eligible.isdisjoint(omitted)

    # Projection integrity
    assert set(revealed_slots).issubset(set(slots))
    assert set(slots).issubset(data_eligible)
    assert gated_ids == (set(slots) & access_gated)

    # Access-gated content must remain in full result when present in contract/facts
    for slot_id in gated_ids:
        assert slot_id in slots, f"{access}: gated {slot_id} missing from full slots"

    # Data-omitted slots must not be generated into full result
    for slot_id in omitted:
        assert slot_id not in slots, f"{access}: data-omitted {slot_id} leaked into slots"
        assert omitted_slots.get(slot_id) == "data_gate" or slot_id not in omitted_slots or omitted_slots.get(
            slot_id
        ) in ("data_gate", "empty")

    # Empty data-eligible slots may be omitted as empty — never as access_gate mislabel
    for slot_id, reason in omitted_slots.items():
        if slot_id in access_gated and slot_id in data_eligible:
            # If content existed it would be in slots; empty is ok
            assert reason in ("empty", "data_gate")
        if reason == "data_gate":
            assert slot_id not in data_eligible


def _project(
    *,
    access: str,
    display_name: str | None = None,
    birth_time: time | str | None = None,
    time_unknown: bool = True,
    latitude: float | None = None,
    longitude: float | None = None,
    location_name: str | None = None,
    facts: dict[str, Any] | None = None,
    name_numerology: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return project_profile_slots_v0(
        contract=contract if contract is not None else FULL_CONTRACT,
        natal_facts=facts,
        birth_date=BIRTH.isoformat(),
        birth_time=birth_time.strftime("%H:%M:%S") if isinstance(birth_time, time) else birth_time,
        time_unknown=time_unknown,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        display_name=display_name,
        name_numerology=name_numerology,
        access=access,  # type: ignore[arg-type]
    )


# --- Scenario payloads -------------------------------------------------


@pytest.mark.parametrize("access", ["free", "trial"])
def test_acceptance_date_only(access: str):
    facts = _date_only_facts(reason="birth_time_missing")
    proj = _project(access=access, time_unknown=True, facts=facts)
    cap = proj["capability"]

    assert cap["mode"] == "date_only"
    assert cap["angles_eligible"] is False
    assert SLOT_IDENTITY in proj["slots"]
    assert SLOT_HELPS in proj["slots"]  # interpretation present
    assert SLOT_NATAL_STRUCTURE not in proj["slots"]
    assert SLOT_NAME_NUMEROLOGY not in proj["slots"]
    assert all(s not in proj["slots"] for s in L2_STRUCTURE_SLOTS)
    assert any(m["code"] == "need_birth_time" for m in cap["user_messages"])
    assert any(m["code"] == "need_name" for m in cap["user_messages"])

    _assert_no_slot_contradictions(proj, access=access)

    if access == "free":
        assert SLOT_HELPS not in proj["revealed_slots"]
        assert SLOT_HELPS in proj["access_gated_slot_ids"]
    else:
        assert SLOT_HELPS in proj["revealed_slots"]


@pytest.mark.parametrize("access", ["free", "trial"])
def test_acceptance_date_plus_name(access: str):
    facts = _date_only_facts(reason="birth_time_missing")
    proj = _project(
        access=access,
        display_name="Анна",
        time_unknown=True,
        facts=facts,
        name_numerology=_name_pack(),
    )
    cap = proj["capability"]

    assert cap["mode"] == "date_only"
    assert cap["has_name"] is True
    assert SLOT_NAME_NUMEROLOGY in proj["slots"]
    assert SLOT_NAME_NUMEROLOGY in proj["revealed_slots"]
    assert SLOT_NATAL_STRUCTURE not in proj["slots"]
    assert not any(m["code"] == "need_name" for m in cap["user_messages"])
    assert any(m["code"] == "need_birth_time" for m in cap["user_messages"])
    _assert_no_slot_contradictions(proj, access=access)


@pytest.mark.parametrize("access", ["free", "trial"])
def test_acceptance_time_without_place(access: str):
    facts = _date_only_facts(reason="birth_place_missing")
    # Even if LLM/fixture tried to invent ASC — validate strips it for date_only.
    invented = validate_natal_facts(
        {
            **facts,
            "angles": {"ascendant": {"sign": "leo", "degree": 1, "absolute_longitude": 121}},
            "houses": [{"house": 1, "sign": "leo"}],
        },
        expected_mode="date_only",
        structure_unavailable_reason="birth_place_missing",
    )
    assert invented["angles"]["ascendant"] is None
    assert invented["houses"] == []

    proj = _project(
        access=access,
        birth_time=time(14, 30),
        time_unknown=False,
        facts=invented,
    )
    cap = proj["capability"]

    assert cap["mode"] == "date_only"
    assert cap["has_time"] is True
    assert cap["birth_time_unsuitable_for_angles"] is True
    # Resolver preserves entered time (capability pack).
    raw_cap = resolve_capability(
        birth_date=BIRTH,
        birth_time=time(14, 30),
        time_unknown=False,
        access=access,  # type: ignore[arg-type]
    )
    assert raw_cap["available_input"]["birth_time"] == "14:30:00"
    assert raw_cap["available_input"]["angles_eligible"] is False

    assert SLOT_NATAL_STRUCTURE not in proj["slots"]
    assert SLOT_HOME not in proj["slots"]
    assert SLOT_WORK not in proj["slots"]
    assert any(m["code"] == "need_birth_place" for m in cap["user_messages"])
    _assert_no_slot_contradictions(proj, access=access)


@pytest.mark.parametrize("access", ["free", "trial"])
def test_acceptance_full_birth_set(access: str):
    facts = _full_natal_facts()
    proj = _project(
        access=access,
        display_name="Анна",
        birth_time=time(14, 30),
        time_unknown=False,
        latitude=55.75,
        longitude=37.62,
        location_name="Москва",
        facts=facts,
        name_numerology=_name_pack(),
    )
    cap = proj["capability"]

    assert cap["mode"] == "full"
    assert cap["angles_eligible"] is True
    assert cap["birth_time_unsuitable_for_angles"] is False
    assert SLOT_NATAL_STRUCTURE in proj["slots"]
    assert SLOT_NAME_NUMEROLOGY in proj["slots"]
    assert SLOT_HELPS in proj["slots"]
    assert facts["angles"]["ascendant"]["sign"] == "virgo"
    assert not any(
        m["code"] in ("need_birth_time", "need_birth_place", "need_name") for m in cap["user_messages"]
    )
    _assert_no_slot_contradictions(proj, access=access)


def test_acceptance_free_vs_trial_same_full_result_different_reveal():
    facts = _full_natal_facts()
    kwargs = dict(
        display_name="Анна",
        birth_time=time(14, 30),
        time_unknown=False,
        latitude=55.75,
        longitude=37.62,
        location_name="Москва",
        facts=facts,
        name_numerology=_name_pack(),
    )
    free = _project(access="free", **kwargs)
    trial = _project(access="trial", **kwargs)

    assert free["capability"]["profile_slots"]["data_eligible"] == trial["capability"]["profile_slots"][
        "data_eligible"
    ]
    assert set(free["slots"].keys()) & CONTENT_SLOTS == set(trial["slots"].keys()) & CONTENT_SLOTS
    assert free["slots"][SLOT_HELPS] == trial["slots"][SLOT_HELPS]
    assert free["slots"][SLOT_IDENTITY] == trial["slots"][SLOT_IDENTITY]
    assert free["slots"][SLOT_NATAL_STRUCTURE] == trial["slots"][SLOT_NATAL_STRUCTURE]

    assert SLOT_HELPS in free["slots"] and SLOT_HELPS not in free["revealed_slots"]
    assert SLOT_HELPS in trial["revealed_slots"]
    assert SLOT_HELPS in free["capability"]["profile_slots"]["access_gated"]
    assert trial["capability"]["profile_slots"]["access_gated"] == []
    assert set(L3_SLOTS).issubset(set(free["capability"]["profile_slots"]["access_gated"]))

    _assert_no_slot_contradictions(free, access="free")
    _assert_no_slot_contradictions(trial, access="trial")


def test_acceptance_data_gap_never_faked_as_access_gate():
    """Name / structure missing because of data — not because of Free."""
    facts = _date_only_facts(reason="birth_time_missing")
    free = _project(access="free", time_unknown=True, facts=facts)
    trial = _project(access="trial", time_unknown=True, facts=facts)

    for proj in (free, trial):
        omitted = proj["capability"]["profile_slots"]["omitted"]
        assert SLOT_NAME_NUMEROLOGY in omitted
        assert SLOT_NATAL_STRUCTURE in omitted
        assert SLOT_NAME_NUMEROLOGY not in proj["slots"]
        assert SLOT_NATAL_STRUCTURE not in proj["slots"]
        # Must not be classified as access_gated
        assert SLOT_NAME_NUMEROLOGY not in proj["capability"]["profile_slots"]["access_gated"]
        assert SLOT_NATAL_STRUCTURE not in proj["capability"]["profile_slots"]["access_gated"]
        assert NAME_SLOTS.isdisjoint(proj["capability"]["profile_slots"]["access_gated"])
        assert L2_STRUCTURE_SLOTS.isdisjoint(proj["capability"]["profile_slots"]["access_gated"])


def test_acceptance_limitations_slot_carries_resolver_ctas():
    facts = _date_only_facts(reason="birth_time_missing")
    proj = _project(access="free", time_unknown=True, facts=facts)
    lim = proj["slots"].get(SLOT_LIMITATIONS)
    assert isinstance(lim, dict)
    codes = {m.get("code") for m in (lim.get("user_messages") or [])}
    assert "need_birth_time" in codes
    assert "need_name" in codes
    assert "l3_gated" in codes
