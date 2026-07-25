"""Tests for day product logic capture session (no LLM required)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from todayflow_backend.services.day_story_capture_session_v0 import (
    CAPTURE_CONTRACT,
    day_story_capture_enabled,
    day_story_capture_session,
    get_day_story_capture_session,
)
from todayflow_backend.services.day_story_interpretation_v1 import build_day_story_interpretation_v1
from todayflow_backend.services.day_story_v1 import (
    build_day_story_fallback_v1,
    day_story_to_today_contract_v1,
)


def test_capture_off_by_default():
    assert get_day_story_capture_session() is None
    assert day_story_capture_enabled() is False


def test_capture_pack_records_color_pipeline_and_orphans(tmp_path: Path):
    color_sym = {
        "name": "Лазурь",
        "benefit_ru": "Успокаивает ум и помогает держать ясность.",
        "clothing_ru": "Рубашка.",
        "accessory_ru": "Браслет.",
        "amount_ru": "Один акцент.",
        "avoid_color_ru": "Кислотно-оранжевый",
        "avoid_why_ru": "Разгоняет темп.",
    }
    with day_story_capture_session(
        case_id="unit-1",
        out_dir=tmp_path,
        target_date="2026-07-20",
        user_id="test",
    ) as session:
        assert day_story_capture_enabled()
        session.record_lifecycle(force_rebuild_used=True, get_calls_llm=False)
        session.record_color(color_symbol=color_sym, color_name="Лазурь")
        interp = build_day_story_interpretation_v1(
            day_engine_brief={
                "anchor_summary": "Ось дня.",
                "do_hint": "Шаг.",
                "avoid_hint": "Не спеши.",
            },
            ritual_context={"head_topic": "relationships"},
            color="Лазурь",
            color_symbol=color_sym,
            celestial_events={
                "sky_aspects": [
                    {
                        "id": "sun-square-moon",
                        "title": "Солнце — квадрат — Луна",
                        "story_ru": "Намерение и настроение расходятся.",
                    }
                ],
                "daily_symbols": {"color": color_sym},
            },
            target_date=date(2026, 7, 20),
            birth_date=date(1990, 3, 15),
        )
        session.record_interpretation_snapshot(interp)
        story = build_day_story_fallback_v1(
            day_engine_brief={
                "anchor_summary": "Ось дня.",
                "do_hint": "Сформулируй позицию до ответа.",
                "avoid_hint": "Не соглашайся сразу ради гармонии.",
            },
            color="Лазурь",
            color_symbol=color_sym,
            interpretation=interp,
            target_date=date(2026, 7, 20),
            birth_date=date(1990, 3, 15),
        )
        # Simulate a trap that catalog does not reference
        story["trap"] = "Согласиться слишком быстро, чтобы сохранить мир"
        story["expect"] = "Появится давление ответить сразу"
        story["do"] = ["Сначала сформулировать свою позицию"]
        story["interpretation_status"] = "ok"
        contract = day_story_to_today_contract_v1(story)
        session.record_final(story=story, contract=contract, used_fallback=True)
        path = session.write_pack(stem="unit-1")

    assert path is not None and path.exists()
    pack = path.read_text(encoding="utf-8")
    assert CAPTURE_CONTRACT in pack
    assert "COLOR_PIPELINE" in pack
    assert "SURFACE_ORPHAN" in pack
    assert "date_preset+catalog" in pack
    assert get_day_story_capture_session() is None
