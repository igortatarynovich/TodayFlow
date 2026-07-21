"""RU fallback templates for today_contract_v1 — literary observations, not command lists."""

from __future__ import annotations

TODAY_CONTRACT_FALLBACKS_V1_LOCALE = "ru"

# --- Meta: Period = что происходит; Growth = что развивать ---
PERIOD_FALLBACK = "День скорее про последовательные шаги, чем про резкие развороты."
DEVELOPMENT_POINT_FALLBACK = "Тревога любит ускорять — сегодня полезнее замечать, где темп можно оставить ровным."
PRIMARY_ACTION_FALLBACK = "Если успеешь закрыть одну важную вещь до обеда, остаток дня обычно идёт легче."

# --- Relationships: контакт и честность ---
RELATIONSHIPS_OPPORTUNITY_FALLBACK = "Иногда одно короткое ясное сообщение меняет больше длинного разговора."
RELATIONSHIPS_RISK_FALLBACK = "Молчаливая дистанция сегодня легко раздувает угадывание — одна честная фраза обычно дешевле."
RELATIONSHIPS_ACTION_FALLBACK = "Если что-то давно обходится стороной, сегодня уместна одна прямая фраза без драмы."
RELATIONSHIPS_STATUS_FALLBACK = "В отношениях сегодня важнее честный контакт, чем красивая картинка."

# --- Money / work: решения и вектор ---
MONEY_WORK_OPPORTUNITY_FALLBACK = "Один ясный приоритет до обеда даёт больше ясности, чем попытка разгрести всё сразу."
MONEY_WORK_RISK_FALLBACK = "Новые обещания из импульса сегодня легко превращаются в шум."
MONEY_WORK_ACTION_FALLBACK = "Одна задача до видимого результата к вечеру обычно стоит дороже десяти начатых."
MONEY_WORK_STATUS_FALLBACK = "В работе и деньгах сегодня важен один вектор, а не десять параллельных входов."

# --- Family: атмосфера дома (never profile personality) ---
FAMILY_OPPORTUNITY_FALLBACK = "Дома сегодня больше помогает тёплое присутствие, чем скорость решений."
FAMILY_RISK_FALLBACK = "Контроль над близкими, если тема не горит, сегодня скорее добавляет шума."
FAMILY_ACTION_FALLBACK = "Один спокойный бытовой жест часто делает дом заметно легче."
FAMILY_STATUS_FALLBACK = "Дома полезнее спокойный ритм, чем попытка решить всё сразу."

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
