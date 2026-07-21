# Profile Content Canon v1 (C3)

**Статус:** принято для аудита и контракта (до переключения production generation).  
**Версия:** 1.0 (2026-07-21).  
**Связь:** [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) §4 · код `profile_content_v1` · текущая генерация `profile_contract_v1` / `profile_disclosure_funnel_v0`.  
**Метод оценки:** как Compatibility — вход → полный prompt → raw → final → ручная оценка.

Профиль — источник персонализации для Today, Compatibility, Tarot и рекомендаций. Качество здесь важнее большинства отдельных модулей.

**Personal Model (уже канон):** личность → Snapshot этим конвейером; модули читают Snapshot.  
Соблюдение в коде: [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md).

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
- Profile V2: факты · характер · направление (сферы) · живая история · небо
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
4. Ручная оценка ≥10  
5. Prompt / contract patch (как Compatibility v1.1)  
6. Вынести LLM с read path → jobs  
7. Подключить snapshot-only для Today / Compat / Tarot  
8. Только потом — новый контент в production по умолчанию  

Флаг (позже): `PROFILE_CONTENT_V1` — default off.

---

## 8. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-07-21 | v1.0 — C3 canon: data types, pipeline audit, layers, source_depth, architecture, eval |
