"""P5 first slice — question registry + ContextPack builder."""

from __future__ import annotations

from todayflow_backend.context_engine_v0 import (
    CONTEXT_ENGINE_VERSION,
    build_context_pack_for_sphere,
    build_context_pack_v0,
    list_question_ids,
    question_id_for_sphere,
)
from todayflow_backend.context_engine_v0.fingerprint_v0 import context_pack_fingerprint


def _foundations(*, houses: bool = False) -> dict:
    natal = {
        "sun_sign": "Leo",
        "venus_sign": "Cancer",
        "jupiter_sign": "Cancer",
        "saturn_sign": "Capricorn",
        "mercury_sign": "Leo",
        "houses_available": houses,
        "houses": {
            "7": {"theme": "Партнёрство через ясный обмен и взаимность шага."},
        }
        if houses
        else {},
    }
    return {
        "locale": "ru",
        "identity": {
            "identity_core": "Держит смысл через тёплый контакт и ясную заботу о близких.",
            "strengths": ["Забота", "Ясность", "Верность"],
            "growth_zones": ["Слияние", "Обида", "Мягкое нет"],
        },
        "styles": {
            "relationship_style": "Близость через тёплые слова и предсказуемый темп без давления.",
            "money_style": "Деньги как спокойная безопасность и малые регулярные шаги.",
            "decision_style": "Решения через один свой критерий и короткий дедлайн.",
        },
        "natal": natal,
    }


def test_question_registry_covers_three_profile_questions() -> None:
    ids = list_question_ids()
    assert ids == ["q.decisions.v1", "q.money.v1", "q.relationships.v1"]
    assert question_id_for_sphere("love") == "q.relationships.v1"
    assert question_id_for_sphere("money") == "q.money.v1"
    assert question_id_for_sphere("decisions") == "q.decisions.v1"


def test_context_pack_for_relationships() -> None:
    pack = build_context_pack_v0("q.relationships.v1", _foundations())
    assert pack["ok"] is True
    assert pack["question_id"] == "q.relationships.v1"
    assert pack["domain"] == "relationships"
    assert pack["sphere_id"] == "love"
    assert pack["context_version"] == CONTEXT_ENGINE_VERSION
    assert pack["cues"]
    assert "profile.style.relationship" in pack["fact_ids"]
    assert any(f.startswith("natal.venus") for f in pack["fact_ids"])
    assert pack["fingerprint"]
    # no houses without time
    assert pack["house_cues"] == []
    assert any(o["id"] == "natal.house.7" for o in pack["omitted_facts"])


def test_house_cues_only_when_available() -> None:
    pack = build_context_pack_v0("q.relationships.v1", _foundations(houses=True))
    assert pack["ok"] is True
    assert pack["house_cues"]
    assert "natal.house.7" in pack["fact_ids"]


def test_fingerprint_stable() -> None:
    f = _foundations()
    a = build_context_pack_v0("q.money.v1", f)
    b = build_context_pack_v0("q.money.v1", f)
    assert a["fingerprint"] == b["fingerprint"]
    assert a["fingerprint"] == context_pack_fingerprint(a)


def test_sphere_adapter() -> None:
    pack = build_context_pack_for_sphere("decisions", _foundations())
    assert pack["ok"] is True
    assert pack["question_id"] == "q.decisions.v1"
