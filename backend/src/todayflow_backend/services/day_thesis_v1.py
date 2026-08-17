"""day_thesis_v1 — единый сюжет дня (не обязательно «конфликт»).

Machine contract: family + variant + mode + label + driver_ids + composition_ids.
UI may say «главный сюжет» / vibe title; not every day is a conflict.
"""

from __future__ import annotations

from typing import Any

DAY_THESIS_V1 = "day_thesis_v1"

# family → analytics / stable logic
# variant → editorial diversity within family
_VARIANTS: dict[str, dict[str, dict[str, str]]] = {
    "decision": {
        "stop_pleasing_everyone": {
            "label_ru": "Выбор без попытки всем угодить",
            "mode": "conflict",
        },
        "one_clear_yes": {
            "label_ru": "Одно ясное «да»",
            "mode": "conflict",
        },
        "close_the_loop": {
            "label_ru": "Закрыть незакрытый контур",
            "mode": "transition",
        },
    },
    "communication": {
        "clarity_returns_after_delay": {
            "label_ru": "Возвращение ясности",
            "mode": "transition",
        },
        "truth_without_filter": {
            "label_ru": "Прямота без фильтра",
            "mode": "conflict",
        },
        "restart_messages": {
            "label_ru": "Перезапуск диалогов",
            "mode": "opportunity",
        },
    },
    "change": {
        "sudden_turns": {
            "label_ru": "Неожиданные повороты",
            "mode": "conflict",
        },
        "soft_expansion": {
            "label_ru": "Мягкое расширение",
            "mode": "opportunity",
        },
        "release_old_script": {
            "label_ru": "Отпускание старого сценария",
            "mode": "recovery",
        },
    },
    "pressure": {
        "patience_test": {
            "label_ru": "Проверка терпения",
            "mode": "conflict",
        },
        "boundary_day": {
            "label_ru": "День границ",
            "mode": "conflict",
        },
        "intensity_without_drama": {
            "label_ru": "Глубина без драмы",
            "mode": "transition",
        },
    },
    "momentum": {
        "steady_productive_rhythm": {
            "label_ru": "Ровный продуктивный ритм",
            "mode": "stability",
        },
        "new_window": {
            "label_ru": "Окно новых возможностей",
            "mode": "opportunity",
        },
        "gather_pace": {
            "label_ru": "Набор темпа",
            "mode": "transition",
        },
    },
    "connection": {
        "honest_contact": {
            "label_ru": "Честный контакт",
            "mode": "opportunity",
        },
        "repair_after_friction": {
            "label_ru": "Починка после трения",
            "mode": "recovery",
        },
    },
}

# kind → default (family, variant) — overridden by compositions / model
_KIND_DEFAULT: dict[str, tuple[str, str]] = {
    "station_direct": ("communication", "clarity_returns_after_delay"),
    "station": ("communication", "clarity_returns_after_delay"),
    "retrograde_edge": ("pressure", "patience_test"),
    "moon_ingress": ("momentum", "gather_pace"),
    "planet_ingress": ("momentum", "gather_pace"),
    "phase_change": ("change", "release_old_script"),
    "lunar_aspect": ("pressure", "intensity_without_drama"),
    "sky_aspect": ("pressure", "intensity_without_drama"),
    "cycle_aspect": ("momentum", "new_window"),
    "personal_transit": ("decision", "one_clear_yes"),
    "seasonal": ("momentum", "new_window"),
}


def _variant_meta(family: str, variant: str) -> dict[str, str]:
    fam = _VARIANTS.get(family) or {}
    row = fam.get(variant) or {}
    if row:
        return {"family": family, "variant": variant, **row}
    # Fallback
    return {
        "family": "momentum",
        "variant": "steady_productive_rhythm",
        "label_ru": "Ровный продуктивный ритм",
        "mode": "stability",
    }


def _text_blob(ev: dict[str, Any]) -> str:
    parts = [
        str(ev.get("kind") or ""),
        str(ev.get("title_ru") or ""),
        str(ev.get("fact_ru") or ""),
        str((ev.get("meta") or {}).get("aspect") or ""),
        str(ev.get("body") or ""),
        str(ev.get("fact_key") or ""),
    ]
    return " ".join(parts).lower()


