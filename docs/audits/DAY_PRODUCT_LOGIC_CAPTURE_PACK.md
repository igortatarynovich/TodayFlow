# Day Product Logic Capture Pack

**Status:** IMPLEMENTATION — infra + rubric  
**Parent plan:** Day Scenario SoT + capture packs  
**Scenario SoT (target):** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)  
**Lifecycle:** [DAY_STORY_GENERATION_LIFECYCLE_V0.md](./DAY_STORY_GENERATION_LIFECYCLE_V0.md)  
**Date:** 2026-07-25

> Capture around the production day path. Do **not** change prompts, color SoT, UI composition, or formula runtime until packs prove architectural defect classes.
>
> **Нет класса `MODEL`.** Несоответствие = дефект нашей цепочки.

---

## Goal

Для **каждого** дня pack должен доказать:

1. Из фактов следует **одна** история (Пролог → Акт III).
2. Персональность видна (Акт II).
3. Сцены (Акт V) и реквизит (Акт VI) имеют **происхождение** из конфликта — или явно orphan.
4. Сырой DeepSeek → postprocess → UI: где связи сохранились / порвались.
5. Lifecycle: GET vs refresh — когда LLM реально вызывался.

Целевая цепочка продукта:

```text
Факты → Интерпретационный хор (почему) → Главный конфликт (что)
  → Сцены → Реквизит → UI
```

Хор (астрология · карта дня · число дня · натал) — **четыре взгляда на одну историю**, не четыре модуля.

---

## Defect classes (architectural only)

```text
INPUT
THESIS
PROMPT_SCHEMA
RESPONSE_COHERENCE
POSTPROCESS
COLOR_PIPELINE
SURFACE_ORPHAN
SCENE_MISSING
SPHERE_COVERAGE
PARALLEL_FORECAST   # card/number/astro tell rival stories
CHORUS_MUTED        # factors present but not used as explanation of conflict
UI_DEDUP
LIFECYCLE
PROJECTION
VALIDATION
```

**Запрещено:** `MODEL`, «модель выдумала» как финальный диагноз.

---

## What this ships

| Piece | Path |
|-------|------|
| Capture session (ContextVar, off by default) | `backend/.../day_story_capture_session_v0.py` |
| LLM attempt hooks | `day_story_v1.call_day_story_llm_v1` |
| Wire hooks | `day_story_wire_v1._build_day_story_record` |
| CLI harness | `backend/evals/day_story_quality/run_day_product_capture_v0.py` |
| Scenario rubric (target SoT) | `docs/DAY_SCENARIO_V1.md` |

**Not shipped in capture PR:** prompt rewrite, story-derived color as runtime SoT, required humor fields, formula-as-user-text.

---

## Pack schema (one JSON per day)

```text
manifest { case_id, target_date, prompt_version, model, capture_version }
day_spine { … }
interpretive_chorus {
  astrology[]     # named factors → how they explain conflict (or orphan)
  day_card        { name, role: archetype_for_conflict|parallel_module|missing }
  day_number      { value, role: how_to_live_conflict|parallel_module|missing }
  natal[]         # personal why
  chorus_coherent # bool — one story or rival forecasts
}
scenario_acts { … }
color {
  recommended, apply{}, avoid{}, provenance.pipeline, coherence{}
}
spheres { wire_domains[], product_sphere_checklist[] }
recommendations { expect, trap, do, avoid, primary_action }
goals { suggested_from_contract, coherence, origin_scene_id }
affirmations { …, compensates_trap, orphan_universal, origin_scene_id }
humor_and_hints { opportunities[], emitted[], forced_empty_fields: false }
prompt { system, user_full, user_sent, chars }
attempts[] { raw, parsed, after_normalize, after_gate, phrase_hits, status }
final { story slice, today_contract_slice }
lifecycle { get_calls_llm: false, refresh_calls_llm: true, force_rebuild_used, … }
defects[]
editorial_review { q1…q10, notes }
```

---

## Scenario rubric (editorial)

| Act | Question |
|-----|----------|
| Prolog | Что изменилось vs вчера? (`day_shift`) |
| I | Какой сегодня мир (среда)? |
| II | Почему для этого человека день ≠ средний? |
| III | Ровно один конфликт? |
| IV | Последствия (не советы) из конфликта? |
| V | Только релевантные сцены с opportunity/trap? |
| VI | Каждый реквизит с `origin_scene_id`? |
| VII | Вечерний payoff того же конфликта? |

### Editorial checklist (10+)

1. Из входных фактов следует одна история?
2. Видно, почему она персональна?
3. Ровно один конфликт?
4. Сцены только релевантные и из конфликта?
5. Сырой DeepSeek связал логику — или постпроцесс порвал?
6. Цвет из сцены или приклеен?
7. Avoid-цвет усиливает ловушку?
8. do / цели / аффирмации — одна проблема, без копипаста?
9. Ощущение живого автора, не JSON-формы?
10. Что пропало между raw и UI?
11. **Хор:** «Луна в Рыбах» / карта / число **объясняют** конфликт или лежат отдельными прогнозами?
12. Карта = архетип конфликта (не новый сюжет)? Число = способ прохождения (не вторая история)?

---

## Production-faithful rules

- Harness вызывает production path (`_build_day_story_record` / refresh with `force_rebuild=True`) или offline path, который бьёт в те же `build_day_story_interpretation_v1` + `call_day_story_llm_v1`.
- Capture **off** by default — без session поведение = prod.
- Sidecar files only; не раздувать `generation_logs`.

---

## Expected early defects (hypothesis to prove)

- `COLOR_PIPELINE` — color = date preset + catalog, not scene
- `SURFACE_ORPHAN` — goals/affirmations without scene provenance
- `SCENE_MISSING` / `SPHERE_COVERAGE` — Wire Model B ≠ 7 product spheres
- `LIFECYCLE` — GET skips LLM → unavailable/facts-only

---

## Success

5–10 packs → **карта дефектов** по классам выше. Недостаточно «prompt слабый».
