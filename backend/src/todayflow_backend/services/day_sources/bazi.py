"""BaZi personal layer — year/day(/month/hour) pillars vs day + animal clashes (canon §5.7).

Reuses sexagenary helpers from chinese_metaphysics. Hour pillar gated on birth_time.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

from todayflow_backend.services.day_sources.chinese_metaphysics import (
    day_pillar_index,
    gan_zhi_from_index,
    solar_month_branch_index,
)
from todayflow_backend.services.day_sources.panchanga import tropical_sun_longitude

# 1984 Lichun opens Jia-Zi year (甲子).
_YEAR_PILLAR_EPOCH_YEAR = 1984

# Yin-month stem for each year stem (Jia→Bing, Yi→Wu, …).
_YIN_MONTH_STEM_BY_YEAR_STEM = (2, 4, 6, 8, 0, 2, 4, 6, 8, 0)

# Zi-hour stem for each day stem (Jia/Ji→Jia, Yi/Geng→Bing, …).
_ZI_HOUR_STEM_BY_DAY_STEM = (0, 2, 4, 6, 8, 0, 2, 4, 6, 8)

# Six clashes (六冲) — unordered pairs of branch ids.
_CLASH_PAIRS: frozenset[frozenset[str]] = frozenset(
    {
        frozenset({"zi", "wu"}),
        frozenset({"chou", "wei"}),
        frozenset({"yin", "shen"}),
        frozenset({"mao", "you"}),
        frozenset({"chen", "xu"}),
        frozenset({"si", "hai"}),
    }
)

# Six combinations (六合) — soft harmony signal.
_COMBINE_PAIRS: frozenset[frozenset[str]] = frozenset(
    {
        frozenset({"zi", "chou"}),
        frozenset({"yin", "hai"}),
        frozenset({"mao", "xu"}),
        frozenset({"chen", "you"}),
        frozenset({"si", "shen"}),
        frozenset({"wu", "wei"}),
    }
)

_CLASH_STORY = {
    frozenset({"zi", "wu"}): "Крыса ↔ Лошадь — ось напряжения в темпе и направлении.",
    frozenset({"chou", "wei"}): "Бык ↔ Коза — трение в устойчивости и заботе.",
    frozenset({"yin", "shen"}): "Тигр ↔ Обезьяна — спор инициативы и манёвра.",
    frozenset({"mao", "you"}): "Кролик ↔ Петух — конфликт мягкости и критики.",
    frozenset({"chen", "xu"}): "Дракон ↔ Собака — спор верности и перемены курса.",
    frozenset({"si", "hai"}): "Змея ↔ Свинья — скрытое vs открытое напряжение.",
}

_COMBINE_STORY = {
    frozenset({"zi", "chou"}): "Крыса + Бык — опора и договорённость.",
    frozenset({"yin", "hai"}): "Тигр + Свинья — поддержка движения.",
    frozenset({"mao", "xu"}): "Кролик + Собака — тёплая связка.",
    frozenset({"chen", "you"}): "Дракон + Петух — собранная пара.",
    frozenset({"si", "shen"}): "Змея + Обезьяна — живой контакт.",
    frozenset({"wu", "wei"}): "Лошадь + Коза — мягкое усиление.",
}


def chinese_solar_year(d: date) -> int:
    """Western year label of the Chinese solar year (Lichun boundary ≈ Feb 4)."""
    lichun_approx = date(d.year, 2, 4)
    if d < lichun_approx:
        return d.year - 1
    return d.year


def year_pillar_for_date(d: date) -> dict[str, Any]:
    y = chinese_solar_year(d)
    idx = (y - _YEAR_PILLAR_EPOCH_YEAR) % 60
    pillar = gan_zhi_from_index(idx)
    pillar["solar_year"] = y
    pillar["kind"] = "year"
    return pillar


def month_pillar_for_date(d: date) -> dict[str, Any]:
    year = year_pillar_for_date(d)
    year_stem_i = int(year["cycle_index"]) % 10
    sun_lon = tropical_sun_longitude(d)
    month_bi = solar_month_branch_index(sun_lon)
    yin_stem = _YIN_MONTH_STEM_BY_YEAR_STEM[year_stem_i]
    # Yin branch index = 2; stem advances with branch from Yin.
    month_stem_i = (yin_stem + (month_bi - 2)) % 10
    # Reconstruct cycle index from stem/branch pair (unique in 60).
    # Find idx where idx%10==stem and idx%12==branch.
    idx = next(i for i in range(60) if i % 10 == month_stem_i and i % 12 == month_bi)
    pillar = gan_zhi_from_index(idx)
    pillar["kind"] = "month"
    return pillar


def day_pillar_for_date(d: date) -> dict[str, Any]:
    pillar = gan_zhi_from_index(day_pillar_index(d))
    pillar["kind"] = "day"
    return pillar


def hour_branch_index(t: time) -> int:
    """Earthly branch for Chinese double-hour; Zi covers 23:00–00:59."""
    h = int(t.hour)
    if h == 23:
        return 0
    return (h + 1) // 2 % 12


def hour_pillar_for_day(day_pillar: dict[str, Any], birth_time: time) -> dict[str, Any]:
    day_stem_i = int(day_pillar["cycle_index"]) % 10
    bi = hour_branch_index(birth_time)
    stem_i = (_ZI_HOUR_STEM_BY_DAY_STEM[day_stem_i] + bi) % 10
    idx = next(i for i in range(60) if i % 10 == stem_i and i % 12 == bi)
    pillar = gan_zhi_from_index(idx)
    pillar["kind"] = "hour"
    pillar["birth_time"] = birth_time.isoformat(timespec="minutes")
    return pillar


def _relation(a_branch: str, b_branch: str) -> str | None:
    pair = frozenset({a_branch, b_branch})
    if pair in _CLASH_PAIRS:
        return "clash"
    if pair in _COMBINE_PAIRS:
        return "combine"
    return None


def _beat_for_relation(
    *,
    rel: str,
    natal_role: str,
    natal_branch: dict[str, Any],
    day_branch: dict[str, Any],
) -> dict[str, Any]:
    pair = frozenset({natal_branch["id"], day_branch["id"]})
    if rel == "clash":
        story = _CLASH_STORY.get(
            pair,
            f"{natal_branch['animal_ru']} ↔ {day_branch['animal_ru']} — clash дня.",
        )
        title = f"Clash: {natal_role} ↔ день"
        kind = "branch_clash"
    else:
        story = _COMBINE_STORY.get(
            pair,
            f"{natal_branch['animal_ru']} + {day_branch['animal_ru']} — гармония дня.",
        )
        title = f"Harmony: {natal_role} + день"
        kind = "branch_combine"
    return {
        "id": f"bazi-{kind}-{natal_role}-{natal_branch['id']}-{day_branch['id']}",
        "kind": kind,
        "relation": rel,
        "title": title,
        "story_ru": story,
        "natal_role": natal_role,
        "natal_animal_ru": natal_branch.get("animal_ru"),
        "day_animal_ru": day_branch.get("animal_ru"),
        "evidence_ref": "bazi.clashes",
    }


def build_bazi_personal_payload(
    target_date: date,
    birth_date: date,
    *,
    birth_time: time | None = None,
) -> dict[str, Any]:
    day = day_pillar_for_date(target_date)
    birth_year = year_pillar_for_date(birth_date)
    birth_month = month_pillar_for_date(birth_date)
    birth_day = day_pillar_for_date(birth_date)
    birth_hour = hour_pillar_for_day(birth_day, birth_time) if birth_time is not None else None

    caps = ["clashes", "bazi"]
    depth = "year_day"
    if birth_time is not None:
        depth = "four_pillars"
        caps.append("hour_pillar")
    else:
        depth = "three_pillars"  # year/month/day without hour

    pillars = {
        "day": day,
        "birth_year": birth_year,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "birth_hour": birth_hour,
    }

    beats: list[dict[str, Any]] = []
    day_br = day["branch"]
    for role, pillar in (
        ("year", birth_year),
        ("day", birth_day),
        ("month", birth_month),
        ("hour", birth_hour),
    ):
        if not isinstance(pillar, dict):
            continue
        rel = _relation(str(pillar["branch"]["id"]), str(day_br["id"]))
        if rel:
            beats.append(
                _beat_for_relation(
                    rel=rel,
                    natal_role=role,
                    natal_branch=pillar["branch"],
                    day_branch=day_br,
                )
            )

    # Tai Sui-ish: birth year animal vs today's year animal
    today_year = year_pillar_for_date(target_date)
    tai = _relation(str(birth_year["branch"]["id"]), str(today_year["branch"]["id"]))
    tai_sui = None
    if tai == "clash":
        tai_sui = {
            "relation": "clash",
            "birth_year_animal_ru": birth_year["branch"]["animal_ru"],
            "year_animal_ru": today_year["branch"]["animal_ru"],
            "story_ru": (
                f"Год {today_year['branch']['animal_ru']} в clash с вашим годом "
                f"{birth_year['branch']['animal_ru']} (Tai Sui soft)."
            ),
        }
        beats.insert(
            0,
            {
                "id": "bazi-tai-sui-clash",
                "kind": "tai_sui_clash",
                "relation": "clash",
                "title": "Tai Sui clash",
                "story_ru": tai_sui["story_ru"],
                "evidence_ref": "bazi.clashes",
            },
        )

    if beats:
        summary = beats[0]["story_ru"]
        if len(beats) > 1:
            summary = f"{summary} Ещё сигналов BaZi: {len(beats) - 1}."
    else:
        summary = (
            f"BaZi: день {day['label_zh']}, ваш год {birth_year['label_zh']} "
            f"({birth_year['branch']['animal_ru']}) — без прямого clash с днём."
        )

    return {
        "capability_ids": caps,
        "depth": depth,
        "pillars": pillars,
        "today_year": today_year,
        "tai_sui": tai_sui,
        "beats": beats,
        "summary_ru": summary[:420],
        "school_canon": "sexagenary_bazi_v0",
        "birth_date": birth_date.isoformat(),
        "target_date": target_date.isoformat(),
    }
