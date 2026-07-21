"""Freemium disclosure for compatibility — guest / registered / paid.

Tiers (product):
- guest: teaser — score, tagline, short overview, strongest/friction one-liners
- registered (free billing): full emotional/communication/conflict blocks; soft action
- paid (lite/pro → pro/premium insight): yes/no framing, do / don't / how, sexuality tips, scenarios

Never mention AI/generation in user-facing gate copy.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Optional

from sqlalchemy.orm import Session

from todayflow_backend.db.models import User
from todayflow_backend.services.insight_depth import InsightDepthTier, get_insight_depth_tier
from todayflow_backend.services.sign_compatibility_product import SignCompatibilityProductSurface

CompatAccessTier = Literal["guest", "registered", "paid"]

COMPAT_ACCESS_CONTRACT = "compatibility_access_v0"


def resolve_compat_access_tier(user: Optional[User], db: Session) -> CompatAccessTier:
    if user is None:
        return "guest"
    depth: InsightDepthTier = get_insight_depth_tier(user, db)
    if depth in ("pro", "premium"):
        return "paid"
    return "registered"


def _yes_no_from_score(score: int, *, locale: str) -> dict[str, str]:
    loc = (locale or "ru").strip().lower()
    ru = loc.startswith("ru")
    if score >= 72:
        return {
            "answer": "да" if ru else "yes",
            "framing": (
                "Связь стоит развивать — опора есть, если не путать близость с контролем."
                if ru
                else "Worth building — the base is there if you don't confuse closeness with control."
            ),
        }
    if score >= 52:
        return {
            "answer": "скорее да, с условиями" if ru else "yes, with conditions",
            "framing": (
                "Можно идти дальше, но только с ясными договорённостями о темпе и границах."
                if ru
                else "You can go further — only with clear agreements on pace and boundaries."
            ),
        }
    return {
        "answer": "пока нет" if ru else "not yet",
        "framing": (
            "Сейчас важнее понять напряжение, чем форсировать «получится / не получится»."
            if ru
            else "Understand the friction first — don't force a yes/no verdict."
        ),
    }


def shape_product_surface_for_tier(
    surface: SignCompatibilityProductSurface,
    *,
    tier: CompatAccessTier,
    overall_score: int,
    locale: str = "ru",
) -> tuple[SignCompatibilityProductSurface, dict[str, Any]]:
    """Returns (shaped_surface, disclosure_meta) for API payload.

    Never raises on sparse/empty LLM surfaces — always returns a serializable teaser.
    """
    loc = (locale or "ru").strip().split("-")[0].lower()
    ru = loc != "en"
    try:
        shaped = surface.model_copy(deep=True)
    except Exception:
        shaped = surface
    # Normalize empties so response validation never fails after gating.
    if not shaped.overview_paragraphs:
        shaped.overview_paragraphs = [
            shaped.score_tagline
            or ("Краткий ориентир по динамике пары." if ru else "A short read on the pair dynamic.")
        ]
    if not shaped.blocks:
        from todayflow_backend.services.sign_compatibility_product import SignCompatAnalysisBlock

        shaped.blocks = [
            SignCompatAnalysisBlock(
                key="emotions",
                title="Эмоции" if ru else "Emotions",
                subtitle="",
                takeaway=shaped.score_tagline or ("Есть притяжение и напряжение." if ru else "Pull and tension."),
                detail="",
                risk="",
                action="",
                tips=[],
            )
        ]
    meta: dict[str, Any] = {
        "contract_version": COMPAT_ACCESS_CONTRACT,
        "tier": tier,
        "locked_layers": [],
        "upsell": None,
    }

    # Always keep score_tagline + first overview paragraph for every tier.
    if tier == "guest":
        shaped.overview_paragraphs = list(shaped.overview_paragraphs[:1])
        # Keep only emotions takeaway as teaser; strip action/risk/detail/tips.
        teaser_blocks = []
        for block in shaped.blocks:
            if block.key not in ("emotions", "communication"):
                continue
            teaser_blocks.append(
                block.model_copy(
                    update={
                        "detail": "",
                        "risk": "",
                        "action": "",
                        "tips": [],
                        "subtitle": "",
                    }
                )
            )
            if len(teaser_blocks) >= 1:
                break
        shaped.blocks = teaser_blocks
        shaped.roles = shaped.roles.model_copy(update={"you_bullets": shaped.roles.you_bullets[:1], "partner_bullets": []})
        shaped.scenarios = []
        meta["locked_layers"] = [
            "full_overview",
            "conflicts",
            "sexuality",
            "long_term",
            "scenarios",
            "yes_no",
            "do_dont_how",
        ]
        meta["upsell"] = {
            "title": "Открой полный разбор" if ru else "Unlock the full reading",
            "body": (
                "После регистрации — эмоции, общение и где вы ломаетесь. "
                "С подпиской — ответы да/нет, что делать, чего не делать и как."
                if ru
                else "After signup — emotions, talk patterns, and where you break. "
                "With a plan — yes/no framing, what to do, what not to, and how."
            ),
            "cta_register": "Создать мой Today" if ru else "Create my Today",
            "cta_subscribe": "Открыть полный доступ" if ru else "Get full access",
        }
        return shaped, meta

    if tier == "registered":
        # Full soft blocks except sexuality tips + paid scenarios + do/dont/how depth.
        kept = []
        for block in shaped.blocks:
            if block.key == "sexuality":
                kept.append(
                    block.model_copy(
                        update={
                            "tips": [],
                            "action": (
                                "Детали и практические шаги — в полном доступе."
                                if ru
                                else "Practical steps unlock with full access."
                            ),
                            "detail": (block.detail or "")[:220],
                        }
                    )
                )
            elif block.key == "long_term":
                kept.append(
                    block.model_copy(
                        update={
                            "action": "",
                            "tips": [],
                            "detail": (block.detail or "")[:180],
                        }
                    )
                )
            else:
                # Soft action only — not the full how-to ladder.
                kept.append(block.model_copy(update={"tips": []}))
        shaped.blocks = kept
        shaped.scenarios = []
        shaped.overview_paragraphs = list(shaped.overview_paragraphs[:2])
        meta["locked_layers"] = ["yes_no", "do_dont_how", "sexuality_tips", "scenarios"]
        meta["upsell"] = {
            "title": "Нужен ясный ответ и план" if ru else "Want a clear answer and a plan",
            "body": (
                "С подпиской: да/нет по вашей динамике, что делать, чего не делать и как — по шагам."
                if ru
                else "With a plan: yes/no on your dynamic, what to do, what not to, and how — step by step."
            ),
            "cta_subscribe": "Открыть полный доступ" if ru else "Get full access",
        }
        return shaped, meta

    # paid — full surface + guidance pack
    yn = _yes_no_from_score(overall_score, locale=loc)
    do_items: list[str] = []
    dont_items: list[str] = []
    how_items: list[str] = []
    for block in shaped.blocks:
        if block.action and block.key in ("emotions", "communication", "conflicts"):
            do_items.append(block.action.strip())
        if block.risk and block.key in ("conflicts", "long_term", "sexuality"):
            dont_items.append(block.risk.strip())
        if block.key == "sexuality" and block.tips:
            how_items.extend([t.strip() for t in block.tips if t.strip()][:3])
    for sc in shaped.scenarios:
        if sc.id == "closer":
            how_items.extend([b.strip() for b in sc.bullets if b.strip()][:2])
        if sc.id == "exit" or sc.id == "boundary":
            dont_items.extend([b.strip() for b in sc.bullets if b.strip()][:1])

    meta["guidance"] = {
        "yes_no": yn,
        "do": do_items[:3],
        "dont": dont_items[:3],
        "how": how_items[:4],
    }
    meta["locked_layers"] = []
    return shaped, meta


def apply_paragraph_gate(
    paragraphs: list[str],
    *,
    tier: CompatAccessTier,
) -> tuple[list[str], list[str]]:
    """Returns (free_paragraphs, full_paragraphs_for_client)."""
    all_p = [p for p in paragraphs if str(p).strip()]
    if tier == "guest":
        return all_p[:1], all_p[:1]
    if tier == "registered":
        return all_p[:2], all_p[:2]
    return all_p[:3], all_p
