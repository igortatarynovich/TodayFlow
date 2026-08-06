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
    h1 = (houses.get("1") or {}).get("how") or (houses.get("1") or {}).get("line") or ""
    assert "1" in houses and h1
    assert "темп" in h1.lower() or "дистанц" in h1.lower() or "контакт" in h1.lower()
    assert houses["1"].get("line") == houses["1"].get("how")
    assert not (houses["1"].get("do") or "").strip()
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
    assert node["kind"] == "tension"
    assert node["title"] == "Главное напряжение"
    assert "living_evidence" not in node
    assert "сегодня" not in (node.get("help") or "").lower()
    assert out["insight_nodes_v0"]["rules"]["forbids_living_day_rhythm_as_identity_trap"] is True
    assert out["insight_nodes_v0"]["rules"]["titles_follow_forms_case_a_c"] is True


def test_consumption_preserves_living_as_repeat_node(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    payload = _payload()
    payload["living"] = {
        "signals": [
            {"note": "Не стала писать коллеге"},
            {"note": "Разговор с партнёром перенесла"},
        ]
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    node = out["insight_nodes_v0"]["nodes"][0]
    assert node["kind"] == "repeat"
    assert node["title"] == "Самая большая ловушка"
    assert node.get("living_evidence")
    assert any("коллеге" in q for q in node["living_evidence"])
    assert "сегодня" not in (node.get("help") or "").lower()


def test_consumption_skips_when_not_grounded(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    out = apply_character_engine_profile_consumption_v0(_payload(grounded=False))
    assert out["character_engine_consumption_v0"]["applied"] is False
    assert out["profile_contract_v1"]["identity_core"].startswith("Старый")
    assert "Ритм дня" in out["insight_nodes_v0"]["nodes"][0]["insight"]


def test_consumption_does_not_stamp_aspect_gists(monkeypatch) -> None:
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
                "gist": "Энциклопедия аспекта — natal SoT.",
            }
        ],
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    gist = out["natal_summary"]["notable_aspects"][0]["gist"]
    # CE must not overwrite every aspect with the same mechanism template.
    assert gist == "Энциклопедия аспекта — natal SoT."
    aspects = (out.get("character_engine_aspect_lines_v0") or {}).get("aspects") or {}
    assert aspects == {}
    houses = (out.get("character_engine_house_lines_v0") or {}).get("houses") or {}
    assert set(houses) == {str(i) for i in range(1, 13)}
    assert not any("не энциклопедия" in (h.get("line") or h.get("how") or "").lower() for h in houses.values())
    for h in houses.values():
        assert h.get("how") or h.get("line")
        assert not (h.get("do") or "").strip()
        assert "здесь это звучит" not in (h.get("how") or "").lower()
        assert "темп зоны" not in (h.get("how") or "").lower()


def test_consumption_applied_asc_and_occupied_house(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    payload = _payload()
    # Cancer ASC + cusp facts + Sun in 8th (occupied non-angular).
    stage2 = payload["diagnostics"]["character_engine_stage2"]
    stage2["stage0"]["raw_facts"].extend(
        [
            {
                "fact_id": "f_asc",
                "fact_type": "angle_sign:ascendant",
                "value": {"sign": "Cancer"},
            },
            {
                "fact_id": "f_mc",
                "fact_type": "angle_sign:mc",
                "value": {"sign": "Pisces"},
            },
            {
                "fact_id": "f_h1",
                "fact_type": "house_cusp_sign:1",
                "value": {"sign": "Cancer"},
            },
            {
                "fact_id": "f_h8",
                "fact_type": "house_cusp_sign:8",
                "value": {"sign": "Aquarius"},
            },
        ]
    )
    payload["natal_summary"] = {
        "available": True,
        "angles": {"ascendant_sign": "Cancer", "midheaven_sign": "Pisces"},
        "luminaries": [{"name": "Sun", "sign": "Aquarius", "house": 8, "gist": "x"}],
        "personal_planets": [],
        "notable_aspects": [],
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    asc = (out.get("character_engine_asc_v0") or {}).get("asc") or {}
    assert asc.get("sign") == "cancer"
    assert asc.get("how") and asc.get("do")
    assert "своих" in asc["how"].lower() or "открыт" in asc["how"].lower() or "контакт" in asc["how"].lower()
    assert "не энциклопедия" not in asc["how"].lower()
    mc = (out.get("character_engine_asc_v0") or {}).get("mc") or {}
    assert mc.get("sign") == "pisces" and mc.get("do")

    houses = (out.get("character_engine_house_lines_v0") or {}).get("houses") or {}
    assert set(houses) == {str(i) for i in range(1, 13)}
    assert "1" in houses and houses["1"].get("how")
    # Cancer cusp on 1 → recognition about «своих» / open carefully.
    assert "своих" in (houses["1"].get("how") or "").lower() or "открыва" in (houses["1"].get("how") or "").lower()
    assert "8" in houses  # Aquarius cusp — method/distance in vulnerability
    assert "метод" in (houses["8"].get("how") or "").lower() or "дистанц" in (houses["8"].get("how") or "").lower()
    assert "солнце" not in (houses["8"].get("how") or "").lower()  # no planet-label dump
    assert houses["2"].get("how")
    assert houses["11"].get("how")
    assert not (houses["2"].get("do") or "").strip()
    # No mechanism stamp spam across every house.
    hows = [(h.get("how") or "") for h in houses.values()]
    assert sum("через автономию и собственную систему" in h.lower() for h in hows) <= 1
    assert all("здесь это звучит" not in h.lower() for h in hows)