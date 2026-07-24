# Profile Content Canon v1 (C3)

**Статус:** принято для аудита и контракта (до переключения production generation).  
**Версия:** 1.0 (2026-07-21).  
**Связь:** [SCREEN_CONTRACTS_V1.md](../SCREEN_CONTRACTS_V1.md) §4 · код `profile_content_v1` · текущая генерация `profile_contract_v1` / `profile_disclosure_funnel_v0` · голос [content/TODAYFLOW_VOICE_CANON.md](../content/TODAYFLOW_VOICE_CANON.md) · **surface IA** [PR4_PROFILE_CANON.md](../archive/PR4_PROFILE_CANON.md) · **видимость LLM-выводов** [LLM_USER_VISIBILITY_CONTRACT_V1.md](../LLM_USER_VISIBILITY_CONTRACT_V1.md).  
**Umbrella (выше модуля):** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) — при конфликте с Content/PR-4 побеждает umbrella.  
**Метод оценки:** как Compatibility — вход → полный prompt → raw → final → ручная оценка + Voice rubric.

Профиль — источник персонализации для Today, Compatibility, Tarot и рекомендаций. Качество здесь важнее большинства отдельных модулей.

**UI origin layers (PR-4):** Identity ↔ факты/расчёты · Interpretation ↔ §4.1–4.2 contract · Evidence ↔ `source_depth` + honesty · Deep Sources ↔ natal attach. Day/week UI не входит в content contract Profile. Каждый блок — полная umbrella-цепочка; PR-4 не ослабляет platform gate.

**Personal Model (уже канон):** личность → Snapshot этим конвейером; модули читают Snapshot.  
Соблюдение в коде: [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](../audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md).

---

## 0. Типы данных (не смешивать)

| Тип | Примеры | Можно ли выдавать за «правду о человеке» |
|-----|---------|------------------------------------------|
| **Фактические** | имя, дата/время/место рождения, пол (если указан) | Да |
| **Рассчитанные** | знак, стихия, life path, baseline archetype | Да как расчёт; не как доказанное поведение |
| **Самоописания** | ответы онбординга, check-in | Да как «вы сказали / отметили» |
| **Выводы системы** | портрет LLM, паттерны | Только с `source_depth` и скромной уверенностью |
| **Гипотезы** | «вы всегда…», диагнозы | **Запрещено** выдавать за факт |

---

## 1. Текущий pipeline (аудит)

### 1.1 Что вводит пользователь
- Имя, пол, locale (`user_settings` / `POST /account/core-setup`)
- Дата/время/место рождения (`astro_profiles`)
- Онбординг: intent / reality (часто localStorage / guest session; слабо в portrait LLM)
- Ежедневные ответы: DayConnection, journal / observation diary, feedback

### 1.2 Что считается
- Знак / стихия / модальность, numerology numbers, `baseline` (archetype_seed, element_focus, rhythm_style)
- `living.summary` — **детерминированный** шаблон, не LLM
- Natal summary — attach на read

### 1.3 Где LLM
- **Канон портрета:** `CoreProfileService.build()` → `build_profile_portrait_v1()` → `run_profile_disclosure_funnel_v0()` (до **4 sync** шагов: identity → styles → patterns → spheres)
- Fallback: oneshot `_PROFILE_SYS_RU` или forming shell без LLM

### 1.4 Что в БД
- `core_profile_snapshots` — полный JSON по `(user_id, profile_hash)`
- Generation logs / prompt versions

### 1.5 Что видит пользователь
- Profile V2 (PR-4): Identity · Interpretation · Evidence · Deep Sources (collapsed natal) — **без** day symbols / Living Maps на скролле
- Контракт: `identity_core`, strengths, growth_zones, styles, patterns, life_spheres, …

### 1.6 Что читают другие модули

| Модуль | Как читает | Риск |
|--------|------------|------|
| Today cycle / morning / Compatibility strip | `build_cached_or_baseline` | OK — без LLM |
| **GET /account/core-profile** | `build()` | **LLM на read path** |
| Today narrative, Tarot context, Questions, day_flow, numerology | `build()` | **LLM на read path** |

---

## 2. Архитектурное правило (обязательно) — Canonical Snapshot

```
profile_facts          — факты + расчёты (без интерпретации)
profile_snapshot       — последняя подтверждённая интерпретация (ready) = Canonical Profile Snapshot
profile_generation_job — фоновая генерация (C1-style)
profile_version        — версия контракта/промпта
profile_fingerprint    — хеш разрешённых входов
```

**Compatibility, Today, Tarot, Natal editorial, Practices читают только snapshot/facts.  
Не вызывают `core_profile.build()` / portrait LLM на read path.**

`build()` / portrait funnel допускается только в job runner / явной кнопке «обновить портрет», не в GET побочных модулей.

**Повтор тех же входных данных** (тот же fingerprint) → тот же Snapshot → те же базовые черты личности в любом модуле.  
Модуль может добавить domain-контекст («сегодня», «в этой паре», «эта карта»), но не новый character arc.

Код-ориентир: `services/profile_content_v1/architecture.py` · publish gate как у Compatibility.

