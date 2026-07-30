"""Wave 2 Phase C — glance timeline unit tests (no live ephemeris)."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from todayflow_backend.services import today_glance_timeline_v1 as glance


def test_label_short_no_aspect_jargon():
    hard = glance.label_short_for("Mars", "square")
    soft = glance.label_short_for("Venus", "trine")
    assert "°" not in hard
    assert "квадрат" not in hard.lower()
    assert "Марс" not in hard
    assert "Венера" not in soft
    assert len(soft.split()) <= 4


def test_valence_soft_hard():
    assert glance.glance_valence("trine", "Venus") == "favorable"
    assert glance.glance_valence("square", "Mars") == "caution"


def test_build_glance_only_timed_rank_1_to_3():
    rows = glance.build_glance_timeline_rows(
        [
            {
                "id": "a1",
                "rank": 1,
                "transiting_planet": "Mars",
                "aspect": "square",
                "natal_point": "Sun",
                "exact_time_local": "2026-08-01T14:30+03:00",
            },
            {
                "id": "a2",
                "rank": 2,
                "transiting_planet": "Venus",
                "aspect": "trine",
                "natal_point": "Moon",
                "exact_time_local": None,
            },
            {
                "id": "a4",
                "rank": 4,
                "transiting_planet": "Moon",
                "aspect": "conjunction",
                "natal_point": "ASC",
                "exact_time_local": "2026-08-01T09:00+03:00",
            },
            {
                "id": "a3",
                "rank": 3,
                "transiting_planet": "Moon",
                "aspect": "trine",
                "natal_point": "Venus",
                "exact_time_local": "2026-08-01T08:15+03:00",
            },
        ]
    )
    assert len(rows) == 2
    assert rows[0]["driver_id"] == "a3"
    assert rows[0]["valence"] == "favorable"
    assert rows[1]["driver_id"] == "a1"
    assert rows[1]["valence"] == "caution"


def test_local_day_bounds_timezone():
    start, end = glance.local_day_bounds(date(2026, 8, 1), "Europe/Moscow")
    assert start.tzinfo is not None
    assert (end - start).total_seconds() == 86400


def test_natal_longitude_from_chart():
    class Chart:
        positions = [
            {"body": "Sun", "longitude": 310.5},
            {"body": "Ascendant", "longitude": 12.0},
        ]

    assert glance.natal_longitude_from_chart(Chart(), "Sun") == 310.5
    assert glance.natal_longitude_from_chart(Chart(), "ASC") == 12.0
    assert glance.natal_longitude_from_chart(Chart(), "Moon") is None


def test_primary_residual_zero_at_exact_trine():
    # transit 30°, natal 150° → 120° trine
    r = glance.primary_residual(30.0, 150.0, 120.0)
    assert abs(r) < 1e-9
