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
  "recognition_line": "string — ONE recognition phrase, ≤120 chars; who they are in action; not advice; do not repeat the archetype label",
  "identity_core": "string — 2–3 sentences",
  "strengths": ["string","string","string"],
  "growth_zones": ["string","string","string"]
}

MANDATORY LIFE PATH REQUIREMENT:
Life path is not background — it is a co-voice equal to astro. At least ONE value in
strengths[] or growth_zones[] MUST be grounded in the thematic core of THIS life path
(not astro, not generic psychology) — such that with a different life path (same natal)
that value would read differently. If astro and numerology point the same way — name the
convergence explicitly; do not duplicate both sources as separate filler lines.

Forbidden: writing so that removing life path from the input would leave every field unchanged.

Forbidden: "as an Aries…"; day advice; inventing longitudinal repeats; kitchen/system meta;
repeating archetype name inside recognition_line.
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
  "recognition_line": "строка — ОДНА фраза-узнавание, ≤120 символов; поведение, не совет; не повторяй имя архетипа",
  "identity_core": "строка — 2–3 предложения",
  "strengths": ["строка","строка","строка"],
  "growth_zones": ["строка","строка","строка"]
}

ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ К LIFE PATH:
Life path — не фоновый факт, а со-голос наравне с astro. Если во входе есть
numerology.co_voice (core_ru / themes_ru) — опирайся на них как на канон этого числа.
Как минимум ОДНО значение в strengths[] или growth_zones[] должно опираться на
тематическое ядро именно этого life path (не astro, не общая психология) — так, чтобы
при другом life path (тот же натал) это значение звучало иначе. Если astro и numerology
указывают в одну сторону — усиль совпадение явно, не дублируй одной фразой оба источника.

Запрещено: писать так, что life path физически можно убрать из входа без изменения
итогового текста ни в одном поле.

При конфликте astro и life path (разные направления) — НЕ растворяй число в астро-метафорах
(огонь/лидерство/дисциплина). Явно возьми одну формулировку из numerology.co_voice.themes_ru
в strengths[] или growth_zones[] (можно близкими словами, но тема должна быть узнаваема).

Запрещено: «как Овен…»; советы на день; выдуманные продольные паттерны; мета про систему;
повторять имя архетипа внутри recognition_line.
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

MANDATORY LIFE PATH REQUIREMENT:
Life path is a co-voice equal to astro. At least ONE of relationship_style / money_style /
decision_style MUST be grounded in THIS life path's thematic core — such that a different
life path (same natal) would change that field. Do not write as if life path were removable
without changing any style field.
"""
    else:
        body = """
Ты — шаг 2 воронки портрета профиля. Верни ТОЛЬКО один JSON.

Задача: стили близости / денег / решений для ЭТОГО человека, согласованные с шагом identity.
Не повторяй identity_core дословно; дай новые ракурсы.

Схема:
{
  "contract_version": "profile_funnel_styles_v0",
  "relationship_style": "строка",
  "money_style": "строка",
  "decision_style": "строка"
}

ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ К LIFE PATH:
Life path — со-голос наравне с astro. Если есть numerology.co_voice — используй themes_ru.
Как минимум ОДНО из relationship_style / money_style / decision_style должно опираться на
тематическое ядро именно этого life path — так, чтобы при другом life path (тот же натал)
это поле звучало иначе. Запрещено писать так, что life path можно убрать из входа без
изменения ни одного style-поля.
"""
    return _frame(locale, body)


def patterns_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 3 of the Profile portrait funnel. Return ONLY one JSON.

Primary task (character_patterns): confirmed recurring behavior patterns from living/signals only.
Each pattern must be grounded in the living evidence in the input — not birth chart, not identity paraphrase.
Also fill: living_changes;
life_mission (one direction line grounded in living — not sun-sign destiny / taxonomy filler);
helps (≥2 concrete supports the person already uses — grounded in living, not birth/taxonomy filler).

Forbidden: inventing repeats, mission, or helps without living evidence; day agenda; sun-sign passport as a “pattern”;
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
Также заполни: living_changes;
life_mission (одна строка направления из living — не судьба по знаку / taxonomy filler);
helps (≥2 конкретных опоры, которые человек уже использует — из living, не birth/taxonomy filler).

Запрещено: выдумывать повторы, миссию или опоры без living; повестка дня; паспорт знака как «паттерн»;
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
