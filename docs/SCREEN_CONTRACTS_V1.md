# Screen Contracts v1

**Статус:** принято (foundation-first — до Engine Projection Specs).  
**Версия:** 1.2 (2026-06-22).  
**Владелец:** Product + Engineering.

**Роль:** **контракт данных и UX** — что пользователь **обязан получить** на каждом экране первого уровня. Не продуктовая формула («навигация»), не engine output.

**Порядок артефактов:**

```
Screen Contracts v1          ← этот документ (что на экране)
        ↓
Engine Projection Specs v1   ← какие projections нужны для сборки
        ↓
Projection implementation    ← Reference / engines / Assembler
```

**Связь:** [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md) · [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) · [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md) · [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) · [TODAY_CONTRACT_ASSEMBLER_MAPPING.md](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md) · Gap: [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md).

---

## 0. Sprint priority (рыночный, не равный backlog)

Люди приходят за **отношениями · деньгами · семьёй · пониманием происходящего**. Главный gap — **Today** (входная дверь). Compatibility / Tarot / Profile — **глубина**; Calendar — **только** если меняет их ответы.

| Tier | ID | Одна фокусная цель |
|------|-----|-------------------|
| **P0.1** | `today_contract_v1` | **3 жизненных домена** + глобальный контекст + рост — не «красивый прогноз» |
| **P0.2** | Compatibility `potential` | «Есть смысл продолжать?» — tier + **условия**, не % |
| **P1** | Living Profile | Паттерны + что меняется во времени (Calendar → Profile) |
| — | Calendar UI | **Не отдельный приоритет** — ценность = влияние на Today завтра |

**Если один спринт:** только **P0.1** `today_contract_v1`. Engine Projection Specs — после P0.1 wire.

---

## 1. Принципы

| Правило | Смысл |
|---------|--------|
| **Screen-first** | Сначала блоки экрана, потом projections |
| **Mandatory vs optional** | Контракт = mandatory; enrich = optional без подмены |
| **Не engine dump** | Raw scores / планеты / traits без слоя Guidance — нарушение контракта |
| **Паритет** | web · iOS · Android — одни и те же mandatory slots |
| **Empty state** | Слот есть; честный fallback («мало данных»), не скрытие блока |
| **PIM loop** | Каждый mandatory slot: **read CUM slice → give → learn**; не data-collection modal; см. [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) §3.1 |

Каждый контракт = **acceptance test** для QA и для Assembler completeness check.

---

---

## 2. Today — архитектура `today_contract_v1` (ADR)

Today = **входная дверь**. Перед OpenAPI / wire — **одна модель**, не две смешанные.

### 2.1 Отвергнутые модели

| Модель | Описание | Почему нет |
|--------|----------|------------|
| **A · 5 равноправных доменов** | Отношения · Деньги · Семья · Период · Рост — все с `status/opportunity/risk/action` | Период и рост **не** «область жизни с четырьмя слотами»; симметрия искусственная |
| **Смешанная (v1.1)** | 3 домена полноценно + период/рост как «домены» с одним полем | Несимметрично; ломает UI и projection |

### 2.2 Принято: Model B — 3 домена + 2 мета-блока

```
┌─────────────────────────────────────────┐
│  global_context.period                  │  ← не домен, одно поле
│  personal_growth.development_point      │  ← не домен, одна рекомендация
├─────────────────────────────────────────┤
│  domains.relationships   │ DomainLens   │
│  domains.money_work      │ DomainLens   │
│  domains.family          │ DomainLens   │
└─────────────────────────────────────────┘
```

**Домен** = жизненная область, на которую пользователь спрашивает: *«что мне важно знать в этой области сегодня?»*  
Ответ — всегда **одинаковая структура** `DomainLens`.

**Не домены:** период (глобальный контекст дня) · личный рост (персональная рекоменция дня).

Рыночно мы закрываем **5 тем** на Today (отношения · деньги · семья · период · рост), но **wire-модель** — 3 + 2, не 5 `domains`.

### 2.3 `DomainLens` — единый тип для всех доменов

| `slot_id` | Смысл | Пример вопроса |
|-----------|--------|----------------|
| `status` | Что **происходит** | «Что сейчас в отношениях?» |
| `opportunity` | Что **помогает** / возможность / поддержка | «Что усиливает связь?» / «Где поддержка в семье?» |
| `risk` | Что **мешает** / риск / напряжение | «Что может навредить?» / «Где напряжение?» |
| `action` | Что **сделать** сегодня | «Один шаг в этой области» |

