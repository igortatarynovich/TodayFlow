"""Phase C3.6 — Gate Maturity and Runtime Safety.

Separates **analysis** (always run) from **runtime policy** (maturity-driven).

Maturity ladder (promotion only after calibration evidence):
  experimental → advisory → candidate_blocking → blocking

Canon: docs/audits/DAY_SCENARIO_GATE_MATURITY_C36.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Maturity = Literal["experimental", "advisory", "candidate_blocking", "blocking"]
Family = Literal["hard", "quality"]
RuntimeAction = Literal["score_only", "retry", "downgrade_general", "reject_story"]

MATURITY_EXPERIMENTAL: Maturity = "experimental"
MATURITY_ADVISORY: Maturity = "advisory"
MATURITY_CANDIDATE_BLOCKING: Maturity = "candidate_blocking"
MATURITY_BLOCKING: Maturity = "blocking"

FAMILY_HARD: Family = "hard"
FAMILY_QUALITY: Family = "quality"

# Only maturity=blocking changes user-facing outcome (hard + promoted quality C3.6.3).
# candidate_blocking behaves like advisory in runtime (observe only).
RUNTIME_BLOCKING_MATURITIES = frozenset({MATURITY_BLOCKING})


@dataclass(frozen=True)
class GateRule:
    code: str
    family: Family
    maturity: Maturity
    allow_retry: bool = False
    allow_downgrade: bool = False
    allow_reject: bool = False
    note: str = ""


def _q_exp(code: str, *, note: str = "") -> GateRule:
    return GateRule(
        code=code,
        family=FAMILY_QUALITY,
        maturity=MATURITY_EXPERIMENTAL,
        note=note or "quality analysis — observe only until calibrated",
    )


def _q_adv(code: str, *, note: str = "") -> GateRule:
    return GateRule(
        code=code,
        family=FAMILY_QUALITY,
        maturity=MATURITY_ADVISORY,
        note=note or "quality analysis — score/capture only",
    )


def _q_cand(code: str, *, note: str = "") -> GateRule:
    return GateRule(
        code=code,
        family=FAMILY_QUALITY,
        maturity=MATURITY_CANDIDATE_BLOCKING,
        note=note or "quality — candidate_blocking (observe until full promotion)",
    )


def _q_block(
    code: str,
    *,
    allow_retry: bool = True,
    allow_reject: bool = True,
    note: str = "",
) -> GateRule:
    """Promoted quality rule: still family=quality, maturity=blocking (may retry/reject)."""
    return GateRule(
        code=code,
        family=FAMILY_QUALITY,
        maturity=MATURITY_BLOCKING,
        allow_retry=allow_retry,
        allow_reject=allow_reject,
        note=note
        or "quality promoted after C3.6.2 sealed pilot — retry then unavailable",
    )


def _h_block(
    code: str,
    *,
    allow_retry: bool = False,
    allow_downgrade: bool = False,
    allow_reject: bool = False,
    note: str = "",
) -> GateRule:
    return GateRule(
        code=code,
        family=FAMILY_HARD,
        maturity=MATURITY_BLOCKING,
        allow_retry=allow_retry,
        allow_downgrade=allow_downgrade,
        allow_reject=allow_reject,
        note=note or "hard contract / safety",
    )


# Seed registry — SoT for runtime policy in C3.6.
GATE_RULES: dict[str, GateRule] = {
    # --- Hard / blocking ---
    "PERSONALIZATION_PROFILE_FACT_LEAK": _h_block(
        "PERSONALIZATION_PROFILE_FACT_LEAK",
        allow_retry=False,
        allow_reject=True,
        note="safety: profile facts must not leak into public prose — reject, no quality rewrite",
    ),
    "PERSONALIZATION_EVIDENCE_ORPHAN": _h_block(
        "PERSONALIZATION_EVIDENCE_ORPHAN",
        allow_retry=True,
        allow_reject=True,
        note="broken evidence_refs / provenance — hard retry then unavailable",
    ),
    # ScreenFlow v3.1 seed-kill — hard SoT, not quality polish.
    "SEED_BANK_BINARY_SHORT_NAME": _h_block(
        "SEED_BANK_BINARY_SHORT_NAME",
        allow_retry=True,
        allow_reject=True,
        note="v3.1: invented opposing-forces bank title as Plot short_name — retry then unavailable",
    ),
    "SEED_CHORUS_PASTE": _h_block(
        "SEED_CHORUS_PASTE",
        allow_retry=True,
        allow_reject=True,
        note="v3.1: chorus pastes short_name / old bridge templates — retry then unavailable",
    ),
    # --- Quality promoted (C3.6.3 · sealed C3.6.2 pilot evidence) ---
    # Dual-agreed reject drivers on B5-template cases: clone / missing everyday /
    # abstract scene / bare astro jargon. Retry then reject_story (unavailable).
    "SCENE_ABSTRACT": _q_block(
        "SCENE_ABSTRACT",
        note="C3.6.2 sealed: abstract/advice-without-scene → retry then unavailable",
    ),
    "SCENE_CLONE": _q_block(
        "SCENE_CLONE",
        note="C3.6.2 sealed: B5 scene clones → retry then unavailable",
    ),
    "SCENE_MISSING_EVERYDAY": _q_block(
        "SCENE_MISSING_EVERYDAY",
        note="C3.6.2 sealed: missing everyday moment → retry then unavailable",
    ),
    "ASTRO_JARGON_BARE": _q_block(
        "ASTRO_JARGON_BARE",
        note="C3.6.2 sealed: bare astro jargon without translation → retry then unavailable",
    ),
    # Present on reject + acceptable_with_issues (minor) — observe at candidate first.
    "SCENE_UNIVERSAL_ADVICE": _q_cand(
        "SCENE_UNIVERSAL_ADVICE",
        note="C3.6.2: reject co-driver but also minor on acceptable — candidate_blocking",
    ),
    # --- Quality / experimental|advisory (editorial C3.1–C3.2, not yet promoted) ---
    "SCENE_MISSING_CHOICE": _q_adv("SCENE_MISSING_CHOICE"),
    "THESIS_ECHO": _q_exp("THESIS_ECHO"),
    "PSEUDO_DIAGNOSIS": _q_exp("PSEUDO_DIAGNOSIS"),
    "CATEGORICAL_PROMISE": _q_exp("CATEGORICAL_PROMISE"),
    "CHORUS_PARALLEL_ECHO": _q_adv("CHORUS_PARALLEL_ECHO"),
    "AFFIRMATION_UNNATURAL": _q_exp("AFFIRMATION_UNNATURAL"),
    "BUREAUCRATIC": _q_adv("BUREAUCRATIC"),
    "NATAL_WITHOUT_EVIDENCE": _q_exp("NATAL_WITHOUT_EVIDENCE"),
    "CHORUS_PARALLEL_FORECAST": _q_exp("CHORUS_PARALLEL_FORECAST"),
    "CHORUS_SEMANTIC_DUPLICATION": _q_cand(
        "CHORUS_SEMANTIC_DUPLICATION",
        note="C3.6.2 human calib: P=R=1.0 on sealed set → candidate_blocking (observe)",
    ),
    "CHORUS_ROLE_DRIFT": _q_exp("CHORUS_ROLE_DRIFT"),
    "CHORUS_UNTRANSLATED_JARGON": _q_exp("CHORUS_UNTRANSLATED_JARGON"),
    "CHORUS_NATAL_WITHOUT_EVIDENCE": _q_exp("CHORUS_NATAL_WITHOUT_EVIDENCE"),
    # --- Quality / advisory (personalization depth & sphere heuristics) ---
    "PERSONALIZATION_CLAIM_WITHOUT_EVIDENCE": _q_adv("PERSONALIZATION_CLAIM_WITHOUT_EVIDENCE"),
    "PERSONALIZATION_DEPTH_OVERREACH": _q_adv("PERSONALIZATION_DEPTH_OVERREACH"),
    "PERSONALIZATION_DECORATIVE_ONLY": _q_adv("PERSONALIZATION_DECORATIVE_ONLY"),
    "PERSONALIZATION_SCENES_UNCHANGED": _q_adv("PERSONALIZATION_SCENES_UNCHANGED"),
    "PERSONALIZATION_GENERIC_ACTION": _q_adv("PERSONALIZATION_GENERIC_ACTION"),
    "PERSONALIZATION_SPHERE_UNJUSTIFIED": _q_adv("PERSONALIZATION_SPHERE_UNJUSTIFIED"),
    "PERSONALIZATION_CONFLICT_UNCHANGED": _q_adv("PERSONALIZATION_CONFLICT_UNCHANGED"),
    "PERSONALIZATION_NATAL_OVERCLAIM": _q_adv("PERSONALIZATION_NATAL_OVERCLAIM"),
    "PERSONALIZATION_SPHERE_OUTSIDE_PACK": _q_adv("PERSONALIZATION_SPHERE_OUTSIDE_PACK"),
    "PERSONALIZATION_SPHERE_SELECTION_EMPTY": _q_adv("PERSONALIZATION_SPHERE_SELECTION_EMPTY"),
    "PERSONALIZATION_SPHERE_CROSS_PROFILE": _q_exp("PERSONALIZATION_SPHERE_CROSS_PROFILE"),
    # --- Eval-only provenance/closure (never runtime-blocking in C3.6) ---
    "PROVENANCE_REF_MISSING": _q_exp("PROVENANCE_REF_MISSING"),
    "PROVENANCE_ACTION_NOT_DERIVED": _q_exp("PROVENANCE_ACTION_NOT_DERIVED"),
    "PROVENANCE_REF_ORPHAN": _q_exp("PROVENANCE_REF_ORPHAN"),
    "PROVENANCE_WRONG_PROFILE": _q_exp("PROVENANCE_WRONG_PROFILE"),
    "PROVENANCE_PROP_NOT_DERIVED": _q_exp("PROVENANCE_PROP_NOT_DERIVED"),
    "CLOSURE_MISSING": _q_exp("CLOSURE_MISSING"),
    "CLOSURE_NO_CONFLICT_CALLBACK": _q_exp("CLOSURE_NO_CONFLICT_CALLBACK"),
    "CLOSURE_WELLNESS_MUSH": _q_exp("CLOSURE_WELLNESS_MUSH"),
    "CLOSURE_NEW_FORECAST": _q_exp("CLOSURE_NEW_FORECAST"),
    "CLOSURE_AFFIRMATION_ECHO": _q_exp("CLOSURE_AFFIRMATION_ECHO"),
    "LOCALE_LANGUAGE_MISMATCH": _q_exp("LOCALE_LANGUAGE_MISMATCH"),
}

# Structural scenario validate errors treated as hard (contract / SoT assemble).
# Soft-healable one-field issues live in apply_soft_scenario_heals (not here).
HARD_SCENARIO_VALIDATE_ERRORS = frozenset(
    {
        "scenario_not_dict",
        "bad_contract_version",
        "scenes_empty",
        "conflict_missing_short_name",
        "conflict_short_name_is_sky_fact",
        # v3.1 seed-kill codes from find_verbatim_seed_leaks_v1
        "conflict.short_name:invented_bank_binary",
        "chorus:seed_paste_bridge",
        # Malformed opposing_forces type (not incomplete pair — that is healable).
        "conflict_opposing_forces_not_dict",
    }
)

# Prefixes from find_verbatim_seed_leaks_v1 (ngram spans are dynamic).
HARD_SCENARIO_VALIDATE_PREFIXES = (
    "verbatim_seed_leak:",
    "scene_serves_conflict_not_opaque:",
)

# Native schema error prefixes / tokens that stay hard-blocking (retry).
# Intentionally excludes subjective checks (e.g. parallel_forecast regex) —
# those live in editorial analyzers under quality maturity.
# Soft-healable one-field issues: day_*_missing_conflict_link, scene_missing_conflict_link,
# scenes_too_many, conflict_forces_incomplete — see apply_soft_native_heals.
HARD_NATIVE_VALIDATE_MARKERS = (
    "payload_not_dict",
    "bad_schema_version",
    "legacy_keys:",
    "conflict_missing_",
    "scenes_too_few",  # content fullness — keep hard; scenes_too_many is heal-trim
    "scene_not_dict",
    "scene_bad_sphere:",
    "scene_missing_id",
    "scene_duplicate_id:",
    "scene_missing_setup:",
    "unknown_evidence:",
    "orphan_prop_",
)

# Max scenes kept when soft-healing scenes_too_many (matches validate ceiling).
SOFT_HEAL_MAX_SCENES = 4


def healed_failure_class(healed_rules: list[str] | None) -> str | None:
    """``healed:<primary_rule>`` so soft-heal is never silent success."""
    rules = [str(r).strip() for r in (healed_rules or []) if str(r).strip()]
    if not rules:
        return None
    primary = rules[0]
    if len(primary) > 96:
        primary = primary[:96]
    return f"healed:{primary}"


def apply_soft_native_heals(payload: dict[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    """Auto-fix cheap one-field native misses before hard reject.

    Does **not** invent meaning: only opaque «тон дня» anchors, trim extras,
    or clear incomplete force pairs.
    """
    from todayflow_backend.services.day_scenario_v1 import _day_tone_anchor

    if not isinstance(payload, dict):
        return {}, []
    out = dict(payload)
    heals: list[str] = []

    conflict = dict(out.get("conflict") or {}) if isinstance(out.get("conflict"), dict) else {}
    force_a = str(conflict.get("force_a") or "").strip()
    force_b = str(conflict.get("force_b") or "").strip()
    if (force_a and not force_b) or (force_b and not force_a):
        conflict["force_a"] = ""
        conflict["force_b"] = ""
        out["conflict"] = conflict
        heals.append("conflict_forces_incomplete")

    scenes_in = out.get("scenes")
    if isinstance(scenes_in, list) and len(scenes_in) > SOFT_HEAL_MAX_SCENES:
        out["scenes"] = list(scenes_in[:SOFT_HEAL_MAX_SCENES])
        heals.append("scenes_too_many")

    chorus = dict(out.get("interpretive_chorus") or {}) if isinstance(out.get("interpretive_chorus"), dict) else {}
    chorus_changed = False
    for label in ("day_card", "day_number"):
        voice_raw = chorus.get(label)
        if not isinstance(voice_raw, dict) or not voice_raw:
            continue
        voice = dict(voice_raw)
        if str(voice.get("link_to_conflict") or "").strip():
            continue
        has_voice = bool(str(voice.get("human_meaning") or "").strip()) or bool(
            str(voice.get("archetype_role") or "").strip()
        )
        if not has_voice:
            continue
        voice["link_to_conflict"] = _day_tone_anchor(str(conflict.get("title") or ""))
        chorus[label] = voice
        chorus_changed = True
        heals.append(f"{label}_missing_conflict_link")
    if chorus_changed:
        out["interpretive_chorus"] = chorus

    scenes = out.get("scenes")
    if isinstance(scenes, list):
        title = str((out.get("conflict") or {}).get("title") or "") if isinstance(out.get("conflict"), dict) else ""
        new_scenes: list[Any] = []
        scenes_changed = False
        for sc in scenes:
            if not isinstance(sc, dict):
                new_scenes.append(sc)
                continue
            row = dict(sc)
            sid = str(row.get("scene_id") or "")
            sphere = str(row.get("sphere") or "")
            setup = str(row.get("setup") or "")
            linked = False
            if title and title[:12].lower() in (
                setup + str(row.get("opportunity") or "") + str(row.get("trap") or "")
            ).lower():
                linked = True
            refs = row.get("chorus_refs") if isinstance(row.get("chorus_refs"), list) else []
            if "conflict" in [str(x).lower() for x in refs]:
                linked = True
            if str(row.get("serves_conflict") or "").strip():
                linked = True
            if not linked and title:
                row["serves_conflict"] = _day_tone_anchor(title)
                scenes_changed = True
                heals.append(f"scene_missing_conflict_link:{sid or sphere}")
            new_scenes.append(row)
        if scenes_changed:
            out["scenes"] = new_scenes

    return out, heals


def apply_soft_scenario_heals(scenario: dict[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    """Auto-fix cheap scenario validate misses (props / incomplete forces)."""
    if not isinstance(scenario, dict):
        return {}, []
    out = dict(scenario)
    heals: list[str] = []

    conflict = dict(out.get("conflict") or {}) if isinstance(out.get("conflict"), dict) else {}
    forces = conflict.get("opposing_forces")
    if isinstance(forces, dict):
        a = str(forces.get("a") or "").strip()
        b = str(forces.get("b") or "").strip()
        if (a and not b) or (b and not a):
            conflict["opposing_forces"] = {"a": "", "b": ""}
            out["conflict"] = conflict
            heals.append("conflict_opposing_forces_incomplete")

    props = dict(out.get("props") or {}) if isinstance(out.get("props"), dict) else {}
    if props.get("status") != "ok":
        return out, heals

    scenes = out.get("scenes") if isinstance(out.get("scenes"), list) else []
    scene_ids = {
        str(sc.get("scene_id"))
        for sc in scenes
        if isinstance(sc, dict) and sc.get("scene_id")
    }
    props_changed = False

    color = props.get("color") if isinstance(props.get("color"), dict) else None
    if color:
        oid = str(color.get("origin_scene_id") or "").strip()
        if not oid:
            props.pop("color", None)
            props_changed = True
            heals.append("prop_color_without_origin_scene")
        elif oid not in scene_ids:
            props.pop("color", None)
            props_changed = True
            heals.append("prop_color_origin_not_in_scenes")

    avoid = props.get("avoid_color") if isinstance(props.get("avoid_color"), dict) else None
    if avoid and not str(avoid.get("origin_scene_id") or "").strip():
        props.pop("avoid_color", None)
        props_changed = True
        heals.append("prop_avoid_without_origin_scene")

    goals = props.get("goals") if isinstance(props.get("goals"), list) else None
    if goals is not None:
        kept = [
            g
            for g in goals
            if not isinstance(g, dict) or str(g.get("origin_scene_id") or "").strip()
        ]
        dropped = len(goals) - len(kept)
        if dropped:
            props["goals"] = kept
            props_changed = True
            for _ in range(dropped):
                heals.append("prop_goal_without_origin_scene")

    affirms = props.get("affirmations") if isinstance(props.get("affirmations"), list) else None
    if affirms is not None:
        kept_a = [
            a
            for a in affirms
            if not isinstance(a, dict) or str(a.get("origin_scene_id") or "").strip()
        ]
        dropped_a = len(affirms) - len(kept_a)
        if dropped_a:
            props["affirmations"] = kept_a
            props_changed = True
            for _ in range(dropped_a):
                heals.append("prop_affirmation_without_origin_scene")

    humor = props.get("humor")
    if isinstance(humor, dict) and humor and not str(humor.get("origin_scene_id") or "").strip():
        props.pop("humor", None)
        props_changed = True
        heals.append("prop_humor_without_origin_scene")

    if props_changed:
        out["props"] = props

    return out, heals


def get_rule(code: str | None) -> GateRule:
    key = str(code or "").strip()
    if key in GATE_RULES:
        return GATE_RULES[key]
    # Unknown codes default to experimental quality (observe, never block).
    return GateRule(
        code=key or "UNKNOWN",
        family=FAMILY_QUALITY,
        maturity=MATURITY_EXPERIMENTAL,
        note="unregistered code — experimental observe-only",
    )


def runtime_action_for_rule(rule: GateRule) -> RuntimeAction:
    if rule.maturity not in RUNTIME_BLOCKING_MATURITIES:
        return "score_only"
    # Prefer retry while attempts remain; caller rejects on final failed attempt.
    if rule.allow_retry:
        return "retry"
    if rule.allow_reject:
        return "reject_story"
    if rule.allow_downgrade:
        return "downgrade_general"
    return "score_only"


def annotate_defects_with_maturity(defects: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Attach family/maturity/runtime_action without dropping analyzer fields."""
    out: list[dict[str, Any]] = []
    for raw in defects or []:
        if not isinstance(raw, dict):
            continue
        d = dict(raw)
        rule = get_rule(str(d.get("code") or ""))
        d["gate_family"] = rule.family
        d["gate_maturity"] = rule.maturity
        d["runtime_action"] = runtime_action_for_rule(rule)
        d["gate_note"] = rule.note
        out.append(d)
    return out


