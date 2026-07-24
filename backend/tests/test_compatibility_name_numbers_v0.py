"""Soft name_numbers_pair for Compatibility."""

from __future__ import annotations

from todayflow_backend.services.compatibility_name_numbers_v0 import build_name_numbers_pair


def test_pair_both_names():
    pack = build_name_numbers_pair(name_a="Анна", name_b="Игорь")
    assert pack is not None
    assert pack["status"] == "ok"
    assert pack["a"]["expression"]["value"]
    assert pack["b"]["expression"]["value"]
    assert pack["claim_lines"]
    assert "Expression" in pack["claim_lines"][0]


def test_pair_partial_one_name():
    pack = build_name_numbers_pair(name_a="Anna", name_b=None)
    assert pack is not None
    assert pack["status"] == "partial"
    assert pack["a"] is not None
    assert pack["b"] is None


def test_pair_empty():
    assert build_name_numbers_pair(name_a="", name_b=None) is None
