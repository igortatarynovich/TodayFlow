# Practice Technique Targeted Safety Ingest v1

> **Research archive / non-blocking (2026-08-26).** Historical evidence only. Not in NOW. Does not unlock fill. Active process: [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md). Index: [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

**Статус:** `ACCEPTED` — paraphrase двух selected safety loci. **Не** Safety Review V1.1. **Не** technique canon.  
**Версия:** 1.0 (2026-08-26).  
**Владелец:** Product + Research.  
**Targeted Safety Shortlist:** [PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md) (stop A).  
**Safety Review V1:** [PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md](./PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md) (`insufficient_safety`, S-B2).  
**Candidate:** [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md) (`normalize_one`; hold `required`).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_targeted_safety_ingest_v1.json`](../../DATA/reference/practice/technique_targeted_safety_ingest_v1.json) · contract [`technique_targeted_safety_ingest_contract_v1.json`](../../DATA/reference/practice/technique_targeted_safety_ingest_contract_v1.json).

**Это:** что утверждают *два* selected hold-safety loci, своими словами, без copy.  
**Это не:** продуктовый `who_must_not_hold` · contraindication list для four-phase square breathing · новые safety rules · rewrite kernel · Canonical Technique · `technique_id`.

`technique_canon_v1.json` остаётся **пустым**.  
`practice.box_breathing.001` остаётся provisional, без `technique_id`.  
Kernel V1.1 **не** переоткрывается.  
Safety Review V1 контракт **не** переписывается.

---

## Architecture impact

- **SoT before:** Targeted Safety Shortlist V1 = stop A. Joshi 2024 selected as `hold_exclusion`; Nivethitha 2017 selected as `hold_precaution`. Следующий шаг мог склеить kumbhaka contraindications и empty-lung BP rise в `who_must_not_hold` для box/square.
- **SoT after:** targeted safety ingest = **ровно два selected loci → independent safety observations**. Joshi: exclusion statements про *kumbhaka / breath retention*, `practice_context = kumbhaka`, не who-list кандидата. Nivethitha: `observed_physiological_response` для empty-lung retention; dose/duration unspecified in this locus; не exclusion list и не доказательство риска короткой post-exhale паузы. `transfer_limits[]` обязательны. После ingest **нет** новых правил безопасности. Safety Review V1.1 впервые решит: достаточно ли для `may_release`, и остаётся ли бинарный `who_must_not_hold` корректной моделью (там же exclusion / precaution / stop_rule, не раньше).
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · JSON · provenance §11 · coverage · landscape pointer · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с `technique_id`, записью canon, `who_must_not_hold`, `may_release`, или optional hold из этого pass.

---

## 0. Закон этого pass

1. **Только два selected loci.** Supporting / rejected / already-ingested method records не ingest заново. BTS/CUH exertion advice не переносится.
2. **Один locus — одна evidence record.** Joshi и Nivethitha не усредняются.
3. **Paraphrase, не copy.** Yoga-as-therapy / efficacy не ingest (C6).
4. **Observation ≠ product rule.** `observed_*` = что написал этот источник в своём named practice.
5. **Чужой дыхательный контекст ≠ four-phase square.** Kumbhaka не становится box/square. Empty-lung retention не становится 4-count hold.
6. **Ingest ≠ Safety Review V1.1.** Запрещены формулы: «who_must_not_hold = …», «box contraindicated in hypertension», «acute BP rise proves the product hold is unsafe», «may_release».
7. **Dose остаётся видимой.** Не импортировать длительность retention из соседних статей той же группы авторов.

---

## 1. Граница

```text
Targeted safety shortlist selected loci
  → targeted ingested safety observations
  ≠ product contraindication list
  ≠ who_must_not_hold
  ≠ Safety Review V1.1 decision
  ≠ Canonical Technique
```

Family ingest V1 и targeted identity ingest остаются отдельным корпусом. Этот pass их не заменяет.

---

## 2. Две записи

| `evidence_id` | Locus | `speech_type` | Что фиксирует | Чего не делает |
|---------------|-------|---------------|----------------|----------------|
| `ev.safety.wjm.joshi.2024.yoga_hypertension` | Joshi / Raveendran / Arumugam, *World J Methodol* 2024, precautions prose + Table 3 kumbhaka row | `hold_exclusion` | Observed exclusion statements: kumbhaka contraindicated in hypertension, heart disease, recovery from illness/surgery/injury. `practice_context = kumbhaka`. Table 3 reports BP rise (cites Nivethitha 2017); prose writes «contraindicated» — держать раздельно. | Не называет box/square. Не клинический guideline. Не `who_must_not_hold` кандидата. Yoga-as-hypertension-therapy out of scope. Adjacent bandha / long-retention — другой named practice. |
| `ev.safety.nivethitha.2017.bahir_kumbhaka` | Nivethitha / Mooventhan / Manjunath, *Adv Integr Med* 2017, legally readable abstract/preview | `observed_physiological_response` | Acute rise in SBP/DBP/MAP during bahir kumbhaka (external / empty-lung retention) in healthy volunteers. SBP reverted after; DBP and MAP did not, as this paper reports. | Не exclusion list. Не доказательство риска короткой post-exhale паузы. Dose/duration **unspecified in this locus**; не импортировать 1 min из других статей. Study response ≠ contraindication. |

---

## 3. Поля evidence record

`evidence_id` · `candidate_family` · `source_ref` · `locus` · `source_family` · `paraphrase` · `speech_type` · `named_practice` · `practice_context` · `hold_phase` · `dose_or_duration` · `population` · `observed_exclusions[]` · `observed_precautions[]` · `observed_physiology[]` · `transfer_limits[]` · `source_claim_scope` · `ingest_status`

`ingest_status` этого pass: `ingested`. Не `extracted`, не `canonical`.

`speech_type`: `hold_exclusion` · `observed_physiological_response`.  
Nivethitha на shortlist была `hold_precaution` (допуск). Ingest записывает, *что источник сделал*: физиологическое наблюдение, не who-list.

`observed_exclusions[]` — statements источника внутри `practice_context`. Не product `who_must_not_hold`.

`transfer_limits[]` обязательны. Минимум, который V1.1 не имеет права стереть:

- kumbhaka ≠ four-phase square breathing;
- unspecified / long retention ≠ short timed hold;
- empty-lung retention физиологически ближе к post-exhale hold, но не тождественна продуктовой дозе;
- study response ≠ contraindication.

---

## 4. Что Safety Review V1.1 должен решить отдельно

Не в этом pass. Два независимых вопроса:

| Вопрос | Этот pass |
|--------|-----------|
| Достаточно ли evidence для `may_release`? | Не решено |
| Остаётся ли бинарный `who_must_not_hold` корректной моделью? | Не решено. Exclusion / precaution / stop_rule **впервые** допустимы там, не здесь |

S-B2 V1 не отменяется. Kernel не reopen. Probe без `technique_id`.

---

## 5. Запрещено

- Писать `technique_canon_v1.json` или `technique_id`.
- Писать `who_must_not_hold` / contraindication list кандидата.
- Объявлять новые product safety rules.
- Переносить kumbhaka exclusions на box/square.
- Переносить empty-lung BP rise на 4-count post-exhale pause.
- Импортировать hold duration из других Nivethitha papers.
- Ingest BTS / CUH / Healthline / MNT.
- Открывать Safety Review V1.1 внутри этого файла как закрытый verdict.
- Объявлять hold optional. Reopen kernel. Следующая семья.

---

## 6. Что дальше

1. Targeted Safety Ingest закрыт. Shortlist stop A стоит. Safety Review V1 = `insufficient_safety`. Canon пуст. Probe не attested.
2. Исторический next этого pass: Safety Review V1.1 (**не открывать**). Не canonical.
3. `technique_id` — только при `canonical`, и только после `may_release`.

**Live (2026-08-26):** research escalation archived, non-blocking. Safety Review V1.1 is **not** the next Product and is not opened. Next = [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). `box_breathing` = skipped_for_now.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | research archive / non-blocking; live next = library fill, not Safety Review V1.1 |
| 2026-08-26 | v1.0 ACCEPTED — two safety observations; kumbhaka exclusions stay in kumbhaka context; Nivethitha is physiology not a who-list; transfer_limits locked; next = Safety Review V1.1 |
