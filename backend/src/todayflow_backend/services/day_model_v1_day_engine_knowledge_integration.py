"""A1.2 — Day Engine knowledge integration contract (read-only hints from context slice)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    CLAIM_PREFIX_ACTION,
    CLAIM_PREFIX_CONTENT_AFFINITY,
    CLAIM_PREFIX_RISK,
    CLAIM_PREFIX_SURFACE,
    CLAIM_PREFIX_TEMPO,
    KNOWLEDGE_TYPE_BEHAVIOR,
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
    KNOWLEDGE_TYPE_TIMING,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    CONTEXT_SLICE_STATUS_READY,
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
)

DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT = "day_engine_knowledge_input_v1"
INTEGRATION_POLICY_VERSION = "1.0.0"

INTEGRATION_STATUS_READY = "ready"

INTEGRATION_RESULT_CREATED = "created"
INTEGRATION_RESULT_REJECTED = "rejected"

CONSUMER_DAY_ENGINE = "day_engine"

HINT_CHANNEL_CONTENT_AFFINITY = "content_affinity"
HINT_CHANNEL_RESPONSE_STYLE = "response_style"
HINT_CHANNEL_ACTION_MODE = "action_mode"
HINT_CHANNEL_TEMPO_ALIGNMENT = "tempo_alignment"
HINT_CHANNEL_RISK_SENSITIVITY = "risk_sensitivity"

ALLOWED_HINT_CHANNELS = frozenset(
    {
        HINT_CHANNEL_CONTENT_AFFINITY,
        HINT_CHANNEL_RESPONSE_STYLE,
        HINT_CHANNEL_ACTION_MODE,
        HINT_CHANNEL_TEMPO_ALIGNMENT,
        HINT_CHANNEL_RISK_SENSITIVITY,
    }
)

APPLICATION_MODE_BOOST = "boost"
APPLICATION_MODE_PRIORITIZE = "prioritize"
APPLICATION_MODE_INCLUDE = "include"
APPLICATION_MODE_SUPPRESS = "suppress"

ALLOWED_APPLICATION_MODES = frozenset(
    {
        APPLICATION_MODE_BOOST,
        APPLICATION_MODE_PRIORITIZE,
        APPLICATION_MODE_INCLUDE,
        APPLICATION_MODE_SUPPRESS,
    }
)

CLAIM_PREFIX_TO_CHANNEL: dict[str, str] = {
    CLAIM_PREFIX_CONTENT_AFFINITY: HINT_CHANNEL_CONTENT_AFFINITY,
    CLAIM_PREFIX_SURFACE: HINT_CHANNEL_RESPONSE_STYLE,
    CLAIM_PREFIX_ACTION: HINT_CHANNEL_ACTION_MODE,
    CLAIM_PREFIX_TEMPO: HINT_CHANNEL_TEMPO_ALIGNMENT,
    CLAIM_PREFIX_RISK: HINT_CHANNEL_RISK_SENSITIVITY,
}

KNOWLEDGE_TYPE_TO_CHANNEL: dict[str, str] = {
    KNOWLEDGE_TYPE_CONTENT_AFFINITY: HINT_CHANNEL_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE: HINT_CHANNEL_RESPONSE_STYLE,
    KNOWLEDGE_TYPE_BEHAVIOR: HINT_CHANNEL_ACTION_MODE,
    KNOWLEDGE_TYPE_TIMING: HINT_CHANNEL_TEMPO_ALIGNMENT,
}

CHANNEL_DEFAULT_APPLICATION_MODE: dict[str, str] = {
    HINT_CHANNEL_CONTENT_AFFINITY: APPLICATION_MODE_BOOST,
    HINT_CHANNEL_RESPONSE_STYLE: APPLICATION_MODE_PRIORITIZE,
    HINT_CHANNEL_ACTION_MODE: APPLICATION_MODE_PRIORITIZE,
    HINT_CHANNEL_TEMPO_ALIGNMENT: APPLICATION_MODE_INCLUDE,
    HINT_CHANNEL_RISK_SENSITIVITY: APPLICATION_MODE_INCLUDE,
}

MAX_HINTS_PER_CHANNEL = 2
MAX_TOTAL_HINTS = 5

FORBIDDEN_INTEGRATION_OPERATIONS = frozenset(
    {
        "override_daymodel",
        "change_strategy",
        "change_risk",
        "change_tempo",
        "change_vector",
        "change_content_keys",
        "mutate_profile",
        "write_memory",
        "call_llm_directly",
        "add_raw_profile",
        "add_sensitive_data",
        "create_recommendation",
    }
)

ALLOWED_DAY_MODEL_SNAPSHOT_KEYS = frozenset(
    {
        "contract_version",
        "vector",
        "tempo",
        "risk",
        "strategy",
        "scales",
        "gate",
    }
)

DAY_ENGINE_KNOWLEDGE_INPUT_V1_KEYS = frozenset(
    {
        "contract_version",
        "integration_id",
        "context_slice_id",
        "target_surface",
        "consumer",
        "integration_policy_version",
        "knowledge_applied",
        "hint_channels",
        "hints",
        "skipped_facts",
        "influence_summary",
        "day_model_snapshot_hash",
        "traceability",
        "status",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class DayEngineKnowledgeIntegrationError(ValueError):
    """Raised when integration inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _split_claim(claim: str) -> tuple[str, str]:
    if ":" not in claim:
        return claim, ""
    prefix, value = claim.split(":", 1)
    return prefix, value


