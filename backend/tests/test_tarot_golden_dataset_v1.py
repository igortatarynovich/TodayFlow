"""Tarot Golden Dataset v1 — scenarios without scores."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.core import models
from todayflow_backend.data import tarot_knowledge_v1 as tarot_kb
from todayflow_backend.data import tarot_question_ontology_v1 as ont
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "backend" / "tests" / "fixtures" / "tarot_golden_dataset_v1.json"
SCHEMA = ROOT / "docs" / "schemas" / "tarot_golden_dataset_v1.schema.json"

_Q1 = (
    "core_scene",
    "central_conflict",
    "adjacent_distinction",
)


def _load() -> dict:
    return json.loads(DATASET.read_text(encoding="utf-8"))


def _spread(sc: dict) -> models.TarotSpreadResult:
    cards = []
    for item in sc["cards"]:
        cards.append(
            models.TarotSpreadCard(
                card=models.TarotCard(
                    id=int(item["card_id"]),
                    name=f"Card {item['card_id']}",
                    keywords=[],
                    upright="",
                    reversed="",
                ),
                orientation=str(item.get("orientation") or "upright"),
                position=models.TarotSpreadPosition(
                    id=str(item["position_id"]),
                    title=str(item.get("title") or item["position_id"]),
                    prompt=str(item.get("title") or ""),
                ),
                meaning="",
            )
        )
    return models.TarotSpreadResult(
        spread_id=str(sc["spread_id"]),
        title=str(sc.get("label") or sc["id"]),
        cards=cards,
    )


def test_golden_dataset_schema_and_coverage():
    payload = _load()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert payload["contract_version"] == "tarot_golden_dataset_v1"
    scenarios = payload["scenarios"]
    assert len(scenarios) >= 10
    ids = [s["id"] for s in scenarios]
    assert len(ids) == len(set(ids))
    types = {s["expect"]["question_type"] for s in scenarios}
    assert types == ont.QUESTION_TYPES
    # No numeric rubric fields in dataset (Eval owns scoring).
    blob = json.dumps(payload, ensure_ascii=False).lower()
    for banned in ('"score"', "paid_worth", "anti_sameness_verdict", "rubric_1_5"):
        assert banned not in blob


def test_golden_dataset_ontology_expects_match_classifier():
    for sc in _load()["scenarios"]:
        kind = engine.spread_kind(sc["spread_id"])
        got = ont.classify_question(
            sc["question"],
            concern_domain=sc.get("concern_domain"),
            spread_kind=kind,
        )
        for key, value in sc["expect"].items():
            if key == "answer_shape":
                continue
            assert got.get(key) == value, (
                f"{sc['id']}: {key} got={got.get(key)!r} want={value!r} full={got}"
            )


def test_golden_dataset_packs_build_with_kb_and_q1_minors():
    for sc in _load()["scenarios"]:
        pack = engine.build_context_pack(
            _spread(sc),
            question=sc["question"],
            concern_domain=sc.get("concern_domain"),
            experience_slice=sc.get("profile") or {},
        )
        assert pack is not None, sc["id"]
        assert pack.get("question")
        blob = json.dumps(pack, ensure_ascii=False)
        assert "Аркан" not in blob
        for card in pack.get("cards") or []:
            rng = card.get("meaning_range") or {}
            assert rng.get("knowledge_source") == "tarot_knowledge_v1", sc["id"]
            cid = int(card["card_id"])
            if cid >= 22:
                for key in _Q1:
                    assert str(rng.get(key) or "").strip(), (sc["id"], cid, key)


def test_golden_q1_adjacent_gates_are_distinct_archetypes():
    cards = tarot_kb.cards_by_id()
    for trio in ((43, 44, 45), (57, 58, 59)):
        scenes = [str(cards[i]["core_scene"]).strip().lower() for i in trio]
        assert len(set(scenes)) == 3, scenes
