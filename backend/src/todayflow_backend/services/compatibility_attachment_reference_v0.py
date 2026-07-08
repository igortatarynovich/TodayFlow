"""Attachment style reference → compatibility deep block ordering (CD → engine).

Uses DATA/reference/psychology/attachment_style_registry_v1.json (draft).
Hypothesis-only: not user diagnosis; confirmation_required on promoted atoms.

Canon: INTERPRETATION_LAYER spawn from reference · USER_KNOWLEDGE_MODEL hypothesis
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.attachment_style_registry_loader import (
    deep_block_bias_for_style,
    list_attachment_styles,
)
from todayflow_backend.services.sign_compatibility_product import SignCompatAnalysisBlock

COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT = "compatibility_attachment_reference_v0"

DEEP_BLOCK_KEYS: tuple[str, ...] = (
    "emotions",
    "communication",
    "conflicts",
    "sexuality",
    "long_term",
)
ATTACHMENT_TRIGGER_BLOCKS = frozenset({"emotions", "communication", "conflicts"})

ECHO_SIGNAL_WEIGHT = {"yes": 1.0, "partial": 0.55, "no": 0.12}

# Pair deep_dive dimension keys (synastry/compare) ↔ attachment block keys
PAIR_DIMENSION_ATTACHMENT_BOOST: dict[str, tuple[str, ...]] = {
    "emotional": ("emotions", "communication"),
    "communication": ("communication", "conflicts"),
    "stability": ("conflicts", "long_term"),
    "attraction": ("sexuality", "emotions"),
    "long_term": ("long_term", "stability"),
}


def _feedback_clean(block_feedback: dict[str, str] | None) -> dict[str, str]:
    if not block_feedback:
        return {}
    out: dict[str, str] = {}
    for key, val in block_feedback.items():
        k = str(key).strip().lower()
        v = str(val).strip().lower()
        if k in DEEP_BLOCK_KEYS and v in ECHO_SIGNAL_WEIGHT:
            out[k] = v
    return out


def _has_attachment_triggers(block_feedback: dict[str, str]) -> bool:
    return any(k in ATTACHMENT_TRIGGER_BLOCKS and v in {"yes", "partial"} for k, v in block_feedback.items())


def score_attachment_styles(
    block_feedback: dict[str, str] | None,
    *,
    locale: str = "ru",
) -> list[dict[str, Any]]:
    """Rank attachment styles by echo alignment with deep_block_bias (reference CD)."""
    fb = _feedback_clean(block_feedback)
    if not _has_attachment_triggers(fb):
        return []

    loc = "ru" if (locale or "ru").strip().split("-")[0].lower() == "ru" else "en"
    ranked: list[tuple[float, dict[str, Any]]] = []

    for style in list_attachment_styles(allowed_statuses=frozenset({"active"})):
        code = str(style.get("code") or "")
        if not code:
            continue
        score = 0.0
        evidence_blocks: list[str] = []
        for block_key, echo in fb.items():
            if block_key not in ATTACHMENT_TRIGGER_BLOCKS:
                continue
            bias = deep_block_bias_for_style(code, block_key)
            if bias is None:
                continue
            weight = ECHO_SIGNAL_WEIGHT.get(echo, 0.0)
            if weight <= 0:
                continue
            score += bias * weight
            evidence_blocks.append(block_key)

        if score <= 0:
            continue

        label = style.get("label_ru") if loc == "ru" else style.get("label_en")
        summary = style.get("summary_ru") if loc == "ru" else style.get("summary_en")
        ranked.append(
            (
                score,
                {
                    "code": code,
                    "label": str(label or code),
                    "summary": str(summary or "")[:240],
                    "score": round(score, 4),
                    "evidence_blocks": evidence_blocks,
                    "confirmation_required": True,
                    "knowledge_type": "hypothesis",
                    "source": COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT,
                },
            )
        )

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in ranked[:3]]


def build_deep_block_order(
    block_feedback: dict[str, str] | None,
    *,
    attachment_hints: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Order deep blocks: attachment bias × echo, then canonical tail."""
    fb = _feedback_clean(block_feedback)
    hints = attachment_hints if attachment_hints is not None else score_attachment_styles(fb)
    block_scores: dict[str, float] = {k: 0.05 for k in DEEP_BLOCK_KEYS}

    if hints:
        primary = hints[0]
        code = str(primary.get("code") or "")
        for block_key in DEEP_BLOCK_KEYS:
            bias = deep_block_bias_for_style(code, block_key)
            if bias is not None:
                block_scores[block_key] += bias * 0.85
        for block_key, echo in fb.items():
            if echo in {"yes", "partial"}:
                block_scores[block_key] += ECHO_SIGNAL_WEIGHT[echo] * 0.35
    else:
        for block_key, echo in fb.items():
            if echo in {"yes", "partial"}:
                block_scores[block_key] += ECHO_SIGNAL_WEIGHT[echo]

    ordered = sorted(DEEP_BLOCK_KEYS, key=lambda k: block_scores.get(k, 0.0), reverse=True)
    return list(ordered)


