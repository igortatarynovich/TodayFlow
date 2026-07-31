"""Tests for state-cycle practice catalog enrichment."""

from todayflow_backend.data.practice_state_cycle_catalog_v1 import (
    NEW_STATE_CYCLE_PRACTICES,
    STATE_CYCLE_META,
    apply_state_cycle_catalog,
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

EXPECTED_NEW_IDS = {
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
}


def test_state_cycle_meta_covers_general_ids():
    assert REQUIRED_GENERAL_IDS <= set(STATE_CYCLE_META.keys())
    meta = STATE_CYCLE_META["breathing-4-7-8"]
    assert "calm" in meta["need_ids"]
    assert meta["format_id"] == "breath"
    assert meta["outcome_label"] == "Снизить тревожность"


def test_new_practices_cover_gap_formats_and_needs():
    assert len(NEW_STATE_CYCLE_PRACTICES) >= 10
    ids = {p["id"] for p in NEW_STATE_CYCLE_PRACTICES}
    assert EXPECTED_NEW_IDS <= ids

    formats = {p["format_id"] for p in NEW_STATE_CYCLE_PRACTICES}
    for fmt in ("stretch", "yoga", "visualization", "music", "sleep", "reflection", "affirmation", "breath", "meditation"):
        assert fmt in formats

    needs = set()
    for p in NEW_STATE_CYCLE_PRACTICES:
        assert p["is_free"] is True
        assert p["access_level"] == "free"
        assert p["difficulty"] == "beginner"
        assert p["need_ids"]
        assert p["outcome_label"]
        assert p["instructions"]
        needs.update(p["need_ids"])
    for need in ("calm", "focus", "recover", "body", "understand", "sleep"):
        assert need in needs


def test_apply_state_cycle_catalog_merges_meta_and_appends():
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
        },
        {
            "id": "custom-keep",
            "title": "Custom",
            "description": "y",
            "category": "meditation",
            "duration_minutes": 1,
            "difficulty": "beginner",
            "is_free": True,
            "is_personalized": False,
            "access_level": "free",
            "tags": [],
            "instructions": [],
        },
    ]
    out = apply_state_cycle_catalog(seed)
    by_id = {p["id"]: p for p in out}
    assert by_id["breathing-4-7-8"]["need_ids"] == ["calm", "sleep"]
    assert by_id["breathing-4-7-8"]["format_id"] == "breath"
    assert by_id["breathing-4-7-8"]["outcome_label"] == "Снизить тревожность"
    assert "custom-keep" in by_id
    assert "need_ids" not in by_id["custom-keep"] or by_id["custom-keep"].get("need_ids") in (None, [])
    for nid in EXPECTED_NEW_IDS:
        assert nid in by_id
    # idempotent append: applying again with already-enriched list should not duplicate
    again = apply_state_cycle_catalog(out)
    assert len(again) == len(out)
    assert seed[0].get("need_ids") is None  # deepcopy: seed unchanged
