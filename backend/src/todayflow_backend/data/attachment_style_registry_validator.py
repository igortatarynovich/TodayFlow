"""Import pilot — Validate attachment style reference registry."""

from __future__ import annotations

from typing import Any

ATTACHMENT_STYLE_REGISTRY_V1_CONTRACT = "attachment_style_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "review", "active"})
ALLOWED_STYLE_STATUSES = frozenset({"draft", "review", "active"})
DEEP_BLOCK_KEYS = frozenset({"emotions", "communication", "conflicts", "sexuality", "long_term"})

REGISTRY_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "source",
        "attachment_styles",
    }
)

STYLE_KEYS = frozenset(
    {
        "code",
        "label_ru",
        "label_en",
        "summary_ru",
        "summary_en",
        "deep_block_bias",
        "relationship_signals",
        "status",
        "version",
    }
)


def validate_attachment_style_registry_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"]

    missing = REGISTRY_TOP_KEYS - set(payload.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    if payload.get("contract_version") != ATTACHMENT_STYLE_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")
    if payload.get("domain") != "psychology":
        errors.append("domain must be psychology")
    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid registry status")

    source = payload.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    elif not str(source.get("license") or "").strip():
        errors.append("source.license required for imported reference")

    styles = payload.get("attachment_styles")
    if not isinstance(styles, dict) or not styles:
        errors.append("attachment_styles must be a non-empty object")
        return errors

    for key, style in styles.items():
        if not isinstance(style, dict):
            errors.append(f"{key}: style must be object")
            continue
        code = str(style.get("code") or "")
        if code != key:
            errors.append(f"{key}: key must match code ({code})")
        if set(style.keys()) != STYLE_KEYS:
            errors.append(f"{key}: invalid style keys")
        if style.get("status") not in ALLOWED_STYLE_STATUSES:
            errors.append(f"{key}: invalid status")

        bias = style.get("deep_block_bias")
        if not isinstance(bias, dict) or set(bias.keys()) != DEEP_BLOCK_KEYS:
            errors.append(f"{key}: deep_block_bias must cover {sorted(DEEP_BLOCK_KEYS)}")
        else:
            total = 0.0
            for block, weight in bias.items():
                try:
                    w = float(weight)
                except (TypeError, ValueError):
                    errors.append(f"{key}.deep_block_bias.{block}: invalid weight")
                    continue
                if w < 0:
                    errors.append(f"{key}.deep_block_bias.{block}: weight must be >= 0")
                total += w
            if total <= 0:
                errors.append(f"{key}: deep_block_bias sum must be > 0")

        signals = style.get("relationship_signals")
        if not isinstance(signals, list) or not signals:
            errors.append(f"{key}: relationship_signals must be non-empty list")

    return errors
