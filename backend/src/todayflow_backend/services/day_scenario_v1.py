"""day_scenario_v1 — central day dramaturgy contract (Phase B engine).

Source of Truth (runtime B5):
  facts → interpretive chorus → conflict → scenes → props → UI projections

B1: foundation, chorus, conflict, scenes.
B2: props-from-scenes (color/avoid/goals/affirm/humor) — catalog knowledge only.
B3–B4: wire projection + FE preference.
B5: ``runtime_sot=True`` — exclusive meaning SoT; legacy slots are projections only.

Canon: docs/DAY_SCENARIO_V1.md
"""

from __future__ import annotations

import re
from typing import Any

DAY_SCENARIO_V1_CONTRACT = "day_scenario_v1"
DAY_SCENARIO_V1_VERSION = "day-scenario-v1.2-b5-runtime-sot"

# Product spheres (Act V). Not all appear every day.
PRODUCT_SPHERE_IDS: tuple[str, ...] = (
    "work_decisions",
    "relationships",
    "communication",
    "money",
    "energy_body",
    "creativity",
    "home",
    "rest_travel",
)

WIRE_DOMAIN_TO_SPHERES: dict[str, tuple[str, ...]] = {
    "money_work": ("work_decisions", "money"),
    "relationships": ("relationships", "communication"),
    "family": ("home", "relationships"),
}

# thesis family → default spheres when domain evidence is thin
_FAMILY_SPHERES: dict[str, tuple[str, ...]] = {
    "decision": ("work_decisions", "communication"),
    "communication": ("communication", "relationships"),
    "change": ("work_decisions", "rest_travel", "energy_body"),
    "pressure": ("work_decisions", "energy_body", "home"),
    "momentum": ("work_decisions", "creativity"),
    "connection": ("relationships", "communication"),
}

_SPHERE_LABEL_RU: dict[str, str] = {
    "work_decisions": "Работа и решения",
    "relationships": "Отношения",
    "communication": "Общение",
    "money": "Деньги",
    "energy_body": "Энергия и тело",
    "creativity": "Творчество",
    "home": "Дом",
    "rest_travel": "Отдых и поездки",
}

# Number → how to live the conflict (tempo / measure), not a second forecast
_NUMBER_TEMPO_RU: dict[int, dict[str, str]] = {
    1: {
        "tempo": "инициатива",
        "style": "один ясный старт",
        "lesson": "не ждать разрешения снаружи",
        "initiative": "высокая, но точечная",
        "closure": "закрыть день видимым первым шагом",
    },
    2: {
        "tempo": "диалог",
        "style": "пара, а не толпа",
        "lesson": "слушать до ответа",
        "initiative": "умеренная — после контакта",
        "closure": "зафиксировать договорённость",
    },
    3: {
        "tempo": "выражение",
        "style": "сказать вслух, не копить",
        "lesson": "форма важна не меньше смысла",
        "initiative": "лёгкая, игрово-творческая",
        "closure": "оставить след — сообщение, набросок, жест",
    },
    4: {
        "tempo": "структура",
        "style": "порядок и границы",
        "lesson": "опора важнее скорости",
        "initiative": "сдержанная, по плану",
        "closure": "закрыть контур, не открывать новый",
    },
    5: {
        "tempo": "движение",
        "style": "смена угла, не смена жизни",
        "lesson": "свобода без разрушения",
        "initiative": "средняя — один эксперимент",
        "closure": "отметить, что изменилось",
    },
    6: {
        "tempo": "забота",
        "style": "близкий круг и ответственность",
        "lesson": "не раствориться в чужом",
        "initiative": "мягкая, сервисная",
        "closure": "тепло без самоотречения",
    },
    7: {
        "tempo": "глубина",
        "style": "пауза, анализ, тишина",
        "lesson": "не заполнять пустоту шумом",
        "initiative": "низкая снаружи, высокая внутри",
        "closure": "одна честная формулировка для себя",
    },
    8: {
        "tempo": "сила",
        "style": "решение и ресурс",
        "lesson": "власть без давления",
        "initiative": "высокая — с мерой",
        "closure": "зафиксировать результат или отказ",
    },
    9: {
        "tempo": "завершение",
        "style": "отпустить и собрать смысл",
        "lesson": "не тащить вчерашнее в завтра",
        "initiative": "завершающая, не стартовая",
        "closure": "ритуал окончания — список, прощание, архив",
    },
}


