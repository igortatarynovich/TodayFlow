"""Уровень оплаты пользователя (биллинг). Единый источник для /auth/me и narrative."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from todayflow_backend.db.models import Subscription, User

BillingLevel = Literal["free", "lite", "pro"]

# Доступ к оплаченному контенту (Stripe)
SUBSCRIPTION_ACCESS_STATUSES = frozenset({"active", "trialing"})

_LEVEL_RANK: dict[BillingLevel, int] = {"free": 0, "lite": 1, "pro": 2}


@dataclass(frozen=True)
class SubscriptionSnapshot:
    """Сводка по подписке для API и логики глубины инсайтов."""

    level: BillingLevel
    active_plan_id: str | None
    subscription_status: str | None


def _plan_id_to_billing_level(plan_id: str | None) -> BillingLevel:
    """
    Маппинг plan_id (Stripe metadata / наши id) → биллинговый уровень.
    Неизвестный, но оплаченный план → lite (как раньше: не отрезаем доступ).
    """
    p = (plan_id or "").strip().lower()
    if not p:
        return "lite"
    if "pro" in p or "full" in p:
        return "pro"
    if "lite" in p or "plus" in p:
        return "lite"
    return "lite"


def get_subscription_snapshot(user: User, db: Session) -> SubscriptionSnapshot:
    """
    Активные подписки (active / trialing). Если несколько — берём сильнейший план.
    Без Stripe: legacy is_paid → lite.
    """
    rows = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status.in_(SUBSCRIPTION_ACCESS_STATUSES),
        )
        .all()
    )
    if not rows:
        if user.is_paid:
            return SubscriptionSnapshot(level="lite", active_plan_id=None, subscription_status=None)
        return SubscriptionSnapshot(level="free", active_plan_id=None, subscription_status=None)

    best: Subscription | None = None
    best_rank = -1
    for sub in rows:
        lvl = _plan_id_to_billing_level(sub.plan_id)
        r = _LEVEL_RANK[lvl]
        if r > best_rank:
            best_rank = r
            best = sub
    assert best is not None
    return SubscriptionSnapshot(
        level=_plan_id_to_billing_level(best.plan_id),
        active_plan_id=best.plan_id,
        subscription_status=best.status,
    )


def get_subscription_level(user: User, db: Session) -> str:
    """Совместимость с вызовами practices / reports: \"free\" | \"lite\" | \"pro\"."""
    return get_subscription_snapshot(user, db).level
