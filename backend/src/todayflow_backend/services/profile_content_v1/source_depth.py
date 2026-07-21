"""Honest profile depth — drives copy constraints."""

from __future__ import annotations

from typing import Any, Literal

ProfileSourceDepth = Literal[
    "birth_data_only",
    "onboarding_answers",
    "profile_plus_checkins",
    "longitudinal_profile",
]


def resolve_profile_source_depth(
    *,
    has_birth: bool = False,
    has_onboarding: bool = False,
    checkin_days: int = 0,
    longitudinal_days: int = 0,
) -> ProfileSourceDepth:
    if longitudinal_days >= 14 and checkin_days >= 7:
        return "longitudinal_profile"
    if checkin_days >= 3 or longitudinal_days >= 7:
        return "profile_plus_checkins"
    if has_onboarding:
        return "onboarding_answers"
    if has_birth:
        return "birth_data_only"
    return "birth_data_only"


def depth_honesty_line(depth: ProfileSourceDepth, *, locale: str = "ru") -> str:
    ru = not (locale or "ru").lower().startswith("en")
    if depth == "longitudinal_profile":
        return (
            "Разбор опирается на ваши ответы и повторяющиеся дни — не только на дату рождения."
            if ru
            else "This uses your answers and recurring days — not birth data alone."
        )
    if depth == "profile_plus_checkins":
        return (
            "Видны первые тенденции из ваших отметок. Это ещё не полный долгосрочный портрет."
            if ru
            else "Early tendencies from your check-ins — not a full long-term portrait."
        )
    if depth == "onboarding_answers":
        return (
            "Часть формулировок опирается на ваши ответы при старте. Поведение «в жизни» ещё не проверено днями."
            if ru
            else "Part of this uses your onboarding answers — real-life patterns are not confirmed yet."
        )
    return (
        "По данным рождения виден общий портрет. Этого недостаточно, чтобы утверждать, как вы реально ведёте себя в стрессе."
        if ru
        else "Birth data shows a general portrait — not enough to claim how you act under stress."
    )


def depth_from_scenario(sc: dict[str, Any]) -> ProfileSourceDepth:
    return resolve_profile_source_depth(
        has_birth=bool(sc.get("birth_date")),
        has_onboarding=bool(sc.get("onboarding")),
        checkin_days=int(sc.get("checkin_days") or 0),
        longitudinal_days=int(sc.get("longitudinal_days") or 0),
    )
