"""IL-4 deterministic theme selection tests."""

from __future__ import annotations

from todayflow_backend.profile_engine.models import ProfileTopicDomain
from todayflow_backend.services.il4_selection_v1 import (
    ASTRO_OBJECT_TOPIC_MAP,
    SIGN_TOPIC_MAP,
    _line_matches_topic,
    _topics_for_line,
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


def test_all_planets_map_to_at_least_one_topic():
    """Every standard planet object id must be connected to at least one topic domain."""
    for planet in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"):
        line = _line(1, "natal", "test", {"what": f"astro.object.{planet}"})
        topics = _topics_for_line(line)
        assert topics, f"astro.object.{planet} has no topic mapping"


def test_all_houses_map_to_at_least_one_topic():
    """Every house object id must be connected to at least one topic domain."""
    for n in range(1, 13):
        line = _line(1, "natal", "test", {"where": f"astro.house.{n:02d}"})
        topics = _topics_for_line(line)
        assert topics, f"astro.house.{n:02d} has no topic mapping"


def test_all_signs_map_to_at_least_one_topic():
    """Every sign object id must be connected to at least one topic domain."""
    for sign in (
        "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
        "sagittarius", "capricorn", "aquarius", "pisces",
    ):
        line = _line(1, "natal", "test", {"what": f"astro.sign.{sign}"})
        topics = _topics_for_line(line)
        assert topics, f"astro.sign.{sign} has no topic mapping"


def test_angles_map_to_at_least_one_topic():
    """Major angles must be connected to at least one topic domain."""
    for angle in ("asc", "mc", "dsc", "ic"):
        line = _line(1, "natal", "test", {"what": f"astro.object.{angle}"})
        topics = _topics_for_line(line)
        assert topics, f"astro.object.{angle} has no topic mapping"


def test_topic_filters_cover_all_non_general_domains():
    """A full pack of planets in houses has at least one line for every non-GENERAL topic."""
    lines = [
        _line(
            i + 1,
            "natal",
            f"{planet.title()} in {n}th house",
            {"what": f"astro.object.{planet}", "where": f"astro.house.{n:02d}"},
        )
        for i, (planet, n) in enumerate(
            [
                ("sun", 10),
                ("moon", 4),
                ("mercury", 3),
                ("venus", 7),
                ("mars", 1),
                ("jupiter", 2),
                ("saturn", 6),
                ("uranus", 9),
                ("neptune", 12),
                ("pluto", 8),
            ]
        )
    ]
    pack = _pack(lines)
    for topic in ProfileTopicDomain:
        if topic == ProfileTopicDomain.GENERAL:
            continue
        out = select_themes(pack, surface="profile", topic=topic)
        assert out is not None and len(out["lines"]) > 0, f"topic {topic.value} has no matching lines"


def test_line_topic_union_from_multiple_objects():
    """A line with multiple relevant object ids contributes topics from all of them."""
    line = _line(
        1,
        "natal",
        "Venus in 7th house",
        {"what": "astro.object.venus", "where": "astro.house.07"},
    )
    topics = _topics_for_line(line)
    assert ProfileTopicDomain.RELATIONSHIPS in topics
    assert ProfileTopicDomain.INTIMACY in topics
    assert ProfileTopicDomain.MONEY in topics


def test_text_fallback_for_topic_keywords():
    """Text-only lines still match topics via explicit keyword hints."""
    line = _line(1, "natal", "financial decision about family money")
    topics = _topics_for_line(line)
    assert ProfileTopicDomain.MONEY in topics
    assert ProfileTopicDomain.FAMILY in topics
    assert ProfileTopicDomain.DECISION in topics
