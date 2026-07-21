"""C3 — profile content contracts and source depth."""

from __future__ import annotations

import json
from pathlib import Path

from todayflow_backend.services.profile_content_v1.architecture import (
    LLM_ON_READ_RISK_CALLERS,
    classify_allowed_claims,
)
from todayflow_backend.services.profile_content_v1.banned_phrases import (
    find_banned_hits,
    find_depth_overclaims,
)
from todayflow_backend.services.profile_content_v1.contracts import ProfileBaseContentV1
from todayflow_backend.services.profile_content_v1.source_depth import (
    depth_honesty_line,
    resolve_profile_source_depth,
)


def test_source_depth_ladder():
    assert resolve_profile_source_depth(has_birth=True) == "birth_data_only"
    assert resolve_profile_source_depth(has_birth=True, has_onboarding=True) == "onboarding_answers"
    assert (
        resolve_profile_source_depth(has_birth=True, has_onboarding=True, checkin_days=4)
        == "profile_plus_checkins"
    )
    assert (
        resolve_profile_source_depth(
            has_birth=True, has_onboarding=True, checkin_days=8, longitudinal_days=20
        )
        == "longitudinal_profile"
    )


def test_birth_honesty_no_behaviour_claim():
    line = depth_honesty_line("birth_data_only", locale="ru")
    assert "недостаточно" in line.lower() or "общего" in line.lower() or "общий" in line.lower()


def test_base_contract_requires_fields():
    m = ProfileBaseContentV1(
        source_depth="birth_data_only",
        headline="Инициатор с коротким запалом",
        core_summary="Вы быстро стартуете и так же быстро выгораете без опоры. Это общий портрет по данным рождения — не описание вашего вчерашнего дня.",
        strengths=["быстрый старт", "ясный импульс"],
        emotional_style="Тепло включается после действия, не до него.",
        communication_style="Прямо и коротко — длинные намёки раздражают.",
        decision_style="Решаете быстро, потом правите по ходу.",
        energy_sources="Новая задача с видимым финишем.",
        energy_drains="Ожидание и размытые договорённости.",
        under_pressure="Может проявляться как ускорение или резкий обрыв контакта.",
        inner_tension="Между желанием вести и усталостью от постоянной инициативы.",
        practical_takeaway="На этой неделе заранее назначьте один слот восстановления после рывка.",
        confidence="low",
    )
    assert m.tier == "base"


def test_depth_overclaim_flagged():
    errs = find_depth_overclaims(
        "В последние недели вы чаще откладываете разговоры",
        source_depth="birth_data_only",
    )
    assert errs


def test_banned_always():
    assert find_banned_hits("Вы всегда так реагируете")


def test_architecture_lists_nonempty():
    assert len(LLM_ON_READ_RISK_CALLERS) >= 3
    claims = classify_allowed_claims("birth_data_only")
    assert claims["recurring_patterns"] is False


def test_scenarios_coverage():
    path = Path(__file__).resolve().parents[1] / "evals" / "profile_quality" / "scenarios_v1.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["scenario_count"] == 10
    assert len(doc["scenarios"]) == 10
    groups = {s["group"] for s in doc["scenarios"]}
    for g in (
        "birth_data_only",
        "onboarding_answers",
        "partial_profile",
        "checkin_history",
        "contradictory",
        "premium_question",
    ):
        assert g in groups
