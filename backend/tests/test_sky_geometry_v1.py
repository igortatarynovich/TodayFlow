"""Shared-sky geometry: majors, daily influence, one headline driver."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_pack_v1 import build_day_events_pack_v1
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1
from todayflow_backend.services.sky_geometry_v1 import (
    pick_headline_sky,
    positions_to_sky_bodies,
    sky_aspects_from_bodies,
)


# Swiss noon UTC 2026-08-15 (live astro chart).
_AUG15 = [
    {"body": "sun", "sign": "Leo", "degree": 22.69, "longitude": 142.69032775836814},
    {"body": "moon", "sign": "Virgo", "degree": 28.7, "longitude": 178.6954523327736},
    {"body": "mercury", "sign": "Leo", "degree": 10.2, "longitude": 130.1998501762578},
    {"body": "venus", "sign": "Libra", "degree": 8.57, "longitude": 188.56509491499142},
    {"body": "mars", "sign": "Cancer", "degree": 2.74, "longitude": 92.73654865893151},
    {"body": "jupiter", "sign": "Leo", "degree": 10.16, "longitude": 130.1565710549407},
    {"body": "saturn", "sign": "Aries", "degree": 14.42, "longitude": 14.423303515607525},
    {"body": "uranus", "sign": "Gemini", "degree": 5.41, "longitude": 65.405853957656},
    {"body": "neptune", "sign": "Aries", "degree": 4.03, "longitude": 4.027670814898489},
    {"body": "pluto", "sign": "Aquarius", "degree": 3.85, "longitude": 303.8452896381068},
]


def test_aug15_headline_is_mercury_jupiter_conjunction():
    bodies = positions_to_sky_bodies(_AUG15)
    assert len(bodies) == 10
    moon = next(b for b in bodies if b["body"] == "moon")
    assert moon["sign"] == "Virgo"
    aspects = sky_aspects_from_bodies(bodies)
    headline = pick_headline_sky(aspects)
    assert headline is not None
    pair = {headline["planet_a"], headline["planet_b"]}
    assert pair == {"Mercury", "Jupiter"}
    assert headline["aspect"] == "conjunction"
    assert float(headline["orb_delta"]) < 0.1
    assert "work" in (headline["domain_weights"] or {})
    assert headline["thesis_hint"] == "communication/restart_messages"


def test_exact_sky_conjunction_outranks_distant_phase():
    bodies = positions_to_sky_bodies(_AUG15)
    aspects = sky_aspects_from_bodies(bodies)
    ce = {
        "lunar_phase": {
            "id": "waxing",
            "name": "Растущая",
            "guidance": "набирай темп",
            "next_phase": {"name": "Полнолуние", "date": "2026-08-28", "in_days": 13},
        },
        "moon_sign": {"sign": "Virgo", "sign_ru": "Дева"},
        "sky_aspects": aspects,
        "timed_lunar_aspects": [],
        "ingresses": [],
        "retrogrades": [],
        "personal_transits": [],
    }
    pack = build_day_events_pack_v1(ce, target_date=date(2026, 8, 15))
    assert pack["ranked_drivers"]
    top_id = pack["ranked_drivers"][0]
    assert "mercury" in top_id and "jupiter" in top_id
    thesis = build_day_thesis_v1(day_events_pack=pack)
    assert thesis["family"] == "communication"
    assert thesis["variant"] == "restart_messages"
