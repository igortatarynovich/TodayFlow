"""
Глубина инсайтов (продуктовая ось) vs биллинг.

Биллинг: free / lite / pro (технические уровни Stripe).
Инсайт: free / pro / premium — насколько глубоко система формулирует понимание пользователя.

Plus (lite) в биллинге = PRO по глубине инсайта.
Full / pro в биллинге = PREMIUM по глубине инсайта.
"""

from __future__ import annotations

from typing import Literal

from sqlalchemy.orm import Session

from todayflow_backend.db.models import User
from todayflow_backend.services.subscription_level import get_subscription_level

InsightDepthTier = Literal["free", "pro", "premium"]


def billing_to_insight_depth(billing: str) -> InsightDepthTier:
    b = (billing or "").strip().lower()
    if b == "pro":
        return "premium"
    if b == "lite":
        return "pro"
    return "free"


def get_insight_depth_tier(user: User, db: Session) -> InsightDepthTier:
    """Глубина инсайтов строго от биллинга (см. get_subscription_snapshot)."""
    return billing_to_insight_depth(get_subscription_level(user, db))
