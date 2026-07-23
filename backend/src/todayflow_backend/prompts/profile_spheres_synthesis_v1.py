"""profile.spheres.synthesis.v1 — per-sphere practical manifestation map.

Model receives prepared cues + identity/style; must not invent astrology or restate inputs.
"""

from __future__ import annotations

import json
from typing import Any

from todayflow_backend.prompts.common_v1 import is_en_locale


def synthesis_system(locale: str) -> str:
    if is_en_locale(locale):
        return """You create one TodayFlow personal profile block: how the person shows up in a single life sphere.

Do NOT retell the inputs. Do NOT explain astrology. Using only the confirmed characteristics provided, create a practical map of how this person shows up in this sphere.

Rules:
1. Use only information from the input.
2. Do not mention planets, signs, houses, calculations, the system, the model, or sources.
3. Do not restate identity_core or relevant_style — transform them into sphere-specific behavior.
4. Do not claim the person always / regularly / every time does something, or invent past events.
5. Do not forecast events or diagnose.
6. If data is insufficient for a claim, omit that claim rather than inventing.
7. Each field must answer a different question and not repeat the others.
8. Personal but not categorical. Address the reader as "you".
9. Avoid empty abstractions (energy, harmony, potential, special connection) without concrete behavior.
10. No universal advice that would fit almost anyone.

Return ONLY JSON with keys: how, need, risk, turns_on, turns_off, helps.
- how: 2 sentences — observable manifestation in this sphere
- need: 1 sentence — condition that helps them stay themselves here
- risk: 1 sentence — how a strength/need turns into difficulty here
- turns_on: 1 sentence — concrete situation that engages them
- turns_off: 1 sentence — concrete situation that shuts them down
- helps: 1 sentence — one doable action for the typical tension here
"""

    return """Ты создаёшь один блок персонального профиля TodayFlow: проявление личности в конкретной сфере жизни.

Твоя задача — не пересказать входные данные и не объяснять астрологические термины. На основе предоставленных подтверждённых характеристик создай практическую карту того, как человек проявляется в этой сфере.

Правила:
1. Используй только информацию из входных данных.
2. Не упоминай планеты, знаки, дома, расчёты, систему, модель или источники.
3. Не пересказывай identity_core и relevant_style дословно и не копируй их целиком в поля.
4. Преобразуй основания в конкретное проявление внутри указанной сферы.
5. Не утверждай, что человек «всегда», «регулярно», «каждый раз» или уже проходил конкретные ситуации.
6. Не предсказывай события и не ставь диагнозы.
7. Если данных недостаточно для конкретного утверждения — не добавляй его.
8. Каждое поле отвечает на отдельный вопрос и не повторяет другие поля.
9. Текст персональный, но не категоричный. Обращение на «ты».
10. Избегай абстракций без поведения: «энергия», «гармония», «потенциал», «особая связь».
11. Не используй универсальные советы, которые подходят почти каждому.
12. Пиши по-русски.

Перед ответом внутренне проверь:
- Может ли этот текст без изменений подойти большинству людей?
- Повторяет ли он базовый портрет или стиль?
- Описывает ли он именно эту сферу?
- Отличаются ли шесть полей по смыслу?
- Есть ли у каждого утверждения основание во входных данных?

Верни ТОЛЬКО JSON с ключами: how, need, risk, turns_on, turns_off, helps.
- how: 2 предложения — как особенности наблюдаемо проявляются в этой сфере
- need: 1 предложение — какое условие помогает оставаться собой здесь
- risk: 1 предложение — как сила/потребность превращается в затруднение
- turns_on: 1 предложение — конкретная ситуация, включающая интерес/доверие/участие
- turns_off: 1 предложение — конкретная ситуация, выключающая интерес/доверие/участие
- helps: 1 предложение — один выполнимый шаг с действием для типичного напряжения сферы
"""


