# Case 09 — Contradictory self-report vs check-ins

**mode:** oneshot (funnel aborted due to timeouts)

## 1. Inputs
```json
{
  "access_tier": "extended",
  "source_depth": "profile_plus_checkins",
  "honesty_line": "Видны первые тенденции из ваших отметок. Это ещё не полный долгосрочный портрет.",
  "person": {
    "first_name": "Оля",
    "gender": "female"
  },
  "birth_date": "1995-12-01",
  "astro": {
    "sun_sign": "sagittarius",
    "element": "fire",
    "modality": "mutable"
  },
  "numerology": {
    "life_path": 5
  },
  "baseline": {
    "archetype_seed": "explorer",
    "element_focus": "fire",
    "rhythm_style": "variable"
  },
  "onboarding": {
    "intent_theme": "freedom",
    "reality_state": "fine",
    "self_notes": [
      "я легко адаптируюсь",
      "мне не нужна рутина",
      "я спокойна в неопределённости"
    ]
  },
  "living": {
    "summary": "На словах — лёгкость; в днях — тревога без плана и срывы при смене планов.",
    "signals": [
      {
        "day": "2026-07-12",
        "mood": "anxious",
        "note": "отменились планы — весь день мимо"
      },
      {
        "day": "2026-07-13",
        "mood": "anxious",
        "note": "нужен был чёткий список"
      },
      {
        "day": "2026-07-14",
        "mood": "irritated",
        "note": "хаос в календаре"
      },
      {
        "day": "2026-07-15",
        "mood": "ok",
        "note": "когда расписала день — легче"
      }
    ],
    "insights": [
      "слова про свободу vs потребность в каркасе"
    ]
  },
  "user_question": null,
  "missing_or_hidden": [],
  "locale": "ru",
  "generation_mode_note": "oneshot_fallback_after_funnel_timeouts"
}
```

## 2. Prompt
```
Ты пишешь **единый портрет человека** для TodayFlow (русский язык).

Вход — JSON с ядром профиля: имя, знак, нумерология, baseline, living (сигналы, инсайты).

Задача: **одна связная карта личности** — без штампов, без «вселенная/поток», без паспорта знака как единственного смысла.
Все текстовые блоки должны быть живыми и персональными — не общие шаблоны.

Поля:
- identity_core, strengths (≥3), growth_zones (≥3)
- relationship_style, money_style, decision_style
- recurring_patterns (≥1), living_changes (или null)
- life_mission, helps (≥2)
- life_spheres: love/sex/money/work/family/kids/body/friends/decisions —
  у каждой how/need/risk/turns_on/turns_off/helps

Верни только JSON с этими полями.


Честность данных: Видны первые тенденции из ваших отметок. Это ещё не полный долгосрочный портрет.

```
```json
{"person": {"first_name": "Оля", "gender": "female"}, "astro": {"sun_sign": "sagittarius", "element": "fire", "modality": "mutable"}, "numerology": {"life_path": 5}, "baseline": {"archetype_seed": "explorer", "element_focus": "fire", "rhythm_style": "variable"}, "living": {"summary": "На словах — лёгкость; в днях — тревога без плана и срывы при смене планов.", "signals": [{"day": "2026-07-12", "mood": "anxious", "note": "отменились планы — весь день мимо"}, {"day": "2026-07-13", "mood": "anxious", "note": "нужен был чёткий список"}, {"day": "2026-07-14", "mood": "irritated", "note": "хаос в календаре"}, {"day": "2026-07-15", "mood": "ok", "note": "когда расписала день — легче"}], "insights": ["слова про свободу vs потребность в каркасе"], "onboarding": {"intent_theme": "freedom", "reality_state": "fine", "self_notes": ["я легко адаптируюсь", "мне не нужна рутина", "я спокойна в неопределённости"]}}, "locale": "ru", "source_depth": "profile_plus_checkins", "user_question": null}
```

## 3. Raw
```

```

## 4. Final
```json
{
  "parsed_contract_current": null,
  "user_facing": {
    "honesty_line": "Видны первые тенденции из ваших отметок. Это ещё не полный долгосрочный портрет.",
    "identity_core": null,
    "strengths": null,
    "growth_zones": null,
    "premium": null
  },
  "validation": {
    "ok": false,
    "errors": []
  },
  "postprocess_changes": [
    "oneshot_not_4step_funnel"
  ],
  "fallback": true,
  "retry": false
}
```

## Tech
```json
{
  "latency_ms": 0,
  "quality_ok": false,
  "fallback": true,
  "mode": "oneshot",
  "note": "Cases 9–10 finished via oneshot after 4-step funnel stalled on ReadTimeout"
}
```
