"""Prompt v1 — separate system prompts per freemium layer (RU first)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.compatibility_content_v1.source_depth import depth_honesty_line

PROMPT_VERSION = "compatibility_content_prompt_v1"

_SHARED_RU = """Ты пишешь разбор совместимости для продукта TodayFlow на живом русском.

СТРОГО ЗАПРЕЩЕНО:
— «вам важно найти баланс», «ключ к гармонии», «позвольте себе»
— «союз двух разных энергий», «при открытом общении всё возможно»
— фатализм, терапевтические диагнозы, эзотерический туман
— общие советы, подходящие любой паре
— повторять названия знаков в каждом абзаце
— пересказывать входные данные
— слова: ИИ, LLM, модель, промпт, алгоритм, расчёт, хаб

НУЖНО:
— конкретные бытовые ситуации и узнаваемое поведение
— короткие выводы, нормальный ритм речи
— «ты» к первому человеку пары
— честно соответствовать глубине данных (source_depth)
— не выдумывать факты о партнёре, которых нет во входе

Верни ТОЛЬКО один JSON-объект без markdown.
"""


def system_prompt_guest_v1(*, source_depth: str, locale: str = "ru") -> str:
    honesty = depth_honesty_line(source_depth, locale=locale)  # type: ignore[arg-type]
    return f"""{_SHARED_RU}

СЛОЙ: GUEST — законченный короткий разбор (не обрывок большого текста).
Цель: дать ценность и желание продолжить после регистрации.
Объём пользовательского текста суммарно ~120–180 слов.

Честность данных: {honesty}

JSON-схема:
{{
  "contract_version": "compatibility_content_v1",
  "tier": "guest",
  "source_depth": "{source_depth}",
  "locale": "ru",
  "headline": "одна строка",
  "score": 0,
  "summary": "цельный короткий разбор",
  "attraction": "главный источник притяжения",
  "main_risk": "главный риск",
  "practical_advice": "один практический вывод",
  "locked_preview": ["эмоции и общение", "конфликты и уязвимое место", "что помогает паре"],
  "confidence": "low|medium|high"
}}
"""


def system_prompt_registered_v1(*, source_depth: str, locale: str = "ru") -> str:
    honesty = depth_honesty_line(source_depth, locale=locale)  # type: ignore[arg-type]
    return f"""{_SHARED_RU}

СЛОЙ: REGISTERED — содержательный разбор отношений.
Каждый блок отвечает на СВОЙ вопрос и НЕ повторяет summary.

Честность данных: {honesty}

Блоки и вопросы:
— emotions: как вы чувствуете и проживаете близость?
— communication: как говорите и слышите друг друга?
— conflict: где ломаетесь и как чините?
— attraction: что тянет и что держит?
— strengths: где вы сильны как пара?
— vulnerable_spot: где пара особенно уязвима?
— what_helps: что помогает отношениям работать?

JSON-схема:
{{
  "contract_version": "compatibility_content_v1",
  "tier": "registered",
  "source_depth": "{source_depth}",
  "locale": "ru",
  "headline": "...",
  "score": 0,
  "summary": "короткий обзор без дублирования блоков",
  "attraction": "...",
  "emotions": "...",
  "communication": "...",
  "conflict": "...",
  "strengths": "...",
  "vulnerable_spot": "...",
  "what_helps": "...",
  "main_risk": "...",
  "practical_advice": "...",
  "confidence": "low|medium|high"
}}
"""


def system_prompt_premium_v1(*, source_depth: str, locale: str = "ru") -> str:
    honesty = depth_honesty_line(source_depth, locale=locale)  # type: ignore[arg-type]
    return f"""{_SHARED_RU}

СЛОЙ: PREMIUM — инструмент решения, не «тот же текст подлиннее».
Не повторяй registered-блоки дословно. Дай практический пакет.

Честность данных: {honesty}

verdict — строго одно из: да | скорее да | зависит | скорее нет | нет
do и avoid не должны противоречить друг другу.
what_to_say — готовая короткая формулировка, которую можно сказать партнёру.
Если во входе есть question — заполни direct_answer; иначе null.

JSON-схема:
{{
  "contract_version": "compatibility_content_v1",
  "tier": "premium",
  "source_depth": "{source_depth}",
  "locale": "ru",
  "verdict": "зависит",
  "verdict_reason": "...",
  "do": "...",
  "avoid": "...",
  "how": "...",
  "what_to_say": "...",
  "focus_now": "...",
  "next_step": "...",
  "direct_answer": null,
  "confidence": "medium",
  "score": 0
}}
"""


def build_user_prompt_v1(payload: dict[str, Any]) -> str:
    """Compact user payload for any tier."""
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)
