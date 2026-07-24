"""Day disclosure prompts v1 — one rich system prompt per funnel step.

These evolve with Day Engine. Child surfaces (day_layer → deepen) always chain
off guide funnel_interpretation when present.
"""

from __future__ import annotations

from todayflow_backend.prompts.common_v1 import (
    day_engine_block,
    is_en_locale,
    profile_layers_block,
    voice_block,
)

# Re-use proven guide funnel copy from the service module to avoid drift during
# the first cut; registry ids still version the surface. Builders wrap with
# shared voice + Day Engine chain so every step carries the product frame.
from todayflow_backend.services.guide_narrative_funnel_v0 import funnel_system_prompts_for_locale


def _frame(locale: str, body: str) -> str:
    return "\n\n".join(
        [
            voice_block(locale),
            day_engine_block(locale),
            profile_layers_block(locale),
            body.strip(),
        ]
    )


def guide_interp_system(locale: str) -> str:
    s1, _, _ = funnel_system_prompts_for_locale(locale)
    return _frame(locale, s1)


def guide_core_system(locale: str) -> str:
    _, s3, _ = funnel_system_prompts_for_locale(locale)
    return _frame(locale, s3)


def guide_satellites_system(locale: str) -> str:
    _, _, s2 = funnel_system_prompts_for_locale(locale)
    return _frame(locale, s2)


def day_layer_personalize_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 1 of the TodayFlow «Day» tab disclosure funnel. Return ONLY one JSON object.

Task: personalize today's thesis for this person BEFORE writing UI copy.
Inputs: funnel_interpretation (canon when present), prior_thesis / context_for_next_surfaces,
day_model, day_engine_brief, ritual_context, intent, visible_profile, internal_profile, user_core, fusion.rhythm_context.

Produce a personalization brief — not final UI strings:
- what lands for THIS person today (1–3 sentences)
- soft edge / overreach risk for them (1–2 sentences)
- one micro-move that fits their bandwidth
- life_now angle (weekly rhythm + discipline signal) as facts, not lectures
- question tone: gentle life-format probe, not "what should I do today"

Schema:
{
  "contract_version": "day_layer_funnel_personalize_v0",
  "what_lands": "string",
  "soft_edge": "string",
  "micro_move": "string",
  "life_now_angle": "string",
  "question_tone": "string",
  "avoid_echo_of_guide": "string — what NOT to repeat verbatim from guide"
}
"""
    else:
        body = """
Ты — шаг 1 воронки вкладки «День» TodayFlow. Верни ТОЛЬКО один JSON.

Задача: персонализировать тезис дня для ЭТОГО человека ДО финальных UI-текстов.
Вход: funnel_interpretation (канон, если есть), prior_thesis / context_for_next_surfaces,
day_model, day_engine_brief, ritual_context, intent, visible_profile, internal_profile, user_core, fusion.rhythm_context.

Выдай brief персонализации — не финальные строки UI:
- что сегодня «ложится» именно на этого человека (1–3 предложения)
- мягкий край / риск перегиба (1–2 предложения)
- один микро-ход под его ресурс
- ракурс life_now (недельный ритм + дисциплина) как факты, не лекция
- тон вопроса: мягкое уточнение формата жизни, не «что делать сегодня»

