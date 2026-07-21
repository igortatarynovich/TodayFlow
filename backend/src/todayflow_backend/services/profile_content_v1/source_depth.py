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
            "Портрет опирается на ваши ответы и повторяющиеся дни — не только на дату рождения."
            if ru
            else "The portrait draws on your answers and recurring days — not birth data alone."
        )
    if depth == "profile_plus_checkins":
        return (
            "По отметкам уже видны первые тенденции. С накоплением дней закономерности вашей жизни становятся яснее."
            if ru
            else "Early tendencies already show in your check-ins. More days make your life patterns clearer."
        )
    if depth == "onboarding_answers":
        return (
            "Часть формулировок опирается на ваши ответы при старте. Закрытые дни покажут, что из этого держится в жизни."
            if ru
            else "Some lines draw on your onboarding answers. Closed days will show what holds in real life."
        )
    return (
        "Портрет по дате рождения показывает общие черты. Повторяющиеся жизненные закономерности проявляются со временем."
        if ru
        else "A birth-date portrait shows general traits. Recurring life patterns appear over time."
    )


def depth_from_scenario(sc: dict[str, Any]) -> ProfileSourceDepth:
    return resolve_profile_source_depth(
        has_birth=bool(sc.get("birth_date")),
        has_onboarding=bool(sc.get("onboarding")),
        checkin_days=int(sc.get("checkin_days") or 0),
        longitudinal_days=int(sc.get("longitudinal_days") or 0),
    )


def depth_from_profile_pack(user_json: dict[str, Any] | None) -> ProfileSourceDepth:
    """Resolve source_depth from the portrait LLM pack (shared funnel input)."""
    pack = user_json if isinstance(user_json, dict) else {}
    person = pack.get("person") if isinstance(pack.get("person"), dict) else {}
    astro = pack.get("astro") if isinstance(pack.get("astro"), dict) else {}
    numerology = pack.get("numerology") if isinstance(pack.get("numerology"), dict) else {}
    living = pack.get("living") if isinstance(pack.get("living"), dict) else {}
    onboarding = living.get("onboarding") if isinstance(living.get("onboarding"), dict) else pack.get("onboarding")

    has_birth = bool(
        person.get("birth_date")
        or astro.get("birth_date")
        or astro.get("sun_sign")
        or numerology.get("birth_date")
        or numerology.get("life_path") is not None
    )
    has_onboarding = bool(onboarding)

    signal = living.get("signal_profile") if isinstance(living.get("signal_profile"), dict) else {}
    checkin_days = int(signal.get("signals_days") or 0)
    if checkin_days <= 0:
        signals = living.get("signals")
        if isinstance(signals, list):
            checkin_days = len(signals)
    longitudinal_days = int(signal.get("longitudinal_days") or living.get("longitudinal_days") or checkin_days or 0)

    return resolve_profile_source_depth(
        has_birth=has_birth,
        has_onboarding=has_onboarding,
        checkin_days=checkin_days,
        longitudinal_days=longitudinal_days,
    )


def patterns_generation_allowed(user_json: dict[str, Any] | None) -> bool:
    """Production invariant: recurring_patterns LLM step only with longitudinal evidence."""
    from todayflow_backend.services.profile_content_v1.architecture import classify_allowed_claims

    depth = depth_from_profile_pack(user_json)
    return bool(classify_allowed_claims(depth).get("recurring_patterns"))
