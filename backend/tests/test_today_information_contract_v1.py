"""Today Information Contract v1 — closed N gate (start hop)."""

from __future__ import annotations

from todayflow_backend.services.today_information_contract_v1 import (
    CHROME_EXEMPT_PREFIXES,
    COVERAGE_STATUSES,
    KNOWLEDGE_TO_SLOT,
    PIC_IDENTITY_SLOTS_FORBIDDEN,
    TIC_COVERAGE,
    TIC_DEFECT_QUEUE,
    TIC_FACT_IDS,
    TIC_KNOWLEDGE_IDS,
    TODAY_MEANING_PRODUCERS,
)


def test_tic_n20_is_closed() -> None:
    assert TIC_KNOWLEDGE_IDS == tuple(f"K{i:02d}" for i in range(1, 21))
    assert len(set(TIC_KNOWLEDGE_IDS)) == 20
    assert TIC_FACT_IDS == tuple(f"F{i:02d}" for i in range(1, 17))
    assert len(set(TIC_FACT_IDS)) == 16


def test_tic_every_k_has_slots_and_no_pic_identity_leak() -> None:
    assert tuple(KNOWLEDGE_TO_SLOT) == TIC_KNOWLEDGE_IDS
    for kid, slots in KNOWLEDGE_TO_SLOT.items():
        assert slots, kid
        for slot in slots:
            assert slot not in PIC_IDENTITY_SLOTS_FORBIDDEN
            assert not slot.startswith("P1.")
            assert not slot.startswith("P2.")
            assert not slot.startswith("P3.")
            assert not slot.startswith("P4.")
            assert not slot.startswith("P5.")
            assert not slot.startswith("P6.")


def test_tic_k01_is_shared_day_kind_not_identity_core() -> None:
    assert KNOWLEDGE_TO_SLOT["K01"] == (
        "T1-hero.energy_word",
        "T1-hero.energy_pct",
        "T1-hero.mood",
        "T1-hero.human_line",
        "T1-hero.sheet",
    )
    assert "P1.recognition_line" not in KNOWLEDGE_TO_SLOT["K01"]


def test_tic_producers_cite_closed_ids_only() -> None:
    assert TODAY_MEANING_PRODUCERS
    for row in TODAY_MEANING_PRODUCERS:
        for kid in row["tic_k"]:  # type: ignore[index]
            assert kid in TIC_KNOWLEDGE_IDS
        for fid in row["tic_f"]:  # type: ignore[index]
            assert fid in TIC_FACT_IDS
        slot = row["slot_id"]
        assert isinstance(slot, str) and slot.startswith("T")


def test_tic_coverage_audit_covers_n20() -> None:
    assert len(TIC_COVERAGE) == 20
    assert tuple(row["tic_k"] for row in TIC_COVERAGE) == TIC_KNOWLEDGE_IDS
    by_id = {str(row["tic_k"]): row for row in TIC_COVERAGE}
    for kid, row in by_id.items():
        assert row["status"] in COVERAGE_STATUSES, kid
        assert row["slot_id"]
    complete = {kid for kid, row in by_id.items() if row["status"] == "COMPLETE"}
    partial = {kid for kid, row in by_id.items() if row["status"] == "PARTIAL"}
    missing = {kid for kid, row in by_id.items() if row["status"] == "MISSING"}
    omit = {kid for kid, row in by_id.items() if row["status"] == "OMIT-BY-DESIGN"}
    assert complete == {
        "K01",
        "K02",
        "K03",
        "K04",
        "K05",
        "K06",
        "K07",
        "K08",
        "K09",
        "K10",
        "K11",
        "K12",
        "K13",
        "K14",
        "K15",
        "K18",
        "K19",
    }
    assert partial == {
        "K16",
        "K17",
        "K20",
    }
    assert missing == set()
    assert omit == set()
    assert TIC_DEFECT_QUEUE == (
        "K16",
        "K17",
        "K20",
    )
    assert TIC_DEFECT_QUEUE[0] == "K16"
    assert by_id["K01"]["status"] == "COMPLETE"
    assert by_id["K06"]["status"] == "COMPLETE"
    assert by_id["K07"]["status"] == "COMPLETE"
    assert by_id["K09"]["status"] == "COMPLETE"
    assert by_id["K10"]["status"] == "COMPLETE"
    assert by_id["K13"]["status"] == "COMPLETE"
    assert by_id["K14"]["status"] == "COMPLETE"
    assert by_id["K15"]["status"] == "COMPLETE"
    assert "P1.recognition_line" not in by_id["K01"]["slot_id"]


def test_tic_chrome_exempt_does_not_include_meaning_slots() -> None:
    meaning = {slot for slots in KNOWLEDGE_TO_SLOT.values() for slot in slots}
    for prefix in CHROME_EXEMPT_PREFIXES:
        assert prefix.startswith(("T1-", "T2-", "T3.", "T4.", "TF.", "SF."))
        for slot in meaning:
            assert slot != prefix
