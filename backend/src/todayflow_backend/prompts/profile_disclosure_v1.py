"""Profile disclosure prompts v1 — multi-request portrait layers."""

from __future__ import annotations

from todayflow_backend.prompts.common_v1 import is_en_locale, profile_layers_block, profile_voice_block


def _frame(locale: str, body: str) -> str:
    return "\n\n".join([profile_voice_block(locale), profile_layers_block(locale), body.strip()])


def identity_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 1 of the TodayFlow Profile portrait funnel. Return ONLY one JSON.

Task: identity core — who this person is in life (stable traits), not a sun-sign passport,
not today's agenda, not confirmed recurring patterns from sparse living.

Inputs: person, astro, numerology, baseline; living only as soft background if present.

Schema:
{
  "contract_version": "profile_funnel_identity_v0",
  "identity_core": "string — 2–3 sentences",
  "strengths": ["string","string","string"],
  "growth_zones": ["string","string","string"]
}

Forbidden: "as an Aries…"; day advice; inventing longitudinal repeats; kitchen/system meta.
"""
    else:
        body = """
Ты — шаг 1 воронки портрета профиля TodayFlow. Верни ТОЛЬКО один JSON.

Задача: ядро идентичности — кто этот человек в жизни (устойчивые черты), не паспорт знака,
не повестка «на сегодня», не подтверждённые повторы из скудного living.

Вход: person, astro, numerology, baseline; living — только мягкий фон, если есть.

Схема:
{
  "contract_version": "profile_funnel_identity_v0",
  "identity_core": "string — 2–3 предложения",
  "strengths": ["строка","строка","строка"],
  "growth_zones": ["строка","строка","строка"]
}

Запрещено: «как Овен…»; советы на день; выдуманные продольные паттерны; мета про систему.
"""
    return _frame(locale, body)


def styles_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 2 of the Profile portrait funnel. Return ONLY one JSON.

Task: relationship / money / decision styles for THIS person, consistent with identity step.
Do not repeat identity_core verbatim; add new angles.

Schema:
{
  "contract_version": "profile_funnel_styles_v0",
  "relationship_style": "string",
  "money_style": "string",
  "decision_style": "string"
}
"""
    else:
        body = """
Ты — шаг 2 воронки портрета профиля. Верни ТОЛЬКО один JSON.

Задача: стили близости / денег / решений для ЭТОГО человека, согласованные с шагом identity.
Не повторяй identity_core дословно; дай новые ракурсы.

Схема:
{
  "contract_version": "profile_funnel_styles_v0",
  "relationship_style": "string",
  "money_style": "string",
  "decision_style": "string"
}
"""
    return _frame(locale, body)


def patterns_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 3 of the Profile portrait funnel. Return ONLY one JSON.

Primary task (character_patterns): confirmed recurring behavior patterns from living/signals only.
Each pattern must be grounded in the living evidence in the input — not birth chart, not identity paraphrase.
Also fill: living_changes; life_mission (one grounded line); helps (≥2 concrete supports).

Forbidden: inventing repeats without living evidence; day agenda; sun-sign passport as a “pattern”;
kitchen/system meta (eligibility, engine, snapshot).

Schema:
{
  "contract_version": "profile_funnel_patterns_v0",
  "recurring_patterns": ["string"],
  "living_changes": "string|null",
  "life_mission": "string",
  "helps": ["string","string"]
}
"""
    else:
        body = """
Ты — шаг 3 воронки портрета профиля. Верни ТОЛЬКО один JSON.

Главная задача (character_patterns): подтверждённые повторяющиеся паттерны поведения — только из living/signals.
Каждый паттерн должен опираться на living во входе — не натальная карта и не пересказ identity.
Также заполни: living_changes; life_mission (одна приземлённая строка); helps (≥2 конкретных опоры).

Запрещено: выдумывать повторы без living; повестка дня; паспорт знака как «паттерн»;
kitchen/system мета (eligibility, engine, snapshot).

Схема:
{
  "contract_version": "profile_funnel_patterns_v0",
  "recurring_patterns": ["строка"],
  "living_changes": "string|null",
  "life_mission": "string",
  "helps": ["строка","строка"]
}
"""
    return _frame(locale, body)


def spheres_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 4 of the Profile portrait funnel. Return ONLY one JSON.

Task: fill EVERY life sphere with personalized, living copy for THIS person.
Use prior identity/styles/patterns + natal/numerology/living facts. No generic horoscope filler.
No empty noun pairs. Each field: concrete verb/situation for this person.

Sphere ids (all required): love, sex, money, work, family, kids, body, friends, decisions.

For each sphere object:
- how: how it shows up in their life (2–4 sentences)
- need: what they need there
- risk: where they break
- turns_on: what engages them
- turns_off: what shuts them down
- helps: one practical support line

Schema:
{
  "contract_version": "profile_funnel_spheres_v0",
  "life_spheres": {
    "love": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "sex": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "money": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "work": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "family": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "kids": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "body": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "friends": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "decisions": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"}
  }
}
"""
    else:
        body = """
Ты — шаг 4 воронки портрета профиля. Верни ТОЛЬКО один JSON.

Задача: заполнить КАЖДУЮ сферу жизни персональным живым текстом для ЭТОГО человека.
Опирайся на identity/styles/patterns + натал/числа/living. Без общего гороскопа и пустых штампов.
Каждое поле — конкретная ситуация/глагол для этого человека.

Обязательные id сфер: love, sex, money, work, family, kids, body, friends, decisions.

Для каждой сферы:
- how: как проявляется в жизни (2–4 предложения)
- need: что нужно
- risk: где ломается
- turns_on: что включает
- turns_off: что выключает
- helps: одна практическая опора

Схема:
{
  "contract_version": "profile_funnel_spheres_v0",
  "life_spheres": {
    "love": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "sex": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "money": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "work": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "family": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "kids": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "body": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "friends": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"},
    "decisions": {"how":"…","need":"…","risk":"…","turns_on":"…","turns_off":"…","helps":"…"}
  }
}
"""
    return _frame(locale, body)
