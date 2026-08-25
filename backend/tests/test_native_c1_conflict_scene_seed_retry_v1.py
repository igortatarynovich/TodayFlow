"""1.3.122 Native C1 conflict→scene seed retry — name why_today paste into scene.why."""

from __future__ import annotations

from pathlib import Path

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_ASTRO_JARGON_BARE,
    SEED_JARGON_CROSS_HINT_RU,
    format_editorial_retry_feedback,
)
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    is_hard_native_validate_error,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_PROMPT_VERSION,
    format_seed_leak_retry_feedback,
    normalize_native_scenario_llm_c1,
    project_native_for_seed_leak,
    validate_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_v1 import find_verbatim_seed_leaks_v1
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "docs" / "today" / "NATIVE_C1_CONFLICT_SCENE_SEED_RETRY_V1.md"

GEN1119_NGRAM = "утром уходит в водолей эмоции становятся"
GEN1119_WHY = (
    "Утром уходит в Водолей, эмоции становятся резче, чем хочется признать вслух."
)


def test_conflict_scene_seed_retry_canon_exists():
    assert CANON.is_file()
    text = CANON.read_text(encoding="utf-8")
    assert "1119" in text
    assert "why_arose" in text
    assert "ASTRO_JARGON_BARE" in text
    assert "not weaken" in text.lower() or "не ослабля" in text or "unchanged" in text


def test_prompt_version_c5_5():
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.5"
    src = (
        ROOT
        / "backend"
        / "src"
        / "todayflow_backend"
        / "services"
        / "day_scenario_native_llm_c1.py"
    ).read_text(encoding="utf-8")
    assert "prod gen 1119" in src
    assert "why_sphere / setup" in src


def test_why_today_pasted_into_scene_why_is_hard():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    native["conflict"]["why_today"] = GEN1119_WHY
    native["scenes"][0]["why_sphere"] = GEN1119_WHY
    projected = project_native_for_seed_leak(native)
    leaks = find_verbatim_seed_leaks_v1(projected)
    assert any(GEN1119_NGRAM in str(e) for e in leaks), leaks
    assert any("conflict.why_arose" in str(e) and "scenes[0].why" in str(e) for e in leaks)
    errors = validate_native_scenario_llm_c1(native)
    seed = [e for e in errors if str(e).startswith("verbatim_seed_leak:")]
    assert seed, errors
    assert all(is_hard_native_validate_error(e) for e in seed)


def test_seed_leak_retry_names_conflict_why_into_scene_why():
    fb = format_seed_leak_retry_feedback(
        [
            f"verbatim_seed_leak:{GEN1119_NGRAM!r}"
            "@conflict.why_arose+scenes[0].why"
        ]
    )
    assert "verbatim_seed_leak" in fb
    assert "why_today" in fb
    assert "why_arose" in fb
    assert "scenes[].why" in fb
    assert "why_sphere" in fb
    assert SEED_JARGON_CROSS_HINT_RU in fb
    assert "1119" in fb
    assert "не ослабляется" in fb


def test_jargon_retry_still_forbids_conflict_scene_leak_rollback():
    fb = format_editorial_retry_feedback(
        [
            {
                "code": DEFECT_ASTRO_JARGON_BARE,
                "field": "chorus.astrology[2]",
                "message": "astro term without human translation",
            }
        ]
    )
    assert "astrology[i]" in fb
    assert "why_sphere" in fb
    assert "1119" in fb
    assert SEED_JARGON_CROSS_HINT_RU in fb
