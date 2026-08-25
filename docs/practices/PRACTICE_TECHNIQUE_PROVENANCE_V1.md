# Practice Technique Provenance v1

**Статус:** `ACCEPTED` — SoT происхождения техник библиотеки.  
**Версия:** 1.1 (2026-08-25).  
**Владелец:** Product + Research.  
**Parent:** [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) (шаги 1–9 до ingest).  
**Аналог provenance (не копировать астрологию):** [INTERPRETATION_LIBRARY_V1.md](../astrology/INTERPRETATION_LIBRARY_V1.md) §6.8.  
**Taxonomy:** [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md).  
**Fill freeze:** [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md).  
**Machine:** [`technique_canon_contract_v1.json`](../../DATA/reference/practice/technique_canon_contract_v1.json) · [`technique_canon_v1.json`](../../DATA/reference/practice/technique_canon_v1.json) (empty).  
**Landscape (parent 5–7):** [PRACTICE_TECHNIQUE_LANDSCAPE_V1.md](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md) · [`technique_landscape_v1.json`](../../DATA/reference/practice/technique_landscape_v1.json).

**Это:** откуда берётся *техника*; как она становится канонической; чем Content Item отличается от канона.  
**Это не:** экран `/practices` · Meaning дня · медицинский протокол · разрешение копировать чужой текст · разрешение заявлять efficacy.

---

## Architecture impact

- **SoT before:** Content Item писался сразу против need cell / type. Источник техники = формулировка LLM под taxonomy. Coverage-first закрывал ячейки, но не проверял, существует ли техника вне модели.
- **SoT after:** техника живёт в **Canonical Technique**. Content Item — продуктовая реализация (`technique_id` + duration / delivery / locale / context). Pipeline: Source → extraction → normalization → safety review → canonical technique → item expression. LLM пишет финальный payload **после** канона, не invents mechanism/steps. Fill библиотеки **заморожен**, пока нет канонических техник. Первые 11 items — architecture probes, не content SoT.
- **Public contract changed?** no — Today / Profile JSON, `practice_recommendation`, screen need/format не меняются.
- **Migration required?** no runtime. `identity.technique_id` optional, пока registry пуст. Когда появятся canonical rows, новые production items обязаны ссылаться; текущие 133 draft остаются без `technique_id`.
- **Canon updated?** yes — этот файл · technique contract + empty registry · item contract · taxonomy pipeline · coverage freeze · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с продолжением LLM-seed как content SoT: audio vs text и дальнейшие items **запрещены**, пока не пройден provenance.

---

## 0. Закон

1. **LLM не источник техники.** Память модели, wellness-блоги, SEO-explainer'ы, «так делают все» — не evidence. LLM может извлечь paraphrase из *легально прочитанного* источника и позже сформулировать item. Не может задать mechanism, steps, safety или claim.
2. **Существование техники ≠ efficacy.** Традиция 2000 лет не даёт медицинского эффекта. Efficacy живёт в `allowed_claims[]` / `prohibited_claims[]` и `efficacy_claim_level`, не выводится из `tradition[]`.
3. **Своя формулировка, не копия.** Канон фиксирует устойчивое ядро (mechanism + bounds + variants). Item — наш текст. Copyrighted protocol / guided script не копируется.
4. **Не lock авторов до shortlist.** Parent: модель → ландшафт типов источников → карта поля → критерии → shortlist → ingest. Запрещено начинать с «откроем Kabat-Zinn / Linehan / Jacobson».
5. **Психология/медицина ≠ астрологический CORE.** Иерархия доказательности задаётся заранее. Межшкольная конвергенция IL не повышает клинический вес.
6. **Meaning не знает `technique_id`.** Как и `item_id`: астрология / CE / Today эмитят need, не технику.

---

## 1. Два объекта

```text
technique.extended_exhale          canonical kernel
  → practice.extended_exhale.001   2 min, text, Today now-job
  → practice.extended_exhale.002   5 min
  → practice.extended_exhale.003   guided audio
  → practice.extended_exhale.004   evening version
```

| Слой | Вопрос | SoT |
|------|--------|-----|
| **Canonical Technique** | Что это за метод? Откуда? Какое ядро? Что нельзя обещать? | этот файл + `technique_canon_v1.json` |
| **Content Item** | Какая двухминутная / вечерняя / audio версия для Today? | taxonomy §10 + `content_library_v1.json` |

Item без `technique_id` может существовать только как **provisional** (architecture probe / frozen density). `status: active` и publish — только с каноном `review_status = canonical`.

Retrieval по-прежнему выбирает **item**. Канон не участвует в matching, кроме того что item на него ссылается.

---

## 2. Pipeline

Две цепочки. Не смешивать.

**Происхождение техники**

