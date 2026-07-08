# DayModel Input Contract

**Статус:** принято (архитектурный шаг P0.1 — между Reference Layer и миграцией данных).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Связь:** [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md), [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §10, [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), код: `backend/.../day_model_v0.py`.

**Предшествует:** editorial scores (P0.3), миграция `tarot_major_arcana.json`, numerology content layer, Reference API.

**P0.2 (форма):** [reference_machine_contract_v1.schema.json](./schemas/reference_machine_contract_v1.schema.json) · [REFERENCE_MACHINE_CONTRACT_V1.md](./schemas/REFERENCE_MACHINE_CONTRACT_V1.md) · CI `reference-machine-contract-schema`.

---

## Жёсткое правило

**Пока нет `reference_machine_contract_v1.schema.json` с зелёным CI — editorial scores (P0.3) не начинаем.**

Также нельзя:

- проектировать Machine Contract «на глаз» без Dependency Map (§3);
- начинать **миграцию JSON** legacy-файлов;
- смешивать Machine и Content в одной записи (валидатор отклоняет).

**Каноническая форма записи** — nested `machine_contract.vector` + enums; см. [REFERENCE_MACHINE_CONTRACT_V1.md](./schemas/REFERENCE_MACHINE_CONTRACT_V1.md). §5 ниже — семантика полей; при расхождении приоритет у JSON Schema.

---

## 1. Параметры DayModel

DayModel — **логический объект дня**, не текст. Шесть обязательных параметров + gate ([DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §10.2).

| Параметр | Смысл | Тип выхода (DayModel) |
|----------|--------|------------------------|
| **Vector** | Доминирующее направление дня после сведения источников | `vector.direction` + `vector.summary` |
| **Tension** | Конфликт **между источниками** (несовпадение шкал) | `tension.summary` + `tension.signals[]` |
| **Opportunity** | Окно, где Vector реализуем | `opportunity.summary` |
| **Risk** | Tension, уточнённый состоянием и поведением пользователя | `risk.summary` |
| **Tempo** | Согласованная скорость дня | `tempo.label` + `tempo.summary` |
| **Strategy** | Класс действия: согласован с Vector, снижает Risk, учитывает человека | `strategy.summary` + `strategy.one_focus` |

**Производные (не из Reference напрямую):**

| Параметр | Кто считает | Вход |
|----------|-------------|------|
| **Opportunity** | DayModel Engine (step 2) | Vector + action_type + intent + spine/foundation |
| **Risk** (финальный) | DayModel Engine (step 3) | Tension draft + Emotional State + Behavior + internal_profile |
| **Strategy** | DayModel Engine (step 3–4) | Vector + Tempo + Risk + intent |

**Gate (§10.10):** пользовательский текст дня допустим только если определены **Vector**, **Tension**, **Risk** (с учётом пользователя). См. `gate` в `day_model_v0`.

---

## 2. Канонические шкалы (Normalization Language)

Все Reference-домены, питающие DayModel, **обязаны** отдавать значения в этом языке. Агрегатор **не** читает prose, keywords и UI-тексты.

### 2.1 Vector — четыре оси (−1 … +1)

Каждый источник отдаёт **четыре score** или явный `null` + `confidence`.

| Scale code | Полюс −1 | Полюс +1 | Влияет на |
|------------|----------|----------|-----------|
| `action_reflection` | Reflection (пауза, наблюдение) | Action (шаг, решение) | Vector, Strategy |
| `expansion_consolidation` | Consolidation (завершение, сжатие) | Expansion (рост, новое) | Vector |
| `self_others` | Self (личный фокус) | Others (связь, переговоры) | Vector, Opportunity |
| `structure_flow` | Flow (гибкость, импровизация) | Structure (рамка, порядок) | Vector, Tension |

**Сведение в `direction` (enum для DayModel v0/v1):**

После взвешенного усреднения осей движок маппит домinant pattern в:

| `direction` | Условие (упрощённо) |
|-------------|---------------------|
| `completion` | consolidation доминирует + action_reflection ≥ 0 |
| `growth` | expansion доминирует |
| `stabilization` | structure доминирует + низкая expansion |
| `conflict` | высокий spread между источниками по любой оси |
| `transition` | слабый сигнал / равновесие осей |

> **Совместимость с кодом сегодня:** `day_model_v0` использует enum `direction` из keyword-classify spine/card/number ([`day_model_v0.py`](../backend/src/todayflow_backend/services/day_model_v0.py)). Целевое состояние — замена keyword-heuristic на scores из §2.1 (**day_model_v1**).

### 2.2 Tempo (enum)

| Value | Смысл |
|-------|--------|
| `slow` | Восстановление, минимум обязательств |
| `steady` | Ровный рабочий режим |
| `dynamic` | Активный, но без форсажа |
| `fast` | Короткие циклы, много решений (осторожно с Risk) |

Источники отдают `tempo_score` ∈ [0, 1] или enum + confidence; агрегатор → финальный `tempo.label`.

> **Сегодня:** tempo в v0 берётся из `fusion.scores` energy 0–100, не из Tarot/Numerology reference.

### 2.3 Risk level (enum)

| Value | Смысл |
|-------|--------|
| `low` | Ошибка маловероятна при базовой дисциплине |
| `medium` | Нужна осознанность, один фокус |
| `high` | Высокий шанс срыва / перегруза / импульса |

Источники отдают `risk_modifier` ∈ {−1, 0, +1} или `risk_level` enum; **финальный Risk** = f(Tension, Emotional load, Behavior, modifiers).

### 2.4 Emotional load (enum)

| Value | Смысл |
|-------|--------|
| `calm` | Стабильный фон |
| `neutral` | Обычный день |
| `intense` | Чувствительность, раздражение, тревога |

Поставщик: **Emotional State** (check-in), не Tarot/Numerology. Маппится в legacy `emotions`: `stable` / `sensitive` / `distorted`.

### 2.5 Action type (enum)

| Value | Смысл |
|-------|--------|
| `start` | Начать новое |
| `continue` | Продолжить начатое |
| `finish` | Завершить / закрыть |
| `leave` | Не трогать / отложить |

Выводится из Vector (`direction`) + numerology action bias; используется в Strategy.

### 2.6 Energy (numeric)

| Field | Range | Поставщики |
|-------|-------|------------|
| `energy_0_100` | 0–100 | Astrology (transit/load), fusion, опционально check-in |

Используется для Tempo и Tension (tempo vs direction).

### 2.7 Confidence (meta, все домены)

| Field | Range | Смысл |
|-------|-------|--------|
| `confidence` | 0.0–1.0 | Насколько надёжен сигнал источника для данного дня |

При `confidence < 0.3` источник **не участвует** в взвешенном среднем (fallback на остальных).

---

## 3. DayModel Dependency Map (P0.1)

**Легенда:** «Обязателен» = без сигнала с `confidence ≥ 0.3` DayModel **не проходит gate** для полного narrative (допустим degraded UI с явной пометкой).

| DayModel Field | Источник | Домен | Вес | Обязателен | Шкалы / поля из Machine Contract |
|----------------|----------|-------|-----|------------|-----------------------------------|
| **Vector** | Tarot card of day | Tarot | 0.40 | Да | `action_reflection`, `expansion_consolidation`, `self_others`, `structure_flow` |
| **Vector** | Personal day number | Numerology | 0.30 | Да | те же 4 оси |
| **Vector** | Daily spine / transits | Astrology | 0.30 | Да | те же 4 оси + `energy_0_100` (partial) |
| **Tension** | Tarot vs Numerology vs Astro | Tarot + Numerology + Astrology | — | Да | pairwise delta по осям; не взвешивается, **conflict detector** |
| **Tension** | (sub) Tarot | Tarot | 0.50 | Да | оси для сравнения |
| **Tension** | (sub) Astrology | Astrology | 0.50 | Да | оси для сравнения |
| **Opportunity** | Derived | Engine | — | Да | Vector + `action_type` + intent + foundation `first_move` |
| **Risk** (draft) | Derived | Engine | — | Да | Tension magnitude + max(`risk_modifier`) по источникам |
| **Risk** (final) | Check-in mood | Emotional State | 0.50 | Да | `emotional_load`, `tempo_cap` |
| **Risk** (final) | Behavior patterns | Behavior / internal_profile | 0.30 | Нет | pattern hints, overload flags |
| **Risk** (final) | Source modifiers | Tarot + Numerology + Astro | 0.20 | Да | `risk_modifier` each |
| **Tempo** | Tarot | Tarot | 0.20 | Нет | `tempo_score` |
| **Tempo** | Numerology | Numerology | 0.40 | Да | `tempo_score` |
| **Tempo** | Astrology | Astrology | 0.40 | Да | `tempo_score`, `energy_0_100` |
| **Tempo** | Check-in energy | Emotional State | 0.30 | Нет | `energy_band` override cap |
| **Strategy** | Derived | Engine | — | Да | Vector + Tempo + Risk + intent; **не** из Reference prose |
| **action_type** | Derived | Engine | — | Да | из Vector `direction` |
| **emotions** (scale) | Check-in | Emotional State | 1.00 | Да | `emotional_load` |

**Правила агрегации Vector:**

```
vector_axis[scale] = Σ (weight_i × score_i × confidence_i) / Σ (weight_i × confidence_i)
```

где `i` ∈ {Tarot, Numerology, Astrology} для данной оси.

**Правила Tension:**

- Для каждой оси: если `max(score) − min(score) ≥ TENSION_THRESHOLD` (default **0.55** на шкале −1…+1) → сигнал tension.
- ≥2 оси в tension **или** Tarot direction class ≠ Astro direction class → `tension.defined = true`.
- Tarot vs Astro в таблице пользователя — **0.50 / 0.50** на этапе **pairwise** сравнения (Numerology включается в triple compare).

**Правила Tempo:**

```
tempo_score = 0.2×tarot + 0.4×numerology + 0.4×astro  (если confidence ok)
→ map to enum slow | steady | dynamic | fast
→ apply min(tempo) cap from Emotional State if emotional_load = intense
```

---

## 4. Обязательность доменов для DayModel

| Domain | DayModel Required | Role | Если отсутствует |
|--------|-------------------|------|------------------|
| **Tarot** | **Да** | Vector 40%, Tension compare, optional Tempo 20% | Gate fail или degraded «карта не выбрана» |
| **Numerology** | **Да** | Vector 30%, Tempo 40% | Gate fail для paid; free — numerology optional по продукту |
| **Astrology** | **Да** | Vector 30%, Tempo 40%, energy | Fallback: generic transit bucket |
| **Emotional State** | **Да** | Risk final, tempo cap, emotions scale | Prompt check-in; Risk = draft only |
| **Behavior** (internal_profile) | Нет | Risk amplifier | Skip |
| **Goals** | Нет | Strategy / Opportunity echo via intent | Skip for DayModel core |
| **Habits** | Нет | Strategy actions (downstream) | Skip |
| **Practice** | Нет | Recommendations after Strategy | Skip |
| **UI Copy** | Нет | Presentation only | Skip |

**Foundation (`daily_foundation.spine`):** не Reference domain, но **сильный prior** для Vector/Astro до полной миграции; в v1 spine должен отдавать те же 4 оси + `confidence`, а не только prose.

---

## 5. Machine Contract — обязательные поля по доменам

Только поля, **необходимые DayModel**. Остальное — Content Contract или другие consumers (Horoscope, Tarot UI).

### 5.1 Tarot (`TarotCard`)

**Файл записи** (P0.3+) должен соответствовать [reference_machine_contract_v1.schema.json](./schemas/reference_machine_contract_v1.schema.json):

```json
{
  "contract_version": "reference_machine_contract_v1",
  "domain": "tarot",
  "entity_code": "tarot.major.07",
  "version": "1.0.0",
  "status": "draft",
  "machine_contract": {
    "vector": {
      "action_reflection": 0.8,
      "expansion_consolidation": 0.3,
      "self_others": -0.2,
      "structure_flow": 0.7
    },
    "tempo": "fast",
    "risk": "medium",
    "risk_modifier": 0.2,
    "emotional_load": "intense",
    "confidence": 0.75
  }
}
```

**Примеры (editorial target, не migration yet):**

| Card | action_reflection | expansion_consolidation | tempo | risk_modifier | direction_hint |
|------|-------------------|-------------------------|-------|---------------|----------------|
| Chariot (VII) | +0.7 | +0.3 | fast (0.85) | +1 | growth |
| Hermit (IX) | −0.8 | −0.2 | slow (0.15) | −1 | transition |
| Tower (XVI) | +0.5 | +0.6 | dynamic (0.7) | +1 | conflict |

### 5.2 Numerology (`PersonalDay` / `CoreNumber`)

```json
{
  "day_value": 7,
  "reduced_value": 7,
  "confidence": 1.0,
  "action_reflection_score": -0.3,
  "expansion_consolidation_score": 0.0,
  "self_others_score": -0.4,
  "structure_flow_score": 0.2,
  "tempo_score": 0.35,
  "risk_modifier": 0,
  "action_type_bias": "continue"
}
```

| Field | Required |
|-------|----------|
| 4 vector axes | Да |
| `tempo_score` | Да |
| `risk_modifier` | Да |
| `action_type_bias` | Да |
| `confidence` | Да |

Life path / personal year — **не** входят в daily Vector (Profile only).

### 5.3 Astrology (`DailyAstroSignal`)

```json
{
  "signal_id": "transit.moon.square.saturn",
  "confidence": 0.85,
  "action_reflection_score": -0.2,
  "expansion_consolidation_score": -0.5,
  "self_others_score": 0.0,
  "structure_flow_score": 0.6,
  "tempo_score": 0.4,
  "energy_0_100": 45,
  "risk_modifier": 1,
  "direction_hint": "stabilization"
}
```

**Агрегация нескольких транзитов:** weighted by `tension_level` из reference aspect, max conflict wins for Tension detector.

Spine from `daily_foundation` — тот же shape, `signal_id: "foundation.spine"`.

### 5.4 Emotional State (`CheckInSnapshot`)

```json
{
  "mood_slug": "tired",
  "energy_band": "low",
  "stress_band": "medium",
  "emotional_load": "intense",
  "tempo_cap": "steady",
  "confidence": 1.0,
  "risk_modifier": 1
}
```

| Field | Required |
|-------|----------|
| `emotional_load` | Да |
| `tempo_cap` | Нет (если intense — default cap) |
| `risk_modifier` | Да |

### 5.5 Behavior (`internal_profile` slice)

Optional:

```json
{
  "overload_tendency": 0.6,
  "pattern_hint": "skips_morning_practice",
  "confidence": 0.5,
  "risk_modifier": 1
}
```

---

## 6. Content Contract — что **не** питает DayModel

Content Contract нужен для LLM и UI **после** фиксации DayModel. Не участвует в агрегации шкал.

| Domain | Content fields (examples) | Consumers |
|--------|---------------------------|-----------|
| Tarot | keywords, advice, warning, reflection_question, ui_short_text | interpret_tarot, Today card reveal |
| Numerology | energy label, usage_hint, avoid_hint, ui_short_text | interpret_number |
| Astrology | category blurbs (love, work, …), spine prose | Horoscope, foundation narrative |
| Emotional State | display labels, system verdict one-liner | check-in UI, tone policy |
| UI Copy | CTA, microcopy | all surfaces |

**Запрет:** использовать `upright` / `advice` text для вычисления Vector — только Machine scores.

---

## 7. Pipeline steps (привязка к Reference)

```
Step 1 — Source signals (Machine only, parallel):
  TarotCard.machine → scores
  PersonalDay.machine → scores
  DailyAstroSignal.machine → scores
  CheckInSnapshot.machine → emotional_load, risk_modifier

Step 2 — Aggregate (Engine):
  Vector axes (weighted)
  Tension (pairwise)
  Tempo (weighted + cap)
  Risk draft
  Opportunity (derived)

Step 3 — User overlay:
  Behavior → Risk final
  intent → Opportunity echo, Strategy

Step 4 — DayModel artifact:
  vector, tension, opportunity, risk, tempo, strategy, gate, scales{}

Step 5 — LLM (Content Contract only as context):
  adapt prose to DayModel; no new directions
```

---

## 8. Gap: `day_model_v0` (код сегодня) vs этот контракт

| Аспект | v0 (сейчас) | v1 (target per this doc) |
|--------|-------------|---------------------------|
| Vector | Keywords on spine / card **name** / number string | 4-axis scores from Reference Machine |
| Tempo | `fusion.scores` energy only | Numerology 0.4 + Astro 0.4 + Tarot 0.2 |
| Tension | Heuristic tempo vs direction, card name class | Pairwise axis delta ≥ threshold |
| Tarot reference | Name string only | Full Machine Contract per card |
| Numerology reference | Value integer only | PersonalDay Machine scores |
| Gate | Partial | Full P0 domain presence |

**Имплементация:** P1.0–P1.12 pipeline · P1.13 `select_day_surface_candidate_v1()`. Preview: `day_model_v1_preview`.

---

## 9. Чеклист перед миграцией JSON

- [x] Dependency Map зафиксирован (§3)
- [x] Шкалы зафиксированы (§2)
- [x] Machine fields per domain (§5)
- [x] JSON Schema `reference_machine_contract_v1` + CI + fixtures
- [x] **P0.3** Editorial draft scores для 22 major arcana — `DATA/reference/tarot/machine/`
- [x] **P0.4** DayModel v1 aggregation test — `reference_machine_loader.py`, `day_model_v1_aggregator.py`, `tests/test_day_model_v1_aggregation.py` (tarot-only preview)
- [x] **P0.5** Numerology machine drafts — `DATA/reference/numerology/machine/` (39 records)
- [x] **P0.7** Astrology Machine Contract — [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md)
- [x] **P0.8** Astrology atomic machine drafts (39: 12+10+12+5)
- [x] **P0.9** Cross-domain validation — [CROSS_DOMAIN_MACHINE_VALIDATION.md](./CROSS_DOMAIN_MACHINE_VALIDATION.md) PASS
- [x] **P1.0–P1.27** DayModel pipeline (interpretation → LLM gate → learning signals → dataset registry) — **реализовано в коде** (`backend/.../day_model_*`, `day_content_*`, tests). Per-step markdown specs удалены 2026-06-23; канон pipeline: [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md), [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md), [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md).
- [ ] Astro signal composer отдаёт validated machine records
- [x] `day_model_v1` читает Machine Contract (multi-source P1.0)
- [ ] Cutover + `reference_version` in generation_logs

---

## 10. Связанные документы (порядок чтения)

1. [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) — taxonomy, catalog §6, freeze  
2. [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) (этот файл) — Dependency Map  
3. [REFERENCE_MACHINE_CONTRACT_V1.md](./schemas/REFERENCE_MACHINE_CONTRACT_V1.md) — JSON Schema формы (P0.2)  
4. P0.3 … → P1.27 ✅ (frozen in code) → **PIM / CUM** ([PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md), [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md)) → ECC → UEM-2  
   Freeze: [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)

---

*При изменении весов, порогов или шкал — bump версию документа и запись в PRODUCT_EXECUTION_TRACKER (P0.1).*
