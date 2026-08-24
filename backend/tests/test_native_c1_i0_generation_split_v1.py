"""1.3.116 Native C1 I0 generation split — Global then Personal overlay."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_LLM_SCHEMA_VERSION,
    NATIVE_PROMPT_VERSION,
    normalize_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
)
from todayflow_backend.services.native_c1_i0_generation_split_v1 import (
    GLOBAL_STAGE_INSTRUCTION_RU,
    PERSONAL_SCHEMA_VERSION,
    PERSONAL_STAGE_INSTRUCTION_RU,
    detect_global_mutation,
    enforce_global_only,
    format_personal_user_message,
    generation_stages,
    global_locked_snapshot,
    merge_personal_overlay,
    normalize_personal_overlay,
    orchestrate_i0_split_generation,
    should_run_personal_stage,
)

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "docs" / "today" / "NATIVE_C1_I0_GENERATION_SPLIT_V1.md"
PIPELINE = ROOT / "docs" / "today" / "TODAY_CONTENT_PIPELINE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
MODULE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "native_c1_i0_generation_split_v1.py"
NATIVE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "day_scenario_native_llm_c1.py"


def _global_native() -> dict[str, Any]:
    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "personalization_depth": DEPTH_GENERAL,
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": "Луна в Рыбах",
                    "human_meaning": "Эмоции сильнее логики.",
                    "link_to_conflict": "Среда мягче, чем хочется назвать точно.",
                    "evidence_refs": ["moon-pisces"],
                }
            ],
            "day_card": {
                "named_factor": "Отшельник",
                "archetype_role": "пауза",
                "link_to_conflict": "Сначала понять, потом говорить.",
                "evidence_refs": ["day_card"],
            },
            "day_number": {
                "named_factor": "7",
                "tempo": "медленно",
                "style": "вглубь",
                "link_to_conflict": "Ритм без спешки.",
                "evidence_refs": ["day_number"],
            },
            "natal": [],
        },
        "conflict": {
            "title": "Прояснение против сглаживания",
            "thesis": "Назвать точно важнее тишины.",
            "force_a": "сгладить",
            "force_b": "сказать честно",
            "why_today": "Луна в Рыбах собирает тон дня.",
            "why_personal": "",
            "driver_refs": ["moon-pisces"],
            "evidence_refs": ["moon-pisces"],
        },
        "primary_scene_id": "scene.relationships",
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "sphere": "relationships",
                "role_in_story": "primary",
                "setup": "Близкий спрашивает, всё ли нормально.",
                "why_sphere": "Отношения сегодня чувствительнее.",
                "opportunity": "Одно короткое сообщение.",
                "trap": "Согласиться ради тишины.",
                "recommended_action": "Написать черновик.",
                "avoid_action": "Не сглаживать смысл.",
                "everyday_example": "Ответ в чате после паузы.",
                "evidence_refs": ["moon-pisces"],
                "chorus_refs": ["conflict"],
            },
            {
                "scene_id": "scene.work_decisions",
                "sphere": "work_decisions",
                "role_in_story": "support",
                "setup": "Письмо ждёт ясного ответа.",
                "why_sphere": "Работа просит формулировки.",
                "opportunity": "Один абзац с запросом.",
                "trap": "Отложить ответ.",
                "recommended_action": "Отправить черновик.",
                "avoid_action": "Не размывать.",
                "everyday_example": "Письмо коллеге.",
                "evidence_refs": ["moon-pisces"],
                "chorus_refs": ["conflict"],
            },
        ],
        "prop_material": {"color_scene_candidates": ["scene.relationships"]},
    }


def _personal_overlay() -> dict[str, Any]:
    return {
        "schema_version": PERSONAL_SCHEMA_VERSION,
        "personalization_depth": DEPTH_DEEP,
        "personalization": {"depth": DEPTH_DEEP, "pack_confidence": 0.8},
        "interpretive_chorus": {
            "natal": [
                {
                    "named_factor": "Личная активация",
                    "human_meaning": "Реакция может быть сильнее.",
                    "link_to_conflict": "Сглаживание особенно привычно.",
                    "evidence_refs": ["natal"],
                }
            ]
        },
        "conflict": {
            "why_personal": "Тебе сглаживание обычно ближе.",
            "personalization": {
                "personalization_level": DEPTH_DEEP,
                "personalization_reason": "baseline из pack",
                "habitual_force": "a",
                "required_movement": "b",
            },
        },
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "personalization": {
                    "personalization_level": DEPTH_DEEP,
                    "sphere_reason": "pack ranked relationships",
                },
            }
        ],
    }


def test_native_c1_i0_generation_split_v1():
    assert CANON.is_file()
    assert "1.3.116" in CANON.read_text(encoding="utf-8")
    assert "c5.1" in NATIVE.read_text(encoding="utf-8")
    assert "6.70" in IL.read_text(encoding="utf-8")
    assert "KC-C-I0-SPLIT" in INVENTORY.read_text(encoding="utf-8")
    assert "1.3.116" in HANDOFF.read_text(encoding="utf-8")
    assert "1.3.116" in TRACKER.read_text(encoding="utf-8")
    assert MODULE.is_file()

    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.2"
    assert GLOBAL_STAGE_INSTRUCTION_RU
    assert PERSONAL_STAGE_INSTRUCTION_RU

    assert generation_stages({"evidence_depth": DEPTH_GENERAL}) == ["global"]
    assert generation_stages({"evidence_depth": DEPTH_LIGHT}) == ["global", "personal"]
    assert generation_stages({"evidence_depth": DEPTH_DEEP}) == ["global", "personal"]
    assert not should_run_personal_stage({"evidence_depth": DEPTH_GENERAL})
    assert should_run_personal_stage({"evidence_depth": DEPTH_DEEP})

    global_norm = normalize_native_scenario_llm_c1(_global_native())
    stripped = enforce_global_only(global_norm)
    assert stripped["interpretive_chorus"]["natal"] == []
    assert not str(stripped["conflict"].get("why_personal") or "").strip()
    assert stripped["personalization_depth"] == DEPTH_GENERAL

    locked = global_locked_snapshot(stripped)
    assert locked["interpretive_chorus"]["natal"] == []
    assert "GLOBAL_LOCKED" in format_personal_user_message(locked, personalization_evidence={"evidence_depth": DEPTH_DEEP})

    overlay = normalize_personal_overlay(_personal_overlay())
    merged = merge_personal_overlay(stripped, overlay)
    assert merged["conflict"]["title"] == stripped["conflict"]["title"]
    assert merged["conflict"]["why_today"] == stripped["conflict"]["why_today"]
    assert len(merged["interpretive_chorus"]["natal"]) == 1
    assert merged["conflict"]["why_personal"]
    assert merged["personalization_depth"] == DEPTH_DEEP
    assert merged["scenes"][0]["setup"] == stripped["scenes"][0]["setup"]

    mutated = json.loads(json.dumps(_global_native()))
    mutated["conflict"]["title"] = "Другой сюжет"
    drift = detect_global_mutation(stripped, mutated)
    assert any("global_mutation:conflict.title" in e for e in drift)

    calls: list[str] = []

    def fake_llm(**kwargs: Any) -> tuple[str | None, str | None, str | None]:
        stage = "global" if GLOBAL_STAGE_INSTRUCTION_RU in kwargs.get("system", "") else "personal"
        calls.append(stage)
        if stage == "global":
            return json.dumps(_global_native(), ensure_ascii=False), None, "test-model"
        return json.dumps(_personal_overlay(), ensure_ascii=False), None, "test-model"

    def accept_global(parsed: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
        norm = normalize_native_scenario_llm_c1(parsed)
        return enforce_global_only(norm), None

    meta: dict[str, Any] = {}
    merged_only, attempts, split_meta = orchestrate_i0_split_generation(
        global_system=GLOBAL_STAGE_INSTRUCTION_RU,
        personal_system=PERSONAL_STAGE_INSTRUCTION_RU,
        user_base="DRAMATURGY",
        pers_pack={"evidence_depth": DEPTH_GENERAL},
        il4_pack=None,
        allowed_evidence_ids=set(),
        max_attempts=2,
        llm_call=lambda **kw: fake_llm(**kw),
        resolve_attempt_model=lambda i: "test-model",
        process_global_normalized=accept_global,
        meta_out=meta,
    )
    assert calls == ["global"]
    assert split_meta["personal_skipped"]
    assert merged_only is not None
    assert merged_only["interpretive_chorus"]["natal"] == []

    calls.clear()
    merged_deep, attempts_deep, split_deep = orchestrate_i0_split_generation(
        global_system=GLOBAL_STAGE_INSTRUCTION_RU,
        personal_system=PERSONAL_STAGE_INSTRUCTION_RU,
        user_base="DRAMATURGY",
        pers_pack={"evidence_depth": DEPTH_DEEP},
        il4_pack=None,
        allowed_evidence_ids=set(),
        max_attempts=2,
        llm_call=lambda **kw: fake_llm(**kw),
        resolve_attempt_model=lambda i: "test-model",
        process_global_normalized=accept_global,
        meta_out=None,
    )
    assert calls == ["global", "personal"]
    assert not split_deep["personal_skipped"]
    assert merged_deep is not None
    assert merged_deep["interpretive_chorus"]["natal"]
    assert merged_deep["conflict"]["title"] == "Прояснение против сглаживания"


def test_call_native_uses_i0_split_orchestrator():
    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=object(),
        ),
        patch(
            "todayflow_backend.services.native_c1_i0_generation_split_v1.orchestrate_i0_split_generation",
        ) as orch,
        patch(
            "todayflow_backend.services.day_story_capture_session_v0.get_day_story_capture_session",
            return_value=None,
        ),
    ):
        from todayflow_backend.services.day_scenario_native_llm_c1 import call_day_scenario_native_llm_c1

        global_norm = enforce_global_only(normalize_native_scenario_llm_c1(_global_native()))
        orch.return_value = (
            global_norm,
            [{"stage": "global", "status": "accepted_global"}],
            {
                "i0_split": True,
                "stages_run": ["global"],
                "personal_skipped": True,
                "personal_degraded": False,
            },
        )

        result = call_day_scenario_native_llm_c1(
            {
                "interpretation": {
                    "day_thesis": {
                        "family": "momentum",
                        "variant": "steady",
                        "mode": "stability",
                        "label_ru": "Ось",
                        "driver_ids": ["moon-pisces"],
                    },
                    "day_events_pack": {"ranked_drivers": [{"id": "moon-pisces"}]},
                }
            },
            interpretation={
                "day_thesis": {
                    "family": "momentum",
                    "variant": "steady",
                    "mode": "stability",
                    "label_ru": "Ось",
                    "driver_ids": ["moon-pisces"],
                },
                "day_events_pack": {"ranked_drivers": [{"id": "moon-pisces"}]},
            },
            ritual_context={"tarot_name_ru": "Отшельник", "numerology_value": 7},
            max_attempts=1,
        )
        assert orch.called
        assert result is not None
        assert result.get("generation_source") == "native_llm_c1"
        assert result["editorial_meta"]["prompt_version"] == "day-scenario-native-c5.2"
        assert result["editorial_meta"]["i0_split"]["i0_split"]
