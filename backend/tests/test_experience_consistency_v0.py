"""Experience Consistency Tests — public CI contract for Source of Interpretation.

Same personality fields must arrive identically in today / compatibility / tarot slices.
If assembler or allowlist drifts and decision_style diverges across Experiences, CI fails.
"""

from __future__ import annotations

from todayflow_backend.services.experience_contract_assembler_v0 import (
    CONSISTENCY_FIELDS,
    EXPERIENCE_ALLOWLISTS,
    PROVENANCE_FIELDS,
    assemble_experience_contract,
    assemble_experience_slice,
    project_experience_slice,
)
from todayflow_backend.services.tarot_answer_v1 import compose_tarot_answer_v1
from todayflow_backend.core import models as api_models


def _rich_snapshot() -> dict:
    return {
        "snapshot_id": 101,
        "profile_hash": "fp-consistency-101",
        "profile_version": "3",
        "is_ready": True,
        "missing_fields": [],
        "person": {"display_name": "Anna"},
        "astro": {"sun_sign": "Cancer"},
        "numerology": {"life_path": 9},
        "baseline": {"rhythm": "evening recovery", "element_focus": "water"},
        "living": {"summary": "Неделя про границы и мягкий темп."},
        "profile_contract_v1": {
            "identity_core": "Чувствует поле раньше слов",
            "decision_style": "Сверяется с телом, потом фиксирует выбор",
            "relationship_style": "Нужна ясность без давления",
            "communication_style": "Коротко и по делу, когда есть доверие",
            "life_mission": "Создавать безопасное пространство для роста",
            "helps": ["пауза", "честный разговор"],
            "strengths": ["эмпатия", "выдержка"],
        },
    }


def test_consistency_fields_identical_across_experiences():
    contract = assemble_experience_contract(_rich_snapshot())
    slices = {
        exp: project_experience_slice(contract, experience_id=exp)
        for exp in ("today", "compatibility", "tarot")
    }
    for field in CONSISTENCY_FIELDS:
        values = {exp: slices[exp].get(field) for exp in slices}
        assert len(set(map(repr, values.values()))) == 1, (
            f"{field} diverged across Experiences: {values}"
        )


def test_provenance_identical_across_experiences():
    contract = assemble_experience_contract(_rich_snapshot())
    slices = {
        exp: project_experience_slice(contract, experience_id=exp)
        for exp in ("today", "compatibility", "tarot")
    }
    for field in PROVENANCE_FIELDS:
        values = {exp: slices[exp].get(field) for exp in slices}
        assert len(set(map(repr, values.values()))) == 1, (
            f"provenance {field} diverged: {values}"
        )
    assert slices["today"]["profile_hash"] == "fp-consistency-101"
    assert slices["today"]["snapshot_id"] == 101
    assert slices["today"]["generated_from_snapshot"] is True


def test_shared_source_contract_fingerprint():
    contract = assemble_experience_contract(_rich_snapshot())
    fps = {
        project_experience_slice(contract, experience_id=exp).get(
            "source_contract_fingerprint"
        )
        for exp in ("today", "compatibility", "tarot")
    }
    assert fps == {contract["contract_fingerprint"]}


def test_allowlist_enforced_no_extra_contract_fields():
    contract = assemble_experience_contract(_rich_snapshot())
    contract["attachment_style"] = "anxious"  # future field — must not leak
    for exp, allow in EXPERIENCE_ALLOWLISTS.items():
        sl = project_experience_slice(contract, experience_id=exp)
        assert "attachment_style" not in sl
        for key in sl:
            if key in (
                "experience_id",
                "contract_version",
                "source_contract_fingerprint",
                "experience_slice_fingerprint",
            ):
                continue
            assert key in allow, f"{exp} slice leaked {key}"


def test_tarot_synthesis_uses_experience_slice():
    snap = _rich_snapshot()
    tarot_slice = assemble_experience_slice(snap, experience_id="tarot")
    spread = api_models.TarotSpreadResult(
        spread_id="three_card",
        title="Три карты",
        cards=[
            api_models.TarotSpreadCard(
                card=api_models.TarotCard(
                    id=0,
                    name="The Fool",
                    keywords=["начало"],
                    upright="начало пути",
                    reversed="осторожность",
                ),
                orientation="upright",
                position=api_models.TarotSpreadPosition(id="past", title="Прошлое"),
                meaning="",
            )
        ],
    )
    reading_with, _ = compose_tarot_answer_v1(
        spread,
        question="Что важно увидеть?",
        experience_slice=tarot_slice,
    )
    reading_without, _ = compose_tarot_answer_v1(
        spread,
        question="Что важно увидеть?",
        experience_slice=None,
    )
    assert reading_with.profile_lens_applied is True
    assert reading_with.profile_lens == tarot_slice["decision_style"]
    assert reading_without.profile_lens_applied is False
    assert reading_with.insight_attention != reading_without.insight_attention
