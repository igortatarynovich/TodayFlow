"""P0.1 — assemble legacy Today inputs into today_contract_v1 (Model B).

Pure function: no DB, API, or LLM. See docs/TODAY_CONTRACT_ASSEMBLER_MAPPING.md.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from todayflow_backend.services.ritual_cue_sanitize import (
    is_garbage_ritual_action_cue,
    replace_quoted_en_slugs_for_ru_display,
    strip_llm_meta_commentary,
)
from todayflow_backend.services.today_contract_fallbacks_v1 import (
    DEVELOPMENT_POINT_FALLBACK,
    DOMAIN_FALLBACKS_V1,
    FAMILY_ACTION_FALLBACK,
    FAMILY_OPPORTUNITY_FALLBACK,
    FAMILY_RISK_FALLBACK,
    FAMILY_STATUS_FALLBACK,
    MONEY_WORK_ACTION_FALLBACK,
    MONEY_WORK_OPPORTUNITY_FALLBACK,
    MONEY_WORK_RISK_FALLBACK,
    MONEY_WORK_STATUS_FALLBACK,
    PERIOD_FALLBACK,
    PRIMARY_ACTION_FALLBACK,
    RELATIONSHIPS_ACTION_FALLBACK,
    RELATIONSHIPS_OPPORTUNITY_FALLBACK,
    RELATIONSHIPS_RISK_FALLBACK,
    RELATIONSHIPS_STATUS_FALLBACK,
)
from todayflow_backend.services.today_contract_growth_v1 import (
    accept_growth_source,
    resolve_development_point,
)
from todayflow_backend.services.today_contract_text_quality_v1 import (
    accept_narrative_source,
    accept_status_source,
    apply_text_quality_gate_to_contract,
    is_headline_label,
    is_profile_trait_text,
    is_valid_action_text,
    validate_today_contract_text_quality_v1,
)

TODAY_CONTRACT_V1_CONTRACT = "today_contract_v1"
TODAY_CONTRACT_V1_VERSION = "1.0.0"

DOMAIN_LENS_SLOTS = frozenset({"status", "opportunity", "risk", "action"})
DOMAIN_IDS = frozenset({"relationships", "money_work", "family"})

# Legacy keys that must not appear anywhere in contract output.
_FORBIDDEN_OUTPUT_KEYS = frozenset(
    {
        "insight",
        "watch",
        "reason",
        "energy",
        "theme",
        "spheres",
        "love",
        "work",
        "money",
        "todayHeadline",
        "todayDetail",
        "today_headline",
        "today_detail",
        "hasDayScenario",
        "rhythmTier",
        "rhythm_tier",
        "score",
    }
)

_DOMAIN_ACTION_PRIORITY = ("relationships", "money_work", "family")


def _clean_text(raw: str | None) -> str:
    if not raw:
        return ""
    t = strip_llm_meta_commentary(str(raw).strip())
    return replace_quoted_en_slugs_for_ru_display(t).strip()


def _field(obj: dict[str, Any] | None, *keys: str) -> str:
    if not obj:
        return ""
    for key in keys:
        v = obj.get(key)
        if isinstance(v, str):
            t = _clean_text(v)
            if t:
                return t
    return ""


def _pick_payload(narrative: dict[str, Any] | None, surface: str) -> dict[str, Any]:
    if not narrative:
        return {}
    surf = narrative.get(surface)
    if isinstance(surf, dict):
        payload = surf.get("payload")
        if isinstance(payload, dict):
            return payload
    return {}


def _pick_narrative_text(narrative: dict[str, Any] | None, surface: str, keys: tuple[str, ...]) -> str:
    payload = _pick_payload(narrative, surface)
    for key in keys:
        t = _field(payload, key)
        if t:
            return t
    return ""


def _pick_scenario(scenarios: list[Any] | None, slugs: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(scenarios, list):
        return {}
    for slug in slugs:
        for item in scenarios:
            if not isinstance(item, dict):
                continue
            if str(item.get("slug") or "").strip().lower() == slug:
                return item
    return {}


def _scenario_parts(scenario: dict[str, Any]) -> tuple[str, str]:
    if not scenario:
        return "", ""
    focus = _field(scenario, "focus")
    summary = _field(scenario, "summary")
    title = _field(scenario, "title")
    headline = focus or title
    detail = summary if summary and summary != focus else ""
    return headline, detail


def _merge_status(headline: str, detail: str, fallback: str) -> str:
    parts: list[str] = []
    for chunk in (headline, detail):
        c = _clean_text(chunk)
        if c and c not in parts:
            parts.append(c)
    if parts:
        return " — ".join(parts) if len(parts) == 2 else parts[0]
    return fallback


def _dedupe_join(parts: list[str]) -> str:
    out: list[str] = []
    for p in parts:
        t = _clean_text(p)
        if not t:
            continue
        if any(t in existing or existing in t for existing in out):
            continue
        out.append(t)
    return " ".join(out)


def _sphere_score(sphere: dict[str, Any] | None, default: int = 0) -> int:
    if not sphere:
        return default
    raw = sphere.get("score")
    if isinstance(raw, (int, float)) and raw > 0:
        return int(raw)
    return default


def _synthesize_action(
    *,
    reason: str = "",
    insight: str = "",
    scenario_focus: str = "",
    spine_first_move: str = "",
    fallback: str,
) -> str:
    for candidate in (reason, spine_first_move, insight, scenario_focus):
        t = _clean_text(candidate)
        if not t or is_garbage_ritual_action_cue(t) or is_headline_label(t):
            continue
        sentences = re.split(r"(?<=[.!?])\s+", t)
        for sentence in sentences:
            s = sentence.strip()
            if is_valid_action_text(s):
                return s[:240].rstrip(".,; ")
    return fallback


def _status_from_scenario(
    domain_id: str,
    scenario: dict[str, Any],
    sphere_headline: str,
    sphere_detail: str,
    fallback: str,
) -> str:
    headline, detail = _scenario_parts(scenario)
    if not headline:
        headline = accept_status_source(sphere_headline) or ""
        detail = accept_status_source(sphere_detail) or ""
    else:
        headline = accept_status_source(headline) or ""
        detail = accept_status_source(detail) or ""
    merged = _merge_status(headline, detail, "")
    if domain_id == "family" and (is_profile_trait_text(merged) or not merged):
        return fallback
    return merged or fallback


def _build_domain_lens(
    *,
    status: str,
    opportunity: str,
    risk: str,
    action: str,
) -> dict[str, str]:
    return {
        "status": status,
        "opportunity": opportunity,
        "risk": risk,
        "action": action,
    }


def _extract_guide_theme(guide_payload: dict[str, Any]) -> str:
    cm = guide_payload.get("core_message")
    if isinstance(cm, str):
        return _clean_text(cm)
    if isinstance(cm, dict):
        return _field(cm, "headline", "body", "message", "main_text")
    return ""


def _horoscope(morning: dict[str, Any] | None) -> dict[str, Any]:
    if not morning:
        return {}
    dh = morning.get("daily_horoscope")
    return dh if isinstance(dh, dict) else {}


def _spine(morning: dict[str, Any] | None) -> dict[str, Any]:
    spine = _horoscope(morning).get("spine")
    return spine if isinstance(spine, dict) else {}


def _scenarios(morning: dict[str, Any] | None) -> list[Any]:
    scenarios = _horoscope(morning).get("scenarios")
    return scenarios if isinstance(scenarios, list) else []


def _recommendations(morning: dict[str, Any] | None) -> dict[str, Any]:
    if not morning:
        return {}
    rec = morning.get("daily_recommendations")
    return rec if isinstance(rec, dict) else {}


def _decision_engine(morning: dict[str, Any] | None) -> dict[str, Any]:
    if not morning:
        return {}
    de = morning.get("decision_engine")
    return de if isinstance(de, dict) else {}


def _pick_safe_growth_narrative(
    narrative: dict[str, Any] | None,
    surface: str,
    keys: tuple[str, ...],
) -> str:
    payload = _pick_payload(narrative, surface)
    for key in keys:
        t = _field(payload, key)
        if t:
            safe = accept_growth_source(t)
            if safe:
                return safe
    return ""


def _pick_safe_narrative(
    narrative: dict[str, Any] | None,
    surface: str,
    keys: tuple[str, ...],
) -> str:
    payload = _pick_payload(narrative, surface)
    for key in keys:
        t = _field(payload, key)
        if t:
            safe = accept_narrative_source(t)
            if safe:
                return safe
    return ""


def _sphere(spheres: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not spheres:
        return {}
    raw = spheres.get(key)
    return raw if isinstance(raw, dict) else {}


def assemble_today_contract_v1(
    *,
    spheres: dict[str, Any] | None = None,
    narrative: dict[str, Any] | None = None,
    morning_ritual: dict[str, Any] | None = None,
    fusion: dict[str, Any] | None = None,
    fallback_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map legacy Today inputs to today_contract_v1 (Model B)."""
    ctx = fallback_context or {}
    love = _sphere(spheres, "love")
    work = _sphere(spheres, "work")
    money = _sphere(spheres, "money")
    energy = _sphere(spheres, "energy")

    spine = _spine(morning_ritual)
    scenarios = _scenarios(morning_ritual)
    rec = _recommendations(morning_ritual)
    decision = _decision_engine(morning_ritual)

    love_scenario = _pick_scenario(scenarios, ("love",))
    work_scenario = _pick_scenario(scenarios, ("career", "work"))
    money_scenario = _pick_scenario(scenarios, ("money",))
    family_scenario = _pick_scenario(scenarios, ("family",))

    best_mode = _field(spine, "best_mode")
    first_move = _field(spine, "first_move")
    main_risk = _field(spine, "main_risk")

    guide_payload = _pick_payload(narrative, "guide")

    encouragement = _field(fusion, "encouragement")

    de_actions = decision.get("actions")
    de_action0 = ""
    if isinstance(de_actions, list) and de_actions:
        de_action0 = _clean_text(str(de_actions[0]))

    hero = decision.get("hero")
    hero_label = ""
    hero_focus = ""
    if isinstance(hero, dict):
        hero_label = _field(hero, "energy_label")
        focus = hero.get("focus")
        if isinstance(focus, list) and focus:
            hero_focus = _clean_text(str(focus[0]))

    what_to_do = _field(rec, "what_to_do")
    what_to_avoid = _field(rec, "what_to_avoid")

    # --- global_context.period ---
    period = (
        _field(guide_payload, "headline", "subline")
        or _extract_guide_theme(guide_payload)
        or best_mode
        or _merge_status(*_scenario_parts(_pick_scenario(scenarios, ("love", "career", "money", "family"))), "")
        or _dedupe_join([hero_label, hero_focus])
        or encouragement
        or PERIOD_FALLBACK
    )

    # --- personal_growth.development_point (skill/quality today — not energy observation) ---
    growth_candidates = [
        _pick_safe_growth_narrative(narrative, "spheres", ("growth_insight", "development_point")),
        _pick_safe_growth_narrative(narrative, "day_layer", ("nudge_message", "personal_insight_body")),
        accept_growth_source(_field(spine, "growth_hint", "development_hint")),
    ]
    development_point_raw = next((c for c in growth_candidates if c), "")
    development_point = resolve_development_point(period, development_point_raw)

    # --- domains.relationships ---
    relationships_status = _status_from_scenario(
        "relationships",
        love_scenario,
        _field(love, "todayHeadline", "today_headline"),
        _field(love, "todayDetail", "today_detail"),
        RELATIONSHIPS_STATUS_FALLBACK,
    )
    relationships_opportunity = (
        _pick_safe_narrative(narrative, "spheres", ("love_insight", "relationships_insight"))
        or accept_narrative_source(_field(love, "insight"))
        or RELATIONSHIPS_OPPORTUNITY_FALLBACK
    )
    relationships_risk = (
        accept_narrative_source(_field(love, "watch"))
        or _pick_safe_narrative(narrative, "spheres", ("love_watch", "relationships_watch"))
        or RELATIONSHIPS_RISK_FALLBACK
    )
    relationships_action = _synthesize_action(
        reason=_field(love, "reason")
        or _pick_narrative_text(narrative, "spheres", ("love_reason", "relationships_reason")),
        insight=relationships_opportunity,
        scenario_focus=_field(love_scenario, "focus"),
        spine_first_move=first_move,
        fallback=RELATIONSHIPS_ACTION_FALLBACK,
    )

    # --- domains.money_work ---
    work_score = _sphere_score(work)
    money_score = _sphere_score(money)
    work_h, work_d = _scenario_parts(work_scenario)
    money_h, money_d = _scenario_parts(money_scenario)
    if not work_h:
        work_h = accept_status_source(_field(work, "todayHeadline", "today_headline"))
        work_d = accept_status_source(_field(work, "todayDetail", "today_detail"))
    if not money_h:
        money_h = accept_status_source(_field(money, "todayHeadline", "today_headline"))
        money_d = accept_status_source(_field(money, "todayDetail", "today_detail"))
    money_work_status = _merge_status(
        _dedupe_join([work_h, money_h]),
        _dedupe_join([work_d, money_d]),
        MONEY_WORK_STATUS_FALLBACK,
    )

    work_insight = accept_narrative_source(_field(work, "insight")) or _pick_safe_narrative(
        narrative, "spheres", ("work_insight", "career_insight", "purpose_insight")
    )
    money_insight = accept_narrative_source(_field(money, "insight")) or _pick_safe_narrative(
        narrative, "spheres", ("money_insight", "wealth_insight", "resource_insight")
    )
    if work_insight and money_insight and work_insight != money_insight:
        money_work_opportunity = _dedupe_join(
            [money_insight if money_score >= work_score else work_insight, work_insight, money_insight]
        )
    else:
        money_work_opportunity = money_insight or work_insight or MONEY_WORK_OPPORTUNITY_FALLBACK

    money_work_risk = (
        accept_narrative_source(_field(money, "watch"))
        or accept_narrative_source(_field(work, "watch"))
        or accept_narrative_source(what_to_avoid)
        or MONEY_WORK_RISK_FALLBACK
    )

    money_work_action = _synthesize_action(
        reason=_field(money, "reason", "wealth_reason")
        or _field(work, "reason")
        or _pick_narrative_text(narrative, "spheres", ("money_reason", "work_reason")),
        insight=money_work_opportunity,
        scenario_focus=_field(money_scenario, "focus") if money_score >= work_score else _field(work_scenario, "focus"),
        spine_first_move=first_move,
        fallback=MONEY_WORK_ACTION_FALLBACK,
    )

    # --- domains.family (independent — never alias love scenario alone) ---
    family_status = _status_from_scenario("family", family_scenario, "", "", FAMILY_STATUS_FALLBACK)

    family_opportunity = (
        _pick_safe_narrative(narrative, "spheres", ("family_support", "family_insight"))
        or accept_narrative_source(_field(family_scenario, "focus"))
        or FAMILY_OPPORTUNITY_FALLBACK
    )
    family_risk = (
        _pick_safe_narrative(narrative, "spheres", ("family_risk", "family_tension"))
        or accept_narrative_source(main_risk)
        or FAMILY_RISK_FALLBACK
    )
    family_action = _synthesize_action(
        reason=_pick_safe_narrative(narrative, "spheres", ("family_reason")),
        scenario_focus=accept_narrative_source(_field(family_scenario, "focus")),
        insight=family_opportunity,
        spine_first_move=first_move,
        fallback=FAMILY_ACTION_FALLBACK,
    )

    domains = {
        "relationships": _build_domain_lens(
            status=relationships_status,
            opportunity=relationships_opportunity,
            risk=relationships_risk,
            action=relationships_action,
        ),
        "money_work": _build_domain_lens(
            status=money_work_status,
            opportunity=money_work_opportunity,
            risk=money_work_risk,
            action=money_work_action,
        ),
        "family": _build_domain_lens(
            status=family_status,
            opportunity=family_opportunity,
            risk=family_risk,
            action=family_action,
        ),
    }

    domain_scores = {
        "relationships": _sphere_score(love, 72),
        "money_work": max(work_score, money_score, 64),
        "family": 58 if family_scenario else 50,
    }

    best_score = max(domain_scores.values())
    primary_action = PRIMARY_ACTION_FALLBACK
    for domain_id in _DOMAIN_ACTION_PRIORITY:
        if domain_scores[domain_id] >= best_score:
            primary_action = domains[domain_id]["action"]
            break

    if primary_action == PRIMARY_ACTION_FALLBACK:
        primary_action = _synthesize_action(
            spine_first_move=first_move,
            reason=what_to_do,
            insight=de_action0,
            fallback=PRIMARY_ACTION_FALLBACK,
        )

    progress = ctx.get("progress")
    if not isinstance(progress, dict):
        progress = {}

    generation_id = _field(ctx, "generation_id")
    guide_surf = narrative.get("guide") if narrative else None
    if not generation_id and isinstance(guide_surf, dict):
        generation_id = _clean_text(str(guide_surf.get("generation_id") or ""))
    if not generation_id:
        generation_id = str(uuid4())

    contract = {
        "contract_version": TODAY_CONTRACT_V1_CONTRACT,
        "global_context": {"period": period},
        "personal_growth": {"development_point": development_point},
        "domains": domains,
        "primary_action": primary_action,
        "progress": progress,
        "generation_id": generation_id,
    }
    return apply_text_quality_gate_to_contract(contract, DOMAIN_FALLBACKS_V1)