def build_attachment_reference_context(
    block_feedback: dict[str, str] | None,
    *,
    locale: str = "ru",
) -> dict[str, Any] | None:
    """Compact slice for learning context / API (no diagnosis wording)."""
    fb = _feedback_clean(block_feedback)
    if not fb:
        return None
    hints = score_attachment_styles(fb, locale=locale)
    order = build_deep_block_order(fb, attachment_hints=hints)
    if not hints and order == list(DEEP_BLOCK_KEYS):
        return None
    from todayflow_backend.data.attachment_style_registry_loader import load_attachment_style_registry_v1

    registry_status = str(load_attachment_style_registry_v1().get("status") or "review")
    return {
        "contract_version": COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT,
        "deep_block_order": order,
        "attachment_style_hints": hints,
        "trigger_blocks": [k for k in order if k in fb],
        "reference_status": registry_status,
    }


def reorder_analysis_blocks(
    blocks: list[SignCompatAnalysisBlock],
    deep_block_order: list[str],
) -> list[SignCompatAnalysisBlock]:
    by_key = {b.key: b for b in blocks}
    ordered: list[SignCompatAnalysisBlock] = []
    for key in deep_block_order:
        if key in by_key:
            ordered.append(by_key[key])
    for block in blocks:
        if block.key not in {b.key for b in ordered}:
            ordered.append(block)
    return ordered if ordered else blocks


def reorder_deep_dive_dimensions(
    deep_dive: dict[str, Any] | None,
    deep_block_order: list[str],
) -> dict[str, Any] | None:
    if not deep_dive or not isinstance(deep_dive.get("dimensions"), list):
        return deep_dive
    dimensions = [d for d in deep_dive["dimensions"] if isinstance(d, dict)]
    if not dimensions:
        return deep_dive

    def dim_score(dim: dict[str, Any]) -> float:
        key = str(dim.get("key") or "").strip().lower()
        total = 0.0
        for rank, block_key in enumerate(deep_block_order):
            rank_boost = max(0.0, (len(deep_block_order) - rank) / len(deep_block_order))
            mapped = PAIR_DIMENSION_ATTACHMENT_BOOST.get(key, ())
            if block_key in mapped:
                total += rank_boost
        return total

    sorted_dims = sorted(dimensions, key=dim_score, reverse=True)
    out = dict(deep_dive)
    out["dimensions"] = sorted_dims
    return out


def apply_attachment_reference_to_surface(
    product_surface: Any,
    block_feedback: dict[str, str] | None,
    *,
    locale: str = "ru",
) -> dict[str, Any] | None:
    """Reorder product_surface.blocks when attachment reference applies."""
    ctx = build_attachment_reference_context(block_feedback, locale=locale)
    if not ctx or not getattr(product_surface, "blocks", None):
        return ctx
    order = ctx.get("deep_block_order") or []
    if isinstance(order, list) and order:
        product_surface.blocks = reorder_analysis_blocks(list(product_surface.blocks), order)
    return ctx
