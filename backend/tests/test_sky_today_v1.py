"""sky_today_v1 — Moon in sign + headline pair for Today strip."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.sky_geometry_v1 import (
    pick_headline_sky,
    positions_to_sky_bodies,
    sky_aspects_from_bodies,
)
from todayflow_backend.services.sky_today_v1 import build_sky_today_v1
from todayflow_backend.services.today_contract_nests_b1_v1 import attach_b1_nests_to_contract

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


def test_sky_today_moon_plus_headline_in_sign():
    bodies = positions_to_sky_bodies(_AUG15)
    aspects = sky_aspects_from_bodies(bodies)
    nest = build_sky_today_v1(
        celestial_events={
            "sky_positions": bodies,
            "sky_aspects": aspects,
            "headline_sky": pick_headline_sky(aspects),
        }
    )
    assert nest is not None
    assert nest["moon"]["body"] == "moon"
    assert nest["moon"]["sign_ru"] == "Дева"
    assert nest["headline"]["planet_a"] == "mercury"
    assert nest["headline"]["planet_b"] == "jupiter"
    assert nest["headline"]["aspect"] == "conjunction"
    assert "Луна" not in (nest["headline"]["title_ru"] or "")
    assert "Меркурий во Льве" in nest["headline"]["title_ru"]
    assert "Юпитер во Льве" in nest["headline"]["title_ru"]
    assert len(nest["positions"]) == 10
    assert nest["aspects"]


def test_sky_today_foundation_moon_only_when_sky_empty():
    nest = build_sky_today_v1(
        day_foundation={"lunar": {"moon_sign": {"sign": "Virgo", "sign_ru": "Дева"}}}
    )
    assert nest is not None
    assert nest["moon"]["sign_ru"] == "Дева"
    assert nest["headline"] is None
    assert nest["positions"] == []


def test_sky_today_omits_when_empty():
    assert build_sky_today_v1() is None
    assert build_sky_today_v1(celestial_events={}) is None


def test_attach_nests_includes_sky_today_from_morning():
    bodies = positions_to_sky_bodies(_AUG15)
    aspects = sky_aspects_from_bodies(bodies)
    morning = {
        "celestial_events": {
            "sky_positions": bodies,
            "sky_aspects": aspects,
            "headline_sky": pick_headline_sky(aspects),
        }
    }
    out = attach_b1_nests_to_contract(
        {
            "day_atmosphere": {"visual_mode": "clarity"},
            "day_story": {"do": ["Шаг"]},
        },
        morning=morning,
        target_date=date(2026, 8, 15),
    )
    assert out["sky_today"]["moon"]["sign"] == "Virgo"
    assert out["sky_today"]["headline"]["aspect"] == "conjunction"
