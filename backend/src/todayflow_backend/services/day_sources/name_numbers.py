"""Name numbers soft layer (canon §5.5.5).

School freeze v0: Cyrillic/Ukrainian letters → Latin translit (same map as account
numerology normalize), then Pythagorean Latin values from DATA/numerology.json.
Not a second alphabet school — one path so RU/EN names stay comparable.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.data import numerology as numerology_ref

_SCHOOL = "pythagorean_latin_v0_via_ru_translit"
_CALC = "name-numbers-v0"

# Frozen translit — keep in sync with api/account._normalize_numerology_name.
_TRANSLIT = str.maketrans(
    {
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "E",
        "Ж": "ZH",
        "З": "Z",
        "И": "I",
        "Й": "I",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "H",
        "Ц": "TS",
        "Ч": "CH",
        "Ш": "SH",
        "Щ": "SH",
        "Ъ": "",
        "Ы": "Y",
        "Ь": "",
        "Э": "E",
        "Ю": "YU",
        "Я": "YA",
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sh",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "І": "I",
        "і": "i",
        "Ї": "I",
        "ї": "i",
        "Є": "E",
        "є": "e",
    }
)

_MASTER = {11, 22, 33}


def normalize_name_for_numbers(raw: str | None) -> str:
    text = (raw or "").translate(_TRANSLIT)
    cleaned = "".join(ch for ch in text if ch.isalpha() or ch in {" ", "-"})
    return " ".join(cleaned.split())


def _reduce(value: int) -> int:
    while value > 9 and value not in _MASTER:
        value = sum(int(d) for d in str(value))
    return value


def build_name_numbers_payload(birth_name: str | None) -> dict[str, Any] | None:
    """Return Expression / Soul Urge / Personality soft pack, or None if unusable."""
    display = (birth_name or "").strip()
    if not display:
        return None

    letter_map = numerology_ref.letters()
    vowels = numerology_ref.vowels()
    normalized = normalize_name_for_numbers(display)
    letters = [ch for ch in normalized.upper() if ch in letter_map]
    if not letters:
        return {
            "status": "unavailable",
            "reason": "no_mappable_letters",
            "birth_name": display,
            "normalized_name": normalized or None,
            "school_canon": _SCHOOL,
            "limitation_ru": (
                "Имя не дало букв после транслита в Pythagorean Latin — слой имени опущен."
            ),
        }

    expression_total = sum(letter_map[ch] for ch in letters)
    soul_total = sum(letter_map[ch] for ch in letters if ch in vowels)
    personality_total = sum(letter_map[ch] for ch in letters if ch not in vowels)

    expression = _reduce(expression_total)
    soul_urge = _reduce(soul_total) if soul_total else None
    personality = _reduce(personality_total) if personality_total else None

    summary = (
        f"Числа имени (soft): Expression {expression}"
        + (f", Soul Urge {soul_urge}" if soul_urge is not None else "")
        + (f", Personality {personality}" if personality is not None else "")
        + "."
    )

    return {
        "status": "ok",
        "birth_name": display,
        "normalized_name": normalized,
        "school_canon": _SCHOOL,
        "calculation_version": _CALC,
        "expression": {
            "value": expression,
            "total": expression_total,
            "name_ru": "Expression",
            "theme_ru": "как звучишь вовне",
        },
        "soul_urge": (
            {
                "value": soul_urge,
                "total": soul_total,
                "name_ru": "Soul Urge",
                "theme_ru": "чего хочется изнутри",
            }
            if soul_urge is not None
            else None
        ),
        "personality": (
            {
                "value": personality,
                "total": personality_total,
                "name_ru": "Personality",
                "theme_ru": "как тебя считывают",
            }
            if personality is not None
            else None
        ),
        "letter_count": len(letters),
        "summary_ru": summary[:280],
        "beats": [
            {
                "id": "name.expression",
                "kind": "name_numbers",
                "title": f"Expression {expression}",
                "story_ru": f"Expression {expression} — как имя звучит вовне (soft Pythagorean).",
                "evidence_ref": "name_numbers.expression",
            }
        ],
        "limitation_ru": (
            "Soft name numbers: RU/UA→Latin translit then Pythagorean A–Z. "
            "Not a native Cyrillic school; not destiny forecasting."
        ),
    }