Схема:
{
  "contract_version": "day_layer_funnel_personalize_v0",
  "what_lands": "string",
  "soft_edge": "string",
  "micro_move": "string",
  "life_now_angle": "string",
  "question_tone": "string",
  "avoid_echo_of_guide": "string — чего НЕ повторять дословно с «Главного»"
}
"""
    return _frame(locale, body)


def day_layer_render_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 2 of the TodayFlow «Day» tab funnel. Return ONLY one JSON object.

Expand day_layer_personalize into UI fields. Do not contradict the personalize brief or funnel_interpretation.
Do not paste day_engine_brief.anchor_summary verbatim into nudge_message or personal_insight_body.
Keep causality: why → what to do, in plain language.
When avoid_echo_of_guide or already_said_in_guide is present — do not repeat those phrases/meanings (weekday ruler, “one important thing”, day color, etc.) verbatim; give a fresh Day-tab angle.
When fixed_day_color is present — the color is locked; never invent another.

Schema:
{
  "nudge_message": "string",
  "nudge_cta_label": "string — short",
  "personal_insight_title": "string",
  "personal_insight_body": "string — 2–4 sentences",
  "personal_insight_chips": ["string","string"],
  "mini_decision_caption": "string — typical extra load for this person today",
  "question_of_day_prompt": "string — soft life-format question",
  "life_now_weekly": "string",
  "life_now_discipline": "string"
}
"""
    else:
        body = """
Ты — шаг 2 воронки вкладки «День» TodayFlow. Верни ТОЛЬКО один JSON.

Разверни day_layer_personalize в поля UI. Не противоречь brief и funnel_interpretation.
Не вставляй day_engine_brief.anchor_summary дословно в nudge_message / personal_insight_body.
Сохрани причинность: почему так → что с этим сделать, бытовым языком.
Если во входе есть avoid_echo_of_guide или already_said_in_guide — не повторяй эти фразы и смыслы (управитель недели, «одна важная вещь», цвет дня и т.п.) дословно; дай новый ракурс вкладки «День».
Если есть fixed_day_color — цвет уже зафиксирован; не называй другой.

Схема:
{
  "nudge_message": "string",
  "nudge_cta_label": "string — коротко",
  "personal_insight_title": "string",
  "personal_insight_body": "string — 2–4 предложения",
  "personal_insight_chips": ["строка","строка"],
  "mini_decision_caption": "string — типичный «лишний» шаг сегодня",
  "question_of_day_prompt": "string — мягкий вопрос про формат жизни",
  "life_now_weekly": "string",
  "life_now_discipline": "string"
}
"""
    return _frame(locale, body)


def spheres_map_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 1 of the TodayFlow «Spheres» disclosure funnel. Return ONLY one JSON.

Task: map today's thesis onto love / family / career / money BEFORE UI lines.
Inputs: funnel_interpretation, prior_thesis, day_model, ritual_context, intent, user_core, rhythm_context.

For each sphere: stance (up|down|neutral), one concrete angle, optional rhythm hook from facts only.

Schema:
{
  "contract_version": "spheres_funnel_map_v0",
  "day_thread": "string — one sentence continuity with guide",
  "spheres": {
    "love": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"},
    "family": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"},
    "career": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"},
    "money": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"}
  }
}
"""
    else:
        body = """
Ты — шаг 1 воронки экрана «Сферы» TodayFlow. Верни ТОЛЬКО один JSON.

Задача: разложить тезис дня по love / family / career / money ДО UI-строк.
Вход: funnel_interpretation, prior_thesis, day_model, ritual_context, intent, user_core, rhythm_context.

Для каждой сферы: stance (up|down|neutral), один конкретный угол, опционально rhythm_hook только из фактов.

Схема:
{
  "contract_version": "spheres_funnel_map_v0",
  "day_thread": "string — одно предложение преемственности с «Главным»",
  "spheres": {
    "love": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"},
    "family": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"},
    "career": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"},
    "money": {"stance":"up|down|neutral","angle":"string","rhythm_hook":"string|null"}
  }
}
"""
    return _frame(locale, body)


def spheres_render_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 2 of the «Spheres» funnel. Return ONLY one JSON.
Turn spheres_map into page copy. Each scenario_tie_in = verb / boundary / one clear step.
If rhythm_context has goals/habits/diary, page_intro or thesis_reminder must echo one recognizable fact.

Schema:
{
  "page_intro": "string — 2 sentences",
  "thesis_reminder": "string",
  "scenario_tie_ins": {
    "love": "string",
    "family": "string",
    "career": "string",
    "money": "string"
  }
}
"""
    else:
        body = """
Ты — шаг 2 воронки «Сферы». Верни ТОЛЬКО один JSON.
Разверни spheres_map в тексты экрана. Каждая scenario_tie_in = глагол / граница / один ясный шаг.
Если в rhythm_context есть цели/привычки/дневник — page_intro или thesis_reminder должны отозваться на узнаваемый факт.

Схема:
{
  "page_intro": "string — 2 предложения",
  "thesis_reminder": "string",
  "scenario_tie_ins": {
    "love": "string",
    "family": "string",
    "career": "string",
    "money": "string"
  }
}
"""
    return _frame(locale, body)


