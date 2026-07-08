"""Pair compare/synastry scenario metrics wiring."""

from todayflow_backend.api.compatibility import (
    _build_pair_scenario_context,
    _resolve_pair_format_id,
)


def test_resolve_pair_format_from_explicit_id() -> None:
    assert _resolve_pair_format_id("romantic", "office") == "office"
    assert _resolve_pair_format_id("romantic", "after_wine") == "after_wine"


def test_resolve_pair_format_from_relation_mode() -> None:
    assert _resolve_pair_format_id("business", None) == "office"
    assert _resolve_pair_format_id("parent_child", None) == "parenting"
    assert _resolve_pair_format_id("romantic", None) == "love"


def test_pair_scenario_context_differs_by_format() -> None:
    base_deep = {
        "dimensions": [
            {"key": "attraction", "score": 80},
            {"key": "emotional", "score": 72},
            {"key": "communication", "score": 70},
            {"key": "stability", "score": 74},
            {"key": "long_term", "score": 76},
        ]
    }
    love_ctx = _build_pair_scenario_context(
        format_id="love",
        relation_mode="romantic",
        deep_dive=base_deep,
        overall_score=78,
        from_sign="aries",
        to_sign="libra",
        from_element="fire",
        to_element="air",
        from_modality="cardinal",
        to_modality="cardinal",
    )
    office_ctx = _build_pair_scenario_context(
        format_id="office",
        relation_mode="romantic",
        deep_dive=base_deep,
        overall_score=78,
        from_sign="aries",
        to_sign="libra",
        from_element="fire",
        to_element="air",
        from_modality="cardinal",
        to_modality="cardinal",
    )
    assert love_ctx.format_id == "love"
    assert office_ctx.format_id == "office"
    assert love_ctx.subscores != office_ctx.subscores or love_ctx.display_score != office_ctx.display_score


def test_playful_pair_skips_funnel_tone() -> None:
    ctx = _build_pair_scenario_context(
        format_id="after_wine",
        relation_mode="romantic",
        deep_dive=None,
        overall_score=70,
        from_sign="leo",
        to_sign="aquarius",
        from_element="fire",
        to_element="air",
        from_modality="fixed",
        to_modality="fixed",
    )
    assert ctx.format_id == "after_wine"
    assert ctx.tone_mode == "playful"
