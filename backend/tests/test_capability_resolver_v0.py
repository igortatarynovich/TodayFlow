"""Capability Resolver + Profile matrix adapter — birth states + Free/Trial L3.

Minimal Profile Journey stack: no natal_facts generation contract dependency.
"""

from datetime import date, time

from todayflow_backend.services.capability_resolver_v0 import (
    SLOT_HELPS,
    SLOT_IDENTITY,
    SLOT_NAME_NUMEROLOGY,
    SLOT_NATAL_STRUCTURE,
    resolve_capability,
)
from todayflow_backend.services.profile_matrix_adapter_v0 import (
    project_profile_slots_v0,
    resolve_access_tier,
    slot_allowed,
)


def _reason_for(unavailable: list, key: str) -> str | None:
    for u in unavailable:
        if u.get("key") == key:
            return u.get("reason")
    return None


def _date_only_facts() -> dict:
    return {
        "mode": "date_only",
        "planets": [{"id": "sun", "sign": "taurus"}],
        "angles": {},
        "houses": [],
        "unavailable_facts": [{"key": "ascendant", "reason": "birth_time_missing"}],
    }


def test_resolve_access_tier_trial_and_paid():
    assert resolve_access_tier(subscription_status="trialing") == "trial"
    assert resolve_access_tier(insight_depth_tier="pro") == "paid"
    assert resolve_access_tier(billing_level="lite") == "paid"
    assert resolve_access_tier() == "free"
    assert resolve_access_tier(is_guest=True) == "guest"


def test_state_date_time_without_place_preserves_time():
    cap = resolve_capability(
        birth_date=date(1990, 5, 15),
        birth_time=time(10, 0),
        time_unknown=False,
        access="free",
    )
    assert cap["mode"] == "date_only"
    assert cap["angles_eligible"] is False
    assert _reason_for(cap["unavailable_facts"], "ascendant") == "birth_place_missing"
    assert SLOT_NATAL_STRUCTURE not in cap["profile_slots"]["data_eligible"]


def test_state_date_only():
    cap = resolve_capability(birth_date=date(1990, 5, 15), time_unknown=True, access="free")
    assert cap["mode"] == "date_only"
    assert _reason_for(cap["unavailable_facts"], "ascendant") == "birth_time_missing"


def test_state_full_birth():
    cap = resolve_capability(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        time_unknown=False,
        latitude=55.75,
        longitude=37.62,
        location_name="Moscow",
        timezone_name="Europe/Moscow",
        access="paid",
    )
    assert cap["mode"] == "full"
    assert cap["angles_eligible"] is True
    assert SLOT_NATAL_STRUCTURE in cap["profile_slots"]["data_eligible"]
    assert SLOT_NATAL_STRUCTURE in cap["profile_slots"]["revealed"]


def test_name_numerology_requires_display_name():
    without = resolve_capability(birth_date=date(1990, 5, 15), access="free")
    with_name = resolve_capability(
        birth_date=date(1990, 5, 15),
        display_name="Игорь",
        access="free",
    )
    assert SLOT_NAME_NUMEROLOGY not in without["profile_slots"]["data_eligible"]
    assert SLOT_NAME_NUMEROLOGY in with_name["profile_slots"]["data_eligible"]


def test_free_gates_l3_reveal_trial_opens():
    free = resolve_capability(birth_date=date(1990, 5, 15), access="free")
    trial = resolve_capability(birth_date=date(1990, 5, 15), access="trial")
    paid = resolve_capability(birth_date=date(1990, 5, 15), access="paid")
    assert SLOT_HELPS not in free["profile_slots"]["revealed"]
    assert SLOT_HELPS in trial["profile_slots"]["revealed"]
    assert SLOT_HELPS in paid["profile_slots"]["revealed"]
    assert free["layers"]["l3_in_result"] is True
    assert free["layers"]["l3_revealed"] is False
    assert trial["layers"]["l3_revealed"] is True
    assert paid["layers"]["l3_revealed"] is True


def test_adapter_keeps_helps_in_slots_gates_reveal_on_free():
    contract = {
        "recognition_line": "Вы опираетесь на устойчивость и ясность.",
        "helps": ["Держите утренний ритуал", "Закрывайте один контур в день"],
        "strengths": ["Выдержка"],
    }
    facts = _date_only_facts()
    free_proj = project_profile_slots_v0(
        contract=contract,
        natal_facts=facts,
        birth_date="1990-05-15",
        access="free",
    )
    trial_proj = project_profile_slots_v0(
        contract=contract,
        natal_facts=facts,
        birth_date="1990-05-15",
        access="trial",
    )
    assert SLOT_IDENTITY in free_proj["slots"]
    assert SLOT_HELPS in free_proj["slots"]  # same saved result
    assert SLOT_HELPS not in free_proj["revealed_slots"]
    assert SLOT_HELPS in free_proj["access_gated_slot_ids"]
    assert SLOT_HELPS in trial_proj["revealed_slots"]
    assert not slot_allowed(free_proj["capability"], SLOT_HELPS)
    assert slot_allowed(trial_proj["capability"], SLOT_HELPS)


def test_adapter_omits_natal_structure_without_full_facts():
    contract = {"recognition_line": "Узнавание."}
    facts = _date_only_facts()
    proj = project_profile_slots_v0(
        contract=contract,
        natal_facts=facts,
        birth_date="1990-05-15",
        birth_time="14:30:00",
        time_unknown=False,
        access="paid",
    )
    # time without place → structure slot not allowed
    assert SLOT_NATAL_STRUCTURE not in proj["slots"]
    assert proj["capability"]["mode"] == "date_only"
