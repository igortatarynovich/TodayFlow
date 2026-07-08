"""Interpretation Reference v0 — deterministic rules (ILR canon, no LLM).

Rules load from DATA/reference/interpretation/interpretation_rule_registry_v1.json (ILR-2).

Canon: INTERPRETATION_LAYER_AND_REFERENCE.md §3–§4
"""

from __future__ import annotations

from typing import Any, TypedDict

from todayflow_backend.data.interpretation_rule_registry_loader import (
    clear_interpretation_rule_registry_cache,
    get_interpretation_rule,
    load_interpretation_rules_v0 as _load_rule_entries,
)


class CandidateMeaning(TypedDict):
    code: str
    label: str
    prior_weight: float


class InterpretationRuleV0(TypedDict):
    interpretation_ref_id: str
    taxonomy: str
    level: str
    trigger_event_type: str
    trigger_payload_key: str | None
    trigger_payload_values: frozenset[str] | None
    trigger_payload_key_secondary: str | None
    trigger_payload_values_secondary: frozenset[str] | None
    candidate_meanings: list[CandidateMeaning]
    min_signal_count: int
    summary_dominant: str
    spawn_hypothesis_ids: tuple[str, ...]


def _values_to_frozenset(raw: list[str] | None) -> frozenset[str] | None:
    if not raw:
        return None
    return frozenset(str(v).strip().lower() for v in raw if str(v).strip())


def _entry_to_runtime_rule(entry: dict[str, Any]) -> InterpretationRuleV0:
    meanings_raw = entry.get("candidate_meanings") or []
    meanings: list[CandidateMeaning] = []
    for item in meanings_raw:
        if not isinstance(item, dict):
            continue
        meanings.append(
            {
                "code": str(item["code"]),
                "label": str(item["label"]),
                "prior_weight": float(item["prior_weight"]),
            }
        )
    return {
        "interpretation_ref_id": str(entry["interpretation_ref_id"]),
        "taxonomy": str(entry["taxonomy"]),
        "level": str(entry["level"]),
        "trigger_event_type": str(entry["trigger_event_type"]),
        "trigger_payload_key": entry.get("trigger_payload_key"),
        "trigger_payload_values": _values_to_frozenset(entry.get("trigger_payload_values")),
        "trigger_payload_key_secondary": entry.get("trigger_payload_key_secondary"),
        "trigger_payload_values_secondary": _values_to_frozenset(entry.get("trigger_payload_values_secondary")),
        "candidate_meanings": meanings,
        "min_signal_count": int(entry["min_signal_count"]),
        "summary_dominant": str(entry["summary_dominant"]),
        "spawn_hypothesis_ids": tuple(
            str(x).strip()
            for x in (entry.get("spawn_hypothesis_ids") or [])
            if str(x).strip()
        ),
    }


def get_interpretation_rules_v0() -> tuple[InterpretationRuleV0, ...]:
    """Active interpretation rules from reference registry."""
    return tuple(_entry_to_runtime_rule(entry) for entry in _load_rule_entries())


def rule_by_ref_id(ref_id: str) -> InterpretationRuleV0 | None:
    try:
        return _entry_to_runtime_rule(get_interpretation_rule(ref_id))
    except Exception:
        return None


def payload_match_value(payload: dict[str, Any], key: str | None) -> str:
    if not key:
        return ""
    raw = payload.get(key)
    if raw is None and key == "mood_id":
        raw = payload.get("mood")
    if raw is None and key == "topic_id":
        raw = payload.get("head_topic")
    if raw is None and key == "format_id":
        raw = payload.get("scenario_id")
    return str(raw or "").strip().lower()


def _payload_value_matches(payload: dict[str, Any], key: str | None, values: frozenset[str] | None) -> bool:
    if not values:
        return True
    value = payload_match_value(payload, key)
    if not value:
        return False
    return value in values or any(v in value for v in values)


def event_matches_rule(event_type: str, payload: dict[str, Any], rule: InterpretationRuleV0) -> bool:
    if event_type != rule["trigger_event_type"]:
        return False
    if not _payload_value_matches(payload, rule.get("trigger_payload_key"), rule.get("trigger_payload_values")):
        return False
    return _payload_value_matches(
        payload,
        rule.get("trigger_payload_key_secondary"),
        rule.get("trigger_payload_values_secondary"),
    )


__all__ = [
    "CandidateMeaning",
    "InterpretationRuleV0",
    "clear_interpretation_rule_registry_cache",
    "event_matches_rule",
    "get_interpretation_rules_v0",
    "payload_match_value",
    "rule_by_ref_id",
]
