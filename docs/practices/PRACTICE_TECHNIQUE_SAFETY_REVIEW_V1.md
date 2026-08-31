# Practice Technique Safety Review v1

> **Research archive / non-blocking (2026-08-26).** Historical evidence only. Not in NOW. Does not unlock fill. Active process: [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md). Index: [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

**Статус:** `ACCEPTED` — review normalized candidate. **Не** Canonical Technique.  
**Версия:** 1.0 (2026-08-26).  
**Владелец:** Product + Research.  
**Normalization V1.1:** [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md) (`normalize_one` candidate).  
**Family ingest:** [PRACTICE_TECHNIQUE_INGEST_V1.md](./PRACTICE_TECHNIQUE_INGEST_V1.md).  
**Targeted ingest:** [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md) §0 · §2 · §5 · §6.  
**Machine:** [`technique_safety_review_v1.json`](../../DATA/reference/practice/technique_safety_review_v1.json) · contract [`technique_safety_review_contract_v1.json`](../../DATA/reference/practice/technique_safety_review_contract_v1.json).

**Это:** имеет ли продукт право выпускать уже нарезанный метод — bounds, stop-rules, who-must-not, claim surface.  
**Это не:** invent kernel · optional hold · split семьи · technique canon row · `technique_id` · аттестация probe.

`technique_canon_v1.json` остаётся **пустым**.  
`practice.box_breathing.001` остаётся provisional, без `technique_id`.  
V1 JSON и landscape V1 hypothesis **не** стираются.  
Kernel V1.1 **не** переоткрывается.

Решение этого pass: **`insufficient_safety`**. Выход = закрытый review ledger, не canon.

---

## Architecture impact

- **SoT before:** V1.1 = `normalize_one`. Kernel = four timed phases, post-exhale hold `required`, equal count `common_parameter`. Следующий шаг мог склеить Safety Review с canonical, объявить hold optional, или выпустить метод на SFH stop-rules без who-must-not.
- **SoT after:** Safety Review — отдельный named pass с тремя вердиктами. `unknown ≠ unsafe` и `unknown ≠ permission to ship`. Для required hold действует **S-B2**: SFH stop-rules недостаточны для `may_release`, пока не закрыт `who_must_not_hold`; отсутствие этого evidence не есть запрет. Corpus пяти ingested records даёт stop-rules (SFH, не в kernel) и не закрывает who-must-not; prohibition = none. Overall = `insufficient_safety`. `review_status` кандидата остаётся `normalized`. Canon row и `technique_id` не пишутся. Следующий named pass **не** открывается автоматически.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · safety-review JSON · provenance §11 · coverage · landscape pointer · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с записью canon, `technique_id`, или `may_release` из этого корпуса.

---

## 0. Закон этого pass

1. **Только после `normalize_one`.** Kernel уже стоит. Этот pass его не invent и не режет заново.
2. **Три overall-исхода.** `may_release` · `insufficient_safety` · `may_not_release`. Других нет.
3. **Сначала оси, потом verdict.** Bounds · stop-rules · who-must-not · prohibition · claim surface.
4. **S-B2 locked.** Required identity-bearing hold: SFH-class stop-rules ≠ `may_release`, пока `who_must_not_hold` не закрыт. S-B2 **не** даёт `may_not_release` сам по себе.
5. **`unknown ≠ unsafe` и `unknown ≠ permission to ship`.**
6. **Sequence ≠ safety.** NHS SFH: BOX BREATHING и stop/safety — разные поля. Stop-rules не входят в kernel.
7. **Existence ≠ efficacy.** Marchant trial, традиция, число loci не заполняют `allowed_claims`. Viral «SEAL box breathing» не source.
8. **Review ≠ canon.** `may_release` всё равно не пишет `technique_canon_v1.json`. Canonical | rejected — отдельное решение owner.
9. **`insufficient_safety` ничего не открывает.** Следующий named pass назначает owner.

---

## 1. Критерии (locked)

### Stop-rules

| Код | Когда |
|-----|--------|
| **S-S1 `present`** | Preferred-class источник даёт when-to-stop / sit-lie / redirect; это лежит в safety, не в steps. |
| **S-S2 `absent`** | В ingested corpus stop-rules нет. |

### `who_must_not_hold`

| Код | Когда |
|-----|--------|
| **S-W1 `closed`** | Preferred-class источник называет, *кому нельзя* держать дыхание (population exclusion для required hold). |
| **S-W2 `unknown`** | Никто в корпусе этого не утверждает. Молчание ≠ запрет. |

**S-B2:** при hold `required` S-S1 без S-W1 **не** есть `may_release`.

### Prohibition

| Код | Когда |
|-----|--------|
| **S-P0 `none`** | Нет положительного evidence, что продукт не должен выпускать этот candidate. |
| **S-P1 `present`** | Есть такое evidence. |

### Claim surface

| Код | Когда |
|-----|--------|
| **S-C1 `default_closed`** | `allowed_claims[]` пуст; `prohibited_claims[]` = минимум provenance §5; `efficacy_claim_level = not_claimed`. |
| **S-C2 `invalid_fill`** | `allowed_claims` заполнены из trial / традиции / benefit-заголовков. |

### Overall

| Исход | Когда |
|-------|--------|
| **`may_release`** | Required safety surface закрыт: bounds recorded + S-S1 + S-W1 + S-C1. |
| **`insufficient_safety`** | Недостаточно для ship, и нет evidence запрета (S-P0). |
| **`may_not_release`** | S-P1: положительное evidence, что в продуктовых рамках выпускать нельзя. |

---

## 2. Corpus

Family ingest: BHF · SFH · Newcastle.  
Targeted ingest: Marchant 2025 · CAVUHB.

Новых источников нет. Kernel не пересобирается.

Normalized candidate (вход, не выход):

- **Kernel:** четыре timed фазы, включая hold после вдоха и после выдоха.
- **Hold:** `required` (N-H1). Не optional. Не unresolved.
- **Equal count:** `common_parameter` (N-E2).

---

## 3. Оси → применение к corpus

### Bounds → `recorded`

Hold required — identity V1.1, safety-relevant здесь. Длина счёта и равенство сторон — параметры. Циклы / поза / обвести квадрат — expression. Не identity-вопрос этого pass.

### Stop-rules → `present` (S-S1)

| Evidence | Что сообщает |
|----------|----------------|
| SFH | Отдельный заголовок: light-headedness → сидеть/лежать; если фокус на дыхании неудобен из‑за breathing-related issues → grounding вместо этого листка. Не смешано с BOX BREATHING steps. |
| Marchant | Experimental: не слишком глубоко; при головокружении мельче. Не product stop-rule и не who-must-not. |
| BHF / Newcastle / CAVUHB | В ingested секциях stop-rules нет. |

### `who_must_not_hold` → `unknown` (S-W2)

| Evidence | Что сообщает |
|----------|----------------|
| BHF | Секция не говорит, кто не должен делать pause. `observed_safety` пуст. |
| SFH | Stop-rules и redirect есть. Это не population exclusion для required hold. |
| Newcastle | Не говорит, кто не должен hold. `observed_safety` пуст. |
| Marchant | Explicitly не общий who-must-not-hold bound. |
| CAVUHB | Не говорит, кто не должен hold. `observed_safety` пуст. |

S-W1 не выполнен. S-B2: без who-must-not нет `may_release`.

### Prohibition → `none` (S-P0)

Никто из пяти не утверждает, что продукт не должен предлагать этот метод. SFH публикует sequence. Молчание who-must-not ≠ ban.

### Claim surface → `default_closed` (S-C1)

`allowed_claims[]` пуст. `efficacy_claim_level = not_claimed`. `prohibited_claims[]` = минимум §5 (лечение/диагноз; гарантия сна/спокойствия/денег/отношений; «вылечит тревогу/бессонницу»; манифестация).

Не использованы как claims: BHF benefit-заголовки, Marchant HRV/mood/anxiety, традиция, viral SEAL packaging.

---

## 4. Overall → `insufficient_safety`

Required hold + S-W2 + S-P0 → не ship, не запрет.

**Почему не `may_release`:** S-B2. Stop-rules SFH не закрывают who-must-not.

**Почему не `may_not_release`:** нет S-P1. Unknown ≠ unsafe.

`candidate_review_status` остаётся `normalized`. Не `safety_reviewed` (поверхность не закрыта для ship). Не `rejected` (это не запрет и не строка canon).

---

## 5. Запрещено

- Писать `technique_canon_v1.json`.
- Ставить `technique_id`.
- Считать probe attested / `status: active`.
- Объявлять hold optional или unresolved.
- Голосовать loci. Split из-за ярлыка *square*.
- Смешивать SFH sequence и safety в kernel.
- Заполнять `allowed_claims` из Marchant / традиции / SEO.
- Стереть V1 `insufficient_evidence` или `mechanism_shape_at_landscape_v1`.
- Автоматически открывать следующий named pass.
- Открывать остальные семьи / audio / новые LLM items.

---

## 6. Что дальше

```text
Safety Review insufficient_safety
  → Targeted Safety Shortlist (stop A)
  → Targeted Safety Ingest (observations, not a who-list)
  → Safety Review V1.1
```

1. Safety Review закрыт как `insufficient_safety`. Targeted Safety Shortlist = stop A. Targeted Safety Ingest = two observations. Canon пуст. Type не attested.
2. Исторический next этого pass: Safety Review V1.1 (**не открывать**). Не canonical.
3. `technique_id` — только при `canonical`, и только после `may_release`.

**Live (2026-08-26):** research escalation archived, non-blocking. Safety Review V1.1 is **not** the next Product and is not opened. Next = [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). `box_breathing` = skipped_for_now.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | research archive / non-blocking; live next = library fill, not Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Ingest V1 closed; next = Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Shortlist V1 = stop A; next = Targeted Safety Ingest |
| 2026-08-26 | v1.0 ACCEPTED — S-B2 locked; three verdicts; corpus → `insufficient_safety`; not canon; next = owner decides |
