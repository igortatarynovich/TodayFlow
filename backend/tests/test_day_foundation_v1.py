"""Tests for day_foundation_v1 — astro + lunar → essence."""

from __future__ import annotations

from todayflow_backend.services.day_foundation_v1 import (
    DAY_FOUNDATION_V1,
    build_day_foundation_v1,
    foundation_to_interpretation_claims,
)


def _sample_ce() -> dict:
    return {
        "lunar_phase": {
            "id": "waning",
            "name": "Убывающая луна",
            "themes": "отпускание лишнего",
            "guidance": "Отпускай лишнее, чтобы осталось главное.",
            "cycle_day": 22,
            "next_phase": {"name": "Новолуние", "in_days": 3},
        },
        "moon_sign": {"sign": "Sagittarius", "sign_ru": "Стрелец", "source": "transit_chart"},
        "ingresses": [
            {
                "planet": "Mercury",
                "planet_ru": "Меркурий",
                "sign_ru": "Рак",
                "story_ru": "Меркурий переходит в Рак — меняется тон разговоров.",
            },
            {
                "planet": "Moon",
                "planet_ru": "Луна",
                "sign_ru": "Стрелец",
                "story_ru": "Луна переходит в Стрелец — взгляд расширяется.",
            },
        ],
        "retrogrades": [],
        "sky_aspects": [
            {
                "id": "sun-trine-saturn",
                "title": "Солнце — тригон — Сатурн",
                "story_ru": "Структура дня поддерживает спокойные решения.",
            },
            {
                "id": "moon-square-mars",
                "title": "Луна — квадрат — Марс",
                "story_ru": "Эмоции быстрее, чем обычно, толкают к действию.",
            },
        ],
    }


def test_foundation_splits_astro_and_lunar():
    f = build_day_foundation_v1(_sample_ce())
    assert f["contract_version"] == DAY_FOUNDATION_V1
    astro_kinds = {b["kind"] for b in f["astro"]["beats"]}
    assert "ingress" in astro_kinds
    assert "aspect" in astro_kinds
    # Mercury ingress is astro; Moon ingress is lunar
    astro_titles = " ".join(b["title"] for b in f["astro"]["beats"])
    assert "Меркурий" in astro_titles
    lunar_titles = " ".join(b["title"] for b in f["lunar"]["beats"])
    assert "Луна" in lunar_titles or "Убывающая" in lunar_titles
    assert f["lunar"]["moon_sign"]["sign_ru"] == "Стрелец"
    assert f["astro"]["summary_ru"]
    assert f["lunar"]["summary_ru"]
    assert f["essence"]["theme"]
    assert f["essence"]["story_ru"]
    assert "стыке" in f["essence"]["story_ru"] or "двух" in f["essence"]["story_ru"]


def test_foundation_empty_without_celestial():
    f = build_day_foundation_v1({})
    assert f["essence"]["story_ru"] == ""
    assert f["source_inputs"]["has_essence"] is False


def test_foundation_claims_for_interpretation():
    f = build_day_foundation_v1(_sample_ce())
    claims = foundation_to_interpretation_claims(f)
    ids = {c["id"] for c in claims}
    assert "claim.foundation.essence" in ids
    assert any(i.startswith("claim.foundation.astro.") for i in ids)
    assert any(i.startswith("claim.foundation.lunar.") for i in ids)
