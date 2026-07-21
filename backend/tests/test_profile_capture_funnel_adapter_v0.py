"""Capture adapter around production funnel — no product logic changes."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from todayflow_backend.services.profile_capture_session_v0 import profile_capture_session
from todayflow_backend.services.profile_disclosure_funnel_v0 import _call_with_retry, _identity_ok


def test_call_with_retry_records_rejected_and_accepted_attempts(tmp_path: Path):
    bad = {"contract_version": "profile_funnel_identity_v0", "identity_core": "short"}
    good = {
        "contract_version": "profile_funnel_identity_v0",
        "identity_core": "Человек первого шага с достаточным текстом для валидатора.",
        "strengths": ["a", "b", "c"],
        "growth_zones": ["d", "e", "f"],
    }
    responses = [
        (bad, '{"bad":true}'),
        (good, '{"good":true}'),
    ]

    def fake_call(*_a: Any, **_k: Any):
        return responses.pop(0)

    with profile_capture_session(case_id="t-retry", out_dir=tmp_path) as sess:
        with (
            patch(
                "todayflow_backend.services.profile_disclosure_funnel_v0.get_prompt",
                return_value=("SYS", "v-test"),
            ),
            patch(
                "todayflow_backend.services.profile_disclosure_funnel_v0._call",
                side_effect=fake_call,
            ),
            patch(
                "todayflow_backend.services.profile_disclosure_funnel_v0.resolve_default_chat_model",
                return_value="mock-model",
            ),
        ):
            result, meta = _call_with_retry(
                prompt_id="profile.identity.v1",
                locale="ru",
                user_payload={"shared": {}},
                depth_level="normal",
                ok_fn=_identity_ok,
            )
        assert result == good
        assert meta["ok"] is True
        assert meta["attempts"] == 2
        attempts = sess.pack["steps"]["identity"]["attempts"]
        assert len(attempts) == 2
        assert attempts[0]["validation_result"]["ok"] is False
        assert attempts[0]["raw_response"] == '{"bad":true}'
        assert attempts[1]["validation_result"]["ok"] is True
        assert attempts[1]["system_prompt"] == "SYS"
