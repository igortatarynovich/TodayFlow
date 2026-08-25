"""1.3.120 Native C1 seed-leak retry — catch verbatim_seed_leak on Global, not after I0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    HARD_NATIVE_VALIDATE_MARKERS,
    is_hard_native_validate_error,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_PROMPT_VERSION,
    format_seed_leak_retry_feedback,
    normalize_native_scenario_llm_c1,
    project_native_for_seed_leak,
    validate_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_personalization_c33 import DEPTH_GENERAL
from todayflow_backend.services.day_scenario_v1 import find_verbatim_seed_leaks_v1
from todayflow_backend.services.native_c1_i0_generation_split_v1 import (
    GLOBAL_STAGE_INSTRUCTION_RU,
    PERSONAL_STAGE_INSTRUCTION_RU,
    enforce_global_only,
    orchestrate_i0_split_generation,
)
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "docs" / "today" / "NATIVE_C1_SEED_LEAK_RETRY_V1.md"

GEN1101_NGRAM = "вчерашний квадрат луны к сатурну оставил"
GEN1101_SETUP = (
    "Вчерашний квадрат луны к сатурну оставил тяжёлый тон, "
    "и хочется ответить коротко."
)


def test_seed_leak_canon_exists():
    assert CANON.is_file()
    text = CANON.read_text(encoding="utf-8")
    assert "verbatim_seed_leak" in text
    assert "1101" in text
    assert "not weaken" in text.lower() or "не ослабля" in text or "unchanged" in text


def test_prompt_version_c5_3():
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.5"
    assert "verbatim_seed_leak" in Path(
        ROOT / "backend" / "src" / "todayflow_backend" / "services" / "day_scenario_native_llm_c1.py"
    ).read_text(encoding="utf-8")


def test_cloned_setup_is_hard_on_native_validate():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    native["scenes"][0]["setup"] = GEN1101_SETUP
    native["scenes"][1]["setup"] = GEN1101_SETUP
    projected = project_native_for_seed_leak(native)
    leaks = find_verbatim_seed_leaks_v1(projected)
    assert any(GEN1101_NGRAM in str(e) for e in leaks)
    errors = validate_native_scenario_llm_c1(native)
    seed = [e for e in errors if str(e).startswith("verbatim_seed_leak:")]
    assert seed, errors
    assert all(is_hard_native_validate_error(e) for e in seed)
    assert "verbatim_seed_leak:" in HARD_NATIVE_VALIDATE_MARKERS


def test_distinct_setups_still_pass():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    errors = validate_native_scenario_llm_c1(native)
    assert not any(str(e).startswith("verbatim_seed_leak:") for e in errors)


def test_sky_fact_title_is_hard_on_native_validate():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    native["conflict"]["title"] = "Вчерашний квадрат Луны к Сатурну"
    errors = validate_native_scenario_llm_c1(native)
    assert "conflict_short_name_is_sky_fact" in errors
    assert is_hard_native_validate_error("conflict_short_name_is_sky_fact")


def test_retry_feedback_names_sky_fact_title():
    fb = format_seed_leak_retry_feedback(["conflict_short_name_is_sky_fact"])
    assert "conflict_short_name_is_sky_fact" in fb
    assert "SEED-KILL" in fb
    assert "title" in fb
    fb = format_seed_leak_retry_feedback(
        [f"verbatim_seed_leak:{GEN1101_NGRAM!r}@scenes[0].what_happens+scenes[1].what_happens"]
    )
    assert "verbatim_seed_leak" in fb
    assert "SEED-KILL" in fb
    assert "не копируй" in fb
    assert "не ослабляется" in fb


def test_global_retry_catches_cloned_setup_before_merge():
    calls: list[str] = []
    good = _valid_native_good()
    cloned = json.loads(json.dumps(good))
    cloned["scenes"][0]["setup"] = GEN1101_SETUP
    cloned["scenes"][1]["setup"] = GEN1101_SETUP

    def fake_llm(**kwargs: Any) -> tuple[str | None, str | None, str | None]:
        user = kwargs.get("user") or ""
        calls.append(user)
        payload = cloned if len(calls) == 1 else good
        return json.dumps(payload, ensure_ascii=False), None, "test-model"

    def process_global(parsed: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
        from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
            is_hard_native_validate_error,
        )

        norm = enforce_global_only(normalize_native_scenario_llm_c1(parsed))
        errors = validate_native_scenario_llm_c1(norm)
        hard = [e for e in errors if is_hard_native_validate_error(e)]
        if hard:
            return None, format_seed_leak_retry_feedback(hard)
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
    assert len(calls) == 2
    assert "SEED-KILL" in calls[1]
    assert attempts[-1].get("status") == "accepted_global"