```text
Source → Technique extraction → normalization → safety review
      → Canonical Technique → Content Item expression
```

**Продуктовая выдача** (без изменения)

```text
Meaning → Need → Retrieval constraints → Content Library → Content Item
```

Fill-pass coverage ([PRACTICE_CONTENT_COVERAGE_V1](./PRACTICE_CONTENT_COVERAGE_V1.md)) остаётся законом *каких ячеек продукт должен уметь закрыть*. Он больше **не** разрешает писать payload из головы, чтобы закрыть ячейку.

---

## 3. Модель техники (до литературы)

Составляющие фиксируются **до** карты авторов. Иначе первый учебник определит, каких слотов «как будто нет».

| Составляющая | Вопрос модели |
|--------------|----------------|
| **mechanism** | Что человек делает или на что направляет внимание? Не цель (`purpose`) и не delivery. |
| **kernel steps** | Какой минимум шагов делает это *этой* техникой, а не соседней? |
| **bounds** | Какие параметры safety-relevant (соотношение вдох/выдох, задержки, усилие, длительность)? |
| **variants** | Что можно менять, не создавая новую технику (счёт, поза, 2 vs 5 мин)? |
| **class fit** | Это разовое действие, направленное внимание, когнитивная формулировка или правило на период? |
| **safety** | Кому нельзя / когда остановиться. Продуктовые пределы, не диагноз. |
| **claim surface** | Что продукт имеет право сказать. По умолчанию — ничего медицинского. |

Это не слоты астрологического объекта. Не копировать `function / themes / polarity`.

---

## 4. Семьи источников по class

Тип источника — класс текста, не фамилия. Parent §3.

| `content_class` | Откуда брать основу | Не основа |
|-----------------|---------------------|-----------|
| **practice** | клиническая психология; mindfulness-протоколы как *описанные методы*; поведенческие подходы; официальные health / academic descriptions; признанные школы практик | LLM; TikTok/SEO grounding; «5-4-3-2-1 как все пишут» без locus |
| **meditation** | MBSR/MBCT и академическая mindfulness-литература (после ландшафта, не author-lock); для традиционных техник — первичные / авторитетные источники традиции | популярный «sleep meditation» скрипт; копия guided audio |
| **affirmation** | self-affirmation research; self-compassion; cognitive/behavioral literature | манифестация, «повторяй — и будут деньги», пустые confidence-лозунги без механизма |
| **discipline** | behavioral science, habit formation, self-regulation; исторические / философские традиции **только если** продукт явно держит слой аскез | wellness challenge, punitive detox как медицина |

`source_family` на каноне — один из:

`clinical_psychology` · `mindfulness_protocol` · `behavioral_science` · `official_health` · `academic_description` · `recognized_school` · `tradition_primary` · `historical_philosophical`

Несколько семей — в `source_refs[]` / `tradition[]`, не второй SoT.

---

## 5. Existence vs efficacy

Два независимых поля.

**`evidence_level`** — насколько техника *как метод* засвидетельствована (существование / описание), не «работает ли».

| `evidence_level` | Смысл |
|------------------|--------|
| `unverified` | нет ingest; LLM / architecture probe |
| `tradition_attested` | устойчиво описана в названной традиции (после shortlist + locus) |
| `protocol_attested` | входит в названный клинический / educational protocol (paraphrase, не копия) |
| `academic_described` | описана в academic / official health источнике как метод |
| `product_only` | наша сборка; техника как канон **не** принимается, пока не переведена в другой уровень или явно отвергнута |

**`efficacy_claim_level`** — право говорить об эффекте. Default: `not_claimed`.

| `efficacy_claim_level` | Смысл |
|------------------------|--------|
| `not_claimed` | продукт не утверждает исход (default) |
| `anecdote` | не для user-facing claims |
| `single_study` | не автоматически в payload |
| `review` | обзор; всё равно `allowed_claims[]` явно |
| `guideline` | официальное руководство; всё равно не копировать medical advice |

`allowed_claims[]` пуст, пока нет review. `prohibited_claims[]` для каждой канонической техники как минимум:

- лечение / диагностика расстройства
- гарантия сна, спокойствия, денег, отношений
- «вылечит тревогу / бессонницу»
- манифестация результата повторением фразы

Традиция в `tradition[]` не заполняет `allowed_claims`.

---

## 6. Поля Canonical Technique

Machine: `technique_canon_contract_v1.json`.

