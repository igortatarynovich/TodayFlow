"""Tests for deterministic content library selection (no LLM, no randomness)."""

from __future__ import annotations

import pytest

from todayflow_backend.services.content_library_selection_v1 import (
    NeedQuery,
    load_content_library,
    load_technique_canon,
    select_content_item,
)


@pytest.fixture
def library():
    return load_content_library()


@pytest.fixture
def technique_canon():
    return load_technique_canon()


class TestSelectContentItemRealData:
    """Selection against the canonical practice library."""

    def test_sleep_prepare_returns_meditation_sleep(self, library, technique_canon):
        query = NeedQuery(purpose="sleep", direction="prepare", input_state=["restless"])
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is True
        assert result.item_id == "meditation.sleep.001"
        assert result.content_class == "meditation"
        assert result.item_type == "sleep"
        assert result.technique_id == "technique.sleep"
        assert result.title == "Челюсть мягче"
        assert "отпусти челюсть" in result.body
        assert result.duration == 5
        assert result.duration_unit == "minutes"
        assert "purpose=sleep" in result.reason

    def test_calm_downregulate_work_context_returns_extended_exhale_001(self, library, technique_canon):
        query = NeedQuery(
            purpose="calm",
            direction="downregulate",
            input_state=["tense"],
            context=["work"],
        )
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is True
        assert result.item_id == "practice.extended_exhale.001"
        assert result.technique_id == "technique.extended_exhale"
        assert result.duration == 2

    def test_rest_downregulate_evening_context_returns_relaxation_003(self, library, technique_canon):
        query = NeedQuery(
            purpose="rest",
            direction="downregulate",
            input_state=["overstimulated"],
            context=["evening"],
        )
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is True
        assert result.item_id == "meditation.relaxation.003"

    def test_energy_activate_returns_mobility_001(self, library, technique_canon):
        query = NeedQuery(purpose="energy", direction="activate", input_state=["low_energy"])
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is True
        assert result.item_id == "practice.mobility.001"
        assert result.technique_id == "technique.mobility"

    def test_sleep_discipline_class_returns_discipline_item(self, library, technique_canon):
        query = NeedQuery(
            purpose="sleep",
            direction="prepare",
            input_state=["restless"],
            content_class="discipline",
            item_type="sleep_discipline",
        )
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is True
        assert result.item_id == "discipline.sleep_discipline.001"
        assert result.content_class == "discipline"
        assert result.technique_id == "technique.sleep_discipline"

    def test_no_match_returns_matched_false(self, library, technique_canon):
        query = NeedQuery(purpose="nonexistent", direction="unknown")
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is False
        assert result.item_id is None
        assert result.title == ""
        assert result.body == ""
        assert "nonexistent" in result.reason

    def test_english_locale(self, library, technique_canon):
        query = NeedQuery(
            purpose="sleep",
            direction="prepare",
            input_state=["restless"],
            locale="en",
        )
        result = select_content_item(query, library=library, technique_canon=technique_canon)
        assert result.matched is True
        assert result.title == "Softer jaw"
        assert "Close your eyes" in result.body

    def test_deterministic_repeat(self, library, technique_canon):
        query = NeedQuery(purpose="focus", direction="focus", input_state=["scattered"])
        r1 = select_content_item(query, library=library, technique_canon=technique_canon)
        r2 = select_content_item(query, library=library, technique_canon=technique_canon)
        assert r1.item_id == r2.item_id
        assert r1.reason == r2.reason


