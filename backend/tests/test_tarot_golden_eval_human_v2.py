"""Tarot Human Golden Eval v2 — schema + seed fixture."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "backend" / "tests" / "fixtures" / "tarot_golden_eval_human_v2.json"
SCHEMA = ROOT / "docs" / "schemas" / "tarot_golden_eval_human_v2.schema.json"


def test_human_eval_v2_seed_matches_schema():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert payload["contract_version"] == "tarot_golden_eval_human_v2"
    assert len(payload["cases"]) >= 1
    by_id = {c["id"]: c for c in payload["cases"]}
    case = by_id["hv2_work_direction_three"]
    human = case["human"]
    assert human["understood_symbols"] == "yes"
    assert human["answered_my_question"] == "yes"
    assert human["would_pay"] == "yes"
    assert human["voice_flags"]["antithesis_formula"] is True
    assert human["voice_flags"]["sees_self"] is True
    # Live captures append unscored; scored owner seed must remain.
    unscored = [c for c in payload["cases"] if not (c.get("human") or {}).get("scored_by")]
    assert len(payload["cases"]) >= 1 + len(unscored)