| Поле | Роль |
|------|------|
| `technique_id` | стабильный id, `technique.{slug}`; Meaning не эмитит |
| `content_class` | `practice` \| `meditation` \| `affirmation` \| `discipline` |
| `type` | код taxonomy, который этот канон реализует (не purpose) |
| `source_family` | §4 |
| `source_refs[]` | locus после ingest: source / edition / locus / paraphrase — не copyrighted prose |
| `tradition[]` | интеллектуальные линии, не «бренд приложения» |
| `evidence_level` | существование метода (§5) |
| `efficacy_claim_level` | право на эффект (§5) |
| `canonical_mechanism` | одно предложение: что делает метод |
| `canonical_steps[]` | устойчивое ядро; bounds; не UI copy |
| `safety_notes[]` | продуктовые пределы |
| `allowed_claims[]` | пусто, пока не reviewed |
| `prohibited_claims[]` | минимум §5 |
| `review_status` | `empty` \| `landscape` \| `extracted` \| `normalized` \| `safety_reviewed` \| `canonical` \| `rejected` |
| `semantic_version` | `practice-technique-v1.x` |

`review_status = canonical` только после safety review. До этого item не `active`.

IL analog: `concept_id` · source · locus · paraphrase · `evidence_tier` · `review_status`. Здесь нет астрологического `school` CORE. `evidence_level` ≠ IL `core`.

---

## 7. Роль LLM

| Можно | Нельзя |
|-------|--------|
| Извлечь paraphrase из легально прочитанного locus (ingest) | Быть полем-источником mechanism / steps |
| После `canonical`: написать item title/body в голосе продукта | Закрыть need cell выдуманной техникой |
| Нормализовать формулировку канона (fill-empty / reject-invalid) | Unconditional overwrite канона «более красивым» текстом |
| Пометить конфликт источников | Объявить efficacy из «обычно так пишут» |

Это тот же принцип, что IL: provenance раньше author-lock; ingest = paraphrase, не copy.

---

## 8. Freeze fill

Coverage-first **архитектуру** (26 cells, type spine, item shape) не откатываем.

Останавливается:

- новые seed items
- P1 density audio vs text
- P1 types на текущих cells
- массовая EN/context плотность как *content SoT*

Уже лежащие 133 draft items = **llm_provisional**. Они проверяют контракт, не происхождение.

**Architecture probes (первые 11, порядок ledger):**

1. `practice.sensory_grounding.001`
2. `practice.extended_exhale.001`
3. `practice.box_breathing.001`
4. `practice.energizing_breath.001`
5. `practice.prompted_reflection.001`
6. `affirmation.capability.001`
7. `practice.body_release.001`
8. `meditation.relaxation.001`
9. `meditation.sleep.001`
10. `discipline.sleep_discipline.001`
11. `practice.micro_action.001`

Items #12–#133 (остальные P0 cells, type-spine, duration/EN/context siblings) — тот же LLM-origin. Этот pass их **не** аттестует и **не** удаляет.

Следующий рабочий шаг — не audio. Landscape семей техник: [PRACTICE_TECHNIQUE_LANDSCAPE_V1](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md). Shortlist и ingest **закрыты**. `technique_canon_v1.json` пуст.

---

## 9. Проверка первых 11 — gap, не ingest

Это **не** shortlist и **не** канон. Ни один автор ниже не обязателен. Цель — честно сказать, что сейчас unverified, и какой *тип* ландшафта нужен.

Ниже «узнаваемое семейство» = в литературе существуют *похожие* методы. Это не attestation нашего текста и не efficacy.

