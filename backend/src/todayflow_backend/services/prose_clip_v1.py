"""Boundary-aware prose clipping — shared SoT for day_scenario surfaces.

Never cut mid-word. Prefer sentence end, else last whitespace.
Also heals legacy mid-word «…» stumps already stored in generation_logs.
"""

from __future__ import annotations

from typing import Any


def heal_ellipsis_midword(text: str) -> str:
    """Fix stored mid-word «…» stumps (legacy raw-index clip) at the last space."""
    t = str(text or "").strip()
    if not t.endswith("…"):
        return t
    body = t[:-1].rstrip()
    if not body or body[-1] in ".!?…":
        return t
    sp = body.rfind(" ")
    if sp <= 0:
        return t
    last = body[sp + 1 :]
    if 1 <= len(last) <= 6:
        return body[:sp].rstrip() + "…"
    return t


def clip_prose(value: Any, n: int = 400) -> str:
    """Clip prose without mid-word cuts.

    Prefer the last sentence end (``.!?…``) in the window, else the last space.
    Short machine tokens (ids, enums) still hard-cut when no whitespace exists.
    """
    text = str(value or "").strip()
    if n <= 0:
        return ""
    if len(text) <= n:
        return text
    budget = max(1, int(n) - 1)
    window = text[:budget]
    min_keep = max(1, budget // 2) if budget >= 8 else 1

    best_sent = -1
    for i, ch in enumerate(window):
        if ch in ".!?…" and (i + 1) >= min_keep:
            best_sent = i + 1
    if best_sent >= min_keep:
        cut = window[:best_sent].rstrip()
        if cut and cut[-1] in ".!?…":
            return cut
        return cut + "…"

    sp = window.rfind(" ")
    if sp >= min_keep:
        return window[:sp].rstrip() + "…"
    return window.rstrip() + "…"
