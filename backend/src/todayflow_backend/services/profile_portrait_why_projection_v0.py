"""Deterministic Profile Step-2 «why» projection (selected_by vs portrait_influenced_by).

SoT: docs/profile/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md § Шаг 2
No Snapshot fields — computed on read from existing core facts (like natal_summary).
Production truth: archetype_seed is selected only from life_path (core_profile._build_baseline).
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.natal_chart_personalization import _sign_label_prepositional
from todayflow_backend.services.profile_baseline_archetype_v0 import archetype_seed_from_life_path

PROJECTION_VERSION = "profile_portrait_why_v0.1"
TITLE_RU = "Почему портрет звучит именно так"
HONESTY_NO_TIME_RU = (
    "Без времени рождения пока не видны ASC и дома — они покажут, "
    "как эти качества проявляются во внешнем поведении и отдельных сферах жизни."
)

_ARCHETYPE_LABEL_RU: dict[str, str] = {
    "architect": "Архитектор",
    "harmonizer": "Гармонизатор",
    "explorer": "Исследователь",
    "sage": "Мудрец",
    "observer": "Наблюдатель",
}

_ELEMENT_LABEL_RU: dict[str, str] = {
    "fire": "огонь",
    "earth": "земля",
    "air": "воздух",
    "water": "вода",
}


def _archetype_label_ru(seed: str | None) -> str:
    key = str(seed or "").strip().lower()
    return _ARCHETYPE_LABEL_RU.get(key) or (str(seed).strip() if seed else "")


def _element_label_ru(element: str | None) -> str | None:
    if not element:
        return None
    key = str(element).strip().lower()
    return _ELEMENT_LABEL_RU.get(key) or key


def _birth_time_known(astro: dict[str, Any]) -> bool:
    if bool(astro.get("time_unknown")):
        return False
    birth_time = astro.get("birth_time")
    return bool(birth_time)


def _moon_sign_from_natal(natal_summary: dict[str, Any] | None) -> str | None:
    if not isinstance(natal_summary, dict) or not natal_summary.get("available"):
        return None
    for row in natal_summary.get("luminaries") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("name") or "").strip().lower() == "moon" and row.get("sign"):
            return str(row.get("sign"))
    for row in natal_summary.get("personal_planets") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("name") or "").strip().lower() == "moon" and row.get("sign"):
            return str(row.get("sign"))
    return None


def _angle_sign(natal_summary: dict[str, Any] | None, key: str) -> str | None:
    if not isinstance(natal_summary, dict) or not natal_summary.get("available"):
        return None
    angles = natal_summary.get("angles") if isinstance(natal_summary.get("angles"), dict) else {}
    raw = angles.get(key)
    return str(raw).strip() if raw else None


def project_portrait_why_v0(
    *,
    numerology: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
    astro: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    """Build Step-2 checklist from existing facts. Never invents ASC/MC without time."""
    _ = locale  # RU product surface for Profile Freeze; EN labels later if needed
    num = numerology if isinstance(numerology, dict) else {}
    base = baseline if isinstance(baseline, dict) else {}
    ast = astro if isinstance(astro, dict) else {}

    selected_by: list[dict[str, Any]] = []
    influenced_by: list[dict[str, Any]] = []
    omitted: list[dict[str, Any]] = []

    life_path = num.get("life_path")
    seed = str(base.get("archetype_seed") or "").strip() or None
    if seed is None and life_path is not None:
        seed = archetype_seed_from_life_path(life_path)

    if life_path is not None and seed:
        label_ru = _archetype_label_ru(seed)
        selected_by.append(
            {
                "id": "archetype_from_life_path",
                "class": "selected_by",
                "fact_keys": ["numerology.life_path", "baseline.archetype_seed"],
                "life_path": life_path,
                "archetype_seed": seed,
                "label": f"Архетип {label_ru} — рассчитан из числа пути {life_path}",
            }
        )

    sun = ast.get("sun_sign")
    if sun:
        prep = _sign_label_prepositional(str(sun))
        influenced_by.append(
            {
                "id": "sun",
                "class": "portrait_influenced_by",
                "fact_keys": ["astro.sun_sign"],
                "value": sun,
                "label": f"Солнце в {prep}",
            }
        )

    element = _element_label_ru(ast.get("sun_element"))
    if element:
        influenced_by.append(
            {
                "id": "element",
                "class": "portrait_influenced_by",
                "fact_keys": ["astro.sun_element"],
                "value": ast.get("sun_element"),
                "label": f"Стихия — {element}",
            }
        )

    rhythm = str(base.get("rhythm_style") or "").strip()
    if rhythm:
        # Exact baseline fact — do not invent a shorter gloss in the projector.
        influenced_by.append(
            {
                "id": "rhythm",
                "class": "portrait_influenced_by",
                "fact_keys": ["baseline.rhythm_style"],
                "value": rhythm,
                "label": f"Ритм — {rhythm[0].lower() + rhythm[1:] if rhythm else rhythm}",
            }
        )

    moon = _moon_sign_from_natal(natal_summary)
    if moon:
        influenced_by.append(
            {
                "id": "moon",
                "class": "portrait_influenced_by",
                "fact_keys": ["natal_summary.luminaries.moon"],
                "value": moon,
                "label": f"Луна в {_sign_label_prepositional(moon)}",
            }
        )

    time_known = _birth_time_known(ast)
    rising = _angle_sign(natal_summary, "ascendant_sign") if time_known else None
    mc = _angle_sign(natal_summary, "midheaven_sign") if time_known else None

    if rising:
        influenced_by.append(
            {
                "id": "asc",
                "class": "portrait_influenced_by",
                "fact_keys": ["natal_summary.angles.ascendant_sign"],
                "value": rising,
                "label": f"ASC в {_sign_label_prepositional(rising)}",
            }
        )
    else:
        omitted.append(
            {
                "id": "asc",
                "reason": "birth_time_unknown" if not time_known else "asc_unavailable",
                "opens": "ASC и вход во внешнее поведение",
            }
        )

    if mc:
        influenced_by.append(
            {
                "id": "mc",
                "class": "portrait_influenced_by",
                "fact_keys": ["natal_summary.angles.midheaven_sign"],
                "value": mc,
                "label": f"MC в {_sign_label_prepositional(mc)}",
            }
        )
    else:
        omitted.append(
            {
                "id": "mc",
                "reason": "birth_time_unknown" if not time_known else "mc_unavailable",
                "opens": "MC и дома / сферы проявления",
            }
        )

    honesty_line = HONESTY_NO_TIME_RU if not time_known else None

    return {
        "projection_version": PROJECTION_VERSION,
        "title": TITLE_RU,
        "selected_by": selected_by,
        "portrait_influenced_by": influenced_by,
        "omitted": omitted,
        "honesty_line": honesty_line,
        # Guardrail for consumers: never treat influenced_by as archetype selectors.
        "rules": {
            "archetype_selected_only_by": "numerology.life_path",
            "forbid_sun_as_archetype_cause": True,
        },
    }


def attach_portrait_why_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Ephemeral read-path attach — must not be written into Snapshot."""
    if not isinstance(payload, dict):
        return payload
    payload["portrait_why_v0"] = project_portrait_why_v0(
        numerology=payload.get("numerology") if isinstance(payload.get("numerology"), dict) else None,
        baseline=payload.get("baseline") if isinstance(payload.get("baseline"), dict) else None,
        astro=payload.get("astro") if isinstance(payload.get("astro"), dict) else None,
        natal_summary=payload.get("natal_summary") if isinstance(payload.get("natal_summary"), dict) else None,
        locale=str((payload.get("person") or {}).get("locale") or "ru")
        if isinstance(payload.get("person"), dict)
        else "ru",
    )
    return payload
