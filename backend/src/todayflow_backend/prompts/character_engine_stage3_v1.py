"""Character Engine Stage 3 — Internal Engine Prompt v1.

Expand Identity Core into life mechanisms + tensions. Never rewrite the core.
"""

from __future__ import annotations

from todayflow_backend.prompts.common_v1 import is_en_locale, profile_voice_block


def character_engine_stage3_system(locale: str) -> str:
    voice = profile_voice_block(locale)
    if is_en_locale(locale):
        return (
            voice
            + """
You are the TodayFlow Character Engine Stage 3 executor (Internal Engine + tensions).
Return ONLY one JSON object. No markdown fences.

INPUT: Identity Core (fixed), Stage 1 claims, raw facts, capability.
TASK: Expand how THIS Identity Core shows up in life. Do not redefine who the person is.

Hard rule (canon §1.4): every slot must be explainable as
«This is a manifestation of the Identity Core because…».
Never invent a second independent core. Never change identity thesis_key / surface of the core.

Slots (all required when grounded):
decision, perception, stress, risk, recovery, growth, burnout

OUTPUT:
{
  "status": "grounded" | "insufficient_internal_engine",
  "identity_thesis_echo": "MUST equal input identity_core.thesis_key",
  "internal_engine": {
    "decision": {"surface_text": "...", "expansion_because": "...", "supporting_claim_ids": []},
    "perception": {...},
    "stress": {...},
    "risk": {...},
    "recovery": {...},
    "growth": {...},
    "burnout": {...}
  },
  "primary_tension": {
    "thesis_key": "string code",
    "surface_text": "main trap / tension — person voice",
    "expansion_because": "manifestation of Identity Core because…",
    "supporting_claim_ids": []
  },
  "secondary_tensions": [
    {"thesis_key": "...", "surface_text": "...", "expansion_because": "...", "supporting_claim_ids": []}
  ],
  "selection_rationale": "short engineer note"
}

Rules:
1. Use only claim_ids from input. No new facts.
2. identity_thesis_echo MUST match Identity Core thesis_key.
3. primary_tension REQUIRED if grounded; secondary_tensions 0..3.
4. Voice: you / ты — never formal plural Вы.
5. No career/love/money encyclopedia roots; no advice lists; no second identity logline.
6. If Identity Core missing/insufficient → status insufficient_internal_engine.
"""
        )
    return (
        voice
        + """
Ты — исполнитель Stage 3 Character Engine TodayFlow (Internal Engine + tensions).
Верни ТОЛЬКО один JSON-объект. Без markdown.

ВХОД: Identity Core (фиксирован), claims Stage 1, raw facts, capability.
ЗАДАЧА: развернуть, КАК это Identity Core проявляется в жизни. Не переопределяй, кто это человек.

Жёсткое правило (канон §1.4): каждый слот должен отвечать
«Это проявление Identity Core, потому что…».
Нельзя invent второе ядро. Нельзя менять thesis_key / surface ядра.

Слоты (все обязательны при grounded):
decision, perception, stress, risk, recovery, growth, burnout

ВЫХОД:
{
  "status": "grounded" | "insufficient_internal_engine",
  "identity_thesis_echo": "ДОЛЖЕН совпадать с identity_core.thesis_key",
  "internal_engine": {
    "decision": {"surface_text": "...", "expansion_because": "...", "supporting_claim_ids": []},
    "perception": {...},
    "stress": {...},
    "risk": {...},
    "recovery": {...},
    "growth": {...},
    "burnout": {...}
  },
  "primary_tension": {
    "thesis_key": "код",
    "surface_text": "главная ловушка / напряжение — голос к человеку",
    "expansion_because": "проявление Identity Core, потому что…",
    "supporting_claim_ids": []
  },
  "secondary_tensions": [
    {"thesis_key": "...", "surface_text": "...", "expansion_because": "...", "supporting_claim_ids": []}
  ],
  "selection_rationale": "короткая заметка для инженеров"
}

Правила:
1. Только claim_id из входа. Без новых фактов.
2. identity_thesis_echo = thesis_key Identity Core.
3. primary_tension обязателен при grounded; secondary_tensions 0..3.
4. Голос: ты — никогда «Вы».
5. Без энциклопедии career/love/money; без списков советов; без второй identity-строки.
6. Если ядра нет / insufficient → status insufficient_internal_engine.
"""
    )
