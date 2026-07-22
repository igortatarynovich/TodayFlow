"""Delta #3: insight node projection from existing Snapshot materials (no second schema)."""

from __future__ import annotations

from todayflow_backend.services.profile_insight_nodes_projection_v0 import (
    PROJECTION_VERSION,
    attach_insight_nodes_v0,
    project_insight_nodes_v0,
)
from todayflow_backend.services.profile_portrait_why_projection_v0 import project_portrait_why_v0


def _why_case_a():
    return project_portrait_why_v0(
        numerology={"life_path": 1},
        baseline={"archetype_seed": "Architect", "rhythm_style": "Быстрый старт без перегрева"},
        astro={"sun_sign": "Aries", "sun_element": "fire", "time_unknown": True},
        natal_summary={"available": False},
    )


def test_case_a_tension_node_without_living_slot() -> None:
    why = _why_case_a()
    out = project_insight_nodes_v0(
        contract={
            "growth_zones": [
                "Ты легко открываешь новый контур, но устойчивость появляется только после закрепления."
            ],
            "strengths": ["Один завершённый контур важнее трёх новых начал."],
            "recurring_patterns": [],
            "helps": [],
        },
        portrait_why=why,
        living=None,
    )
    assert out["projection_version"] == PROJECTION_VERSION
    assert out["rules"]["not_a_second_patterns_schema"] is True
    assert len(out["nodes"]) == 1
    node = out["nodes"][0]
    assert node["kind"] == "tension"
    assert node["title"] == "Главное напряжение"
    assert "living_evidence" not in node
    assert node["help"]
    assert any(g.get("id") == "sun" for g in node["grounded_on"])
    assert "profile_contract_v1.growth_zones" in node["source_fields"]


def test_case_c_repeat_node_reuses_patterns_helps_and_signal_notes() -> None:
    why = project_portrait_why_v0(
        numerology={"life_path": 4},
        baseline={"archetype_seed": "Sage", "rhythm_style": "Опора на проверенное, без лишних рывков"},
        astro={"sun_sign": "Taurus", "sun_element": "earth", "time_unknown": True},
        natal_summary={"available": False},
    )
    out = project_insight_nodes_v0(
        contract={
            "recurring_patterns": [
                "Ты откладываешь сложный разговор, пока усталость не делает его ещё тяжелее."
            ],
            "helps": [
                "Назвать тему разговора одним предложением до того, как накопится вечерняя усталость."
            ],
            "growth_zones": ["Что-то другое не должно стать узлом при наличии patterns"],
            "strengths": ["Порядок"],
        },
        portrait_why=why,
        living={
            "signals": [
                {"day": "2026-07-14", "note": "не стала писать коллеге"},
                {"day": "2026-07-16", "note": "Разговор с партнёром перенесла"},
            ]
        },
    )
    assert len(out["nodes"]) == 1
    node = out["nodes"][0]
    assert node["kind"] == "repeat"
    assert node["title"] == "Самая большая ловушка"
    assert node["insight"].startswith("Ты откладываешь")
    assert node["help"].startswith("Назвать тему")
    assert node["living_evidence"] == [
        "«не стала писать коллеге»",
        "«Разговор с партнёром перенесла»",
    ]
    assert "profile_contract_v1.recurring_patterns" in node["source_fields"]
    assert "living.signals.note" in node["source_fields"]


def test_empty_contract_yields_no_nodes() -> None:
    out = project_insight_nodes_v0(contract={"recurring_patterns": [], "growth_zones": []}, living=None)
    assert out["nodes"] == []


def test_attach_after_why() -> None:
    payload = {
        "profile_contract_v1": {
            "growth_zones": ["Напряжение достаточно длинное для узла портрета."],
            "strengths": ["Опора достаточно длинная для помощи в узле."],
            "recurring_patterns": [],
            "helps": [],
        },
        "living": None,
        "astro": {"sun_sign": "Aries", "sun_element": "fire", "time_unknown": True},
        "numerology": {"life_path": 1},
        "baseline": {"archetype_seed": "Architect", "rhythm_style": "Быстрый старт без перегрева"},
        "portrait_why_v0": _why_case_a(),
    }
    out = attach_insight_nodes_v0(payload)
    assert out["insight_nodes_v0"]["nodes"][0]["kind"] == "tension"
