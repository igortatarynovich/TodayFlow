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
SEED_3_ID = "practice.box_breathing.001"
SEED_3_CELL = "need.focus.focus"
SEED_4_ID = "practice.energizing_breath.001"
SEED_4_CELL = "need.energy.activate"
SEED_5_ID = "practice.prompted_reflection.001"
SEED_5_CELL = "need.clarity.reflect"
SEED_6_ID = "affirmation.capability.001"
SEED_6_CELL = "need.confidence.open"
SEED_7_ID = "practice.body_release.001"
SEED_7_CELL = "need.release.release"
SEED_8_ID = "meditation.relaxation.001"
SEED_8_CELL = "need.rest.downregulate"
SEED_9_ID = "meditation.sleep.001"
SEED_9_CELL = "need.sleep.prepare"
SEED_10_ID = "discipline.sleep_discipline.001"
SEED_10_CELL = "need.sleep.discipline"


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


def test_p0_seed_3_is_first_ledger_empty_cell_focus() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "breathwork"
    assert item["identity"]["type"] == "box_breathing"
    assert item["identity"]["seed_cell"] == SEED_3_CELL
    assert item["retrieval"]["purpose"] == ["focus"]
    assert item["retrieval"]["direction"] == ["focus"]
    assert item["retrieval"]["input_state"] == ["scattered"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_3_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_3_ID]
    assert coverage["need_cells"][1]["id"] == SEED_3_CELL


def test_p0_seed_4_is_first_ledger_empty_cell_energy() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_4_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "breathwork"
    assert item["identity"]["type"] == "energizing_breath"
    assert item["identity"]["seed_cell"] == SEED_4_CELL
    assert item["retrieval"]["purpose"] == ["energy"]
    assert item["retrieval"]["direction"] == ["activate"]
    assert item["retrieval"]["input_state"] == ["low_energy"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_4_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_4_ID]
    assert coverage["need_cells"][2]["id"] == SEED_4_CELL


def test_p0_seed_5_is_first_ledger_empty_cell_clarity() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_5_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "reflection"
    assert item["identity"]["type"] == "prompted_reflection"
    assert item["identity"]["seed_cell"] == SEED_5_CELL
    assert item["retrieval"]["purpose"] == ["clarity"]
    assert item["retrieval"]["direction"] == ["reflect"]
    assert item["retrieval"]["input_state"] == ["uncertain"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_5_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_5_ID]
    assert coverage["need_cells"][4]["id"] == SEED_5_CELL


def test_p0_seed_6_is_first_ledger_empty_cell_confidence() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_6_ID)
    assert item["identity"]["content_class"] == "affirmation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "capability"
    assert item["identity"]["seed_cell"] == SEED_6_CELL
    assert item["retrieval"]["purpose"] == ["confidence"]
    assert item["retrieval"]["direction"] == ["open"]
    assert item["retrieval"]["input_state"] == ["uncertain"]
    assert item["payload"]["body_kind"] == "affirmation_text"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_6_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_6_ID]
    assert coverage["need_cells"][5]["id"] == SEED_6_CELL


def test_p0_seed_7_is_first_ledger_empty_cell_release() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_7_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "somatic"
    assert item["identity"]["type"] == "body_release"
    assert item["identity"]["seed_cell"] == SEED_7_CELL
    assert item["retrieval"]["purpose"] == ["release"]
    assert item["retrieval"]["direction"] == ["release"]
    assert item["retrieval"]["input_state"] == ["emotionally_heavy", "stuck"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_7_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_7_ID]
    assert coverage["need_cells"][6]["id"] == SEED_7_CELL


def test_p0_seed_8_is_first_ledger_empty_cell_rest() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_8_ID)
    assert item["identity"]["content_class"] == "meditation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "relaxation"
    assert item["identity"]["seed_cell"] == SEED_8_CELL
    assert item["retrieval"]["purpose"] == ["rest"]
    assert item["retrieval"]["direction"] == ["downregulate"]
    assert item["retrieval"]["input_state"] == ["overstimulated"]
    assert item["payload"]["body_kind"] == "script"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_8_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_8_ID]
    assert coverage["need_cells"][7]["id"] == SEED_8_CELL


def test_p0_seed_9_is_first_ledger_empty_cell_sleep_prepare() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_9_ID)
    assert item["identity"]["content_class"] == "meditation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "sleep"
    assert item["identity"]["seed_cell"] == SEED_9_CELL
    assert item["retrieval"]["purpose"] == ["sleep"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["restless", "overstimulated"]
    assert item["payload"]["body_kind"] == "script"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_9_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_9_ID]
    assert coverage["need_cells"][8]["id"] == SEED_9_CELL

    sleep_discipline = next(
        c for c in coverage["need_cells"] if c["id"] == SEED_10_CELL
    )
    assert SEED_9_ID not in (sleep_discipline.get("item_ids") or [])


