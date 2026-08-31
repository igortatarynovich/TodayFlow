"""Tests for Content Library deterministic selector + catalog adapter.

Canon: docs/practices/CONTENT_LIBRARY_SELECTION_V1.md
"""

from __future__ import annotations

import pytest

from todayflow_backend.services.content_library_selection_v1 import (
    NeedQuery,
    all_content_library_practices,
    get_content_library_practice_by_id,
    select_content_item,
    select_content_library_practices,
)


class TestCatalogAdapter:
    def test_all_active_accepted_items_are_mapped(self) -> None:
        practices = all_content_library_practices(locale="ru")
        assert len(practices) >= 111
        for p in practices:
            assert p["id"]
            assert p["title"]
            assert p["description"]
            assert p["category"]
            assert p["difficulty"] in ("beginner", "intermediate", "advanced")
            assert p["is_free"] is True
            assert p["access_level"] == "free"
            assert p["is_personalized"] is False
            assert p["need_ids"]
            assert p["format_id"]
            assert p["instructions"]

    def test_no_technique_id_leaks_to_practice_dict(self) -> None:
        practices = all_content_library_practices(locale="ru")
        for p in practices:
            assert "technique_id" not in p

    def test_get_by_id_existing(self) -> None:
        p = get_content_library_practice_by_id("meditation.body_scan.001", locale="ru")
        assert p is not None
        assert p["id"] == "meditation.body_scan.001"
        assert p["title"]

    def test_multiline_body_splits_intro_from_steps(self) -> None:
        p = get_content_library_practice_by_id("meditation.acceptance.002", locale="ru")
        assert p is not None
        assert "\n" not in p["description"]
        assert "не улучшая" in p["description"]
        assert len(p["instructions"]) >= 3
        assert p["description"] not in p["instructions"]
        assert any("закрой глаза" in step.lower() for step in p["instructions"])

    def test_get_by_id_missing(self) -> None:
        assert get_content_library_practice_by_id("no.such.item.001", locale="ru") is None

    def test_filter_by_need(self) -> None:
        calm = select_content_library_practices(need="calm", locale="ru")
        assert calm
        for p in calm:
            assert "calm" in [x.lower() for x in p["need_ids"]]

    def test_filter_by_format(self) -> None:
        breath = select_content_library_practices(format_id="breath", locale="ru")
        assert breath
        for p in breath:
            assert p["format_id"] == "breath"

    def test_limit(self) -> None:
        all_items = select_content_library_practices(locale="ru")
        limited = select_content_library_practices(locale="ru", limit=10)
        assert len(limited) == 10
        assert len(limited) <= len(all_items)


class TestDeterministicSelector:
    def test_selector_returns_matched_selection(self) -> None:
        q = NeedQuery(purpose="sleep", direction="prepare", input_state=["restless"], locale="ru")
        s = select_content_item(q)
        assert s.matched is True
        assert s.item_id == "meditation.sleep.001"
        assert s.content_class == "meditation"
        assert s.item_type == "sleep"
        assert s.title
        assert s.body
        assert s.reason
        assert s.matched

    def test_selector_returns_no_match_for_unknown_need(self) -> None:
        q = NeedQuery(purpose="definitely-not-a-purpose", direction="prepare", locale="ru")
        s = select_content_item(q)
        assert s.matched is False
        assert s.item_id is None

    def test_hard_filter_content_class(self) -> None:
        q = NeedQuery(purpose="self_control", direction="stabilize", content_class="discipline", locale="ru")
        s = select_content_item(q)
        assert s.matched is True
        assert s.content_class == "discipline"

    def test_hard_filter_item_type(self) -> None:
        q = NeedQuery(purpose="calm", direction="downregulate", item_type="extended_exhale", locale="ru")
        s = select_content_item(q)
        assert s.matched is True
        assert s.item_type == "extended_exhale"

    def test_deterministic_same_query_same_item(self) -> None:
        q = NeedQuery(purpose="focus", direction="focus", input_state=["scattered"], locale="ru")
        a = select_content_item(q)
        b = select_content_item(q)
        assert a.matched and b.matched
        assert a.item_id == b.item_id

    def test_technique_id_is_internal_only(self) -> None:
        q = NeedQuery(purpose="sleep", direction="prepare", locale="ru")
        s = select_content_item(q)
        assert s.technique_id