**UI labels** по домену (copy), **wire ids** всегда `status · opportunity · risk · action`:

| `domain_id` | Label для `opportunity` | Label для `risk` |
|-------------|-------------------------|------------------|
| `relationships` | что помогает | что может навредить |
| `money_work` | где возможность | где риск |
| `family` | где поддержка | где напряжение |

Один компонент `TodayDomainLens` · один projection type `domain_lens_v1` · любой новый домен = новый `domain_id` + тот же lens.

### 2.4 Мета-блоки (не `DomainLens`)

| Блок | `block_id` | Поля | Смысл |
|------|------------|------|--------|
| **Глобальный контекст** | `global_context` | `period: string` | Главный контекст **дня/периода** (фаза, что важно в масштабе дня) |
| **Персональный рост** | `personal_growth` | `development_point: string` | Одна **точка развития** дня (почему реагирую так · что усилить) |

Hero **Main Theme** агрегирует `global_context.period` (+ опционально hint из `personal_growth`), не подменяет домены.

### 2.5 Не substitute

`energy` · `theme` · `insight` · `watch` · `reason` — поля **внутренней сборки** (legacy four areas), не замена `DomainLens`. При P0.1 миграция: assembler **заполняет контракт**, UI **читает контракт**.

---

## 3. Today Contract (P0.1)

**Screen job:** ежедневная навигация по [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md) §3.  
**Архитектура:** Model B (§2.2) — **3 `DomainLens` + `global_context` + `personal_growth`**.

### 3.1 Mandatory structure

| Часть | Тип | Mandatory |
|-------|-----|-----------|
| `domains.relationships` | `DomainLens` | ✅ все 4 slots |
| `domains.money_work` | `DomainLens` | ✅ |
| `domains.family` | `DomainLens` | ✅ (не slug в love) |
| `global_context.period` | string | ✅ |
| `personal_growth.development_point` | string | ✅ |
| `primary_action` | string | ✅ главный шаг дня |
| `progress` | object | ✅ empty OK |

### 3.2 Сквозные блоки Today (из [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md))

| Block | Mandatory | Контракт |
|-------|-----------|----------|
| Main Theme | ✅ | Агрегирует `global_context.period` |
| Focus / Avoid | ✅ | Сводка; не дублировать 3 домена verbatim |
| Action (главный) | ✅ | **Один** главный шаг дня — может echo strongest domain `action` |
| Progress | ✅ | След дня (empty state OK) |
| Symbolic (карта/число) | ✅ | Краткий слой; полный Tarot → экран Tarot |
| Why | по tap | Explainability, не wall of transits |

### 3.3 Минимальный payload — `today_contract_v1` (P0.1)

```yaml
# Reusable type — все life domains
DomainLens:
  status: string
  opportunity: string
  risk: string
  action: string

today_contract_v1:
  global_context:
    period: string                 # не DomainLens
  personal_growth:
    development_point: string      # не DomainLens
  domains:
    relationships: DomainLens
    money_work: DomainLens
    family: DomainLens
  primary_action: string           # echo strongest domain action или отдельный synthesis
  progress: object
  generation_id: string
```

**P0.1 DoD:** Today без вопроса закрывает **3 DomainLens + period + development_point + primary_action**.  
**Anti-pattern:** период/рост как `domains.period` · family только в love slug · `tension/support` как wire ids (только UI labels → `risk/opportunity`).

### 3.4 UI composition (preview)

```
[ Hero ← global_context.period ]
[ personal_growth.development_point ]
[ TodayDomainLens × 3 — один компонент ]
[ primary_action ]
[ progress ]
```

---

## 4. Profile Contract (P1 — Living Profile)

**Screen job:** живая база знаний (не snapshot, не паспорт знака/числа).  
**Ценность Calendar** проявляется здесь — что **меняется** во времени.

### 4.1 Mandatory elements

