"""profile_slice_for_today — continuity pack from saved personality."""

from todayflow_backend.services.profile_slice_for_today_v0 import build_profile_slice_for_today


def test_slice_reads_personality_and_natal_mode():
    core = {
        "astro": {"sun_sign": "Телец", "sun_element": "earth"},
        "numerology": {"life_path": 7},
        "capability": {"mode": "date_only"},
        "profile_contract_v1": {
            "personality_v1": {
                "identity_summary": "Держит ясность через ритм.",
                "emotional_style": "Чувствует глубже.",
                "decision_style": "Сначала тело.",
                "strengths": ["Выдержка"],
            },
            "recognition_line": "legacy",
        },
    }
    slice_out = build_profile_slice_for_today(core)
    assert slice_out["identity_summary"].startswith("Держит")
    assert slice_out["emotional_style"]
    assert slice_out["natal_mode"] == "date_only"
    assert slice_out["life_path"] == 7
    assert slice_out["strengths"] == ["Выдержка"]


def test_slice_empty_without_profile():
    assert build_profile_slice_for_today(None) == {}
    assert build_profile_slice_for_today({}) == {"source": "profile_slice_for_today_v0"}
