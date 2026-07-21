"""Validate Compatibility content contracts (length, language, bans, contradictions)."""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from todayflow_backend.services.compatibility_content_v1.banned_phrases import find_banned_hits
from todayflow_backend.services.compatibility_content_v1.contracts import (
    GuestContentV1,
    PremiumContentV1,
    RegisteredContentV1,
)

_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
_SIGN_NAME_RE = re.compile(
    r"\b(овен|телец|близнецы|рак|лев|дева|весы|скорпион|стрелец|козерог|водолей|рыбы)\b",
    re.I,
)


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", (text or "").strip()) if w])


def _has_cyrillic(text: str) -> bool:
    return bool(_CYRILLIC_RE.search(text or ""))


def _collect_text(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return " ".join(_collect_text(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return " ".join(_collect_text(v) for v in obj)
    if hasattr(obj, "model_dump"):
        return _collect_text(obj.model_dump())
    return str(obj)


def validate_guest_dict(data: dict[str, Any]) -> tuple[GuestContentV1 | None, list[str]]:
    errors: list[str] = []
    try:
        model = GuestContentV1.model_validate(data)
    except ValidationError as exc:
        return None, [f"schema:{e['loc']}:{e['msg']}" for e in exc.errors()]

    blob = _collect_text(model)
    wc = _word_count(
        " ".join(
            [
                model.summary,
                model.attraction,
                model.main_risk,
                model.practical_advice,
            ]
        )
    )
    if model.locale.startswith("ru") and not _has_cyrillic(blob):
        errors.append("locale:expected_cyrillic")
    if wc < 90:
        errors.append(f"length:too_short:{wc}")
    if wc > 220:
        errors.append(f"length:too_long:{wc}")
    hits = find_banned_hits(blob, locale=model.locale)
    errors.extend(f"banned:{h}" for h in hits)
    # Sign names should not dominate every sentence.
    sign_hits = len(_SIGN_NAME_RE.findall(blob))
    if sign_hits > 8:
        errors.append(f"sign_name_spam:{sign_hits}")
    if errors:
        return model, errors
    return model, []


def validate_registered_dict(data: dict[str, Any]) -> tuple[RegisteredContentV1 | None, list[str]]:
    errors: list[str] = []
    try:
        model = RegisteredContentV1.model_validate(data)
    except ValidationError as exc:
        return None, [f"schema:{e['loc']}:{e['msg']}" for e in exc.errors()]

    blocks = [
        model.emotions,
        model.communication,
        model.conflict,
        model.strengths,
        model.vulnerable_spot,
        model.what_helps,
    ]
    # Near-duplicate blocks (same opening 40 chars).
    openings = [b.strip()[:40].lower() for b in blocks]
    if len(set(openings)) < len(openings) - 1:
        errors.append("repetition:block_openings_too_similar")

    blob = _collect_text(model)
    if model.locale.startswith("ru") and not _has_cyrillic(blob):
        errors.append("locale:expected_cyrillic")
    hits = find_banned_hits(blob, locale=model.locale)
    errors.extend(f"banned:{h}" for h in hits)
    # summary should not equal emotions
    if model.summary.strip()[:80] == model.emotions.strip()[:80]:
        errors.append("repetition:summary_equals_emotions")
    if errors:
        return model, errors
    return model, []


def validate_premium_dict(data: dict[str, Any]) -> tuple[PremiumContentV1 | None, list[str]]:
    errors: list[str] = []
    try:
        model = PremiumContentV1.model_validate(data)
    except ValidationError as exc:
        return None, [f"schema:{e['loc']}:{e['msg']}" for e in exc.errors()]

    blob = _collect_text(model)
    if model.locale.startswith("ru") and not _has_cyrillic(blob):
        errors.append("locale:expected_cyrillic")
    hits = find_banned_hits(blob, locale=model.locale)
    errors.extend(f"banned:{h}" for h in hits)

    do_n = model.do.strip().lower()
    avoid_n = model.avoid.strip().lower()
    # Crude contradiction: same core verb phrase.
    if do_n and avoid_n and (do_n in avoid_n or avoid_n in do_n):
        errors.append("contradiction:do_vs_avoid")

    # Verdict tone vs reason length already enforced; soft check for "нет" with "обязательно продолжайте"
    if model.verdict in ("нет", "скорее нет") and any(
        x in model.verdict_reason.lower() for x in ("обязательно продолж", "идеальная пара", "всё будет хорошо")
    ):
        errors.append("contradiction:verdict_vs_reason")

    if errors:
        return model, errors
    return model, []