def _clip(value: Any, n: int = 400) -> str:
    text = str(value or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _event_by_id(pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for ev in _as_list(pack.get("events")):
        if isinstance(ev, dict) and ev.get("id"):
            out[str(ev["id"])] = ev
    return out


def _driver_rows(pack: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = _event_by_id(pack)
    rows: list[dict[str, Any]] = []
    for did in _as_list(pack.get("ranked_drivers"))[:3]:
        eid = str(did)
        ev = by_id.get(eid) or {}
        rows.append(
            {
                "id": eid,
                "kind": ev.get("kind"),
                "title_ru": ev.get("title_ru"),
                "fact_ru": ev.get("fact_ru") or ev.get("title_ru") or eid,
                "strength": ev.get("strength"),
                "body": ev.get("body"),
                "sign": ev.get("sign"),
                "aspect": ev.get("aspect"),
                "evidence_ref": f"event:{eid}",
            }
        )
    return rows


def _claims_by_prefix(claims: list[Any], prefix: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in claims:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id") or "")
        if cid.startswith(prefix):
            out.append(c)
    return out


def build_scenario_foundation_v1(
    *,
    interpretation: dict[str, Any] | None = None,
    day_events_pack: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Facts and computed data — not user-facing prose."""
    interp = _as_dict(interpretation)
    pack = day_events_pack if isinstance(day_events_pack, dict) else _as_dict(interp.get("day_events_pack"))
    ritual = _as_dict(ritual_context)
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    foundation_nest = _as_dict(interp.get("day_foundation"))
    personal_nest = _as_dict(interp.get("day_personal"))
    claims = _as_list(interp.get("derived_claims"))
    evidence = _as_list(interp.get("evidence"))

    drivers = _driver_rows(pack)
    astronomy: list[dict[str, Any]] = []
    astrology: list[dict[str, Any]] = []
    for row in drivers:
        kind = str(row.get("kind") or "")
        item = {
            "id": row["id"],
            "label_ru": row.get("fact_ru"),
            "kind": kind,
            "strength": row.get("strength"),
            "evidence_ref": row.get("evidence_ref"),
        }
        if kind in {"lunar_phase", "eclipse", "ingress", "moon_ingress"} or "moon" in kind:
            astronomy.append(item)
            astrology.append(item)
        else:
            astrology.append(item)

    # Extra sky from celestial if pack thin
    if not astronomy:
        lunar = _as_dict(ce.get("lunar_phase") or _as_dict(interp.get("day_sky")).get("lunar_phase"))
        if lunar.get("name"):
            astronomy.append(
                {
                    "id": "lunar_phase",
                    "label_ru": lunar.get("name"),
                    "kind": "lunar_phase",
                    "guidance": lunar.get("guidance"),
                    "evidence_ref": "celestial.lunar_phase",
                }
            )

    natal_activations: list[dict[str, Any]] = []
    # Wave2 single pool: geometric activations on celestial_events (from compute_natal_activations).
    geo = _as_list(ce.get("natal_activations"))
    if geo:
        from todayflow_backend.services.today_natal_activations_v1 import (
            foundation_rows_from_activations,
        )

        natal_activations = foundation_rows_from_activations(geo)
    if not natal_activations:
        for c in _claims_by_prefix(claims, "claim.personal."):
            natal_activations.append(
                {
                    "id": c.get("id"),
                    "text": _clip(c.get("text"), 280),
                    "evidence_ids": list(c.get("evidence_ids") or []),
                    "layer": c.get("layer") or "personal",
                }
            )
    if not natal_activations and personal_nest:
        natal_activations.append(
            {
                "id": "day_personal.summary",
                "text": _clip(personal_nest.get("summary") or personal_nest.get("dynamic") or "", 280),
                "evidence_ids": [],
                "layer": "personal",
            }
        )

    card_name = str(ritual.get("tarot_name_ru") or ritual.get("tarot_main_id") or "").strip() or None
    if not card_name:
        for c in claims:
            if isinstance(c, dict) and str(c.get("id") or "") == "claim.day_card":
                card_name = _clip(c.get("text"), 120) or None
                break

    number_val: int | str | None = None
    if ritual.get("numerology_value") is not None:
        try:
            number_val = int(ritual.get("numerology_value"))
        except (TypeError, ValueError):
            number_val = str(ritual.get("numerology_value"))
    num_block = _as_dict(foundation_nest.get("numerology"))
    if number_val is None and num_block.get("personal_day") is not None:
        number_val = num_block.get("personal_day")
    elif number_val is None and num_block.get("universal_day") is not None:
        number_val = num_block.get("universal_day")

    cycles: list[dict[str, Any]] = []
    weekday = _as_dict(foundation_nest.get("weekday"))
    if weekday:
        cycles.append(
            {
                "id": "weekday",
                "label_ru": weekday.get("name_ru") or weekday.get("ruler_planet"),
                "evidence_ref": "day_foundation.weekday",
            }
        )
    seasonal = _as_dict(foundation_nest.get("seasonal"))
    if seasonal:
        cycles.append(
            {
                "id": "seasonal",
                "label_ru": seasonal.get("summary_ru") or seasonal.get("name"),
                "evidence_ref": "day_foundation.seasonal",
            }
        )

    confidence = interp.get("confidence")
    if not isinstance(confidence, (int, float)):
        confidence = 0.55 if drivers else 0.35

    return {
        "contract_version": "day_scenario_foundation_v1",
        "ranked_drivers": drivers,
        "astronomy_facts": astronomy,
        "astrology_facts": astrology,
        "personal_natal_activations": [a for a in natal_activations if a.get("text")],
        "tarot_card": {
            "name": card_name,
            "id": ritual.get("tarot_main_id"),
            "present": bool(card_name),
            "evidence_ref": "ritual.tarot" if card_name else None,
        },
        "day_number": {
            "value": number_val,
            "personal_day": num_block.get("personal_day"),
            "universal_day": num_block.get("universal_day"),
            "present": number_val is not None,
            "evidence_ref": "ritual.numerology" if ritual.get("numerology_value") is not None else "day_foundation.numerology",
        },
        "cycles": cycles,
        "confidence": float(confidence),
        "evidence_references": [
            {"id": e.get("id"), "source": e.get("source"), "text": _clip(e.get("text") or e.get("fact_ru"), 160)}
            for e in evidence
            if isinstance(e, dict)
        ][:40],
        "limitations": list(interp.get("limitations") or []),
    }


def _human_meaning_for_driver(row: dict[str, Any], conflict_label: str) -> str:
    fact = _clip(row.get("fact_ru") or row.get("title_ru"), 200)
    if not fact:
        return f"Фактор дня усиливает линию «{conflict_label}»."
    return f"{fact} Это подталкивает день к сюжету «{conflict_label}»."


def _card_archetype_voice(card_name: str, conflict_label: str) -> dict[str, str]:
    name = card_name.strip()
    return {
        "named": f"Карта дня — {name}",
        "role_for_conflict": (
            f"Архетип «{name}» лучше всего описывает, какой ролью пройти «{conflict_label}» — "
            f"не как отдельный прогноз, а как способ отношения к уже названному конфликту."
        ),
        "hidden_side": f"«{name}» может открыть скрытую сторону того же конфликта, а не новую тему дня.",
        "way_to_relate": f"Проживите день в ключе «{name}»: держите одну роль, не собирайте второй сюжет.",
    }


def _number_voice(value: Any, conflict_label: str) -> dict[str, Any]:
    try:
        n = int(value) % 9 or 9
    except (TypeError, ValueError):
        n = 0
    tempo = _NUMBER_TEMPO_RU.get(n) or {
        "tempo": "ровный",
        "style": "без лишних параллельных сюжетов",
        "lesson": "держаться одной линии",
        "initiative": "умеренная",
        "closure": "закрыть день осознанно",
    }
    return {
        "named": f"Число дня — {value}",
        "reduced": n or None,
        **tempo,
        "for_conflict": (
            f"Число {value} окрашивает прохождение «{conflict_label}»: "
            f"темп — {tempo['tempo']}, способ — {tempo['style']}."
        ),
    }


def build_interpretive_chorus_v1(
    *,
    foundation: dict[str, Any],
    conflict_label: str,
    interpretation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Four voices for one story — explain, do not compete."""
    interp = _as_dict(interpretation)
    claims = _as_list(interp.get("derived_claims"))
    label = conflict_label or "главный сюжет дня"

    astrology_voices: list[dict[str, Any]] = []
    for row in _as_list(foundation.get("ranked_drivers")) or _as_list(foundation.get("astrology_facts")):
        if not isinstance(row, dict):
            continue
        fact = _clip(row.get("fact_ru") or row.get("label_ru") or row.get("title_ru"), 220)
        if not fact or _is_calendar_kitchen_fact(fact):
            continue
        astrology_voices.append(
            {
                "voice": "astrology",
                "named_factor": fact,
                "human_meaning": _human_meaning_for_driver(row, label),
                "link_to_conflict": f"Объясняет, почему сегодня в центре «{label}».",
                "evidence_ref": row.get("evidence_ref") or row.get("id"),
                "driver_id": row.get("id"),
            }
        )

    card = _as_dict(foundation.get("tarot_card"))
    card_voice = None
    if card.get("present") and card.get("name"):
        voices = _card_archetype_voice(str(card["name"]), label)
        card_voice = {
            "voice": "day_card",
            "named_factor": voices["named"],
            "archetype_role": voices["role_for_conflict"],
            "hidden_side": voices["hidden_side"],
            "way_to_relate": voices["way_to_relate"],
            "link_to_conflict": voices["role_for_conflict"],
            "human_meaning": voices["way_to_relate"],
            "evidence_ref": card.get("evidence_ref"),
            "is_not_astro_proof": True,
            "must_not_invent_second_plot": True,
        }

    number = _as_dict(foundation.get("day_number"))
    number_voice = None
    if number.get("present") and number.get("value") is not None:
        nv = _number_voice(number.get("value"), label)
        number_voice = {
            "voice": "day_number",
            "named_factor": nv["named"],
            "tempo": nv.get("tempo"),
            "style": nv.get("style"),
            "lesson": nv.get("lesson"),
            "initiative": nv.get("initiative"),
            "closure": nv.get("closure"),
            "link_to_conflict": nv["for_conflict"],
            "human_meaning": nv["for_conflict"],
            "evidence_ref": number.get("evidence_ref"),
            "must_not_invent_second_plot": True,
        }

    natal_voices: list[dict[str, Any]] = []
    for act in _as_list(foundation.get("personal_natal_activations")):
        if not isinstance(act, dict) or not act.get("text"):
            continue
        raw = str(act.get("text") or "").strip()
        if _is_kitchen_natal_text(raw):
            # Keep evidence in kitchen; never dump Firdaria/ZR lists into UI chorus.
            continue
        natal_voices.append(
            {
                "voice": "natal",
                "named_factor": _clip(raw, 200),
                "human_meaning": (
                    f"Личная активация усиливает «{label}»: реакция может быть сильнее средней."
                ),
                "link_to_conflict": f"Почему именно вы проживаете «{label}» именно так.",
                "evidence_ref": act.get("id"),
                "evidence_ids": list(act.get("evidence_ids") or []),
            }
        )
    if not natal_voices and any(
        isinstance(a, dict) and a.get("text")
        for a in _as_list(foundation.get("personal_natal_activations"))
    ):
        # Soft personal voice without mechanism dump when only kitchen claims exist.
        natal_voices.append(
            {
                "voice": "natal",
                "named_factor": f"Ваш личный фон усиливает «{label}».",
                "human_meaning": (
                    "Реакция сегодня может быть сильнее средней — это про вас, не про «всех»."
                ),
                "link_to_conflict": f"Почему именно вы проживаете «{label}» именно так.",
                "evidence_ref": "personal_natal:soft",
                "evidence_ids": [],
            }
        )
    if not natal_voices:
        for c in _claims_by_prefix(claims, "claim.personal.")[:3]:
            raw = str(c.get("text") or "").strip()
            if not raw or _is_kitchen_natal_text(raw):
                continue
            natal_voices.append(
                {
                    "voice": "natal",
                    "named_factor": _clip(raw, 200),
                    "human_meaning": f"Натальный слой делает «{label}» личным.",
                    "link_to_conflict": f"Почему «{label}» задевает именно вас.",
                    "evidence_ref": c.get("id"),
                    "evidence_ids": list(c.get("evidence_ids") or []),
                }
            )

    return {
        "contract_version": "day_scenario_chorus_v1",
        "astrology": astrology_voices,
        "day_card": card_voice,
        "day_number": number_voice,
        "natal": natal_voices,
        "dialogue_rule": (
            "Четыре взгляда на одну историю: астрология — что снаружи; "
            "карта — архетип; число — темп; натал — почему вам."
        ),
        "named_language_encouraged": True,
        "parallel_forecast_forbidden": True,
    }


# Kitchen / mechanism natal prose — never user-facing on Today.
_KITCHEN_NATAL_RE = re.compile(
    r"Firdaria|ZR\s*Fortune|ZR\s*Spirit|Лоты\s*soft|Vimshottari|BaZi|"
    r"HD\s*soft|Variables\s*soft|Solar\s*return|time[_\s-]?lords|"
    r"управител|прогрес+и|нет\s+ASC|soft:\s*Луна",
    re.IGNORECASE,
)

# Cached mash: "Force A или Force B — пока <truncated fact…>"
# Also strip calendar-day kitchen facts glued after an em dash.
_MASHED_SHORT_NAME_RE = re.compile(
    r"^(.+?\s+или\s+.+?)\s+[—–-]\s+(?:пока\s+|календарн)",
    re.IGNORECASE,
)
_CALENDAR_FACT_RE = re.compile(
    r"календарн\w*\s+день|"
    r"\d+-й\s+день\s+года|"
    r"день\s+года\s+\d+|"
    r"calendar-doy",
    re.IGNORECASE,
)


def _is_kitchen_natal_text(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    return bool(_KITCHEN_NATAL_RE.search(t))


def is_calendar_kitchen_fact(text: str) -> bool:
    """Calendar DOY lines are kitchen — date already lives in UI chrome."""
    return bool(_CALENDAR_FACT_RE.search(text or ""))


def is_calendar_driver_row(row: dict[str, Any] | None) -> bool:
    if not isinstance(row, dict):
        return False
    rid = str(row.get("id") or row.get("driver_id") or "")
    kind = str(row.get("kind") or "")
    if rid.startswith("calendar-doy") or kind == "calendar":
        return True
    return is_calendar_kitchen_fact(
        str(row.get("fact_ru") or row.get("title_ru") or row.get("named_factor") or "")
    )


# Back-compat aliases used inside this module
_is_calendar_kitchen_fact = is_calendar_kitchen_fact
_is_calendar_driver_row = is_calendar_driver_row


def sanitize_conflict_short_name(value: Any) -> str:
    """User-facing conflict label: tension only, no mashed truncated sky fact."""
    text = str(value or "").strip()
    if not text:
        return ""
    mashed = _MASHED_SHORT_NAME_RE.match(text)
    if mashed:
        text = mashed.group(1).strip()
    # Any leftover "— пока …" / calendar glue after tension label
    if " или " in text.lower() and re.search(r"\s+[—–-]\s+", text):
        before, after = re.split(r"\s+[—–-]\s+", text, maxsplit=1)
        if " или " in before.lower() and (
            after.lower().startswith("пока")
            or _is_calendar_kitchen_fact(after)
            or "…" in after
        ):
            text = before.strip()
    if "…" in text and " или " in text.lower():
        before = re.split(r"\s+[—–-]\s+", text, maxsplit=1)[0].strip()
        if " или " in before.lower():
            text = before
    return _clip(text, 72)


def _opposing_forces(family: str, mode: str) -> tuple[str, str]:
    pairs: dict[str, tuple[str, str]] = {
        "decision": ("угодить всем", "выбрать своё"),
        "communication": ("сгладить", "сказать прямо"),
        "change": ("удержать привычное", "принять поворот"),
        "pressure": ("сорваться", "удержать меру"),
        "momentum": ("распылиться", "держать ритм"),
        "connection": ("закрыться", "войти в контакт"),
    }
    a, b = pairs.get(family, ("автопилот", "осознанный выбор"))
    if mode == "opportunity":
        return ("упустить окно", "сделать один ясный шаг")
    if mode == "recovery":
        return ("тащить старое", "отпустить и восстановиться")
    if mode == "stability":
        return ("ломать работающее", "беречь ровный ритм")
    return (a, b)


def _everyday_conflict_short_name(
    *,
    force_a: str,
    force_b: str,
    lead_fact: str,
    registry_label: str,
) -> str:
    """Hero conflict = everyday tension only.

    Sky fact belongs in ``why_arose`` / ``events_lead`` / chorus — never mashed
    into ``short_name`` (that produced truncated hero copy: «… к це…»).
    """
    del lead_fact, registry_label  # kept in signature for call-site stability
    a = _clip(force_a, 48) or "автопилот"
    b = _clip(force_b, 48) or "осознанный выбор"
    return sanitize_conflict_short_name(f"{a.capitalize()} или {b}")


def _human_natal_why(
    natal_activations: list[Any],
    *,
    conflict_label: str,
) -> str:
    """Pick first non-kitchen natal activation for why_personal."""
    label = conflict_label or "этот сюжет"
    for act in natal_activations:
        if not isinstance(act, dict):
            continue
        text = str(act.get("text") or "").strip()
        if text and not _is_kitchen_natal_text(text):
            return _clip(text, 220)
    return (
        f"Личный ритм делает сюжет «{label}» узнаваемым именно вам — "
        "не средним прогнозом на всех."
    )


def build_scenario_conflict_v1(
    *,
    foundation: dict[str, Any],
    day_thesis: dict[str, Any] | None = None,
    interpretation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One central conflict. Foundation = drivers + natal; card/number only refine reading."""
    interp = _as_dict(interpretation)
    thesis = day_thesis if isinstance(day_thesis, dict) else _as_dict(interp.get("day_thesis"))
    if not thesis.get("family"):
        # last resort from primary_conflict alias
        pc = interp.get("primary_conflict")
        if isinstance(pc, dict):
            thesis = _as_dict(pc.get("day_thesis")) or {
                "family": "momentum",
                "variant": "steady_productive_rhythm",
                "mode": "stability",
                "label_ru": pc.get("label_ru") or "Ровный день",
                "driver_ids": list(pc.get("driver_ids") or []),
            }
        elif isinstance(pc, str) and pc.strip():
            thesis = {
                "family": "momentum",
                "variant": "steady_productive_rhythm",
                "mode": "stability",
                "label_ru": pc.strip(),
                "driver_ids": [d.get("id") for d in _as_list(foundation.get("ranked_drivers")) if isinstance(d, dict)],
            }

    family = str(thesis.get("family") or "momentum")
    variant = str(thesis.get("variant") or "steady_productive_rhythm")
    mode = str(thesis.get("mode") or "stability")
    registry_label = str(thesis.get("label_ru") or thesis.get("label") or "").strip()
    # Wave 2 D.2b: conflict.driver_ids SoT = natal pt-* when present; pack stays on foundation.
    from todayflow_backend.services.today_natal_activations_v1 import natal_conflict_driver_ids

    natal_driver_ids = natal_conflict_driver_ids(foundation.get("personal_natal_activations"))
    if natal_driver_ids:
        driver_ids = natal_driver_ids
    else:
        driver_ids = [str(x) for x in _as_list(thesis.get("driver_ids"))][:3]
        if not driver_ids:
            driver_ids = [
                str(d.get("id"))
                for d in _as_list(foundation.get("ranked_drivers"))
                if isinstance(d, dict) and d.get("id")
            ][:3]

    force_a, force_b = _opposing_forces(family, mode)
    why_arose_parts = [
        _clip(d.get("fact_ru"), 160)
        for d in _as_list(foundation.get("ranked_drivers"))
        if isinstance(d, dict)
        and d.get("fact_ru")
        and not _is_calendar_kitchen_fact(str(d.get("fact_ru") or ""))
    ][:2]
    why_arose = (
        " · ".join(why_arose_parts)
        if why_arose_parts
        else "Факты дня собирают одну линию напряжения / возможности."
    )
    lead_fact = why_arose_parts[0] if why_arose_parts else ""
    short_name = _everyday_conflict_short_name(
        force_a=force_a,
        force_b=force_b,
        lead_fact=lead_fact,
        registry_label=registry_label,
    )

    natal = _as_list(foundation.get("personal_natal_activations"))
    why_personal = _human_natal_why(natal, conflict_label=short_name)

    chorus_refs: list[str] = []
    for d in driver_ids:
        chorus_refs.append(f"astrology:{d}")
    card = _as_dict(foundation.get("tarot_card"))
    if card.get("present"):
        chorus_refs.append("day_card")
    number = _as_dict(foundation.get("day_number"))
    if number.get("present"):
        chorus_refs.append("day_number")
    if natal:
        chorus_refs.append("natal")

    confidence = float(foundation.get("confidence") or 0.5)
    if not driver_ids:
        confidence = min(confidence, 0.4)

    return {
        "contract_version": "day_scenario_conflict_v1",
        "short_name": short_name,
        "thesis": {
            "family": family,
            "variant": variant,
            "mode": mode,
            # Act III registry seed — not the Level-1 plot title
            "label_ru": registry_label or short_name,
            "day_thesis": thesis,
            "act_iii_registry_label": registry_label or None,
        },
        "opposing_forces": {"a": force_a, "b": force_b},
        "why_arose": why_arose,
        "why_personal": why_personal,
        "driver_ids": driver_ids,
        "chorus_references": chorus_refs,
        "confidence": confidence,
        "foundation_rule": (
            "Conflict short_name is everyday tension from ranked facts + opposing forces; "
            "day_thesis.label_ru is Act III registry seed only. "
            "Card and number refine reading/tempo, never invent a rival plot."
        ),
    }


def _select_sphere_ids(
    *,
    family: str,
    domains_present: list[str],
    max_scenes: int = 4,
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    def add(sid: str) -> None:
        if sid in PRODUCT_SPHERE_IDS and sid not in seen:
            seen.add(sid)
            ordered.append(sid)

    for domain in domains_present:
        for sid in WIRE_DOMAIN_TO_SPHERES.get(domain, ()):
            add(sid)
    for sid in _FAMILY_SPHERES.get(family, ("work_decisions", "communication")):
        add(sid)
        if len(ordered) >= max_scenes:
            break
    if not ordered:
        add("work_decisions")
        add("communication")
    return ordered[:max_scenes]


def _scene_role(sphere_id: str, index: int) -> str:
    if index == 0:
        return "primary"
    if sphere_id in {"energy_body", "rest_travel", "home"}:
        return "support_or_risk"
    return "secondary"


def _person_first_name(person_name: str | None) -> str | None:
    raw = str(person_name or "").strip()
    if not raw:
        return None
    token = raw.split()[0].strip(".,;:!?«»\"'")
    return token[:40] if token else None


def _vocative_prefix(person_name: str | None) -> str:
    """«Игорь, …» — first name only; empty when unknown."""
    first = _person_first_name(person_name)
    return f"{first}, " if first else ""


# Lived beats per sphere. Conflict axis is already named in opening —
# do **not** paste force_a/force_b quotes into every scene line.
_SCENE_BEATS: dict[str, dict[str, str]] = {
    "work_decisions": {
        "what": "{who}в работе сегодня решающий жест — остаться в привычном контуре или сделать поворот.",
        "opportunity": "Одно письмо или решение без ожидания чужого одобрения.",
        "trap": "Снова отложить «на потом» и сделать вид, будто выбора нет.",
        "do": "Сделай один короткий шаг в сторону поворота — по делу, без оправданий.",
        "avoid": "Не соглашайся автоматом, лишь бы снять напряжение.",
        "domestic": "Письмо или звонок, который ты откладывал(а) из‑за чужой реакции.",
    },
    "relationships": {
        "what": "{who}в близких отношениях сегодня важнее не сохранить видимый мир, а сказать коротко и честно.",
        "opportunity": "Одна фраза вслух — без сглаживания и без разгона в спор.",
        "trap": "Снова сгладить ради тишины и потом нести тяжесть недосказанного.",
        "do": "Назови одну вещь прямо — коротко, без обвинения.",
        "avoid": "Не делай вид, что «всё нормально», если внутри уже нет.",
        "domestic": "Разговор, где важно не сгладить то, что лучше проговорить.",
    },
    "communication": {
        "what": "{who}в сообщениях сегодня скорость ответа спорит с ясностью смысла.",
        "opportunity": "Сначала смысл — потом кнопка «отправить».",
        "trap": "Ответить быстро, чтобы закрыть тему, и потерять суть.",
        "do": "Перечитай одно сообщение и убери лишнее до отправки.",
        "avoid": "Не ускоряй ответ ради чужого спокойствия.",
        "domestic": "Сообщение: сначала смысл, потом скорость ответа.",
    },
    "money": {
        "what": "{who}в деньгах сегодня легко купить спокойствие импульсом — или выдержать паузу.",
        "opportunity": "Одна трата или отказ: решение по смыслу, не по нерву.",
        "trap": "Потратить «чтобы стало легче» и усилить дыру.",
        "do": "Перед тратой спроси себя: это нужно или это анестезия?",
        "avoid": "Не покупай облегчение на автопилоте.",
        "domestic": "Трата или отказ: не покупать спокойствие импульсом.",
    },
    "energy_body": {
        "what": "{who}тело сегодня первым чувствует, где ты держишь лишнее напряжение.",
        "opportunity": "Пауза до усталости — вода, прогулка, сон без «ещё час».",
        "trap": "Дожать себя «ещё чуть‑чуть» и к вечеру остаться без ресурса.",
        "do": "Сделай одну короткую паузу до того, как тело потребует её криком.",
        "avoid": "Не откладывай отдых до полного выгорания.",
        "domestic": "Пауза до усталости — вода, прогулка, сон без «ещё один час».",
    },
    "creativity": {
        "what": "{who}в творчестве сегодня важнее живой черновик, чем идеальная форма.",
        "opportunity": "Набросок без требования шедевра — один конкретный жест.",
        "trap": "Ждать идеальных условий и так ничего не начать.",
        "do": "Сделай черновик на десять минут — без оценки.",
        "avoid": "Не требуй от первого шага законченного результата.",
        "domestic": "Набросок без требования шедевра.",
    },
    "home": {
        "what": "{who}дома сегодня один бытовой контур важнее «навести порядок везде».",
        "opportunity": "Один небольшой контур — стол, угол, список — доведённый до конца.",
        "trap": "Разбросаться на весь дом и закончить ничем.",
        "do": "Выбери один бытовой жест и закрой его сегодня.",
        "avoid": "Не начинай пять дел сразу «чтобы стало легче».",
        "domestic": "Один бытовой контур — не весь дом сразу.",
    },
    "rest_travel": {
        "what": "{who}в отдыхе и поездках сегодня важно отличи побег от настоящей смены воздуха.",
        "opportunity": "Смена обстановки на час — если тянет «всё бросить».",
        "trap": "Сидеть на месте из упрямства и называть это стабильностью.",
        "do": "Выйди из привычной обстановки хотя бы на час — без большого плана.",
        "avoid": "Не путай привычный контур с заботой о себе.",
        "domestic": "Смена обстановки на час, если тянет «всё бросить».",
    },
}

_DEFAULT_SCENE_BEAT: dict[str, str] = {
    "what": "{who}сегодня конфликт дня проявляется в одной живой сцене — не в общей теме.",
    "opportunity": "Один конкретный жест в пользу поворота.",
    "trap": "Сделать вид, что выбора не было, и остаться в автопилоте.",
    "do": "Сделай один шаг — маленький, но сегодняшний.",
    "avoid": "Не усиливай автопилот согласием «ради спокойствия».",
    "domestic": "Одна бытовая сцена, где конфликт становится видимым.",
}

_TEMPLATE_OPP_RE = re.compile(r"^Шанс выбрать «.+» именно здесь")
_TEMPLATE_WHAT_MARKERS = ("тот же выбор — «", "день упирается в выбор: «")


def scene_copy_needs_heal_v1(scenes: list[Any] | None) -> bool:
    """True when scenes still use force-paste templates (pre-variety beats)."""
    for sc in scenes or []:
        if not isinstance(sc, dict):
            continue
        opp = str(sc.get("opportunity") or "")
        what = str(sc.get("what_happens") or "")
        if _TEMPLATE_OPP_RE.match(opp.strip()):
            return True
        if any(m in what for m in _TEMPLATE_WHAT_MARKERS):
            return True
    return False


def build_scenario_scenes_v1(
    *,
    conflict: dict[str, Any],
    chorus: dict[str, Any],
    foundation: dict[str, Any],
    interpretation: dict[str, Any] | None = None,
    max_scenes: int = 4,
    person_name: str | None = None,
) -> list[dict[str, Any]]:
    """Only spheres where the conflict actually shows.

    Copy rule: conflict axis is named once in opening. Scene lines paraphrase
    into lived sphere language — no force_a/force_b quote spam. Prefer name.
    """
    interp = _as_dict(interpretation)
    family = str((_as_dict(conflict.get("thesis")).get("family")) or "momentum")
    label = str(conflict.get("short_name") or "сюжет дня")
    domains_present = [str(d) for d in _as_list(interp.get("domains_present"))]
    sphere_ids = _select_sphere_ids(family=family, domains_present=domains_present, max_scenes=max_scenes)

    who = _vocative_prefix(person_name)
    driver_ids = list(conflict.get("driver_ids") or [])
    number_voice = _as_dict(chorus.get("day_number"))
    card_voice = _as_dict(chorus.get("day_card"))
    lead_fact = ""
    for d in _as_list(foundation.get("ranked_drivers")):
        if not isinstance(d, dict) or not d.get("fact_ru"):
            continue
        fact = str(d.get("fact_ru") or "")
        if _is_calendar_kitchen_fact(fact):
            continue
        lead_fact = _clip(fact, 120)
        break

    scenes: list[dict[str, Any]] = []
    for idx, sid in enumerate(sphere_ids):
        scene_id = f"scene.{sid}"
        sphere_label = _SPHERE_LABEL_RU.get(sid, sid)
        role = _scene_role(sid, idx)
        beat = _SCENE_BEATS.get(sid) or _DEFAULT_SCENE_BEAT
        what = beat["what"].format(who=who)
        if lead_fact and idx == 0:
            # One soft sky cue on primary only — not pasted into every sphere / domestic.
            what = f"{what} {_clip(lead_fact, 110)}"
        why = conflict.get("why_arose") or "Факты дня собираются в одну линию."
        opportunity = beat["opportunity"]
        trap = beat["trap"]
        do = beat["do"]
        avoid = beat["avoid"]
        domestic = beat["domestic"]

        chorus_refs: list[str] = ["conflict"]
        if driver_ids:
            chorus_refs.append(f"astrology:{driver_ids[0]}")
        if card_voice:
            chorus_refs.append("day_card")
        if number_voice:
            chorus_refs.append("day_number")
        if _as_list(chorus.get("natal")):
            chorus_refs.append("natal")

        if number_voice.get("tempo"):
            do = f"{do} Темп: {number_voice.get('tempo')}."

        scenes.append(
            {
                "scene_id": scene_id,
                "sphere": sid,
                "sphere_label_ru": sphere_label,
                "role_in_story": role,
                "what_happens": what,
                "why": why,
                "opportunity": opportunity,
                "trap": trap,
                "recommended_action": do,
                "do_not": avoid,
                "domestic_example": domestic,
                "evidence_references": list(driver_ids),
                "chorus_references": chorus_refs,
                "confidence": float(conflict.get("confidence") or 0.5),
                "serves_conflict": label,
            }
        )
    return scenes


def empty_props_v1() -> dict[str, Any]:
    """Empty props shell (tests / unavailable)."""
    return {
        "contract_version": "day_scenario_props_v1",
        "status": "empty",
        "color": None,
        "avoid_color": None,
        "goals": [],
        "affirmations": [],
        "humor": None,
        "strong_spheres": [],
        "weak_spheres": [],
        "rule": "Every prop must carry origin_scene_id; catalog is knowledge only, not SoT.",
    }


def _needed_color_tags(*, trap: str, force_a: str, sphere: str, mode: str) -> set[str]:
    blob = f"{trap} {force_a} {sphere} {mode}".lower()
    tags: set[str] = set()
    if any(k in blob for k in ("соглас", "угодить", "гармон", "please", "сглад")):
        tags.update({"hold_distance", "boundaries", "slow_reply", "clarity"})
    if any(k in blob for k in ("спеш", "импульс", "ускор", "rush", "срыв")):
        tags.update({"calm_clarity", "pause_before_act", "depth"})
    if any(k in blob for k in ("разговор", "сообщ", "контакт", "communication", "прям")):
        tags.update({"soft_speech", "communication", "inner_honesty"})
    if any(k in blob for k in ("устал", "восстанов", "тело", "сон", "energy")):
        tags.update({"restore", "body", "tempo_gentle"})
    if any(k in blob for k in ("давлен", "границ", "контрол", "pressure")):
        tags.update({"boundaries", "ground", "focus"})
    if any(k in blob for k in ("распыл", "сует", "шум")):
        tags.update({"focus", "calm_clarity", "steady"})
    if mode in {"recovery", "stability"}:
        tags.update({"restore", "steady", "ground"})
    if not tags:
        tags.update({"calm_clarity", "hold_distance", "clarity"})
    if sphere in {"relationships", "communication"}:
        tags.add("communication")
    if sphere in {"energy_body", "rest_travel"}:
        tags.update({"restore", "body"})
    if sphere in {"work_decisions", "money"}:
        tags.update({"focus", "decision", "calm_clarity"})
    return tags


def _amplify_tags_for_trap(trap: str, force_a: str) -> set[str]:
    blob = f"{trap} {force_a}".lower()
    tags: set[str] = set()
    if any(k in blob for k in ("соглас", "угодить", "гармон", "сглад", "please")):
        tags.update({"please", "harmony_at_any_cost", "soft_over_truth"})
    if any(k in blob for k in ("спеш", "импульс", "ускор", "реакц")):
        tags.update({"rush", "react_first", "impulse", "alarm"})
    if any(k in blob for k in ("распыл", "сует", "шум")):
        tags.update({"scatter", "noise"})
    if any(k in blob for k in ("давлен", "всё или", "контрол")):
        tags.update({"pressure", "all_or_nothing", "over_control", "harsh"})
    if not tags:
        tags.update({"rush", "scatter", "please"})
    return tags


def _pick_primary_scene(scenes: list[dict[str, Any]]) -> dict[str, Any] | None:
    for sc in scenes:
        if isinstance(sc, dict) and sc.get("role_in_story") == "primary":
            return sc
    for sc in scenes:
        if isinstance(sc, dict):
            return sc
    return None


def _humor_opportunity(scene: dict[str, Any], conflict: dict[str, Any]) -> dict[str, Any] | None:
    blob = " ".join(
        str(scene.get(k) or "")
        for k in ("domestic_example", "trap", "opportunity", "what_happens")
    ).lower()
    patterns: list[tuple[str, re.Pattern[str]]] = [
        ("impulse_purchase", re.compile(r"покуп|импульс|трат")),
        ("odd_message", re.compile(r"сообщен|написа|ответ")),
        ("cancel_plans", re.compile(r"отмен|вс[её]\s*брос|планы")),
        ("vacation_urge", re.compile(r"отпуск|уех|обстанов")),
        ("romantic_glitch", re.compile(r"отношен|близост|роман")),
        ("over_control", re.compile(r"контрол|вс[её]\s*удерж")),
    ]
    for kind, pat in patterns:
        if pat.search(blob):
            return {
                "kind": kind,
                "origin_scene_id": scene.get("scene_id"),
                "text": (
                    f"Если поймаете себя на «{conflict.get('opposing_forces', {}).get('a') or 'автопилоте'}» "
                    f"в зоне «{scene.get('sphere_label_ru')}» — это уже сцена дня, не личный провал. "
                    f"Можно улыбнуться и выбрать другой жест."
                ),
                "serves_conflict": conflict.get("short_name"),
                "optional": True,
            }
    return None


def build_scenario_props_v1(
    *,
    conflict: dict[str, Any],
    scenes: list[dict[str, Any]],
    chorus: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive color/avoid/goals/affirmations/humor from scenes (B2).

    Color catalog = knowledge only. Selection + user-facing why come from conflict/scene.
    """
    from todayflow_backend.services.day_color_catalog_v1 import (
        list_color_knowledge,
        score_color_for_needs,
    )

    primary = _pick_primary_scene(scenes)
    if not primary:
        return empty_props_v1()

    trap = str(primary.get("trap") or "")
    force = _as_dict(conflict.get("opposing_forces"))
    force_a = str(force.get("a") or "")
    force_b = str(force.get("b") or "")
    thesis = _as_dict(conflict.get("thesis"))
    mode = str(thesis.get("mode") or "")
    sphere = str(primary.get("sphere") or "")
    scene_id = str(primary.get("scene_id") or "")
    label = str(conflict.get("short_name") or "сюжет дня")

    needed = _needed_color_tags(trap=trap, force_a=force_a, sphere=sphere, mode=mode)
    amplify = _amplify_tags_for_trap(trap, force_a)

    catalog = list_color_knowledge()
    ranked = sorted(
        catalog,
        key=lambda e: score_color_for_needs(e, needed),
        reverse=True,
    )
    chosen = ranked[0] if ranked else None
    if not chosen:
        return empty_props_v1()

    # Prefer catalog avoid candidate that amplifies today's trap tags
    avoid_pick = None
    best_avoid_score = -1
    for cand in chosen.get("avoid_candidates") or ():
        if not isinstance(cand, dict):
            continue
        score = len(set(cand.get("amplifies") or ()) & amplify)
        if score > best_avoid_score:
            best_avoid_score = score
            avoid_pick = cand
    if avoid_pick is None:
        # scan other entries' avoid candidates
        for entry in catalog:
            for cand in entry.get("avoid_candidates") or ():
                if not isinstance(cand, dict):
                    continue
                score = len(set(cand.get("amplifies") or ()) & amplify)
                if score > best_avoid_score:
                    best_avoid_score = score
                    avoid_pick = cand

    apply = _as_dict(chosen.get("apply"))
    color_prop = {
        "name": chosen.get("name"),
        "origin_scene_id": scene_id,
        "serves_conflict": label,
        "link_to_conflict": _clip(
            f"{chosen.get('symbolic_property')} — якорь против срыва в «{force_a}» "
            f"и в сторону «{force_b}».",
            220,
        ),
        "supports_or_compensates": _clip(f"Компенсирует ловушку дня в зоне «{primary.get('sphere_label_ru')}».", 160),
        "expected_effect_today": _clip(
            f"Напоминает выбрать «{force_b}», когда тянет в «{force_a}».",
            160,
        ),
        "where_to_use": {
            "clothing": apply.get("clothing"),
            "accessory": apply.get("accessory"),
            "workspace": apply.get("workspace"),
            "makeup": apply.get("makeup"),
            "ui_or_bg": apply.get("ui_or_bg"),
        },
        "intensity": chosen.get("intensity_default"),
        "catalog_knowledge_ref": chosen.get("name"),
        "evidence_references": list(primary.get("evidence_references") or []),
        "chorus_references": list(primary.get("chorus_references") or []),
        "so_t_note": "scenario_scene_derived; catalog is knowledge only",
    }

    avoid_name = str((avoid_pick or {}).get("name") or "Кислотный неон")
    avoid_prop = {
        "name": avoid_name,
        "origin_scene_id": scene_id,
        "serves_conflict": label,
        "amplifies_trap": _clip(trap, 120),
        "why": _clip(
            f"{avoid_name} сегодня разгоняет «{force_a}». Держи его вне поля зрения.",
            160,
        ),
        "where_especially_avoid": (
            f"В одежде и на фоне разговора/решения в зоне «{primary.get('sphere_label_ru')}»."
        ),
        "ok_as_tiny_accent": False,
        "catalog_knowledge_ref": avoid_name,
        "evidence_references": list(primary.get("evidence_references") or []),
    }

    # Goals: 1 primary + up to 2 secondary from other scenes — not verbatim do
    goals: list[dict[str, Any]] = []
    primary_goal = {
        "text": _clip(
            f"Один жест в зоне «{primary.get('sphere_label_ru')}» в сторону «{force_b}» "
            f"— без ожидания чужой реакции.",
            200,
        ),
        "origin_scene_id": scene_id,
        "serves_conflict": label,
        "solves": _clip(trap, 120),
        "one_day_feasible": True,
        "duplicates_do": False,
        "role": "primary",
    }
    goals.append(primary_goal)
    for sc in scenes:
        if not isinstance(sc, dict) or sc.get("scene_id") == scene_id:
            continue
        if len(goals) >= 3:
            break
        goals.append(
            {
                "text": _clip(
                    f"В «{sc.get('sphere_label_ru')}» заметить «{force_a}» "
                    f"и заменить одним маленьким «{force_b}».",
                    200,
                ),
                "origin_scene_id": sc.get("scene_id"),
                "serves_conflict": label,
                "solves": _clip(sc.get("trap"), 100),
                "one_day_feasible": True,
                "duplicates_do": False,
                "role": "secondary",
            }
        )

    action_hint = _clip(primary.get("recommended_action"), 100)
    sphere_label = str(primary.get("sphere_label_ru") or "сегодня")
    affirmations = [
        {
            "text": _clip(
                action_hint
                or f"В зоне «{sphere_label}» я делаю один ясный шаг — без автопилота.",
                160,
            ),
            "origin_scene_id": scene_id,
            "serves_conflict": label,
            "compensates_trap": _clip(trap, 120),
            "helps_action": action_hint,
            "universal_formula": False,
        }
    ]

    humor = _humor_opportunity(primary, conflict)

    strong: list[dict[str, Any]] = []
    weak: list[dict[str, Any]] = []
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        row = {
            "sphere": sc.get("sphere"),
            "sphere_label_ru": sc.get("sphere_label_ru"),
            "origin_scene_id": sc.get("scene_id"),
            "role_in_story": sc.get("role_in_story"),
        }
        if sc.get("role_in_story") == "primary" or sc.get("sphere") in {
            "work_decisions",
            "communication",
            "relationships",
            "creativity",
        }:
            # primary + opportunity-forward spheres → strong unless explicitly support_or_risk body/rest
            if sc.get("role_in_story") == "support_or_risk" and sc.get("sphere") in {
                "energy_body",
                "rest_travel",
                "home",
            }:
                weak.append({**row, "status": "vulnerable", "risk": sc.get("trap")})
            else:
                strong.append({**row, "status": "strong", "opportunity": sc.get("opportunity")})
        else:
            weak.append({**row, "status": "vulnerable", "risk": sc.get("trap")})

    # Ensure primary appears in strong
    if primary and not any(s.get("origin_scene_id") == scene_id for s in strong):
        strong.insert(
            0,
            {
                "sphere": primary.get("sphere"),
                "sphere_label_ru": primary.get("sphere_label_ru"),
                "origin_scene_id": scene_id,
                "role_in_story": primary.get("role_in_story"),
                "status": "strong",
                "opportunity": primary.get("opportunity"),
            },
        )

    return {
        "contract_version": "day_scenario_props_v1",
        "status": "ok",
        "color": color_prop,
        "avoid_color": avoid_prop,
        "goals": goals,
        "affirmations": affirmations,
        "humor": humor,
        "strong_spheres": strong,
        "weak_spheres": weak,
        "rule": "Every prop carries origin_scene_id; catalog is knowledge only, not SoT.",
        "chorus_tempo_hint": (_as_dict(chorus).get("day_number") or {}).get("tempo")
        if isinstance(chorus, dict)
        else None,
    }


def build_day_scenario_v1(
    *,
    interpretation: dict[str, Any] | None = None,
    day_events_pack: dict[str, Any] | None = None,
    day_thesis: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    max_scenes: int = 4,
    person_name: str | None = None,
) -> dict[str, Any]:
    """Assemble day_scenario_v1 spine + props. Exclusive meaning SoT (B5)."""
    interp = _as_dict(interpretation)
    foundation = build_scenario_foundation_v1(
        interpretation=interp,
        day_events_pack=day_events_pack,
        ritual_context=ritual_context,
        celestial_events=celestial_events,
    )
    conflict = build_scenario_conflict_v1(
        foundation=foundation,
        day_thesis=day_thesis,
        interpretation=interp,
    )
    chorus = build_interpretive_chorus_v1(
        foundation=foundation,
        conflict_label=str(conflict.get("short_name") or ""),
        interpretation=interp,
    )
    scenes = build_scenario_scenes_v1(
        conflict=conflict,
        chorus=chorus,
        foundation=foundation,
        interpretation=interp,
        max_scenes=max_scenes,
        person_name=person_name,
    )
    props = build_scenario_props_v1(conflict=conflict, scenes=scenes, chorus=chorus)
    ready = bool(scenes) and bool(conflict.get("short_name"))
    return {
        "contract_version": DAY_SCENARIO_V1_CONTRACT,
        "version": DAY_SCENARIO_V1_VERSION,
        "runtime_sot": True,
        "ready": ready,
        "generation_source": "deterministic_engine_b5",
        "foundation": foundation,
        "chorus": chorus,
        "conflict": conflict,
        "scenes": scenes,
        "props": props,
        "projections": {
            "status": "day_scenario_project_v1.b5",
            "note": "Legacy day_story slots are projections only; not meaning inputs.",
        },
    }


def validate_day_scenario_v1(scenario: dict[str, Any] | None) -> list[str]:
    """Structural validation — architectural invariants for B1+B2."""
    errors: list[str] = []
    if not isinstance(scenario, dict):
        return ["scenario_not_dict"]
    if scenario.get("contract_version") != DAY_SCENARIO_V1_CONTRACT:
        errors.append("bad_contract_version")
    foundation = _as_dict(scenario.get("foundation"))
    conflict = _as_dict(scenario.get("conflict"))
    chorus = _as_dict(scenario.get("chorus"))
    scenes = _as_list(scenario.get("scenes"))

    if not conflict.get("short_name"):
        errors.append("conflict_missing_short_name")
    if not conflict.get("driver_ids") and not _as_list(foundation.get("ranked_drivers")):
        errors.append("conflict_without_drivers_or_foundation")
    if not isinstance(conflict.get("opposing_forces"), dict):
        errors.append("conflict_missing_opposing_forces")

    drivers = _as_list(conflict.get("driver_ids"))
    if not drivers and (foundation.get("tarot_card") or {}).get("present"):
        if not _as_list(foundation.get("personal_natal_activations")):
            errors.append("conflict_card_without_drivers")

    if chorus.get("day_card") and not chorus["day_card"].get("must_not_invent_second_plot"):
        errors.append("day_card_missing_no_second_plot_flag")
    if chorus.get("day_number") and not chorus["day_number"].get("must_not_invent_second_plot"):
        errors.append("day_number_missing_no_second_plot_flag")

    if not scenes:
        errors.append("scenes_empty")
    scene_ids = set()
    for sc in scenes:
        if not isinstance(sc, dict):
            errors.append("scene_not_dict")
            continue
        if not sc.get("scene_id"):
            errors.append("scene_missing_id")
        else:
            scene_ids.add(str(sc["scene_id"]))
        if sc.get("sphere") not in PRODUCT_SPHERE_IDS:
            errors.append(f"scene_bad_sphere:{sc.get('sphere')}")
        if not sc.get("serves_conflict"):
            errors.append(f"scene_missing_serves_conflict:{sc.get('scene_id')}")

    props = _as_dict(scenario.get("props"))
    if props.get("status") == "ok":
        color = _as_dict(props.get("color"))
        if color:
            if not color.get("origin_scene_id"):
                errors.append("prop_color_without_origin_scene")
            elif str(color.get("origin_scene_id")) not in scene_ids:
                errors.append("prop_color_origin_not_in_scenes")
            if not color.get("link_to_conflict"):
                errors.append("prop_color_missing_conflict_link")
        avoid = _as_dict(props.get("avoid_color"))
        if avoid:
            if not avoid.get("origin_scene_id"):
                errors.append("prop_avoid_without_origin_scene")
            if not avoid.get("amplifies_trap"):
                errors.append("prop_avoid_missing_trap_link")
        for g in _as_list(props.get("goals")):
            if isinstance(g, dict) and not g.get("origin_scene_id"):
                errors.append("prop_goal_without_origin_scene")
        for a in _as_list(props.get("affirmations")):
            if isinstance(a, dict) and not a.get("origin_scene_id"):
                errors.append("prop_affirmation_without_origin_scene")
            if isinstance(a, dict) and a.get("universal_formula"):
                errors.append("prop_affirmation_universal_forbidden")
        humor = props.get("humor")
        if isinstance(humor, dict) and humor and not humor.get("origin_scene_id"):
            errors.append("prop_humor_without_origin_scene")

    return errors
