"""Wave 2 Phase D.1b / D.2 — project day_scenario nest onto day_facts_v1.

No dramaturgy regenerate. Temporal gate (D.2): all conflict.driver_ids must be
natal-style (`pt-…`) and ⊆ fresh activation pool. Pack ids → no project / partial.
Act 3 stays on day_scenario nest (not demoted by this gate).
"""

from __future__ import annotations

from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _looks_like_natal_driver(driver_id: str) -> bool:
    """Natal activation id namespace used by Strip / glance / day_facts pool."""
    return (driver_id or "").strip().lower().startswith("pt-")


def narrative_drivers_in_pool(
    conflict_driver_ids: list[str] | tuple[str, ...] | None,
    activations: list[dict[str, Any]] | None,
) -> bool:
    """True when conflict drivers are verifiably in the fresh natal activation pool.

    D.2: every id must be natal-style (`pt-…`) and ⊆ pool. Event-pack ids
    (`sky-`/`phase-`/`moon-`/…) fail — uncheckable against activations, so day_facts
    omits narrative (`partial: true`). No invent / no top-by-rank substitution.
    """
    ids = [str(x) for x in (conflict_driver_ids or []) if x]
    if not ids:
        return False
    if not all(_looks_like_natal_driver(i) for i in ids):
        return False
    pool = {str(a.get("id") or "") for a in (activations or []) if a.get("id")}
    return set(ids) <= pool


def load_ready_day_scenario(db: Any, *, user_id: int, local_date: Any) -> dict[str, Any] | None:
    """Load ready day_scenario from cached day_story for the request date (no rebuild)."""
    from todayflow_backend.services.day_story_wire_v1 import _load_cached_day_story

    hit = _load_cached_day_story(
        db,
        user_id=int(user_id),
        target_date=local_date,
        any_for_date=True,
    )
    if not hit:
        return None
    story, _gen_id, _fp = hit
    sc = story.get("day_scenario") if isinstance(story, dict) else None
    if not isinstance(sc, dict):
        return None
    if sc.get("ready") is False or sc.get("runtime_sot") is False:
        return None
    conflict = _as_dict(sc.get("conflict"))
    if not _clean(conflict.get("short_name")):
        return None
    scenes = [s for s in _as_list(sc.get("scenes")) if isinstance(s, dict)]
    if not scenes:
        return None
    return sc


