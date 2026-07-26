"""CE → Profile consumption slice — Identity Core owns recognition / why / trap."""

from __future__ import annotations

from todayflow_backend.services.character_engine_profile_consumption_v0 import (
    apply_character_engine_profile_consumption_v0,
)


def _payload(*, grounded: bool = True) -> dict:
    surface = (
        "Ты строишь жизнь через собственную систему и дистанцию — "
        "ясность важнее чужого темпа."
    )
    return {
        "profile_contract_v1": {
            "contract_version": "v1",
            "identity_core": "Старый портрет из funnel.",
            "recognition_line": "Мудрец — старый ярлык.",
            "strengths": [],
            "growth_zones": [],
            "relationship_style": "",
            "money_style": "",
            "decision_style": "",
            "recurring_patterns": ["Ритм дня живет неровно — старая ловушка living."],
        },
        "portrait_why_v0": {
            "selected_by": [{"label": "Архетип Мудрец по числу пути"}],
            "portrait_influenced_by": [],
        },
        "insight_nodes_v0": {
            "nodes": [
                {
                    "id": "old",
                    "kind": "tension",
                    "title": "Самая большая ловушка",
                    "insight": "Ритм дня живет неровно.",
                }
            ]
        },
        "diagnostics": {
            "character_engine_stage2": {
                "stage0": {
                    "raw_facts": [
                        {
                            "fact_id": "f_sun",
                            "fact_type": "planet_sign:sun",
                            "value": {"sign": "Aquarius"},
                        },
                        {
                            "fact_id": "f_lp",
                            "fact_type": "life_path",
                            "value": 7,
                        },
                    ]
                },
                "stage1": {
                    "claims": [
                        {
                            "claim_id": "c_autonomy",
                            "thesis_key": "autonomy_high",
                            "supporting_fact_ids": ["f_sun"],
                        },
                        {
                            "claim_id": "c_air",
                            "thesis_key": "direction_through_air_mind",
                            "supporting_fact_ids": ["f_sun"],
                        },
                    ]
                },
                "stage2": {
                    "status": "grounded" if grounded else "insufficient_identity_core",
                    "identity_core": {
                        "primary_claim_id": "c_autonomy",
                        "thesis_key": "builds_through_autonomy",
                        "surface_text": surface,
                    },
                },
            }
        },
    }


def test_consumption_off_is_noop(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": False})(),
    )
    before = _payload()
    out = apply_character_engine_profile_consumption_v0(before)
    assert out["profile_contract_v1"]["identity_core"].startswith("Старый")
    assert "character_engine_consumption_v0" not in out


def test_consumption_overwrites_recognition_why_trap(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    out = apply_character_engine_profile_consumption_v0(_payload())
    meta = out["character_engine_consumption_v0"]
    assert meta["applied"] is True
    assert meta["recognition_label"] == "Автономия"
    assert meta["identity_thesis"] == "builds_through_autonomy"

    contract = out["profile_contract_v1"]
    assert "собственную систему" in contract["identity_core"]
    assert "Мудрец" not in (contract.get("recognition_line") or "")
    trap = contract["recurring_patterns"][0]
    assert "дистанцию" in trap or "анализ" in trap or "контроль" in trap
    assert "Ритм дня" not in trap
    assert "неровно" not in trap
    assert contract["living_changes"] is None
    assert any(
        "систем" in s.lower() or "дистанц" in s.lower() or "независимо" in s.lower()
        for s in contract["strengths"]
    )
    assert "Вы " not in contract["decision_style"]
    assert "ты " in contract["decision_style"].lower() or contract["decision_style"].startswith("Ты ")
    assert "Вы " not in contract["relationship_style"]
    help_line = out["insight_nodes_v0"]["nodes"][0].get("help")
    assert help_line
    spheres = contract.get("life_spheres") or {}
    assert "love" in spheres and "how" in spheres["love"]
    assert "Вы " not in spheres["love"]["how"]
    houses = (out.get("character_engine_house_lines_v0") or {}).get("houses") or {}
    assert "1" in houses and "автоном" in houses["1"]["line"].lower()
    assert "Вы " not in (contract.get("emotional_style") or "")
    assert "ты " in (contract.get("emotional_style") or "").lower() or (contract.get("emotional_style") or "").startswith(
        "Эмоции ты"
    )
    assert contract.get("work_and_realization")
    assert contract.get("home_and_security")

    why = out["portrait_why_v0"]
    assert why["source"] == "character_engine_stage2"
    assert why["selected_by"]
    assert "Автономия" in why["selected_by"][0]["label"]
    assert "Мудрец" not in str(why)

    node = out["insight_nodes_v0"]["nodes"][0]
    assert "Ритм дня" not in node["insight"]
    assert out["insight_nodes_v0"]["rules"]["forbids_living_day_rhythm_as_identity_trap"] is True


def test_consumption_skips_when_not_grounded(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    out = apply_character_engine_profile_consumption_v0(_payload(grounded=False))
    assert out["character_engine_consumption_v0"]["applied"] is False
    assert out["profile_contract_v1"]["identity_core"].startswith("Старый")
    assert "Ритм дня" in out["insight_nodes_v0"]["nodes"][0]["insight"]


def test_consumption_rewrites_aspect_gists(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    payload = _payload()
    payload["natal_summary"] = {
        "available": True,
        "notable_aspects": [
            {
                "bodies": "Sun · Moon",
                "aspect": "sesquiquadrate",
                "strength": "tight",
                "gist": "Энциклопедия аспекта для вас.",
            }
        ],
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    gist = out["natal_summary"]["notable_aspects"][0]["gist"]
    assert "Вы " not in gist
    assert "автоном" in gist.lower() or "ядро" in gist.lower()
    aspects = (out.get("character_engine_aspect_lines_v0") or {}).get("aspects") or {}
    assert aspects
    assert any("автоном" in (v.get("line") or "").lower() for v in aspects.values())
