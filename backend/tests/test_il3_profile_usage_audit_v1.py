"""IL-3 Profile Decode usage audit harness tests."""

from __future__ import annotations

from todayflow_backend.profile_engine.models import ProfileTopicDomain
from todayflow_backend.services.il3_profile_usage_audit_v1 import (
    audit_report,
    evaluate_citation,
    make_synthetic_profile_pack,
)


def test_synthetic_profile_pack_has_24_natal_lines():
    pack = make_synthetic_profile_pack()
    assert pack["surface"] == "profile"
    assert pack["tone"] == "structural"
    assert pack["meaning_source"] == "il3_themes"
    assert len(pack["lines"]) == 24
    assert all(line["band"] == "natal" for line in pack["lines"])
    assert all(line["rank"] == i + 1 for i, line in enumerate(pack["lines"]))


def test_evaluate_citation_counts_cited_and_ignored():
    pack = make_synthetic_profile_pack()
    # Response mentions Sun (1st line) and Jupiter (6th line, planet-in-house).
    response = "The Sun in the 1st house gives a strong identity. Jupiter expands things."
    result = evaluate_citation(response, pack)

    assert result["total_lines"] == 24
    assert result["cited_count"] >= 2
    assert result["ignored_count"] == 24 - result["cited_count"]
    assert 0.0 < result["coverage_ratio"] <= 1.0

    cited_texts = {line["text"] for line in result["cited"]}
    assert "Sun in 10th house" in cited_texts or "Sun in 1th house" in cited_texts
    assert any("Jupiter" in text for text in cited_texts)


def test_evaluate_citation_ignores_unrelated_text():
    pack = make_synthetic_profile_pack()
    result = evaluate_citation("Random unrelated astrology text about black holes.", pack)
    assert result["cited_count"] == 0
    assert result["ignored_count"] == 24
    assert result["coverage_ratio"] == 0.0


def test_evaluate_citation_topic_coverage():
    pack = make_synthetic_profile_pack()
    # Response explicitly covers a work/career line (Saturn in 7th house) and
    # a relationship line (Venus in 4th house).
    response = "Saturn in the 7th house brings discipline. Venus in the 4th house deepens roots."
    result = evaluate_citation(response, pack)

    all_topics = set(ProfileTopicDomain) - {ProfileTopicDomain.GENERAL}
    for topic in all_topics:
        assert topic.value in result["cited_by_topic"]
        assert topic.value in result["ignored_by_topic"]
        assert topic.value in result["topic_coverage_ratio"]

    # Saturn maps to work/money/family/habits/discipline/decision; Venus to relationships/intimacy/money.
    assert result["cited_by_topic"][ProfileTopicDomain.WORK.value] >= 1
    assert result["cited_by_topic"][ProfileTopicDomain.RELATIONSHIPS.value] >= 1


def test_audit_report_structure():
    pack = make_synthetic_profile_pack()
    response = "Sun in the 1st house and Moon in the 2nd house."
    report = audit_report(response, pack, response_source="mock")

    assert report["response_source"] == "mock"
    assert report["pack_shape"]["surface"] == "profile"
    assert report["pack_shape"]["line_count"] == 24
    assert report["summary"]["cited"] >= 2
    assert report["summary"]["ignored"] == 24 - report["summary"]["cited"]
    assert isinstance(report["ignored_lines"], list)
    assert len(report["ignored_lines"]) == report["summary"]["ignored"]


def test_evaluate_citation_with_custom_pack():
    custom = make_synthetic_profile_pack(
        [
            {
                "rank": 1,
                "band": "natal",
                "role": "primary",
                "construction": "planet_in_house",
                "jobs": {"what": ["astro.object.mars"], "where": ["astro.house.01"]},
                "text": "Mars in 1st house",
            }
        ]
    )
    result = evaluate_citation("Mars in the first house is assertive.", custom)
    assert result["total_lines"] == 1
    assert result["cited_count"] == 1
    assert result["coverage_ratio"] == 1.0


def test_synthetic_pack_lines_connect_to_topics():
    """Every default line must map to at least one non-GENERAL topic."""
    pack = make_synthetic_profile_pack()
    for line in pack["lines"]:
        topics = evaluate_citation("", {"lines": [line]})["line_details"][0]["topics"]
        assert topics, f"line {line['text']} has no topic mapping"
        assert ProfileTopicDomain.GENERAL.value not in topics
