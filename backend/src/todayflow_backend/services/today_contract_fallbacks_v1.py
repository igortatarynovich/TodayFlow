"""RU fallback templates for today_contract_v1 — literary observations, not command lists."""

from __future__ import annotations

TODAY_CONTRACT_FALLBACKS_V1_LOCALE = "ru"

# --- Meta: Period = что происходит; Growth = что развивать ---
PERIOD_FALLBACK = "День скорее про последовательные шаги, чем про резкие развороты."
DEVELOPMENT_POINT_FALLBACK = (
    "Сегодня полезно замечать, где тревога ускоряет темп — и оставлять его ровным."
)
PRIMARY_ACTION_FALLBACK = "Если успеешь закрыть одну важную вещь до обеда, остаток дня обычно идёт легче."

# --- Relationships ---
RELATIONSHIPS_OPPORTUNITY_FALLBACK = "Иногда одно короткое ясное сообщение меняет больше длинного разговора."
RELATIONSHIPS_RISK_FALLBACK = "Молчаливая дистанция сегодня легко раздувает угадывание — одна честная фраза обычно дешевле."
RELATIONSHIPS_ACTION_FALLBACK = "Если что-то давно обходится стороной, сегодня уместна одна прямая фраза без драмы."
RELATIONSHIPS_STATUS_FALLBACK = "В отношениях сегодня важнее честный контакт, чем красивая картинка."

# --- Work ---
WORK_OPPORTUNITY_FALLBACK = "Один ясный приоритет до обеда даёт больше ясности, чем попытка разгрести всё сразу."
WORK_RISK_FALLBACK = "Новые обещания из импульса сегодня легко превращаются в шум."
WORK_ACTION_FALLBACK = "Одна задача до видимого результата к вечеру обычно стоит дороже десяти начатых."
WORK_STATUS_FALLBACK = "В работе сегодня важен один вектор, а не десять параллельных входов."

# --- Money ---
MONEY_OPPORTUNITY_FALLBACK = "Одно денежное решение по смыслу сегодня сильнее импульсной траты «чтобы стало легче»."
MONEY_RISK_FALLBACK = "Покупка спокойствия импульсом сегодня легко усиливает дыру."
MONEY_ACTION_FALLBACK = "Спроси перед тратой: это нужно или это анестезия?"
MONEY_STATUS_FALLBACK = "В деньгах сегодня важнее ясный жест, чем суета вокруг цифр."

# --- Energy ---
ENERGY_OPPORTUNITY_FALLBACK = "Короткая пауза до усталости сегодня возвращает больше, чем «ещё один час»."
ENERGY_RISK_FALLBACK = "Дожать себя «ещё чуть-чуть» сегодня легко оставляет без ресурса к вечеру."
ENERGY_ACTION_FALLBACK = "Сделай одну короткую паузу до того, как тело потребует её криком."
ENERGY_STATUS_FALLBACK = "Тело сегодня первым чувствует, где держится лишнее напряжение."

# Legacy aliases (read/compat only — prefer fixed-4 keys above)
MONEY_WORK_OPPORTUNITY_FALLBACK = WORK_OPPORTUNITY_FALLBACK
MONEY_WORK_RISK_FALLBACK = WORK_RISK_FALLBACK
MONEY_WORK_ACTION_FALLBACK = WORK_ACTION_FALLBACK
MONEY_WORK_STATUS_FALLBACK = WORK_STATUS_FALLBACK
FAMILY_OPPORTUNITY_FALLBACK = RELATIONSHIPS_OPPORTUNITY_FALLBACK
FAMILY_RISK_FALLBACK = RELATIONSHIPS_RISK_FALLBACK
FAMILY_ACTION_FALLBACK = RELATIONSHIPS_ACTION_FALLBACK
FAMILY_STATUS_FALLBACK = RELATIONSHIPS_STATUS_FALLBACK

DOMAIN_FALLBACKS_V1: dict[str, dict[str, str]] = {
    "relationships": {
        "status": RELATIONSHIPS_STATUS_FALLBACK,
        "opportunity": RELATIONSHIPS_OPPORTUNITY_FALLBACK,
        "risk": RELATIONSHIPS_RISK_FALLBACK,
        "action": RELATIONSHIPS_ACTION_FALLBACK,
    },
    "work": {
        "status": WORK_STATUS_FALLBACK,
        "opportunity": WORK_OPPORTUNITY_FALLBACK,
        "risk": WORK_RISK_FALLBACK,
        "action": WORK_ACTION_FALLBACK,
    },
    "money": {
        "status": MONEY_STATUS_FALLBACK,
        "opportunity": MONEY_OPPORTUNITY_FALLBACK,
        "risk": MONEY_RISK_FALLBACK,
        "action": MONEY_ACTION_FALLBACK,
    },
    "energy": {
        "status": ENERGY_STATUS_FALLBACK,
        "opportunity": ENERGY_OPPORTUNITY_FALLBACK,
        "risk": ENERGY_RISK_FALLBACK,
        "action": ENERGY_ACTION_FALLBACK,
    },
    "_meta": {
        "period": PERIOD_FALLBACK,
        "development_point": DEVELOPMENT_POINT_FALLBACK,
        "primary_action": PRIMARY_ACTION_FALLBACK,
    },
}
