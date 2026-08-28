"""IL-4 deterministic theme selection tests."""

from __future__ import annotations

from todayflow_backend.profile_engine.models import ProfileTopicDomain
from todayflow_backend.services.il4_selection_v1 import (
    _line_matches_topic,
    select_themes,
)


def _line(rank: int, band: str, text: str, jobs: dict | None = None) -> dict:
    return {
        "rank": rank,
        "band": band,
        "construction": "planet_in_house",
        "text": text,
        "jobs": jobs or {},
    }


def _pack(lines: list[dict]) -> dict:
    return {
        "surface": "profile",
        "tone": "direct_supportive",
        "meaning_source": "il3_themes",
        "lines": lines,
        "dropped": [{"construction": "transit_to_natal", "reason": "missing_atom"}],
    }


def test_select_themes_today_primary_only():
    pack = _pack(
        [
            _line(1, "transit", "first"),
            _line(2, "natal", "second"),
            _line(3, "natal", "third"),
        ]
    )
    out = select_themes(pack, surface="today")
    assert out is not None
    assert len(out["lines"]) == 1
    assert out["lines"][0]["text"] == "first"
    # Dropped refusals are preserved for validation; compact_meaning strips them.
    assert "dropped" in out


def test_select_themes_profile_natal_only_capped():
    pack = _pack(
        [_line(i, "natal" if i % 2 else "transit", f"line{i}") for i in range(1, 31)]
    )
    out = select_themes(pack, surface="profile", max_themes=10)
    assert out is not None
    assert len(out["lines"]) == 10
    assert all(line["band"] == "natal" for line in out["lines"])
    assert out["lines"][0]["rank"] == 1


def test_select_themes_profile_default_cap_24():
    pack = _pack([_line(i, "natal", f"line{i}") for i in range(1, 41)])
    out = select_themes(pack, surface="profile")
    assert out is not None
    assert len(out["lines"]) == 24


def test_select_themes_profile_topic_filter():
    pack = _pack(
        [
            _line(1, "natal", "Sun in 10th house", {"what": "astro.object.sun", "where": "astro.house.10"}),
            _line(2, "natal", "Venus in 7th house", {"what": "astro.object.venus", "where": "astro.house.07"}),
            _line(3, "natal", "Mercury in 3rd house", {"what": "astro.object.mercury", "where": "astro.house.03"}),
        ]
    )
    out = select_themes(pack, surface="profile", topic=ProfileTopicDomain.DECISION)
    assert out is not None
    assert len(out["lines"]) == 1
    assert "mercury" in out["lines"][0]["text"].lower()


def test_select_themes_profile_topic_filter_money():
    pack = _pack(
        [
            _line(1, "natal", "Moon in 4th house", {"what": "astro.object.moon", "where": "astro.house.04"}),
            _line(2, "natal", "Jupiter in 2nd house", {"what": "astro.object.jupiter", "where": "astro.house.02"}),
            _line(3, "natal", "Saturn in 10th house", {"what": "astro.object.saturn", "where": "astro.house.10"}),
        ]
    )
    out = select_themes(pack, surface="profile", topic=ProfileTopicDomain.MONEY)
    assert out is not None
    texts = {line["text"] for line in out["lines"]}
    assert "Jupiter in 2nd house" in texts
    assert "Saturn in 10th house" in texts
    assert "Moon in 4th house" not in texts


def test_select_themes_compatibility_keeps_transit():
    pack = _pack(
        [
            _line(1, "transit", "first transit"),
            _line(2, "natal", "second natal"),
        ]
    )
    out = select_themes(pack, surface="compatibility", max_themes=10)
    assert out is not None
    assert len(out["lines"]) == 2
    bands = {line["band"] for line in out["lines"]}
    assert bands == {"transit", "natal"}


def test_select_themes_preserves_dropped_for_validation():
    pack = _pack([_line(1, "natal", "Venus in 7th house")])
    out = select_themes(pack, surface="profile")
    assert out is not None
    assert "dropped" in out


def test_select_themes_no_pack():
    assert select_themes(None, surface="today") is None


def test_line_matches_topic_general():
    assert _line_matches_topic(_line(1, "natal", "anything"), ProfileTopicDomain.GENERAL) is True


def test_line_matches_topic_body_energy():
    line = _line(1, "natal", "Sun in 1st house", {"what": "astro.object.sun", "where": "astro.house.01"})
    assert _line_matches_topic(line, ProfileTopicDomain.BODY_ENERGY) is True
    assert _line_matches_topic(line, ProfileTopicDomain.INTIMACY) is False
