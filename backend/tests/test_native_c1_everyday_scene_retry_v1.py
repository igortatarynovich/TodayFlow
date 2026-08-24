"""1.3.119 Native C1 everyday scene retry — all scenes must keep lived markers."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_SCENE_ABSTRACT,
    DEFECT_SCENE_MISSING_EVERYDAY,
    format_editorial_retry_feedback,
    run_editorial_quality_gate_c31,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_PROMPT_VERSION,
    _NATIVE_SYS_RU,
    call_day_scenario_native_llm_c1,
    normalize_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_personalization_c33 import DEPTH_GENERAL
from todayflow_backend.services.native_c1_i0_generation_split_v1 import (
    GLOBAL_STAGE_INSTRUCTION_RU,
    PERSONAL_STAGE_INSTRUCTION_RU,
    enforce_global_only,
    orchestrate_i0_split_generation,
)
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "docs" / "today" / "NATIVE_C1_EVERYDAY_SCENE_RETRY_V1.md"


def test_everyday_retry_canon_exists():
    assert CANON.is_file()
    text = CANON.read_text(encoding="utf-8")
    assert "SCENE_MISSING_EVERYDAY" in text
    assert "detectors unchanged" in text or "detector weakening" in text


def test_prompt_version_c5_2():
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.2"
    assert inspect.signature(call_day_scenario_native_llm_c1).parameters["max_attempts"].default == 3
    assert "ЧЧ:ММ" in _NATIVE_SYS_RU
    assert "Не чини одну сцену" in _NATIVE_SYS_RU


def test_thin_everyday_still_blocked():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    native["scenes"][0]["everyday_example"] = "Слушайте себя и сохраняйте баланс сегодня."
    defects = run_editorial_quality_gate_c31(native, has_natal_evidence=False)
    codes = {str(d.get("code")) for d in defects}
    assert DEFECT_SCENE_MISSING_EVERYDAY in codes


def test_retry_feedback_forbids_whack_a_mole():
    fb = format_editorial_retry_feedback(
        [
            {
                "code": DEFECT_SCENE_MISSING_EVERYDAY,
                "field": "scenes[0]",
                "message": "everyday_example too thin",
            },
            {
                "code": DEFECT_SCENE_ABSTRACT,
                "field": "scenes[0]",
                "message": "lacks lived moment",
            },
        ]
    )
    assert "КАЖДОЙ сцене" in fb
    assert "не укорачивай" in fb
    assert "ЧЧ:ММ" in fb or "12" in fb


def test_three_global_attempts_cover_whack_a_mole():
    """Prod gen 1104: attempt 0 scene[0] fail, attempt 1 scene[1] fail — need attempt 2."""
    calls: list[str] = []
    good = _valid_native_good()
    thin = "Слушайте себя и сохраняйте баланс сегодня."

    def payload_for_call(n: int) -> dict[str, Any]:
        native = json.loads(json.dumps(good))
        if n == 1:
            native["scenes"][0]["everyday_example"] = thin
        elif n == 2:
            native["scenes"][1]["everyday_example"] = thin
        return native

    def fake_llm(**kwargs: Any) -> tuple[str | None, str | None, str | None]:
        user = kwargs.get("user") or ""
        calls.append(user)
        return json.dumps(payload_for_call(len(calls)), ensure_ascii=False), None, "test-model"

    def process_global(parsed: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
        from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
            annotate_defects_with_maturity,
            should_reject_story,
            should_retry_defects,
        )

        norm = enforce_global_only(normalize_native_scenario_llm_c1(parsed))
        editorial = annotate_defects_with_maturity(
            run_editorial_quality_gate_c31(norm, has_natal_evidence=False)
        )
        if should_reject_story(editorial):
            return None, "hard_reject"
        if should_retry_defects(editorial):
            retryable = [d for d in editorial if str(d.get("runtime_action")) == "retry"]
            return None, format_editorial_retry_feedback(retryable)
        return norm, None

    merged, attempts, _ = orchestrate_i0_split_generation(
        global_system=GLOBAL_STAGE_INSTRUCTION_RU,
        personal_system=PERSONAL_STAGE_INSTRUCTION_RU,
        user_base="DRAMATURGY",
        pers_pack={"evidence_depth": DEPTH_GENERAL},
        il4_pack=None,
        allowed_evidence_ids=set(),
        max_attempts=3,
        llm_call=lambda **kw: fake_llm(**kw),
        resolve_attempt_model=lambda i: "test-model",
        process_global_normalized=process_global,
        meta_out=None,
    )
    assert merged is not None
    assert len(calls) == 3
    assert "не укорачивай" in calls[1]
    assert "не укорачивай" in calls[2]
    assert attempts[-1].get("status") == "accepted_global"