def project_conflict(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Wave2 conflict shape. thesis = label_ru only; else null (no filler)."""
    c = _as_dict(raw)
    short_name = _clean(c.get("short_name"))
    if not short_name:
        return None
    thesis_obj = c.get("thesis")
    thesis: str | None = None
    if isinstance(thesis_obj, str):
        thesis = thesis_obj.strip() or None
    elif isinstance(thesis_obj, dict):
        label = _clean(thesis_obj.get("label_ru"))
        thesis = label or None
    opposing = _as_dict(c.get("opposing_forces"))
    wp = c.get("why_personal")
    if wp == "omit":
        why_personal: str | None = "omit"
    else:
        why_personal = _clean(wp) or None
    driver_ids = [str(x) for x in _as_list(c.get("driver_ids")) if x]
    return {
        "short_name": short_name,
        "thesis": thesis,
        "opposing_forces": {
            "a": _clean(opposing.get("a")),
            "b": _clean(opposing.get("b")),
        },
        "why_arose": _clean(c.get("why_arose")),
        "why_personal": why_personal,
        "driver_ids": driver_ids,
    }


def _map_role(role: str) -> str:
    r = (role or "").strip().lower()
    if r in {"primary", "support", "caution"}:
        return r
    if r in {"secondary", "support_or_risk", "peak"}:
        return "caution" if r != "secondary" else "support"
    return "support"


def project_scenes(raw_scenes: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sc in _as_list(raw_scenes):
        if not isinstance(sc, dict):
            continue
        scene_id = _clean(sc.get("scene_id")) or _clean(sc.get("id"))
        if not scene_id:
            continue
        drivers = [str(x) for x in _as_list(sc.get("driver_ids")) if x]
        if not drivers:
            drivers = [str(x) for x in _as_list(sc.get("evidence_references")) if x]
        out.append(
            {
                "id": scene_id,
                "sphere": _clean(sc.get("sphere")),
                "role_in_story": _map_role(str(sc.get("role_in_story") or "")),
                "what_happens": _clean(sc.get("what_happens")),
                "opportunity": _clean(sc.get("opportunity")),
                "trap": _clean(sc.get("trap")),
                "recommended_action": _clean(sc.get("recommended_action")),
                "do_not": _clean(sc.get("do_not")),
                "domestic_example": (_clean(sc.get("domestic_example")) or None),
                "driver_ids": drivers,
            }
        )
    return out


def project_props(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Map day_scenario props → Wave2 props. evening_payoff always null (SH-4)."""
    p = _as_dict(raw)
    if not p or p.get("status") == "empty":
        # Still allow partial props if color/goals present
        if not any(p.get(k) for k in ("color", "avoid_color", "goals", "affirmations", "humor")):
            return None

    color = p.get("color") if isinstance(p.get("color"), dict) else None
    avoid = p.get("avoid_color") if isinstance(p.get("avoid_color"), dict) else None
    goals = [g for g in _as_list(p.get("goals")) if isinstance(g, dict)]
    affirms = [a for a in _as_list(p.get("affirmations")) if isinstance(a, dict)]
    humor = p.get("humor") if isinstance(p.get("humor"), dict) else None

    practice = None
    if goals:
        g0 = goals[0]
        text = _clean(g0.get("text"))
        if text:
            practice = {
                "text": text,
                "window": _clean(g0.get("window")) or None,
                "serves_conflict": _clean(g0.get("serves_conflict")) or None,
            }

    affirmation = None
    if affirms:
        a0 = affirms[0]
        text = _clean(a0.get("text"))
        if text:
            affirmation = {
                "text": text,
                "compensates_trap": _clean(a0.get("compensates_trap")) or None,
            }

    color_out = None
    if color and _clean(color.get("name")):
        color_out = {
            "name": _clean(color.get("name")),
            "link_to_conflict": _clean(color.get("link_to_conflict")) or None,
            "where_to_use": _clean(color.get("where_to_use")) or None,
        }

    avoid_out = None
    if avoid and _clean(avoid.get("name")):
        avoid_out = {
            "name": _clean(avoid.get("name")),
            "amplifies_trap": _clean(avoid.get("amplifies_trap")) or None,
        }

    humor_out = None
    if humor and _clean(humor.get("text")):
        humor_out = {
            "text": _clean(humor.get("text")),
            "serves_conflict": _clean(humor.get("serves_conflict")) or None,
        }

    return {
        "color": color_out,
        "avoid_color": avoid_out,
        "practice_or_promise": practice,
        "affirmation": affirmation,
        "humor": humor_out,
        "evening_payoff": None,
    }


def project_numerology(foundation: dict[str, Any] | None) -> dict[str, Any] | None:
    day_number = _as_dict(_as_dict(foundation).get("day_number"))
    personal = day_number.get("personal_day")
    if personal is None:
        return None
    try:
        n = int(personal)
    except (TypeError, ValueError):
        return None
    return {"personal_day": n, "source": "classic_reduce_v0"}


def project_moon_phase(scenario: dict[str, Any] | None) -> dict[str, Any] | None:
    """Map lunar snapshot without inventing illumination."""
    sc = _as_dict(scenario)
    foundation = _as_dict(sc.get("foundation"))
    # Prefer explicit lunar block if ever present on scenario
    lunar = _as_dict(sc.get("lunar_phase"))
    if not lunar:
        for row in _as_list(foundation.get("astronomy_facts")) or _as_list(
            foundation.get("astronomy")
        ):
            if isinstance(row, dict) and str(row.get("kind") or "") == "lunar_phase":
                lunar = row
                break
    if not lunar:
        return None

    name = _clean(lunar.get("name") or lunar.get("label_ru") or lunar.get("id")).lower()
    is_new = "new" in name or "новолун" in name
    is_full = "full" in name or "полнолун" in name
    phase: str | None = None
    if "wax" in name or "растущ" in name:
        phase = "waxing"
    elif "wan" in name or "убыва" in name:
        phase = "waning"
    elif is_new or is_full:
        phase = "waxing" if is_new else "waning"

    illumination = lunar.get("illumination_pct")
    if illumination is None:
        illumination = lunar.get("cycle_percent")
    ill_out: float | None = None
    if illumination is not None:
        try:
            ill_out = float(illumination)
        except (TypeError, ValueError):
            ill_out = None

    # Require at least one honest signal
    if phase is None and ill_out is None and not (is_new or is_full):
        return None

    return {
        "illumination_pct": ill_out,
        "phase": phase,
        "is_new": bool(is_new),
        "is_full": bool(is_full),
    }


def project_sky_drivers(scenario: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Thin sky list from foundation transit rows — empty if shape unavailable."""
    foundation = _as_dict(_as_dict(scenario).get("foundation"))
    out: list[dict[str, Any]] = []
    for row in _as_list(foundation.get("sky_drivers")):
        if not isinstance(row, dict):
            continue
        planet = _clean(row.get("planet") or row.get("body"))
        sign = _clean(row.get("sign"))
        if not planet or not sign:
            continue
        try:
            degree = float(row.get("degree_in_sign"))
        except (TypeError, ValueError):
            continue
        out.append(
            {
                "planet": planet,
                "sign": sign,
                "degree_in_sign": degree,
                "retrograde": bool(row.get("retrograde")),
            }
        )
    return out


def project_narrative_blob(
    scenario: dict[str, Any],
    *,
    activations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return conflict/scenes/props/sky/moon/numerology or None if gate fails."""
    conflict = project_conflict(scenario.get("conflict"))
    scenes = project_scenes(scenario.get("scenes"))
    if not conflict or not scenes:
        return None
    if not narrative_drivers_in_pool(conflict.get("driver_ids") or [], activations):
        return None
    props = project_props(scenario.get("props"))
    foundation = _as_dict(scenario.get("foundation"))
    return {
        "conflict": conflict,
        "scenes": scenes,
        "props": props,
        "numerology": project_numerology(foundation),
        "moon_phase": project_moon_phase(scenario),
        "sky_drivers": project_sky_drivers(scenario),
    }