| # | Element | `profile_element_id` | Что пользователь получает |
|---|---------|----------------------|---------------------------|
| 1 | Кто он | `identity_core` | Стабильный портрет: архетип + 2–3 предложения смысла |
| 2 | Сильные стороны | `strengths` | ≥3 конкретных сильных сторон |
| 3 | Слабые стороны / зоны внимания | `growth_zones` | ≥3 зон внимания (не stigma) |
| 4 | Стиль отношений | `relationship_style` | Как строит близость, границы, конфликт |
| 5 | Стиль денег | `money_style` | Как относится к деньгам, риск, ценность |
| 6 | Стиль решений | `decision_style` | Как выбирает, что тормозит, что ускоряет |
| 7 | Повторяющиеся паттерны | `recurring_patterns` | Что **повторяется** (из Calendar + поведения) |
| 8 | Living changes | `living_changes` | Что **изменилось** за период: усиливается / ослабевает |

### 4.2 Anti-patterns

- Знак зодиака как hero без `identity_core`
- Natal wall на L1 без CTA в глубину
- Статичный текст без `living_changes` после 7+ дней активности

### 4.3 Минимальный payload

```yaml
profile_contract_v1:
  identity_core: string
  strengths: string[]          # min 3 labels or phrases
  growth_zones: string[]
  relationship_style: string
  money_style: string
  decision_style: string
  recurring_patterns: string[]   # min 1 or explicit empty_reason
  living_changes: string | null  # required when activity_threshold met
  profile_snapshot_version: string
```

**Связь с картами 1–6:** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) — Profile cards питают эти элементы.

---

## 5. Compatibility Contract (P0.2 — Potential)

**Screen job:** понимание отношений (L1 рынок). Серьёзный и вирусный формат — **один контракт**, разный tone.

**Контент-слои Guest / Registered / Premium (C2):** см. [COMPATIBILITY_CONTENT_CANON_V1.md](./COMPATIBILITY_CONTENT_CANON_V1.md) — отдельные контракты, `source_depth`, RU voice. Не путать с freemium truncate в `compatibility_access_v0`.

### 5.1 Mandatory elements (result surface)

| # | Element | `compat_element_id` | Что пользователь получает |
|---|---------|---------------------|---------------------------|
| 1 | Что работает | `what_works` | Сильные стороны связи / синергия |
| 2 | Что не работает | `what_fails` | Зоны несовместимости / хроническое трение |
| 3 | Где трение | `friction_points` | Конкретные точки конфликта (не generic) |
| 4 | **Потенциал** | `potential` | **Есть смысл продолжать?** — tier + условия (не %) |
| 5 | Что делать дальше | `next_step` | Один практический шаг или правило пары |

### 5.1.1 `potential` (P0.2 — отдельный блок)

Пользователю не нужен score. Нужен ответ: **есть смысл продолжать или нет?**

| Поле | Тип | Пример |
|------|-----|--------|
| `potential_tier` | `high` \| `medium` \| `low` | «Высокий потенциал» |
| `potential_conditions` | string | «…если оба готовы открыто обсуждать ожидания» |
| `potential_summary` | string | Одна строка для UI (tier + условие) |

**Anti-pattern:** score-only UI без narrative slots. **Hero % — primary UI** (ring + 4 sub-scores + tagline); `potential_tier` — secondary/metadata для engine и learning.

### 5.2 Anti-patterns

- Таблица знаков без `what_works` / `what_fails`
- Score-only UI («78% совместимости») без narrative slots
- Вирусный формат без `next_step` (даже шутка → мягкий insight)

### 5.3 Минимальный payload

```yaml
compatibility_contract_v1:
  pair_id: string
  format_id: string              # living_together | apocalypse | synastry | …
  what_works: string
  what_fails: string
  friction_points: string[]      # min 1
  potential_tier: high | medium | low
  potential_conditions: string
  potential_summary: string      # UI one-liner
  next_step: string
  generation_id: string
```

---

## 6. Tarot Contract

**Screen job:** помощь в решении при напряжении. **Не** «что происходит» (Today).

### 6.1 Mandatory elements

| # | Element | `tarot_element_id` | Что пользователь получает |
|---|---------|-------------------|---------------------------|
| 1 | Новый угол зрения | `new_angle` | Смена перспективы на ситуацию |
| 2 | Скрытый фактор | `hidden_factor` | Что не замечает / недооценивает |
| 3 | Возможный риск | `risk` | Что может усилить проблему |
| 4 | Следующий шаг | `next_step` | Конкретное действие или пауза с критерием |

