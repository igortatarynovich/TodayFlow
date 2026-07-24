"""Kabbalah / letter-number day factors v0 (canon §5.11).

School freeze (civil product layer — not liturgical authority):
- Hebrew civil date via absolute JDN ↔ Hebrew calendar (Fourmilab-style).
- Date gematria = day + month_index + year digits (simple mispar).
- Month letter = Alef… mapped to Hebrew month index (1→א).
- Weekday letter: Sunday=א … Saturday=ז (Hebrew week start).
- Soft sefira from weekday (Western occult weekday↔7 lower sefirot).

in_foundation=no; Today claims deferred (in_today=false).
"""

from __future__ import annotations

from datetime import date
from typing import Any

# Absolute JDN of Hebrew epoch (1 Tishri AM 1) — Fourmilab / Dershowitz–Reingold.
_HEBREW_EPOCH = 347998

_HEBREW_MONTHS_COMMON: list[tuple[str, str]] = [
    ("tishrei", "Тишрей"),
    ("cheshvan", "Хешван"),
    ("kislev", "Кислев"),
    ("tevet", "Тевет"),
    ("shevat", "Шват"),
    ("adar", "Адар"),
    ("nisan", "Нисан"),
    ("iyar", "Ияр"),
    ("sivan", "Сиван"),
    ("tamuz", "Таммуз"),
    ("av", "Ав"),
    ("elul", "Элул"),
]

_HEBREW_MONTHS_LEAP: list[tuple[str, str]] = [
    ("tishrei", "Тишрей"),
    ("cheshvan", "Хешван"),
    ("kislev", "Кислев"),
    ("tevet", "Тевет"),
    ("shevat", "Шват"),
    ("adar_i", "Адар I"),
    ("adar_ii", "Адар II"),
    ("nisan", "Нисан"),
    ("iyar", "Ияр"),
    ("sivan", "Сиван"),
    ("tamuz", "Таммуз"),
    ("av", "Ав"),
    ("elul", "Элул"),
]

# Hebrew letters א–ת for ordinals 1..22 (soft month/weekday labels).
_LETTERS: list[tuple[str, str, int]] = [
    ("alef", "א", 1),
    ("bet", "ב", 2),
    ("gimel", "ג", 3),
    ("dalet", "ד", 4),
    ("he", "ה", 5),
    ("vav", "ו", 6),
    ("zayin", "ז", 7),
    ("chet", "ח", 8),
    ("tet", "ט", 9),
    ("yod", "י", 10),
    ("kaf", "כ", 20),
    ("lamed", "ל", 30),
    ("mem", "מ", 40),
    ("nun", "נ", 50),
    ("samekh", "ס", 60),
    ("ayin", "ע", 70),
    ("pe", "פ", 80),
    ("tsadi", "צ", 90),
    ("qof", "ק", 100),
    ("resh", "ר", 200),
    ("shin", "ש", 300),
    ("tav", "ת", 400),
]

# Python weekday Mon=0…Sun=6 → Hebrew Sunday-first index 0..6
def _hebrew_weekday_index(d: date) -> int:
    return (d.weekday() + 1) % 7  # Sun=0 … Sat=6


_WEEKDAY_SEFIROT: list[tuple[str, str, str]] = [
    ("chesed", "Хесед", "доброта / расширение"),
    ("gevurah", "Гевура", "мера / граница"),
    ("tiferet", "Тиферет", "красота / баланс"),
    ("netzach", "Нецах", "стойкость / победа"),
    ("hod", "Ход", "сияние / признание"),
    ("yesod", "Йесод", "основа / связь"),
    ("malkhut", "Малхут", "проявление / присутствие"),
]


def _gregorian_to_jdn(d: date) -> int:
    y, m, day = d.year, d.month, d.day
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return day + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def hebrew_leap(year: int) -> bool:
    return ((year * 7) + 1) % 19 < 7


def _hebrew_calendar_elapsed_days(year: int) -> int:
    """Days from Hebrew epoch to before Tishri 1 of `year` (molad-based)."""
    months_elapsed = (235 * year - 234) // 19
    parts_elapsed = 12084 + 13753 * months_elapsed
    day = 29 * months_elapsed + parts_elapsed // 25920
    if (3 * (day + 1)) % 7 < 3:
        day += 1
    return day


def _hebrew_year_length(year: int) -> int:
    return _hebrew_calendar_elapsed_days(year + 1) - _hebrew_calendar_elapsed_days(year)


def _hebrew_month_length(year: int, month: int) -> int:
    """Tishrei-based month index; leap years insert Adar II as month 7."""
    leap = hebrew_leap(year)
    yl = _hebrew_year_length(year)
    if month == 1:  # Tishrei
        return 30
    if month == 2:  # Cheshvan
        return 30 if yl in (355, 385) else 29
    if month == 3:  # Kislev
        return 29 if yl in (353, 383) else 30
    if month == 4:  # Tevet
        return 29
    if month == 5:  # Shevat
        return 30
    if leap:
        if month == 6:  # Adar I
            return 30
        if month == 7:  # Adar II
            return 29
        # 8 Nisan, 9 Iyar, 10 Sivan, 11 Tamuz, 12 Av, 13 Elul
        if month in (8, 10, 12):
            return 30
        if month in (9, 11, 13):
            return 29
    else:
        if month == 6:  # Adar
            return 29
        if month in (7, 9, 11):  # Nisan, Sivan, Av
            return 30
        if month in (8, 10, 12):  # Iyar, Tamuz, Elul
            return 29
    return 29


