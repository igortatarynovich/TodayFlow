"""Mayan calendars v0 — classical Tzolkin/Haab (GMT) + Dreamspell (Argüelles).

Canon §5.10: never merge tzolkin_haab ids with dreamspell ids.
"""

from __future__ import annotations

from datetime import date
from typing import Any

# Goodman–Martinez–Thompson correlation: LC 0.0.0.0.0 = JD 584283
# = proleptic Gregorian 3114-08-11 BCE (astronomical year -3113-08-11).
_GMT_JD = 584283
# At epoch: Tzolkin 4 Ajaw, Haab 8 Cumku.
_TZOLKIN_EPOCH_NUMBER = 4
_TZOLKIN_EPOCH_SIGN = 19  # Ajaw
_HAAB_EPOCH_DOY = 17 * 20 + 8  # Cumku day 8

# Dreamspell school freeze: 1987-07-26 = Kin 1 (Red Magnetic Dragon).
_DREAMSPELL_EPOCH = date(1987, 7, 26)

_TZOLKIN_SIGNS: list[tuple[str, str]] = [
    ("imix", "Имиш"),
    ("ik", "Ик"),
    ("akbal", "Акбаль"),
    ("kan", "Кан"),
    ("chicchan", "Чикчан"),
    ("cimi", "Кими"),
    ("manik", "Маник"),
    ("lamat", "Ламат"),
    ("muluc", "Мулук"),
    ("oc", "Ок"),
    ("chuen", "Чуэн"),
    ("eb", "Эб"),
    ("ben", "Бен"),
    ("ix", "Иш"),
    ("men", "Мен"),
    ("cib", "Киб"),
    ("caban", "Кабан"),
    ("etznab", "Эцнаб"),
    ("cauac", "Кавак"),
    ("ahau", "Ахав"),
]

_HAAB_MONTHS: list[tuple[str, str]] = [
    ("pop", "Поп"),
    ("wo", "Во"),
    ("sip", "Сип"),
    ("sotz", "Соц"),
    ("sek", "Сек"),
    ("xul", "Шуль"),
    ("yaxkin", "Яшкин"),
    ("mol", "Моль"),
    ("chen", "Чен"),
    ("yax", "Яш"),
    ("sac", "Сак"),
    ("keh", "Кех"),
    ("mak", "Мак"),
    ("kankin", "Канкін"),
    ("muan", "Муан"),
    ("pax", "Паш"),
    ("kayab", "Каяб"),
    ("kumku", "Кумку"),
    ("wayeb", "Вайеб"),
]

# Dreamspell seals (Argüelles) — separate vocabulary from classical signs.
_DREAMSPELL_SEALS: list[tuple[str, str, str]] = [
    ("dragon", "Дракон", "red"),
    ("wind", "Ветер", "white"),
    ("night", "Ночь", "blue"),
    ("seed", "Семя", "yellow"),
    ("serpent", "Змей", "red"),
    ("worldbridger", "Мировой мост", "white"),
    ("hand", "Рука", "blue"),
    ("star", "Звезда", "yellow"),
    ("moon", "Луна", "red"),
    ("dog", "Собака", "white"),
    ("monkey", "Обезьяна", "blue"),
    ("human", "Человек", "yellow"),
    ("skywalker", "Небесный странник", "red"),
    ("wizard", "Маг", "white"),
    ("eagle", "Орёл", "blue"),
    ("warrior", "Воин", "yellow"),
    ("earth", "Земля", "red"),
    ("mirror", "Зеркало", "white"),
    ("storm", "Шторм", "blue"),
    ("sun", "Солнце", "yellow"),
]

_DREAMSPELL_TONES: list[tuple[str, str]] = [
    ("magnetic", "Магнитный"),
    ("lunar", "Лунный"),
    ("electric", "Электрический"),
    ("self_existing", "Самосуществующий"),
    ("overtone", "ОбTone"),
    ("rhythmic", "Ритмический"),
    ("resonant", "Резонансный"),
    ("galactic", "Галактический"),
    ("solar", "Солнечный"),
    ("planetary", "Планетарный"),
    ("spectral", "Спектральный"),
    ("crystal", "Кристаллический"),
    ("cosmic", "Космический"),
]

# Fix tone 5 label typo
_DREAMSPELL_TONES[4] = ("overtone", "Обертон")

_COLOR_RU = {"red": "красный", "white": "белый", "blue": "синий", "yellow": "жёлтый"}


