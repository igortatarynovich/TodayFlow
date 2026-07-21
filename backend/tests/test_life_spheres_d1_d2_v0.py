"""D1/D2 regressions for life_spheres projector v0.2."""

from __future__ import annotations

import json
from pathlib import Path

from todayflow_backend.services.life_spheres_projector_v0 import (
    PROJECTION_VERSION,
    project_life_spheres_v0,
)
from todayflow_backend.services.life_spheres_style_buckets_v0 import classify_style_scored
from todayflow_backend.services.life_spheres_traits_v0 import (
    normalize_sign,
    resolve_sphere_trait,
    trait_supported,
)

CASES = Path(__file__).resolve().parents[1] / "evals/profile_quality/life_spheres_quality_cases_v0.json"


def _case(cid: str) -> dict:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    for c in payload["cases"]:
        if c["id"] == cid:
            return c
    raise KeyError(cid)


def test_projection_version_is_v0_2() -> None:
    assert PROJECTION_VERSION == "life_spheres_projector_v0.2"


def test_lsq01_relationship_bucket_is_care_not_pace() -> None:
    style = _case("lsq-01")["foundations"]["styles"]["relationship_style"]
    scored = classify_style_scored(style, domain="love")
    assert scored["primary"] == "care"
    assert scored["scores"].get("care", 0) > scored["scores"].get("pace", 0)


def test_lsq08_decision_style_is_speed_not_analysis() -> None:
    style = _case("lsq-08")["foundations"]["styles"]["decision_style"]
    scored = classify_style_scored(style, domain="decisions")
    assert scored["primary"] == "speed"
    assert scored["scores"].get("speed", 0) > scored["scores"].get("analysis", 0)
    # conflict cues must debit analysis
    assert any(h["bucket"] == "analysis" and h["weight"] < 0 for h in scored["hits"])


def test_speed_vs_analysis_cue_contract() -> None:
    scored = classify_style_scored(
        "Решения сразу: скорость важнее долгого анализа.",
        domain="decisions",
    )
    assert scored["primary"] == "speed"


def test_planet_sign_traits_not_boilerplate() -> None:
    natal = {"venus_sign": "Cancer", "sun_sign": "Leo", "jupiter_sign": "Cancer", "saturn_sign": "Capricorn"}
    for sid in ("love", "money", "decisions"):
        trait = resolve_sphere_trait(sid, natal, locale="ru")
        assert trait is not None, sid
        assert "задаёт тон" not in trait["text"].lower()
        assert trait["trait_rule_id"].startswith(f"trait:{sid}.")
        assert trait["planet"]
        assert trait["sign"]


def test_all_supported_signs_emit_traits_for_anchor_planets() -> None:
    for sign in (
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    ):
        assert trait_supported("love", "venus", sign)
        assert trait_supported("money", "jupiter", sign)
        assert trait_supported("decisions", "saturn", sign)


def test_unsupported_trait_omits_sphere(monkeypatch) -> None:
    from todayflow_backend.services import life_spheres_projector_v0 as mod

    monkeypatch.setattr(mod, "resolve_sphere_trait", lambda *a, **k: None)
    f = _case("lsq-01")["foundations"]
    spheres, meta = project_life_spheres_v0(f)
    assert "love" not in spheres
    reasons = {o["id"]: o["reason"] for o in meta["spheres_omitted"]}
    assert reasons.get("love") == "trait_unsupported"


def test_evidence_contains_trait_and_bucket_scores() -> None:
    f = _case("lsq-01")["foundations"]
    spheres, meta = project_life_spheres_v0(f)
    assert "love" in spheres
    love = meta["per_sphere"]["love"]
    assert love["trait"]["trait_rule_id"] == "trait:love.venus.cancer"
    assert love["style_class"] == "care"
    assert "scores" in love["style_bucket"]
    evidence = love["evidence"]
    assert any(str(e).startswith("trait:love.venus.cancer") for e in evidence)
    assert "bucket:care" in evidence
    assert "задаёт тон" not in spheres["love"]["how"].lower()
    assert "эмоциональная безопасность" in spheres["love"]["how"].lower()


def test_fingerprint_changes_with_projection_version(monkeypatch) -> None:
    from todayflow_backend.services import life_spheres_projector_v0 as mod

    f = _case("lsq-02")["foundations"]
    _, meta_a = project_life_spheres_v0(f)
    fp_a = meta_a["fingerprint"]
    monkeypatch.setattr(mod, "PROJECTION_VERSION", "life_spheres_projector_v0.2-testbump")
    _, meta_b = project_life_spheres_v0(f)
    assert meta_b["fingerprint"] != fp_a


def test_sign_normalization() -> None:
    assert normalize_sign("Leo") == "leo"
    assert normalize_sign("рак") == "cancer"
    assert normalize_sign("Aquarius") == "aquarius"


def test_quality_cases_comparisons_still_diverge() -> None:
    a = project_life_spheres_v0(_case("lsq-01")["foundations"])[0]
    b = project_life_spheres_v0(_case("lsq-02")["foundations"])[0]
    assert a["love"]["how"] != b["love"]["how"]
    assert a["love"]["need"] != b["love"]["need"]
    c = project_life_spheres_v0(_case("lsq-03")["foundations"])[0]
    d = project_life_spheres_v0(_case("lsq-04")["foundations"])[0]
    assert c["love"]["need"] != d["love"]["need"]
    assert c["money"]["helps"] != d["money"]["helps"]
