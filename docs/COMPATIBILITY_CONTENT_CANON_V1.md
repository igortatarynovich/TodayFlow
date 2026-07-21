# Compatibility Content Canon v1

**Статус:** guest + registered approved under feature flag (human review v1.1). Premium — не широко.  
**Версия:** 1.1 (2026-07-21).  
**Владелец:** Product + Content + Engineering.  
**Связь:** [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) §5 · freemium access `compatibility_access_v0` · jobs C1 · код `compatibility_content_v1` · голос [content/TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md).

**Роль:** продуктовый контракт слоёв Guest / Registered / Premium, глубина данных (`source_depth`), голос RU и quality bar.  
Не инфраструктура генерации (C1). Не обрезание одного LLM-ответа под тариф.

**Personal Model:** Compatibility анализирует взаимодействие Snapshot A × Snapshot B (или честный shallow `source_depth`).  
Не строить психопортрет из дат/знаков при наличии Snapshot.  
Code gap: [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md).

---

## 0. Принцип freemium

| Ошибка | Правило |
|--------|---------|
| Guest = обрезанный Registered | **Запрещено.** Guest — отдельный законченный контракт. |
| Premium = Registered + длина | **Запрещено.** Premium — инструмент решения, отдельный контракт. |
| Один промпт → shape_for_tier | **Запрещено для v1-контента.** Каждый слой — свой prompt + schema. |
| Текст глубже данных | **Запрещено.** `source_depth` ограничивает формулировки. |

**Rollout (2026-07-21):** Guest + Registered — `COMPATIBILITY_CONTENT_V1=1` (publish_gate в `compatibility_enrichment_v0`). Premium — не включать широко до ≥5 реальных вопросов. Промпт не трогать до пользовательских данных; следующий контроль — telemetry.

---

## 1. Роли слоёв

### 1.1 Guest

**Цель:** ощутимая ценность + желание продолжить (регистрация), не «обрывок».

| Поле | Назначение |
|------|------------|
| `headline` | Одна строка про динамику этой пары |
| `score` | 0–100 (как сейчас в UI) |
| `summary` | Короткий цельный разбор (ядро 120–180 слов суммарно с блоками) |
| `attraction` | Главный источник притяжения |
| `main_risk` | Главный риск |
| `practical_advice` | Один практический вывод |
| `locked_preview` | Preview закрытых разделов (что откроется после регистрации) — без выдачи содержимого |
| `confidence` | `low` \| `medium` \| `high` — скромно для zodiac_only |
| `source_depth` | см. §3 |

**Объём:** 120–180 слов пользовательского текста (без `locked_preview` мета-подписей).  
**LLM:** для guest можно не вызывать автоматически (C1); baseline обязан быть **парно-специфичным**, не 12 универсальных фраз.

### 1.2 Registered

**Цель:** содержательный разбор отношений. Каждый блок — отдельный вопрос.

| Поле | Вопрос блока |
|------|----------------|
| `emotions` | Как вы чувствуете и проживаете близость? |
| `communication` | Как вы говорите и слышите друг друга? |
| `conflict` | Где ломаетесь и как чините? |
| `attraction` | Что тянет и что держит? |
| `strengths` | Где вы сильны как пара? |
| `vulnerable_spot` | Где пара особенно уязвима? |
| `what_helps` | Что помогает отношениям работать? |

Плюс общие: `headline`, `score`, `summary`, `main_risk`, `practical_advice`, `confidence`, `source_depth`.

**Не включать** в registered: полный premium-verdict pack, сценарии «да/нет» как финальный verdict.

### 1.3 Premium

**Цель:** инструмент для принятия решений — полезнее, не длиннее.

| Поле | Назначение |
|------|------------|
| `verdict` | `да` \| `скорее да` \| `зависит` \| `скорее нет` \| `нет` |
| `verdict_reason` | Почему — опирается на остальной текст |
| `do` | Что делать |
| `avoid` | Чего не делать (не противоречит `do`) |
| `how` | Как именно действовать |
| `what_to_say` | Что сказать партнёру (готовая формулировка) |
| `focus_now` | На что обратить внимание сейчас |
| `next_step` | Ближайший практический шаг |
| `direct_answer` | Ответ на конкретный вопрос пользователя (если был) |

Генерировать **только по entitlement + явному запросу** (уже C1 `POST /dynamics/premium`).

---

## 2. Уровни точности (`source_depth`)

| Значение | Данные | Честность формулировок |
|----------|--------|------------------------|
| `zodiac_only` | Два знака | Общая динамика. Нельзя выдавать за поведение в реальном конфликте. |
| `birth_dates` | Даты → знаки + числа пути / базовая нумерология | Можно говорить о ритмах и жизненных числах; не выдумывать характер «как в профиле». |
| `profile_enriched` | Один полный профиль + второй знак/дата | Персонализация со стороны пользователя; партнёр — осторожнее. |
| `two_profiles` | Два профиля | Стили общения, конфликт, близость, цели — максимальная глубина. |

