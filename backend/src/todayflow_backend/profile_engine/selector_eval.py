"""Profile Selector eval harness — golden routing cases (no LLM)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from todayflow_backend.profile_engine.models import (
    ProfileContextSelectorInput,
    ProfilePromptSurface,
    ProfileTaskType,
    ProfileTopicDomain,
    UserOperatingMode,
)
from todayflow_backend.profile_engine.selector import select_profile_context


@dataclass(frozen=True)
class ProfileSelectorEvalCase:
    id: str
    inp: ProfileContextSelectorInput
    ritual_context: dict[str, Any] | None = None
    fusion_dump: dict[str, Any] | None = None
    core_profile: dict[str, Any] | None = None
    history_slice: dict[str, Any] | None = None
    expect_task: ProfileTaskType | None = None
    expect_topic: ProfileTopicDomain | None = None
    expect_mode: UserOperatingMode | None = None
    expect_rules_depth: str | None = None
    expect_profile_keys: tuple[str, ...] = ()
    expect_signals_contain: tuple[str, ...] = ()
    custom_assert: Callable[[Any], None] | None = None


def _minimal_fusion(**score_overrides: int) -> dict[str, Any]:
    scores = {"energy": 3, "focus": 3, "emotional_balance": 3}
    scores.update(score_overrides)
    return {
        "date": "2026-07-03",
        "scores": scores,
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {},
        "recommendations": [],
        "encouragement": "",
    }


PROFILE_SELECTOR_EVAL_CASES: tuple[ProfileSelectorEvalCase, ...] = (
    ProfileSelectorEvalCase(
        id="anxious_today_short_rules",
        inp=ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru"),
        ritual_context={"mood": "anxious"},
        fusion_dump=_minimal_fusion(),
        expect_task=ProfileTaskType.TODAY_SUMMARY,
        expect_mode=UserOperatingMode.ANXIETY,
        expect_rules_depth="short",
        expect_profile_keys=("action_fit", "avoid"),
    ),
    ProfileSelectorEvalCase(
        id="head_topic_money_domain",
        inp=ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru"),
        ritual_context={"head_topic": "money"},
        fusion_dump=_minimal_fusion(),
        expect_topic=ProfileTopicDomain.MONEY,
        expect_profile_keys=("topic",),
    ),
    ProfileSelectorEvalCase(
        id="evening_reflection_task",
        inp=ProfileContextSelectorInput(surface=ProfilePromptSurface.EVENING, locale="ru"),
        fusion_dump=_minimal_fusion(),
        expect_task=ProfileTaskType.EVENING_REFLECTION,
    ),
    ProfileSelectorEvalCase(
        id="topic_life_area_excerpt",
        inp=ProfileContextSelectorInput(
            surface=ProfilePromptSurface.TODAY,
            topic=ProfileTopicDomain.MONEY,
            locale="ru",
        ),
        core_profile={
            "interpretation": {
                "identity": "Общая линия",
                "life_areas": {"money": "Деньги растут через ясные границы и устойчивый темп."},
            }
        },
        fusion_dump=_minimal_fusion(),
        expect_topic=ProfileTopicDomain.MONEY,
        expect_profile_keys=("topic_sphere_excerpt",),
        custom_assert=lambda out: "деньги" in str(out.relevant_profile.get("topic_sphere_excerpt", "")).lower(),
    ),
    ProfileSelectorEvalCase(
        id="day_history_delta_signal",
        inp=ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru"),
        fusion_dump=_minimal_fusion(energy=4),
        history_slice={
            "contract_version": "day_history_v0",
            "fusion_score_delta_vs_yesterday": {"energy": 1, "focus": 0, "emotional_balance": -1},
            "fusion_score_delta_trustworthy": True,
        },
        expect_signals_contain=("day_history_delta:",),
    ),
)


@dataclass
class ProfileSelectorEvalResult:
    case_id: str
    passed: bool
    errors: list[str]


def run_profile_selector_eval_case(case: ProfileSelectorEvalCase) -> ProfileSelectorEvalResult:
    out = select_profile_context(
        case.inp,
        core_profile=case.core_profile,
        fusion_dump=case.fusion_dump,
        ritual_context=case.ritual_context,
        behavior_patterns=None,
        history_slice=case.history_slice,
    )
    errors: list[str] = []

    if case.expect_task is not None and out.task != case.expect_task:
        errors.append(f"task: expected {case.expect_task.value}, got {out.task.value}")
    if case.expect_topic is not None and out.topic != case.expect_topic:
        errors.append(f"topic: expected {case.expect_topic.value}, got {out.topic.value}")
    if case.expect_mode is not None and out.current_mode != case.expect_mode:
        errors.append(f"mode: expected {case.expect_mode.value}, got {out.current_mode.value}")
    if case.expect_rules_depth is not None and out.generation_rules.depth != case.expect_rules_depth:
        errors.append(
            f"rules.depth: expected {case.expect_rules_depth}, got {out.generation_rules.depth}",
        )
    for key in case.expect_profile_keys:
        if key not in out.relevant_profile:
            errors.append(f"relevant_profile missing key: {key}")
    for needle in case.expect_signals_contain:
        if not any(needle in signal for signal in out.recent_signals):
            errors.append(f"recent_signals missing: {needle}")
    if case.custom_assert is not None:
        try:
            case.custom_assert(out)
        except AssertionError as exc:
            errors.append(f"custom_assert: {exc}")

    return ProfileSelectorEvalResult(case_id=case.id, passed=not errors, errors=errors)


def run_profile_selector_eval(
    cases: tuple[ProfileSelectorEvalCase, ...] = PROFILE_SELECTOR_EVAL_CASES,
) -> list[ProfileSelectorEvalResult]:
    return [run_profile_selector_eval_case(case) for case in cases]
