# Display Construction Grammar v1

**Status:** ACTIVE — **закон конструкции** Profile и Today  
**Date:** 2026-08-29  
**Роль:** одинаковые правила для любых поверхностей. Не каталог слотов — каталоги: [PROFILE_DISPLAY_INVENTORY_V1](../profile/PROFILE_DISPLAY_INVENTORY_V1.md) · [TODAY_DISPLAY_INVENTORY_V1](../today/TODAY_DISPLAY_INVENTORY_V1.md).

**Не заменяет:** Character Engine · TODAY_CONTENT_PIPELINE · Product Flow · ScreenFlow mechanics · visual SoT.

---

## Architecture impact

- **SoT before:** Display Inventories named slots and budgets, but the chain, five constraint types, generated-input lock, and anti-dupe-by-question lived as prose. FE powers were implied.
- **SoT after:** this file is the construction law. Inventory is the **last authority before UI** for *which* slots exist. This file is the law for *how* a slot is specified and what FE may do. Same grammar on Profile and Today; different slot sets.
- **Public contract changed?** no JSON.
- **Migration required?** no. UI cutover waits until both inventories fill this record for every visible atom.
- **Canon updated?** yes — this file · foundation `_INDEX` · README · both inventories §0 · tracker.
- **Backward compatible?** yes for API. FE that chooses meaning, fills empty, or adds a block not in Inventory is out of frame.

---

## 1. Цепочка (LOCKED)

```text
расчёт
    → semantic authority          (кто решает смысл)
    → composition                 (какие атомы входят в кадр)
    → named slot                  (один id, один вопрос)
    → Display Inventory           (последний authority перед UI)
    → projection                  (view-model без новой семантики)
    → UI                          (показать / omit / clip)
```

**Запрещено:**

```text
JSON → frontend → «что-нибудь красиво покажем»
```

Frontend **не** решает: что важно · какой смысл вывести · какую мысль добавить · чем заполнить пустое · стоит ли показать дополнительный блок.

Frontend получает **разрешённые слоты** из Inventory и отображает их. Clip — защита длины. Hide — только по `empty_behavior` / capability / time gate, уже записанным в слоте.

Projector / ScreenFlow / FE **не** semantic authority. Pipeline Ownership остаётся для смысла дня; Character Engine — для личности. Inventory не invent смысла — раскладывает уже решённое.

---

## 2. Пять ограничений + omit

Слот **не существует**, пока заполнены все пять. Пустой шестой пункт (`empty_behavior`) обязателен.

| # | Ограничение | Вопрос |
|---|-------------|--------|
| 1 | **Existence** | Есть ли `slot_id` в Inventory этой поверхности? Нет → продукта нет. |
| 2 | **Authority** | Кто имеет право определить смысл? (не кто формулирует) |
| 3 | **Inputs** | Какие данные разрешено использовать? Всё остальное = forbidden inference. |
| 4 | **Semantic role** | На какой **ровно один** вопрос отвечает слот? |
| 5 | **Presentation budget** | Предложения / слова / символы / число элементов. |

**Empty → omit.** Нет заполнения пустоты шаблоном, calm-строкой, соседним слотом или «для любого».

Транспорт / throw → chrome `TF.no_connection` («Нет соединения.»).  
Сервер flagged unavailable → chrome `TF.unavailable` («Не удалось загрузить.»).  
Не invent product content.

---

## 3. Запись слота (обязательные поля)

Каждый видимый атом — одна запись. Трасса от слова на экране:

```text
visible text
  → slot_id
  → text_class
  → display_source          (поле / copy key / projection)
  → semantic_source         (кто решил смысл)
  → allowed_inputs
  → authority
  → persist_key / version
  → rendering_rule          (clip · omit · map label)
```

И отдельно:

```text
slot_id
  → one_question
  → budget
  → empty_behavior
  → interaction
  → forbidden
```

### 3.1 Поля записи

| Поле | Обязательно | Смысл |
|------|-------------|--------|
| `slot_id` | да | стабильный id (`T1-hero.human_line`, `P1.recognition_line`) |
| `surface` | да | `profile` · `today` · `ritual` · `my_day` · `evening` · `chrome-shared` |
| `role` | да | зачем элемент существует (не вопрос пользователя) |
| `one_question` | да для meaning | ровно один вопрос, на который отвечает слот |
| `text_class` | да | см. §4 |
| `authority` | да | semantic authority |
| `semantic_source` | да | где живёт решение (Engine nest, Snapshot field, copy file) |
| `display_source` | да | что читает UI (projection path / copy key) |
| `allowed_inputs` | да для generated / projected | разрешённые семантические входы |
| `forbidden_inference` | да для generated / projected | что нельзя вывести, даже «осторожно» |
| `output` | да | форма выхода (1 предложение, chip, visual) |
| `budget` | да | sentences / words / chars / count |
| `required` | да | да / нет / conditional |
| `empty_behavior` | да | почти всегда `omit` |
| `may_fe_transform` | да | `none` \| `clip` \| `map_label` \| `hide_by_gate` |
| `may_llm_add_meaning` | да | **нет**, кроме формулировки уже решённого входа |
| `interaction` | да | none / tap→sheet того же слота / navigate / disclose |
| `forbidden` | да | чужие слои, дубли ролей, kitchen |
| `why_here` | да | место в пути (Recognition дня, Шаг 3 Profile, …) |
| `persist_key` | да для meaning | ключ повторяемости |
| `anti_dupe_group` | да для meaning | id группы, внутри которой один proposition ≠ два слота |

Chrome-лейблы могут делить одну запись-семейство (`P.chrome.step_title`) со списком `members[]`, если все поля кроме copy key совпадают.

---

## 4. Классы текста

