"""Global Day Engine v1 — deterministic energy, drivers, windows.

Canon: docs/today/TODAY_CONTENT_PIPELINE_V1.md (I0 · §3).
No natal, tarot, numerology, or LLM. Downstream may verbalize, never mutate.
"""

from __future__ import annotations

from typing import Any

GLOBAL_DAY_ENGINE_V1 = "global_day_engine_v1.0"
GLOBAL_DAY_PROFILE_CONTRACT = "global_day_profile_v1"

ENERGY_SET: tuple[str, ...] = (
    "grounded",
    "flow",
    "radiance",
    "momentum",
    "clarity",
    "tension",
    "renewal",
    "depth",
)

ACTION_TYPES: tuple[str, ...] = (
    "physical_action",
    "sensitive_conversation",
    "deep_work",
    "admin_order",
    "rest",
    "emotional_processing",
    "public_visibility",
    "hard_negotiation",
)

_PERSONAL_KINDS = frozenset({"personal_transit", "natal", "natal_transit"})
_HARD_ASPECTS = frozenset(
    {"square", "opposition", "semisquare", "sesquiquadrate", "quincunx"}
)
_SOFT_ASPECTS = frozenset({"trine", "sextile", "quintile", "biquintile", "conjunction"})

_EARTH = frozenset({"taurus", "virgo", "capricorn", "телец", "дева", "козерог"})
_WATER = frozenset({"cancer", "scorpio", "pisces", "рак", "скорпион", "рыбы"})
_FIRE = frozenset({"aries", "leo", "sagittarius", "овен", "лев", "стрелец"})
_AIR = frozenset({"gemini", "libra", "aquarius", "близнецы", "весы", "водолей"})

_KIND_ENERGY: dict[str, dict[str, float]] = {
    "moon_ingress": {"flow": 0.45, "grounded": 0.1},
    "planet_ingress": {"momentum": 0.35, "clarity": 0.15},
    "phase_change": {"renewal": 0.4, "radiance": 0.2},
    "station_direct": {"clarity": 0.5, "momentum": 0.2},
    "station": {"depth": 0.35, "tension": 0.3},
    "retrograde_edge": {"tension": 0.4, "depth": 0.2},
    "lunar_aspect": {"flow": 0.25, "tension": 0.15},
    "sky_aspect": {"radiance": 0.2, "tension": 0.2},
    "cycle_aspect": {"momentum": 0.35, "clarity": 0.1},
    "perigee": {"tension": 0.25, "flow": 0.15},
    "apogee": {"depth": 0.25, "rest": 0.0},
}

