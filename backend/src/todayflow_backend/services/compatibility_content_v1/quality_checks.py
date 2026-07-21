"""Structural quality checks beyond schema validation (C2 §7)."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from todayflow_backend.services.compatibility_content_v1.banned_phrases import find_banned_hits
from todayflow_backend.services.compatibility_content_v1.validators import (
    validate_guest_dict,
    validate_premium_dict,
    validate_registered_dict,
)

_FABRICATED_PARTNER = re.compile(
    r"(партн[её]р(ша)?\s+(всегда|никогда|точно)\s|"
    r"он(а)?\s+(всегда|никогда)\s|"
    r"ваш партн[её]р\s+(работает|живёт|имеет детей))",
    re.I,
)


def _norm_sense(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").lower().strip())
    t = re.sub(r"[^\w\sа-яё]", "", t, flags=re.I)
    return t[:240]


def sense_fingerprint(payload: dict[str, Any]) -> str:
    """Stable short hash of meaning-bearing fields for stability checks."""
    keys = (
        "headline",
        "summary",
        "attraction",
        "main_risk",
        "practical_advice",
        "emotions",
        "communication",
        "conflict",
        "verdict",
        "do",
        "avoid",
        "next_step",
    )
    blob = "|".join(_norm_sense(str(payload.get(k) or "")) for k in keys)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def check_guest_vs_registered_distinct(
    guest: dict[str, Any],
    registered: dict[str, Any],
) -> list[str]:
    errs: list[str] = []
    g_sum = _norm_sense(str(guest.get("summary") or ""))
    r_sum = _norm_sense(str(registered.get("summary") or ""))
    if g_sum and r_sum and (g_sum == r_sum or g_sum in r_sum[: len(g_sum) + 20]):
        errs.append("tier_overlap:guest_summary_inside_registered")
    # Guest must not look like truncated registered (missing own practical_advice uniqueness).
    if not guest.get("locked_preview"):
        errs.append("guest_missing:locked_preview")
    if registered.get("emotions") and guest.get("emotions"):
        errs.append("guest_should_not_expose:emotions_full")
    return errs


def check_premium_vs_registered_distinct(
    premium: dict[str, Any],
    registered: dict[str, Any],
) -> list[str]:
    errs: list[str] = []
    p_do = _norm_sense(str(premium.get("do") or ""))
    r_advice = _norm_sense(str(registered.get("practical_advice") or ""))
    if p_do and r_advice and p_do == r_advice:
        errs.append("tier_overlap:premium_do_equals_registered_advice")
    for key in ("emotions", "communication", "conflict"):
        r_block = _norm_sense(str(registered.get(key) or ""))
        for pk in ("verdict_reason", "how", "focus_now"):
            p_block = _norm_sense(str(premium.get(pk) or ""))
            if r_block and p_block and r_block == p_block:
                errs.append(f"tier_overlap:premium_{pk}_copies_registered_{key}")
    if not premium.get("verdict"):
        errs.append("premium_missing:verdict")
    return errs


def check_no_fabricated_partner_facts(
    text_blob: str,
    *,
    known_facts: set[str] | None = None,
) -> list[str]:
    errs: list[str] = []
    if _FABRICATED_PARTNER.search(text_blob or ""):
        errs.append("hallucination:absolute_partner_claim")
    # If profiles absent, ban "в вашем профиле сказано" style false precision.
    known = known_facts or set()
    if "profile_b" not in known and re.search(r"в профиле партн", (text_blob or "").lower()):
        errs.append("hallucination:partner_profile_claimed")
    return errs


def check_source_depth_honesty(content: dict[str, Any]) -> list[str]:
    depth = str(content.get("source_depth") or "")
    blob = " ".join(str(v) for v in content.values() if isinstance(v, str)).lower()
    errs: list[str] = []
    if depth == "zodiac_only":
        overclaim = (
            "в реальном конфликте вы всегда",
            "точно знаем, как вы ссоритесь",
            "ваш стиль общения",
            "по вашему профилю",
        )
        for phrase in overclaim:
            if phrase in blob:
                errs.append(f"depth_overclaim:{phrase}")
    return errs


def check_template_diversity(
    outputs: list[dict[str, Any]],
    *,
    field: str = "summary",
    min_unique_ratio: float = 0.7,
) -> list[str]:
    """Different pairs should not share one template summary."""
    values = [_norm_sense(str(o.get(field) or "")) for o in outputs]
    values = [v for v in values if v]
    if len(values) < 3:
        return []
    unique = len(set(values))
    ratio = unique / len(values)
    if ratio < min_unique_ratio:
        return [f"template_collapse:{field}:{unique}/{len(values)}"]
    return []


def run_quality_suite(
    *,
    tier: str,
    content: dict[str, Any],
    peer_registered: dict[str, Any] | None = None,
    peer_guest: dict[str, Any] | None = None,
    known_facts: set[str] | None = None,
) -> dict[str, Any]:
    """Validate + structural checks. Returns {ok, errors, fingerprint}."""
    errors: list[str] = []
    model = None
    if tier == "guest":
        model, verr = validate_guest_dict(content)
        errors.extend(verr)
        if peer_registered:
            errors.extend(check_guest_vs_registered_distinct(content, peer_registered))
    elif tier == "registered":
        model, verr = validate_registered_dict(content)
        errors.extend(verr)
        if peer_guest:
            errors.extend(check_guest_vs_registered_distinct(peer_guest, content))
    elif tier == "premium":
        model, verr = validate_premium_dict(content)
        errors.extend(verr)
        if peer_registered:
            errors.extend(check_premium_vs_registered_distinct(content, peer_registered))
    else:
        errors.append(f"unknown_tier:{tier}")

    blob = " ".join(str(v) for v in content.values() if isinstance(v, (str, list)))
    errors.extend(find_banned_hits(blob, locale=str(content.get("locale") or "ru")))
    errors.extend(check_no_fabricated_partner_facts(blob, known_facts=known_facts))
    errors.extend(check_source_depth_honesty(content))

    return {
        "ok": not errors and model is not None,
        "errors": errors,
        "fingerprint": sense_fingerprint(content),
        "tier": tier,
    }