**UI (продукт, не техтермины):**  
«По знакам — общая динамика. После профиля разбор опирается на ваш стиль общения и реакции.»

Пример честной фразы при `zodiac_only`:  
*«По знакам между вами сильное притяжение, но этого недостаточно, чтобы судить о реальном поведении в конфликте.»*

---

## 3. Голос и запреты (RU)

### 3.1 Запрещённые клише (не исчерпывающий список — см. код `BANNED_PHRASES_RU`)

- «вам важно найти баланс»
- «ключ к гармонии»
- «позвольте себе»
- «это союз двух разных энергий»
- «при открытом общении всё возможно»
- терапевтические диагнозы, фатализм
- советы, подходящие любой паре
- повтор названий знаков в каждом абзаце
- пересказ входных данных
- метаязык: ИИ, модель, расчёт, промпт, алгоритм

### 3.2 Нужно

- конкретные бытовые ситуации;
- узнаваемое поведение («кто ускоряет», «кто замолкает»);
- короткие выводы;
- нормальный ритм русской речи;
- без эзотерического тумана.

---

## 4. Контракт ответа (логические поля)

```
compatibility_content_v1:
  contract_version: "compatibility_content_v1"
  tier: guest | registered | premium
  source_depth: zodiac_only | birth_dates | profile_enriched | two_profiles
  locale: ru          # эталон; en/pl later
  headline: string
  score: int
  summary: string
  attraction: string
  main_risk: string
  practical_advice: string
  confidence: low | medium | high
  # guest:
  locked_preview?: string[]
  # registered:
  emotions?: string
  communication?: string
  conflict?: string
  strengths?: string
  vulnerable_spot?: string
  what_helps?: string
  # premium:
  verdict?: ...
  verdict_reason?: ...
  do?: ...
  avoid?: ...
  how?: ...
  what_to_say?: ...
  focus_now?: ...
  next_step?: ...
  direct_answer?: ...
```

Валидация: длина, непустота, язык (кириллица для `ru`), banned phrases, `do`⊥`avoid`, verdict согласован с тоном текста.

---

## 5. Evaluation

Минимум **80 кейсов** в `backend/evals/compatibility_quality/scenarios_v1.json`:

| Группа | N |
|--------|---|
| Знаки | 20 |
| Даты | 20 |
| Один полный профиль | 20 |
| Два профиля | 20 |

Обязательные включения: одинаковые знаки; «сложные» пары; похожие / противоположные стили; missing data; вопрос пользователя; эталон **RU**.

Рубрика: конкретность · естественность · отсутствие повторов · полезность · соответствие `source_depth` · согласованность блоков · качество совета · готовность к показу · **TodayFlow Voice** / Memorability (см. [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md)).

---

## 6. Порядок выката

1. Канон (этот файл) — ✅  
2. Контракты + validators в коде  
3. Prompt v1 на слой  
4. Evaluation set  
5. Прогон модели (offline)  
6. Ручная оценка ≥30 ответов  
7. Правки дефектов  
8. ✅ Human review v1.1 → guest/registered under flag; publish_gate in enrichment worker  
9. Next: publish/fallback telemetry · regen rate · save · block opens · user confirm/reject (не ещё один synthetic pack)  

---

## 7. Definition of Done

- [x] Три слоя — разные задачи и отдельные контракты (`GuestContentV1` / `RegisteredContentV1` / `PremiumContentV1`)
- [x] Guest — законченный контракт + deterministic baseline (`guest_baseline_v1`); не обрезка registered  
- [x] Registered / Premium — отдельные prompt v1 + validators (LLM offline / flag)  
- [x] `source_depth` + honesty lines в коде  
- [x] Banned phrases + structural quality checks  
- [x] Evaluation set 80 кейсов + offline guest baseline runner  
- [x] Ручная оценка первого пакета (10) + prompt v1.1; guest/registered approved under flag  
- [x] Production enrichment на v1 + publish_gate (`compatibility_enrichment_v0` when flag on)  
- [ ] Premium wide enable only after ≥5 real-user questions  
- [ ] Telemetry: publish/fallback, regen, save, opens, confirm/reject  

---

## 8. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-07-21 | v1.0 — C2 content canon: layers, source_depth, voice, eval, rollout |
| 2026-07-21 | v1.1 — код `compatibility_content_v1`, eval 80, flag `COMPATIBILITY_CONTENT_V1` (default off) |
| 2026-07-21 | prompt **v1.1** patch: score 20–95 / no score on premium; publish gate rejects invalid; registered≠verdict; birth_dates honesty; zodiac hedges; no gender hacks |
| 2026-07-21 | guest+registered approved; publish_gate wired into enrichment worker; Voice Canon |
