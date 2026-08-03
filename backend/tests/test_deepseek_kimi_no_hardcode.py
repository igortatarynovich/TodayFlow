"""Kimi primary → DeepSeek fallback; attempt1 Kimi-only; no B5 invent after LLM fail."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

from todayflow_backend.services.day_scenario_native_llm_c1 import (
    ATTEMPT2_POLICY_TIMEOUT,
    call_day_scenario_native_llm_c1,
    resolve_native_attempt_model,
)
from todayflow_backend.services.day_story_v1 import DAY_STORY_V1_CONTRACT
from todayflow_backend.services.day_story_wire_v1 import (
    _load_prior_native_day_story_same_date,
    _mark_kept_prior_native,
)


def test_resolve_native_attempt_model_always_primary(monkeypatch) -> None:
    with patch(
        "todayflow_backend.services.day_scenario_native_llm_c1.resolve_default_chat_model",
        return_value="moonshotai/Kimi-K3",
    ):
        assert resolve_native_attempt_model(0) == "moonshotai/Kimi-K3"
        assert resolve_native_attempt_model(1) == "moonshotai/Kimi-K3"


def test_attempt1_kimi_only_no_deepseek_fallback(monkeypatch) -> None:
    meta: dict[str, Any] = {}
    models: list[str] = []
    fallback_flags: list[bool] = []

    def _chat(_client, *, model, messages, allow_model_fallback=True, **_kwargs):
        models.append(str(model))
        fallback_flags.append(bool(allow_model_fallback))
        if len(models) == 1:
            return ("{not-json", None, model)
        return (None, "empty", model)

    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=MagicMock(),
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_default_chat_model",
            return_value="moonshotai/Kimi-K3",
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.chat_completion_plain_with_status",
            side_effect=_chat,
        ),
        patch(
            "todayflow_backend.services.day_story_capture_session_v0.get_day_story_capture_session",
            return_value=None,
        ),
    ):
        result = call_day_scenario_native_llm_c1(
            {"interpretation": {}},
            interpretation={},
            max_attempts=2,
            meta_out=meta,
        )

    assert result is None
    assert models == [
        "moonshotai/Kimi-K3",
        "moonshotai/Kimi-K3",
    ]
    assert fallback_flags == [True, False]
    assert meta.get("attempt2_policy") == ATTEMPT2_POLICY_TIMEOUT


def test_mark_kept_prior_native_sets_refresh_flags() -> None:
    out = _mark_kept_prior_native({"expect": "kept text", "editorial": {"runtime_source": "x"}})
    assert out["expect"] == "kept text"
    assert out["editorial"]["kept_prior_native"] is True
    assert out["editorial"]["story_refresh_required"] is True
    assert out["editorial"]["runtime_source"] == "kept_prior_native"


def test_load_prior_native_same_date_skips_other_dates_and_fallback() -> None:
    today = date(2026, 8, 3)
    good = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "interpretation_status": "ok",
        "day_scenario": {"ready": True, "scenes": [{"id": "s1"}], "generation_source": "native_llm_c1"},
        "expect": "живой текст дня",
        "do": ["a", "b"],
    }
    rows = [
        SimpleNamespace(
            id=10,
            input_payload={
                "target_date": "2026-08-02",
                "generation_source": "native_llm_c1",
            },
            normalized_response=good,
        ),
        SimpleNamespace(
            id=11,
            input_payload={
                "target_date": today.isoformat(),
                "generation_source": "unavailable_after_llm",
            },
            normalized_response=good,
        ),
        SimpleNamespace(
            id=12,
            input_payload={
                "target_date": today.isoformat(),
                "generation_source": "native_llm_c1",
            },
            normalized_response=good,
        ),
    ]
    q = MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.limit.return_value = rows
    db = MagicMock()
    db.query.return_value = q

    hit = _load_prior_native_day_story_same_date(db, user_id=1, target_date=today)
    assert hit is not None
    story, gen_id = hit
    assert gen_id == 12
    assert story["expect"] == "живой текст дня"


def test_unavailable_project_strips_b5_action_templates() -> None:
    from todayflow_backend.services.day_scenario_project_v1 import (
        project_day_scenario_onto_day_story_v1,
    )

    shell = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": "t",
        "expect": "Сделай один короткий шаг в сторону поворота — по делу, без оправданий.",
        "do": ["Сделай один короткий шаг в сторону поворота — по делу, без оправданий.", "x"],
        "trap": "y",
        "direction": "d",
        "advantage": "a",
        "abstain": "b",
        "today_move": "m",
        "global_period": "g",
        "story": "s",
        "avoid": ["1", "2"],
        "domains": {},
        "day_thesis": {"label_ru": "Тезис"},
    }
    out = project_day_scenario_onto_day_story_v1(shell, None)
    assert out["interpretation_status"] == "unavailable"
    assert out["expect"] == ""
    assert out["do"] == []
    assert "Сделай один короткий шаг" not in str(out.get("expect") or "")
    assert "Сделай один короткий шаг" not in str(out.get("do") or "")
