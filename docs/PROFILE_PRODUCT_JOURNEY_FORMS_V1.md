# Profile Product Journey — Locked Forms v1

**Status:** CONDITIONAL PRODUCT SIGN-OFF — samples corrected 2026-07-22; mechanism deltas next  
**Date:** 2026-07-22  
**Parent SoT:** [PROFILE_PRODUCT_SURFACE_CANON.md](./PROFILE_PRODUCT_SURFACE_CANON.md)  
**Fixtures:** `pq-001` (birth-only, no time) · `pq-007` (living) — `backend/evals/profile_quality/scenarios_v1.json`  
**Rule:** метрика = человеческая реакция. Не `PASS` по JSON.  
**Запрет:** выдавать корреляционные признаки за причину результата, которого система не рассчитывала.

Production archetype seed (код): `core_profile._build_baseline` — **только** `life_path` → `Architect` / `Harmonizer` / `Explorer` / `Sage` / `Observer`.  
RU label + SVG: `frontend/src/lib/visualIdentity/registry.ts` · `ArchetypeSymbol`.  
Eval-сценарии с `initiator` / `stabilizer` **не** SoT имени — побеждает production calc.

---

## Шаг 1 — Меня поняли (LOCKED FORM)

### Чувство / метрика

| | |
|---|---|
| Чувство | «Ого. Это про меня.» |
| Метрика | «Да, это похоже на меня.» |
| Share test | Хочется отправить / сохранить. Текст без образа = fail. |

### Форма на экране (ровно это)

```text
┌─────────────────────────────────────┐
│                                     │
│         [ VISUAL OBJECT ]           │  ← обязательно, ≥ половины первого взгляда
│                                     │
│            АРХИТЕКТОР               │  ← recognition_name
│                                     │
│     Ты первым видишь структуру      │  ← recognition_line
│     там, где остальные пока         │
│     видят только хаос.              │
│                                     │
└─────────────────────────────────────┘
```

| Слот | Правило | Источник |
|------|---------|----------|
| **Visual object** | Один тип на archetype: `ArchetypeSymbol` (SVG из registry). Не pills. Не eyebrow «Профиль». | `baseline.archetype_seed` → slug → asset |
| **recognition_name** | 1 слово/название ядра, UPPER или display weight | calc RU label (`archetypeDisplayLabel`) |
| **recognition_line** | 1 мысль, ≤ 120 символов, 1–2 короткие строки. Узнаваемое поведение; отличает archetype от соседних; не совет «сегодня» | **обязательное поле** identity contract |
| Запрет на Шаге 1 | второй абзац «кто ты»; список сил; натал; «Личный профиль» как смысл | — |

### Target contract (механизм под форму)

Сегодня: длинный `identity_core` + FE `«{Archetype}. {identity_core}.»` — **недостаточно**.

| Field | Required | Notes |
|-------|----------|-------|
| `recognition_name` | yes | = calc label; можно не дублировать в LLM |
| `recognition_line` | **yes — отдельное поле** identity contract | не compress «на глаз» из длинного ядра в UI |
| `identity_core` | kitchen / later | не главный UI Шага 1; материал для узлов, если не перефраз |

**Не новый engine.** Патч identity step: модель отдаёт `recognition_line` отдельно от длинного ядра.

Accept Шага 1: человек читает только name + line + видит символ → метрика «похоже» без скролла дальше.

### Sample — Case A (`pq-001`)

Факты: 1991-04-12 · Овен · огонь · cardinal · life_path **1** → production **Architect** → **Архитектор**. Нет времени/места/living.

| Слот | Sample (product intent, не live LLM) |
|------|--------------------------------------|
| Visual | `ArchetypeSymbol` · architect |
| Name | Архитектор |
| Line | Ты первым видишь структуру там, где остальные пока видят только хаос. |

Share test: имя + линия + символ на карточке — OK после этой линии.

---

## Шаг 2 — Понятно, почему (LOCKED FORM)

### Чувство / метрика

| | |
|---|---|
| Чувство | «А, поэтому. Не случайный AI-текст.» |
| Метрика | Может указать: откуда имя · чем расширен портрет · чего ещё нет |

### Правило честности: `selected_by` ≠ `portrait_influenced_by`

| Класс | Смысл | Production truth |
|-------|--------|------------------|
| **selected_by** | Что **выбрало** `recognition_name` / `archetype_seed` | **только** `numerology.life_path` → baseline mapping |
| **portrait_influenced_by** | Что **расширяет** интерпретацию портрета | sun · element · modality/rhythm · moon/ASC/MC when known · living later |

**Запрещено** заголовком или порядком строк создавать впечатление, что Солнце / стихия / ритм участвовали в выборе имени архетипа.

Это правило **проекции** (и copy), не новая схема БД.

### Форма

Заголовок смысла: **Почему портрет звучит именно так** (не «Почему именно {Archetype}»).