| # | Item | Что в payload сейчас | Кандидат семейства (не lock) | Вердикт |
|---|------|----------------------|------------------------------|---------|
| 1 | `practice.sensory_grounding.001` | 3 вижу / 2 слышу / 1 касаюсь | sensory / 5-4-3-2-1 grounding в клинической psychoeducation / distress-tolerance; наш счёт — укороченный вариант | **unverified**. Нельзя принять 3-2-1 как ядро, пока ландшафт не отделит устойчивый метод от интернет-формулы. Нужны: clinical/educational descriptions grounding, варианты счёта, safety (диссоциация, травма — продукт не лечит). |
| 2 | `practice.extended_exhale.001` | выдох длиннее вдоха, 4 цикла | slow / extended-exhale breathing в дыхательной физиологии и clinical breath protocols | **unverified как наш протокол**. Ядро «выдох > вдох в безопасных границах» — сильный *кандидат* mechanism. 4 цикла / 2 мин — item, не канон. Нужны bounds (задержки, гипервентиляция), не HRV-маркетинг. |
| 3 | `practice.box_breathing.001` | 4–4–4–4 | equal-count square breathing; пересекается с pranayama equal ratio и с popular tactical packaging | **unverified**. Не брать viral «SEAL box breathing» как source. Ландшафт: academic/clinical equal-ratio vs yoga primary vs popularizer. Safety: задержки дыхания. |
| 4 | `practice.energizing_breath.001` | выдох короче вдоха, через рот | не совпадает с известными forceful pranayama (kapalabhati / bhastrika) и не с typical clinical downregulating breath | **weak / possibly invalid**. Высокий риск LLM-invention. Не плодить siblings. Сначала ландшафт *energizing breath* как класса; если ядра нет — `rejected`, type не закрывать выдумкой. |
| 5 | `practice.prompted_reflection.001` | одно предложение «что неясно» | generic journaling / prompted writing; не named clinical protocol | **generic instruction**. Возможно, канон = «один внешний prompt + запрет редактировать», а не бренд-техника. Либо привязать к journaling methods после ландшафта, либо пометить `product_only` и не делать efficacy. |
| 6 | `affirmation.capability.001` | «Я справлюсь с тем, что прямо сейчас» | **не** Steele-style values self-affirmation; ближе к coping statement | **mismatch risk**. Self-affirmation literature ≠ motivational slogan. Запрещено обещать уверенность/деньги от повторения. Ландшафт должен развести: values affirmation / self-compassion / CBT coping phrase. Этот payload пока не канон. |
| 7 | `practice.body_release.001` | плечи вверх–сброс | фрагмент PMR-adjacent / informal somatic; не протокол Jacobson | **unverified fragment**. Канон progressive muscle ≠ один жест плеч. Либо technique «shoulder drop» после источников, либо item — expression более широкого `body_release` / PMR kernel. |
| 8 | `meditation.relaxation.001` | тяжесть в руках на выдохе | generic relaxation imagery; пересекается с autogenic-adjacent, не Schultz protocol | **unverified**. Не называть autogenic training. Ландшафт MBSR/relaxation vs autogenic vs yoga nidra — какие ядра нам нужны для `meditation.relaxation`. |
| 9 | `meditation.sleep.001` | челюсть мягче, лёжа | generic wind-down, не CBT-I и не yoga nidra | **unverified**. `efficacy` sleep **запрещён** (taxonomy: не лечить бессонницу). Канон, если будет, = evening downregulate attention, не «лечение сна». |
| 10 | `discipline.sleep_discipline.001` | семь дней тот же час | sleep schedule / hygiene / stimulus-control *adjacent* (CBT-I family) | **unverified as medical**. Дисциплина «фиксированное время» — кандидат behavioral. Не заявлять лечение инсомнии. 7 дней — item window, не длина протокола CBT-I. |
| 11 | `practice.micro_action.001` | действие < 2 мин, сделать, остановиться | behavioral activation / implementation intentions / tiny-task families | **unverified**. Не lock Fogg/BA manuals до shortlist. Ядро-кандидат: один конкретный акт короче порога + стоп. Efficacy «запустит мотивацию» — not_claimed. |

**Общий итог probes:** ни один из 11 не имеет `source_refs`, `review_status = canonical` или права на efficacy. Architecture (item groups, seed_cell, coverage ledger) полезна. Содержание — неизвестного происхождения.

Не делать на этом шаге: канонические JSON-тела, список обязательных книг, копирование 5-4-3-2-1 / MBSR / CBT-I скриптов.

---

## 10. Запрещено

- Писать новые Content Items, пока fill frozen.
- Ставить `identity.technique_id` на item, которого нет в registry, или на `review_status` ниже `canonical` для publish.
- Считать coverage `seed` = «техника проверена».
- Копировать астрологический CORE / school-intersection в evidence техник.
- Lock авторов (Kabat-Zinn, Linehan, Jacobson, Steele, Fogg, …) до шагов 8–9 parent.
- Переносить традицию в `allowed_claims`.
- Медицинские, диагностические, манифестационные формулировки.
- Параллельный «practice research v2» без указателя на этот файл и на parent.
- Считать C1 registries или `CONTENT/practices/*.json` provenance.

---

## 11. Что дальше

1. **Сейчас:** [PRACTICE_TECHNIQUE_LANDSCAPE_V1](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md) (parent шаги 5–7). Shortlist не открыт.
2. Затем критерии отбора (шаг 8) от модели семей, не от первой главы.
3. Затем shortlist (шаг 9) по семьям — приоритет четыре различия landscape §4.
4. Только потом ingest: paraphrase loci → draft technique rows (`extracted`, не `canonical`).
5. Safety review → `canonical` → привязать probe item или заменить.
6. Только потом — новые expressions (5 min / audio) от канона, не от LLM-seed.

Registry сейчас **пуст**. Это правильно.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-25 | v1.1 — next named pass = landscape ([PRACTICE_TECHNIQUE_LANDSCAPE_V1](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md)); shortlist still closed |
| 2026-08-25 | v1.0 ACCEPTED — Canonical Technique слой; existence ≠ efficacy; LLM = formulation; fill frozen; 11 probes gap-reviewed, not ingested |