def _collect_forbidden_keys(obj: Any, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_s = str(key)
            child_path = f"{path}.{key_s}" if path else key_s
            if key_s == "day_story":
                continue
            if key_s in _FORBIDDEN_OUTPUT_KEYS:
                hits.append(child_path)
            hits.extend(_collect_forbidden_keys(value, child_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            hits.extend(_collect_forbidden_keys(item, f"{path}[{i}]"))
    return hits


def validate_today_contract_v1(contract: dict[str, Any]) -> list[str]:
    """Return validation errors; empty list means contract is acceptable for P0.1 wire."""
    errors: list[str] = []

    if contract.get("contract_version") != TODAY_CONTRACT_V1_CONTRACT:
        errors.append("contract_version must be today_contract_v1")

    if not isinstance(contract.get("global_context"), dict):
        errors.append("global_context missing")
    elif not _clean_text(contract["global_context"].get("period")):
        errors.append("global_context.period empty")

    if not isinstance(contract.get("personal_growth"), dict):
        errors.append("personal_growth missing")
    elif not _clean_text(contract["personal_growth"].get("development_point")):
        errors.append("personal_growth.development_point empty")

    domains = contract.get("domains")
    if not isinstance(domains, dict):
        errors.append("domains missing")
        return errors

    for domain_id in DOMAIN_IDS:
        lens = domains.get(domain_id)
        if not isinstance(lens, dict):
            errors.append(f"domains.{domain_id} missing")
            continue
        if str(lens.get("evidence_status") or "") == "absent":
            # PR-3: absent domain is honest empty — no invented copy required.
            continue
        extra = set(lens.keys()) - DOMAIN_LENS_SLOTS - {"evidence_status"}
        if extra:
            errors.append(f"domains.{domain_id} has extra keys: {sorted(extra)}")
        for slot in DOMAIN_LENS_SLOTS:
            if not _clean_text(lens.get(slot)):
                errors.append(f"domains.{domain_id}.{slot} empty")

    if not _clean_text(contract.get("primary_action")):
        errors.append("primary_action empty")

    if not isinstance(contract.get("progress"), dict):
        errors.append("progress must be object")

    if not _clean_text(contract.get("generation_id")):
        errors.append("generation_id empty")

    forbidden = _collect_forbidden_keys(contract)
    if forbidden:
        errors.append(f"legacy keys in output: {forbidden}")

    errors.extend(validate_today_contract_text_quality_v1(contract))

    return errors
