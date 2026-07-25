"""Tarot Position Semantics v1 — role library + pack projection."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.core import models
from todayflow_backend.data import tarot_position_semantics_v1 as pos
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine

ROOT = Path(__file__).resolve().parents[2]
ROLES_JSON = ROOT / "DATA" / "reference" / "tarot" / "position_semantics_v1" / "roles.json"
SCHEMA = ROOT / "docs" / "schemas" / "tarot_position_semantics_v1.schema.json"
SPREADS = ROOT / "DATA" / "astrology_reference" / "tarot_spreads.json"


def _card(cid: int, orientation: str, pid: str, title: str) -> models.TarotSpreadCard:
    return models.TarotSpreadCard(
        card=models.TarotCard(id=cid, name=f"Card {cid}", keywords=[], upright="", reversed=""),
        orientation=orientation,
        position=models.TarotSpreadPosition(id=pid, title=title, prompt=title),
        meaning="",
    )


def test_position_semantics_schema_and_roles():
    payload = json.loads(ROLES_JSON.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    roles = pos.roles_by_id()
    for required in (
        "gain",
        "resource",
        "risk",
        "blocks",
        "hidden_cause",
        "next_step",
        "outcome",
        "past",
        "present",
        "future",
        "advice",
        "warning",
    ):
        assert required in roles, required
        row = roles[required]
        assert row["purpose"] and row["answers_question"] and row["extract_from_card"]
        assert len(row["do_not"]) >= 2
        assert "Аркан" not in json.dumps(row, ensure_ascii=False)


def test_live_spread_position_ids_map():
    spreads = json.loads(SPREADS.read_text(encoding="utf-8"))
    known = set(pos.roles_by_id())
    missing: list[str] = []
    for spread in spreads:
        for p in spread.get("positions") or []:
            pid = str(p.get("id") or "")
            role = pos.resolve_role_id(pid)
            if role not in known:
                missing.append(f"{spread.get('id')}:{pid}->{role}")
            # Prefer explicit map / non-neutral for known product spreads
            if spread.get("id") == "guidance_choice_two":
                assert role != "neutral", pid
    assert not missing


def test_next_step_and_risk_semantics_differ_for_same_card():
    """Fool in risk vs next_step must carry different position instructions."""
    spread = models.TarotSpreadResult(
        spread_id="guidance_choice_two",
        title="Выбор",
        cards=[
            _card(0, "upright", "a_risk", "Вариант A — риск"),
            _card(0, "upright", "best_step", "Лучший следующий шаг"),
            _card(0, "upright", "a_gives", "Вариант A — что он даёт"),
            _card(0, "upright", "outcome", "Итог"),
        ],
    )
    pack = engine.build_context_pack(spread, question="Стоит ли начинать?", concern_domain="decision")
    assert pack is not None
    risk, step, gain, outcome = (c["position_semantics"] for c in pack["cards"])
    assert risk["role_id"] == "risk"
    assert step["role_id"] == "next_step"
    assert gain["role_id"] == "gain"
    assert outcome["role_id"] == "outcome"
    assert risk["result_type"] != step["result_type"]
    assert "совет" in " ".join(risk["do_not"]).lower()
    assert "шаг" in step["extract_from_card"].lower() or "действи" in step["extract_from_card"].lower()
    assert pack["cards"][0]["position_role"] == "risk"
    assert pack["cards"][1]["position_role_instruction"]
