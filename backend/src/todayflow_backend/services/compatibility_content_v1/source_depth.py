"""Resolve factual depth of inputs — drives honest copy constraints."""

from __future__ import annotations

from typing import Any, Optional

from todayflow_backend.services.compatibility_content_v1.contracts import SourceDepth


def resolve_source_depth(
    *,
    mode: str | None = None,
    has_birth_dates: bool = False,
    profile_a_ready: bool = False,
    profile_b_ready: bool = False,
    has_signs: bool = True,
) -> SourceDepth:
    if profile_a_ready and profile_b_ready:
        return "two_profiles"
    if profile_a_ready or profile_b_ready:
        return "profile_enriched"
    if has_birth_dates or (mode or "").strip().lower() == "precise":
        return "birth_dates"
    if has_signs:
        return "zodiac_only"
    return "zodiac_only"


def depth_honesty_line(depth: SourceDepth, *, locale: str = "ru") -> str:
    """User-facing honesty line (no technical jargon)."""
    ru = not (locale or "ru").lower().startswith("en")
    if depth == "two_profiles":
        return (
            "Разбор опирается на стили общения и реакции обоих — не только на знаки."
            if ru
            else "This reading uses both people's communication styles — not signs alone."
        )
    if depth == "profile_enriched":
        return (
            "Часть выводов опирается на ваш профиль; о партнёре — осторожнее, данных меньше."
            if ru
            else "Part of this uses your profile; we stay cautious about the partner."
        )
    if depth == "birth_dates":
        # v1.1: do not claim life-path numbers until they are computed into the prompt.
        return (
            "Учтены знаки, определённые по датам рождения. Для более глубокого разбора нужны дополнительные данные."
            if ru
            else "Signs are derived from birth dates. Deeper reading needs more profile data."
        )
    return (
        "По знакам видна общая динамика, но этого недостаточно, чтобы судить о реальном поведении в конфликте."
        if ru
        else "Signs show a general dynamic — not enough to judge real conflict behaviour."
    )


def depth_from_payload(payload: dict[str, Any] | None) -> SourceDepth:
    p = payload or {}
    return resolve_source_depth(
        mode=str(p.get("mode") or ""),
        has_birth_dates=bool(p.get("birth_date_1") and p.get("birth_date_2")),
        profile_a_ready=bool(p.get("profile_a_ready")),
        profile_b_ready=bool(p.get("profile_b_ready")),
        has_signs=bool(p.get("from_sign") and p.get("to_sign")),
    )
