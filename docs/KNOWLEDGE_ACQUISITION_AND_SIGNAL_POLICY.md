# Knowledge Acquisition & Signal Policy (KASP)

**Статус:** принято (канон **что**, **откуда** и **как** система имеет право собирать данные).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Уровень:** **до** [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) — Knowledge строится **только** из разрешённых и описанных источников.

**Связь:** [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md) (signal → meaning), [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md) (learned → knowledge lifecycle), [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md), [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md), [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (event names), [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md), [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md), [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md).

---

## 0. Главная проблема

Слабое место персонализации — **сбор данных**.

Типичная ошибка: собирать всё подряд → через год миллион events → невозможно извлечь знание.

**KASP отвечает на 4 вопроса:**

1. Какие данные система **имеет право** собирать (концептуально)?  
2. Какие **уровни доверия** у каждого источника?  
3. Какие **каналы сбора** существуют (полный каталог)?  
4. Что **запрещено** (event → knowledge без подтверждения)?

### Цепочка с Acquisition

```
Reference → Profile
  → [Acquisition Channels] → Events → Signals
  → Interpretation Engine → Confirmation → Knowledge → Memory → Context → LLM → Feedback
```

**UKM** применяется только к данным, прошедшим KASP + ILR, и **только** если двигает [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md) §2–§3.

---

## 1. Три класса данных (conceptual)

Система **не смешивает** классы в одном поле без явной метки.

| Класс | Код | Что это | Пример | Может стать Knowledge? |
|-------|-----|---------|--------|------------------------|
| **Явные данные** | `explicit` | пользователь **сообщил** | дата рождения, цель, оценка «это про меня» | → **fact** напрямую |
| **Поведенческие данные** | `behavioral` | пользователь **сделал** | открыл, сохранил, выполнил, пропустил | → **signal** only; knowledge после подтверждения |
| **Выведенные данные** | `inferred` | система **предположила** | интерес к деньгам, вечерняя активность | → **hypothesis** until confirmed |

**Правило:** inferred **никогда** не записывается как fact без explicit confirmation или stable pattern gate.

---

## 2. Три типа знания (knowledge_type)

В [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) каждый Knowledge Atom **обязан** иметь:

| `knowledge_type` | Определение | Источники (типично) | В LLM / рекомендациях |
|------------------|-------------|---------------------|------------------------|
| **`fact`** | проверяемый факт | onboarding, profile questions, user-stated goal/habit | высокий приоритет |
| **`pattern`** | устойчивое поведение | повторяющиеся behavioral signals | высокий после `stable` |
| **`hypothesis`** | рабочая гипотеза | inferred, single events, model guess | **низкий**; см. §6 |

### Запрет

**Hypothesis нельзя** использовать как источник **высокоприоритетных** рекомендаций, push, или жёстких UX-решений **без подтверждения** (§5).

---

## 3. Уровни доверия (trust_tier)

Каждый signal и knowledge atom наследует `trust_tier` от **канала** и **класса данных**.

| trust_tier | Источник | Базовый confidence cap | knowledge_type cap |
|------------|----------|------------------------|---------------------|
| **T1 — very_high** | прямой ответ пользователя | 0.95–1.0 | `fact` |
| **T2 — high** | повторяющееся поведение (≥ stable threshold) | 0.75–0.94 | `pattern` |
| **T3 — medium** | однократное / редкое действие | 0.45–0.74 | `hypothesis` max |
| **T4 — low** | вывод модели / LLM | 0.25–0.55 | `hypothesis` only |
| **T5 — very_low** | предположение по cohort / default | 0.0–0.30 | **не** в персонализацию |

**Правило:** `confidence` atom ≤ cap(`trust_tier`). Повышение tier — только через §5 pipeline.

---

## 4. Каталог каналов сбора (Acquisition Channels)

Каждый канал: **что получаем**, **класс данных**, **trust**, **event types** (если есть), **→ knowledge**.

### A. Onboarding

| | |
|---|---|
| **Получаем** | имя, дата/время/место рождения; 1 intent chip; 1 reality chip (post-signup, не на signup) |
| **Класс** | `explicit` |
| **Trust** | T1 |
| **knowledge_type** | `fact` (birth); intent/reality → signals / ritual_context (день 1 **не** Knowledge Atom UI-fact) |
| **Хранение** | CoreProfile SN + client/server onboarding state |
| **Events** | `core_setup_completed`, `onboarding_intent_selected`, `onboarding_reality_selected` |
| **Маршруты (target)** | `/onboarding/core` · `/onboarding/intent` · `/onboarding/reality` → `/today?first=1` |
| **Код (interim)** | `POST /account/core-setup`; `/profile?setup=core` (legacy — см. [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) §13) |

---

### B. Profile Questions

| | |
|---|---|
| **Получаем** | постепенные ответы (не анкета на 100 вопросов); малые порции по времени |
| **Класс** | `explicit` |
| **Trust** | T1 |
| **knowledge_type** | `fact` |
| **Правило** | один вопрос — один claim; не блокировать UX |
| **Код** | Profile Engine, JTBD routes, `questions.py` |

---

### C. Daily Check-in

| | |
|---|---|
| **Получаем** | mood, energy, stress, focus / operating mode |
| **Класс** | `explicit` (выбор) + `behavioral` (ritual flow) |
| **Trust** | T1 для slug выбора; T3 для skip |
| **knowledge_type** | `fact` (today state RT); patterns over windows |
| **Events** | `mood_selected`, check-in tracking |
| **Код** | Today ritual, `check_ins.json`, fusion |

---

### D. Tracker Events

| | |
|---|---|
| **Получаем** | выполнение, пропуск, streak, relapse |
| **Класс** | `behavioral` |
| **Trust** | T2 при регулярности; T3 на одиночный skip |
| **knowledge_type** | `pattern` after stable; else `hypothesis` |
| **Events** | habit/goal/ascetic tracking, `practice_completed`, `focus_*` |
| **Код** | tracking API, Calendar |

---

### E. Content Interaction

| | |
|---|---|
| **Получаем** | open, save, read depth, repeat view, dismiss |
| **Класс** | `behavioral` |
| **Trust** | T3 single; T2 repeated |
| **knowledge_type** | **hypothesis** until §5 confirmed |
| **Events** | `sphere_opened`, `today_guide_why_opened`, `today_day_history_first_visible`; save/dismiss backlog |
| **Пример anti-pattern** | 1× save про деньги ≠ `money_interest` fact |

---

### F. Calendar Behavior

| | |
|---|---|
| **Получаем** | ритмы, сильные/слабые дни, пропуски, циклы |
| **Класс** | `behavioral` (aggregated) |
| **Trust** | T2 при ≥14d window |
| **knowledge_type** | `pattern` |
| **Events** | fusion scores, day completion, calendar views (backlog) |
| **Код** | `GET /tracking/fusion`, Calendar P3 |

---

### G. Search / Questions

| | |
|---|---|
| **Получаем** | формулировки запросов, темы, повторы |
| **Класс** | `explicit` (текст вопроса) + `behavioral` (repeat) |
| **Trust** | T1 intent per question; T2 theme recurrence |
| **knowledge_type** | `fact` (asked topic); `pattern` (recurring themes) |
| **Ценность** | **очень высокая** для semantic memory |
| **Код** | Guidance, JTBD, `questions.py` |

---

### H. Reflection

| | |
|---|---|
| **Получаем** | вечерние ответы, дневник, заметки |
| **Класс** | `explicit` (user text) |
| **Trust** | T1 для stated feeling; T4 если LLM извлёк тему из текста |
| **knowledge_type** | user statements → `fact`; extracted themes → `hypothesis` until confirmed |
| **Events** | `evening_reflection_submitted`, diary |
| **Privacy** | redaction before LLM; см. DATA_OWNERSHIP |

---

### I. Recommendation Response

| | |
|---|---|
| **Получаем** | что произошло **после** совета (accepted, started, completed, ignored) |
| **Класс** | `behavioral` |
| **Trust** | T2 on completion; T3 on ignore |
| **knowledge_type** | `pattern` for practice effectiveness |
| **Events** | `action_option_selected`, `support_selected`, `practice_completed`, `sphere_feedback` |
| **Link** | обязателен `generation_id` — [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) |

---

## 5. Pipeline: Event → Signal → Confirmation → Knowledge

**Запрещено:** Event → Knowledge напрямую.

### 5.1 Обязательные стадии

```
Event (channel A–I)
  → Signal (normalized)
  → Interpretation Instance (multi-weight, ILR)
  → Confirmation (threshold / user / time)
  → Knowledge Atom (UKM)
  → Memory materialization
```

### 5.2 Confirmation rules (v0)

| Переход | Минимум | Результат knowledge_type |
|---------|---------|--------------------------|
| explicit user answer | 1 ответ | `fact`, T1 |
| behavioral → interest theme | ≥3 signals / 14d **или** ≥5 / 60d | `pattern`, T2 |
| behavioral → interest theme | 1–2 signals | `hypothesis`, T3 — **no strong rec** |
| model / LLM inference | always | `hypothesis`, T4 |
| user rates «да» on feedback | 1 + matching signal | promote hypothesis → `pattern` |
| user «не про меня» | 1 | demote / suppress atom |

### 5.3 Пример (деньги)

| Шаг | Данные |
|-----|--------|
| Event | 1× save post about money |
| Signal | `useful` (weak) |
| Confirmation | **fail** (need ≥3) |
| Knowledge | **не создаётся** `money_interest` pattern; optional `hypothesis` T3 capped, not for rec |

| Шаг | Данные |
|-----|--------|
| Events | 8× opens money sphere, 3× save, 2× «да» feedback |
| Signals | repeated engagement |
| Confirmation | pass (60d window) |
| Knowledge | `interest.money.v1`, `pattern`, T2, confidence 0.88 |

---

## 6. Политика использования hypothesis

| Допустимо | Запрещено |
|-----------|-----------|
| soft copy tuning («возможно, тебе ближе короткий формат») | push «начни денежную цель» |
| A/B exploration с low stakes | habit assignment from hypothesis alone |
| include in LLM slice with `hypothesis` label | present hypothesis as fact in UI |
| prompt to confirm («это про тебя?») | high-pressure CTA |

**Recommendation rank:** `fact` > `pattern` > `hypothesis`; hypothesis weight ≤ 0.3 in ranking blend.

---

## 7. Что нельзя собирать / использовать

| Запрещено | Почему |
|-----------|--------|
| Скрытый сбор без channel id | нарушение KASP |
| Cross-user profiling для individual rec | T5 only, aggregate research |
| Event dump в LLM | token waste + noise |
| Auto-diagnosis (mental health, trauma) | privacy + harm |
| Cohort defaults as user fact | T5 ≠ T1 |
| Permanent fact from single behavioral event | §5 |
| Mixing hypothesis into CoreProfile static SN | ownership violation |

---

## 8. Signal catalog (Learning Signal Layer)

Signals — **нормализованный выход** каналов перед UKM. Расширение [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) §6.

| Signal | Типичный channel | → knowledge domain |
|--------|------------------|-------------------|
| `explicit_stated` | B, H, G | fact |
| `useful` | E, I | interest / format |
| `effective` | I, D | practice |
| `low_relevance` | E | format negative |
| `incomplete` | G, I | prompt strategy |
| `positive_impact` | I, C | practice / mood |
| `suppress_pattern` | E, I | negative |
| `practice_works` | D, I | practice |
| `timing_format_mismatch` | D, E | timing |
| `user_rejected` | I, H | negative / demote |
| `user_confirmed` | I, B | promote hypothesis |

**Правило:** новый signal type — PR + запись здесь + web/iOS parity if client-emitted.

---

## 9. Mapping: channel → UKM atom fields

Каждый Knowledge Atom **обязан** включать:

| Поле | Источник |
|------|----------|
| `acquisition_channel` | A–I |
| `data_class` | explicit \| behavioral \| inferred |
| `trust_tier` | T1–T5 |
| `knowledge_type` | fact \| pattern \| hypothesis |
| `confirmation_stage` | `pending` \| `confirmed` \| `rejected` |
| `evidence_count` | from signals |

---

## 10. Integration & build order

| # | Артефакт | Статус |
|---|----------|--------|
| **KASP-1** | Этот документ (канон channels + policy) | ✅ |
| **KASP-2** | Channel registry in code (enum + OpenAPI) | ⬜ |
| **UKM-1** | Atom schema + fields §9 | ⬜ |
| **UKM-2** | Signal → Knowledge rules (uses §5) | ⬜ |
| **UKM-3** | Knowledge Store | ⬜ |
| **AMLL Gate** | after UKM-3 | ⬜ |

**Порядок:** KASP → UKM → Gate. **Не** gate_decision первым.

---

## 11. Feature DoD (acquisition-aware)

Новая фича с данными:

- [ ] channel id (A–I or new with canon update)  
- [ ] data_class + default trust_tier  
- [ ] event types (if behavioral)  
- [ ] confirmation rule before knowledge  
- [ ] max knowledge_type produced  
- [ ] privacy / user correction path  

---

## 12. Changelog

- **1.0 (2026-05-31)** — первый канон KASP: 3 data classes, 3 knowledge types, trust tiers T1–T5, channels A–I, Event→Signal→Confirmation→Knowledge, hypothesis policy.
