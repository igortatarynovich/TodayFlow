"""Явный мост в дневной Flow / OS поверх `suggested_route` для Guidance."""

from __future__ import annotations

def build_guidance_flow_bridge(
    *,
    lane: str,
    topic: str | None,
    locale: str | None = None,
) -> dict[str, str]:
    """
    Второй маршрут: закрепить разбор в Today или углубить в тематическом OS.
    Клиенты показывают отдельной кнопкой (паритет веб / iOS / будущий Android).
    """
    is_en = (locale or "").startswith("en")
    t = (topic or "").strip()

    if lane == "decision":
        return {
            "href": "/questions/decision?from_guidance=1",
            "label": "Decision OS · закрепить выбор" if not is_en else "Decision OS · anchor the choice",
            "reason": (
                "Сведи разбор к одному проверяемому решению и зафиксируй критерий пересмотра — это слой Decision OS."
                if not is_en
                else "Turn the reading into one testable decision and a revisit criterion in Decision OS."
            ),
            "kind": "decision_os",
        }

    if lane == "love" or t in {"relationships", "family", "intimacy"}:
        return {
            "href": "/today?from_guidance=1&flow=relationship_checkpoint",
            "label": "Today · чекпоинт связи" if not is_en else "Today · relationship checkpoint",
            "reason": (
                "Перенеси вывод расклада в дневной Flow: один честный шаг по контакту и границам, без додумывания."
                if not is_en
                else "Move the spread insight into Today: one honest step on contact and boundaries."
            ),
            "kind": "today_relationship",
        }

    if lane in {"state", "pattern"}:
        return {
            "href": "/today?from_guidance=1&flow=state_checkpoint",
            "label": "Today · стабилизация" if not is_en else "Today · stabilization",
            "reason": (
                "Закрепи разбор в Today как опору дня: сон, нагрузка, один маленький шаг, а не новый круг анализа."
                if not is_en
                else "Anchor the reading in Today as daily support: load, rest, one small step."
            ),
            "kind": "today_state",
        }

    if lane == "money_career" or t in {"work", "money"}:
        return {
            "href": "/today?from_guidance=1&flow=resource_checkpoint",
            "label": "Today · ресурс и шаг" if not is_en else "Today · resource step",
            "reason": (
                "Свяжи вывод с днём: один измеримый шаг по деньгам/роли, чтобы разбор стал действием."
                if not is_en
                else "Link the insight to today: one measurable money/role step."
            ),
            "kind": "today_resource",
        }

    # default: дневной Flow
    return {
        "href": "/today?from_guidance=1",
        "label": "Today · дневной Flow" if not is_en else "Today · daily flow",
        "reason": (
            "Продолжи в Today: фокус дня, риски и один конкретный шаг после расклада."
            if not is_en
            else "Continue in Today: daily focus, risks, and one concrete step after the spread."
        ),
        "kind": "today_default",
    }