def evening_reflect_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 1 of the TodayFlow evening closure funnel. Return ONLY one JSON.

Task: close the day with continuity — morning intent → what happened → soft landing.
Do not judge. Do not invent completed actions beyond fusion/rhythm facts.

Schema:
{
  "contract_version": "evening_funnel_reflect_v0",
  "morning_thread": "string",
  "day_residue": "string — what may still be open",
  "gentle_close": "string",
  "one_note_for_tomorrow": "string"
}
"""
    else:
        body = """
Ты — шаг 1 воронки вечернего закрытия TodayFlow. Верни ТОЛЬКО один JSON.

Задача: закрыть день с преемственностью — утреннее намерение → что было → мягкая посадка.
Без вины. Не выдумывай сделанных действий сверх фактов fusion/rhythm.

Схема:
{
  "contract_version": "evening_funnel_reflect_v0",
  "morning_thread": "string",
  "day_residue": "string — что ещё может быть открыто",
  "gentle_close": "string",
  "one_note_for_tomorrow": "string"
}
"""
    return _frame(locale, body)


def evening_render_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 2 of the evening funnel. Return ONLY one JSON.
Render evening_reflect into panel fields. Warm, soft, choice-respecting.

Schema:
{
  "panel_intro": "string",
  "outlook_preamble": "string",
  "closure_invitation": "string"
}
"""
    else:
        body = """
Ты — шаг 2 вечерней воронки. Верни ТОЛЬКО один JSON.
Разверни evening_reflect в поля панели. Тон тёплый, мягкий, с уважением к выбору.

Схема:
{
  "panel_intro": "string",
  "outlook_preamble": "string",
  "closure_invitation": "string"
}
"""
    return _frame(locale, body)


def deepen_expand_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 1 of the TodayFlow deepen funnel. Return ONLY one JSON.

Task: expand the chosen topic inside today's thesis — structure the deepening before prose.
Stay inside day_engine_brief / day_model; do not invent a second day.

Schema:
{
  "contract_version": "deepen_funnel_expand_v0",
  "topic_frame": "string",
  "why_this_topic_today": "string",
  "personal_hook": "string",
  "practical_spine": ["string","string","string"],
  "closing_intent": "string"
}
"""
    else:
        body = """
Ты — шаг 1 воронки углубления TodayFlow. Верни ТОЛЬКО один JSON.

Задача: раскрыть выбранный topic внутри тезиса дня — структура до прозы.
Оставайся в рамках day_engine_brief / day_model; не создавай «второй день».

Схема:
{
  "contract_version": "deepen_funnel_expand_v0",
  "topic_frame": "string",
  "why_this_topic_today": "string",
  "personal_hook": "string",
  "practical_spine": ["строка","строка","строка"],
  "closing_intent": "string"
}
"""
    return _frame(locale, body)


def deepen_render_system(locale: str) -> str:
    if is_en_locale(locale):
        body = """
You are step 2 of the deepen funnel. Return ONLY one JSON.
Turn deepen_expand into readable depth: title, body (2–5 short paragraphs), bullets, closing_line.
Balance meaning + one practical step. No categorical predictions.

Schema:
{
  "title": "string",
  "body": "string",
  "bullets": ["string","string","string"],
  "closing_line": "string"
}
"""
    else:
        body = """
Ты — шаг 2 воронки углубления. Верни ТОЛЬКО один JSON.
Разверни deepen_expand в читаемую глубину: title, body (2–5 коротких абзацев), bullets, closing_line.
Баланс «смысл + практический шаг». Без категоричных предсказаний.

Схема:
{
  "title": "string",
  "body": "string",
  "bullets": ["строка","строка","строка"],
  "closing_line": "string"
}
"""
    return _frame(locale, body)
