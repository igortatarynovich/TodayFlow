"""Strict validation + quality/consistency gates for profile_contract_v1."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.profile_disclosure_funnel_v0 import SPHERE_FIELDS, SPHERE_IDS

PROFILE_CONTRACT_QUALITY_V1 = "profile_contract_quality_v1"

REQUIRED_TOP_LEVEL = (
    "identity_core",
    "strengths",
    "growth_zones",
    "relationship_style",
    "money_style",
    "decision_style",
    "recurring_patterns",
    "living_changes",
    "life_mission",
    "helps",
    "life_spheres",
)

GENERIC_PHRASE_MARKERS_RU = (
    "вселенная",
    "поток энергии",
    "слушай интуицию",
    "будь собой",
    "энергия дня",
    "уникальная душа",
    "звёзды говорят",
    "как все люди",
    "для любого человека",
    "в общем случае",
)

_CONTRADICTION_PAIRS = (
    (("быстр", "импульс", "сразу"), ("долг", "анализ", "тщательн", "медленн")),
    (("избег", "осторожн", "без риска"), ("риск", "смел", "прыж")),
)


def _norm(s: str) -> str:
    t = re.sub(r"\s+", " ", (s or "").strip().lower())
    t = re.sub(r"[«»\"'.,!?;:—\-]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?\n]+", text or "")
    return [p.strip() for p in parts if len(p.strip()) >= 12]


def _list_texts(contract: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in (
        "identity_core",
        "relationship_style",
        "money_style",
        "decision_style",
        "living_changes",
        "life_mission",
    ):
        out.append(str(contract.get(key) or ""))
    for key in ("strengths", "growth_zones", "recurring_patterns", "helps"):
        items = contract.get(key)
        if isinstance(items, list):
            out.extend(str(x) for x in items)
    spheres = contract.get("life_spheres")
    if isinstance(spheres, dict):
        for sid in SPHERE_IDS:
            row = spheres.get(sid)
            if isinstance(row, dict):
                for field in SPHERE_FIELDS:
                    out.append(str(row.get(field) or ""))
    return out


def validate_required_fields(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["contract_not_dict"]
    if str(contract.get("contract_version") or "") != "profile_contract_v1":
        errors.append("invalid_contract_version")

    if len(str(contract.get("identity_core") or "").strip()) < 20:
        errors.append("identity_core_short")
    for key in ("strengths", "growth_zones"):
        items = contract.get(key)
        if not isinstance(items, list) or len(items) < 3:
            errors.append(f"{key}_need_3")
        elif any(len(str(x or "").strip()) < 4 for x in items[:3]):
            errors.append(f"{key}_item_short")
    for key in ("relationship_style", "money_style", "decision_style", "life_mission"):
        if len(str(contract.get(key) or "").strip()) < 12:
            errors.append(f"{key}_short")
    if len(str(contract.get("living_changes") or "").strip()) < 12:
        errors.append("living_changes_required")
    patterns = contract.get("recurring_patterns")
    if not isinstance(patterns, list) or len(patterns) < 1 or len(str(patterns[0] or "").strip()) < 8:
        errors.append("recurring_patterns_required")
    helps = contract.get("helps")
    if not isinstance(helps, list) or len(helps) < 2:
        errors.append("helps_need_2")

    spheres = contract.get("life_spheres")
    if not isinstance(spheres, dict):
        errors.append("life_spheres_missing")
    else:
        for sid in SPHERE_IDS:
            row = spheres.get(sid)
            if not isinstance(row, dict):
                errors.append(f"sphere_{sid}_missing")
                continue
            for field in SPHERE_FIELDS:
                if len(str(row.get(field) or "").strip()) < 8:
                    errors.append(f"sphere_{sid}_{field}_short")
    return errors


def validate_quality_gates(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    texts = [t for t in _list_texts(contract) if t.strip()]
    # Duplicate sentences across the portrait
    seen: dict[str, str] = {}
    for text in texts:
        for sent in _sentences(text):
            key = _norm(sent)
            if len(key) < 20:
                continue
            if key in seen:
                errors.append("duplicate_sentence")
                break
            seen[key] = sent
        if "duplicate_sentence" in errors:
            break

    identity = _norm(str(contract.get("identity_core") or ""))
    if identity:
        spheres = contract.get("life_spheres") if isinstance(contract.get("life_spheres"), dict) else {}
        echo_hits = 0
        for sid in SPHERE_IDS:
            row = spheres.get(sid) if isinstance(spheres, dict) else None
            if not isinstance(row, dict):
                continue
            how = _norm(str(row.get("how") or ""))
            if how and (identity in how or how in identity):
                echo_hits += 1
        if echo_hits >= 3:
            errors.append("identity_echo_in_spheres")

    # Sphere distinctness: how fields must not be near-duplicates
    hows: list[str] = []
    spheres = contract.get("life_spheres") if isinstance(contract.get("life_spheres"), dict) else {}
    if isinstance(spheres, dict):
        for sid in SPHERE_IDS:
            row = spheres.get(sid)
            if isinstance(row, dict):
                hows.append(_norm(str(row.get("how") or "")))
    for i, a in enumerate(hows):
        if len(a) < 24:
            continue
        for b in hows[i + 1 :]:
            if not b:
                continue
            if a == b or (len(a) > 40 and (a in b or b in a)):
                errors.append("spheres_not_distinct")
                break
        if "spheres_not_distinct" in errors:
            break

    blob = " ".join(_norm(t) for t in texts)
    for marker in GENERIC_PHRASE_MARKERS_RU:
        if marker in blob:
            errors.append(f"generic_phrase:{marker}")
            break
    return errors


def validate_consistency(contract: dict[str, Any]) -> list[str]:
    """Lightweight lexical consistency across styles vs identity/spheres."""
    errors: list[str] = []
    identity = _norm(str(contract.get("identity_core") or ""))
    decision = _norm(str(contract.get("decision_style") or ""))
    work_how = ""
    spheres = contract.get("life_spheres")
    if isinstance(spheres, dict) and isinstance(spheres.get("work"), dict):
        work_how = _norm(str(spheres["work"].get("how") or ""))

    pack = " ".join([identity, decision, work_how])
    for fast_keys, slow_keys in _CONTRADICTION_PAIRS:
        has_fast = any(k in pack for k in fast_keys)
        has_slow = any(k in pack for k in slow_keys)
        # Only flag when both sides appear in different primary fields, not same sentence
        if has_fast and has_slow:
            id_fast = any(k in identity for k in fast_keys)
            dec_slow = any(k in decision for k in slow_keys)
            if id_fast and dec_slow:
                errors.append("tempo_contradiction_identity_vs_decision")
                break
    return errors


def validate_profile_contract_strict(contract: dict[str, Any]) -> dict[str, Any]:
    required = validate_required_fields(contract)
    quality = validate_quality_gates(contract) if not required else []
    consistency = validate_consistency(contract) if not required else []
    ok = not required and not quality and not consistency
    return {
        "contract_version": PROFILE_CONTRACT_QUALITY_V1,
        "ok": ok,
        "required_errors": required,
        "quality_errors": quality,
        "consistency_errors": consistency,
        "all_errors": required + quality + consistency,
    }
