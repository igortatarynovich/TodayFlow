"""Civil / soft holiday calendar for seasonal_calendar (canon §5.14 holidays).

v0: fixed-date civil observances by locale. No moveable feasts (Easter etc.) yet.
"""

from __future__ import annotations

from datetime import date
from typing import Any

# (month, day) → (id, name_ru, name_en, kind)
_RU_FIXED: dict[tuple[int, int], tuple[str, str, str, str]] = {
    (1, 1): ("new_year", "Новый год", "New Year's Day", "civil"),
    (1, 2): ("new_year_holiday", "Новогодние каникулы", "New Year holiday", "civil"),
    (1, 7): ("orthodox_christmas", "Рождество Христово", "Orthodox Christmas", "religious_civil"),
    (2, 23): ("defender_day", "День защитника Отечества", "Defender of the Fatherland Day", "civil"),
    (3, 8): ("womens_day", "Международный женский день", "International Women's Day", "civil"),
    (5, 1): ("labour_day", "Праздник Весны и Труда", "Spring and Labour Day", "civil"),
    (5, 9): ("victory_day", "День Победы", "Victory Day", "civil"),
    (6, 12): ("russia_day", "День России", "Russia Day", "civil"),
    (11, 4): ("unity_day", "День народного единства", "Unity Day", "civil"),
    (12, 31): ("new_year_eve", "Канун Нового года", "New Year's Eve", "observance"),
}

_EN_FIXED: dict[tuple[int, int], tuple[str, str, str, str]] = {
    (1, 1): ("new_year", "Новый год", "New Year's Day", "civil"),
    (2, 14): ("valentines", "День святого Валентина", "Valentine's Day", "observance"),
    (3, 8): ("womens_day", "Международный женский день", "International Women's Day", "observance"),
    (3, 17): ("st_patricks", "День святого Патрика", "St. Patrick's Day", "observance"),
    (5, 1): ("labour_day", "День труда", "International Workers' Day", "observance"),
    (7, 4): ("independence_us", "День независимости США", "Independence Day (US)", "civil"),
    (10, 31): ("halloween", "Хэллоуин", "Halloween", "observance"),
    (12, 25): ("christmas", "Рождество", "Christmas Day", "religious_civil"),
    (12, 31): ("new_year_eve", "Канун Нового года", "New Year's Eve", "observance"),
}

_SHARED_SOFT: dict[tuple[int, int], tuple[str, str, str, str]] = {
    (1, 1): ("new_year", "Новый год", "New Year's Day", "civil"),
    (3, 8): ("womens_day", "Международный женский день", "International Women's Day", "observance"),
    (5, 1): ("labour_day", "Праздник труда", "Labour Day", "observance"),
    (12, 31): ("new_year_eve", "Канун Нового года", "New Year's Eve", "observance"),
}


def _locale_bucket(locale: str | None) -> str:
    loc = (locale or "ru").strip().lower()
    if loc.startswith("en"):
        return "en"
    if loc.startswith("ru") or loc.startswith("uk") or loc.startswith("be"):
        return "ru"
    return "soft"


def holidays_for_date(target: date, *, locale: str | None = "ru") -> dict[str, Any]:
    bucket = _locale_bucket(locale)
    table = _RU_FIXED if bucket == "ru" else _EN_FIXED if bucket == "en" else _SHARED_SOFT
    key = (target.month, target.day)
    hit = table.get(key)
    today: list[dict[str, Any]] = []
    if hit:
        hid, name_ru, name_en, kind = hit
        today.append(
            {
                "id": hid,
                "name_ru": name_ru,
                "name_en": name_en,
                "kind": kind,
                "fixed_date": True,
            }
        )

    name = today[0]["name_ru"] if today else None
    summary = (
        f"Сегодня — {name}."
        if name
        else "Сегодня без отмеченного гражданского праздника в soft-календаре."
    )
    return {
        "locale_bucket": bucket,
        "school_canon": "civil_fixed_v0",
        "today": today,
        "is_holiday": bool(today),
        "summary_ru": summary,
        "limitation_ru": (
            "Soft fixed-date civil/observance calendar. No moveable feasts; "
            "not a legal holiday API."
        ),
    }
