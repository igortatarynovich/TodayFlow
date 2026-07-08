"""ILR-2 — Validate Interpretation Rule registry (machine contract)."""

from __future__ import annotations

from typing import Any

INTERPRETATION_RULE_REGISTRY_V1_CONTRACT = "interpretation_rule_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "review", "active"})
ALLOWED_RULE_STATUSES = frozenset({"draft", "review", "active"})
ALLOWED_LEVELS = frozenset({"L1", "L2", "L3", "L4"})
ALLOWED_TAXONOMIES = frozenset(
    {
        "interest",
        "behavior",
        "motivation",
        "goal",
        "emotional",
        "rhythm",
        "relationship",
        "career",
        "learning",
        "transformation",
    }
)

REGISTRY_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "interpretation_rules",
    }
)

RULE_KEYS = frozenset(
    {
        "interpretation_ref_id",
        "taxonomy",
        "level",
        "trigger_event_type",
        "trigger_payload_key",
        "trigger_payload_values",
        "trigger_payload_key_secondary",
        "trigger_payload_values_secondary",
        "candidate_meanings",
        "min_signal_count",
        "summary_dominant",
        "status",
        "version",
    }
)

OPTIONAL_RULE_KEYS = frozenset({"spawn_hypothesis_ids"})
ALLOWED_RULE_KEYS = RULE_KEYS | OPTIONAL_RULE_KEYS

MEANING_KEYS = frozenset({"code", "label", "prior_weight"})


def validate_interpretation_rule_registry_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"]

    extra_top = set(payload.keys()) - REGISTRY_TOP_KEYS
    if extra_top:
        errors.append(f"unexpected top-level keys: {sorted(extra_top)}")
    missing_top = REGISTRY_TOP_KEYS - set(payload.keys())
    if missing_top:
        errors.append(f"missing top-level keys: {sorted(missing_top)}")

    if payload.get("contract_version") != INTERPRETATION_RULE_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")
    if payload.get("domain") != "interpretation":
        errors.append("domain must be interpretation")
    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid registry status")

    rules = payload.get("interpretation_rules")
    if not isinstance(rules, dict) or not rules:
        errors.append("interpretation_rules must be a non-empty object")
        return errors

    seen_ids: set[str] = set()
    for key, rule in rules.items():
        if not isinstance(rule, dict):
            errors.append(f"{key}: rule must be an object")
            continue

        ref_id = str(rule.get("interpretation_ref_id") or "")
        if not ref_id:
            errors.append(f"{key}: interpretation_ref_id required")
            continue
        if ref_id != key:
            errors.append(f"{key}: key must match interpretation_ref_id ({ref_id})")
        if ref_id in seen_ids:
            errors.append(f"duplicate interpretation_ref_id: {ref_id}")
        seen_ids.add(ref_id)

        extra = set(rule.keys()) - ALLOWED_RULE_KEYS
        if extra:
            errors.append(f"{ref_id}: unexpected keys {sorted(extra)}")
        missing = RULE_KEYS - set(rule.keys())
        if missing:
            errors.append(f"{ref_id}: missing keys {sorted(missing)}")

        if rule.get("taxonomy") not in ALLOWED_TAXONOMIES:
            errors.append(f"{ref_id}: invalid taxonomy")
        if rule.get("level") not in ALLOWED_LEVELS:
            errors.append(f"{ref_id}: invalid level")
        if rule.get("status") not in ALLOWED_RULE_STATUSES:
            errors.append(f"{ref_id}: invalid status")

        event_type = str(rule.get("trigger_event_type") or "").strip()
        if not event_type:
            errors.append(f"{ref_id}: trigger_event_type required")

        min_count = rule.get("min_signal_count")
        if not isinstance(min_count, int) or min_count < 1:
            errors.append(f"{ref_id}: min_signal_count must be int >= 1")

        summary = str(rule.get("summary_dominant") or "").strip()
        if not summary:
            errors.append(f"{ref_id}: summary_dominant required")

        meanings = rule.get("candidate_meanings")
        if not isinstance(meanings, list) or len(meanings) < 2:
            errors.append(f"{ref_id}: candidate_meanings must have >= 2 entries")
        else:
            weight_sum = 0.0
            codes: set[str] = set()
            for idx, meaning in enumerate(meanings):
                if not isinstance(meaning, dict):
                    errors.append(f"{ref_id}: meaning[{idx}] must be object")
                    continue
                if set(meaning.keys()) != MEANING_KEYS:
                    errors.append(f"{ref_id}: meaning[{idx}] invalid keys")
                code = str(meaning.get("code") or "")
                if not code:
                    errors.append(f"{ref_id}: meaning[{idx}] code required")
                elif code in codes:
                    errors.append(f"{ref_id}: duplicate meaning code {code}")
                codes.add(code)
                label = str(meaning.get("label") or "").strip()
                if not label:
                    errors.append(f"{ref_id}: meaning[{idx}] label required")
                try:
                    w = float(meaning.get("prior_weight"))
                except (TypeError, ValueError):
                    errors.append(f"{ref_id}: meaning[{idx}] prior_weight invalid")
                    continue
                if w <= 0:
                    errors.append(f"{ref_id}: meaning[{idx}] prior_weight must be > 0")
                weight_sum += w
            if meanings and abs(weight_sum - 1.0) > 0.05:
                errors.append(f"{ref_id}: prior_weight sum must be ~1.0 (got {weight_sum:.3f})")

        for field in ("trigger_payload_values", "trigger_payload_values_secondary"):
            values = rule.get(field)
            if values is None:
                continue
            if not isinstance(values, list) or not values:
                errors.append(f"{ref_id}: {field} must be non-empty list when set")
            elif not all(isinstance(v, str) and v.strip() for v in values):
                errors.append(f"{ref_id}: {field} must be list of non-empty strings")

        spawn_ids = rule.get("spawn_hypothesis_ids")
        if spawn_ids is not None:
            if not isinstance(spawn_ids, list) or not spawn_ids:
                errors.append(f"{ref_id}: spawn_hypothesis_ids must be non-empty list when set")
            elif not all(isinstance(x, str) and x.strip() for x in spawn_ids):
                errors.append(f"{ref_id}: spawn_hypothesis_ids must be list of non-empty strings")

    return errors
