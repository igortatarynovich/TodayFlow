"""Продуктовый слой для GET /compatibility/signs: динамика пары, подскоры, блоки, роли.

Тексты опираются на стихию/модальность и контекст отношений — без привязки поведения к полу.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from todayflow_backend.i18n import translate


class SignCompatSubscores(BaseModel):
    attraction: int = Field(ge=0, le=100)
    stability: int = Field(ge=0, le=100)
    conflicts: int = Field(ge=0, le=100)
    sexuality: int = Field(ge=0, le=100)


class SignCompatAnalysisBlock(BaseModel):
    key: str
    title: str
    subtitle: str
    takeaway: str
    detail: str
    risk: str
    action: str
    tips: List[str] = Field(default_factory=list)


class SignCompatRoles(BaseModel):
    you_bullets: List[str]
    partner_bullets: List[str]


class SignCompatScenarioGroup(BaseModel):
    id: str
    title: str
    bullets: List[str]


class SignCompatibilityProductSurface(BaseModel):
    score_tagline: str
    subscores: SignCompatSubscores
    overview_paragraphs: List[str]
    blocks: List[SignCompatAnalysisBlock]
    roles: SignCompatRoles
    scenarios: List[SignCompatScenarioGroup]


_CONTEXT_ALIASES: dict[str, str] = {
    "": "unspecified",
    "unspecified": "unspecified",
    "just_met": "just_met",
    "starting": "just_met",
    "mutual_attraction": "mutual_attraction",
    "attraction": "mutual_attraction",
    "in_relationship": "in_relationship",
    "relationship": "in_relationship",
    "unclear": "unclear",
    "conflict_distance": "conflict_distance",
    "conflict": "conflict_distance",
    "split_but_pull": "split_but_pull",
    "split": "split_but_pull",
}


def normalize_relationship_context(raw: str | None) -> str:
    if not raw:
        return "unspecified"
    key = raw.strip().lower()
    return _CONTEXT_ALIASES.get(key, "unspecified")


def _norm_compat_locale(locale: str | None) -> str:
    if locale is None:
        return "ru"
    base = locale.strip().split("-")[0].lower()
    return base if base in ("en", "ru") else "en"


def _clamp_int(value: float, lo: int = 45, hi: int = 95) -> int:
    return max(lo, min(hi, int(round(value))))


def _modality_lines(modality: str, *, side: str, locale: str) -> List[str]:
    """side: 'you' | 'partner' — формулировки про роль в паре."""
    m = (modality or "").strip().lower()
    role = "you" if side == "you" else "partner"
    prefix = f"compat.role.{role}"
    if m == "cardinal":
        return [
            translate(f"{prefix}.cardinal.1", locale=locale),
            translate(f"{prefix}.cardinal.2", locale=locale),
        ]
    if m == "fixed":
        return [
            translate(f"{prefix}.fixed.1", locale=locale),
            translate(f"{prefix}.fixed.2", locale=locale),
        ]
    if m == "mutable":
        return [
            translate(f"{prefix}.mutable.1", locale=locale),
            translate(f"{prefix}.mutable.2", locale=locale),
        ]
    return [translate(f"{prefix}.default.1", locale=locale)]


def _sexuality_intensity_key(from_sign: str, to_sign: str, attraction: int) -> str:
    sid = {from_sign.lower(), to_sign.lower()}
    if "scorpio" in sid or {"cancer", "pisces"} & sid == {"cancer", "pisces"}:
        return "compat.sexintensity.deep"
    if "taurus" in sid or "leo" in sid:
        return "compat.sexintensity.strong"
    if attraction >= 82:
        return "compat.sexintensity.fast"
    if attraction >= 68:
        return "compat.sexintensity.good"
    return "compat.sexintensity.low"


def _sexuality_practical_tips(
    *,
    from_modality: str,
    to_modality: str,
    sexuality_score: int,
    locale: str,
) -> list[str]:
    loc = _norm_compat_locale(locale)
    fm = (from_modality or "").lower()
    tm = (to_modality or "").lower()
    tips: list[str] = []
    if fm != tm:
        tips.append(translate("compat.block.sexuality.tip.initiative_alt", locale=loc))
    else:
        tips.append(translate("compat.block.sexuality.tip.initiative_shared", locale=loc))
    tips.append(translate("compat.block.sexuality.tip.position_pace", locale=loc))
    if sexuality_score >= 78:
        tips.append(translate("compat.block.sexuality.tip.high_drive", locale=loc))
    else:
        tips.append(translate("compat.block.sexuality.tip.warmup", locale=loc))
    tips.append(translate("compat.block.sexuality.tip.if_rejected", locale=loc))
    if "fixed" in (fm, tm):
        tips.append(translate("compat.block.sexuality.tip.fixed_pace", locale=loc))
    return tips[:5]


def _pair_tagline_seed(from_sign: str, to_sign: str) -> int:
    a, b = sorted([(from_sign or "").lower(), (to_sign or "").lower()])
    return sum(ord(c) for c in f"{a}:{b}")


def _pick_tagline(
    attraction: int,
    stability: int,
    conflicts: int,
    sexuality: int,
    locale: str,
    *,
    from_sign: str = "",
    to_sign: str = "",
) -> str:
    candidates: list[str] = []
    if attraction >= 78 and stability < 68:
        candidates.append("compat.tagline.t1")
    if attraction >= 78 and conflicts < 62:
        candidates.append("compat.tagline.t2")
    if stability >= 78 and attraction < 68:
        candidates.append("compat.tagline.t3")
    if attraction >= 72 and sexuality >= 78:
        candidates.extend(
            [
                "compat.tagline.t4",
                "compat.tagline.t6",
                "compat.tagline.t7",
                "compat.tagline.t8",
            ]
        )
    if stability >= 70 and conflicts >= 68:
        candidates.append("compat.tagline.t9")
    if not candidates:
        candidates = ["compat.tagline.t5", "compat.tagline.t10"]

    seen: set[str] = set()
    pool: list[str] = []
    for key in candidates:
        if key not in seen:
            seen.add(key)
            pool.append(key)
    idx = _pair_tagline_seed(from_sign, to_sign) % len(pool)
    return translate(pool[idx], locale=locale)


def _context_hook(ctx: str, locale: str) -> str:
    ctx_key = normalize_relationship_context(ctx)
    return translate(f"compat.sign.ctx.{ctx_key}", locale=locale)


def build_sign_product_surface(
    *,
    from_sign: str,
    to_sign: str,
    from_name: str,
    to_name: str,
    from_element: str,
    to_element: str,
    from_modality: str,
    to_modality: str,
    score: int,
    relationship_context: str,
    element_relation: str,
    rhythm_relation: str,
    strongest: str,
    friction: str,
    locale: str | None = None,
) -> SignCompatibilityProductSurface:
    loc = _norm_compat_locale(locale)
    fe = (from_element or "").lower()
    te = (to_element or "").lower()
    fm = (from_modality or "").lower()
    tm = (to_modality or "").lower()

    attraction = float(score)
    if {fe, te} in ({"fire", "air"}, {"earth", "water"}):
        attraction += 7
    elif fe == te:
        attraction += 4
    elif {fe, te} == {"fire", "water"}:
        attraction += 11
    attraction_i = _clamp_int(attraction)

    stability = float(score)
    if fm != tm:
        stability -= 6
    if {fe, te} == {"fire", "water"}:
        stability -= 8
    if {fe, te} == {"earth", "air"}:
        stability -= 5
    if fm == tm:
        stability += 5
    stability_i = _clamp_int(stability)

    # Чем выше conflicts score — тем здоровее восстановление после срыва (не «уровень ссор»).
    conflicts = float(score)
    if {fm, tm} == {"fixed", "mutable"}:
        conflicts -= 6
    if {fm, tm} == {"cardinal", "fixed"}:
        conflicts -= 3
    if fm == tm:
        conflicts += 4
    conflicts_i = _clamp_int(conflicts)

    sexuality = (attraction_i * 0.48 + score * 0.28 + (100 - abs(attraction_i - stability_i)) * 0.15)
    sid = {from_sign.lower(), to_sign.lower()}
    if "scorpio" in sid or "taurus" in sid:
        sexuality += 7
    sexuality_i = _clamp_int(sexuality)

    ctx = normalize_relationship_context(relationship_context)
    hook = _context_hook(ctx, loc)

    overview = [
        hook,
        translate("compat.sign.overview.bridge", locale=loc).format(
            from_name=from_name, to_name=to_name, element_relation=element_relation
        ),
        translate("compat.sign.overview.rhythm", locale=loc).format(rhythm_relation=rhythm_relation),
        translate("compat.sign.overview.not_verdict", locale=loc),
    ]
    if ctx == "conflict_distance":
        overview.append(translate("compat.sign.overview.extra.conflict", locale=loc))
    elif ctx == "split_but_pull":
        overview.append(translate("compat.sign.overview.extra.split", locale=loc))

    emo_take = (
        translate("compat.block.emotions.take.diff", locale=loc)
        if fe != te
        else translate("compat.block.emotions.take.same", locale=loc)
    )
    emo_detail = (
        translate("compat.block.emotions.detail.diff", locale=loc).format(element_relation=element_relation)
        if fe != te
        else translate("compat.block.emotions.detail.same", locale=loc)
    )

    comm_take = (
        translate("compat.block.communication.take.diff", locale=loc)
        if fm != tm
        else translate("compat.block.communication.take.same", locale=loc)
    )
    comm_detail = translate("compat.block.communication.detail", locale=loc).format(rhythm_relation=rhythm_relation)

    conf_take = translate("compat.block.conflicts.take", locale=loc)
    conf_detail = translate("compat.block.conflicts.detail", locale=loc).format(rhythm_relation=rhythm_relation)
    conf_risk = friction

    sex_int_key = _sexuality_intensity_key(from_sign, to_sign, attraction_i)
    sex_int = translate(sex_int_key, locale=loc)
    initiator = (
        translate("compat.block.sexuality.initiator.diff", locale=loc)
        if fm != tm
        else translate("compat.block.sexuality.initiator.same", locale=loc)
    )
    control_line = (
        translate("compat.block.sexuality.control.fixed", locale=loc)
        if "fixed" in (fm, tm)
        else translate("compat.block.sexuality.control.other", locale=loc)
    )

    long_take = (
        translate("compat.block.long_term.take.low", locale=loc)
        if stability_i < 72
        else translate("compat.block.long_term.take.high", locale=loc)
    )
    long_detail = translate("compat.block.long_term.detail", locale=loc).format(strongest=strongest)

    sex_detail = translate("compat.block.sexuality.detail.mid", locale=loc).format(
        initiator=initiator, control_line=control_line
    )

    blocks = [
        SignCompatAnalysisBlock(
            key="emotions",
            title=translate("compat.block.emotions.title", locale=loc),
            subtitle=translate("compat.block.emotions.subtitle", locale=loc),
            takeaway=emo_take,
            detail=emo_detail,
            risk=translate("compat.block.emotions.risk", locale=loc),
            action=translate("compat.block.emotions.action", locale=loc),
        ),
        SignCompatAnalysisBlock(
            key="communication",
            title=translate("compat.block.communication.title", locale=loc),
            subtitle=translate("compat.block.communication.subtitle", locale=loc),
            takeaway=comm_take,
            detail=comm_detail,
            risk=translate("compat.block.communication.risk", locale=loc),
            action=translate("compat.block.communication.action", locale=loc),
        ),
        SignCompatAnalysisBlock(
            key="conflicts",
            title=translate("compat.block.conflicts.title", locale=loc),
            subtitle=translate("compat.block.conflicts.subtitle", locale=loc),
            takeaway=conf_take,
            detail=conf_detail,
            risk=conf_risk,
            action=translate("compat.block.conflicts.action", locale=loc),
        ),
        SignCompatAnalysisBlock(
            key="sexuality",
            title=translate("compat.block.sexuality.title", locale=loc),
            subtitle=translate("compat.block.sexuality.subtitle", locale=loc),
            takeaway=translate("compat.block.sexuality.take", locale=loc).format(sex_intensity=sex_int),
            detail=sex_detail,
            risk=translate("compat.block.sexuality.risk", locale=loc),
            action=translate("compat.block.sexuality.action", locale=loc),
            tips=_sexuality_practical_tips(
                from_modality=from_modality,
                to_modality=to_modality,
                sexuality_score=sexuality_i,
                locale=loc,
            ),
        ),
        SignCompatAnalysisBlock(
            key="long_term",
            title=translate("compat.block.long_term.title", locale=loc),
            subtitle=translate("compat.block.long_term.subtitle", locale=loc),
            takeaway=long_take,
            detail=long_detail,
            risk=translate("compat.block.long_term.risk", locale=loc),
            action=translate("compat.block.long_term.action", locale=loc),
        ),
    ]

    scenarios = [
        SignCompatScenarioGroup(
            id="closer",
            title=translate("compat.scenario.closer.title", locale=loc),
            bullets=[
                translate("compat.scenario.closer.b1", locale=loc),
                translate("compat.scenario.closer.b2", locale=loc),
                translate("compat.scenario.closer.b3", locale=loc),
            ],
        ),
        SignCompatScenarioGroup(
            id="clarity",
            title=translate("compat.scenario.clarity.title", locale=loc),
            bullets=[
                translate("compat.scenario.clarity.b1", locale=loc),
                translate("compat.scenario.clarity.b2", locale=loc),
                translate("compat.scenario.clarity.b3", locale=loc),
            ],
        ),
        SignCompatScenarioGroup(
            id="exit",
            title=translate("compat.scenario.exit.title", locale=loc),
            bullets=[
                translate("compat.scenario.exit.b1", locale=loc),
                translate("compat.scenario.exit.b2", locale=loc),
                translate("compat.scenario.exit.b3", locale=loc),
            ],
        ),
    ]

    if ctx == "just_met":
        scenarios[0].bullets.insert(0, translate("compat.scenario.insert.just_met", locale=loc))
    elif ctx == "conflict_distance":
        scenarios[1].bullets.insert(0, translate("compat.scenario.insert.conflict", locale=loc))

    roles = SignCompatRoles(
        you_bullets=_modality_lines(fm, side="you", locale=loc)[:3],
        partner_bullets=_modality_lines(tm, side="partner", locale=loc)[:3],
    )

    tagline = _pick_tagline(
        attraction_i, stability_i, conflicts_i, sexuality_i, loc, from_sign=from_sign, to_sign=to_sign
    )

    return SignCompatibilityProductSurface(
        score_tagline=tagline,
        subscores=SignCompatSubscores(
            attraction=attraction_i,
            stability=stability_i,
            conflicts=conflicts_i,
            sexuality=sexuality_i,
        ),
        overview_paragraphs=overview,
        blocks=blocks,
        roles=roles,
        scenarios=scenarios,
    )