```text
Почему портрет звучит именно так

✓ Архетип Архитектора — рассчитан из числа пути 1     ← selected_by
✓ Солнце в Овне                                         ← portrait_influenced_by
✓ Стихия огня
✓ Ритм — быстрый старт                                  ← факт baseline; без лишней интерпретации
○ Луна в …          — только если известна
○ ASC в …           — только если reliable birth time
○ MC в …            — только если reliable birth time
```

| Якорь | Path | Класс | Appear when | Omit when |
|-------|------|-------|-------------|-----------|
| Архетип ← число пути | `life_path` + `archetype_seed` | **selected_by** | всегда с LP | нет LP/seed |
| Солнце | `astro.sun_sign` | influenced | birth date | нет даты → нет портрета |
| Стихия | `astro.sun_element` | influenced | sun known | — |
| Ритм | `baseline.rhythm_style` | influenced | calc | показывать **точное** значение поля; не дописывать интерпретацию в UI |
| Луна | natal / identity moon | influenced | position known | нет карты/луны |
| ASC | natal rising | influenced | time known + not `time_unknown` | **нет времени** |
| MC | house 10 / mc | influenced | same as ASC | **нет времени** |
| Дома / аспекты | natal | influenced / deepen | углубление | dump всех 12 |

**Роль-проза** рядом с якорем — только из существующего evidence/card field. Иначе — чистый факт.  
LLM не пишет «вы Овен, поэтому Архитектор».

### Honesty без времени (Case A / B)

> Без времени рождения пока не видны ASC и дома — они покажут, как эти качества проявляются во внешнем поведении и отдельных сферах жизни.

CTA: добавить время → что откроется (ASC / дома), Voice §0.05.

### Sample — Case A (`pq-001`)

```text
Почему портрет звучит именно так

✓ Архетип Архитектора — рассчитан из числа пути 1
✓ Солнце в Овне
✓ Стихия огня
✓ Ритм — быстрый старт

Без времени рождения пока не видны ASC и дома —
они покажут, как эти качества проявляются во внешнем
поведении и отдельных сферах жизни.
```

Примечание по ритму: в коде `rhythm_style` для (fire, cardinal) = «Быстрый старт без перегрева».  
На Шаге 2 в sample показываем **укороченный факт** «быстрый старт», если полный string несёт интерпретацию сверх нужды чеклиста; либо полный string **дословно** из baseline — без UI-дописки. Не смешивать.

Новая ценность vs Шаг 1: видно **откуда имя** и **чем расширен портрет**, не ложная причинность label.

---

## Шаг 3 — Нахожу то, чего не замечал (LOCKED NODE FORM)

### Чувство / метрика

| | |
|---|---|
| Чувство | «Вот этого я ещё не видел.» |
| Метрика | ≥1 инсайт, которого не было в name+line Шага 1 |

### Форма узла (не три зоны)

Один **узел-история**. First release: **один** сильный static-узел (макс. два допустимы позже). С living — 1 сильный узел предпочтительнее трёх слабых списков.

```text
[ Заголовок узла — ловушка / сила / повтор ]
  одна фраза сути
        ↓
На что опирается вывод
  calc anchors (факты) — не категорическое «Почему»,
  пока нет per-node causal trace
        ↓
Что помогает
  одна конкретная опора (не day tip)
        ↓
Как это уже проявлялось     ← только living evidence; иначе слот отсутствует
  цитаты / сигналы наблюдений
```

| Материал | Snapshot / source | В узле |
|----------|-------------------|--------|
| Суть ловушки / силы | `growth_zones` / `strengths` / `recurring_patterns` | заголовок + суть |
| На что опирается | calc anchors (подмножество Шага 2, класс influenced + LP как факт) | **не** утверждать точную причинность без trace |
| Что помогает | `helps` если gate open; иначе одна строка из strengths/practical | не выдуманный living |
| Как проявлялось | living signals / summary | **omit** без living; отделять от calc |

**Запрет:** три секции Strengths · Limits · Patterns как равные документы.  
**Запрет:** интерпретации («опора на порядок») в слоте calc-якорей.  
Массивы JSON = склад материалов, не IA.

### Sample — Case A (`pq-001`, no living) — 1 узел

```text
Главное напряжение

  Ты легко открываешь новый контур,
  но устойчивость появляется только после осознанного закрепления.

На что опирается вывод
  Солнце в Овне · число пути 1 · ритм быстрого старта

Что помогает
  Один завершённый контур важнее трёх новых начал.
```

Слот «как проявлялось» — **нет** (living null). Не обещать паттерны.

### Sample — Case C (`pq-007`, living) — 1 узел

Факты: Телец · земля · life_path **4** → production **Sage** → **Мудрец**. Living: перегруз к вечеру, откладывание сложных разговоров.

```text
Самая большая ловушка

  Ты откладываешь сложный разговор,
  пока усталость не делает его ещё тяжелее.

На что опирается вывод
  Телец · стихия земли · число пути 4

Что помогает
  Назвать тему разговора одним предложением
  до того, как накопится вечерняя усталость.

Как это уже проявлялось
  «Не стала писать коллеге» · «Разговор с партнёром перенесла».
```

