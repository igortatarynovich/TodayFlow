"""Tests for day_story_v1 — single canonical Today narrative artifact."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from todayflow_backend.services.day_story_v1 import (
    DAY_STORY_V1_CONTRACT,
    build_day_story_fallback_v1,
    day_story_to_legacy_narrative,
    day_story_to_today_contract_v1,
    validate_day_story_v1,
)


def _sample_story() -> dict:
    return {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": "Один ясный шаг вместо распыления",
        "direction": "Сегодня лучше держать один вектор и не брать лишние обещания.",
        "story": (
            "День просит последовательности: стержень дня поддерживает один приоритет. "
            "Карта и число подсказывают не форсировать темп. "
            "Если замечаешь импульс взять вторую задачу — это сигнал замедлиться."
        ),
        "do": [
            "Выбери одну задачу и доведи до видимого результата",
            "Скажи прямо одну вещь в разговоре",
            "Сделай короткую паузу после главного шага",
        ],
        "avoid": [
            "Не подписывайся на новые обязательства из импульса",
            "Не распыляйся на второй приоритет",
            "Не форсируй темп из тревоги",
        ],
        "advantage": "Один приоритет до обеда даёт ясность.",
        "abstain": "Сегодня не стоит брать второй фронт без времени.",
        "today_move": "Выбери одну задачу и доведи её до видимого результата до вечера.",
        "global_period": "День последовательных действий, не резких поворотов.",
        "development_point": "Замечать, когда тревога подталкивает ускориться без причины.",
        "primary_action": "Выбери одну задачу и доведи её до видимого результата до вечера.",
        "domains": {
            "relationships": {
                "status": "Сегодня в отношениях важнее честный контакт.",
                "opportunity": "Прямой разговор снижает угадывание.",
                "risk": "Молчание может нарастить дистанцию.",
                "action": "Скажи прямо одну вещь, которую обычно обходишь.",
            },
            "money_work": {
                "status": "Сегодня в работе важен один вектор.",
                "opportunity": "Один приоритет до обеда даёт ясность.",
                "risk": "Импульсные решения могут размыть фокус.",
                "action": "Доведи одну задачу до видимого результата.",
            },
            "family": {
                "status": "Сегодня дома полезнее спокойный ритм.",
                "opportunity": "Тёплое присутствие важнее скорости.",
                "risk": "Контроль может нагреть атмосферу.",
                "action": "Сделай один бытовой шаг для спокойствия дома.",
            },
        },
        "talisman": {"color": "лазурь", "stone": "сапфир", "note": "Носи как якорь спокойного темпа."},
        "practice_recommendation": {"kind": "none", "text": "", "reason": ""},
        "evening_closure": "Коротко отметь, что получилось — без самооценки.",
        "symbolic_note": "",
    }


def test_validate_day_story_v1_green_on_sample():
    assert validate_day_story_v1(_sample_story()) == []


def test_build_day_story_fallback_v1_has_required_fields():
    brief = {
        "anchor_summary": "Сегодня — один приоритет.",
        "do_hint": "Сделай один шаг.",
        "avoid_hint": "Не распыляйся.",
        "tempo_hint": "Держи ровный темп.",
    }
    story = build_day_story_fallback_v1(day_engine_brief=brief, color="синий", stone="сапфир")
    assert story["contract_version"] == DAY_STORY_V1_CONTRACT
    assert validate_day_story_v1(story) == []


def test_day_story_to_today_contract_v1_validates():
    contract = day_story_to_today_contract_v1(_sample_story(), generation_id="42", progress={})
    assert contract["contract_version"] == "today_contract_v1"
    assert contract["generation_id"] == "42"
    assert contract["global_context"]["period"]
    assert contract["domains"]["family"]["action"]


def test_day_story_to_legacy_narrative_derives_surfaces():
    narrative = day_story_to_legacy_narrative(_sample_story(), generation_id="42")
    assert narrative["guide"]["payload"]["headline"] == _sample_story()["theme"]
    assert narrative["spheres"]["payload"]["page_intro"] == _sample_story()["story"]
    assert narrative["day_layer"]["payload"]["nudge_message"] == _sample_story()["today_move"]
    assert narrative["evening"]["payload"]["panel_intro"]


def test_build_day_story_v1_wire_uses_fallback_without_llm():
    from datetime import date

    from todayflow_backend.services.day_story_wire_v1 import build_day_story_v1_wire

    user = MagicMock()
    user.id = 1
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value = []

    morning = MagicMock()
    morning.tarot_card = {"id": 1, "name": "Маг"}
    morning.numerology_number = {"value": 3}
    morning.daily_recommendations = {}

    with patch(
        "todayflow_backend.services.day_story_wire_v1._load_foundation_from_logs",
        return_value={"spine": {"axis": "Один вектор"}},
    ), patch(
        "todayflow_backend.services.day_story_wire_v1._latest_snapshot_id",
        return_value=None,
    ), patch(
        "todayflow_backend.services.day_story_wire_v1.build_meaning_surface_patterns_v0",
        return_value={"total_events": 0},
    ), patch(
        "todayflow_backend.services.day_story_wire_v1.get_insight_depth_tier",
        return_value="free",
    ), patch(
        "todayflow_backend.services.day_story_wire_v1.call_day_story_llm_v1",
        return_value=None,
    ), patch(
        "todayflow_backend.services.day_story_wire_v1.get_learning_service"
    ) as mock_learning:
        svc = MagicMock()
        mock_learning.return_value = svc
        pv = MagicMock()
        pv.id = 7
        svc.get_or_create_prompt_version.return_value = pv
        gen = MagicMock()
        gen.id = 99
        svc.log_generation.return_value = gen

        contract, narrative, gen_id = build_day_story_v1_wire(
            db,
            user=user,
            target_date=date(2026, 6, 22),
            locale="ru",
            morning=morning,
            fusion_dump={"scores": {}, "rhythm_context": {}},
            core_profile={},
        )

    assert gen_id == 99
    assert contract["contract_version"] == "today_contract_v1"
    assert contract["primary_action"]
    assert narrative["guide"]["payload"]["day_story_source"] == DAY_STORY_V1_CONTRACT
