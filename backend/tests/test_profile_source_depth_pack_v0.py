"""source_depth helpers for portrait packs / generation gates."""

from __future__ import annotations

from todayflow_backend.services.profile_content_v1.source_depth import (
    depth_from_profile_pack,
    patterns_generation_allowed,
)


def test_depth_birth_only_from_pack():
    depth = depth_from_profile_pack(
        {
            "person": {"first_name": "Аня"},
            "astro": {"sun_sign": "aries"},
            "numerology": {"life_path": 1},
            "living": None,
        }
    )
    assert depth == "birth_data_only"
    assert patterns_generation_allowed({"astro": {"sun_sign": "aries"}, "living": None}) is False


def test_depth_checkins_allows_patterns():
    pack = {
        "astro": {"sun_sign": "taurus"},
        "living": {
            "summary": "перегруз",
            "signals": [{}, {}, {}],
            "signal_profile": {"signals_days": 8},
        },
    }
    assert depth_from_profile_pack(pack) == "profile_plus_checkins"
    assert patterns_generation_allowed(pack) is True


def test_onboarding_alone_disallows_confirmed_patterns():
    pack = {
        "astro": {"sun_sign": "cancer"},
        "living": {"onboarding": {"intent_theme": "career"}},
    }
    assert depth_from_profile_pack(pack) == "onboarding_answers"
    assert patterns_generation_allowed(pack) is False
