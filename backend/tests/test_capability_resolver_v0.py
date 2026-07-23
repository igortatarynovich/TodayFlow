"""Capability Resolver + Profile matrix adapter — four birth states + Free/Trial L3."""

from datetime import date, time

from todayflow_backend.services.capability_resolver_v0 import (
    SLOT_HELPS,
    SLOT_IDENTITY,
    SLOT_NAME_NUMEROLOGY,
    SLOT_NATAL_STRUCTURE,
    resolve_capability,
)
from todayflow_backend.services.natal_facts_contract_v1 import (
    build_available_input,
    date_only_fallback,
    generate_natal_facts,
    validate_natal_facts,
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


def test_resolve_access_tier_trial_and_paid():
    assert resolve_access_tier(subscription_status="trialing") == "trial"
    assert resolve_access_tier(insight_depth_tier="pro") == "paid"
    assert resolve_access_tier(billing_level="lite") == "paid"
    assert resolve_access_tier() == "free"
    assert resolve_access_tier(is_guest=True) == "guest"


def test_state_date_time_without_place_preserves_time():
    cap = resolve_capability(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        time_unknown=False,
        access="free",
    )
    assert cap["mode"] == "date_only"
    assert cap["has_time"] is True
    assert cap["has_place"] is False
    assert cap["available_input"]["birth_time"] == "14:30:00"
    assert cap["available_input"]["time_unknown"] is False
    assert cap["available_input"]["angles_eligible"] is False
    assert cap["available_input"]["birth_time_unsuitable_for_angles"] is True
    assert cap["birth_time_unsuitable_for_angles"] is True
    assert _reason_for(cap["unavailable_facts"], "ascendant") == "birth_place_missing"
    assert SLOT_NATAL_STRUCTURE not in cap["profile_slots"]["data_eligible"]
    assert SLOT_HELPS in cap["profile_slots"]["data_eligible"]
    assert SLOT_HELPS in cap["profile_slots"]["access_gated"]
    assert SLOT_HELPS not in cap["profile_slots"]["revealed"]


def test_state_date_only():
    cap = resolve_capability(birth_date=date(1990, 5, 15), access="free")
    assert cap["mode"] == "date_only"
    assert cap["has_time"] is False
    assert cap["has_place"] is False
    assert cap["has_name"] is False
    assert _reason_for(cap["unavailable_facts"], "ascendant") == "birth_time_missing"
    assert _reason_for(cap["unavailable_facts"], "name_numerology") == "name_missing"
    assert SLOT_IDENTITY in cap["profile_slots"]["data_eligible"]
    assert SLOT_IDENTITY in cap["profile_slots"]["revealed"]
    assert SLOT_NATAL_STRUCTURE not in cap["profile_slots"]["data_eligible"]
    assert SLOT_NAME_NUMEROLOGY not in cap["profile_slots"]["data_eligible"]
    assert SLOT_HELPS in cap["profile_slots"]["data_eligible"]
    assert SLOT_HELPS in cap["profile_slots"]["access_gated"]
    assert SLOT_HELPS not in cap["profile_slots"]["allowed"]


def test_state_date_plus_name():
    cap = resolve_capability(
        birth_date=date(1990, 5, 15),
        display_name="Anna",
        access="free",
    )
    assert cap["mode"] == "date_only"
    assert cap["has_name"] is True
    assert SLOT_NAME_NUMEROLOGY in cap["profile_slots"]["data_eligible"]
    assert SLOT_NAME_NUMEROLOGY in cap["profile_slots"]["revealed"]
    assert _reason_for(cap["unavailable_facts"], "name_numerology") is None
    assert _reason_for(cap["unavailable_facts"], "ascendant") == "birth_time_missing"


def test_state_full_time_and_place():
    cap = resolve_capability(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        time_unknown=False,
        latitude=55.75,
        longitude=37.62,
        location_name="Moscow",
        timezone_name="Europe/Moscow",
        display_name="Anna",
        access="free",
    )
    assert cap["mode"] == "full"
    assert cap["layers"]["l2_structure"] is True
    assert SLOT_NATAL_STRUCTURE in cap["profile_slots"]["data_eligible"]
    assert SLOT_NAME_NUMEROLOGY in cap["profile_slots"]["data_eligible"]
    assert not any(u["key"] == "ascendant" for u in cap["unavailable_facts"])
    assert SLOT_HELPS in cap["profile_slots"]["data_eligible"]
    assert SLOT_HELPS not in cap["profile_slots"]["revealed"]
    assert cap["layers"]["l3_in_result"] is True
    assert cap["layers"]["l3_revealed"] is False


def test_free_vs_trial_l3_disclosure_same_data_eligible():
    base = dict(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        time_unknown=False,
        latitude=55.75,
        longitude=37.62,
    )
    free = resolve_capability(**base, access="free")
    trial = resolve_capability(**base, access="trial")
    paid = resolve_capability(**base, access="paid")
    assert free["profile_slots"]["data_eligible"] == trial["profile_slots"]["data_eligible"]
    assert SLOT_HELPS in free["profile_slots"]["data_eligible"]
    assert SLOT_HELPS in free["profile_slots"]["access_gated"]
    assert SLOT_HELPS not in free["profile_slots"]["revealed"]
    assert SLOT_HELPS in trial["profile_slots"]["revealed"]
    assert SLOT_HELPS in paid["profile_slots"]["revealed"]
    assert free["layers"]["l3_in_result"] is True
    assert free["layers"]["l3_revealed"] is False
    assert trial["layers"]["l3_revealed"] is True
    assert paid["layers"]["l3_revealed"] is True


def test_build_available_input_embeds_capability_and_precise_reason():
    available = build_available_input(
        birth_date=date(1990, 5, 15),
        birth_time=time(10, 0),
        time_unknown=False,
        access="free",
    )
    assert available["mode"] == "date_only"
    assert available["_capability"]["mode"] == "date_only"
    assert _reason_for(available["_capability"]["unavailable_facts"], "ascendant") == "birth_place_missing"


def test_generate_natal_facts_merges_capability_without_llm(monkeypatch):
    monkeypatch.setattr(
        "todayflow_backend.services.natal_facts_contract_v1.is_llm_chat_configured",
        lambda: False,
    )
    available = build_available_input(
        birth_date=date(1990, 5, 15),
        time_unknown=True,
        access="free",
    )
    cap = available.pop("_capability")
    facts = generate_natal_facts(available_input=available, capability=cap)
    assert facts["mode"] == "date_only"
    assert facts["planets"][0]["id"] == "sun"
    assert facts["capability"]["mode"] == "date_only"
    assert _reason_for(facts["unavailable_facts"], "ascendant") == "birth_time_missing"


def test_validate_strips_angles_with_precise_reason():
    raw = {
        "planets": [{"id": "sun", "sign": "taurus"}],
        "angles": {"ascendant": {"sign": "virgo", "degree": 10}},
        "houses": [{"house": 1, "sign": "virgo"}],
    }
    facts = validate_natal_facts(
        raw,
        expected_mode="date_only",
        structure_unavailable_reason="birth_place_missing",
    )
    assert facts["angles"]["ascendant"] is None
    assert _reason_for(facts["unavailable_facts"], "ascendant") == "birth_place_missing"


def test_adapter_keeps_helps_in_slots_gates_reveal_on_free():
    contract = {
        "recognition_line": "Вы опираетесь на устойчивость и ясность.",
        "helps": ["Держите утренний ритуал", "Закрывайте один контур в день"],
        "strengths": ["Выдержка"],
    }
    facts = date_only_fallback(date(1990, 5, 15), structure_unavailable_reason="birth_time_missing")
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
    facts = {
        "mode": "date_only",
        "planets": [{"id": "sun", "sign": "taurus"}],
        "angles": {},
        "houses": [],
        "unavailable_facts": [{"key": "ascendant", "reason": "birth_time_missing"}],
    }
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