def _gregorian_to_jd(d: date) -> int:
    """Julian Day Number at noon UT (integer civil JD)."""
    y, m, day = d.year, d.month, d.day
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return day + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def days_since_maya_epoch(d: date) -> int:
    return _gregorian_to_jd(d) - _GMT_JD


def long_count(days: int) -> dict[str, Any]:
    """Classic Long Count from days since 0.0.0.0.0 (soft accompaniment)."""
    baktun, rem = divmod(days, 144000)
    katun, rem = divmod(rem, 7200)
    tun, rem = divmod(rem, 360)
    uinal, kin = divmod(rem, 20)
    return {
        "baktun": baktun,
        "katun": katun,
        "tun": tun,
        "uinal": uinal,
        "kin": kin,
        "label": f"{baktun}.{katun}.{tun}.{uinal}.{kin}",
    }


def tzolkin_for_days(days: int) -> dict[str, Any]:
    number = ((_TZOLKIN_EPOCH_NUMBER - 1 + days) % 13) + 1
    sign_i = (_TZOLKIN_EPOCH_SIGN + days) % 20
    sid, name_ru = _TZOLKIN_SIGNS[sign_i]
    return {
        "number": number,
        "sign_id": sid,
        "sign_index": sign_i,
        "sign_ru": name_ru,
        "label": f"{number} {name_ru}",
        "cycle_day": days % 260,
    }


def haab_for_days(days: int) -> dict[str, Any]:
    doy = (_HAAB_EPOCH_DOY + days) % 365
    if doy >= 360:
        month_i = 18
        day = doy - 360
    else:
        month_i = doy // 20
        day = doy % 20
    mid, name_ru = _HAAB_MONTHS[month_i]
    return {
        "day": day,
        "month_id": mid,
        "month_index": month_i,
        "month_ru": name_ru,
        "label": f"{day} {name_ru}",
        "day_of_year": doy,
    }


def build_tzolkin_haab(d: date) -> dict[str, Any]:
    days = days_since_maya_epoch(d)
    tz = tzolkin_for_days(days)
    haab = haab_for_days(days)
    lc = long_count(days)
    summary = (
        f"Классический майя (GMT): цолькин {tz['label']}, хааб {haab['label']}, "
        f"Long Count {lc['label']}."
    )
    return {
        "capability_id": "tzolkin_haab",
        "correlation": "gmt_584283",
        "days_since_epoch": days,
        "tzolkin": tz,
        "haab": haab,
        "long_count": lc,
        "summary_ru": summary,
        "school_canon": "historical_gmt_tzolkin_haab",
    }


def build_dreamspell(d: date) -> dict[str, Any]:
    """Argüelles Dreamspell Kin — independent of classical Tzolkin numbering."""
    delta = (d - _DREAMSPELL_EPOCH).days
    # Kin 1 on epoch; Kin cycles 1..260
    kin = (delta % 260) + 1
    tone_i = (kin - 1) % 13
    seal_i = (kin - 1) % 20
    tone_id, tone_ru = _DREAMSPELL_TONES[tone_i]
    seal_id, seal_ru, color = _DREAMSPELL_SEALS[seal_i]
    wavespell = ((kin - 1) // 13) + 1
    summary = (
        f"Dreamspell: Kin {kin} — {tone_ru} {seal_ru} "
        f"({_COLOR_RU[color]}), волны {wavespell}/20."
    )
    return {
        "capability_id": "dreamspell",
        "kin": kin,
        "tone": {"index": tone_i + 1, "id": tone_id, "name_ru": tone_ru},
        "seal": {
            "index": seal_i + 1,
            "id": seal_id,
            "name_ru": seal_ru,
            "color": color,
            "color_ru": _COLOR_RU[color],
        },
        "wavespell": wavespell,
        "epoch": _DREAMSPELL_EPOCH.isoformat(),
        "summary_ru": summary,
        "school_canon": "arguelles_dreamspell_kin1_1987_07_26",
        # Explicit non-identity with classical count:
        "not_classical_tzolkin": True,
    }


def build_mayan_calendars_payload(d: date) -> dict[str, Any]:
    classical = build_tzolkin_haab(d)
    dreamspell = build_dreamspell(d)
    summary = f"{classical['summary_ru']} {dreamspell['summary_ru']}"
    return {
        "tzolkin_haab": classical,
        "dreamspell": dreamspell,
        "capability_ids": ["tzolkin_haab", "dreamspell"],
        "summary_ru": summary[:420],
        "target_date": d.isoformat(),
        "note_ru": "Цолькин/Хааб и Dreamspell — разные системы; ids не смешиваются.",
    }