def _hash_snapshot(snapshot: dict[str, Any]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sanitize_day_model_snapshot(
    day_model_snapshot: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Keep only Day Engine core fields for trace — no profile dumps."""
    if day_model_snapshot is None:
        return None, []

    errors: list[str] = []
    unknown = set(day_model_snapshot.keys()) - ALLOWED_DAY_MODEL_SNAPSHOT_KEYS
    if unknown:
        errors.append(f"day_model_snapshot has forbidden keys: {sorted(unknown)}")

    sanitized: dict[str, Any] = {}
    for key in ALLOWED_DAY_MODEL_SNAPSHOT_KEYS:
        if key in day_model_snapshot:
            sanitized[key] = day_model_snapshot[key]

    return sanitized or None, errors


def resolve_hint_channel(fact: dict[str, Any]) -> str | None:
    claim = str(fact.get("claim") or "")
    prefix, _ = _split_claim(claim)
    if prefix in CLAIM_PREFIX_TO_CHANNEL:
        return CLAIM_PREFIX_TO_CHANNEL[prefix]

    knowledge_type = fact.get("knowledge_type")
    if isinstance(knowledge_type, str):
        return KNOWLEDGE_TYPE_TO_CHANNEL.get(knowledge_type)

    return None


def map_fact_to_hint(fact: dict[str, Any]) -> dict[str, Any] | None:
    channel = resolve_hint_channel(fact)
    if channel is None:
        return None

    claim = str(fact.get("claim") or "")
    _, claim_value = _split_claim(claim)

    return {
        "knowledge_id": fact.get("knowledge_id"),
        "claim": claim,
        "knowledge_type": fact.get("knowledge_type"),
        "hint_channel": channel,
        "hint_value": claim_value,
        "application_mode": CHANNEL_DEFAULT_APPLICATION_MODE[channel],
        "influence_level": fact.get("influence_level"),
        "confidence": fact.get("confidence"),
        "freshness_score": fact.get("freshness_score"),
        "relevance_score": fact.get("relevance_score"),
        "final_score": fact.get("final_score"),
        "runtime_decision_id": fact.get("runtime_decision_id"),
    }


def build_hint_channels(hints: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    channels: dict[str, list[dict[str, Any]]] = {ch: [] for ch in ALLOWED_HINT_CHANNELS}
    for hint in hints:
        channel = hint.get("hint_channel")
        if isinstance(channel, str) and channel in channels:
            channels[channel].append(hint)
    return channels


def compute_influence_summary(hints: list[dict[str, Any]]) -> dict[str, Any]:
    levels = [str(h.get("influence_level") or "low") for h in hints]
    has_medium = any(level == "medium" for level in levels)
    return {
        "hint_count": len(hints),
        "max_influence_level": "medium" if has_medium else ("low" if hints else "none"),
        "channels_used": sorted(
            {str(h.get("hint_channel")) for h in hints if h.get("hint_channel")}
        ),
    }


def try_build_day_engine_knowledge_input_v1(
    knowledge_context_slice: dict[str, Any],
    *,
    day_model_snapshot: dict[str, Any] | None = None,
    created_at: str | None = None,
    integration_id: str | None = None,
) -> dict[str, Any]:
    """
    Map Knowledge Context Slice → Day Engine read-only hint input.

    Does not mutate day_model or apply hints — contract boundary only.
    """
    reasons: list[str] = []

    if knowledge_context_slice.get("contract_version") != KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT:
        reasons.append("invalid context slice contract_version")

    if knowledge_context_slice.get("status") != CONTEXT_SLICE_STATUS_READY:
        reasons.append("context slice status must be ready")

    if knowledge_context_slice.get("profile_update_allowed") is not False:
        reasons.append("context slice profile_update_allowed must be false")

    sanitized_snapshot, snapshot_errors = sanitize_day_model_snapshot(day_model_snapshot)
    reasons.extend(snapshot_errors)

    if reasons:
        return {
            "result": INTEGRATION_RESULT_REJECTED,
            "reasons": reasons,
            "knowledge_input": None,
        }

    selected_facts = knowledge_context_slice.get("selected_facts")
    if not isinstance(selected_facts, list):
        reasons.append("selected_facts must be a list")
        return {
            "result": INTEGRATION_RESULT_REJECTED,
            "reasons": reasons,
            "knowledge_input": None,
        }

    hints: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    channel_counts: dict[str, int] = {ch: 0 for ch in ALLOWED_HINT_CHANNELS}

    for fact in selected_facts:
        if not isinstance(fact, dict):
            skipped.append({"reason": "invalid_fact_shape"})
            continue

        hint = map_fact_to_hint(fact)
        if hint is None:
            skipped.append(
                {
                    "knowledge_id": fact.get("knowledge_id"),
                    "claim": fact.get("claim"),
                    "reason": "unmapped_claim",
                }
            )
            continue

        channel = str(hint["hint_channel"])
        if channel_counts[channel] >= MAX_HINTS_PER_CHANNEL:
            skipped.append(
                {
                    "knowledge_id": fact.get("knowledge_id"),
                    "claim": fact.get("claim"),
                    "reason": "channel_cap_exceeded",
                    "detail": f"max={MAX_HINTS_PER_CHANNEL}",
                }
            )
            continue

        if len(hints) >= MAX_TOTAL_HINTS:
            skipped.append(
                {
                    "knowledge_id": fact.get("knowledge_id"),
                    "claim": fact.get("claim"),
                    "reason": "total_cap_exceeded",
                    "detail": f"max={MAX_TOTAL_HINTS}",
                }
            )
            continue

        channel_counts[channel] += 1
        hints.append(hint)

    knowledge_input = {
        "contract_version": DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT,
        "integration_id": integration_id or generate_integration_id(),
        "context_slice_id": knowledge_context_slice.get("context_slice_id"),
        "target_surface": knowledge_context_slice.get("target_surface"),
        "consumer": CONSUMER_DAY_ENGINE,
        "integration_policy_version": INTEGRATION_POLICY_VERSION,
        "knowledge_applied": False,
        "hint_channels": build_hint_channels(hints),
        "hints": hints,
        "skipped_facts": skipped,
        "influence_summary": compute_influence_summary(hints),
        "day_model_snapshot_hash": _hash_snapshot(sanitized_snapshot)
        if sanitized_snapshot
        else None,
        "traceability": {
            "context_slice_id": knowledge_context_slice.get("context_slice_id"),
            "knowledge_ids": [h["knowledge_id"] for h in hints if h.get("knowledge_id")],
            "runtime_decision_ids": [
                h["runtime_decision_id"] for h in hints if h.get("runtime_decision_id")
            ],
            "selection_policy_version": knowledge_context_slice.get(
                "selection_policy_version"
            ),
            "selected_count": len(selected_facts),
            "integrated_count": len(hints),
            "skipped_count": len(skipped),
        },
        "status": INTEGRATION_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }

    validation_errors = validate_day_engine_knowledge_input_v1(knowledge_input)
    if validation_errors:
        return {
            "result": INTEGRATION_RESULT_REJECTED,
            "reasons": validation_errors,
            "knowledge_input": None,
        }

    return {
        "result": INTEGRATION_RESULT_CREATED,
        "reasons": [],
        "knowledge_input": knowledge_input,
    }


def generate_integration_id() -> str:
    return f"deki-{uuid4()}"


def validate_day_engine_knowledge_input_v1(knowledge_input: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if knowledge_input.get("contract_version") != DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_ENGINE_KNOWLEDGE_INPUT_V1_KEYS:
        if key not in knowledge_input:
            errors.append(f"missing field: {key}")

    if knowledge_input.get("consumer") != CONSUMER_DAY_ENGINE:
        errors.append("consumer must be day_engine")

    if knowledge_input.get("knowledge_applied") is not False:
        errors.append("knowledge_applied must be false at contract build")

    if knowledge_input.get("status") != INTEGRATION_STATUS_READY:
        errors.append("status must be ready")

    for flag in (
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    ):
        if knowledge_input.get(flag) is not False:
            errors.append(f"{flag} must be false")

    hints = knowledge_input.get("hints")
    if isinstance(hints, list):
        if len(hints) > MAX_TOTAL_HINTS:
            errors.append("hints exceeds max total cap")
        for hint in hints:
            if not isinstance(hint, dict):
                errors.append("invalid hint entry")
                continue
            mode = hint.get("application_mode")
            if mode not in ALLOWED_APPLICATION_MODES:
                errors.append(f"invalid application_mode: {mode}")
            channel = hint.get("hint_channel")
            if channel not in ALLOWED_HINT_CHANNELS:
                errors.append(f"invalid hint_channel: {channel}")

    hint_channels = knowledge_input.get("hint_channels")
    if isinstance(hint_channels, dict):
        for channel, items in hint_channels.items():
            if channel not in ALLOWED_HINT_CHANNELS:
                errors.append(f"invalid hint_channels key: {channel}")
            elif isinstance(items, list) and len(items) > MAX_HINTS_PER_CHANNEL:
                errors.append(f"hint_channels.{channel} exceeds cap")

    return errors
