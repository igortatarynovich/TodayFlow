"""Tests for state-cycle practice catalog enrichment."""

from todayflow_backend.data.practice_state_cycle_catalog_v1 import (
    NEW_STATE_CYCLE_PRACTICES,
    STATE_CYCLE_FORMAT_IDS,
    STATE_CYCLE_META,
    STATE_CYCLE_NEED_IDS,
    apply_state_cycle_catalog,
    catalog_coverage,
    rank_practices_for_need,
)


REQUIRED_GENERAL_IDS = {
    "breathing-4-7-8",
    "body-scan",
    "gratitude-list",
    "box-breathing",
    "morning-intention",
    "loving-kindness-meditation",
    "alternate-nostril-breathing",
    "walking-meditation",
    "kapalabhati-breathing",
    "mindful-eating",
    "deep-breathing-relaxation",
}

EXPECTED_CORE_NEW_IDS = {
    "tension-release-3",
    "soft-stretch-reset",
    "gentle-yoga-flow",
    "volume-imagination",
    "clarity-three-questions",
    "self-ground-affirmation",
    "evening-release",
    "bedtime-stretch",
    "sleep-sound-bed",
    "calm-ambient-backdrop",
    "energy-reset-breath",
    "focus-return-4",
    "volumetric-digits",
    "worry-park-list",
    "nature-sound-restore",
}


def test_state_cycle_meta_covers_general_ids():
    assert REQUIRED_GENERAL_IDS <= set(STATE_CYCLE_META.keys())
    meta = STATE_CYCLE_META["breathing-4-7-8"]
    assert "calm" in meta["need_ids"]
    assert meta["format_id"] == "breath"
    assert meta["outcome_label"] == "Снизить тревожность"


def test_new_practices_rich_coverage():
    assert len(NEW_STATE_CYCLE_PRACTICES) >= 30
    ids = {p["id"] for p in NEW_STATE_CYCLE_PRACTICES}
    assert EXPECTED_CORE_NEW_IDS <= ids
    assert len(ids) == len(NEW_STATE_CYCLE_PRACTICES)  # unique ids

    formats = {p["format_id"] for p in NEW_STATE_CYCLE_PRACTICES}
    for fmt in STATE_CYCLE_FORMAT_IDS:
        assert fmt in formats

    needs = set()
    for p in NEW_STATE_CYCLE_PRACTICES:
        assert p["is_free"] is True
        assert p["access_level"] == "free"
        assert p["need_ids"]
        assert p["outcome_label"]
        assert p["instructions"]
        assert p["duration_minutes"] >= 3
        needs.update(p["need_ids"])
    for need in STATE_CYCLE_NEED_IDS:
        assert need in needs

    # Mockup-aligned titles present
    titles = {p["title"] for p in NEW_STATE_CYCLE_PRACTICES}
    for title in (
        "Объёмное воображение",
        "Снять напряжение",
        "Мягкая растяжка",
        "Вечернее отпускание",
        "Музыка для сна",
        "Объёмные цифры",
    ):
        assert title in titles


def test_apply_and_coverage_thresholds():
    seed = [
        {
            "id": "breathing-4-7-8",
            "title": "Дыхание 4-7-8",
            "description": "x",
            "category": "breathing",
            "duration_minutes": 5,
            "difficulty": "beginner",
            "is_free": True,
            "is_personalized": False,
            "access_level": "free",
            "tags": ["успокоение"],
            "instructions": ["a"],
        }
    ]
    out = apply_state_cycle_catalog(seed)
    by_id = {p["id"]: p for p in out}
    assert by_id["breathing-4-7-8"]["need_ids"] == ["calm", "sleep"]
    for nid in EXPECTED_CORE_NEW_IDS:
        assert nid in by_id

    cov = catalog_coverage(out)
    assert cov["total"] >= 31
    assert cov["tagged"] >= 31
    for need in STATE_CYCLE_NEED_IDS:
        assert cov["need_counts"][need] >= 4, need
    for fmt in STATE_CYCLE_FORMAT_IDS:
        assert cov["format_counts"][fmt] >= 2, fmt

    ranked = rank_practices_for_need(out, "sleep")
    assert ranked
    assert ranked[0]["need_ids"][0] == "sleep" or "sleep" in ranked[0]["need_ids"]
    # primary-first: first items should list sleep as first need when available
    primaries = [p for p in ranked if p["need_ids"][0] == "sleep"]
    assert primaries
    assert ranked[0]["id"] == primaries[0]["id"]

    again = apply_state_cycle_catalog(out)
    assert len(again) == len(out)
