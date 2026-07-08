"""Tests for attachment reference → deep block ordering."""

from todayflow_backend.services.compatibility_attachment_reference_v0 import (
    build_attachment_reference_context,
    build_deep_block_order,
    reorder_analysis_blocks,
    score_attachment_styles,
)
from todayflow_backend.services.sign_compatibility_product import SignCompatAnalysisBlock


def _blocks() -> list[SignCompatAnalysisBlock]:
    keys = ["emotions", "communication", "conflicts", "sexuality", "long_term"]
    return [
        SignCompatAnalysisBlock(
            key=k,
            title=k,
            subtitle="",
            takeaway=f"takeaway-{k}",
            detail="",
            risk="",
            action="",
        )
        for k in keys
    ]


def test_score_attachment_styles_from_communication_yes() -> None:
    hints = score_attachment_styles({"communication": "yes"})
    assert hints
    assert hints[0]["code"] in {"secure", "anxious", "dismissive_avoidant", "fearful_avoidant"}
    assert hints[0]["confirmation_required"] is True


def test_deep_block_order_prioritizes_echoed_block() -> None:
    order = build_deep_block_order({"conflicts": "yes", "communication": "partial"})
    assert order[0] in {"conflicts", "communication", "emotions"}


def test_reorder_analysis_blocks() -> None:
    blocks = _blocks()
    order = ["conflicts", "communication", "emotions", "sexuality", "long_term"]
    reordered = reorder_analysis_blocks(blocks, order)
    assert [b.key for b in reordered[:3]] == ["conflicts", "communication", "emotions"]


def test_build_attachment_reference_context() -> None:
    ctx = build_attachment_reference_context({"communication": "yes", "conflicts": "yes"})
    assert ctx is not None
    assert isinstance(ctx.get("deep_block_order"), list)
    assert len(ctx.get("attachment_style_hints") or []) >= 1


def test_no_context_without_feedback() -> None:
    assert build_attachment_reference_context({}) is None
    assert build_attachment_reference_context(None) is None