def partition_defects(defects: list[dict[str, Any]] | None) -> dict[str, list[dict[str, Any]]]:
    annotated = annotate_defects_with_maturity(defects)
    buckets: dict[str, list[dict[str, Any]]] = {
        "score_only": [],
        "retry": [],
        "downgrade_general": [],
        "reject_story": [],
    }
    for d in annotated:
        action = str(d.get("runtime_action") or "score_only")
        buckets.setdefault(action, []).append(d)
    return buckets


def should_retry_defects(defects: list[dict[str, Any]] | None) -> bool:
    """True only when a blocking rule explicitly allows retry (not reject-only)."""
    return bool(partition_defects(defects)["retry"])


def should_reject_story(defects: list[dict[str, Any]] | None) -> bool:
    return bool(partition_defects(defects)["reject_story"])


def should_downgrade_general(defects: list[dict[str, Any]] | None) -> bool:
    parts = partition_defects(defects)
    # Downgrade only when explicitly allowed by blocking hard rules — not for quality.
    return bool(parts["downgrade_general"]) and not parts["reject_story"]


def is_hard_scenario_validate_error(error: str) -> bool:
    e = str(error or "")
    if e in HARD_SCENARIO_VALIDATE_ERRORS:
        return True
    return any(e.startswith(p) for p in HARD_SCENARIO_VALIDATE_PREFIXES)


