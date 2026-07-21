"""Deterministic life_spheres projector v0.1 — unit tests."""

from __future__ import annotations

from todayflow_backend.services.life_spheres_projector_v0 import (
    PROJECTION_VERSION,
    build_sphere_foundations_v0,
    project_life_spheres_v0,
    spheres_projection_allowed,
)

assert PROJECTION_VERSION.startswith("life_spheres_projector_v0.2")


def _foundations(**overrides):
    base = {
        "locale": "ru",
        "person": {"birth_date": "1990-05-12"},
        "identity": {
            "identity_core": "Человек держит смысл через ясный фокус и живой контакт с миром.",
            "strengths": ["Фокус", "Контакт", "Доведение"],
            "growth_zones": ["Распыление", "Контроль", "Откладывание"],
        },
        "styles": {
            "relationship_style": "Близость через прямые слова и предсказуемость без давления.",
            "money_style": "Деньги как ценность и спокойный шаг без импульса и стыда.",
            "decision_style": "Решения через один критерий и короткий честный дедлайн.",
        },
        "natal": {
            "sun_sign": "Taurus",
            "venus_sign": "Cancer",
            "jupiter_sign": "Virgo",
            "saturn_sign": "Capricorn",
            "mercury_sign": "Gemini",
            "houses_available": False,
            "houses": {},
        },
    }
    base.update(overrides)
    return base


def test_spheres_gate_independent_of_patterns() -> None:
    f = _foundations()
    assert spheres_projection_allowed(f) is True
    # Gate does not read living/patterns — only foundations.
    assert spheres_projection_allowed({**f, "living": None}) is True


def test_spheres_gate_requires_sun_and_identity() -> None:
    f = _foundations()
    bad = dict(f)
    bad["natal"] = {**f["natal"], "sun_sign": ""}
    bad["person"] = {}
    assert spheres_projection_allowed(bad) is False
    bad2 = dict(f)
    bad2["identity"] = {"identity_core": "short"}
    assert spheres_projection_allowed(bad2) is False


def test_projector_love_money_decisions_sign_only() -> None:
    f = _foundations()
    spheres, meta = project_life_spheres_v0(f)
    assert set(spheres.keys()) == {"love", "money", "decisions"}
    assert meta["projection_version"] == PROJECTION_VERSION
    assert meta["fingerprint"] and meta["fingerprint"].startswith("sha256:")
    assert "sex" not in spheres
    for sid, row in spheres.items():
        for field in ("how", "need", "risk", "turns_on", "turns_off", "helps"):
            assert len(row[field]) >= 20, f"{sid}.{field}"
        assert "доме" not in row["how"].lower()
        assert "асцендент" not in row["how"].lower()
        assert "задаёт тон" not in row["how"].lower()
        trait = meta["per_sphere"][sid]["trait"]
        assert str(trait["trait_rule_id"]).startswith("trait:")
    # Stable fingerprint
    _, meta2 = project_life_spheres_v0(f)
    assert meta["fingerprint"] == meta2["fingerprint"]


def test_projector_with_houses_enriches_how() -> None:
    f = _foundations(
        natal={
            "sun_sign": "Taurus",
            "venus_sign": "Cancer",
            "jupiter_sign": "Virgo",
            "saturn_sign": "Capricorn",
            "mercury_sign": "Gemini",
            "houses_available": True,
            "houses": {
                "7": {"description": "Партнёрство через честный разговор и равный темп."},
                "2": {"description": "Ресурс растёт от регулярных малых шагов."},
                "9": {"description": "Выбор через смысл и проверенный критерий."},
            },
        }
    )
    spheres, meta = project_life_spheres_v0(f)
    assert "love" in spheres
    love_ev = meta["per_sphere"]["love"]["evidence"]
    assert "house:7" in love_ev
    assert "Партнёрство" in spheres["love"]["how"] or "партнёр" in spheres["love"]["how"].lower()