### 6.2 Anti-patterns

- Описание карты без `new_angle` и `next_step`
- Substitute love/money forecast
- Wall of card keywords

### 6.3 Минимальный payload

```yaml
tarot_contract_v1:
  spread_id: string
  cards: object[]                # positions + card ids
  new_angle: string
  hidden_factor: string
  risk: string
  next_step: string
  profile_lens_applied: boolean
  generation_id: string
```

### 6.4 Question-first entry (ACCEPTED 2026-07-02)

**North star:** продукт строится вокруг **вопроса человека**, не вокруг колоды.

**Главный вопрос раздела:** «На какой вопрос ты хочешь получить новый взгляд сегодня?» — не «что спросить у карт».

**Единица UX:** concern → refinement → spread → ritual → synthesis. Карты — инструмент углубления, не каталог значений.

| Step | Screen job | Product output | Learning (`event_type`) |
|------|------------|----------------|-------------------------|
| 1 Hero | Снять «идём тянуть карты» | Спокойный вход, новый угол | `tarot_session_started` |
| 2 Concern | «Что сейчас занимает мысли?» | 8 доменов + своё поле | `tarot_question_domain_selected` |
| 3 Refine | Уточнить формулировку | Варианты по домену | `tarot_question_refined` |
| 4 Spread | Выбор расклада | Карточки по **вопросам**, не по числу карт | `tarot_spread_selected` |
| 5 Ritual | Эмоциональный выбор карт | Pick + flip (не мгновенный draw) | `tarot_selected`, `tarot_revealed` |
| 6 Synthesis | Ответ на вопрос | См. §6.5 | `first_synthesis_viewed`, `tarot_reading_follow_up` |

**Код (web Phase A):** `frontend/src/lib/tarotQuestionFlowCanon.ts`, `frontend/src/components/tarot/TarotQuestionFlow.tsx`.

### 6.5 Synthesis screen structure (result)

**Принцип:** психологический диалог через карты — не энциклопедия. Главный объект экрана — **вопрос человека**; карты невидимы в UI (смысл только в narrative). **Для всех раскладов и доменов** — один голос: понятный ответ на поставленный вопрос, как разговор с тарологом.

Порядок блоков — **обязателен**:

| # | Block | `tarot_element_id` | Язык |
|---|-------|-------------------|------|
| 1 | Твой вопрос | `user_question` | Дословно вопрос пользователя |
| 2 | Главный ответ | `main_answer` | **Одна мысль** — ответ на вопрос, не структура расклада |
| 3 | Почему именно такой вывод | `story_narrative` | История карт **в диалоге**; без имён карт и позиций |
| 4 | Сейчас самое сложное / То, что уже начинает меняться / Попробуй заметить | `insight_*` | Конкретные жизненные формулировки, не сырой текст карт |
| 5 | Что можно сделать сегодня | `today_suggestion` | **Одна** рекомендация, не список из 3 |
| 6 | Follow-up из расклада | `reading_follow_up` | Чипы по домену («Отпустить», «Понять…») → `tarot_reading_follow_up` |
| 7 | Что дальше? | `next_routes` | Today, goal, practice, save *(опционально)* |

**Запрещено в UI:** имена карт на английском; список карт с thumbnail; «линия расклада», «диалог карт», «контекст вопроса»; «What this means for you»; «Three steps for today»; generic «насколько откликается?» как primary CTA.

**Запрещённые формулировки:** «значение карты», «позиция: …», «что означает карта», «избегайте фаталистического чтения».

**API (`TarotSpreadReading`):** `meaning`, `synthesis_why`, `insight_holding`, `insight_shifting`, `insight_attention`, `today_suggestion`, `follow_up_prompt`, `follow_up_chips[]`.

### 6.6 Today ↔ Tarot bridge

- **Deepen:** карта дня Today → «Исследовать глубже» → первая карта расклада уже выбрана, остаётся добрать N−1.
- **Echo:** после большого расклада Today может ссылаться на карту/тему без «мы посмотрели Today» в copy.

### 6.7 Journey (Phase C)

**«Твоё путешествие через карты»** — narrative history (темы месяца, частые архетипы, эволюция вопросов), не статистика ради статистики. Порог показа: ≥5 `tarot_spread_done` / session events.

