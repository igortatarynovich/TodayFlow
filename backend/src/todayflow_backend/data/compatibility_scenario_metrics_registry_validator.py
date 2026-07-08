"""Compat-ref-1 — Validate compatibility scenario metrics registry."""

from __future__ import annotations

from typing import Any

COMPATIBILITY_SCENARIO_METRICS_REGISTRY_V1_CONTRACT = "compatibility_scenario_metrics_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "review", "active"})
METRIC_SLOTS = frozenset({"attraction", "stability", "conflicts", "sexuality"})

REGISTRY_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "scenario_blends",
        "scenario_hero_weights",
        "scenario_funnel_domains",
        "default_scenario_id",
    }
)


def _validate_blend_map(
    blends: dict[str, Any],
    *,
    label: str,
    errors: list[str],
    require_all_slots: bool,
) -> None:
    if not isinstance(blends, dict) or not blends:
        errors.append(f"{label} must be a non-empty object")
        return
    for scenario_id, slots in blends.items():
        if not isinstance(slots, dict):
            errors.append(f"{label}.{scenario_id}: must be object")
            continue
        slot_keys = set(slots.keys())
        if require_all_slots and slot_keys != METRIC_SLOTS:
            errors.append(f"{label}.{scenario_id}: slots must be {sorted(METRIC_SLOTS)}")
        for slot, weights in slots.items():
            if slot not in METRIC_SLOTS:
                errors.append(f"{label}.{scenario_id}.{slot}: invalid slot")
                continue
            if not isinstance(weights, dict):
                errors.append(f"{label}.{scenario_id}.{slot}: weights must be object")
                continue
            wsum = 0.0
            for key, value in weights.items():
                if key not in METRIC_SLOTS:
                    errors.append(f"{label}.{scenario_id}.{slot}: invalid weight key {key}")
                try:
                    w = float(value)
                except (TypeError, ValueError):
                    errors.append(f"{label}.{scenario_id}.{slot}.{key}: weight must be number")
                    continue
                if w < 0:
                    errors.append(f"{label}.{scenario_id}.{slot}.{key}: weight must be >= 0")
                wsum += w
            if wsum <= 0:
                errors.append(f"{label}.{scenario_id}.{slot}: weight sum must be > 0")


def validate_compatibility_scenario_metrics_registry_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"]

    missing = REGISTRY_TOP_KEYS - set(payload.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    if payload.get("contract_version") != COMPATIBILITY_SCENARIO_METRICS_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")
    if payload.get("domain") != "compatibility":
        errors.append("domain must be compatibility")
    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid registry status")

    default_id = str(payload.get("default_scenario_id") or "")
    blends = payload.get("scenario_blends")
    if isinstance(blends, dict) and default_id and default_id not in blends:
        errors.append(f"default_scenario_id {default_id!r} missing from scenario_blends")

    _validate_blend_map(blends if isinstance(blends, dict) else {}, label="scenario_blends", errors=errors, require_all_slots=True)

    hero = payload.get("scenario_hero_weights")
    if isinstance(hero, dict):
        for scenario_id, weights in hero.items():
            if not isinstance(weights, dict):
                errors.append(f"scenario_hero_weights.{scenario_id}: must be object")
                continue
            if set(weights.keys()) != METRIC_SLOTS:
                errors.append(f"scenario_hero_weights.{scenario_id}: must have all metric slots")
            wsum = sum(float(v) for v in weights.values() if isinstance(v, (int, float)))
            if abs(wsum - 1.0) > 0.05:
                errors.append(f"scenario_hero_weights.{scenario_id}: sum must be ~1.0")

    funnel = payload.get("scenario_funnel_domains")
    if isinstance(funnel, dict):
        for scenario_id, domains in funnel.items():
            if not isinstance(domains, list) or not domains:
                errors.append(f"scenario_funnel_domains.{scenario_id}: must be non-empty list")
            elif not all(isinstance(d, str) and d.strip() for d in domains):
                errors.append(f"scenario_funnel_domains.{scenario_id}: invalid domain ids")

    return errors
