"""person_meaning_from_core_v0 — CE/contract over life_areas."""

from __future__ import annotations

from todayflow_backend.services.person_meaning_from_core_v0 import (
    identity_excerpt_from_core,
    person_sot_label,
    sphere_excerpt_from_core,
    strengths_from_core,
    watchouts_from_core,
)


def test_person_sot_prefers_ready_character_engine():
    core = {
        "character_engine_v1": {"status": "ready"},
        "profile_contract_v1": {"identity_core": "x"},
    }
    assert person_sot_label(core) == "character_engine_v1"


def test_identity_prefers_contract_over_interpretation():
    core = {
        "profile_contract_v1": {"identity_core": "Контрактное ядро личности."},
        "interpretation": {"identity": "Старое interpretation identity."},
    }
    assert identity_excerpt_from_core(core) == "Контрактное ядро личности."


def test_sphere_prefers_life_spheres_then_style_then_life_areas():
    core = {
        "profile_contract_v1": {
            "relationship_style": "Style fallback.",
            "life_spheres": {"love": {"how": "Сфера love how из контракта."}},
        },
        "interpretation": {"life_areas": {"love": "Legacy life_areas love."}},
    }
    assert "Сфера love" in (sphere_excerpt_from_core(core, "love") or "")

    core_style_only = {
        "profile_contract_v1": {"money_style": "Деньги через контракт."},
        "interpretation": {"life_areas": {"money": "Legacy money."}},
    }
    assert sphere_excerpt_from_core(core_style_only, "money") == "Деньги через контракт."

    core_legacy = {
        "interpretation": {"life_areas": {"family": "Дом как опора."}},
    }
    assert sphere_excerpt_from_core(core_legacy, "family") == "Дом как опора."


def test_strengths_and_watchouts_prefer_contract():
    core = {
        "profile_contract_v1": {
            "strengths": ["ясность"],
            "growth_zones": ["перегруз"],
        },
        "interpretation": {
            "strengths": ["legacy strength"],
            "watchouts": ["legacy watch"],
        },
    }
    assert strengths_from_core(core) == ["ясность"]
    assert watchouts_from_core(core) == ["перегруз"]
