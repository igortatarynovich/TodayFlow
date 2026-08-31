# Practice Technique Shortlist v1

> **Research archive / non-blocking (2026-08-26).** Historical evidence only. Not in NOW. Does not unlock fill. Active process: [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md). Index: [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

**Статус:** `ACCEPTED` — первый вертикальный shortlist-slice. **Не** technique canon. Ingest этой семьи: [PRACTICE_TECHNIQUE_INGEST_V1](./PRACTICE_TECHNIQUE_INGEST_V1.md).  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product + Research.  
**Parent order:** [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) шаг 9.  
**Landscape:** [PRACTICE_TECHNIQUE_LANDSCAPE_V1.md](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md).  
**Criteria:** [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md) (C1–C9).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_shortlist_v1.json`](../../DATA/reference/practice/technique_shortlist_v1.json) · contract [`technique_shortlist_contract_v1.json`](../../DATA/reference/practice/technique_shortlist_contract_v1.json).

**Это:** оценка реальных внешних loci для **одной** landscape-семьи.  
**Это не:** Canonical Technique · `technique_id` · аттестация Content Item · открытие всех семей · efficacy.

`technique_canon_v1.json` остаётся **пустым**.  
Остальные landscape-семьи: `shortlist_status = not_opened`.  
Открыта только `family.practice.equal_count_breath` (`sliced`).

---

## Architecture impact

- **SoT before:** Criteria V1 зафиксировал C1–C9, но корпуса не было. Следующий шаг мог открыть все семьи сразу или подогнать ISBN под type `box_breathing`.
- **SoT after:** shortlist открыт как **vertical slice** на одной семье. Выход = `candidate_sources[]` с C1–C9, `selection_decision`, `selected_loci[]`. `selected` = **разрешён для следующего ingest-pass**, не «источник доказал технику», не efficacy, не canon. Несколько selected loci могут нести разные исследовательские функции; конфликты записываются, не усредняются. Type `box_breathing` остаётся expression hypothesis. Граница **Landscape family → selected evidence loci, ещё не Canonical Technique** выдержана.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen. Probes without `technique_id`.
- **Canon updated?** yes — этот файл · shortlist JSON · landscape slice-fields · provenance §11 · coverage next_pass · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с записью `technique_canon_v1.json` или `technique_id` из этого pass.

---

## 0. Закон этого pass

1. **Одна семья.** Аналог seed-item для контракта. Не открывать 40 семей, чтобы «было к чему применить гейты».
2. **Семья, не type.** Вопрос: какие loci описывают *equal-count breathing*? Не: какой ISBN подтвердит `box_breathing`.
3. **`selected` ≠ канон.** Только допуск к ingest paraphrase. Canonical Technique — отдельный pass после extract / normalize / safety review.
4. **Не один идеальный источник.** Один locus может фиксировать kernel, другой — bounds/safety, третий — конфликтный вариант или традиционное существование (если C2 проходит). Запрещено молча склеивать несовместимые утверждения.
5. **Не копировать.** Ingest ещё не начат; даже в ledger нет copyrighted protocol text.
6. **Landscape kernel не переписывается молча.** Если locus спорит с `mechanism_shape`, это `conflict`, не hidden landscape bump.

---

## 1. Почему первая семья — `equal_count_breath`

Probe `practice.box_breathing.001` несёт 4–4–4–4 с двумя задержками. Landscape уже отделил **семейство метода** от популярной упаковки box / tactical breathing. Slice проверяет, что research-модель это различие выдерживает на реальных источниках.

Landscape `source_families[]` этой семьи дополнен `official_health` после slice: patient-education страницы реально описывают метод. Это уточнение карты поля, не канон техники.

---

## 2. Карточка семьи (сводка)

Полные гейты, bibliographic identity и extractable — JSON. Здесь — решения.

| `source_id` | class | decision | research function |
|-------------|-------|----------|-------------------|
| `src.bhf.heart_matters.box` | `official_health` | **selected** | four-phase kernel |
| `src.nhs.sfh.box_leaflet` | `clinical_psychology` | **selected** | four-phase kernel + stop-rules |
| `src.nhs.newcastle.square` | `clinical_psychology` | **selected** | three-phase **conflict** locus |
| `src.clevelandclinic.box` | `official_health` | supporting | 4-phase exists; C3 packaging (SEAL + sama vritti) |
| `src.iyengar.light_on_pranayama.ch18` | `recognized_school` | supporting | tradition/school **NEED_OWNER** |
| `src.ijcmph.dalvi.2023.samavritti` | `academic_description` | supporting | 4s×4 methods only; efficacy out of scope |
| `src.harvard.tactical_breather` | (packaging) | **rejected** | C3/C7 tactical identity |
| `src.healthline.box` | SEO | **rejected** | C6/C7 |
| `src.ayurwiki.vritti` | wiki | **rejected** | C2/C5 derivative |

`selected_loci[]` = BHF · NHS SFH · Newcastle.

Cleveland не selected: шаги отделимы, но locus **отождествляет** метод с Navy SEAL и sama vritti. Тот же four-phase kernel уже выбран на BHF/SFH без этой склейки.

Iyengar 1981, гл. 18 *Vrtti Pranayama*, ISBN `0-8264-0048-5` — названный school locus. Тело не ingest: нет лицензионной копии в этом pass. Archive.org dump и wiki-цитаты **не** legal locus (C2/C5).

---

## 3. C1–C9 на этом slice

| Gate | Что slice показал |
|------|-------------------|
| C1 | Patient-ed и NHS leaflets описывают *шаги*, не только «дыхание снижает стресс». |
| C2 | Public URL / NHS PDF — читаемые loci. Iyengar — named, не readable → NEED_OWNER, не selected. |
| C3 | «Box» как четыре шага отделяется (BHF, SFH). «Tactical breather» / SEAL+sama vritti — не отделяется; rejected или supporting. |
| C4 | SFH даёт dizziness / sit-lie / «если дыхание-фокус неудобен». BHF box-секция и Newcastle — `bounds_unknown` для who-must-not-hold; не выдумано. |
| C5 | Короткие public how-to; не workbook. Книга Iyengar не копируется. |
| C6 | Benefit-заголовки (BHF, Cleveland, IJCMPH BP) не входят в extractable kernel и не заполняют `allowed_claims`. |
| C7 | Предпочтение clinical_psychology / official_health / named school. SEO и tactical — вне. |
| C8 | Три несовместимых описания **не** склеены в один kernel (см. §4). |
| C9 | Семья не product_only. Slice не маскирует выдумку под established. |

---

## 4. Конфликты (не усреднять)

1. **Число фаз.** 4 фазы с двумя задержками (BHF, SFH) vs 3 фазы inhale–hold–exhale (Newcastle «square»). Ярлык square/box не есть kernel.
2. **Паузы как ядро vs позже.** Landscape `mechanism_shape` считает паузы идентичностью семьи. Iyengar unread; вторичные отчёты, что новичок равен только вдох/выдох, **не** ingest из wiki. Landscape kernel **не** переписан.
3. **Счёт «4».** Частый health-ed default, не доказанное ядро семьи. Probe использует 4 — это гипотеза expression.
4. **Склейка имён.** Box ≠ tactical ≠ sama vritti, пока ingest + legal school locus этого не разведут отдельно.

---

## 5. Expression hypothesis (не attestation)

Probe `practice.box_breathing.001` / type `box_breathing` **совпадает по форме** с four-phase patient-ed (BHF, SFH).

Он **не** совпадает с Newcastle 3-phase square.  
Он **не** attested как beginner samavrtti.  
Он **не** получил `technique_id`.  
Shortlist **не** покрывает ячейку `need.focus.focus`.

---

## 6. Граница, которую slice обязан держать

```text
Landscape candidate family
  → selected evidence loci
  ≠ Canonical Technique
```

Сейчас: семья `equal_count_breath` имеет selected loci.  
Ещё нет: extracted row, canonical kernel, `technique_id`, publish.

Если эта граница держится, остальные семьи открываются **тем же** процессом, по одной (или малой пачке), не все сразу.

---

## 7. Запрещено

- Писать строки в `technique_canon_v1.json`.
- Ставить `technique_id` на Content Item.
- Открывать остальные семьи «заодно».
- Усреднить 3-phase и 4-phase в один kernel.
- Считать Iyengar / Navy SEAL / Healthline источником семьи.
- Копировать protocol/book. Заявлять efficacy. Писать новые items.
- Начать ingest, подменив его «уже каноном».

---

## 8. Что дальше

1. Slice стоит. Ingest V1 записал три evidence records. Normalization V1 = `insufficient_evidence`. V1.1 = `normalize_one` candidate. Safety Review = `insufficient_safety`. Targeted Safety Shortlist = stop A. Targeted Safety Ingest = two observations. Canon пуст. Type не attested.
2. Исторический next этого pass: Safety Review V1.1 (**не открывать**). Не следующая семья.
3. `technique_id` — только после `canonical`.

**Live (2026-08-26):** research escalation archived, non-blocking. Safety Review V1.1 is **not** the next Product and is not opened. Next = [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). `box_breathing` = skipped_for_now.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | research archive / non-blocking; live next = library fill, not Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Ingest V1 closed; next = Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Shortlist V1 = stop A; next = Targeted Safety Ingest |
| 2026-08-26 | pointer: Safety Review V1 = insufficient_safety; next = owner decides |
| 2026-08-25 | pointer: Normalization V1.1 = normalize_one candidate; next = Safety Review |
| 2026-08-25 | pointer: Targeted Ingest V1 closed; next = Normalization V1.1 |
| 2026-08-25 | pointer: Targeted Shortlist V1 closed; next = targeted ingest → Normalization V1.1 |
| 2026-08-25 | pointer: Normalization V1 = insufficient_evidence; next = targeted shortlist |
| 2026-08-25 | pointer: Ingest V1 recorded selected loci as evidence; next = Normalization V1 |
| 2026-08-25 | v1.0 ACCEPTED — vertical slice `equal_count_breath`; three selected loci; conflicts recorded; technique canon empty |