---

## 3. Уровни глубины (`source_depth`)

| Значение | Данные | Честность |
|----------|--------|-----------|
| `birth_data_only` | Рождение ± знак/числа | Общий портрет. **Нет** утверждений о реальном поведении |
| `onboarding_answers` | + прямые ответы онбординга | Можно опираться на ответы; **нет** «повторяющихся паттернов» |
| `profile_plus_checkins` | + check-in / diary | Осторожные тенденции |
| `longitudinal_profile` | История недель/месяцев | «В последние недели…» только с опорой в evidence |

UI: без технических терминов — короткая honesty line.

---

## 4. Продуктовые слои

### 4.1 Базовый профиль (после регистрации)

| Поле | Вопрос |
|------|--------|
| `headline` | Одна строка «кто вы» |
| `core_summary` | Краткое ядро |
| `strengths` | Сильные стороны |
| `emotional_style` | Эмоциональные потребности / стиль |
| `communication_style` | Стиль общения |
| `decision_style` | Как принимает решения |
| `energy_sources` | Что даёт энергию |
| `energy_drains` | Что истощает |
| `under_pressure` | Типичные реакции под давлением |
| `inner_tension` | Главный внутренний конфликт |
| `practical_takeaway` | Один практический вывод |
| `confidence` | low \| medium \| high |
| `source_depth` | см. §3 |

Не одна длинная биография. Не «только приятный портрет» и не «разоблачение».

### 4.2 Расширенный (после накопления данных)

`recurring_patterns` · `avoidance_pattern` · `recovery_pattern` · `work_style` · `relationship_needs` · `boundaries` · `current_shift` · `evidence_summary`

Паттерны **запрещены** на `birth_data_only` / осторожны на `onboarding_answers`.

### 4.3 Premium (применение, не длина)

`direct_answer` · `do` · `avoid` · `how` · `what_to_say` · `next_step`  
(+ при вопросе пользователя обязателен `direct_answer`)

---

## 5. Дефекты, которые ищем в текущей генерации

- общие формулировки «для любого»
- противоречия между блоками
- повтор одного тезиса
- выдуманные факты / диагнозы
- категоричность («всегда»)
- всё объясняется знаком
- кальки с EN
- только комплименты или только негатив
- нет практического применения
- `recurring_patterns` / `living_changes` без опоры в living-данных

---

## 6. Review packs

Первый пакет — **10 кейсов** (см. `evals/profile_quality/`):

| N | Состав |
|---|--------|
| 2 | только birth data |
| 2 | после онбординга |
| 2 | частично заполненный профиль |
| 2 | с историей check-in |
| 1 | противоречивые ответы |
| 1 | premium + конкретный вопрос |

Каждый пакет: разрешённый input · system · user · raw (по шагам воронки) · parsed · final · postprocess · validation · model/params · latency · fallback/retry.

---

## 7. Порядок C3

1. Канон + pipeline audit — ✅  
2. Контракты + source_depth в коде  
3. Review runner на **текущей** воронке (baseline качества)  
4. Ручная оценка ≥10 (после C2 publish_gate + Snapshot fixes — воспроизводимо)  
5. Prompt / contract patch (как Compatibility v1.1)  
6. Вынести LLM с read path → jobs  
7. Подключить snapshot-only для Today / Compat / Tarot  
8. Только потом — новый контент в production по умолчанию  

Флаг (позже): `PROFILE_CONTENT_V1` — default off.

Порядок этапов **не переставлять:** C3 → Telemetry → Reference Rate as decision tool → Longitudinal Validation.

### Критерии закрытия этапов

**C3 закрыт**, когда можно честно ответить:

1. Нужны ли действительно четыре LLM-шага?
2. Каждый ли шаг производит **уникальное** знание?
3. Нет ли повторения одних и тех же выводов между разделами Profile?
4. Используется ли prior snapshot как **источник знаний**, а не только как входной контекст?

**Telemetry закрыт**, когда есть не просто события, а ответы на продуктовые вопросы:

1. Какие разделы реально читают?
2. Какие подтверждают пользователи?
3. Где происходит regeneration?
4. Где чаще всего fallback?
5. Как меняется Reference Rate?

**Reference Rate используется**, когда его можно **сравнивать между модулями** (например Today высокий, Tarot низкий) и это влияет на решения — не «красивая метрика», а инструмент приоритизации wiring / prompts / allowlists.

**Longitudinal Validation** — см. §7.3: проверка гипотезы, не фича-эпик.

---

## 7.1 Линза ручного аудита C3 (приоритет ≠ язык)

Русский язык вторичен. Смотреть три вопроса:

### A. Зачем четыре LLM-шага?

Текущая воронка: identity → styles → patterns → spheres (до 4 sync вызовов).  
Гипотеза аудита: часть шагов историческая.

| Вопрос | Если да |
|--------|---------|
| portrait + patterns — одна задача? | Один проход → меньше latency / cost / drift |
| spheres — детерминированная постобработка? | Убрать LLM-шаг |
| Каждый шаг читает один Snapshot разными промптами? | Схлопнуть или явно развести контракты |

