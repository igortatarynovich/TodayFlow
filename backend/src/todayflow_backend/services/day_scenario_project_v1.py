"""Project day_scenario_v1 → day_story / today_contract slots (Phase B3).

Public contract shape stays today_contract_v1 + day_story nest.
Meaning authority for projected fields: day_scenario (when present & valid).

Legacy paths that no longer set meaning after projection:
- celestial date-preset color as user recommendation (seed only)
- empty facts-only expect/trap when scenario scenes exist
- formula bank (still QA-only; never projected)

Missing scenes: do not invent editorial slots; keep unavailable if already;
attach scenario meta with scenes=[].

Canon: docs/DAY_SCENARIO_V1.md · docs/audits/DAY_SCENARIO_WIRE_PROJECTION_B3.md
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_scenario_v1 import (
    PRODUCT_SPHERE_IDS,
    validate_day_scenario_v1,
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

PROJECTION_MAP = {
    "expect": "conflict + primary scene opportunity/what_happens",
    "trap": "primary scene.trap",
    "do": "props.goals[0] or primary scene.recommended_action",
    "avoid": "primary scene.do_not",
    "primary_action": "same as do[0]",
    "today_move": "same as do[0]",
    "domains.*": "scenes grouped by wire lens",
    "talisman.color": "props.color.name",
    "talisman.note": "props.color.link_to_conflict (+ avoid hint)",
    "practice_recommendation": "props.affirmations[0] as kind=affirmation",
    "day_thesis / primary_conflict": "conflict.thesis / short_name",
    "events_lead": "foundation.ranked_drivers fact_ru",
    "interpretive_chorus": "chorus voices (card/number/astro/natal)",
    "day_scenario": "full internal nest (runtime_sot flag)",
}

LEGACY_NON_SOT = (
    "celestial_events.daily_symbols.color catalog copy as user why",
    "date_preset color selection as meaning SoT",
    "formula_bank runtime prose",
    "independent tarot/numerology forecast modules on Today",
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


def _chorus_public(chorus: dict[str, Any]) -> dict[str, Any]:
    """Slim chorus for day_story public nest — explanation layer, not second plot."""
    astro = _as_list(chorus.get("astrology"))
    natal = _as_list(chorus.get("natal"))
    card = _as_dict(chorus.get("day_card"))
    number = _as_dict(chorus.get("day_number"))
    return {
        "astrology_lead": _clip((astro[0] or {}).get("named_factor") if astro else "", 220),
        "astrology_meaning": _clip((astro[0] or {}).get("human_meaning") if astro else "", 280),
        "day_card": {
            "named": card.get("named_factor"),
            "role": card.get("archetype_role") or card.get("link_to_conflict"),
        }
        if card
        else None,
        "day_number": {
            "named": number.get("named_factor"),
            "tempo": number.get("tempo"),
            "style": number.get("style"),
            "for_conflict": number.get("link_to_conflict") or number.get("human_meaning"),
        }
        if number
        else None,
        "natal_lead": _clip((natal[0] or {}).get("named_factor") if natal else "", 220),
        "dialogue_rule": chorus.get("dialogue_rule"),
        "parallel_forecast_forbidden": True,
    }


def _domains_from_scenes(scenes: list[Any]) -> dict[str, dict[str, Any]]:
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
        # Prefer support opportunity / risk from first matching scene
        out[did] = {
            "status": _clip(primary.get("what_happens"), 200),
            "opportunity": _clip(primary.get("opportunity"), 240),
            "risk": _clip(primary.get("trap"), 240),
            "action": _clip(primary.get("recommended_action"), 200),
            "evidence_status": "present",
            "origin_scene_id": primary.get("scene_id"),
        }
    return out


def project_day_scenario_onto_day_story_v1(
    story: dict[str, Any] | None,
    scenario: dict[str, Any] | None,
    *,
    fill_empty_editorial: bool = True,
) -> dict[str, Any]:
    """Merge scenario meaning into day_story slots. Returns new story dict.

    - Always attaches ``day_scenario`` + ``interpretive_chorus`` when scenario validates.
    - Always projects color / affirmation / thesis / events_lead when props/scenes exist.
    - Fills empty expect/trap/do/avoid from scenes when ``fill_empty_editorial``
      (including recovering from ``interpretation_status=unavailable``).
    - Missing scenes: no invented editorial; unavailable preserved if already set.
    """
    base = dict(story) if isinstance(story, dict) else {}
    scen = scenario if isinstance(scenario, dict) else None
    if scen is None:
        return base

    errors = validate_day_scenario_v1(scen)
    # Allow projection even with soft errors except total break
    hard = [e for e in errors if e in {"scenario_not_dict", "bad_contract_version", "scenes_empty", "conflict_missing_short_name"}]
    scenes = _as_list(scen.get("scenes"))
    conflict = _as_dict(scen.get("conflict"))
    props = _as_dict(scen.get("props"))
    foundation = _as_dict(scen.get("foundation"))
    chorus = _as_dict(scen.get("chorus"))
    primary = _primary_scene(scenes)

    editorial = dict(_as_dict(base.get("editorial")))
    editorial["projection_map"] = PROJECTION_MAP
    editorial["legacy_non_sot"] = list(LEGACY_NON_SOT)
    editorial["scenario_version"] = scen.get("version")
    editorial["scenario_validate_errors"] = errors

    # Always attach full scenario for meta / future UI (B4)
    base["day_scenario"] = {
        **scen,
        "runtime_sot": True,  # meaning authority for projected fields on this story
        "wire_projection": "day_scenario_project_v1",
    }
    base["interpretive_chorus"] = _chorus_public(chorus)

    if hard or not primary:
        editorial["runtime_source"] = "scenario_meta_only"
        editorial["projection_note"] = (
            "Scenario attached but scenes missing/invalid — editorial slots not invented."
        )
        base["editorial"] = editorial
        return base

    # Thesis / conflict label
    thesis = _as_dict(conflict.get("thesis"))
    label = str(conflict.get("short_name") or thesis.get("label_ru") or "").strip()
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

    # events_lead from drivers
    facts = [
        str(d.get("fact_ru") or "").strip()
        for d in _as_list(foundation.get("ranked_drivers"))
        if isinstance(d, dict) and d.get("fact_ru")
    ]
    if facts:
        base["events_lead"] = _clip(" ".join(facts[:3]), 480)

    # Domains from scenes (fill empty lenses; do not wipe rich LLM prose if present)
    scene_domains = _domains_from_scenes(scenes)
    domains = dict(_as_dict(base.get("domains")))
    for did, lens in scene_domains.items():
        existing = _as_dict(domains.get(did))
        has_prose = bool(
            str(existing.get("opportunity") or "").strip()
            or str(existing.get("risk") or "").strip()
            or str(existing.get("action") or "").strip()
        )
        if not has_prose:
            domains[did] = lens
    base["domains"] = domains

    # Color / avoid from props (scenario SoT — overrides catalog seed on talisman)
    color = _as_dict(props.get("color"))
    avoid = _as_dict(props.get("avoid_color"))
    talisman = dict(_as_dict(base.get("talisman")))
    if color.get("name"):
        talisman["color"] = str(color["name"])
        note_parts = [
            _clip(color.get("link_to_conflict"), 160),
            _clip(color.get("expected_effect_today"), 120),
        ]
        if avoid.get("name"):
            note_parts.append(
                _clip(f"Избегать: {avoid.get('name')} — {avoid.get('why')}", 160)
            )
        talisman["note"] = _clip(" ".join(p for p in note_parts if p), 280)
        talisman["origin_scene_id"] = color.get("origin_scene_id")
        talisman["avoid_color"] = avoid.get("name")
        talisman["avoid_why"] = avoid.get("why")
        base["talisman"] = talisman

    # Affirmation → practice_recommendation
    affirms = _as_list(props.get("affirmations"))
    if affirms and isinstance(affirms[0], dict) and affirms[0].get("text"):
        a0 = affirms[0]
        base["practice_recommendation"] = {
            "kind": "affirmation",
            "text": _clip(a0.get("text"), 240),
            "reason": _clip(a0.get("compensates_trap") or a0.get("helps_action"), 200),
            "origin_scene_id": a0.get("origin_scene_id"),
        }

    # Goals → development / optional today_move seed
    goals = _as_list(props.get("goals"))
    if goals and isinstance(goals[0], dict) and goals[0].get("text"):
        if not str(base.get("development_point") or "").strip():
            base["development_point"] = _clip(goals[0].get("text"), 240)

    unavailable = str(base.get("interpretation_status") or "").strip() == "unavailable"
    expect_empty = not str(base.get("expect") or base.get("direction") or "").strip()
    trap_empty = not str(base.get("trap") or base.get("abstain") or "").strip()
    do_empty = not _as_list(base.get("do"))

    filled_from_scenario = False
    if fill_empty_editorial and (unavailable or expect_empty or trap_empty or do_empty):
        if expect_empty or unavailable:
            base["expect"] = _clip(
                f"{primary.get('what_happens')} {primary.get('opportunity')}".strip(),
                400,
            )
            filled_from_scenario = True
        if trap_empty or unavailable:
            base["trap"] = _clip(primary.get("trap"), 320)
            filled_from_scenario = True
        if do_empty or unavailable:
            do_text = ""
            if goals and isinstance(goals[0], dict):
                do_text = str(goals[0].get("text") or "")
            if not do_text:
                do_text = str(primary.get("recommended_action") or "")
            do_list = [_clip(do_text, 240)] if do_text else []
            # Secondary do from second scene / goal so validate_day_story (>=2) passes
            if len(goals) > 1 and isinstance(goals[1], dict) and goals[1].get("text"):
                do_list.append(_clip(goals[1].get("text"), 240))
            elif len(scenes) > 1 and isinstance(scenes[1], dict):
                alt = _clip(scenes[1].get("recommended_action"), 240)
                if alt and alt not in do_list:
                    do_list.append(alt)
            if len(do_list) == 1:
                force_a = str(_as_dict(conflict.get("opposing_forces")).get("a") or "автопилот")
                do_list.append(
                    _clip(f"Заметить момент «{force_a}» и не усилить его.", 240)
                )
            base["do"] = do_list
            base["today_move"] = _clip(do_list[0] if do_list else do_text, 200)
            base["primary_action"] = _clip(do_list[0] if do_list else do_text, 200)
            filled_from_scenario = True
        if not _as_list(base.get("avoid")):
            avoid_list = []
            avoid_text = _clip(primary.get("do_not"), 240)
            if avoid_text:
                avoid_list.append(avoid_text)
            force_a = str(_as_dict(conflict.get("opposing_forces")).get("a") or "автопилот")
            avoid_list.append(
                _clip(f"Не усиливать стратегию «{force_a}» ради ложной гармонии.", 240)
            )
            base["avoid"] = avoid_list[:3]
            filled_from_scenario = True
        if not str(base.get("direction") or "").strip():
            base["direction"] = _clip(base.get("expect") or primary.get("opportunity"), 320)
        if not str(base.get("advantage") or "").strip():
            base["advantage"] = _clip(primary.get("opportunity"), 280)
        if not str(base.get("abstain") or "").strip():
            base["abstain"] = _clip(base.get("trap") or primary.get("trap"), 280)
        if not str(base.get("story") or "").strip():
            base["story"] = _clip(primary.get("domestic_example") or primary.get("what_happens"), 400)
            filled_from_scenario = True
        if not str(base.get("evening_closure") or "").strip():
            base["evening_closure"] = _clip(
                f"Если удержали «{label}» — к вечеру яснее, где выбрали осознанно.",
                280,
            )
        if not str(base.get("global_period") or "").strip():
            base["global_period"] = label

        if filled_from_scenario and (
            str(base.get("expect") or "").strip() or str(base.get("trap") or "").strip()
        ):
            base["interpretation_status"] = "ok"
            base.pop("interpretation_unavailable_message", None)
            editorial["runtime_source"] = "day_scenario_v1"
            editorial["recovered_from_unavailable"] = unavailable
        elif unavailable:
            editorial["runtime_source"] = "unavailable_with_scenario_meta"
    else:
        editorial["runtime_source"] = editorial.get("runtime_source") or "llm_with_scenario_overlay"
        editorial["scenario_overlay"] = ["talisman", "practice_recommendation", "domains_fill", "thesis", "chorus"]

    # Strong/weak as editorial hint for FE (B4)
    editorial["strong_spheres"] = props.get("strong_spheres") or []
    editorial["weak_spheres"] = props.get("weak_spheres") or []
    editorial["goals"] = goals
    if props.get("humor"):
        editorial["humor"] = props.get("humor")

    base["editorial"] = editorial

    # Mark scenario as SoT for projected fields on this payload
    if isinstance(base.get("day_scenario"), dict):
        base["day_scenario"]["runtime_sot"] = True

    # Ensure product sphere ids referenced stay documented
    _ = PRODUCT_SPHERE_IDS

    return base


def build_and_project_day_scenario_v1(
    *,
    story: dict[str, Any],
    interpretation: dict[str, Any] | None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    day_thesis: dict[str, Any] | None = None,
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
    )
    return project_day_scenario_onto_day_story_v1(story, scenario)
