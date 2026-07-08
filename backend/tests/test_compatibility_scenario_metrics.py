"""Scenario metrics produce different subscores per theme."""

from todayflow_backend.services.compatibility_scenario_metrics import apply_scenario_metrics


def test_different_scenarios_yield_different_subscores() -> None:
    base = {"attraction": 80, "stability": 73, "conflicts": 73, "sexuality": 82}
    love_sub, love_score = apply_scenario_metrics(
        "love", base, 78, from_sign="aries", to_sign="libra", from_element="fire", to_element="air"
    )
    office_sub, office_score = apply_scenario_metrics(
        "office", base, 78, from_sign="aries", to_sign="libra", from_element="fire", to_element="air"
    )
    assert love_sub.model_dump() != office_sub.model_dump()
    assert love_score != office_score or love_sub.stability != office_sub.stability


def test_same_pair_different_scenarios_change_hero() -> None:
    base = {"attraction": 76, "stability": 70, "conflicts": 68, "sexuality": 79}
    _, s1 = apply_scenario_metrics("sex", base, 75, from_sign="leo", to_sign="aquarius")
    _, s2 = apply_scenario_metrics("money_together", base, 75, from_sign="leo", to_sign="aquarius")
    assert s1 != s2


def test_funnel_domains_filtered_by_scenario() -> None:
    from todayflow_backend.services.compatibility_funnel_artifact import build_compatibility_funnel_artifact

    art_love = build_compatibility_funnel_artifact(
        mode="quick",
        relationship_context="in_relationship",
        overall_score=78,
        subscores={"attraction": 80, "stability": 73, "conflicts": 73, "sexuality": 82},
        pair_dynamics={"user_1_contact_style": "a", "user_2_contact_style": "b", "leader_guess": "mixed", "withdrawer_guess": "mixed"},
        user1_label="A",
        user2_label="B",
        from_element="fire",
        to_element="air",
        from_modality="cardinal",
        to_modality="fixed",
        locale="ru",
        format_id="office",
    )
    art_full = build_compatibility_funnel_artifact(
        mode="quick",
        relationship_context="in_relationship",
        overall_score=78,
        subscores={"attraction": 80, "stability": 73, "conflicts": 73, "sexuality": 82},
        pair_dynamics={"user_1_contact_style": "a", "user_2_contact_style": "b", "leader_guess": "mixed", "withdrawer_guess": "mixed"},
        user1_label="A",
        user2_label="B",
        from_element="fire",
        to_element="air",
        from_modality="cardinal",
        to_modality="fixed",
        locale="ru",
    )
    assert art_love.scenario_id == "office"
    assert len(art_love.domain_scores) == 4
    assert len(art_full.domain_scores) >= 6
    assert {d.domain_id for d in art_love.domain_scores} == {"work_live", "conflicts", "money", "emotional"}