| `text_class` | Кто пишет смысл | Кто формулирует | FE |
|--------------|-----------------|-----------------|-----|
| `chrome` | продукт (Inventory / copy lock) | copy file | только этот ключ |
| `calc` | Engine / mapping | детерминированный факт или closed-set label | показать / omit / map_label |
| `generated` | **не LLM** — authority слота | LLM формулирует **уже решённое** | clip only |
| `projected` | тот же, что у исходного слота | детерминированная проекция (effort из help, bridge pack) | clip; no LLM |
| `catalog` | справочник символа | catalog copy | as-is |
| `user` | человек | человек | persist; не переписывать meaning дня/профиля |

**LLM не шестой источник смысла.**  
`generated` = формулировка. Если вывода нет в `allowed_inputs`, его нет в слоте — даже если фраза «хорошо звучит».

Пример:

```text
primary_energy = grounded          ← Engine
T1-hero.human_line                 ← LLM может сказать, каково grounded-день
НЕ может сам решить
  «сегодня лучше избегать важных разговоров»
  если этого нет во входах ЭТОГО слота
  (а у human_line входов на do/avoid нет — это T1-risk / T3-caution)
```

---

## 5. Одна грамматика, разные поверхности

Одинаковые правила. Не одинаковые блоки.

```text
Profile:   Recognition → Why → Insight → Effort → Bridge → Explore
Today:     TODAY → RITUAL → MY DAY → EVENING
```

Внутри каждой поверхности — **закрытый** набор `slot_id`.  
Пользователь учится, как TodayFlow разговаривает: сначала узнавание / какой день, потом почему, потом новое, потом жест, потом мост / вечер.

New-value: следующий meaning-слот не перефразирует предыдущий proposition. Это **anti_dupe_group**, не «похожая длина».

---

## 6. Semantic role ≠ длина

Недостаточно: «headline — 1 предложение, focus — 1–2».

Нужна **разная функция**. Тогда тест ловит две перефразировки одного тезиса.

| Поверхность | Слот | `one_question` (замок) |
|-------------|------|------------------------|
| Profile | `P1.recognition_line` | Кто я как наблюдаемый механизм? |
| Profile | `P3.insight` | Какую закономерность / ловушку я раньше не называл? |
| Profile | `P4.effort_vector` | Куда прикладывать усилие в поведении? |
| Profile | `P5.bridge_line` | Почему сейчас открыть Today? |
| Today | `T1-hero.human_line` | Каков уже выбранный общий день на человеческом языке? |
| Today | `T3.headline` | Что главное *лично для меня* сегодня? |
| Today | `T3.focus_body` | Где это проявится и на что направить внимание? |
| Today | `T3.priority` | Что конкретно сделать? |
| Today | `T3.caution` | Где персональный риск, не копия Global chips? |
| Today | `T2.catalog` | Что символ значит в каталоге? |
| Today | `T2.lens` | Как символ окрашивает *уже посчитанный* Personal Day? |

Один semantic source **не** может незаконно обслуживать две роли. Пример дефекта: `why_personal` → и `T3.headline`, и `T3.focus_body`.

`P1.identity_core` — **раскрытие той же оси**, что `recognition_line` (не новая роль). Anti-dupe: не равен `P3.insight` / `P4` / `P5`.

---

## 7. Rendering (единственные права FE)

| Правило | Да | Нет |
|---------|----|-----|
| `clip` | обрезать по budget на границе предложения/слова | дописать смысл |
| `map_label` | closed-set → RU chrome (`grounded` → «Заземление») | свободный синоним |
| `hide_by_gate` | capability, time gate, `required=no` + empty | спрятать, потому что «некрасиво» |
| `omit` | нет payload | заполнить соседним полем |
| sheet / disclose | тот же `slot_id` / тот же вопрос | новый смысл в overlay |

---

## 8. Persist / воспроизводимость

| Слой | Ключ |
|------|------|
| Chrome | ключ copy + версия Inventory |
| Profile meaning | `(user_id, profile_hash)` Snapshot + prompt/projection version |
| Global Day | `GlobalDayKey = local_date + locale + semantic_version` |
| Personal Day | `PersonalDayKey = user_identity + local_date + semantic_version` |
| Ritual identity | `(owner, local_date)` — не пересчитывает день |
| Gratitude | user record + `manifest`; **не** мутирует день |

Одинаковые ключи + версия правил → одинаковый **набор слотов**. Generated текст стабилен после persist (GET = 0 LLM на слое).

---

## 9. Audit (целевой harness — не этот PR)

Когда оба Inventory заполнены записями §3, проверяемо:

| # | Находка |
|---|---------|
| 1 | FE label / copy key не в Inventory |
| 2 | JSON field рисуется без `slot_id` |
| 3 | generated длиннее budget |
| 4 | personal / natal / CE source на Global `today` |
| 5 | ritual symbol во входах Global Day |
| 6 | один semantic source в двух `anti_dupe_group` ролях |
| 7 | fallback, придумавший смысл |
| 8 | неизвестный `text_class` |
| 9 | >3 ranked drivers на T1 |
| 10 | >4 support chips / >3 risk chips |
| 11 | Evening в скролле до time gate |
| 12 | guest с MY DAY meaning slots |
| 13 | `may_fe_transform` шире clip/map/hide_by_gate |
| 14 | generated слот без `allowed_inputs` + `forbidden_inference` |

---

## 10. Новый слот

1. Запись §3 в нужном Inventory.  
2. Architecture impact.  
3. Anti-dupe: новый `one_question` или явно «disclosure той же оси».  
4. Код projection **после** записи, не наоборот.

Нет записи → нет UI.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-29 | v1.0 — цепочка; пять ограничений; generated ≠ authority; anti-dupe by question; FE powers |
