"""Tests for PR1 PIM read audit markers."""

from todayflow_backend.services.today_pim_read_audit_v1 import build_pim_read_audit_v1


def test_build_pim_read_audit_empty_slice_ok():
    day_ctx = {
        "layers": {
            "day_engine_brief": {"headline": "x"},
            "knowledge_context_slice": {"items": []},
        }
    }
    audit = build_pim_read_audit_v1(
        day_ctx=day_ctx,
        ritual_context={"tarot_main_id": 5, "numerology_value": "7"},
        fusion_dump={"scores": {"energy": 0.5}},
    )
    assert audit["pim_slice_requested"]["read_model_id"]
    assert audit["pim_slice_used"]["atom_count"] == 0
    assert audit["pim_slice_used"]["atom_ids"] == []
    assert "ritual_context.tarot_main_id" in audit["dre_fields_used"]
    assert "layers.knowledge_context_slice" in audit["dre_fields_used"]
    assert "fusion_dump.scores" in audit["dre_fields_used"]


def test_build_pim_read_audit_day1_empty_atoms():
    """Day-1: slice path exists, zero atoms — not a missing audit."""
    audit = build_pim_read_audit_v1(
        day_ctx={"layers": {"knowledge_context_slice": {"items": []}}},
        ritual_context={"tarot_main_id": 3, "numerology_value": "7"},
        fusion_dump={"scores": {"energy": 0.4}},
    )
    assert audit["pim_slice_used"]["atom_count"] == 0
    assert audit["pim_slice_used"]["atom_ids"] == []
    assert audit["dre_fields_used"]
    assert "ritual_context.tarot_main_id" in audit["dre_fields_used"]
    assert "fusion_dump.scores" in audit["dre_fields_used"]


def test_build_pim_read_audit_day_n_with_atoms():
    """Day-N: same path, non-empty atom_ids — proves slice can flow to DRE."""
    day_ctx = {
        "layers": {
            "knowledge_context_slice": {
                "items": [{"knowledge_id": "k1"}, {"knowledge_id": "k2"}],
            },
        }
    }
    audit = build_pim_read_audit_v1(day_ctx=day_ctx, ritual_context=None, fusion_dump=None)
    assert audit["pim_slice_used"]["atom_count"] == 2
    assert set(audit["pim_slice_used"]["atom_ids"]) == {"k1", "k2"}
