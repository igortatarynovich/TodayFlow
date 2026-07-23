"""Profile header knowledge pack v0 — deterministic catalog for шапка.

Accumulates lookups so we never ask the LLM «какой знак 13 февраля?» /
«чей год 1990?». Feeds matrix slot ``cultural_catalog`` + sun/element keys.

SoT: docs/PRODUCT_AVAILABILITY_MATRIX.md §3.1 шапка · PRODUCT_DATA_PROVIDERS §0
"""

from __future__ import annotations

from datetime import date
from typing import Any

from todayflow_backend.data.astrology import sign_for_date
from todayflow_backend.services.chinese_horoscope import get_chinese_horoscope_service
from todayflow_backend.services.tibetan_horoscope import get_tibetan_horoscope_service

PACK_VERSION = "profile_header_knowledge_v0.1"

# Accumulated catalog: tropical sign → signature color (Profile шапка only — not «цвет дня»).
_SIGN_COLORS_RU: dict[str, str] = {
    "aries": "алый",
    "taurus": "изумрудный",
    "gemini": "лимонно-жёлтый",
    "cancer": "перламутрово-серебристый",
    "leo": "золотой",
    "virgo": "оливковый",
    "libra": "розово-пудровый",
    "scorpio": "бордовый",
    "sagittarius": "королевский синий",
    "capricorn": "графитовый",
    "aquarius": "электрик",
    "pisces": "морской бирюзовый",
}

_SIGN_RU: dict[str, str] = {
    "aries": "Овен",
    "taurus": "Телец",
    "gemini": "Близнецы",
    "cancer": "Рак",
    "leo": "Лев",
    "virgo": "Дева",
    "libra": "Весы",
    "scorpio": "Скорпион",
    "sagittarius": "Стрелец",
    "capricorn": "Козерог",
    "aquarius": "Водолей",
    "pisces": "Рыбы",
}

_ELEMENT_RU: dict[str, str] = {
    "fire": "огонь",
    "earth": "земля",
    "air": "воздух",
    "water": "вода",
    "wood": "дерево",
    "metal": "металл",
    "iron": "железо",
}

_STONE_RU: dict[str, str] = {
    "carnelian": "сердолик",
    "diamond": "алмаз",
    "emerald": "изумруд",
    "rose_quartz": "розовый кварц",
    "agate": "агат",
    "citrine": "цитрин",
    "moonstone": "лунный камень",
    "pearl": "жемчуг",
    "sunstone": "солнечный камень",
    "peridot": "хризолит",
    "sapphire": "сапфир",
    "jade": "нефрит",
    "opal": "опал",
    "lapis": "лазурит",
    "lapis_lazuli": "лазурит",
    "topaz": "топаз",
    "amethyst": "аметист",
    "garnet": "гранат",
    "turquoise": "бирюза",
    "aquamarine": "аквамарин",
}

_ANIMAL_RU: dict[str, str] = {
    "rat": "Крыса",
    "mouse": "Мышь",
    "ox": "Бык",
    "tiger": "Тигр",
    "rabbit": "Кролик",
    "dragon": "Дракон",
    "snake": "Змея",
    "horse": "Лошадь",
    "goat": "Коза",
    "sheep": "Овца",
    "monkey": "Обезьяна",
    "rooster": "Петух",
    "bird": "Птица",
    "dog": "Собака",
    "pig": "Свинья",
}


def _label_stone(key: str) -> str:
    return _STONE_RU.get(key.strip().lower().replace(" ", "_"), key.replace("_", " "))


def _label_animal(key: str) -> str:
    return _ANIMAL_RU.get(key.strip().lower(), key)


def _label_element(key: str) -> str:
    return _ELEMENT_RU.get(key.strip().lower(), key)


def build_profile_header_knowledge(
    birth_date: date | str | None,
    *,
    life_path: int | None = None,
    birthday_number: int | None = None,
    locale: str = "ru",
) -> dict[str, Any] | None:
    """Deterministic header pack for Profile шапка. None if no birth date."""
    if birth_date is None:
        return None
    if isinstance(birth_date, str):
        try:
            birth = date.fromisoformat(birth_date.strip()[:10])
        except ValueError:
            return None
    else:
        birth = birth_date

    sign = sign_for_date(birth)
    if not sign:
        return None

    sign_id = str(sign.get("id") or "").strip().lower()
    if not sign_id:
        return None

    stones_raw = [str(s) for s in (sign.get("stones") or []) if s]
    stones = [{"id": s, "label": _label_stone(s)} for s in stones_raw]
    color = _SIGN_COLORS_RU.get(sign_id)
    element = str(sign.get("element") or "").strip().lower() or None

    chinese = get_chinese_horoscope_service().calculate(birth)
    tibetan = get_tibetan_horoscope_service().calculate(birth)

    traditions: list[dict[str, Any]] = [
        {
            "id": "tropical_western",
            "label": "Западный (тропический)",
            "value": _SIGN_RU.get(sign_id, sign.get("name") or sign_id),
            "value_id": sign_id,
        },
        {
            "id": "chinese",
            "label": "Китайский",
            "value": f"{_label_animal(str(chinese.get('animal') or ''))}"
            + (f" · {_label_element(str(chinese.get('element') or ''))}" if chinese.get("element") else ""),
            "value_id": str(chinese.get("animal") or "").lower() or None,
            "element": chinese.get("element"),
            "chinese_year": chinese.get("chinese_year"),
        },
        {
            "id": "tibetan",
            "label": "Тибетский",
            "value": f"{_label_animal(str(tibetan.get('animal') or ''))}"
            + (f" · {_label_element(str(tibetan.get('element') or ''))}" if tibetan.get("element") else ""),
            "value_id": str(tibetan.get("animal") or "").lower() or None,
            "element": tibetan.get("element"),
            "mewa": tibetan.get("mewa"),
        },
    ]

    pack: dict[str, Any] = {
        "pack_version": PACK_VERSION,
        "source": "deterministic_catalog",
        "birth_date": birth.isoformat(),
        "tropical_sign": {
            "id": sign_id,
            "label": _SIGN_RU.get(sign_id, sign.get("name")),
            "element": element,
            "element_label": _label_element(element) if element else None,
            "modality": sign.get("modality"),
            "rulers": list(sign.get("rulers") or []),
            "themes": list(sign.get("themes") or []),
        },
        "correspondences": {
            "color": color,
            "stones": stones,
        },
        "traditions": traditions,
        "numerology_core": {
            "life_path": life_path,
            "birthday_number": birthday_number,
        },
        "locale": (locale or "ru")[:8],
    }
    # Drop empty numerology bag
    if life_path is None and birthday_number is None:
        pack["numerology_core"] = None
    return pack


def header_pack_to_matrix_catalog(pack: dict[str, Any] | None) -> dict[str, Any] | None:
    """Shape for profile_matrix_adapter ``catalog=`` / slot cultural_catalog."""
    if not isinstance(pack, dict):
        return None
    corr = pack.get("correspondences") if isinstance(pack.get("correspondences"), dict) else {}
    stones = corr.get("stones") if isinstance(corr.get("stones"), list) else []
    if not pack.get("traditions") and not corr.get("color") and not stones:
        return None
    return {
        "pack_version": pack.get("pack_version"),
        "tropical_sign": pack.get("tropical_sign"),
        "color": corr.get("color"),
        "stones": stones,
        "traditions": pack.get("traditions") or [],
        "numerology_core": pack.get("numerology_core"),
    }