def test_identity_echo_omits_sphere() -> None:
    core = "Человек держит смысл через ясный фокус и живой контакт с миром."
    f = _foundations(identity={"identity_core": core, "strengths": [], "growth_zones": []})
    # Force how == identity by mangling natal so planet line empty and... actually
    # identity echo checks how vs identity; templates won't copy full identity.
    # Simulate by projecting then checking gate rejects when how equals identity:
    from todayflow_backend.services import life_spheres_projector_v0 as mod

    original = mod._build_sphere

    def echo_love(sid, *, foundations):
        if sid != "love":
            return original(sid, foundations=foundations)
        return (
            {
                "how": core,
                "need": "В любви нужна ясность и предсказуемый контакт — в духе «прямые слова».",
                "risk": "Точка слома — ожидание, что другой угадает без слов.",
                "turns_on": "Спокойный прямой разговор и совпадение по темпу близости.",
                "turns_off": "Намёки, двойные сигналы и давление без следующего шага.",
                "helps": "Одна короткая честная договорённость на неделю — не разбор всего.",
            },
            {"claim_depth": "sign_only", "evidence": [], "style_class": "clarity"},
        )

    # Monkeypatch via attribute
    mod._build_sphere = echo_love  # type: ignore[assignment]
    try:
        spheres, meta = project_life_spheres_v0(f)
    finally:
        mod._build_sphere = original  # type: ignore[assignment]
    assert "love" not in spheres
    reasons = {o["id"]: o["reason"] for o in meta["spheres_omitted"]}
    assert reasons.get("love") == "identity_echo"


def test_style_passthrough_rejected() -> None:
    from todayflow_backend.services import life_spheres_projector_v0 as mod

    f = _foundations()
    style = f["styles"]["relationship_style"]
    original = mod._build_sphere

    def passthrough(sid, *, foundations):
        if sid != "love":
            return original(sid, foundations=foundations)
        return (
            {
                "how": style,
                "need": "В любви нужна ясность и предсказуемый контакт — в духе «прямые слова».",
                "risk": "Точка слома — ожидание, что другой угадает без слов.",
                "turns_on": "Спокойный прямой разговор и совпадение по темпу близости.",
                "turns_off": "Намёки, двойные сигналы и давление без следующего шага.",
                "helps": "Одна короткая честная договорённость на неделю — не разбор всего.",
            },
            {"claim_depth": "sign_only", "evidence": [], "style_class": "clarity"},
        )

    mod._build_sphere = passthrough  # type: ignore[assignment]
    try:
        spheres, meta = project_life_spheres_v0(f)
    finally:
        mod._build_sphere = original  # type: ignore[assignment]
    assert "love" not in spheres
    reasons = {o["id"]: o["reason"] for o in meta["spheres_omitted"]}
    assert reasons.get("love") == "style_passthrough"


def test_partial_map_omits_other_six() -> None:
    spheres, meta = project_life_spheres_v0(_foundations())
    assert set(spheres) <= {"love", "money", "decisions"}
    omitted_ids = {o["id"] for o in meta["spheres_omitted"]}
    for sid in ("sex", "work", "family", "kids", "body", "friends"):
        assert sid in omitted_ids


def test_build_foundations_from_funnel_pack() -> None:
    shared = {
        "locale": "ru",
        "person": {"birth_date": "1990-05-12"},
        "astro": {"sun_sign": "Leo"},
        "numerology": {"life_path": 1},
        "baseline": {},
    }
    identity = {
        "identity_core": "Человек держит смысл через ясный фокус и живой контакт.",
        "strengths": ["a", "b", "c"],
        "growth_zones": ["d", "e", "f"],
    }
    styles = {
        "relationship_style": "Близость через прямые слова и предсказуемость.",
        "money_style": "Деньги как ценность и спокойный шаг без импульса.",
        "decision_style": "Решения через один критерий и короткий дедлайн.",
    }
    f = build_sphere_foundations_v0(shared=shared, identity=identity, styles=styles)
    assert spheres_projection_allowed(f)
    spheres, _ = project_life_spheres_v0(f)
    assert len(spheres) == 3
