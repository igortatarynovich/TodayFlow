"""Validate day content registry entries (P1.3)."""

from __future__ import annotations

import re
from typing import Any

EXPECTED_DAY_CONTENT_KEY_COUNT = 37
ENTRY_VERSION = "0.1.0"
TEXT_MEDIUM_MAX_MULTIPLIER = 2

ALLOWED_CONTENT_SLOTS = frozenset(
    {
        "headline",
        "guidance",
        "risk_warning",
        "action_hint",
        "reflection_hint",
        "tempo_hint",
    }
)
ENTRY_VERSION = "0.1.0"
TEXT_MEDIUM_MAX_MULTIPLIER = 2

ALLOWED_CONTENT_STATUSES = frozenset({"draft", "review", "active"})
ALLOWED_CONTENT_LOCALES = frozenset({"en"})
ALLOWED_CONTENT_TONES = frozenset({"neutral", "soft", "direct"})
ALLOWED_FORBIDDEN_CLAIMS = frozenset(
    {
        "outcome_guarantee",
        "medical_advice",
        "financial_advice",
        "destiny_claim",
        "domain_reference",
    }
)

ENTRY_REQUIRED_FIELDS = (
    "key",
    "slot",
    "status",
    "locale",
    "text_short",
    "text_medium",
    "tone",
    "max_chars",
    "forbidden_claims",
    "version",
)

PROHIBITED_PHRASE_PATTERNS = (
    re.compile(r"\bthe universe\b", re.I),
    re.compile(r"\buniverse wants\b", re.I),
    re.compile(r"\bcosmos\b", re.I),
    re.compile(r"\bdestiny\b", re.I),
    re.compile(r"\bfate\b", re.I),
    re.compile(r"\bguaranteed\b", re.I),
    re.compile(r"\byou will succeed\b", re.I),
    re.compile(r"\btarot\b", re.I),
    re.compile(r"\bhoroscope\b", re.I),
    re.compile(r"\bnumerology\b", re.I),
    re.compile(r"\bzodiac\b", re.I),
    re.compile(r"\bmajor arcana\b", re.I),
    re.compile(r"\bstars align\b", re.I),
    re.compile(r"\bdiagnos", re.I),
    re.compile(r"\binvest(ment|ing)\b", re.I),
    re.compile(r"\bfinancial return\b", re.I),
    re.compile(r"\bсегодня\b", re.I),
    re.compile(r"\bвселенн", re.I),
)


class DayContentRegistryValidationError(Exception):
    """Raised when registry content entries fail P1.3 validation."""


def validate_day_content_entry(key: str, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return [f"{key}: entry must be object"]

    for field in ENTRY_REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{key}: missing field {field!r}")

    entry_key = entry.get("key")
    if entry_key != key:
        errors.append(f"{key}: entry.key mismatch ({entry_key!r})")

    slot = entry.get("slot")
    if slot not in ALLOWED_CONTENT_SLOTS:
        errors.append(f"{key}: invalid slot {slot!r}")

    status = entry.get("status")
    if status not in ALLOWED_CONTENT_STATUSES:
        errors.append(f"{key}: invalid status {status!r}")

    locale = entry.get("locale")
    if locale not in ALLOWED_CONTENT_LOCALES:
        errors.append(f"{key}: invalid locale {locale!r}")

    tone = entry.get("tone")
    if tone not in ALLOWED_CONTENT_TONES:
        errors.append(f"{key}: invalid tone {tone!r}")

    version = entry.get("version")
    if version != ENTRY_VERSION:
        errors.append(f"{key}: expected version {ENTRY_VERSION!r}, got {version!r}")

    if entry.get("status") != "draft":
        errors.append(f"{key}: P1.3 seed entries must have status draft")

    text_short = entry.get("text_short")
    text_medium = entry.get("text_medium")
    max_chars = entry.get("max_chars")

    if not isinstance(text_short, str) or not text_short.strip():
        errors.append(f"{key}: text_short must be non-empty string")
    if not isinstance(text_medium, str) or not text_medium.strip():
        errors.append(f"{key}: text_medium must be non-empty string")

    if isinstance(max_chars, int) and isinstance(text_short, str):
        if len(text_short) > max_chars:
            errors.append(f"{key}: text_short exceeds max_chars ({len(text_short)}>{max_chars})")
        medium_limit = max_chars * TEXT_MEDIUM_MAX_MULTIPLIER
        if isinstance(text_medium, str) and len(text_medium) > medium_limit:
            errors.append(
                f"{key}: text_medium exceeds limit ({len(text_medium)}>{medium_limit})"
            )

    forbidden_claims = entry.get("forbidden_claims")
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        errors.append(f"{key}: forbidden_claims must be non-empty list")
    elif isinstance(forbidden_claims, list):
        unknown = [c for c in forbidden_claims if c not in ALLOWED_FORBIDDEN_CLAIMS]
        if unknown:
            errors.append(f"{key}: unknown forbidden_claims {unknown}")

    for field_name in ("text_short", "text_medium"):
        text = entry.get(field_name)
        if isinstance(text, str):
            errors.extend(_prohibited_phrase_errors(key, field_name, text))

    return errors


def _prohibited_phrase_errors(key: str, field_name: str, text: str) -> list[str]:
    errors: list[str] = []
    for pattern in PROHIBITED_PHRASE_PATTERNS:
        if pattern.search(text):
            errors.append(f"{key}: prohibited phrase in {field_name}: {pattern.pattern}")
    return errors


def validate_day_content_registry_keys(keys: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if len(keys) != EXPECTED_DAY_CONTENT_KEY_COUNT:
        errors.append(
            f"expected {EXPECTED_DAY_CONTENT_KEY_COUNT} keys, got {len(keys)}"
        )
    for key, entry in keys.items():
        if not key.startswith("day."):
            errors.append(f"invalid key prefix: {key!r}")
        errors.extend(validate_day_content_entry(key, entry))
    return errors


def validate_day_content_registry_payload(payload: dict[str, Any]) -> list[str]:
    keys = payload.get("keys")
    if not isinstance(keys, dict):
        return ["registry.keys must be object"]
    return validate_day_content_registry_keys(keys)