def _hebrew_months_in_year(year: int) -> int:
    return 13 if hebrew_leap(year) else 12


def _month_meta(year: int, month: int) -> tuple[str, str]:
    table = _HEBREW_MONTHS_LEAP if hebrew_leap(year) else _HEBREW_MONTHS_COMMON
    if 1 <= month <= len(table):
        return table[month - 1]
    return ("unknown", "—")


def jdn_to_hebrew(jdn: int) -> dict[str, Any]:
    """Convert absolute JDN (noon) to Hebrew y/m/d."""
    year = (98496 * (jdn - _HEBREW_EPOCH)) // 35975351 + 1
    while jdn >= _HEBREW_EPOCH + _hebrew_calendar_elapsed_days(year):
        year += 1
    year -= 1
    start = _HEBREW_EPOCH + _hebrew_calendar_elapsed_days(year)
    day_of_year = jdn - start
    month = 1
    while month <= _hebrew_months_in_year(year):
        ml = _hebrew_month_length(year, month)
        if day_of_year < ml:
            break
        day_of_year -= ml
        month += 1
    day = day_of_year + 1
    mid, name_ru = _month_meta(year, month)

    return {
        "year": year,
        "month": month,
        "day": day,
        "month_id": mid,
        "month_ru": name_ru,
        "leap": hebrew_leap(year),
        "label_ru": f"{day} {name_ru} {year}",
    }


def gregorian_to_hebrew(d: date) -> dict[str, Any]:
    return jdn_to_hebrew(_gregorian_to_jdn(d))


def _letter_for_ordinal(n: int) -> dict[str, Any]:
    """1→Alef … 22→Tav (wrap for safety)."""
    idx = (max(1, int(n)) - 1) % 22
    lid, glyph, value = _LETTERS[idx]
    return {
        "id": lid,
        "glyph": glyph,
        "name_ru": lid,
        "ordinal": idx + 1,
        "gematria_value": value,
    }


def date_gematria(hebrew: dict[str, Any]) -> dict[str, Any]:
    """Simple civil-kabbalah mispar: day + month + digit-sum(year)."""
    year = int(hebrew["year"])
    year_digits = sum(int(c) for c in str(abs(year)))
    total = int(hebrew["day"]) + int(hebrew["month"]) + year_digits
    reduced = total
    while reduced > 9:
        reduced = sum(int(c) for c in str(reduced))
    return {
        "total": total,
        "reduced": reduced,
        "method": "day_plus_month_plus_year_digits",
    }


def build_kabbalah_letter_payload(d: date) -> dict[str, Any]:
    hebrew = gregorian_to_hebrew(d)
    gem = date_gematria(hebrew)
    month_letter = _letter_for_ordinal(int(hebrew["month"]))
    wd = _hebrew_weekday_index(d)
    weekday_letter = _letter_for_ordinal(wd + 1)
    sef_id, sef_ru, sef_theme = _WEEKDAY_SEFIROT[wd]

    beats = [
        {
            "id": "kabbalah.hebrew_date",
            "kind": "hebrew_date",
            "title": hebrew["label_ru"],
            "story_ru": f"Еврейская дата (civil): {hebrew['label_ru']}.",
            "evidence_ref": "kabbalah_letter.hebrew_date",
        },
        {
            "id": "kabbalah.gematria",
            "kind": "date_gematria",
            "title": f"Гематрия дня {gem['total']} → {gem['reduced']}",
            "story_ru": (
                f"Гематрия даты {gem['total']} (сведение {gem['reduced']}) — "
                f"школа civil_mispar_v0."
            ),
            "evidence_ref": "kabbalah_letter.date_gematria",
        },
        {
            "id": "kabbalah.sefira",
            "kind": "sefira_soft",
            "title": sef_ru,
            "story_ru": f"Сефира дня (soft): {sef_ru} — {sef_theme}.",
            "evidence_ref": "kabbalah_letter.sefira_soft",
        },
    ]

    summary = (
        f"Каббала (civil v0): {hebrew['label_ru']}; "
        f"буква месяца {month_letter['glyph']}; "
        f"гематрия {gem['total']}→{gem['reduced']}; "
        f"сефира {sef_ru}."
    )

    return {
        "capability_ids": [
            "hebrew_date",
            "date_gematria",
            "month_letter",
            "weekday_letter",
            "sefira_soft",
        ],
        "hebrew_date": hebrew,
        "date_gematria": gem,
        "month_letter": month_letter,
        "weekday_letter": weekday_letter,
        "sefira": {
            "id": sef_id,
            "name_ru": sef_ru,
            "theme_ru": sef_theme,
            "weekday_index_sun0": wd,
        },
        "beats": beats,
        "summary_ru": summary[:420],
        "school_canon": "civil_hebrew_calendar_mispar_v0",
        "target_date": d.isoformat(),
        "notes_ru": (
            "Не литургический авторитет: школа зафиксирована для продукта; "
            "религиозные варианты остаются вне v0."
        ),
    }
