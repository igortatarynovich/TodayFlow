"""C3.6 — Integration/regression: native LLM orchestration uses maturity policy only.

Proves there is no parallel CRITICAL → retry/downgrade/unavailable path.
LLM is mocked; analyzers + maturity policy run for real.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any
from unittest.mock import patch

from todayflow_backend.services.day_scenario_editorial_gate_c31 import CRITICAL_DEFECTS
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    FAMILY_QUALITY,
    GATE_RULES,
    GateRule,
    MATURITY_CANDIDATE_BLOCKING,
    annotate_defects_with_maturity,
    non_blocking_maturities,
    runtime_action_for_rule,
    should_downgrade_general,
    should_reject_story,
    should_retry_defects,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import call_day_scenario_native_llm_c1
from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEFECT_CLAIM_WITHOUT_EVIDENCE,
    DEFECT_PROFILE_FACT_LEAK,
    personalization_decision_after_retries,
    personalization_requires_retry,
)
from todayflow_backend.services.day_story_capture_session_v0 import day_story_capture_session
from tests.test_day_scenario_native_llm_c1 import _interp_and_allowed, _valid_native


def _run_native(payload: dict[str, Any], *, max_attempts: int = 2, chat_side_effect=None):
    pack, _thesis, ritual, interp, _allowed = _interp_and_allowed()
    user_json = {"interpretation": interp}
    responses = chat_side_effect
    if responses is None:
        responses = [json.dumps(payload, ensure_ascii=False)]

    call_count = {"n": 0}

    def _chat(*_a, **_k):
        # Native module now calls chat_completion_plain_with_status:
        # (text, failure_class, model_id).
        i = call_count["n"]
        call_count["n"] += 1
        if i >= len(responses):
            return responses[-1], None, "test-model"
        return responses[i], None, "test-model"

    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=object(),
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_default_chat_model",
            return_value="test-model",
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.chat_completion_plain_with_status",
            side_effect=_chat,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_max_tokens",
            return_value=2400,
        ),
    ):
        result = call_day_scenario_native_llm_c1(
            user_json,
            interpretation=interp,
            ritual_context=ritual,
            celestial_events={"day_events_pack": pack},
            max_attempts=max_attempts,
        )
    return result, call_count["n"]


def test_promoted_abstract_scene_retries_then_accepts_good():
    """C3.6.3: SCENE_ABSTRACT blocking → retry; second good payload ships."""
    bad = _valid_native()
    for sc in bad["scenes"]:
        sc["setup"] = "Сегодня важно быть внимательным к отношениям."
        sc["everyday_example"] = "Будьте мягче."
        sc["opportunity"] = "Сохраняйте баланс."
        sc["trap"] = "Не торопитесь."
        sc["recommended_action"] = "Сделайте паузу."
        sc["avoid_action"] = "Избегайте крайностей."
        sc["chorus_refs"] = ["conflict", "day_card"]
    good = _valid_native()

    with day_story_capture_session(case_id="c363-quality-retry") as session:
        result, calls = _run_native(
            bad,
            max_attempts=2,
            chat_side_effect=[
                json.dumps(bad, ensure_ascii=False),
                json.dumps(good, ensure_ascii=False),
            ],
        )

    # I0 split: 2 Global attempts (bad → retry → good) + 1 Personal stage call.
    assert result is not None
    assert calls == 3
    meta = result.get("editorial_meta") or {}
    assert "gate_maturity" not in meta  # still not a public-contract expansion
    assert CRITICAL_DEFECTS  # scoring vocabulary still exists
    # Capture records the final merged i0-split attempt; the retry itself is
    # proven by the call count above (2 Global + 1 Personal).
    statuses = [a.get("status") for a in (session.pack.get("attempts") or [])]
    assert "accepted_native_i0_split" in statuses


def test_promoted_abstract_scene_exhausted_retries_unavailable():
    bad = _valid_native()
    for sc in bad["scenes"]:
        sc["setup"] = "Сегодня важно быть внимательным к отношениям."
        sc["everyday_example"] = "Будьте мягче."
        sc["opportunity"] = "Сохраняйте баланс."
        sc["trap"] = "Не торопитесь."
        sc["recommended_action"] = "Сделайте паузу."
        sc["avoid_action"] = "Избегайте крайностей."
        sc["chorus_refs"] = ["conflict", "day_card"]

    result, calls = _run_native(
        bad,
        max_attempts=2,
        chat_side_effect=[
            json.dumps(bad, ensure_ascii=False),
            json.dumps(bad, ensure_ascii=False),
        ],
    )
    assert result is None
    assert calls == 2


def test_legacy_critical_helpers_do_not_match_runtime_policy():
    """Prove old personalization CRITICAL set would retry/downgrade — maturity must not."""
    soft = [{"code": DEFECT_CLAIM_WITHOUT_EVIDENCE, "severity": "critical"}]
    assert personalization_requires_retry(soft) is True
    assert personalization_decision_after_retries(soft) == "downgrade_general"
    assert should_retry_defects(soft) is False
    assert should_downgrade_general(soft) is False
    assert should_reject_story(soft) is False


def test_candidate_blocking_is_observe_only():
    rule = GateRule(
        code="FAKE_CANDIDATE",
        family=FAMILY_QUALITY,
        maturity=MATURITY_CANDIDATE_BLOCKING,
        allow_retry=True,
        allow_reject=True,
    )
    assert runtime_action_for_rule(rule) == "score_only"
    assert MATURITY_CANDIDATE_BLOCKING in non_blocking_maturities()


def test_profile_fact_leak_rejects_without_retry_or_rewrite():
    leak = _valid_native()
    result, calls = _run_native_with_pers_patch(leak, max_attempts=2)
    assert result is None
    # I0 split: Global succeeds (1), personalization gate rejects at the
    # Personal stage (2) — no rewrite/retry loop beyond that.
    assert calls == 2


def _run_native_with_pers_patch(payload: dict[str, Any], *, max_attempts: int = 2):
    """Patch personalization gate at the module it is imported from (inside the call)."""
    pack, _thesis, ritual, interp, _allowed = _interp_and_allowed()
    user_json = {"interpretation": interp}
    responses = [json.dumps(payload, ensure_ascii=False)]
    call_count = {"n": 0}

    def _chat(*_a, **_k):
        i = call_count["n"]
        call_count["n"] += 1
        return responses[min(i, len(responses) - 1)], None, "test-model"

    leak_defects = [
        {
            "code": DEFECT_PROFILE_FACT_LEAK,
            "field": "public_prose",
            "message": "public text leaks raw profile/system fields",
            "severity": "critical",
        }
    ]

    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=object(),
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_default_chat_model",
            return_value="test-model",
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.chat_completion_plain_with_status",
            side_effect=_chat,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_max_tokens",
            return_value=2400,
        ),
        patch(
            "todayflow_backend.services.day_scenario_personalization_c33.run_personalization_gate_c33",
            return_value=leak_defects,
        ),
        patch(
            "todayflow_backend.services.day_scenario_sphere_selection_c33b.run_sphere_selection_gate_c33b",
            return_value=[],
        ),
    ):
        result = call_day_scenario_native_llm_c1(
            user_json,
            interpretation=interp,
            ritual_context=ritual,
            celestial_events={"day_events_pack": pack},
            max_attempts=max_attempts,
        )
    return result, call_count["n"]


def test_hard_schema_retries_then_unavailable():
    broken = {"schema_version": "wrong", "scenes": []}
    good = _valid_native()
    result, calls = _run_native(
        broken,
        max_attempts=2,
        chat_side_effect=[
            json.dumps(broken, ensure_ascii=False),
            json.dumps(broken, ensure_ascii=False),
        ],
    )
    assert result is None
    assert calls == 2

    result2, calls2 = _run_native(
        broken,
        max_attempts=2,
        chat_side_effect=[
            json.dumps(broken, ensure_ascii=False),
            json.dumps(good, ensure_ascii=False),
        ],
    )
    # I0 split: 2 Global attempts (broken → good) + 1 Personal stage call.
    assert result2 is not None
    assert calls2 == 3


def test_first_valid_kept_when_advisory_defects_present():
    native = _valid_native()
    native["conflict"]["why_personal"] = "Вам обычно свойственно сглаживать конфликт."
    native["personalization_depth"] = "general"

    with day_story_capture_session(case_id="c36-advisory") as session:
        result, calls = _run_native(native, max_attempts=2)

    # I0 split: 1 Global attempt (advisory defects don't retry) + 1 Personal call.
    assert result is not None
    assert calls == 2
    assert result.get("conflict")
    meta = result["editorial_meta"]
    assert "gate_maturity" not in meta
    attempts = session.pack.get("attempts") or []
    assert attempts
    last = attempts[-1]
    assert last.get("status") == "accepted_native_i0_split"
    after = last.get("after_normalize") or {}
    assert "gate_maturity" in after


def test_unpromoted_quality_rules_remain_observe_only():
    from todayflow_backend.services.day_scenario_gate_maturity_c36 import MATURITY_BLOCKING

    for code, rule in GATE_RULES.items():
        if rule.family != FAMILY_QUALITY:
            continue
        if rule.maturity == MATURITY_BLOCKING:
            d = annotate_defects_with_maturity([{"code": code}])[0]
            assert d["runtime_action"] in {"retry", "reject_story"}
            continue
        assert rule.maturity in non_blocking_maturities()
        d = annotate_defects_with_maturity([{"code": code}])[0]
        assert d["runtime_action"] == "score_only"


def test_promoted_editorial_defect_forces_second_llm_call():
    """C3.6.3: promoted SCENE_ABSTRACT opens maturity retry branch."""
    from todayflow_backend.services.day_scenario_editorial_gate_c31 import DEFECT_SCENE_ABSTRACT

    native = _valid_native()
    abstract_defects = [
        {
            "code": DEFECT_SCENE_ABSTRACT,
            "severity": "critical",
            "field": "scenes[0].setup",
            "message": "abstract",
        }
    ]
    pack, _thesis, ritual, interp, _allowed = _interp_and_allowed()
    call_count = {"n": 0}

    def _chat(*_a, **_k):
        call_count["n"] += 1
        # Always return same native; gate patched to keep firing → exhausted reject.
        return json.dumps(native, ensure_ascii=False), None, "test-model"

    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=object(),
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_default_chat_model",
            return_value="test-model",
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.chat_completion_plain_with_status",
            side_effect=_chat,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.resolve_max_tokens",
            return_value=2400,
        ),
        patch(
            "todayflow_backend.services.day_scenario_editorial_gate_c31.run_editorial_quality_gate_c31",
            return_value=abstract_defects,
        ),
    ):
        result = call_day_scenario_native_llm_c1(
            {"interpretation": interp},
            interpretation=interp,
            ritual_context=ritual,
            celestial_events={"day_events_pack": pack},
            max_attempts=2,
        )
    assert result is None
    assert call_count["n"] == 2
