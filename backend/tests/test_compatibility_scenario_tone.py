"""Scenario tone registry and LLM voice directives."""

from todayflow_backend.services.compatibility_scenario_tone import (
    resolve_scenario_format,
    scenario_context_for_llm,
)


def test_resolve_playful_scenario_after_wine() -> None:
    spec = resolve_scenario_format(series_id="after_wine")
    assert spec.format_id == "after_wine"
    assert spec.tone_mode == "playful"
    ctx = scenario_context_for_llm(spec, locale="ru")
    assert ctx["format_id"] == "after_wine"
    assert "весёлый" in ctx["voice_directive"].lower() or "игр" in ctx["voice_directive"].lower()


def test_resolve_serious_apocalypse() -> None:
    spec = resolve_scenario_format(series_id="apocalypse")
    assert spec.tone_mode == "serious"
    assert spec.tone_family == "dramatic"


def test_encyclopedia_selection_includes_tone(client) -> None:
    from todayflow_backend.services.compatibility_encyclopedia import resolve_encyclopedia_selection

    sel = resolve_encyclopedia_selection(
        topic_id=None,
        reading_id=None,
        series_id="home_renovation",
        locale="ru",
    )
    assert sel is not None
    assert sel["format_id"] == "home_renovation"
    assert sel["tone_mode"] == "playful"
    assert sel["scenario_context"]["voice_directive"]


def test_compatibility_dynamics_playful_series_metadata(client) -> None:
    response = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "quick",
            "from_sign": "aries",
            "to_sign": "libra",
            "generation": "template",
            "series_id": "after_wine",
            "locale": "ru",
        },
    )
    assert response.status_code == 200
    data = response.json()
    sel = (data.get("pair_dynamics") or {}).get("encyclopedia_selection") or {}
    assert sel.get("format_id") == "after_wine"
    assert sel.get("tone_mode") == "playful"
    tagline = data["product_surface"]["score_tagline"]
    assert not tagline.lower().startswith("с лёгкой иронией:")
    assert len(tagline) <= 200
    overview = data["product_surface"]["overview_paragraphs"]
    assert len(overview) <= 1
    assert data.get("funnel_artifact") is None