_WEAK_DAY_THRESHOLD = 0.28
_TIE_ENERGY = "clarity"
_WEAK_ENERGY = "grounded"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _norm(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def is_global_event(event: dict[str, Any] | None) -> bool:
    """True when the event may participate in Global Day (no natal/card/number)."""
    if not isinstance(event, dict):
        return False
    kind = _norm(event.get("kind"))
    eid = str(event.get("id") or "")
    if kind in _PERSONAL_KINDS:
        return False
    if eid.startswith("pt-") or eid.startswith("natal"):
        return False
    blob = " ".join(
        str(event.get(k) or "")
        for k in ("id", "kind", "source", "layer", "family")
    ).lower()
    if "natal" in blob or "tarot" in blob or "card" in blob:
        return False
    return True


def _events_by_id(pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for ev in _as_list(pack.get("events")):
        if isinstance(ev, dict) and ev.get("id"):
            out[str(ev["id"])] = ev
    return out


def global_ranked_drivers(pack: dict[str, Any] | None) -> list[dict[str, Any]]:
    """1–3 shared-sky drivers; natal/card/number rows dropped."""
    p = _as_dict(pack)
    by_id = _events_by_id(p)
    ranked = _as_list(p.get("ranked_drivers"))
    out: list[dict[str, Any]] = []
    for item in ranked:
        if isinstance(item, dict):
            ev = item
        else:
            ev = by_id.get(str(item) or "")
        if is_global_event(ev):
            out.append(ev)
        if len(out) >= 3:
            break
    if out:
        return out
    events = [e for e in _as_list(p.get("events")) if is_global_event(e)]
    events.sort(key=lambda e: (-float(e.get("strength") or 0), str(e.get("id") or "")))
    return events[:3]


def _sign_energy_boost(sign: str) -> dict[str, float]:
    s = _norm(sign)
    if s in _EARTH:
        return {"grounded": 0.22}
    if s in _WATER:
        return {"flow": 0.18, "depth": 0.1}
    if s in _FIRE:
        return {"momentum": 0.18, "radiance": 0.1}
    if s in _AIR:
        return {"clarity": 0.2}
    return {}


def _aspect_energy(event: dict[str, Any]) -> dict[str, float]:
    aspect = _norm(event.get("aspect") or event.get("aspect_type"))
    if aspect in _HARD_ASPECTS:
        return {"tension": 0.35}
    if aspect in _SOFT_ASPECTS:
        return {"flow": 0.15, "radiance": 0.12}
    return {}


def _phase_energy(event: dict[str, Any]) -> dict[str, float]:
    blob = " ".join(
        str(event.get(k) or "")
        for k in ("kind", "title_ru", "fact_ru", "phase", "id")
    ).lower()
    if "new" in blob or "новолун" in blob:
        return {"renewal": 0.35}
    if "full" in blob or "полнолун" in blob:
        return {"radiance": 0.3, "tension": 0.1}
    return {}


def score_energy(drivers: list[dict[str, Any]]) -> dict[str, float]:
    scores = {k: 0.0 for k in ENERGY_SET}
    for ev in drivers:
        kind = _norm(ev.get("kind"))
        weight = _clip01(float(ev.get("strength") or 0.5))
        for energy, amt in _KIND_ENERGY.get(kind, {"clarity": 0.15}).items():
            if energy in scores:
                scores[energy] += amt * (0.5 + weight)
        for energy, amt in _sign_energy_boost(str(ev.get("sign") or "")).items():
            scores[energy] += amt * weight
        for energy, amt in _aspect_energy(ev).items():
            scores[energy] += amt * weight
        if kind == "phase_change":
            for energy, amt in _phase_energy(ev).items():
                scores[energy] += amt * weight
        tension = _norm(ev.get("tension_level"))
        if tension in {"high", "tense", "challenging"}:
            scores["tension"] += 0.12
    return {k: round(_clip01(v), 4) for k, v in scores.items()}


def pick_primary_energy(scores: dict[str, float]) -> str:
    """Argmax over closed 8-set. Weak day → grounded. Tie → clarity."""
    if not scores:
        return _WEAK_ENERGY
    ranked = sorted(ENERGY_SET, key=lambda k: (-float(scores.get(k) or 0), k))
    top = ranked[0]
    top_v = float(scores.get(top) or 0)
    if top_v < _WEAK_DAY_THRESHOLD:
        return _WEAK_ENERGY
    second = ranked[1] if len(ranked) > 1 else top
    second_v = float(scores.get(second) or 0)
    if abs(top_v - second_v) < 1e-6:
        return _TIE_ENERGY
    return top


def _action_from_event(event: dict[str, Any]) -> tuple[list[str], list[str]]:
    blob = " ".join(
        str(event.get(k) or "")
        for k in ("body", "planet", "title_ru", "fact_ru", "id", "kind")
    ).lower()
    aspect = _norm(event.get("aspect") or event.get("aspect_type"))
    supports: list[str] = []
    cautions: list[str] = []
    if "mars" in blob or "марс" in blob:
        supports.append("physical_action")
        cautions.append("sensitive_conversation")
    if "mercury" in blob or "меркур" in blob:
        supports.append("admin_order")
        if aspect in _HARD_ASPECTS or "station" in _norm(event.get("kind")):
            cautions.append("hard_negotiation")
        else:
            supports.append("deep_work")
    if "moon" in blob or "лун" in blob:
        supports.append("emotional_processing")
        cautions.append("hard_negotiation")
    if "saturn" in blob or "сатурн" in blob:
        supports.append("deep_work")
        cautions.append("public_visibility")
    if "sun" in blob or "солнц" in blob:
        supports.append("public_visibility")
    if "venus" in blob or "венер" in blob:
        supports.append("sensitive_conversation")
    if aspect in _HARD_ASPECTS:
        if "physical_action" not in supports:
            cautions.append("sensitive_conversation")
        cautions.append("hard_negotiation")
    kind = _norm(event.get("kind"))
    if kind in {"phase_change"} and ("new" in blob or "новолун" in blob):
        supports.append("rest")
    if kind == "moon_ingress":
        supports.append("emotional_processing")
        cautions.append("hard_negotiation")
    if kind in {"void_of_course", "voc"}:
        supports.append("rest")
        cautions.append("hard_negotiation")
        cautions.append("physical_action")
    # Dedupe, closed set only
    def _closed(seq: list[str]) -> list[str]:
        seen: list[str] = []
        for x in seq:
            if x in ACTION_TYPES and x not in seen:
                seen.append(x)
        return seen[:4]

    supports_c = _closed(supports)
    cautions_c = _closed([c for c in cautions if c not in supports_c])
    if not supports_c:
        supports_c = ["deep_work"]
    return supports_c, cautions_c


def _hhmm(raw: Any) -> str | None:
    s = str(raw or "").strip()
    if not s:
        return None
    if len(s) >= 16 and s[10] in {"T", " "}:
        return s[11:16]
    if len(s) >= 5 and s[2] == ":":
        return s[:5]
    return None


def _window_row(
    *,
    time_s: str,
    driver_id: str,
    intensity: float,
    supports: list[str],
    cautions: list[str],
) -> dict[str, Any]:
    return {
        "time": time_s,
        "driver_id": driver_id,
        "intensity": round(_clip01(intensity), 3),
        "supports": supports,
        "cautions": cautions,
    }


def build_global_windows(
    *,
    celestial_events: dict[str, Any] | None,
    drivers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Timed shared-sky windows. Natal glance clocks are Personal — not here."""
    ce = _as_dict(celestial_events)
    windows: list[dict[str, Any]] = []
    seen_times: set[str] = set()

    def _add(raw_time: Any, event: dict[str, Any], *, intensity: float | None = None) -> None:
        hh = _hhmm(raw_time)
        if not hh or hh in seen_times:
            return
        seen_times.add(hh)
        supports, cautions = _action_from_event(event)
        windows.append(
            _window_row(
                time_s=hh,
                driver_id=str(event.get("id") or event.get("kind") or "sky"),
                intensity=float(intensity if intensity is not None else event.get("strength") or 0.55),
                supports=supports,
                cautions=cautions,
            )
        )

    headline = _as_dict(ce.get("headline_sky"))
    if headline:
        _add(headline.get("exact_time") or headline.get("exact_time_local"), headline)

    for row in _as_list(ce.get("timed_lunar_aspects")):
        if isinstance(row, dict):
            _add(row.get("exact_time") or row.get("exact_time_local"), row)

    for row in _as_list(ce.get("ingresses")):
        if not isinstance(row, dict):
            continue
        planet = " ".join(str(row.get(k) or "") for k in ("planet", "planet_ru", "body")).lower()
        if "moon" not in planet and "лун" not in planet:
            continue
        _add(row.get("exact_time") or row.get("local_time"), row)

    voc = _as_dict(ce.get("void_of_course"))
    if voc.get("status") == "ok" and voc.get("starts_at"):
        _add(
            voc.get("starts_at"),
            {
                "id": str(voc.get("last_aspect_id") or "voc"),
                "kind": "void_of_course",
                "body": "Moon",
            },
            intensity=0.4,
        )

    if not windows:
        for ev in drivers:
            when = ev.get("exact_time") or ev.get("exact_time_local") or ev.get("when")
            if when:
                _add(when, ev)

    windows.sort(key=lambda w: str(w.get("time") or ""))
    return windows[:6]


def _strength_risk(drivers: list[dict[str, Any]], windows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    supports: list[str] = []
    cautions: list[str] = []
    for ev in drivers:
        s, c = _action_from_event(ev)
        supports.extend(s)
        cautions.extend(c)
    for w in windows:
        supports.extend(list(w.get("supports") or []))
        cautions.extend(list(w.get("cautions") or []))

    def _uniq(seq: list[str]) -> list[str]:
        seen: list[str] = []
        for x in seq:
            if x in ACTION_TYPES and x not in seen:
                seen.append(x)
        return seen[:4]

    strength = _uniq(supports)
    risk = _uniq([c for c in cautions if c not in strength])
    return strength, risk


def build_global_day_profile_v1(
    *,
    day_events_pack: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic Global Day Profile. Safe on empty input (neutral day)."""
    drivers = global_ranked_drivers(day_events_pack)
    scores = score_energy(drivers)
    primary = pick_primary_energy(scores)
    windows = build_global_windows(celestial_events=celestial_events, drivers=drivers)
    strength, risk = _strength_risk(drivers, windows)
    slim_drivers = [
        {
            "id": str(d.get("id") or ""),
            "kind": d.get("kind"),
            "fact_ru": d.get("fact_ru") or d.get("title_ru"),
            "strength": d.get("strength"),
        }
        for d in drivers
        if d.get("id")
    ]
    return {
        "contract_version": GLOBAL_DAY_PROFILE_CONTRACT,
        "scoring_version": GLOBAL_DAY_ENGINE_V1,
        "primary_energy": primary,
        "energy_scores": scores,
        "drivers": slim_drivers,
        "strength": strength,
        "risk": risk,
        "windows": windows,
    }


def extract_pack_and_sky(story: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Pull day_events_pack + celestial_events from a day_story-shaped dict."""
    st = _as_dict(story)
    trace = _as_dict(st.get("trace"))
    pack = trace.get("day_events_pack")
    if not isinstance(pack, dict):
        pack = st.get("day_events_pack")
    ce = st.get("celestial_events")
    if not isinstance(ce, dict):
        ce = trace.get("celestial_events")
    if not isinstance(ce, dict):
        fd = _as_dict(st.get("day_foundation"))
        ce = fd.get("celestial_events") if isinstance(fd.get("celestial_events"), dict) else {}
    if not isinstance(pack, dict) and isinstance(ce, dict) and isinstance(ce.get("day_events_pack"), dict):
        pack = ce.get("day_events_pack")
    scen = _as_dict(st.get("day_scenario"))
    foundation = _as_dict(scen.get("foundation"))
    if not isinstance(pack, dict) or not pack.get("events"):
        ranked = _as_list(foundation.get("ranked_drivers"))
        if ranked:
            pack = {
                "events": [e for e in ranked if isinstance(e, dict)],
                "ranked_drivers": [
                    str(e.get("id") or "") for e in ranked if isinstance(e, dict) and e.get("id")
                ],
            }
    return _as_dict(pack), _as_dict(ce)


_PERSONAL_MUTATION_KEYS = frozenset(
    {
        "primary_energy",
        "visual_mode",
        "windows",
        "energy_scores",
        "drivers",
        "strength",
        "risk",
        "scoring_version",
    }
)

DAILY_ACTION_KINDS = frozenset({"practice", "affirmation", "reflection", "goal"})


def build_personal_day_nest_v1(story: dict[str, Any] | None) -> dict[str, Any] | None:
    """Natal overlay / personal bind. Omits energy/windows. Guest → None."""
    st = _as_dict(story)
    raw = st.get("day_personal")
    if not isinstance(raw, dict) or not raw:
        trace = _as_dict(st.get("trace"))
        raw = trace.get("day_personal")
    if not isinstance(raw, dict) or not raw:
        return None
    overlay = {k: v for k, v in raw.items() if k not in _PERSONAL_MUTATION_KEYS}
    if not overlay:
        return None
    return {
        "contract_version": "personal_day_v1",
        "mutates_global": False,
        "natal_overlay": overlay,
    }


def build_day_package_manifest_v1(
    story: dict[str, Any] | None = None,
    global_day: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Version stamps for an immutable day package. GET must not recompute."""
    st = _as_dict(story)
    gd = _as_dict(global_day)
    trace = _as_dict(st.get("trace"))
    scen = _as_dict(st.get("day_scenario"))
    return {
        "contract_version": "day_package_manifest_v1",
        "immutable": True,
        "ephemeris_version": str(trace.get("ephemeris_version") or "sky_geometry_v1"),
        "astro_rules_version": str(trace.get("astro_rules_version") or "amc_v1"),
        "scoring_version": str(gd.get("scoring_version") or GLOBAL_DAY_ENGINE_V1),
        "timeline_rules_version": GLOBAL_DAY_ENGINE_V1,
        "natal_overlay_version": "natal_overlay_v1",
        "canon_lookup_version": "thin_v0",
        "global_prompt_version": str(trace.get("prompt_version") or ""),
        "personal_prompt_version": "",
        "card_catalog_version": "card_base_v1",
        "number_catalog_version": "number_base_v1",
        "color_catalog_version": "color_catalog_v1",
        "today_contract_version": "today_contract_v1",
        "scenario_generation_source": str(scen.get("generation_source") or ""),
    }


def build_daily_actions_v1(story: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Typed actions from practice_recommendation + primary-scene goals. No invent."""
    st = _as_dict(story)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _push(kind: str, text: str, *, origin: str | None = None) -> None:
        k = kind if kind in DAILY_ACTION_KINDS else ""
        t = str(text or "").strip()
        if not k or not t:
            return
        key = f"{k}:{t.lower()}"
        if key in seen:
            return
        seen.add(key)
        row: dict[str, Any] = {"kind": k, "text": t}
        if origin:
            row["origin_scene_id"] = origin
        out.append(row)

    rec = st.get("practice_recommendation") if isinstance(st.get("practice_recommendation"), dict) else {}
    rec_kind = str(rec.get("kind") or "").strip().lower()
    if rec_kind == "promise":
        rec_kind = "affirmation"
    if rec_kind == "ascetic":
        rec_kind = "practice"
    _push(rec_kind, str(rec.get("text") or ""), origin=str(rec.get("origin_scene_id") or "") or None)

    scen = _as_dict(st.get("day_scenario"))
    props = _as_dict(scen.get("props"))
    primary_id = str(scen.get("primary_scene_id") or "")
    for goal in _as_list(props.get("goals")):
        if not isinstance(goal, dict):
            continue
        origin = str(goal.get("origin_scene_id") or "")
        if primary_id and origin and origin != primary_id:
            continue
        _push("goal", str(goal.get("text") or goal.get("title") or ""), origin=origin or None)
    for aff in _as_list(props.get("affirmations")):
        if not isinstance(aff, dict):
            continue
        origin = str(aff.get("origin_scene_id") or "")
        if primary_id and origin and origin != primary_id:
            continue
        _push("affirmation", str(aff.get("text") or ""), origin=origin or None)
    return out[:4]