P0-симптом уже виден в incomplete review packs: один портрет = десятки минут / timeout.

### B. Накопление знаний

Ищет не красивый текст, а:

> использует ли профиль уже известные знания?

Новый Snapshot «с нуля» при том же fingerprint / без учёта prior snapshot → **P0**.  
Модуль может добавить domain-контекст; не должен переписывать character arc.

### C. Практическая полезность разделов

Каждый блок отвечает на **свой** вопрос пользователя:

| Поле (пример) | Отдельный вопрос |
|---------------|------------------|
| `emotional_style` | Как проживаю эмоции? |
| `decision_style` | Как принимаю решения? |
| `energy_sources` | Откуда беру энергию? |

Главный дефект ожидания: одна мысль разными словами между блоками.

Приоритет кейсов review: **03, 04, 07, 08**, затем остальные.

---

## 7.2 Product metric (после telemetry): Reference Rate

Не техническое качество — проверка, становится ли TodayFlow **системой с памятью**.

**Жёсткое определение (канон):**

> Reference Rate — доля генераций, которые использовали ранее накопленные знания,  
> **которые невозможно было получить только из текущего входа.**

| Считается Reference = да | Считается Reference = нет |
|--------------------------|---------------------------|
| В prompt/контракт вошли поля Snapshot / living / prior patterns, которых нет во входе запроса | Snapshot лишь «был доступен» в БД, но генерация шла только от знаков/дат/вопроса |
| Today/Compat/Tarot цитируют или опираются на prior interpretation | Модуль заново интерпретирует личность из DOB/знаков при наличии Snapshot |
| Profile refresh **обновляет** snapshot от фактов (delta), а не пишет рассказ с нуля | Profile refresh = новый character arc без опоры на prior |

Profile refresh «создал новый snapshot» учитывается отдельно от «прочитал и использовал».

Низкий Reference Rate через недели = Product Model на бумаге, модули живут изолированно.

Связь с C2 telemetry: publish/fallback · regen · save · opens · confirm/reject · **+ Reference Rate**.

---

## 7.3 Reserved after C3: Longitudinal Validation *(не C4)*

Не фича и не content epic. **Проверка гипотезы** после стабильного Profile.

**Гипотеза (канон — не менять без явного product decision):**

> Персональная модель должна изменяться только при накоплении достаточного количества  
> новых подтверждённых фактов, а не из-за повторной генерации или изменения промпта.

Если через полгода формулировка остаётся неизменной — архитектура выдержала проверку временем.

Пример сценария:
- Неделя 1: Profile — «обычно долго принимает решения».
- Через 3 месяца: ежедневные факты показывают быстрые решения.
- Snapshot **должен** сдвинуться от evidence — не от новой истории LLM / нового prompt id.

Критерии проверки:
- изменение Snapshot связано с evidence / Experiences, не с drift промпта и не с regen;
- отсутствие изменения при стабильном поведении — валидный исход;
- Voice Consistency across time, не только across modules.

Статус: **RESERVED** — после закрытия C3 (§7 exit) + Snapshot-on-read; не начинать как C4.

---

## 7.4 Reserved: критерии пересмотра гипотез *(не сейчас)*

§7 отвечает: «когда этап закрыт?».  
После **первых недель** работы с реальными пользователями и telemetry понадобится соседний раздел:

> При каких наблюдениях мы признаём, что гипотеза оказалась неверной?

Это **продуктовые фальсификаторы**, не инженерные exit criteria.  
**Не формализовать и не применять до появления полевых данных.** Черновик кандидатов (заполнить/сузить позже):

| Наблюдение | Возможный вывод |
|-------------|-----------------|
| Reference Rate растёт, а удержание и пользовательские подтверждения — нет | Само по себе использование накопленных знаний не создаёт ценности |
| Longitudinal почти никогда не двигает модель | Порог фактов слишком высокий или модель слишком инертна |
| Consistency высокая, но Today и Tarot воспринимаются как одно и то же по смыслу | «Единый интеллект» скатился в повторение, а не в согласованную персонализацию |

Статус: **RESERVED** — активировать после первых недель real-user telemetry; до этого решения только по §7 exit + данные, не по ощущению текста.

---

## 8. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-07-21 | v1.0 — C3 canon: data types, pipeline audit, layers, source_depth, architecture, eval |
| 2026-07-21 | C3 audit lens: 4-step justification · knowledge accumulation · section usefulness · Reference Rate |
| 2026-07-21 | Reference Rate hardened (memory, not availability); Longitudinal Validation reserved after C3 |
| 2026-07-21 | Stage exit criteria: C3 / Telemetry / Reference Rate-as-tool; Longitudinal = hypothesis test |
| 2026-07-21 | §7.4 reserved: hypothesis falsifiers after first real-user weeks (not active yet) |
| 2026-07-21 | Link PR-4 surface layers (Identity/Interpretation/Evidence/Deep Sources); UI day/week out of Profile |
| 2026-07-21 | Umbrella parent explicit: EXPLAINABLE_COMPUTATION wins over Content/PR-4 on conflict |
