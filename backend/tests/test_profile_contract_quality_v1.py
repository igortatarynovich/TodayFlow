"""Unit tests for profile_contract_quality_v1 gates."""

from __future__ import annotations

from todayflow_backend.services.profile_contract_quality_v1 import (
    validate_profile_contract_strict,
    validate_quality_gates,
    validate_required_fields,
)
from todayflow_backend.services.profile_disclosure_funnel_v0 import SPHERE_IDS


def test_missing_spheres_fail_required() -> None:
    errors = validate_required_fields(
        {
            "contract_version": "profile_contract_v1",
            "identity_core": "Достаточно длинный identity core для проверки поля.",
            "strengths": ["a", "b", "c"],
            "growth_zones": ["d", "e", "f"],
            "relationship_style": "Стиль отношений достаточно длинный.",
            "money_style": "Стиль денег достаточно длинный.",
            "decision_style": "Стиль решений достаточно длинный.",
            "recurring_patterns": ["Паттерн достаточно длинный."],
            "living_changes": "Изменения сейчас достаточно длинные.",
            "life_mission": "Миссия достаточно длинная строка.",
            "helps": ["опора один", "опора два"],
            "life_spheres": {},
        }
    )
    assert any(e.startswith("sphere_") for e in errors)


def test_duplicate_sentence_flagged() -> None:
    dup = "Один и тот же длинный смысловой кусок повторяется без нужды в портрете."
    spheres = {
        sid: {
            "how": dup if sid == "love" else f"{sid} how concrete situation with a verb and boundary.",
            "need": f"{sid} need clarity and one honest step today.",
            "risk": f"{sid} risk is stacking silent obligations again.",
            "turns_on": f"{sid} turns on with calm structure and contact.",
            "turns_off": f"{sid} turns off under vague pressure and noise.",
            "helps": f"{sid} helps with one small protected calendar block.",
        }
        for sid in SPHERE_IDS
    }
    spheres["money"]["how"] = dup
    errors = validate_quality_gates(
        {
            "identity_core": "Человек держит фокус через ясный контакт, не через суету.",
            "life_spheres": spheres,
            "relationship_style": "Близость через прямые слова и предсказуемость ответа.",
            "money_style": "Деньги как спокойный шаг без импульса и стыда.",
            "decision_style": "Решения через один критерий и короткий дедлайн.",
            "living_changes": "Сейчас растёт запрос на один главный фокус дня.",
            "life_mission": "Держать свой ритм и не растворяться в чужих задачах.",
            "strengths": ["Фокус", "Контакт", "Доведение"],
            "growth_zones": ["Распыление", "Контроль", "Откладывание"],
            "helps": ["Один фокус", "Пауза перед да"],
            "recurring_patterns": ["Второй приоритет без слота"],
        }
    )
    assert "duplicate_sentence" in errors


def test_strict_ok_on_distinct_portrait() -> None:
    spheres = {
        sid: {
            "how": f"В сфере {sid} человек проходит уникальный сценарий с глаголом и границей.",
            "need": f"{sid} needs clarity and one honest named step.",
            "risk": f"{sid} risk is stacking silent obligations without a slot.",
            "turns_on": f"{sid} turns on with calm structure and one clear ask.",
            "turns_off": f"{sid} turns off under vague pressure and comparison.",
            "helps": f"{sid} helps with one small protected calendar block.",
        }
        for sid in SPHERE_IDS
    }
    report = validate_profile_contract_strict(
        {
            "contract_version": "profile_contract_v1",
            "identity_core": "Человек держит смысл через ясный фокус и прямой контакт.",
            "strengths": ["Фокус на одном", "Прямой контакт", "Доведение до конца"],
            "growth_zones": ["Второй приоритет", "Контроль вместо ясности", "Откладывание разговора"],
            "relationship_style": "Близость строится через прямые слова и предсказуемый ритм.",
            "money_style": "Деньги как ценность спокойствия и один ясный шаг.",
            "decision_style": "Решения через один критерий и короткий дедлайн.",
            "recurring_patterns": ["Часто берёт второй приоритет без слота времени."],
            "living_changes": "Сейчас усиливается запрос на один главный фокус.",
            "life_mission": "Удерживать свой ритм и не растворяться в чужих задачах.",
            "helps": ["Один фокус на день", "Пауза перед новым да"],
            "life_spheres": spheres,
        }
    )
    assert report["ok"] is True
