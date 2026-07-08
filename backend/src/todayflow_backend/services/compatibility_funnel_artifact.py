"""Единый артефакт воронки совместимости: доменные скоры, confidence, таймлайн, риски.

Используется для быстрого (знаки) и среднего (даты) входа; тексты локализуются через i18n.
Полный профиль в следующих итерациях расширит accuracy_tier и наполнение без смены формы API.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from todayflow_backend.i18n import translate
from todayflow_backend.services.compatibility_scenario_metrics import funnel_domains_for_scenario
from todayflow_backend.services.sign_compatibility_product import normalize_relationship_context

AccuracyTier = Literal["signs_only", "birth_dates", "full_profile"]
RiskLevel = Literal["ok", "caution", "critical"]
TimelinePhaseId = Literal["now", "near", "inertia", "conscious"]


class FunnelDomainScore(BaseModel):
    """Один домен: процент = насколько легко сфере работать без осознанных усилий (не судьба)."""

    domain_id: str
    label: str
    score_pct: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0, description="Насколько оценка опирается на данные, а не на допущения")
    applicable: bool = True
    basis: str
    raises: list[str] = Field(default_factory=list)
    lowers: list[str] = Field(default_factory=list)
    improve: list[str] = Field(default_factory=list)


class FunnelTimelinePhase(BaseModel):
    phase_id: TimelinePhaseId
    headline: str
    body: str


class FunnelDynamicCore(BaseModel):
    """Асимметрия ролей + заметка про контроль/ясность (поверх pair_dynamics)."""

    you_line: str
    partner_line: str
    control_pattern: str
    clarity_note: str


class FunnelRiskBand(BaseModel):
    level: RiskLevel
    headline: str
    when_ok: str
    when_shifts: str
    when_breaks: str


class FunnelTodayAlignment(BaseModel):
    """Согласование с дневным слоем (тот же источник, что персонализация / Today-ритм)."""

    source: Literal["daily_guidance"] = "daily_guidance"
    focus_label: str = ""
    do_echo: str = ""
    avoid_echo: str = ""
    sync_note: str = ""


class CompatibilityLLMBaseModelFields(BaseModel):
    """Первый шаг LLM-цепочки: структурный слой поверх детерминированных сигналов."""

    pull_vs_tension: str = Field(default="", max_length=520)
    attraction_or_dependency: str = Field(default="", max_length=520)
    conflict_cycle: str = Field(default="", max_length=520)
    sexual_dynamic: str = Field(default="", max_length=520)
    aligned_actions_hint: str = Field(default="", max_length=400)


class CompatibilityFunnelArtifact(BaseModel):
    pipeline_version: str = "funnel-v1"
    scenario_id: str | None = None
    accuracy_tier: AccuracyTier
    accuracy_label: str
    relationship_context: str
    score_semantics: str
    confidence_note: str
    overall_score: int = Field(ge=0, le=100)
    domain_scores: list[FunnelDomainScore]
    children_relevant: bool
    timeline: list[FunnelTimelinePhase]
    dynamic_core: FunnelDynamicCore
    risk_bands: list[FunnelRiskBand]
    today_alignment: FunnelTodayAlignment | None = None
    llm_base_model: CompatibilityLLMBaseModelFields | None = None


def _loc_base(locale: str) -> str:
    return locale.strip().split("-")[0].lower() if locale else "ru"


def _clamp_pct(x: float) -> int:
    return max(0, min(100, int(round(x))))


def _bucket(score: int) -> Literal["h", "m", "l"]:
    if score >= 72:
        return "h"
    if score >= 55:
        return "m"
    return "l"


def _tier_confidence(tier: AccuracyTier) -> float:
    if tier == "signs_only":
        return 0.38
    if tier == "birth_dates":
        return 0.52
    return 0.72


def _pick_domain_drivers(
    domain_id: str,
    *,
    locale: str,
    attraction: int,
    stability: int,
    conflicts: int,
    sexuality: int,
    fe: str,
    te: str,
    fm: str,
    tm: str,
) -> tuple[list[str], list[str]]:
    """Факторы ↑/↓ уникальные для домена — не дублировать глобальную пару во всех блоках."""
    loc = _loc_base(locale)
    t = lambda key: translate(key, locale=loc)
    raises: list[str] = []
    lowers: list[str] = []

    if domain_id == "love":
        if attraction >= 74:
            raises.append(t("compat.funnel.driver.attr_high"))
        elif sexuality >= 78:
            raises.append(t("compat.funnel.driver.sex_high"))
        if attraction < 58:
            lowers.append(t("compat.funnel.driver.attr_low"))
        elif stability < 58:
            lowers.append(t("compat.funnel.driver.stab_low"))
        elif fm != tm:
            lowers.append(t("compat.funnel.driver.modality_diff"))

    elif domain_id == "sex":
        if sexuality >= 78:
            raises.append(t("compat.funnel.driver.sex_high"))
        elif attraction >= 74:
            raises.append(t("compat.funnel.driver.attr_high"))
        if sexuality < 58:
            lowers.append(t("compat.funnel.driver.sex_low"))
        elif {fe, te} == {"fire", "water"}:
            lowers.append(t("compat.funnel.driver.fire_water"))

    elif domain_id == "emotional":
        if stability >= 74:
            raises.append(t("compat.funnel.driver.stab_high"))
        if stability < 58:
            lowers.append(t("compat.funnel.driver.stab_low"))
        elif fe != te:
            lowers.append(t("compat.funnel.driver.element_diff"))

    elif domain_id == "conflicts":
        if conflicts >= 72:
            raises.append(t("compat.funnel.driver.repair_high"))
        if conflicts < 55:
            lowers.append(t("compat.funnel.driver.repair_low"))
        elif fm != tm:
            lowers.append(t("compat.funnel.driver.modality_diff"))

    elif domain_id == "money":
        if stability >= 74:
            raises.append(t("compat.funnel.driver.stab_high"))
        elif fe in {"earth", "water"} and te in {"earth", "water"}:
            raises.append(t("compat.funnel.driver.money_grounded"))
        if {fe, te} == {"fire", "water"}:
            lowers.append(t("compat.funnel.driver.fire_water"))
        elif stability < 58:
            lowers.append(t("compat.funnel.driver.stab_low"))

    elif domain_id == "family":
        if stability >= 74:
            raises.append(t("compat.funnel.driver.stab_high"))
        elif "water" in {fe, te}:
            raises.append(t("compat.funnel.driver.family_water"))
        if stability < 58:
            lowers.append(t("compat.funnel.driver.stab_low"))
        elif fm != tm:
            lowers.append(t("compat.funnel.driver.modality_diff"))

    elif domain_id == "work_live":
        if fm == tm:
            raises.append(t("compat.funnel.driver.modality_same"))
        elif stability >= 74:
            raises.append(t("compat.funnel.driver.stab_high"))
        if fm != tm:
            lowers.append(t("compat.funnel.driver.modality_diff"))
        elif fe != te:
            lowers.append(t("compat.funnel.driver.element_diff"))

    elif domain_id == "children":
        if stability >= 74 and conflicts >= 65:
            raises.append(t("compat.funnel.driver.repair_high"))
        elif stability >= 74:
            raises.append(t("compat.funnel.driver.stab_high"))
        if conflicts < 55:
            lowers.append(t("compat.funnel.driver.repair_low"))
        elif stability < 58:
            lowers.append(t("compat.funnel.driver.stab_low"))

    def uniq(seq: list[str]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for s in seq:
            if s and s not in seen:
                seen.add(s)
                out.append(s)
        return out[:2]

    r = uniq(raises)
    lo = uniq(lowers)
    if not r:
        r = [t("compat.funnel.driver.neutral_raise")]
    if not lo:
        lo = [t("compat.funnel.driver.neutral_lower")]
    return r[:1], lo[:1]


def _domain_basis(locale: str, domain: str, score: int) -> str:
    loc = _loc_base(locale)
    b = _bucket(score)
    return translate(f"compat.funnel.basis.{domain}.{b}", locale=loc)


def _domain_improve(locale: str, domain: str, b: str) -> list[str]:
    loc = _loc_base(locale)
    return [translate(f"compat.funnel.improve.{domain}.{b}", locale=loc)]


def _compute_child_relevant(ctx: str) -> bool:
    return ctx in {"in_relationship", "mutual_attraction"}


def _money_score(overall: int, stability: int, fe: str, te: str) -> int:
    base = 0.52 * overall + 0.48 * stability
    if fe in {"earth", "water"} and te in {"earth", "water"}:
        base += 6
    if {fe, te} == {"fire", "air"}:
        base += 3
    if {fe, te} == {"fire", "water"}:
        base -= 7
    return _clamp_pct(base)


def _family_score(love: int, stability: int, fe: str, te: str) -> int:
    base = 0.45 * love + 0.55 * stability
    if "water" in {fe, te}:
        base += 5
    if fe == te and fe in {"earth", "water"}:
        base += 4
    return _clamp_pct(base)


def _work_score(overall: int, stability: int, attraction: int, fm: str, tm: str) -> int:
    base = 0.4 * overall + 0.35 * stability + 0.25 * attraction
    if fm == tm:
        base += 5
    if {fm, tm} == {"cardinal", "fixed"}:
        base += 3
    return _clamp_pct(base)


def _children_score(stability: int, conflicts: int) -> int:
    return _clamp_pct(0.55 * stability + 0.45 * conflicts)


def _dynamic_core_from_pair(
    *,
    locale: str,
    user1_label: str,
    user2_label: str,
    pair_dynamics: dict[str, Any],
    ctx_norm: str,
) -> FunnelDynamicCore:
    loc = _loc_base(locale)
    u1_style = str(pair_dynamics.get("user_1_contact_style") or "")
    u2_style = str(pair_dynamics.get("user_2_contact_style") or "")
    leader = str(pair_dynamics.get("leader_guess") or "mixed")
    withdrawer = str(pair_dynamics.get("withdrawer_guess") or "mixed")

    you_line = f"{user1_label}: {u1_style}".strip()
    partner_line = f"{user2_label}: {u2_style}".strip()

    if leader == "user_1":
        control_pattern = translate("compat.funnel.control.lead_you", locale=loc)
    elif leader == "user_2":
        control_pattern = translate("compat.funnel.control.lead_partner", locale=loc)
    else:
        control_pattern = translate("compat.funnel.control.shared", locale=loc)

    if withdrawer == "user_1":
        clarity_note = translate("compat.funnel.clarity.you_withdraw", locale=loc)
    elif withdrawer == "user_2":
        clarity_note = translate("compat.funnel.clarity.partner_withdraw", locale=loc)
    else:
        clarity_note = translate("compat.funnel.clarity.balanced", locale=loc)

    ctx_key = ctx_norm if ctx_norm in {
        "just_met", "mutual_attraction", "in_relationship", "unclear",
        "conflict_distance", "split_but_pull", "unspecified",
    } else "unspecified"
    clarity_note = f"{clarity_note} {translate(f'compat.funnel.clarity.ctx.{ctx_key}', locale=loc)}".strip()

    return FunnelDynamicCore(
        you_line=you_line,
        partner_line=partner_line,
        control_pattern=control_pattern,
        clarity_note=clarity_note,
    )


def _timeline(locale: str, ctx_label: str) -> list[FunnelTimelinePhase]:
    loc = _loc_base(locale)
    phases: list[tuple[TimelinePhaseId, str, str]] = [
        ("now", "compat.funnel.timeline.now.title", "compat.funnel.timeline.now.body"),
        ("near", "compat.funnel.timeline.near.title", "compat.funnel.timeline.near.body"),
        ("inertia", "compat.funnel.timeline.inertia.title", "compat.funnel.timeline.inertia.body"),
        ("conscious", "compat.funnel.timeline.conscious.title", "compat.funnel.timeline.conscious.body"),
    ]
    out: list[FunnelTimelinePhase] = []
    for pid, tk, bk in phases:
        body_t = translate(bk, locale=loc)
        try:
            body_f = body_t.format(context_label=ctx_label)
        except (KeyError, ValueError):
            body_f = body_t
        out.append(
            FunnelTimelinePhase(
                phase_id=pid,
                headline=translate(tk, locale=loc),
                body=body_f,
            )
        )
    return out


def _risk_bands(locale: str, stability: int, conflicts: int) -> list[FunnelRiskBand]:
    loc = _loc_base(locale)
    # conflicts = ease of repair (высокий = легче чинить связь)
    strain = 100 - (0.55 * conflicts + 0.45 * stability)

    if strain < 38:
        level: RiskLevel = "ok"
    elif strain < 58:
        level = "caution"
    else:
        level = "critical"

    bands = [
        FunnelRiskBand(
            level="ok",
            headline=translate("compat.funnel.risk.ok.headline", locale=loc),
            when_ok=translate("compat.funnel.risk.ok.when_ok", locale=loc),
            when_shifts=translate("compat.funnel.risk.ok.when_shifts", locale=loc),
            when_breaks=translate("compat.funnel.risk.ok.when_breaks", locale=loc),
        ),
        FunnelRiskBand(
            level="caution",
            headline=translate("compat.funnel.risk.caution.headline", locale=loc),
            when_ok=translate("compat.funnel.risk.caution.when_ok", locale=loc),
            when_shifts=translate("compat.funnel.risk.caution.when_shifts", locale=loc),
            when_breaks=translate("compat.funnel.risk.caution.when_breaks", locale=loc),
        ),
        FunnelRiskBand(
            level="critical",
            headline=translate("compat.funnel.risk.critical.headline", locale=loc),
            when_ok=translate("compat.funnel.risk.critical.when_ok", locale=loc),
            when_shifts=translate("compat.funnel.risk.critical.when_shifts", locale=loc),
            when_breaks=translate("compat.funnel.risk.critical.when_breaks", locale=loc),
        ),
    ]
    # Подсветка «текущей зоны» для клиента: первым кладём активный уровень
    primary = [b for b in bands if b.level == level]
    rest = [b for b in bands if b.level != level]
    return primary + rest


def build_compatibility_funnel_artifact(
    *,
    mode: Literal["quick", "precise", "full"],
    relationship_context: str | None,
    overall_score: int,
    subscores: dict[str, int],
    pair_dynamics: dict[str, Any],
    user1_label: str,
    user2_label: str,
    from_element: str,
    to_element: str,
    from_modality: str,
    to_modality: str,
    locale: str,
    today_alignment: FunnelTodayAlignment | None = None,
    llm_base_model: CompatibilityLLMBaseModelFields | None = None,
    format_id: str | None = None,
) -> CompatibilityFunnelArtifact:
    ctx_norm = normalize_relationship_context(relationship_context)
    loc = _loc_base(locale)
    if mode == "full":
        tier: AccuracyTier = "full_profile"
    elif mode == "precise":
        tier = "birth_dates"
    else:
        tier = "signs_only"
    conf = _tier_confidence(tier)

    attr = int(subscores.get("attraction", overall_score))
    stab = int(subscores.get("stability", overall_score))
    conf_rep = int(subscores.get("conflicts", overall_score))
    sex = int(subscores.get("sexuality", overall_score))

    fe = (from_element or "").lower()
    te = (to_element or "").lower()
    fm = (from_modality or "").lower()
    tm = (to_modality or "").lower()

    love = _clamp_pct(0.44 * attr + 0.32 * stab + 0.24 * sex)
    emotional = stab
    money = _money_score(overall_score, stab, fe, te)
    family = _family_score(love, stab, fe, te)
    work_live = _work_score(overall_score, stab, attr, fm, tm)
    child_rel = _compute_child_relevant(ctx_norm)
    children = _children_score(stab, conf_rep) if child_rel else 0

    def pack_domain(
        domain_id: str,
        label_key: str,
        score: int,
        applicable: bool = True,
    ) -> FunnelDomainScore:
        b = _bucket(score)
        basis = _domain_basis(locale, domain_id, score)
        r, lo = _pick_domain_drivers(
            domain_id,
            locale=locale,
            attraction=attr,
            stability=stab,
            conflicts=conf_rep,
            sexuality=sex,
            fe=fe,
            te=te,
            fm=fm,
            tm=tm,
        )
        return FunnelDomainScore(
            domain_id=domain_id,
            label=translate(label_key, locale=loc),
            score_pct=score if applicable else 0,
            confidence=conf,
            applicable=applicable,
            basis=basis,
            raises=r,
            lowers=lo,
            improve=_domain_improve(locale, domain_id, b),
        )

    domain_scores = [
        pack_domain("love", "compat.funnel.domain.love.label", love),
        pack_domain("sex", "compat.funnel.domain.sex.label", sex),
        pack_domain("emotional", "compat.funnel.domain.emotional.label", emotional),
        pack_domain("conflicts", "compat.funnel.domain.conflicts.label", conf_rep),
        pack_domain("money", "compat.funnel.domain.money.label", money),
        pack_domain("family", "compat.funnel.domain.family.label", family),
        pack_domain("work_live", "compat.funnel.domain.work.label", work_live),
        pack_domain("children", "compat.funnel.domain.children.label", children, applicable=child_rel),
    ]

    scenario_domains = funnel_domains_for_scenario(format_id)
    if scenario_domains:
        allowed = set(scenario_domains)
        domain_scores = [d for d in domain_scores if d.domain_id in allowed and d.applicable]
        # Keep order from scenario spec
        by_id = {d.domain_id: d for d in domain_scores}
        domain_scores = [by_id[did] for did in scenario_domains if did in by_id]

    ctx_label = translate(f"compat.context.{ctx_norm}", locale=loc)

    return CompatibilityFunnelArtifact(
        scenario_id=format_id,
        accuracy_tier=tier,
        accuracy_label=translate(f"compat.funnel.tier.{tier}", locale=loc),
        relationship_context=ctx_norm,
        score_semantics=translate("compat.funnel.score_semantics", locale=loc),
        confidence_note=translate(f"compat.funnel.confidence_note.{tier}", locale=loc),
        overall_score=overall_score,
        domain_scores=domain_scores,
        children_relevant=child_rel,
        timeline=_timeline(locale, ctx_label),
        dynamic_core=_dynamic_core_from_pair(
            locale=locale,
            user1_label=user1_label,
            user2_label=user2_label,
            pair_dynamics=pair_dynamics,
            ctx_norm=ctx_norm,
        ),
        risk_bands=_risk_bands(locale, stab, conf_rep),
        today_alignment=today_alignment,
        llm_base_model=llm_base_model,
    )