def is_hard_native_validate_error(error: str) -> bool:
    e = str(error or "")
    return any(e == m or e.startswith(m) for m in HARD_NATIVE_VALIDATE_MARKERS)


def maturity_summary(defects: list[dict[str, Any]] | None) -> dict[str, Any]:
    annotated = annotate_defects_with_maturity(defects)
    by_maturity: dict[str, int] = {}
    by_family: dict[str, int] = {}
    by_action: dict[str, int] = {}
    for d in annotated:
        by_maturity[str(d.get("gate_maturity"))] = by_maturity.get(str(d.get("gate_maturity")), 0) + 1
        by_family[str(d.get("gate_family"))] = by_family.get(str(d.get("gate_family")), 0) + 1
        by_action[str(d.get("runtime_action"))] = by_action.get(str(d.get("runtime_action")), 0) + 1
    return {
        "contract_version": "day_scenario_gate_maturity_c36",
        "defect_count": len(annotated),
        "by_maturity": by_maturity,
        "by_family": by_family,
        "by_action": by_action,
        "blocking_enabled_for": sorted(RUNTIME_BLOCKING_MATURITIES),
    }


_INTERNAL_DEFECT_KEYS = frozenset(
    {"gate_family", "gate_maturity", "runtime_action", "gate_note", "capture_class"}
)


def public_defect_view(defects: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Analyzer fields only — strip maturity/policy annotations from any persisted nest.

    C3.6: maturity + runtime_action live in capture/eval metadata, not as new public
    contract fields. Pre-existing editorial_meta scores/defects keep analyzer shape.
    """
    out: list[dict[str, Any]] = []
    for raw in defects or []:
        if not isinstance(raw, dict):
            continue
        out.append({k: v for k, v in raw.items() if k not in _INTERNAL_DEFECT_KEYS})
    return out


def non_blocking_maturities() -> frozenset[str]:
    """experimental / advisory / candidate_blocking — observe only until promotion."""
    return frozenset(
        {MATURITY_EXPERIMENTAL, MATURITY_ADVISORY, MATURITY_CANDIDATE_BLOCKING}
    )
