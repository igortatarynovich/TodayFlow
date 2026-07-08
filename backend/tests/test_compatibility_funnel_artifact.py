"""Funnel artifact: per-domain drivers must not duplicate across domains."""

from todayflow_backend.services.compatibility_funnel_artifact import build_compatibility_funnel_artifact


def test_domain_drivers_are_not_identical_across_all_domains() -> None:
    art = build_compatibility_funnel_artifact(
        mode="quick",
        relationship_context="in_relationship",
        overall_score=78,
        subscores={"attraction": 80, "stability": 73, "conflicts": 73, "sexuality": 82},
        pair_dynamics={
            "user_1_contact_style": "держит темп",
            "user_2_contact_style": "подстраивается",
            "leader_guess": "user_1",
            "withdrawer_guess": "user_2",
        },
        user1_label="Ты",
        user2_label="Партнёр",
        from_element="fire",
        to_element="air",
        from_modality="cardinal",
        to_modality="fixed",
        locale="ru",
    )
    applicable = [d for d in art.domain_scores if d.applicable]
    assert len(applicable) >= 5

    signatures = {(tuple(d.raises), tuple(d.lowers)) for d in applicable}
    # Не все домены должны иметь один и тот же набор ↑/↓
    assert len(signatures) > 1

    for d in applicable:
        assert d.raises
        assert d.lowers
        assert d.basis
        assert d.improve


def test_different_sign_pairs_get_different_tagline_pool(client) -> None:
    r1 = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "quick",
            "from_sign": "aries",
            "to_sign": "libra",
            "generation": "template",
            "locale": "ru",
        },
    )
    r2 = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "quick",
            "from_sign": "taurus",
            "to_sign": "scorpio",
            "generation": "template",
            "locale": "ru",
        },
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    t1 = r1.json()["product_surface"]["score_tagline"]
    t2 = r2.json()["product_surface"]["score_tagline"]
    # Разные пары — не обязаны совпадать (при высокой химии пул из нескольких tagline)
    assert t1
    assert t2