def test_p0_seed_10_is_first_ledger_empty_cell_sleep_discipline() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_10_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "sleep_discipline"
    assert item["identity"]["seed_cell"] == SEED_10_CELL
    assert item["retrieval"]["purpose"] == ["sleep"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["restless"]
    assert "duration" not in item["retrieval"]
    assert "duration_unit" not in item["retrieval"]
    assert item["retrieval"]["duration_days"] == 7
    assert item["retrieval"]["frequency"] == "daily"
    assert item["retrieval"]["difficulty"] == "low"
    assert item["retrieval"]["failure_policy"] == "continue"
    assert item["retrieval"]["check_in_frequency"] == "daily"
    assert item["payload"]["body_kind"] == "commitment_rule"
    assert item["payload"]["commitment_rule"]
    assert item["payload"]["restriction"]
    assert item["payload"]["start_condition"]
    assert item["payload"]["completion_condition"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_10_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"] == [SEED_10_ID]
    assert coverage["need_cells"][9]["id"] == SEED_10_CELL
    assert cell["job"] == "period"

    sleep_prepare = next(c for c in coverage["need_cells"] if c["id"] == SEED_9_CELL)
    assert SEED_10_ID not in (sleep_prepare.get("item_ids") or [])
    assert sleep_prepare["item_ids"] == [SEED_9_ID]

    next_empty = first_empty_p0_cell(coverage)
    assert next_empty is not None
    assert next_empty["id"] == "need.motivation.activate"


def test_overlapping_state_does_not_close_other_cells() -> None:
    _vocab, _library, coverage = _load()
    calm = next(c for c in coverage["need_cells"] if c["id"] == SEED_2_CELL)
    grounding = next(c for c in coverage["need_cells"] if c["id"] == SEED_1_CELL)
    focus = next(c for c in coverage["need_cells"] if c["id"] == SEED_3_CELL)
    energy = next(c for c in coverage["need_cells"] if c["id"] == SEED_4_CELL)
    clarity = next(c for c in coverage["need_cells"] if c["id"] == SEED_5_CELL)
    motivation = next(c for c in coverage["need_cells"] if c["id"] == "need.motivation.activate")
    recovery = next(c for c in coverage["need_cells"] if c["id"] == "need.recovery.recover")
    confidence = next(c for c in coverage["need_cells"] if c["id"] == SEED_6_CELL)
    decision = next(c for c in coverage["need_cells"] if c["id"] == "need.decision_making.focus")
    awareness = next(c for c in coverage["need_cells"] if c["id"] == "need.emotional_awareness.reflect")
    reset = next(c for c in coverage["need_cells"] if c["id"] == "need.reset.release")
    sleep_prepare = next(c for c in coverage["need_cells"] if c["id"] == SEED_9_CELL)
    sleep_discipline = next(c for c in coverage["need_cells"] if c["id"] == SEED_10_CELL)
    rest = next(c for c in coverage["need_cells"] if c["id"] == SEED_8_CELL)
    detachment = next(c for c in coverage["need_cells"] if c["id"] == "need.detachment.release")
    simplicity = next(c for c in coverage["need_cells"] if c["id"] == "need.simplicity.release")
    assert SEED_1_ID not in (calm.get("item_ids") or [])
    assert SEED_2_ID not in (grounding.get("item_ids") or [])
    assert SEED_1_ID not in (focus.get("item_ids") or [])
    assert SEED_3_ID not in (grounding.get("item_ids") or [])
    assert SEED_4_ID not in (motivation.get("item_ids") or [])
    assert SEED_4_ID not in (recovery.get("item_ids") or [])
    assert SEED_5_ID not in (confidence.get("item_ids") or [])
    assert SEED_6_ID not in (clarity.get("item_ids") or [])
    assert SEED_6_ID not in (decision.get("item_ids") or [])
    assert SEED_7_ID not in (motivation.get("item_ids") or [])
    assert SEED_7_ID not in (awareness.get("item_ids") or [])
    assert SEED_7_ID not in (reset.get("item_ids") or [])
    assert SEED_8_ID not in (calm.get("item_ids") or [])
    assert SEED_8_ID not in (sleep_prepare.get("item_ids") or [])
    assert SEED_8_ID not in (detachment.get("item_ids") or [])
    assert SEED_8_ID not in (simplicity.get("item_ids") or [])
    assert SEED_9_ID not in (rest.get("item_ids") or [])
    assert SEED_9_ID not in (sleep_discipline.get("item_ids") or [])
    assert SEED_10_ID not in (sleep_prepare.get("item_ids") or [])
    assert motivation["status"] == "empty"
    assert recovery["status"] == "empty"
    assert decision["status"] == "empty"
    assert awareness["status"] == "empty"
    assert reset["status"] == "empty"
    assert detachment["status"] == "empty"
    assert simplicity["status"] == "empty"
    assert energy["item_ids"] == [SEED_4_ID]
    assert confidence["item_ids"] == [SEED_6_ID]
    assert calm["item_ids"] == [SEED_2_ID]
    assert sleep_prepare["item_ids"] == [SEED_9_ID]
    assert sleep_discipline["item_ids"] == [SEED_10_ID]


def test_coverage_counts() -> None:
    _vocab, library, coverage = _load()
    assert coverage["counts"]["library_items"] == 10
    assert coverage["counts"]["need_cells_empty"] == 16
    assert coverage["counts"]["need_cells_seed"] == 10
    assert library["status"] == "seed"


def test_repo_paths_exist() -> None:
    for path in (VOCAB_PATH, LIBRARY_PATH, COVERAGE_PATH):
        assert Path(path).is_file()
