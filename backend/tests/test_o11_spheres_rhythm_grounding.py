"""O11: привязка текста «Сферы» к rhythm_context при достаточном объёме данных."""

from __future__ import annotations

from todayflow_backend.services.today_narrative import (
    _rhythm_context_signal_categories,
    _spheres_payload_grounded_in_rhythm,
)


def test_rhythm_categories_counts_distinct_buckets():
    rc = {
        "goals": [{"title": "x", "scope": "week", "completed": False}],
        "habits": [],
        "ascetics": [],
        "diary": {"has_entry_today": False, "entries_last_7_days": 0},
    }
    assert _rhythm_context_signal_categories(rc) == 1
    rc2 = {
        "goals": [{"title": "x", "scope": "week", "completed": False}],
        "habits": [{"name": "h", "category": None, "frequency": "daily", "completed_today": False}],
        "ascetics": [],
        "diary": {"has_entry_today": False, "entries_last_7_days": 0},
    }
    assert _rhythm_context_signal_categories(rc2) == 2


def test_grounding_skipped_when_few_categories():
    payload = {
        "page_intro": "Общий день без отсылок к привычкам.",
        "thesis_reminder": "Линия дня.",
        "scenario_tie_ins": {"love": "шаг", "family": "шаг", "career": "шаг", "money": "шаг"},
    }
    rc = {
        "goals": [{"title": "Марафон подготовки", "scope": "week", "completed": False}],
        "habits": [],
        "ascetics": [],
        "diary": {"has_entry_today": False, "entries_last_7_days": 0},
    }
    assert _spheres_payload_grounded_in_rhythm(payload, rc) is True


def test_grounding_passes_with_title_needle():
    payload = {
        "page_intro": "Сегодня опираемся на марафон подготовки и ровный темп.",
        "thesis_reminder": "Одна линия.",
        "scenario_tie_ins": {"love": "шаг", "family": "шаг", "career": "шаг", "money": "шаг"},
    }
    rc = {
        "goals": [{"title": "Марафон подготовки", "scope": "week", "completed": False}],
        "habits": [{"name": "Утро без телефона", "category": None, "frequency": "daily", "completed_today": False}],
        "ascetics": [],
        "diary": {"has_entry_today": False, "entries_last_7_days": 0},
    }
    assert _rhythm_context_signal_categories(rc) == 2
    assert _spheres_payload_grounded_in_rhythm(payload, rc) is True


def test_grounding_passes_with_soft_anchor_ru():
    payload = {
        "page_intro": "Две опоры — цель недели и привычка утра — задают тон сферам.",
        "thesis_reminder": "Без новой драмы.",
        "scenario_tie_ins": {"love": "шаг", "family": "шаг", "career": "шаг", "money": "шаг"},
    }
    rc = {
        "goals": [{"title": "X", "scope": "week", "completed": False}],
        "habits": [{"name": "Y", "category": None, "frequency": "daily", "completed_today": False}],
        "ascetics": [],
        "diary": {"has_entry_today": False, "entries_last_7_days": 0},
    }
    assert _spheres_payload_grounded_in_rhythm(payload, rc) is True


def test_grounding_fails_when_orphan_text():
    payload = {
        "page_intro": "Сферы звучат мягко и ровно, без лишнего шума.",
        "thesis_reminder": "Держи одну линию.",
        "scenario_tie_ins": {"love": "шаг", "family": "шаг", "career": "шаг", "money": "шаг"},
    }
    rc = {
        "goals": [{"title": "Марафон подготовки", "scope": "week", "completed": False}],
        "habits": [{"name": "Утро без телефона", "category": None, "frequency": "daily", "completed_today": False}],
        "ascetics": [],
        "diary": {"has_entry_today": False, "entries_last_7_days": 0},
    }
    assert _spheres_payload_grounded_in_rhythm(payload, rc) is False
