"""Map content_v1 contracts onto legacy SignCompatibilityProductSurface for UI."""

from __future__ import annotations

from todayflow_backend.services.compatibility_content_v1.contracts import (
    GuestContentV1,
    RegisteredContentV1,
)
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatAnalysisBlock,
    SignCompatibilityProductSurface,
    SignCompatRoles,
    SignCompatSubscores,
)


def _subscores_from_score(score: int) -> SignCompatSubscores:
    s = max(45, min(95, int(score)))
    return SignCompatSubscores(
        attraction=min(95, s + 4),
        stability=max(45, s - 3),
        conflicts=max(45, s - 1),
        sexuality=min(95, s + 2),
    )


def guest_to_product_surface(content: GuestContentV1) -> SignCompatibilityProductSurface:
    """Finished guest surface — not a slice of registered blocks."""
    return SignCompatibilityProductSurface(
        score_tagline=content.headline,
        subscores=_subscores_from_score(content.score),
        overview_paragraphs=[
            content.summary,
            content.attraction,
            f"Главный риск: {content.main_risk}",
            f"Практический вывод: {content.practical_advice}",
        ],
        blocks=[
            SignCompatAnalysisBlock(
                key="attraction",
                title="Притяжение",
                subtitle="",
                takeaway=content.attraction,
                detail="",
                risk=content.main_risk,
                action=content.practical_advice,
                tips=[],
            )
        ],
        roles=SignCompatRoles(you_bullets=[content.practical_advice], partner_bullets=[]),
        scenarios=[],
    )


def registered_to_product_surface(content: RegisteredContentV1) -> SignCompatibilityProductSurface:
    def block(key: str, title: str, body: str, *, risk: str = "", action: str = "") -> SignCompatAnalysisBlock:
        take = body.strip().split(".")[0].strip()
        if len(take) < 12:
            take = body[:120]
        return SignCompatAnalysisBlock(
            key=key,
            title=title,
            subtitle="",
            takeaway=take[:220],
            detail=body,
            risk=risk,
            action=action,
            tips=[],
        )

    return SignCompatibilityProductSurface(
        score_tagline=content.headline,
        subscores=_subscores_from_score(content.score),
        overview_paragraphs=[content.summary, content.attraction],
        blocks=[
            block("emotions", "Эмоции", content.emotions),
            block("communication", "Общение", content.communication),
            block("conflicts", "Конфликты", content.conflict, risk=content.main_risk),
            block("attraction", "Притяжение", content.attraction),
            block("strengths", "Сильные стороны", content.strengths),
            block("vulnerable", "Уязвимое место", content.vulnerable_spot),
            block("what_helps", "Что помогает", content.what_helps, action=content.practical_advice),
        ],
        roles=SignCompatRoles(
            you_bullets=[content.practical_advice],
            partner_bullets=[content.what_helps],
        ),
        scenarios=[],
    )
