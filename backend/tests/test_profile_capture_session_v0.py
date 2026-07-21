"""Unit tests for Profile capture session (no LLM)."""

from __future__ import annotations

import json
from pathlib import Path

from todayflow_backend.services.profile_capture_session_v0 import (
    get_profile_capture_session,
    profile_capture_enabled,
    profile_capture_session,
)


def test_capture_off_by_default():
    assert profile_capture_enabled() is False
    assert get_profile_capture_session() is None


def test_capture_session_records_steps_and_invariant(tmp_path: Path):
    with profile_capture_session(
        case_id="pq-001",
        label="birth-only",
        redact=False,
        out_dir=tmp_path,
    ) as sess:
        assert profile_capture_enabled() is True
        sess.set_inputs(
            inputs={"person": {"first_name": "Аня"}, "living": None},
            calculated_facts={"astro": {"sun_sign": "aries"}},
            source_depth="birth_data_only",
            missing_fields=["birth_time", "checkins"],
            allowed_claims={"recurring_patterns": False},
        )
        sess.record_step_attempt(
            "identity",
            prompt_id="profile.identity.v1",
            prompt_version="t",
            system_prompt="SYS",
            user_prompt='{"shared":{}}',
            model_request={"model": "x", "temperature": 0.48},
            raw_response='{"identity_core":"Человек первого шага — длинный текст."}',
            parsed_response={"identity_core": "Человек первого шага — длинный текст."},
            validation_result={"ok": True, "validator": "_identity_ok"},
            attempt_index=1,
            ms=10,
        )
        sess.record_step_attempt(
            "patterns",
            prompt_id="profile.patterns.v1",
            prompt_version="t",
            system_prompt="SYS-PAT",
            user_prompt='{"shared":{}}',
            model_request={"model": "x", "temperature": 0.48},
            raw_response='{"recurring_patterns":["Регулярно бросает начатое"]}',
            parsed_response={
                "recurring_patterns": ["Регулярно бросает начатое без внешнего каркаса."],
            },
            validation_result={"ok": True, "validator": "_patterns_ok"},
            attempt_index=1,
            ms=10,
        )
        sess.record_quality(
            before={
                "identity_core": "Человек первого шага — длинный текст.",
                "decision_style": "Быстро принимает решения, если есть ясный первый ход.",
                "recurring_patterns": ["Регулярно бросает начатое без внешнего каркаса."],
            },
            validation={"ok": True},
            after={
                "identity_core": "Человек первого шага — длинный текст.",
                "decision_style": "Быстро принимает решения, если есть ясный первый ход.",
                "recurring_patterns": ["Регулярно бросает начатое без внешнего каркаса."],
            },
            forming_fallback=False,
        )
        path = sess.write()
        assert path is not None
        pack = json.loads(path.read_text(encoding="utf-8"))
        assert pack["manifest"]["case_id"] == "pq-001"
        assert pack["source_depth"] == "birth_data_only"
        assert len(pack["steps"]["identity"]["attempts"]) == 1
        assert pack["steps"]["identity"]["attempts"][0]["raw_response"]
        codes = {d["code"] for d in pack["defects"]}
        assert "invariant_birth_only_confirmed_patterns" in codes
        assert all(d["class"] != "MODEL" for d in pack["defects"])
        assert any(d["class"] == "GENERATION_GATE" for d in pack["defects"])
        assert pack["block_eligibility"]["patterns"]["may_generate"] is False
        assert pack["block_eligibility"]["patterns"]["ran"] is True
        assert any(r["origin"] == "patterns LLM" for r in pack["claim_trace"])

    assert profile_capture_enabled() is False


def test_redaction_scrubs_name_and_date(tmp_path: Path):
    with profile_capture_session(
        case_id="pq-x",
        redact=True,
        out_dir=tmp_path,
    ) as sess:
        sess.set_inputs(
            inputs={
                "person": {"first_name": "Аня", "birth_date": "1991-04-12"},
                "note": "born 1991-04-12",
            },
            source_depth="birth_data_only",
        )
        sess.write()
        packs = list(tmp_path.glob("capture_*.json"))
        assert packs
        pack = json.loads(packs[0].read_text(encoding="utf-8"))
        person = pack["inputs"]["person"]
        assert person["first_name"] == "[redacted]"
        assert person["birth_date"] == "[redacted]"
        assert "[date]" in pack["inputs"]["note"]