def build_synthesis_user_payload(pack: dict[str, Any]) -> dict[str, Any]:
    """Structured pack for the synthesis call (no kitchen astrology homework)."""
    cues = pack.get("sphere_cues") if isinstance(pack.get("sphere_cues"), list) else []
    houses = pack.get("house_cues") if isinstance(pack.get("house_cues"), list) else []
    return {
        "contract_version": "profile_spheres_synthesis_input_v0",
        "sphere_name": pack.get("sphere_name"),
        "user_question": pack.get("user_question"),
        "user_value": pack.get("user_value"),
        "identity_core": pack.get("identity_core"),
        "strengths": pack.get("strengths") or [],
        "growth_zones": pack.get("growth_zones") or [],
        "relevant_style": pack.get("relevant_style"),
        "sphere_cues": [str(c.get("text") or "").strip() for c in cues if str(c.get("text") or "").strip()],
        "house_cues": [str(c.get("text") or "").strip() for c in houses if str(c.get("text") or "").strip()],
        "fields": {
            "how": "как особенности наблюдаемо проявляются в этой сфере; 2 предложения",
            "need": "условие, помогающее оставаться собой; 1 предложение",
            "risk": "как сила превращается в затруднение; 1 предложение",
            "turns_on": "конкретная ситуация включения; 1 предложение",
            "turns_off": "конкретная ситуация выключения; 1 предложение",
            "helps": "один выполнимый шаг с действием; 1 предложение",
        },
    }


def format_synthesis_user_message(pack: dict[str, Any], *, locale: str = "ru") -> str:
    """Human-readable user message + JSON payload (task framing first)."""
    payload = build_synthesis_user_payload(pack)
    cues = payload["sphere_cues"]
    houses = payload["house_cues"]
    strengths = payload["strengths"]
    growth = payload["growth_zones"]

    if is_en_locale(locale):
        lines = [
            f"Sphere: {payload['sphere_name']}",
            f"Main question: {payload['user_question']}",
            f"What the user should understand: {payload['user_value']}",
            "",
            "Available grounds:",
            f"Identity core: {payload['identity_core']}",
            f"Strengths: {', '.join(str(x) for x in strengths)}",
            f"Growth zones: {', '.join(str(x) for x in growth)}",
            f"Relevant style: {payload['relevant_style']}",
            "Prepared semantic cues for this sphere:",
            *[f"- {c}" for c in cues],
        ]
        if houses:
            lines.append("House context (only if calculated):")
            lines.extend(f"- {h}" for h in houses)
        else:
            lines.append("House context: (none)")
        lines.extend(
            [
                "",
                "Fill fields how, need, risk, turns_on, turns_off, helps as specified in the system prompt.",
                "Return ONLY JSON. Structured copy of inputs:",
                json.dumps(payload, ensure_ascii=False, indent=2),
            ]
        )
        return "\n".join(lines)

    lines = [
        f"Сфера: {payload['sphere_name']}",
        f"Главный вопрос блока: {payload['user_question']}",
        f"Что пользователь должен понять после чтения: {payload['user_value']}",
        "",
        "Доступные основания:",
        "",
        f"Базовый портрет: {payload['identity_core']}",
        f"Сильные стороны: {', '.join(str(x) for x in strengths)}",
        f"Зоны роста: {', '.join(str(x) for x in growth)}",
        f"Релевантный стиль: {payload['relevant_style']}",
        "",
        "Рассчитанные смысловые признаки для этой сферы:",
        *[f"- {c}" for c in cues],
        "",
    ]
    if houses:
        lines.append("Дополнительный контекст домов (только если рассчитан):")
        lines.extend(f"- {h}" for h in houses)
    else:
        lines.append("Дополнительный контекст домов: (нет)")
    lines.extend(
        [
            "",
            "Заполни поля how, need, risk, turns_on, turns_off, helps по правилам системного промпта.",
            "Верни только JSON. Структурированная копия входов:",
            json.dumps(payload, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)
