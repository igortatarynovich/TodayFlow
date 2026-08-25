# Practice Technique Shortlist Criteria v1

**Статус:** `ACCEPTED` — SoT допуска семьи к shortlist. **Не** shortlist. **Не** ingest.  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product + Research.  
**Parent order:** [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) шаг 8.  
**Landscape:** [PRACTICE_TECHNIQUE_LANDSCAPE_V1.md](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_shortlist_criteria_v1.json`](../../DATA/reference/practice/technique_shortlist_criteria_v1.json).

**Это:** при каких условиях `candidate_family` вообще имеет право войти в shortlist.  
**Это не:** список книг · выбранные loci · canonical technique · аттестация Content Item · открытие `shortlist_status`.

`technique_canon_v1.json` остаётся **пустым**.  
`technique_landscape_v1.json`: `shortlist_opened = false`. Criteria **не** открывает shortlist. Opening = [PRACTICE_TECHNIQUE_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md) (vertical slice).

---

## Architecture impact

- **SoT before:** landscape описал семьи и типы источников. Следующий шаг мог начаться с «найти источник для `box_breathing`». Риск — подогнать критерии под уже удобный блог, workbook или брендовый протокол.
- **SoT after:** критерии зафиксированы **до** корпуса. Единица shortlist = `candidate_family`, не taxonomy type и не probe item. Type проверяется позже: допустимая ли *product expression* этой семьи. `technique_id` на item — только при `review_status = canonical`. Убедительный shortlist ничего в библиотеке не аттестует.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen. Probes remain without `technique_id`.
- **Canon updated?** yes — этот файл · criteria JSON · landscape next-pointer · provenance pipeline/§11 · coverage next_pass · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с открытием shortlist или ingest из этого pass.

---

## 0. Закон

1. **Критерии раньше корпуса.** Не открывать shortlist, чтобы «было к чему применить гейты». Гейты задаются от модели семьи ([landscape](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md) + provenance §3).
2. **Единица отбора — семья.** Вопрос shortlist: «какие loci описывают *equal-count breathing*?» не «какой ISBN подтвердит type `box_breathing`?». Type — гипотеза expression, проверяется после loci.
3. **Допуск ≠ выбор.** Семья может быть *eligible* и всё равно не получить selected locus. Eligibility — этот файл. Selection — следующий pass.
4. **Conflict не усредняется.** Два несовместимых описания kernel = `conflict`, не «обычно так». LLM не судья.
5. **Existence ≠ efficacy.** Источник, который меряет эффект и не описывает метод, не проходит C1.
6. **Canonical раньше `technique_id`.** Даже полный shortlist и `extracted` row не связывают probe. Только `canonical` (после safety review).
7. **Product-only только явно.** `claim_risk = product_only` / `likely_invention` не маскируются под established technique.

Parent: quality × independence × relevance к составляющей × legal accessibility — ниже разложены в гейты C1–C9. Не копировать астрологический CORE.

---

## 1. Порядок после этого файла

Criteria **не** открывает корпус. Shortlist V1 открыл **одну** семью:

```text
candidate_family
  → shortlist candidates          (типы источников + названные loci, ещё не ingest)
  → source / locus assessment     (C1–C9)
  → selected loci
  → ingest paraphrase             (не copy)
  → extracted technique
  → normalization
  → safety review
  → canonical | rejected
```

Только `canonical` даёт право: Content Item `identity.technique_id` → этот `technique_id`.  
До этого: library = `llm_provisional`. Fill frozen.

Запрещённый порядок: удобный PDF → критерии под него → семья под type probe.

---

## 2. Гейты

Каждый гейт: `id` · вопрос · pass · fail · hard/preference.

Hard fail выводит *locus* (или всю семью, если ни один locus не может пройти) из shortlist. Preference не исключает класс источника целиком, но ранжирует.

### C1 — метод, не только эффект · **hard**

Источник описывает, *что делать / на что направлять внимание* (mechanism + шаги или эквивалент). Статья «breathing reduced anxiety» без паттерна дыхания — fail.

### C2 — конкретный locus для paraphrase · **hard**

Есть названный, легально читаемый locus (издание, раздел, страница/якорь, официальная страница протокола). «Все так делают», память модели, анонимный explainer — fail. Нечитаемый том может стоять в карте поля; в shortlist candidates он `NEED_OWNER`, не selected, пока нет тела.

### C3 — kernel отделяется от упаковки · **hard**

Можно отличить устойчивое ядро от бренда, школы, приложения, «Navy SEAL», «5-4-3-2-1 как в Instagram», имени автора. Если отделить нельзя — locus описывает продукт/бренд, не семью.

### C4 — bounds / safety извлекаемы или явно unknown · **hard**

Либо из locus читаются safety-relevant bounds (задержки, усилие, кому остановиться), либо row помечает `bounds_unknown` / `safety_unknown`. Запрещено выдумывать bounds, чтобы «семья выглядела готовой».

### C5 — не требуется copy protected script/protocol · **hard**

Ingest = paraphrase ядра. Если единственный способ воспроизвести метод — скопировать workbook, guided script, CBT-I manual, MBSR handout — locus не selected. Семья может остаться eligible, если есть другой locus.

### C6 — existence не смешивается с efficacy · **hard**

Locus может упоминать исследования эффекта; это не заполняет `allowed_claims` и не повышает `evidence_level` существования. Fail, если shortlist-карточка пишет «работает, значит это наша техника».

### C7 — предпочтение класса источника · **preference**

При равном C1–C6 предпочтение зависит от `source_families[]` семьи (landscape), не от фамилии:

| `source_family` семьи | Предпочитать |
|----------------------|--------------|
| `clinical_psychology` / `behavioral_science` | academic description, official health, recognized clinical educational text |
| `mindfulness_protocol` | protocol description + academic mindfulness; не популярный app script |
| `tradition_primary` | первичный / авторитетный текст традиции, затем recognized school |
| `official_health` | официальное health/academic описание метода |
| `recognized_school` | учебник/manual школы как описание метода, не маркетинговая обложка |
| `historical_philosophical` | только если семья явно аскетический слой |

SEO, viral tactical, manifestation deck, LLM — вне предпочтения и обычно fail C1/C2/C3.

### C8 — конфликт фиксируется, не усредняется · **hard**

Два locus дают несовместимый kernel (есть пауза / нет паузы; values-writing / coping slogan; PMR sequence / один drop). Карточка: `conflict`, оба описания, без «среднего». Fail, если LLM склеивает в один канон до ingest.

### C9 — product-only только явно · **hard**

Семья с `claim_risk` `product_only` или `likely_invention` входит в shortlist **только** с пометкой `track = product_only` или `track = reject_or_remap`. Запрещено искать «настоящий источник», который задним числом сделает выдумку established. Manifestation-семья: **не eligible**.

---

## 3. Допуск семьи (eligibility), не selected loci

Семья **eligible** для будущего shortlist, если:

- она есть в landscape;
- для неё мыслим хотя бы один класс источника из её `source_families[]` (или явный C9 track);
- hard-гейты не делают поиск бессмысленным заранее (например manifestation).

Семья **не eligible** как established-hunt:

| `family_id` | Почему |
|-------------|--------|
| `family.affirmation.manifestation_outcome` | C9; исключена из product SoT |
| `family.discipline.clinical_insomnia_protocol` | distinction row; не product family; не shortlist ради маппинга `sleep_discipline` |
| `family.practice.unattested_short_exhale` | только `reject_or_remap` track, не hunt «настоящего короткого выдоха» |
| `family.practice.activating_forceful_breath` | eligible как *полевая* семья; **не** для аттестации `energizing_breath` |
| `family.affirmation.values_self_affirmation` | eligible как construct; **не** для аттестации `capability` probe |
| `family.practice.progressive_muscle_relaxation` | eligible; **не** для `body_release` |
| `family.discipline.historical_ascetic` | eligible только если продукт явно открывает слой аскез |

Четыре landscape-различия остаются в силе: equal-count shortlist не обязан подтвердить type `box_breathing`; сначала loci семьи, потом «является ли box допустимой expression».

---

## 4. Что shortlist будет спрашивать (ещё не строить)

Когда pass откроется, карточка кандидата — про **семью**:

1. Какие loci описывают эту семью (C1–C2)?
2. Какой kernel отделяется от упаковки (C3)?
3. Bounds known / unknown (C4)?
4. Можно ли paraphrase без copy (C5)?
5. Есть ли conflict (C8)?
6. Наш taxonomy type — допустимая expression этого kernel, другой type, remap или reject?

Пример: не «найти источник для `box_breathing`», а «loci для `family.practice.equal_count_breath`; затем: 4–4–4–4 с паузами — expression, вариант или другая семья?».

Не делать в Criteria V1: ISBN, author-lock, selected loci, ingest.

---

## 5. `technique_id` и библиотека

| Состояние | Library |
|-----------|---------|
| landscape / criteria / shortlist candidates / selected loci | probes без `technique_id`; не attestation |
| `extracted` / `normalized` / `safety_reviewed` | всё ещё нет `technique_id` на item |
| `canonical` | можно связать item; `active` только тогда |
| `rejected` | type/item заменить или снять; не оставлять как «проверенное» |

Убедительный shortlist ≠ covered cell.

---

## 6. Запрещено

- Менять `shortlist_status` на всех семьях сразу. Slice — один family_id.
- Писать `technique_canon_v1.json`.
- Ставить `technique_id` на Content Item.
- Подбирать критерии под уже найденный удобный источник.
- Усреднять конфликтующие описания.
- Маскировать product-only / likely_invention под established.
- Копировать protected protocol. Заявлять efficacy. Писать новые items.

---

## 7. Что дальше

1. Criteria V1 стоит. Full shortlist **закрыт**.
2. Vertical slice + ingest + normalize: [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md) · [PRACTICE_TECHNIQUE_INGEST_V1](./PRACTICE_TECHNIQUE_INGEST_V1.md) · [PRACTICE_TECHNIQUE_NORMALIZATION_V1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md).
3. Следующий named pass: **targeted shortlist** (post-exhale hold identity).
4. `technique_id` — на canonical.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-25 | pointer: Normalization V1 insufficient_evidence; this file still does not open the corpus |
| 2026-08-25 | pointer: Ingest V1 recorded evidence; this file still does not open the corpus |
| 2026-08-25 | pointer: Shortlist V1 vertical slice opened one family; this file still does not open the corpus |
| 2026-08-25 | v1.0 ACCEPTED — family eligibility gates C1–C9; shortlist remains closed; technique_id only at canonical |
