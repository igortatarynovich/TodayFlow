"""Tarot Knowledge Base v1 — load + pack projection tests."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.core import models
from todayflow_backend.data import tarot_knowledge_v1 as tarot_kb
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine

ROOT = Path(__file__).resolve().parents[2]
KB_JSON = ROOT / "DATA" / "reference" / "tarot" / "knowledge_v1" / "cards.json"
SCHEMA = ROOT / "docs" / "schemas" / "tarot_knowledge_v1.schema.json"


def _card(cid: int, orientation: str, pid: str, title: str) -> models.TarotSpreadCard:
    return models.TarotSpreadCard(
        card=models.TarotCard(id=cid, name=f"Card {cid}", keywords=[], upright="", reversed=""),
        orientation=orientation,
        position=models.TarotSpreadPosition(id=pid, title=title, prompt=title),
        meaning="",
    )


def test_knowledge_base_covers_full_deck_and_schema():
    payload = json.loads(KB_JSON.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert len(tarot_kb.cards_by_id()) == 78
    fool = tarot_kb.get_card(0)
    assert fool is not None
    assert "неизвестн" in fool["central_archetype"]
    assert fool["domains"]["work"]
    assert "Аркан" not in json.dumps(payload, ensure_ascii=False)


def test_context_pack_uses_knowledge_base_fields():
    spread = models.TarotSpreadResult(
        spread_id="guidance_choice_two",
        title="Выбор",
        cards=[
            _card(18, "reversed", "a_gives", "Вариант A — что он даёт"),
            _card(15, "upright", "a_risk", "Вариант A — риск"),
            _card(14, "upright", "weights", "Что важно учитывать"),
            _card(0, "upright", "best_step", "Лучший следующий шаг"),
        ],
    )
    pack = engine.build_context_pack(
        spread,
        question="Стоит ли уходить из отношений?",
        concern_domain="relationships",
    )
    assert pack is not None
    moon = pack["cards"][0]["meaning_range"]
    assert moon["knowledge_source"] == "tarot_knowledge_v1"
    assert moon.get("inner_conflict")
    assert moon.get("outer_expression")
    assert moon.get("domain_lens", {}).get("domain") == "relationships"
    assert moon.get("reversed_trap")
    # Devil intensifies Moon; Temperance softens Devil — present in same spread.
    devil = pack["cards"][1]["meaning_range"]
    assert any("Луна" in n for n in devil.get("intensifies_drawn") or []) or any(
        "Умеренность" in n for n in devil.get("softens_drawn") or []
    )
    step = pack["cards"][3]["meaning_range"]
    assert step["central_symbol"]
    assert "Аркан" not in json.dumps(pack, ensure_ascii=False)


def test_minor_pack_not_just_suit_keyword():
    spread = models.TarotSpreadResult(
        spread_id="three_cards",
        title="Три",
        cards=[_card(52, "upright", "core", "Суть")],
    )
    pack = engine.build_context_pack(spread, question="Почему так больно?", concern_domain="relationships")
    assert pack is not None
    rng = pack["cards"][0]["meaning_range"]
    assert rng["knowledge_source"] == "tarot_knowledge_v1"
    blob = " ".join(
        str(rng.get(k) or "")
        for k in ("central_symbol", "core_scene", "central_conflict", "inner_conflict")
    ).lower()
    assert any(tok in blob for tok in ("боль", "разрез", "меч", "сердц")), blob
    assert rng.get("inner_conflict")
    assert rng.get("core_scene")
    assert rng.get("adjacent_distinction")


_Q1_FIELDS = (
    "core_scene",
    "central_conflict",
    "driving_need",
    "shadow_pattern",
    "growth_direction",
    "work_lens",
    "relationship_lens",
    "money_lens",
    "inner_lens",
    "reversed_shift",
    "adjacent_distinction",
)


def test_all_minors_have_q1_archetype_profile():
    cards = tarot_kb.cards_by_id()
    assert len(cards) == 78
    for cid in range(22, 78):
        row = cards[cid]
        for key in _Q1_FIELDS:
            assert str(row.get(key) or "").strip(), (cid, key)
        assert len(str(row["adjacent_distinction"]).strip()) >= 12


def test_adjacent_swords_and_cups_are_distinct_archetypes():
    """Gate: 8/9/10 of a suit must be three different human stories."""
    cards = tarot_kb.cards_by_id()
    # Swords 8/9/10 = 57/58/59; Cups 8/9/10 = 43/44/45
    for trio in ((57, 58, 59), (43, 44, 45)):
        scenes = [str(cards[i]["core_scene"]).strip().lower() for i in trio]
        centrals = [str(cards[i]["central_archetype"]).strip().lower() for i in trio]
        conflicts = [str(cards[i]["central_conflict"]).strip().lower() for i in trio]
        assert len(set(scenes)) == 3, scenes
        assert len(set(centrals)) == 3, centrals
        assert len(set(conflicts)) == 3, conflicts
        for i in trio:
            adj = str(cards[i]["adjacent_distinction"]).strip()
            assert len(adj) >= 12
            # Distinction text must not be identical to this card's own core_scene.
            assert adj.strip().lower() != str(cards[i]["core_scene"]).strip().lower()
