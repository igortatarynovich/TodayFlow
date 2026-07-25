"""C3.2 chorus quality — causal chain, not four parallel forecasts."""

from __future__ import annotations

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
    DEFECT_CHORUS_PARALLEL_FORECAST,
    DEFECT_CHORUS_ROLE_DRIFT,
    DEFECT_CHORUS_SEMANTIC_DUPLICATION,
    DEFECT_CHORUS_UNTRANSLATED_JARGON,
    conflict_anchor_id,
    editorial_has_critical,
    format_editorial_retry_feedback,
    run_editorial_quality_gate_c31,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import normalize_native_scenario_llm_c1
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good


def test_good_chorus_passes_c32_gate():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    defects = run_editorial_quality_gate_c31(native, has_natal_evidence=True)
    critical = [d for d in defects if editorial_has_critical([d])]
    assert critical == [], defects
    # conflict_id filled by normalize
    astro = native["interpretive_chorus"]["astrology"][0]
    assert astro.get("conflict_id") == conflict_anchor_id(native["conflict"])


def test_parallel_forecast_rejected():
    native = _valid_native_good()
    native["interpretive_chorus"]["astrology"][0]["human_meaning"] = (
        "Сегодня вас ждёт удача в работе; день благоприятен для сделок."
    )
    native["interpretive_chorus"]["astrology"][0]["link_to_conflict"] = (
        "Астрология обещает отдельный прогноз по карьере."
    )
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_CHORUS_PARALLEL_FORECAST for d in defects)
    assert editorial_has_critical(defects)


def test_semantic_duplication_rejected():
    native = _valid_native_good()
    shared = (
        "Сегодня важнее назвать точно, чем сгладить; пауза перед ответом помогает "
        "пройти прояснение против сглаживания без спешки."
    )
    native["interpretive_chorus"]["astrology"][0]["human_meaning"] = shared
    native["interpretive_chorus"]["astrology"][0]["link_to_conflict"] = shared
    native["interpretive_chorus"]["day_card"]["archetype_role"] = shared
    native["interpretive_chorus"]["day_card"]["link_to_conflict"] = shared
    native["interpretive_chorus"]["day_number"]["tempo"] = "сначала"
    native["interpretive_chorus"]["day_number"]["style"] = "ритм"
    native["interpretive_chorus"]["day_number"]["link_to_conflict"] = shared
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_CHORUS_SEMANTIC_DUPLICATION for d in defects)


def test_role_drift_day_card_as_environment_rejected():
    native = _valid_native_good()
    native["interpretive_chorus"]["day_card"] = {
        "named_factor": "Карта дня",
        "archetype_role": "",
        "link_to_conflict": "Атмосфера дня становится мягче, внешний фон тише.",
        "evidence_refs": ["day_card"],
    }
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_CHORUS_ROLE_DRIFT for d in defects)


def test_untranslated_jargon_rejected():
    native = _valid_native_good()
    native["interpretive_chorus"]["astrology"] = [
        {
            "named_factor": "Луна в Рыбах в квадрате к Марсу",
            "human_meaning": "Квадрат. Трины. Ретроград.",
            "link_to_conflict": "Аспект дня.",
            "evidence_refs": ["moon-pisces"],
        }
    ]
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_CHORUS_UNTRANSLATED_JARGON for d in defects)


def test_natal_without_evidence_rejected():
    native = _valid_native_good()
    native["interpretive_chorus"]["natal"] = [
        {
            "named_factor": "Марс в 7 доме",
            "human_meaning": "Вам привычно резко требовать ясности в близких.",
            "link_to_conflict": "Ваша уязвимость — давление вместо короткого ответа.",
            "evidence_refs": [],
        }
    ]
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=False
    )
    assert any(d["code"] == DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE for d in defects)
    assert editorial_has_critical(defects)


def test_retry_feedback_mentions_chorus_chain():
    native = _valid_native_good()
    native["interpretive_chorus"]["astrology"][0]["human_meaning"] = "День благоприятен."
    native["interpretive_chorus"]["astrology"][0]["link_to_conflict"] = (
        "Сегодня вас ждёт отдельный прогноз."
    )
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    fb = format_editorial_retry_feedback(defects)
    assert "причинная линия" in fb or "C3.2" in fb
    assert "CHORUS_" in fb or "conflict_id" in fb
