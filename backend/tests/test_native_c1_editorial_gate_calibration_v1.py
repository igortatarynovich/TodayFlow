"""1.3.117 Native C1 editorial gate calibration — retry feedback + regression matrix."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_ASTRO_JARGON_BARE,
    DEFECT_SCENE_ABSTRACT,
    DEFECT_SCENE_MISSING_EVERYDAY,
    format_editorial_retry_feedback,
    run_editorial_quality_gate_c31,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_PROMPT_VERSION,
    normalize_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
)
from todayflow_backend.services.native_c1_i0_generation_split_v1 import (
    GLOBAL_STAGE_INSTRUCTION_RU,
    PERSONAL_STAGE_INSTRUCTION_RU,
    enforce_global_only,
    orchestrate_i0_split_generation,
)
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good
from tests.test_native_c1_i0_generation_split_v1 import _global_native

ROOT = Path(__file__).resolve().parents[2]
CALIB_CANON = ROOT / "docs" / "today" / "NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md"


def _global_from_good() -> dict[str, Any]:
    return normalize_native_scenario_llm_c1(_valid_native_good())


def test_calibration_canon_exists():
    assert CALIB_CANON.is_file()
    assert "SCENE_MISSING_EVERYDAY" in CALIB_CANON.read_text(encoding="utf-8")


def test_prompt_version_c5_1():
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.1"


def test_retry_feedback_targets_everyday_and_astro_codes():
    defects = [
        {
            "code": DEFECT_SCENE_MISSING_EVERYDAY,
            "field": "scenes[0]",
            "message": "everyday_example missing",
        },
        {
            "code": DEFECT_ASTRO_JARGON_BARE,
            "field": "chorus.astrology[0]",
            "message": "astro term without human translation",
        },
    ]
    fb = format_editorial_retry_feedback(defects)
    assert "everyday_example" in fb
    assert "astrology voice" in fb
    assert DEFECT_SCENE_MISSING_EVERYDAY in fb


def test_regression_matrix_general_light_deep_pass_gate():
    native = _global_from_good()
    for depth in (DEPTH_GENERAL, DEPTH_LIGHT, DEPTH_DEEP):
        native["personalization_depth"] = depth
        defects = run_editorial_quality_gate_c31(native, has_natal_evidence=depth == DEPTH_DEEP)
        blocking = [
            d
            for d in defects
            if str(d.get("runtime_action")) == "retry"
            or d.get("code") in {
                DEFECT_SCENE_MISSING_EVERYDAY,
                DEFECT_SCENE_ABSTRACT,
                DEFECT_ASTRO_JARGON_BARE,
            }
        ]
        assert blocking == [], (depth, defects)


def test_orchestrate_gate_retry_passes_editorial_feedback_to_second_attempt():
    calls: list[str] = []
    bad = _global_from_good()
    bad["scenes"][0]["everyday_example"] = "Слушайте себя и сохраняйте баланс."

    def fake_llm(**kwargs: Any) -> tuple[str | None, str | None, str | None]:
        user = kwargs.get("user") or ""
        calls.append(user)
        payload = bad if len(calls) == 1 else _global_from_good()
        return json.dumps(payload, ensure_ascii=False), None, "test-model"

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
        max_attempts=2,
        llm_call=lambda **kw: fake_llm(**kw),
        resolve_attempt_model=lambda i: "test-model",
        process_global_normalized=process_global,
        meta_out=None,
    )
    assert merged is not None
    assert len(calls) == 2
    assert "everyday_example" in calls[1] or DEFECT_SCENE_MISSING_EVERYDAY in calls[1]
    assert attempts[-1].get("status") == "accepted_global"


def test_personal_degraded_keeps_global():
    calls: list[str] = []

    def fake_llm(**kwargs: Any) -> tuple[str | None, str | None, str | None]:
        system = kwargs.get("system", "")
        calls.append("personal" if PERSONAL_STAGE_INSTRUCTION_RU in system else "global")
        if "global" in calls[-1]:
            return json.dumps(_global_native(), ensure_ascii=False), None, "m"
        return None, "timeout", None

    def accept_global(parsed: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
        return enforce_global_only(normalize_native_scenario_llm_c1(parsed)), None

    merged, _, split_meta = orchestrate_i0_split_generation(
        global_system=GLOBAL_STAGE_INSTRUCTION_RU,
        personal_system=PERSONAL_STAGE_INSTRUCTION_RU,
        user_base="DRAMATURGY",
        pers_pack={"evidence_depth": DEPTH_DEEP},
        il4_pack=None,
        allowed_evidence_ids=set(),
        max_attempts=2,
        llm_call=lambda **kw: fake_llm(**kw),
        resolve_attempt_model=lambda i: "m",
        process_global_normalized=accept_global,
        meta_out=None,
    )
    assert split_meta.get("personal_degraded")
    assert merged is not None
    assert merged["conflict"]["title"] == "Прояснение против сглаживания"
    assert merged["interpretive_chorus"]["natal"] == []
