"""P0: no second native attempt after provider timeout."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

from todayflow_backend.services.day_scenario_native_llm_c1 import (
    ATTEMPT2_POLICY_TIMEOUT,
    NATIVE_FAILURE_TIMEOUT,
    call_day_scenario_native_llm_c1,
)


def test_native_llm_no_retry_on_timeout_fills_meta() -> None:
    meta: dict[str, Any] = {}
    client = MagicMock()

    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=client,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_default_chat_model",
            return_value="test-model",
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.chat_completion_plain_with_status",
            return_value=(None, "timeout", "test-model"),
        ) as plain,
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
    assert plain.call_count == 1
    assert meta.get("failure_class") == NATIVE_FAILURE_TIMEOUT
    assert meta.get("attempt_count") == 1
    assert meta.get("no_retry_on_timeout") is True
    assert meta.get("attempt2_policy") == ATTEMPT2_POLICY_TIMEOUT
    assert meta.get("model") == "test-model"
