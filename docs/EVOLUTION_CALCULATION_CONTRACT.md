# Evolution Calculation Contract (ECC)

**Статус:** принято (канон **формулы** Evolution Score и переходов стадий).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Роль:** формализует **из чего** считается Evolution Score (ES), **какие сигналы** влияют, **какие нет**, **веса**, **стадии** и **требования перехода** — до появления поля `evolution_stage` в публичном API.

**Связь:** [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) (стадии и PEG), [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) (milestone gates), [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) (CUM inputs), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (commerce reads month/year, not ES directly).

---

## 0. Gate: API freeze

| Правило | Статус |
|---------|--------|
| **`evolution_stage` в REST/OpenAPI** | **Запрещено** до ECC v1.0 `active` + UEM-2 implementation |
| **`evolution_score` в REST/OpenAPI** | **Запрещено** (internal only) |
| **Commerce / narrative depth по stage** | Только после ECC + CUM P0.8; до этого — legacy heuristics с явной пометкой `degraded` |
| **Изменение весов ES** | Bump версии ECC + запись в PRODUCT_EXECUTION_TRACKER |

**Порядок исполнения (Foundation First):**

```
P0.5 Numerology ✅ → P0.7 AMC ✅ → P0.8 Astro drafts → P0.9 Cross-domain
  → P1.0 DayModel (three sources) → P1.1 CUM → ECC active → UEM-2
```

**Не делать P0.6 / partial aggregator:** DayModel weights 0.4/0.3/0.3 требуют три SoT; два домена = неполный мир.

UEM/Evolution — **потребитель** Reference + DayModel + CUM. Не строить Evolution до второго столпа DayModel (Numerology) и агрегатора.

---

## 1. Что такое Evolution Score

**Evolution Score (ES):** внутренний скаляр **0–1000**, не отображается пользователю как «XP».

**Path Stage:** дискретная ступень Personal Path (`seeker` … `master`) — производная от ES **и** обязательных milestone gates.

ES отвечает на: «насколько устойчиво пользователь **практикует и подтверждает** паттерны», а не «сколько раз открыл приложение».

---

## 2. Входные сигналы (v1)

### 2.1 Влияют на ES

| Сигнал | Вес | Источник | Примечание |
|--------|-----|----------|------------|
| Practice completion | **0.25** | `practice_completed` events, tracker | Подтверждённые сессии |
| Goal / milestone progress | **0.20** | goals domain | Закрытые шаги, не создание цели |
| Rhythm stability | **0.20** | calendar fusion, streaks | Недельная стабильность ритуала |
| Reflection quality | **0.15** | evening check-in, journal (KASP H) | Не пустой текст; min length gate |
| Profile data quality | **0.10** | CUM `confidence.overall`, birth time, Q&A | Multiplier, не прямой ES |
| Account age | **0.10** | account created_at | **Floor only** — не promotion driver |

**Сумма весов:** 1.0 (нормализованный вклад в ES delta за расчётный период).

### 2.2 Не влияют на ES (v1)

| Сигнал | Причина |
|--------|---------|
| Tarot card pulls count | Symbolic consumption ≠ transformation |
| Numerology / astro page views | Reference read, not behavior |
| Login count / session length | Vanity metric |
| Unconfirmed hypotheses (UKM) | Hypothesis не для high-stakes scoring |
| LLM generation count | API volume ≠ evolution |
| Purchases / subscriptions | Commerce не покупает стадию |
| Personal day/month/year **значения** | Reference cycles для DayModel/commerce, не ES |
| Single check-in mood | Emotional State — risk/tempo modifier для DayModel, не ES |

### 2.3 CUM blocks → ES (multipliers)

| CUM block | Эффект |
|-----------|--------|
| `confidence.overall` | Multiplier 0.5–1.0 на promotion eligibility |
| `behavioral_patterns` (confirmed) | Основной положительный вклад в practice/rhythm buckets |
| `active_themes` depth | Gate для `explorer+` |
| Identity completeness | Gate для `architect+` |

---

## 3. Формула (v1 sketch)

Расчёт **еженедельный** (batch job + on-demand для account settings preview).

```
period_score = Σ (weight_i × normalized_signal_i)   # each signal ∈ [0, 1]

ES_next = clamp(ES_prev + round(period_score × 100), 0, 1000)
```

**normalized_signal_i:** per-signal функция с cap (anti-gaming). Пример: practice — min(1.0, sessions_week / target_sessions).

**confidence multiplier** (promotion only):

```
promotion_eligible = (ES >= stage_threshold) AND gates_passed AND (confidence.overall >= stage_min_confidence)
effective_ES_for_promotion = ES × confidence.overall
```

Детальные пороги per signal — в implementation ticket UEM-2; **изменение порогов** = bump ECC minor version.

---

## 4. Стадии и пороги ES

| Stage | Код | ES min | Min confidence | Обязательные gates |
|-------|-----|--------|----------------|-------------------|
| Искатель | `seeker` | 0 | — | default |
| Наблюдатель | `observer` | 80 | 0.3 | 7-day ritual streak **or** 5 confirmed evenings |
| Практик | `practitioner` | 200 | 0.45 | 14-day rhythm + 3 practices/week avg |
| Исследователь | `explorer` | 380 | 0.55 | 1 active theme depth ≥ 2 + goal in progress |
| Архитектор | `architect` | 550 | 0.65 | habit system (≥2 habits tracked 30d) |
| Наставник | `mentor` | 720 | 0.75 | 1 completed cycle (90d) + confirmed path |
| Мастер | `master` | 900 | 0.85 | 2 completed cycles + peer/share opt-in (future) |

**Demotion:** не применяется в v1 (stage sticky down only on account reset / explicit product rule).

Полный список milestone gates — [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md).

---

## 5. Выход ECC → движок

После UEM-2 (read-only v0):

| Consumer | Поле | Источник |
|----------|------|----------|
| Narrative depth / DE-8 | `evolution_stage` | PEG snapshot |
| Symbolic commerce ranking | stage + `personal_month/year` (Reference) | CUM + Numerology machine |
| PIL retrieval bias | stage tier | engine config table UEM §5 |
| API account | `evolution_stage` (optional) | **только** после ECC active |

**Запрещено до UEM-2:** добавлять `evolution_stage` в `CoreProfile`, `/today/*`, OpenAPI без строки в PRODUCT_EXECUTION_TRACKER и ECC version bump.

---

## 6. Версионирование и тесты

| Артеfact | Требование |
|----------|------------|
| ECC document | semver в шапке |
| Fixture ES scenarios | `backend/tests/test_evolution_score_v1.py` (B1.4 ✅ integration path) |
| Golden promotion cases | seeker→observer, practitioner→explorer with/without confidence |
| Regression | изменение веса >0.05 — explicit review |

**Implementation path:** read-only `evolution_score_calculation_v1` in backend; no API; no promotion until UEM-2.

---

- [ ] P0.5 Numerology machine drafts — `active`
- [ ] P0.8 Astrology machine drafts
- [x] P1.0 DayModel multi-source aggregation
- [ ] P1.1 DayModel Interpretation Rules
- [ ] P1.2 CUM
- [x] ECC v1 document (этот файл)
- [ ] ES weekly job + PEG persistence
- [ ] Integration tests green
- [ ] PRODUCT_EXECUTION_TRACKER: UEM-2 row `active`
- [ ] OpenAPI: `evolution_stage` optional on account schema

---

*При изменении весов, порогов или списка «не влияет» — bump ECC version и PRODUCT_EXECUTION_TRACKER.*
