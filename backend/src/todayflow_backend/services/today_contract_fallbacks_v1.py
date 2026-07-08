"""RU fallback templates for today_contract_v1 assembler — short Today navigation copy."""

from __future__ import annotations

TODAY_CONTRACT_FALLBACKS_V1_LOCALE = "ru"

# --- Meta: Period = что происходит; Growth = что развивать ---
PERIOD_FALLBACK = "День лучше подходит для последовательных действий, чем для резких изменений."
DEVELOPMENT_POINT_FALLBACK = "Тренируй способность не ускоряться только из тревоги — день просит ровный темп."
PRIMARY_ACTION_FALLBACK = "Выбери один короткий шаг и сделай его до обеда."

# --- Relationships: контакт и честность ---
RELATIONSHIPS_OPPORTUNITY_FALLBACK = "Прямой разговор сегодня снижает угадывание и напряжение."
RELATIONSHIPS_RISK_FALLBACK = "Сегодня не строй дистанцию молчанием — лучше одна ясная фраза."
RELATIONSHIPS_ACTION_FALLBACK = "Скажи прямо одну вещь, которую обычно обходишь в разговоре."
RELATIONSHIPS_STATUS_FALLBACK = "Сегодня в отношениях важнее честный контакт, чем красивая картинка."

# --- Money / work: решения и вектор ---
MONEY_WORK_OPPORTUNITY_FALLBACK = "Один приоритет до обеда сегодня даёт ясность в деньгах и задачах."
MONEY_WORK_RISK_FALLBACK = "Сегодня не подписывайся на новые обязательства из импульса."
MONEY_WORK_ACTION_FALLBACK = "Выбери одну задачу и доведи её до видимого результата до вечера."
MONEY_WORK_STATUS_FALLBACK = "Сегодня в работе и деньгах важен один вектор и ясное решение."

# --- Family: атмосфера дома (never profile personality) ---
FAMILY_OPPORTUNITY_FALLBACK = "Сегодня в семье помогает тёплое присутствие, а не скорость решений."
FAMILY_RISK_FALLBACK = "Сегодня не тащи контроль на близких, если тема не горит."
FAMILY_ACTION_FALLBACK = "Сделай один бытовой шаг, который сделает дом спокойнее."
FAMILY_STATUS_FALLBACK = "Сегодня дома полезнее создавать спокойный ритм, чем пытаться решить всё сразу."

DOMAIN_FALLBACKS_V1: dict[str, dict[str, str]] = {
    "relationships": {
        "status": RELATIONSHIPS_STATUS_FALLBACK,
        "opportunity": RELATIONSHIPS_OPPORTUNITY_FALLBACK,
        "risk": RELATIONSHIPS_RISK_FALLBACK,
        "action": RELATIONSHIPS_ACTION_FALLBACK,
    },
    "money_work": {
        "status": MONEY_WORK_STATUS_FALLBACK,
        "opportunity": MONEY_WORK_OPPORTUNITY_FALLBACK,
        "risk": MONEY_WORK_RISK_FALLBACK,
        "action": MONEY_WORK_ACTION_FALLBACK,
    },
    "family": {
        "status": FAMILY_STATUS_FALLBACK,
        "opportunity": FAMILY_OPPORTUNITY_FALLBACK,
        "risk": FAMILY_RISK_FALLBACK,
        "action": FAMILY_ACTION_FALLBACK,
    },
    "_meta": {
        "period": PERIOD_FALLBACK,
        "development_point": DEVELOPMENT_POINT_FALLBACK,
        "primary_action": PRIMARY_ACTION_FALLBACK,
    },
}
