"""1.3.121 Native C1 astro jargon retry — don't trade ASTRO_JARGON_BARE for why_today paste."""

from __future__ import annotations

from pathlib import Path

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_ASTRO_JARGON_BARE,
    SEED_JARGON_CROSS_HINT_RU,
    format_editorial_retry_feedback,
    run_editorial_quality_gate_c31,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_PROMPT_VERSION,
    format_seed_leak_retry_feedback,
    normalize_native_scenario_llm_c1,
)
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "docs" / "today" / "NATIVE_C1_ASTRO_JARGON_RETRY_V1.md"


def test_astro_jargon_retry_canon_exists():
    assert CANON.is_file()
    text = CANON.read_text(encoding="utf-8")
    assert "ASTRO_JARGON_BARE" in text
    assert "1117" in text
    assert "why_today" in text


def test_prompt_version_c5_4():
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.4"
    src = (
        ROOT
        / "backend"
        / "src"
        / "todayflow_backend"
        / "services"
        / "day_scenario_native_llm_c1.py"
    ).read_text(encoding="utf-8")
    assert "каждый interpretive_chorus.astrology[i]" in src


def test_jargon_retry_covers_all_astrology_rows_and_seed_kill():
    fb = format_editorial_retry_feedback(
        [
            {
                "code": DEFECT_ASTRO_JARGON_BARE,
                "field": "chorus.astrology[1]",
                "message": "astro term without human translation",
            }
        ]
    )
    assert "astrology[i]" in fb
    assert "why_today" in fb
    assert "verbatim_seed_leak" in fb
    assert SEED_JARGON_CROSS_HINT_RU in fb


def test_seed_leak_retry_forbids_jargon_rollback():
    fb = format_seed_leak_retry_feedback(
        [
            "verbatim_seed_leak:'ощущение недостаточности как будто что-то не'"
            "@chorus.astrology[1].human_meaning+conflict.why_arose"
        ]
    )
    assert "why_today" in fb
    assert "human_meaning" in fb
    assert "ASTRO_JARGON_BARE" in fb
    assert SEED_JARGON_CROSS_HINT_RU in fb


def test_untranslated_astrology_row_still_blocked():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    native["interpretive_chorus"]["astrology"].append(
        {
            "named_factor": "Квадрат Луны к Сатурну",
            "human_meaning": "Луна квадрат Сатурн.",
            "link_to_conflict": "Аспект Сатурна.",
            "evidence_refs": ["moon-pisces"],
        }
    )
    defects = run_editorial_quality_gate_c31(native, has_natal_evidence=False)
    codes = {str(d.get("code")) for d in defects}
    assert DEFECT_ASTRO_JARGON_BARE in codes
