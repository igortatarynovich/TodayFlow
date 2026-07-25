"""Tarot Golden Eval v1 — rubric / shape / report schema tests."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.core import models
from todayflow_backend.services import tarot_golden_eval_v1 as geval
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "backend" / "tests" / "fixtures" / "tarot_golden_dataset_v1.json"
RESULT_SCHEMA = ROOT / "docs" / "schemas" / "tarot_golden_eval_result_v1.schema.json"


def _spread(sc: dict) -> models.TarotSpreadResult:
    cards = []
    for item in sc["cards"]:
        cards.append(
            models.TarotSpreadCard(
                card=models.TarotCard(
                    id=int(item["card_id"]),
                    name=f"Card {item['card_id']}",
                    keywords=[],
                    upright="",
                    reversed="",
                ),
                orientation=str(item.get("orientation") or "upright"),
                position=models.TarotSpreadPosition(
                    id=str(item["position_id"]),
                    title=str(item.get("title") or item["position_id"]),
                    prompt=str(item.get("title") or ""),
                ),
                meaning="",
            )
        )
    return models.TarotSpreadResult(
        spread_id=str(sc["spread_id"]),
        title=str(sc.get("label") or sc["id"]),
        cards=cards,
    )


def test_rubric_heuristic_scores_good_and_bad_answers():
    good = {
        "symbols_overview": "В раскладе напряжение между уходом и почти-полным комфортом.",
        "question_story": "Ты уже внутренне отошёл, но держишься за привычную картину общего дома.",
        "direct_answer": "Сейчас честнее признать дистанцию и проверить её двухнедельным экспериментом, а не требовать гарантий.",
        "next_step": "Запиши три критерия живой близости и обсуди один из них на этой неделе.",
    }
    bad = {
        "symbols_overview": "Аркан Луны. Карта 1 говорит. Карта 2 говорит.",
        "question_story": "Карта 1… Карта 2… Он точно думает о расставании.",
        "direct_answer": "Он точно уйдёт 15 июля.",
        "next_step": "Жди.",
    }
    good_scores = geval.score_rubric_heuristic(good, question="Стоит ли уходить?")
    bad_scores = geval.score_rubric_heuristic(bad, question="Стоит ли уходить?")
    assert geval.rubric_mean(good_scores) is not None
    assert geval.rubric_mean(good_scores) > geval.rubric_mean(bad_scores)
    assert bad_scores["symbolism_natural"] <= 2
    assert bad_scores["no_false_confidence"] <= 2


def test_shape_and_anti_sameness_helpers():
    pack = {
        "cards": [
            {"card_id": 43, "name_ru": "Восьмёрка Кубков", "meaning_range": {"core_scene": "уход от почти-полного"}},
            {"card_id": 44, "name_ru": "Девятка Кубков", "meaning_range": {"core_scene": "личное мне хорошо"}},
            {"card_id": 45, "name_ru": "Десятка Кубков", "meaning_range": {"core_scene": "общий дом семьи"}},
        ]
    }
    interp = {
        "symbols_overview": "Три разные водные истории: уход, сытость, общий дом.",
        "question_story": "Путь остаться сохраняет личный комфорт; путь уйти рискует ради общей радости.",
        "direct_answer": "Сейчас вектор уже направлен прочь от почти-полного, даже если картинка ещё красива.",
        "next_step": "Сделай двухнедельный эксперимент дистанции без объявления разрыва.",
    }
    shape = geval.check_answer_shape(
        flags=["no_arkan_label", "compare_options", "distinct_minors", "direct_answer", "next_step"],
        interpretation=interp,
        pack=pack,
    )
    assert shape["no_arkan_label"] is True
    assert shape["distinct_minors"] is True
    assert shape["direct_answer"] is True
    sim = geval.mean_pairwise_similarity(
        [
            "Один и тот же шаблон ответа про карты.",
            "Один и тот же шаблон ответа про карты снова.",
            "Совершенно другая человеческая история про границы и уход.",
        ]
    )
    assert sim is not None
    gates = geval.summarize_gates(
        shape_results=[shape],
        rubric_means=[4.2],
        anti_sameness_mean=0.2,
        llm_pass=12,
        scenario_count=12,
    )
    assert gates["critical_shape_pass"] is True
    assert gates["freeze_lift_ready"] is True
    gates_low_llm = geval.summarize_gates(
        shape_results=[shape],
        rubric_means=[4.2],
        anti_sameness_mean=0.2,
        llm_pass=7,
        scenario_count=12,
    )
    assert gates_low_llm["freeze_lift_ready"] is False


def test_offline_eval_report_validates_schema_for_all_dataset_scenarios():
    payload = json.loads(DATASET.read_text(encoding="utf-8"))
    schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    scenarios = []
    shape_list = []
    for sc in payload["scenarios"]:
        pack = engine.build_context_pack(
            _spread(sc),
            question=sc["question"],
            concern_domain=sc.get("concern_domain"),
            experience_slice=sc.get("profile") or {},
        )
        assert pack is not None
        interp = engine.thin_fallback_from_pack(pack)
        shape = geval.check_answer_shape(
            flags=list((sc.get("expect") or {}).get("answer_shape") or []),
            interpretation=interp,
            pack=pack,
            scenario=sc,
        )
        # Pack-critical offline asserts
        if "no_arkan_label" in shape:
            assert shape["no_arkan_label"] is True, sc["id"]
        if "distinct_minors" in shape:
            assert shape["distinct_minors"] is True, sc["id"]
        rubric = geval.score_rubric_heuristic(interp, question=sc["question"], answer_shape=shape)
        scenarios.append(
            {
                "id": sc["id"],
                "pack_ok": True,
                "llm_ok": None,
                "shape": shape,
                "rubric": rubric,
                "paid_worth": None,
                "rubric_mean": geval.rubric_mean(rubric),
                "notes": ["offline_test"],
            }
        )
        shape_list.append({k: shape[k] for k in shape if k in {"no_arkan_label", "distinct_minors"}})

    report = {
        "contract_version": "tarot_golden_eval_result_v1",
        "dataset_contract": "tarot_golden_dataset_v1",
        "mode": "offline",
        "generated_at": "2026-07-25T00:00:00+00:00",
        "scenarios": scenarios,
        "summary": {
            "scenario_count": len(scenarios),
            "pack_pass": len(scenarios),
            "llm_pass": None,
            "shape_pass": len(scenarios),
            "rubric_mean": None,
            "anti_sameness_mean": None,
            "anti_sameness_pass": None,
            "gates": geval.summarize_gates(
                shape_results=shape_list,
                rubric_means=[],
                anti_sameness_mean=None,
            ),
        },
    }
    report["summary"]["gates"]["freeze_lift_ready"] = False
    jsonschema.validate(report, schema)