class TestSelectContentItemSynthetic:
    """Edge cases with small, controlled libraries."""

    def test_draft_items_not_selected(self):
        library = {
            "items": [
                {
                    "identity": {
                        "item_id": "draft.item",
                        "content_class": "practice",
                        "type": "draft",
                        "status": "draft",
                        "technique_id": "technique.accepted",
                    },
                    "retrieval": {
                        "purpose": ["calm"],
                        "direction": ["downregulate"],
                        "input_state": ["tense"],
                        "context": ["anytime"],
                        "duration": 2,
                        "duration_unit": "minutes",
                        "energy_effect": "down",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Draft", "body": "draft body"}},
                    },
                },
                {
                    "identity": {
                        "item_id": "active.item",
                        "content_class": "practice",
                        "type": "active",
                        "status": "active",
                        "technique_id": "technique.accepted",
                    },
                    "retrieval": {
                        "purpose": ["calm"],
                        "direction": ["downregulate"],
                        "input_state": ["tense"],
                        "context": ["anytime"],
                        "duration": 2,
                        "duration_unit": "minutes",
                        "energy_effect": "down",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Active", "body": "active body"}},
                    },
                },
            ]
        }
        techniques = {
            "techniques": [
                {
                    "technique_id": "technique.accepted",
                    "content_class": "practice",
                    "type": "active",
                    "status": "accepted",
                }
            ]
        }
        query = NeedQuery(purpose="calm", direction="downregulate", input_state=["tense"])
        result = select_content_item(query, library=library, technique_canon=techniques)
        assert result.matched is True
        assert result.item_id == "active.item"

    def test_skipped_technique_item_not_selected(self):
        library = {
            "items": [
                {
                    "identity": {
                        "item_id": "skipped.tech.item",
                        "content_class": "practice",
                        "type": "box",
                        "status": "active",
                        "technique_id": "technique.skipped",
                    },
                    "retrieval": {
                        "purpose": ["focus"],
                        "direction": ["focus"],
                        "input_state": ["scattered"],
                        "context": ["anytime"],
                        "duration": 2,
                        "duration_unit": "minutes",
                        "energy_effect": "neutral",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Box", "body": "box body"}},
                    },
                }
            ]
        }
        techniques = {
            "techniques": [
                {
                    "technique_id": "technique.skipped",
                    "content_class": "practice",
                    "type": "box",
                    "status": "skipped",
                }
            ]
        }
        query = NeedQuery(purpose="focus", direction="focus", input_state=["scattered"])
        result = select_content_item(query, library=library, technique_canon=techniques)
        assert result.matched is False

    def test_energy_effect_bumps_score(self):
        library = {
            "items": [
                {
                    "identity": {
                        "item_id": "up.item",
                        "content_class": "practice",
                        "type": "up",
                        "status": "active",
                    },
                    "retrieval": {
                        "purpose": ["energy"],
                        "direction": ["activate"],
                        "input_state": ["low_energy"],
                        "context": ["anytime"],
                        "duration": 2,
                        "duration_unit": "minutes",
                        "energy_effect": "up",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Up", "body": "up body"}},
                    },
                },
                {
                    "identity": {
                        "item_id": "neutral.item",
                        "content_class": "practice",
                        "type": "neutral",
                        "status": "active",
                    },
                    "retrieval": {
                        "purpose": ["energy"],
                        "direction": ["activate"],
                        "input_state": ["low_energy"],
                        "context": ["anytime"],
                        "duration": 2,
                        "duration_unit": "minutes",
                        "energy_effect": "neutral",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Neutral", "body": "neutral body"}},
                    },
                },
            ]
        }
        techniques = {"techniques": []}
        query = NeedQuery(
            purpose="energy",
            direction="activate",
            input_state=["low_energy"],
            energy_effect="up",
        )
        result = select_content_item(query, library=library, technique_canon=techniques)
        assert result.matched is True
        assert result.item_id == "up.item"

    def test_duration_filter(self):
        library = {
            "items": [
                {
                    "identity": {
                        "item_id": "two.min",
                        "content_class": "practice",
                        "type": "two",
                        "status": "active",
                    },
                    "retrieval": {
                        "purpose": ["calm"],
                        "direction": ["downregulate"],
                        "input_state": ["tense"],
                        "context": ["anytime"],
                        "duration": 2,
                        "duration_unit": "minutes",
                        "energy_effect": "down",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Two", "body": "two body"}},
                    },
                },
                {
                    "identity": {
                        "item_id": "five.min",
                        "content_class": "practice",
                        "type": "five",
                        "status": "active",
                    },
                    "retrieval": {
                        "purpose": ["calm"],
                        "direction": ["downregulate"],
                        "input_state": ["tense"],
                        "context": ["anytime"],
                        "duration": 5,
                        "duration_unit": "minutes",
                        "energy_effect": "down",
                        "delivery": ["text"],
                    },
                    "payload": {
                        "body_kind": "instruction",
                        "locales": {"ru": {"title": "Five", "body": "five body"}},
                    },
                },
            ]
        }
        techniques = {"techniques": []}
        query = NeedQuery(purpose="calm", direction="downregulate", duration=5)
        result = select_content_item(query, library=library, technique_canon=techniques)
        assert result.matched is True
        assert result.item_id == "five.min"
