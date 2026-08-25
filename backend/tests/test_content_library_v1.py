"""Practice content library seed — taxonomy + coverage ledger."""

from __future__ import annotations

from pathlib import Path

from todayflow_backend.data.content_library_validator_v1 import (
    first_empty_p0_cell,
    load_json,
    validate_content_library_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

PRACTICE_REF = DATA_ROOT / "reference" / "practice"
VOCAB_PATH = PRACTICE_REF / "content_taxonomy_v1.json"
LIBRARY_PATH = PRACTICE_REF / "content_library_v1.json"
COVERAGE_PATH = PRACTICE_REF / "content_coverage_matrix_v1.json"

SEED_1_ID = "practice.sensory_grounding.001"
SEED_1_CELL = "need.grounding.stabilize"
SEED_2_ID = "practice.extended_exhale.001"
SEED_2_CELL = "need.calm.downregulate"


def _load() -> tuple[dict, dict, dict]:
    return (
        load_json(VOCAB_PATH),
        load_json(LIBRARY_PATH),
        load_json(COVERAGE_PATH),
    )


def test_library_valid_against_taxonomy_and_ledger() -> None:
    vocab, library, coverage = _load()
    assert validate_content_library_v1(library, vocab=vocab, coverage=coverage) == []


def test_seed_pass_closes_exactly_one_cell_per_item() -> None:
    _vocab, library, coverage = _load()
    items = {item["identity"]["item_id"]: item for item in library["items"]}
    listed: dict[str, list[str]] = {}
    for cell in coverage["need_cells"]:
        for iid in cell.get("item_ids") or []:
            listed.setdefault(iid, []).append(cell["id"])
    for iid, item in items.items():
        assert listed.get(iid) == [item["identity"]["seed_cell"]]


def test_p0_seed_1_grounding_stabilize() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_1_ID)
    assert item["identity"]["seed_cell"] == SEED_1_CELL
    assert item["identity"]["type"] == "sensory_grounding"
    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_1_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_1_ID]


def test_p0_seed_2_is_first_ledger_empty_cell_calm() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_2_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "breathwork"
    assert item["identity"]["type"] == "extended_exhale"
    assert item["identity"]["seed_cell"] == SEED_2_CELL
    assert item["retrieval"]["purpose"] == ["calm"]
    assert item["retrieval"]["direction"] == ["downregulate"]
    assert "tense" in item["retrieval"]["input_state"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_2_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_2_ID]
    assert coverage["need_cells"][0]["id"] == SEED_2_CELL

    next_empty = first_empty_p0_cell(coverage)
    assert next_empty is not None
    assert next_empty["id"] == "need.focus.focus"


def test_overlapping_state_does_not_close_other_cells() -> None:
    _vocab, _library, coverage = _load()
    calm = next(c for c in coverage["need_cells"] if c["id"] == SEED_2_CELL)
    grounding = next(c for c in coverage["need_cells"] if c["id"] == SEED_1_CELL)
    assert SEED_1_ID not in (calm.get("item_ids") or [])
    assert SEED_2_ID not in (grounding.get("item_ids") or [])


def test_coverage_counts() -> None:
    _vocab, library, coverage = _load()
    assert coverage["counts"]["library_items"] == 2
    assert coverage["counts"]["need_cells_empty"] == 24
    assert coverage["counts"]["need_cells_seed"] == 2
    assert library["status"] == "seed"


def test_repo_paths_exist() -> None:
    for path in (VOCAB_PATH, LIBRARY_PATH, COVERAGE_PATH):
        assert Path(path).is_file()
