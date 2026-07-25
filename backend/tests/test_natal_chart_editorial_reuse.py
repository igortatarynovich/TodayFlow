"""Natal editorial should reuse last success instead of calling LLM every GET."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from todayflow_backend.services import natal_chart_editorial as editorial


def test_reuse_last_successful_editorial_returns_payload():
    db = MagicMock()
    prior_row = SimpleNamespace(
        id=99,
        core_profile_snapshot_id=11,
        normalized_response={
            "headline": "Сохранённый тезис карты",
            "summary": "Краткое summary.",
            "gifts": ["дар"],
            "tensions": ["напряжение"],
            "next_step": "шаг",
            "memory": {"chart_thesis": "тезис"},
        },
    )
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
        prior_row
    ]

    reused = editorial._reuse_last_successful_editorial(
        db, user_id=7, core_profile_snapshot_id=11
    )
    assert reused is not None
    assert reused["headline"] == "Сохранённый тезис карты"
    assert reused["reused"] is True
    assert reused["generation_log_id"] == 99


def test_generate_natal_chart_editorial_reuses_without_llm():
    db = MagicMock()
    user = SimpleNamespace(id=7)
    prior_row = SimpleNamespace(
        id=99,
        core_profile_snapshot_id=11,
        normalized_response={
            "headline": "Сохранённый тезис карты",
            "summary": "Краткое summary.",
            "gifts": ["дар"],
            "tensions": ["напряжение"],
            "next_step": "шаг",
            "memory": {
                "chart_thesis": "тезис",
                "dominant_house": "1",
                "dominant_planet": "Sun",
                "growth_theme": "рост",
            },
        },
    )
    snapshot = SimpleNamespace(id=11)

    learning = MagicMock()
    learning.build_user_learning_context.return_value = {}
    learning.get_or_create_prompt_version.return_value = SimpleNamespace(id=1)

    # Calls: prior_memory GenerationLog, CoreProfileSnapshot, reuse GenerationLog
    gen_q = MagicMock()
    gen_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [prior_row]
    snap_q = MagicMock()
    snap_q.filter.return_value.order_by.return_value.first.return_value = snapshot

    def query_side_effect(model):
        name = getattr(model, "__name__", str(model))
        if "CoreProfileSnapshot" in name:
            return snap_q
        return gen_q

    db.query.side_effect = query_side_effect

    with (
        patch.object(editorial, "get_learning_service", return_value=learning),
        patch.object(editorial, "chat_completion_text") as chat,
        patch.object(editorial, "is_llm_chat_configured", return_value=True),
    ):
        result = editorial.generate_natal_chart_editorial(
            db,
            user=user,
            core_profile={"baseline": {"archetype_seed": "seed"}},
            natal_summary=None,
            interpretations=None,
            aspects=None,
            locale="ru",
        )

    assert result["headline"] == "Сохранённый тезис карты"
    assert result.get("reused") is True
    chat.assert_not_called()
