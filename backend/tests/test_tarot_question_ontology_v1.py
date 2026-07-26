"""Tarot Question Ontology v1 — classification + pack projection."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.core import models
from todayflow_backend.data import tarot_question_ontology_v1 as ont
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine
from todayflow_backend.services import tarot_interpretation_llm_v1 as tarot_llm

ROOT = Path(__file__).resolve().parents[2]
TYPES_JSON = ROOT / "DATA" / "reference" / "tarot" / "question_ontology_v1" / "types.json"
SCHEMA = ROOT / "docs" / "schemas" / "tarot_question_ontology_v1.schema.json"
INTEGRATION = ROOT / "backend" / "tests" / "fixtures" / "tarot_question_ontology_integration_v1.json"


def _card(cid: int, orientation: str, pid: str, title: str) -> models.TarotSpreadCard:
    return models.TarotSpreadCard(
        card=models.TarotCard(id=cid, name=f"Card {cid}", keywords=[], upright="", reversed=""),
        orientation=orientation,
        position=models.TarotSpreadPosition(id=pid, title=title, prompt=title),
        meaning="",
    )


def test_question_ontology_schema_has_ten_types():
    payload = json.loads(TYPES_JSON.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert set(ont.types_by_id()) == ont.QUESTION_TYPES


def test_integration_set_classifies_expected_types():
    cases = json.loads(INTEGRATION.read_text(encoding="utf-8"))["cases"]
    assert len(cases) >= 10
    for case in cases:
        got = ont.classify_question(
            case["question"],
            concern_domain=case.get("concern_domain"),
            spread_kind=case.get("spread_kind"),
        )
        expect = case["expect"]
        for key, value in expect.items():
            assert got.get(key) == value, f"{case['id']}: {key} got={got.get(key)!r} want={value!r} full={got}"
        if case.get("not_question_type"):
            assert got["question_type"] != case["not_question_type"], case["id"]
        needle = case.get("must_not_claim_contains")
        if needle:
            blob = " ".join(got.get("must_not_claim") or [])
            assert needle.lower() in blob.lower(), case["id"]


def test_choice_clarify_open_reflection_differ():
    choice = ont.classify_question(
        "Уйти с работы или остаться ещё на год?",
        concern_domain="work",
        spread_kind="choice",
    )
    clarify = ont.classify_question(
        "Помоги прояснить, что на самом деле происходит с моим решением о переезде",
        concern_domain="decision",
    )
    open_q = ont.classify_question("Что мне важно увидеть сейчас?", concern_domain="other")
    assert choice["question_type"] == "choice"
    assert clarify["question_type"] != "choice"
    assert open_q["question_type"] == "open_reflection"
    assert choice["central_task"] != open_q["central_task"]
    assert any("гарант" in x.lower() or "лучше" in x.lower() for x in choice["must_not_claim"])


def test_relationship_intent_and_timing_guards_in_pack():
    intent = ont.pack_question_ontology("Что она хочет от этих отношений?")
    assert intent["question_type"] == "relationship_intent"
    assert any("факт" in x.lower() or "мысли" in x.lower() for x in intent["must_not_claim"])

    timing = ont.pack_question_ontology("Пора ли сейчас менять работу?")
    assert timing["question_type"] == "timing_readiness"
    assert any("дат" in x.lower() for x in timing["must_not_claim"])

    spread = models.TarotSpreadResult(
        spread_id="one_card",
        title="Одна",
        cards=[_card(0, "upright", "focus", "Фокус")],
    )
    pack = engine.build_context_pack(
        spread,
        question="Что он думает обо мне?",
        concern_domain="relationships",
    )
    assert pack is not None
    qo = pack["question_ontology"]
    assert qo["question_type"] == "relationship_intent"
    assert qo["must_not_claim"]
    assert pack["response_shape"].get("next_step_kind")


def test_single_prompt_version_mentions_ontology_not_per_type_branch():
    assert tarot_llm.TAROT_INTERPRETATION_PROMPT_VER == "tarot-interpretation-v1.6"
    assert "question_ontology" in tarot_llm._SYSTEM_RU
    assert "не переключайся на отдельный шаблон" in tarot_llm._SYSTEM_RU
    assert "relationship_intent" in tarot_llm._SYSTEM_RU
    assert "timing_readiness" in tarot_llm._SYSTEM_RU
    assert "Не обязательно называть карты по имени" in tarot_llm._SYSTEM_RU
