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
        "money": ("Money — practical moves", "Деньги — практичные ходы"),
        "intimacy": ("Intimacy — franker tips", "Близость — откровеннее"),
        "love": ("Relationships — what to say", "Отношения — что сказать"),
        "career": ("Work — one clear decision", "Работа — одно решение"),
        "family": ("Home circle — deeper", "Дом и близкие — глубже"),
        "full_day": ("Whole day — deeper", "День целиком — глубже"),
    }
    pair = labels.get(topic) or ("Day topic", "Тема дня")
    return pair[0] if en else pair[1]


def topic_value_line(topic: str, *, locale: str = "ru") -> str:
    en = (locale or "ru").lower().startswith("en")
    lines = {
        "money": (
            "A sharper money move for today: risk, number, or one decision.",
            "Более точный денежный ход на сегодня: риск, цифра или одно решение.",
        ),
        "intimacy": (
            "Franker closeness tips: gesture, wording, or a clear boundary.",
            "Откровеннее про близость: жест, формулировка или ясная граница.",
        ),
        "love": (
            "Deeper relationship guidance: what to say and what to skip today.",
            "Глубже про отношения: что сказать и чего не делать сегодня.",
        ),
        "career": (
            "One concrete work decision with a boundary.",
            "Одно конкретное рабочее решение и граница.",
        ),
        "family": (
            "Deeper home-circle guidance for today.",
            "Глубже про дом и близкий круг на сегодня.",
        ),
        "full_day": (
            "A deeper pass on the whole day thread.",
            "Более глубокий разбор нити всего дня.",
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
            f"With a subscription you can deepen «{label}»: {value}\n\n"
            "This is an optional layer — nothing in the base day is locked."
        )
        if en
        else (
            f"Полный день у вас уже есть. "
            f"С подпиской можно углубить тему «{label}»: {value}\n\n"
            "Это дополнительный слой — базовый день ничем не закрыт."
        )
    )
    return {
        "title": title,
        "body": body,
        "bullets": [
            (
                "Keep reading your full day story — it is complete."
                if en
                else "Читайте полный рассказ дня — он уже цельный."
            ),
            (
                "Subscribe or start a trial to generate this deepen pack."
                if en
                else "Оформите подписку или trial, чтобы сгенерировать этот слой."
            ),
        ],
        "closing_line": (
            "Depth is a choice, not a lock on today."
            if en
            else "Глубина — выбор, а не замок на сегодня."
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
