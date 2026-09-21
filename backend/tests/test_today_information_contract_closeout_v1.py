"""TIC close-out gate — independent of TIC_COVERAGE COMPLETE."""

from __future__ import annotations

from pathlib import Path

from todayflow_backend.services.today_information_contract_v1 import (
    TIC_CLOSEOUT_BLOCKS,
    TIC_KNOWLEDGE_IDS,
    evaluate_tic_closeout,
)

ROOT = Path(__file__).resolve().parents[2]


def test_closeout_does_not_treat_coverage_table_as_verdict() -> None:
    src = (ROOT / "backend/src/todayflow_backend/services/today_information_contract_v1.py").read_text(
        encoding="utf-8"
    )
    fn = src.split("def evaluate_tic_closeout", 1)[1].split("def ", 1)[0]
    assert "TIC_COVERAGE" not in fn
    result = evaluate_tic_closeout(ROOT)
    assert result["independent_of_tic_coverage"] is True
    assert result["n"] == 20
    assert result["invented_k21"] is False
    assert TIC_KNOWLEDGE_IDS[-1] == "K20"


def test_tic_closeout_four_blocks_pass() -> None:
    result = evaluate_tic_closeout(ROOT)
    names = tuple(str(b["block"]) for b in result["blocks"])  # type: ignore[index]
    assert names == TIC_CLOSEOUT_BLOCKS
    assert result["failed_blocks"] == ()
    assert result["verdict"] == "PASS"
    assert result["status"] == "CLOSED"
    glance = result["glance_leftover"]
    assert glance["in_locked_surface_scope"] is False
    assert glance["declared_out_of_scope"] is True


def test_closeout_executable_re_audit_is_20_complete() -> None:
    result = evaluate_tic_closeout(ROOT)
    audit = next(b for b in result["blocks"] if b["block"] == "executable_re_audit")  # type: ignore[index]
    assert audit["verdict"] == "PASS"
    assert audit["complete"] == 20
    assert audit["partial"] == 0
    assert audit["missing"] == 0
    assert audit["omit_by_design"] == 0
    assert audit["defects"] == ()