def _pick_from_drivers(
    drivers: list[dict[str, Any]],
    *,
    compositions: list[dict[str, Any]] | None,
    day_engine_brief: dict[str, Any] | None,
    day_model: dict[str, Any] | None,
) -> tuple[str, str]:
    """Return (family, variant) from ranked drivers + compositions + model."""
    # Composition wins when present and strong.
    comps = compositions or []
    if comps:
        top = max(comps, key=lambda c: float(c.get("strength") or 0))
        if float(top.get("strength") or 0) >= 0.7:
            mapped = str(top.get("thesis_hint") or "")
            if "/" in mapped:
                fam, var = mapped.split("/", 1)
                if fam in _VARIANTS and var in _VARIANTS[fam]:
                    return fam, var

    family, variant = "momentum", "steady_productive_rhythm"
    if drivers:
        top = drivers[0]
        hint = ""
        meta = top.get("meta") if isinstance(top.get("meta"), dict) else {}
        hint = str(meta.get("thesis_hint") or top.get("thesis_hint") or "")
        kind = str(top.get("kind") or "").lower()
        hinted = False
        if "/" in hint:
            fam, var = hint.split("/", 1)
            if fam in _VARIANTS and var in _VARIANTS[fam]:
                family, variant = fam, var
                hinted = True
        if not hinted:
            family, variant = _KIND_DEFAULT.get(kind, (family, variant))
        blob = _text_blob(top)
        # Pair mapping from shared sky is the plot; blob heuristics are for kind defaults.
        if hinted:
            return family, variant
        # Interaction with second driver / model
        second_blob = _text_blob(drivers[1]) if len(drivers) > 1 else ""
        combined = f"{blob} {second_blob}"

        model = day_model if isinstance(day_model, dict) else {}
        tension = model.get("tension") if isinstance(model.get("tension"), dict) else {}
        opportunity = model.get("opportunity") if isinstance(model.get("opportunity"), dict) else {}
        risk = model.get("risk") if isinstance(model.get("risk"), dict) else {}
        t_sum = str(tension.get("summary") or "").lower()
        o_sum = str(opportunity.get("summary") or "").lower()
        r_sum = str(risk.get("summary") or "").lower()
        high_tension = any(x in t_sum or x in r_sum for x in ("давлен", "риск", "накал", "резк", "конфликт"))
        high_opportunity = any(x in o_sum for x in ("возможност", "удач", "открыт", "прорыв"))

        if "station_direct" in kind or "station_direct" in blob or "direct" in blob:
            if high_tension or any(x in combined for x in ("pluto", "плутон", "square", "квадрат")):
                return "communication", "truth_without_filter"
            if high_opportunity or "sagittarius" in combined or "стрелец" in combined:
                return "communication", "restart_messages"
            return "communication", "clarity_returns_after_delay"

        if any(x in combined for x in ("uranus", "уран")):
            return "change", "sudden_turns"
        if any(x in combined for x in ("pluto", "плутон")) and high_tension:
            return "pressure", "intensity_without_drama"
        if any(x in combined for x in ("saturn", "сатурн", "границ")):
            return "pressure", "boundary_day"
        if high_opportunity and not high_tension:
            return "momentum", "new_window"
        if "moon_ingress" in kind and any(x in combined for x in ("стрелец", "sagittarius", "близнец", "gemini")):
            return "change", "soft_expansion"

    brief = day_engine_brief if isinstance(day_engine_brief, dict) else {}
    risk_b = str(brief.get("avoid_hint") or "").lower()
    if "всем угодить" in risk_b or "двум стул" in risk_b:
        return "decision", "stop_pleasing_everyone"
    if "границ" in risk_b:
        return "pressure", "boundary_day"

    return family, variant


def build_day_thesis_v1(
    *,
    day_events_pack: dict[str, Any] | None,
    day_engine_brief: dict[str, Any] | None = None,
    day_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic day thesis from ranked drivers + compositions + day_model."""
    pack = day_events_pack if isinstance(day_events_pack, dict) else {}
    by_id = {
        str(e.get("id")): e
        for e in (pack.get("events") or [])
        if isinstance(e, dict) and e.get("id")
    }
    drivers = [by_id[str(i)] for i in (pack.get("ranked_drivers") or []) if str(i) in by_id]
    compositions = [c for c in (pack.get("compositions") or []) if isinstance(c, dict)]

    family, variant = _pick_from_drivers(
        drivers,
        compositions=compositions,
        day_engine_brief=day_engine_brief,
        day_model=day_model,
    )
    meta = _variant_meta(family, variant)
    driver_ids = [str(d.get("id")) for d in drivers[:3]]
    composition_ids = [
        str(c.get("composition_id") or c.get("id") or "")
        for c in compositions[:3]
        if c.get("composition_id") or c.get("id")
    ]
    composition_ids = [c for c in composition_ids if c]

    return {
        "contract_version": DAY_THESIS_V1,
        "family": meta["family"],
        "variant": meta["variant"],
        "mode": meta["mode"],
        "label_ru": meta["label_ru"],
        # Back-compat alias for early UI that still says «конфликт»
        "label": meta["label_ru"],
        "driver_ids": driver_ids,
        "composition_ids": composition_ids,
    }


def list_day_thesis_variant_keys() -> list[str]:
    """Stable `family.variant` keys for editorial formula coverage checks."""
    keys: list[str] = []
    for family, variants in _VARIANTS.items():
        for variant in variants:
            keys.append(f"{family}.{variant}")
    return sorted(keys)


# Back-compat wrappers during migration from primary_conflict
def pick_primary_conflict(**kwargs: Any) -> dict[str, Any]:
    thesis = build_day_thesis_v1(**kwargs)
    return {
        "contract_version": "day_conflict_registry_v1",
        "id": f"{thesis['family']}.{thesis['variant']}",
        "label_ru": thesis["label_ru"],
        "driver_ids": thesis["driver_ids"],
        "day_thesis": thesis,
    }


def conflict_label(conflict_id: str) -> str:
    if "." in conflict_id:
        fam, var = conflict_id.split(".", 1)
        return _variant_meta(fam, var)["label_ru"]
    # legacy ids
    legacy = {
        "choice": ("decision", "one_clear_yes"),
        "sudden_turns": ("change", "sudden_turns"),
        "clarity_return": ("communication", "clarity_returns_after_delay"),
        "patience_test": ("pressure", "patience_test"),
        "new_opportunity": ("momentum", "new_window"),
        "intensity": ("pressure", "intensity_without_drama"),
        "release": ("change", "release_old_script"),
        "momentum": ("momentum", "gather_pace"),
        "boundary": ("pressure", "boundary_day"),
        "connection": ("connection", "honest_contact"),
    }
    pair = legacy.get(conflict_id)
    if pair:
        return _variant_meta(pair[0], pair[1])["label_ru"]
    return _variant_meta("momentum", "steady_productive_rhythm")["label_ru"]