### 6.8 Extended payload (target)

```yaml
tarot_question_flow_v1:
  session_id: string
  concern_domain: string          # relationship | work | money | …
  refinement_id: string | null
  question_text: string           # composed user-facing question
  spread_id: string
  synthesis_why: string           # cards in dialogue (story narrative)
  insight_holding: string | null
  insight_shifting: string | null
  insight_attention: string | null
  today_suggestion: string
  follow_up_prompt: string
  follow_up_chips: { id, label }[]
  reading_follow_up_chip_id: string | null   # learning signal
  profile_lens_applied: boolean   # internal only — not shown in UI
  generation_id: string
```

---

## 7. Calendar Contract

**Приоритет:** не standalone. Ценность Calendar = **какие данные изменят ответ Today завтра** (и P1 Profile).

**Screen job:** сбор фактов + сигналов для Living Profile и персонализации Today.

### 7.1 Mandatory elements

| # | Element | `calendar_element_id` | Что пользователь получает |
|---|---------|----------------------|---------------------------|
| 1 | Что происходит фактически | `facts_timeline` | События, отметки, completions по периоду |
| 2 | Закономерности | `visible_patterns` | ≥1 pattern insight из данных *(или empty с объяснением)* |
| 3 | Что улучшается | `improving` | Сфера/метрика с положительной динамикой |
| 4 | Что ухудшается | `worsening` | Сфера/метрика с негативной динамикой |
| 5 | Что влияет на состояние | `state_drivers` | Факторы ↔ настроение/энергия *(корреляция, не магия)* |

### 7.2 Anti-patterns

- Только чеклисты без `visible_patterns` / `state_drivers` на обзоре периода
- Эзотерика без tie к фактам пользователя

### 7.3 Минимальный payload

```yaml
calendar_contract_v1:
  period: { start, end }
  facts_timeline: object[]       # day records, habits, mood, …
  visible_patterns: string[]     # min 1 or empty_reason
  improving: string | null
  worsening: string | null
  state_drivers: string[]        # min 1 when mood/energy data exists
```

### 7.4 Profile loop (mandatory behavior)

Calendar data **должен** питать `profile_contract_v1.living_changes` и `recurring_patterns` при threshold — см. [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md) §6.

---

## 8. Screen → Answer Contract mapping

| Screen | Primary `need_id` examples | Answer Contract |
|--------|---------------------------|-----------------|
| Today | `need_daily_*`, domain needs | §3 slots = mandatory answer elements |
| Profile | `need_self_understanding` | §4 = Identity retention |
| Compatibility | `need_relationship_*` | §5 = love contracts |
| Tarot | `need_decision_clarity` | §6 = decision slice |
| Calendar | facts / patterns | §7 → feeds Profile |

---

## 9. Assembler completeness (preview)

**Today legacy bridge:** [TODAY_CONTRACT_ASSEMBLER_MAPPING.md](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md) — до OpenAPI.

До Engine Projection Specs Assembler проверяет:

```
for screen in opened:
  for mandatory_slot in SCREEN_CONTRACT[screen]:
    assert slot.present and slot.not_raw_engine_dump
```

Projection Specs позже мапят: `projection_field` → `slot_id`.

---

## 10. Definition of Done (v1)

- [ ] OpenAPI / internal DTO names align with `*_contract_v1` payloads (можно partial v0).
- [ ] Gap analysis: [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md).
- [ ] Today UI: 3 domain lenses + period + growth — review against §3.
- [ ] Compatibility result: 5 elements §5 — review (уже близко в трекере 2026-03-27).
- [ ] Profile: 8 elements §4 — gap analysis vs current cards.
- [ ] Tarot result: 4 elements §6 — gap analysis.
- [ ] Calendar overview: 5 elements §7 — gap analysis.
- [ ] **Engine Projection Specs v1** — только после green checklist выше.

---

## 11. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-22 | v1.0 — five screen contracts + Today domain slot model |
| 2026-06-22 | v1.1 — §0 sprint priority; Today market questions; family tension/support; P0.2 potential_tier; Calendar demoted; Living Profile P1 |
| 2026-06-22 | v1.2 — ADR Model B: 3 DomainLens + global_context + personal_growth; unified slot ids; отвергнуты Model A и смешанная v1.1 |