Новая ценность vs Шаги 1–2: конкретная ловушка + living след отдельно от calc; не пересказ «Мудрец».

Patterns/helps LLM: только если `patterns_generation_allowed`. Иначе узел из strengths/growth + calc; living slot только из реальных сигналов (детерминированно), без лейбла «подтверждённый паттерн» без gate.

---

## Шаг 4 — Понятно, что делать дальше (LOCKED FORM)

### Чувство / метрика

| | |
|---|---|
| Чувство | «Ясно, куда прикладывать усилия.» |
| Метрика | Одним предложением: куда усилие (не «кто я») |

### Форма

```text
Куда прикладывать усилия

  {effort_vector — одна фраза}

  [опционально 1–2 сферы только если новая ценность,
   не пересказ effort_vector]
```

| Field | Source | Rule |
|-------|--------|------|
| `effort_vector` | **node projection**: insight → help → compact action (не обязательный отдельный LLM-step) | ≤ 140 символов; начинается с действия; **не** повторяет `recognition_line`; не day agenda |
| spheres | `life_spheres` | только если добавляют *где*; иначе omit |

Валидатор: action-start · ≠ recognition_line · ≤140.

Без living: вектор из static-узла (напряжение→усилие), не `life_mission` из patterns step (gate closed).

### Sample — Case A

```text
Куда прикладывать усилия

  Доводить один начатый контур до видимого результата,
  прежде чем открывать следующий.
```

### Sample — Case C

```text
Куда прикладывать усилия

  Начинать короткий честный разговор
  до того, как накопятся усталость и напряжение.
```

---

## Шаг 5 — Хочу возвращаться (LOCKED BRIDGE)

### Чувство / метрика

| | |
|---|---|
| Чувство | «Хочу проверить это в жизни.» |
| Метрика | Один очевидный выход с ценностью |

### Форма (на Profile — тонкий мост, не day product)

```text
Проверить в жизни
  {bridge_line — что откроется}
  [ CTA → Today / наблюдения / карты ]
```

| Case | bridge_line | CTA |
|------|-------------|-----|
| A (no living) | Наблюдения за несколько дней откроют, что у вас реально повторяется — не как теория, а как ваш ритм. | → Today / наблюдения |
| C (has living) | Отметь следующий сложный разговор в Today — так станет видно, удалось ли изменить этот повтор. | → Today |

Запрет: прогноз «завтра»; day stone / «главный шаг сегодня» на Profile (PR-4).

---

## New-value check (обязателен)

| После шага | Должно появиться впервые |
|------------|---------------------------|
| 1 | Узнавание (имя + линия + образ) |
| 2 | Откуда имя (**selected_by**) + чем расширен портрет (**influenced_by**) + чего нет |
| 3 | Ловушка/сила + честные опоры + (если есть) living отдельно |
| 4 | Вектор усилия (глагол), не перефраз имени |
| 5 | Мост вовне Profile с действием и ценностью |

Если шаг = перефраз или ложная причинность — **удалить/слить/переписать**, не полировать.

---

## Mechanism deltas (NEXT — не UI, не новая архитектура)

| # | Delta | Why | Status |
|---|-------|-----|--------|
| 1 | `recognition_line` — отдельное поле identity contract | Шаг 1 | **SHIPPED** `7d6e7bc` (Snapshot field; UI not wired) |
| 2 | Проекция Шага 2: `selected_by` vs `portrait_influenced_by` | без ложной причинности label | **IN CODE** — `portrait_why_v0` read-path only (no Snapshot fields); `profile_portrait_why_projection_v0.py` |
| 3 | Node projection: insight → anchors → help → living evidence | Шаг 3; слот «На что опирается вывод» | waiting |
| 4 | `effort_vector` из node projection + validator | Шаг 4; без отдельного LLM-вызова | waiting |
| 5 | `bridge_line` (+ CTA Today) | Шаг 5; без day-forecast | waiting |

Пауза: `character_decisions` · новые Freeze-строки · UI journey surface.

---

## Sign-off checklist

| Проверка | Вердикт |
|----------|---------|
| Шаг 1 Case A: share test | **OK** после `recognition_line` |
| Шаг 1: отдельное поле contract | **требуется** в mechanism delta #1 |
| Шаг 2: понятно почему | **OK** после selected_by / influenced_by |
| Шаг 2: omit ASC честен | **OK** |
| Шаг 3 Case A: новый инсайт без living | **OK** |
| Шаг 3 Case C: одна история · calc ≠ living | **OK** |
| Шаг 4: вектор ≠ Hero | **OK** |
| Шаг 5: мост без day-content | **OK** (Case C без прогноза «завтра») |

**Product sign-off (forms + corrected samples):** **YES** — 2026-07-22  
**Next:** mechanism deltas #1–5 only.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | v1.0 — locked forms Steps 1–5; samples pq-001 / pq-007 |
| 2026-07-22 | v1.1 — product review fixes: recognition_line; selected_by vs influenced_by; node wording; Case C rewrite; effort/bridge; conditional → **sign-off YES** |
