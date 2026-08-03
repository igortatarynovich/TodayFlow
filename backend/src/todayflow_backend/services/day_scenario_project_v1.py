"""Project day_scenario_v1 → day_story / today_contract slots (Phase B5 exclusive SoT).

Meaning authority: day_scenario only (when scenes valid).
Legacy expect/trap/do/avoid/domains/LLM prose are projections or discarded —
they never remain as parallel meaning SoT.

Modes:
- scenario ready → interpretation_status=ok; all meaning slots overwritten from scenario
- scenario not ready (no/invalid scenes) → unavailable; strip editorial meaning;
  keep facts + scenario meta + honest message

Canon: docs/DAY_SCENARIO_V1.md · docs/audits/DAY_SCENARIO_RUNTIME_SOT_B5.md
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_scenario_v1 import (
    PRODUCT_SPHERE_IDS,
    build_scenario_props_v1,
    build_scenario_scenes_v1,
    is_calendar_driver_row,
    is_calendar_kitchen_fact,
    sanitize_conflict_short_name,
    scene_copy_needs_heal_v1,
    validate_day_scenario_v1,
)

_UNAVAILABLE_RU = (
    "Мы не смогли подготовить персональную интерпретацию дня. "
    "Попробуйте обновить экран через несколько минут."
)

# Product sphere → wire DomainLens id (Model B)
_SPHERE_TO_WIRE: dict[str, str] = {
    "work_decisions": "money_work",
    "money": "money_work",
    "relationships": "relationships",
    "communication": "relationships",
    "home": "family",
    # energy/creativity/travel have no dedicated wire lens — fold softly
    "energy_body": "money_work",
    "creativity": "money_work",
    "rest_travel": "family",
}

_WIRE_DOMAIN_IDS = ("relationships", "money_work", "family")

PROJECTION_VERSION = "day_scenario_project_v1.b5"

PROJECTION_MAP = {
    "expect": "conflict + primary scene opportunity/what_happens",
    "trap": "primary scene.trap",
    "do": "props.goals[0] or primary scene.recommended_action",
    "avoid": "primary scene.do_not",
    "primary_action": "same as do[0]",
    "today_move": "same as do[0]",
    "domains.*": "scenes grouped by wire lens (overwrite)",
    "talisman.color": "props.color.name",
    "talisman.note": "props.color.link_to_conflict (+ avoid hint)",
    "practice_recommendation": "props.affirmations[0] as kind=affirmation",
    "day_thesis / primary_conflict": "conflict.thesis / short_name",
    "events_lead": "foundation.ranked_drivers fact_ru",
    "interpretive_chorus": "chorus voices (card/number/astro/natal)",
    "day_scenario": "full internal nest (runtime_sot exclusive)",
}

LEGACY_NON_SOT = (
    "celestial_events.daily_symbols.color catalog copy as user why",
    "date_preset color selection as meaning SoT",
    "formula_bank runtime prose",
    "independent tarot/numerology forecast modules on Today",
    "LLM day_story expect/trap/do/avoid as parallel SoT",
    "domains editorial prose as scene SoT",
    "llm_with_scenario_overlay hybrid mode",
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clip(value: Any, n: int = 400) -> str:
    text = str(value or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def _primary_scene(scenes: list[Any]) -> dict[str, Any] | None:
    for sc in scenes:
        if isinstance(sc, dict) and sc.get("role_in_story") == "primary":
            return sc
    for sc in scenes:
        if isinstance(sc, dict):
            return sc
    return None


def _origin_conflict_id(conflict: dict[str, Any]) -> str:
    label = str(conflict.get("short_name") or "").strip()
    if label:
        return f"conflict:{label}"
    drivers = _as_list(conflict.get("driver_ids"))
    if drivers:
        return f"conflict:drivers:{'+'.join(str(d) for d in drivers[:3])}"
    return "conflict:unknown"


def _field_provenance(
    *,
    origin_scene_id: str | None,
    origin_conflict_id: str,
    evidence_refs: list[Any] | None = None,
    source_kind: str = "day_scenario_v1",
) -> dict[str, Any]:
    return {
        "source_kind": source_kind,
        "origin_scene_id": origin_scene_id,
        "origin_conflict_id": origin_conflict_id,
        "evidence_refs": list(evidence_refs or [])[:8],
        "projection_version": PROJECTION_VERSION,
    }


def _is_kitchen_natal_lead(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    return bool(
        re.search(
            r"Firdaria|ZR\s*Fortune|ZR\s*Spirit|Лоты\s*soft|Vimshottari|BaZi|"
            r"HD\s*soft|Variables\s*soft|Solar\s*return|time[_\s-]?lords|"
            r"управител|прогрес+и|нет\s+ASC",
            t,
            re.IGNORECASE,
        )
    )


def _chorus_public(chorus: dict[str, Any]) -> dict[str, Any]:
    """Slim chorus for day_story public nest — explanation layer, not second plot."""
    astro = _as_list(chorus.get("astrology"))
    natal = _as_list(chorus.get("natal"))
    card = _as_dict(chorus.get("day_card"))
    number = _as_dict(chorus.get("day_number"))
    astro0 = _as_dict(astro[0]) if astro else {}
    natal0: dict[str, Any] = {}
    for row in natal:
        if not isinstance(row, dict):
            continue
        named = str(row.get("named_factor") or "").strip()
        if named and not _is_kitchen_natal_lead(named):
            natal0 = row
            break
    if not natal0 and natal:
        # Soft fallback without dumping kitchen named_factor
        natal0 = {
            "named_factor": "Личный фон усиливает сегодняшний сюжет.",
            "human_meaning": _as_dict(natal[0]).get("human_meaning"),
            "evidence_refs": _as_dict(natal[0]).get("evidence_refs")
            or _as_dict(natal[0]).get("evidence_ids")
            or [],
        }
    return {
        "astrology_lead": _clip(astro0.get("named_factor"), 220),
        "astrology_meaning": _clip(astro0.get("human_meaning"), 280),
        "day_card": {
            "named": card.get("named_factor"),
            "role": card.get("archetype_role") or card.get("link_to_conflict"),
            "evidence_refs": list(card.get("evidence_refs") or card.get("evidence_references") or [])[:4],
        }
        if card
        else None,
        "day_number": {
            "named": number.get("named_factor"),
            "tempo": number.get("tempo"),
            "style": number.get("style"),
            "for_conflict": number.get("link_to_conflict") or number.get("human_meaning"),
            "evidence_refs": list(
                number.get("evidence_refs") or number.get("evidence_references") or []
            )[:4],
        }
        if number
        else None,
        "natal_lead": _clip(natal0.get("named_factor"), 220) if natal0 else "",
        "dialogue_rule": chorus.get("dialogue_rule"),
        "parallel_forecast_forbidden": True,
        "evidence_refs": {
            "astrology": list(astro0.get("evidence_refs") or astro0.get("event_ids") or [])[:4],
            "natal": list(
                natal0.get("evidence_refs")
                or natal0.get("activation_ids")
                or natal0.get("evidence_ids")
                or []
            )[:4],
        },
    }


def _domains_from_scenes(
    scenes: list[Any],
    *,
    origin_conflict_id: str,
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {d: [] for d in _WIRE_DOMAIN_IDS}
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        sphere = str(sc.get("sphere") or "")
        wire = _SPHERE_TO_WIRE.get(sphere)
        if wire in buckets:
            buckets[wire].append(sc)

    out: dict[str, dict[str, Any]] = {}
    for did, rows in buckets.items():
        if not rows:
            continue
        primary = rows[0]
        origin_scene = primary.get("scene_id")
        out[did] = {
            "status": _clip(primary.get("what_happens"), 200),
            "opportunity": _clip(primary.get("opportunity"), 240),
            "risk": _clip(primary.get("trap"), 240),
            "action": _clip(primary.get("recommended_action"), 200),
            "evidence_status": "present",
            "origin_scene_id": origin_scene,
            "provenance": _field_provenance(
                origin_scene_id=str(origin_scene) if origin_scene else None,
                origin_conflict_id=origin_conflict_id,
                evidence_refs=_as_list(primary.get("evidence_references")),
            ),
        }
    return out


def _strip_meaning_slots(base: dict[str, Any]) -> None:
    """Remove user-facing editorial so unavailable cannot leak legacy story."""
    base["expect"] = ""
    base["trap"] = ""
    base["direction"] = ""
    base["advantage"] = ""
    base["abstain"] = ""
    base["story"] = ""
    base["do"] = []
    base["avoid"] = []
    base["today_move"] = ""
    base["primary_action"] = ""
    base["development_point"] = ""
    base["vibe_closing"] = ""
    base["vibe_strokes"] = []
    base["supports_story"] = ""
    base["evening_closure"] = ""
    base["practice_recommendation"] = None
    base.pop("talisman", None)
    # Domains: keep structure empty — contract maps unavailable → empty lenses
    base["domains"] = {}


_FORCE_PASTE_AFFIRM_RE = re.compile(
    r"Мне не нужно выбирать «.+», чтобы сохранить лицо дня",
    re.IGNORECASE,
)


def _heal_template_scene_copy(
    scen: dict[str, Any],
    *,
    person_name: str | None = None,
) -> dict[str, Any]:
    """Rewrite force-paste scene/props templates and mashed short_name on serve."""
    scenes = scen.get("scenes")
    conflict = _as_dict(scen.get("conflict"))
    chorus = _as_dict(scen.get("chorus"))
    foundation = _as_dict(scen.get("foundation"))
    props = _as_dict(scen.get("props"))
    raw_short = str(conflict.get("short_name") or "")
    clean_short = sanitize_conflict_short_name(raw_short)
    short_needs = bool(clean_short and clean_short != raw_short.strip().rstrip(".!?"))
    affirm_blob = " ".join(
        str(a.get("text") or "")
        for a in _as_list(props.get("affirmations"))
        if isinstance(a, dict)
    )
    props_need = bool(_FORCE_PASTE_AFFIRM_RE.search(affirm_blob))
    scenes_need = scene_copy_needs_heal_v1(scenes if isinstance(scenes, list) else None)
    if not (scenes_need or short_needs or props_need):
        return scen
    if not conflict or not foundation:
        # Still heal short_name in place when possible
        if short_needs and conflict:
            healed_min = dict(scen)
            c = dict(conflict)
            c["short_name"] = clean_short
            healed_min["conflict"] = c
            return healed_min
        return scen
    prior = [s for s in (scenes or []) if isinstance(s, dict)]
    domains: list[str] = []
    for s in prior:
        wire = _SPHERE_TO_WIRE.get(str(s.get("sphere") or ""))
        if wire and wire not in domains:
            domains.append(wire)
    healed = dict(scen)
    c = dict(conflict)
    if clean_short:
        c["short_name"] = clean_short
    healed["conflict"] = c
    if scenes_need or props_need:
        new_scenes = build_scenario_scenes_v1(
            conflict=c,
            chorus=chorus,
            foundation=foundation,
            interpretation={"domains_present": domains} if domains else None,
            max_scenes=max(len(prior), 3),
            person_name=person_name,
        )
        healed["scenes"] = new_scenes
        from todayflow_backend.services.today_domain_verdicts_v1 import (
            day_favorable_from_activations,
        )

        healed["props"] = build_scenario_props_v1(
            conflict=c,
            scenes=new_scenes,
            chorus=chorus,
            day_favorable=day_favorable_from_activations(
                foundation.get("personal_natal_activations") or []
            ),
        )
    return healed


def project_day_scenario_onto_day_story_v1(
    story: dict[str, Any] | None,
    scenario: dict[str, Any] | None,
    *,
    exclusive_runtime_sot: bool = True,
    person_name: str | None = None,
) -> dict[str, Any]:
    """Merge scenario meaning into day_story slots. Returns new story dict.

    B5: with valid scenes, overwrite all meaning slots from scenario.
    Legacy LLM/catalog prose is never kept as parallel SoT.
    ``exclusive_runtime_sot`` must stay True in runtime (parameter retained for
    call-site clarity / Architecture impact).
    """
    if not exclusive_runtime_sot:
        raise ValueError("exclusive_runtime_sot=False is retired (B5); scenario is sole meaning SoT")

    base = dict(story) if isinstance(story, dict) else {}
    scen = scenario if isinstance(scenario, dict) else None
    if scen is None:
        # No scenario → cannot claim interpretation
        _strip_meaning_slots(base)
        base["interpretation_status"] = "unavailable"
        base["interpretation_unavailable_message"] = _UNAVAILABLE_RU
        editorial = dict(_as_dict(base.get("editorial")))
        editorial["runtime_source"] = "facts_only_unavailable"
        editorial["projection_version"] = PROJECTION_VERSION
        editorial["legacy_non_sot"] = list(LEGACY_NON_SOT)
        base["editorial"] = editorial
        base.pop("day_scenario", None)
        base.pop("interpretive_chorus", None)
        return base

    scen = _heal_template_scene_copy(scen, person_name=person_name)

    errors = validate_day_scenario_v1(scen)
    hard = [
        e
        for e in errors
        if e
        in {
            "scenario_not_dict",
            "bad_contract_version",
            "scenes_empty",
            "conflict_missing_short_name",
        }
    ]
    scenes = _as_list(scen.get("scenes"))
    conflict = _as_dict(scen.get("conflict"))
    props = _as_dict(scen.get("props"))
    foundation = _as_dict(scen.get("foundation"))
    chorus = _as_dict(scen.get("chorus"))
    primary = _primary_scene(scenes)
    origin_conflict = _origin_conflict_id(conflict)
    driver_ids = list(conflict.get("driver_ids") or [])[:5]

    editorial = dict(_as_dict(base.get("editorial")))
    editorial["projection_map"] = PROJECTION_MAP
    editorial["legacy_non_sot"] = list(LEGACY_NON_SOT)
    editorial["scenario_version"] = scen.get("version")
    editorial["scenario_validate_errors"] = errors
    editorial["projection_version"] = PROJECTION_VERSION
    editorial["exclusive_runtime_sot"] = True

    base["day_scenario"] = {
        **scen,
        "runtime_sot": True,
        "wire_projection": PROJECTION_VERSION,
    }
    base["interpretive_chorus"] = _chorus_public(chorus)

    if hard or not primary:
        _strip_meaning_slots(base)
        # Keep factual lead from foundation drivers only (not editorial story)
        facts = [
            str(d.get("fact_ru") or "").strip()
            for d in _as_list(foundation.get("ranked_drivers"))
            if isinstance(d, dict)
            and d.get("fact_ru")
            and not is_calendar_driver_row(d)
            and not is_calendar_kitchen_fact(str(d.get("fact_ru") or ""))
        ]
        if facts:
            base["events_lead"] = _clip(" ".join(facts[:3]), 480)
        elif "events_lead" in base:
            # Drop cached calendar-only lead
            base.pop("events_lead", None)
        label = sanitize_conflict_short_name(conflict.get("short_name") or "")
        if label:
            base["theme"] = label
            base["headline_anchor"] = label
            base["primary_conflict"] = label
            base["global_period"] = label
        base["interpretation_status"] = "unavailable"
        base["interpretation_unavailable_message"] = _UNAVAILABLE_RU
        editorial["runtime_source"] = "scenario_meta_only"
        editorial["projection_note"] = (
            "Scenario attached but scenes missing/invalid — meaning slots stripped; "
            "facts-only unavailable shell."
        )
        base["editorial"] = editorial
        if isinstance(base.get("day_scenario"), dict):
            base["day_scenario"]["runtime_sot"] = False
            base["day_scenario"]["ready"] = False
        return base

    # --- Exclusive overwrite path ---
    thesis = _as_dict(conflict.get("thesis"))
    label = sanitize_conflict_short_name(
        conflict.get("short_name") or thesis.get("label_ru") or ""
    )
    if isinstance(base.get("day_scenario"), dict) and label:
        # Heal cached mashed short_name on serve/reproject
        c = dict(_as_dict(base["day_scenario"].get("conflict")))
        if c:
            c["short_name"] = label
            base["day_scenario"] = {**base["day_scenario"], "conflict": c}
    scene_id = str(primary.get("scene_id") or "")
    scene_evidence = _as_list(primary.get("evidence_references")) or driver_ids

    if label:
        base["theme"] = label
        base["headline_anchor"] = label
        base["primary_conflict"] = label
        base["global_period"] = label
        base["day_thesis"] = {
            "family": thesis.get("family") or "momentum",
            "variant": thesis.get("variant") or "steady_productive_rhythm",
            "mode": thesis.get("mode") or "stability",
            "label_ru": label,
            "driver_ids": list(conflict.get("driver_ids") or [])[:3],
            "composition_ids": list(thesis.get("composition_ids") or [])[:3],
        }

    facts = [
        str(d.get("fact_ru") or "").strip()
        for d in _as_list(foundation.get("ranked_drivers"))
        if isinstance(d, dict)
        and d.get("fact_ru")
        and not is_calendar_driver_row(d)
        and not is_calendar_kitchen_fact(str(d.get("fact_ru") or ""))
    ]
    if facts:
        base["events_lead"] = _clip(" ".join(facts[:3]), 480)
    else:
        base.pop("events_lead", None)

    # Domains: full overwrite from scenes (empty lenses for uncovered wire ids)
    scene_domains = _domains_from_scenes(scenes, origin_conflict_id=origin_conflict)
    base["domains"] = scene_domains

    # Color / avoid from props only
    color = _as_dict(props.get("color"))
    avoid = _as_dict(props.get("avoid_color"))
    if color.get("name"):
        note_parts = [
            _clip(color.get("link_to_conflict"), 160),
            _clip(color.get("expected_effect_today"), 120),
        ]
        if avoid.get("name"):
            note_parts.append(
                _clip(f"Избегать: {avoid.get('name')} — {_clip(avoid.get('why'), 100)}", 160)
            )
        base["talisman"] = {
            "color": str(color["name"]),
            "note": _clip(" ".join(p for p in note_parts if p), 280),
            "origin_scene_id": color.get("origin_scene_id"),
            "avoid_color": avoid.get("name"),
            "avoid_why": avoid.get("why"),
            "provenance": _field_provenance(
                origin_scene_id=str(color.get("origin_scene_id") or scene_id or None),
                origin_conflict_id=origin_conflict,
                evidence_refs=scene_evidence,
            ),
        }
    else:
        base.pop("talisman", None)

    affirms = _as_list(props.get("affirmations"))
    if affirms and isinstance(affirms[0], dict) and affirms[0].get("text"):
        a0 = affirms[0]
        text = _clip(a0.get("text"), 200)
        # Prefer trap-compensation as reason; never repeat the affirmation text.
        reason_raw = _clip(a0.get("compensates_trap"), 120) or _clip(a0.get("helps_action"), 160)
        reason = reason_raw if reason_raw and reason_raw.lower() != text.lower() else ""
        base["practice_recommendation"] = {
            "kind": "affirmation",
            "text": text,
            "reason": reason or None,
            "origin_scene_id": a0.get("origin_scene_id"),
            "provenance": _field_provenance(
                origin_scene_id=str(a0.get("origin_scene_id") or None),
                origin_conflict_id=origin_conflict,
                evidence_refs=scene_evidence,
            ),
        }
    else:
        base["practice_recommendation"] = None

    goals = _as_list(props.get("goals"))
    if goals and isinstance(goals[0], dict) and goals[0].get("text"):
        base["development_point"] = _clip(goals[0].get("text"), 240)
    else:
        base["development_point"] = _clip(primary.get("recommended_action"), 240)

    # Editorial slots — always from scenario
    base["expect"] = _clip(
        f"{primary.get('what_happens')} {primary.get('opportunity')}".strip(),
        400,
    )
    base["trap"] = _clip(primary.get("trap"), 320)
    base["direction"] = _clip(primary.get("opportunity") or base["expect"], 320)
    base["advantage"] = _clip(primary.get("opportunity"), 280)
    base["abstain"] = _clip(primary.get("trap"), 280)
    base["story"] = _clip(
        primary.get("domestic_example") or primary.get("what_happens"),
        400,
    )

    do_text = ""
    if goals and isinstance(goals[0], dict):
        do_text = str(goals[0].get("text") or "")
    if not do_text:
        do_text = str(primary.get("recommended_action") or "")
    do_list = [_clip(do_text, 240)] if do_text else []
    if len(goals) > 1 and isinstance(goals[1], dict) and goals[1].get("text"):
        do_list.append(_clip(goals[1].get("text"), 240))
    elif len(scenes) > 1 and isinstance(scenes[1], dict):
        alt = _clip(scenes[1].get("recommended_action"), 240)
        if alt and alt not in do_list:
            do_list.append(alt)
    if len(do_list) == 1:
        # v3.1 seed-kill: no opposing_forces quote as filler do-line
        do_list.append(_clip("Заметить момент автопилота и не усилить его.", 240))
    base["do"] = do_list
    base["today_move"] = _clip(do_list[0] if do_list else do_text, 200)
    base["primary_action"] = _clip(do_list[0] if do_list else do_text, 200)

    avoid_list: list[str] = []
    avoid_text = _clip(primary.get("do_not"), 240)
    if avoid_text:
        avoid_list.append(avoid_text)
    # v3.1: generic avoid — never paste force_a / short_name into day_story avoid
    avoid_list.append(
        _clip("Не усиливать привычный автопилот ради ложной гармонии.", 240)
    )
    base["avoid"] = avoid_list[:3]

    base["evening_closure"] = _clip(
        "Если удержали тон дня — к вечеру яснее, где выбрали осознанно.",
        280,
    )

    # Provenance for primary slots (editorial nest for capture packs)
    editorial["slot_provenance"] = {
        "expect": _field_provenance(
            origin_scene_id=scene_id or None,
            origin_conflict_id=origin_conflict,
            evidence_refs=scene_evidence,
        ),
        "trap": _field_provenance(
            origin_scene_id=scene_id or None,
            origin_conflict_id=origin_conflict,
            evidence_refs=scene_evidence,
        ),
        "do": _field_provenance(
            origin_scene_id=str(
                (goals[0].get("origin_scene_id") if goals and isinstance(goals[0], dict) else None)
                or scene_id
                or None
            ),
            origin_conflict_id=origin_conflict,
            evidence_refs=scene_evidence,
        ),
        "avoid": _field_provenance(
            origin_scene_id=scene_id or None,
            origin_conflict_id=origin_conflict,
            evidence_refs=scene_evidence,
        ),
        "talisman": _field_provenance(
            origin_scene_id=str(color.get("origin_scene_id") or scene_id or None),
            origin_conflict_id=origin_conflict,
            evidence_refs=scene_evidence,
        ),
    }
    editorial["strong_spheres"] = props.get("strong_spheres") or []
    editorial["weak_spheres"] = props.get("weak_spheres") or []
    editorial["goals"] = goals
    if props.get("humor"):
        editorial["humor"] = props.get("humor")
    editorial["runtime_source"] = "day_scenario_v1"
    editorial.pop("scenario_overlay", None)
    editorial.pop("recovered_from_unavailable", None)

    base["interpretation_status"] = "ok"
    base.pop("interpretation_unavailable_message", None)
    base["editorial"] = editorial

    if isinstance(base.get("day_scenario"), dict):
        base["day_scenario"]["runtime_sot"] = True
        base["day_scenario"]["ready"] = True

    _ = PRODUCT_SPHERE_IDS
    return base


def build_and_project_day_scenario_v1(
    *,
    story: dict[str, Any],
    interpretation: dict[str, Any] | None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    day_thesis: dict[str, Any] | None = None,
    person_name: str | None = None,
) -> dict[str, Any]:
    """Convenience: build scenario from interpretation and project onto story."""
    from todayflow_backend.services.day_scenario_v1 import build_day_scenario_v1

    interp = interpretation if isinstance(interpretation, dict) else {}
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=interp.get("day_events_pack")
        if isinstance(interp.get("day_events_pack"), dict)
        else None,
        day_thesis=day_thesis
        if isinstance(day_thesis, dict)
        else (interp.get("day_thesis") if isinstance(interp.get("day_thesis"), dict) else None),
        ritual_context=ritual_context,
        celestial_events=celestial_events,
        person_name=person_name,
    )
    return project_day_scenario_onto_day_story_v1(story, scenario, person_name=person_name)
