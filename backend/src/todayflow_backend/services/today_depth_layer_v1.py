"""Today Depth Layer v1 — optional subscriber deepen (not a paywall on base day).

Canon: docs/TODAY_DEPTH_LAYER_V1.md
Base day pack stays full for Free and Paid. surface=deepen generates the **extra**
topic pack only for Trial/Paid (billing lite/pro, including Stripe trialing).
"""

from __future__ import annotations

from typing import Any, Literal

from sqlalchemy.orm import Session

from todayflow_backend.db.models import User
from todayflow_backend.services.subscription_level import get_subscription_level

DEPTH_LAYER_VERSION = "today_depth_layer_v1"

# Menu topics (user-chosen focus). full_day kept for legacy Life Spheres deepen.
DepthTopic = Literal["money", "intimacy", "love", "career", "family", "full_day"]

DEPTH_LAYER_TOPICS: tuple[str, ...] = (
    "money",
    "intimacy",
    "love",
    "career",
    "family",
    "full_day",
)

# First ship menu (chips). full_day stays API-valid but not a chip.
DEPTH_LAYER_MENU_V1: tuple[str, ...] = ("money", "intimacy", "love", "career")


def normalize_depth_topic(raw: str | None) -> str:
    t = (raw or "").strip().lower()
    if t in DEPTH_LAYER_TOPICS:
        return t
    return "full_day"


def can_generate_depth_layer(user: User, db: Session) -> bool:
    """Trial/Paid (billing lite|pro) may generate the extra deepen pack."""
    return get_subscription_level(user, db) in {"lite", "pro"}


def topic_label(topic: str, *, locale: str = "ru") -> str:
    en = (locale or "ru").lower().startswith("en")
    labels = {
        "money": ("Money — risk, number, decision", "Деньги — риск, цифра, решение"),
        "intimacy": ("Intimacy — clear, adult cues", "Близость — точные взрослые подсказки"),
        "love": ("Relationships — wording and boundary", "Отношения — формулировка и граница"),
        "career": ("Work — one decision, one check", "Работа — одно решение и проверка"),
        "family": ("Home circle — one clear move", "Дом и близкие — один ясный ход"),
        "full_day": ("Day thread — cause → step", "Нить дня — причина → шаг"),
    }
    pair = labels.get(topic) or ("Day topic", "Тема дня")
    return pair[0] if en else pair[1]


def topic_value_line(topic: str, *, locale: str = "ru") -> str:
    en = (locale or "ru").lower().startswith("en")
    lines = {
        "money": (
            "Name the risk, the number, and one decision you can verify today.",
            "Назовите риск, цифру и одно решение, которое можно проверить сегодня.",
        ),
        "intimacy": (
            "A precise cue: consent, wording, gesture, or boundary — no empty mystique.",
            "Точный сигнал: согласие, формулировка, жест или граница — без пустой мистики.",
        ),
        "love": (
            "What to say, what to skip, and how you’ll know it worked.",
            "Что сказать, чего не делать, и как понять, что сработало.",
        ),
        "career": (
            "One work choice plus a checkable signal (reply, deadline, scope).",
            "Один рабочий выбор и проверяемый сигнал (ответ, срок, объём).",
        ),
        "family": (
            "One concrete move at home — wording or boundary you can test today.",
            "Один конкретный ход дома — формулировка или граница, проверяемая сегодня.",
        ),
        "full_day": (
            "One causal line from today’s data to one testable step.",
            "Одна причинная нить из данных дня к одному проверяемому шагу.",
        ),
    }
    pair = lines.get(topic) or lines["full_day"]
    return pair[0] if en else pair[1]


def build_depth_layer_menu(*, locale: str = "ru") -> list[dict[str, str]]:
    """Chip menu for UI (Paid generates; Free shows value)."""
    return [
        {
            "topic": t,
            "label": topic_label(t, locale=locale),
            "value": topic_value_line(t, locale=locale),
        }
        for t in DEPTH_LAYER_MENU_V1
    ]


def build_depth_layer_cta_payload(topic: str, *, locale: str = "ru") -> dict[str, Any]:
    """Free-tier response for surface=deepen — soft CTA, base day untouched."""
    en = (locale or "ru").lower().startswith("en")
    t = normalize_depth_topic(topic)
    label = topic_label(t, locale=locale)
    value = topic_value_line(t, locale=locale)
    title = label
    body = (
        (
            f"Your full day is already available. "
            f"A subscription unlocks an analytic pass on «{label}»: {value}\n\n"
            "Optional layer only — the base day stays complete and unlocked."
        )
        if en
        else (
            f"Полный день у вас уже есть. "
            f"Подписка открывает аналитический разбор темы «{label}»: {value}\n\n"
            "Это дополнительный слой — базовый день остаётся полным и открытым."
        )
    )
    return {
        "title": title,
        "body": body,
        "bullets": [
            (
                "Keep reading your full day story — it is already complete."
                if en
                else "Читайте полный рассказ дня — он уже цельный."
            ),
            (
                "Subscribe or start a trial to generate this analytic topic pack."
                if en
                else "Оформите подписку или trial, чтобы получить этот тематический разбор."
            ),
        ],
        "closing_line": (
            "Extra analysis is optional — not a lock on today."
            if en
            else "Доп. разбор опционален — это не замок на сегодня."
        ),
        "depth_layer": {
            "version": DEPTH_LAYER_VERSION,
            "topic": t,
            "access": "cta",
            "can_generate": False,
            "menu": build_depth_layer_menu(locale=locale),
            "subscribe_path": "/account/subscriptions",
        },
    }


def annotate_depth_layer_payload(
    payload: dict[str, Any],
    *,
    topic: str,
    locale: str = "ru",
) -> dict[str, Any]:
    """Attach depth_layer meta to a successful Paid deepen payload."""
    out = dict(payload) if isinstance(payload, dict) else {}
    t = normalize_depth_topic(topic)
    out["depth_layer"] = {
        "version": DEPTH_LAYER_VERSION,
        "topic": t,
        "access": "generated",
        "can_generate": True,
        "menu": build_depth_layer_menu(locale=locale),
    }
    return out
