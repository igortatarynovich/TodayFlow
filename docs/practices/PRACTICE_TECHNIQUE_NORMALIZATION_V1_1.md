# Practice Technique Normalization v1.1

> **Research archive / non-blocking (2026-08-26).** Historical evidence only. Not in NOW. Does not unlock fill. Active process: [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md). Index: [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

**Статус:** `ACCEPTED` — повторная нормализация после targeted ingest. **Не** Canonical Technique.  
**Версия:** 1.1 (2026-08-25).  
**Владелец:** Product + Research.  
**V1:** [PRACTICE_TECHNIQUE_NORMALIZATION_V1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md) (`insufficient_evidence`, история стоит).  
**Family ingest:** [PRACTICE_TECHNIQUE_INGEST_V1.md](./PRACTICE_TECHNIQUE_INGEST_V1.md).  
**Targeted ingest:** [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md).  
**Landscape:** [PRACTICE_TECHNIQUE_LANDSCAPE_V1.md](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_normalization_v1_1.json`](../../DATA/reference/practice/technique_normalization_v1_1.json) · contract [`technique_normalization_v1_1_contract_v1.json`](../../DATA/reference/practice/technique_normalization_v1_1_contract_v1.json).

**Это:** проверка первоначальной нарезки `family.practice.equal_count_breath` по двум осям, затем overall verdict.  
**Это не:** голосование loci · optional hold · technique canon row · `technique_id` · аттестация probe.

`technique_canon_v1.json` остаётся **пустым**.  
`practice.box_breathing.001` остаётся provisional, без `technique_id`.  
V1 JSON **не** переписывается.

Решение этого pass: **`normalize_one`**. Выход = **normalized candidate**, не canon.

---

## Architecture impact

- **SoT before:** V1 = `insufficient_evidence`. Targeted ingest дал definition/contrast (Marchant square vs 5:5) и label observation (CAVUHB 4-4-6-2 *square*). Landscape kernel всё ещё «four equal phases; ratio identity is the kernel». Оси были сигнал.
- **SoT after:** V1.1 решает оси по **зафиксированным критериям**, не по числу loci. `post_exhale_hold = required`. `equal_count = common_parameter`. Overall = `normalize_one`. Landscape family **ремапится**: identity = четырёхфазная структура с post-exhale hold; equal count уходит в параметры. `family_id` остаётся ledger-ключом исследовательской нити (история V1 не стирается: `mechanism_shape_at_landscape_v1`). Normalized candidate ≠ `technique_canon` row. Следующий named pass = **Safety Review**. Probe без `technique_id`.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · V1.1 JSON · landscape remap · provenance §11 · coverage · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с записью canon или `technique_id` из этого pass.

---

## 0. Закон этого pass

1. **Три overall-исхода.** `normalize_one` · `split_family` · `insufficient_evidence`. Новых статусов нет.
2. **Сначала оси, потом verdict.** `post_exhale_hold` и `equal_count` решаются отдельно.
3. **Не голосовать loci.** Критерии ниже, не 4 против 1.
4. **`absent_but_unaddressed` ≠ автоматический unresolved.** Опущение без identity-claim не опровергает definition/contrast.
5. **`common_parameter` разрешён контрактом**, если тот же ярлык метода встречается с неравным счётом и никто не доказывает, что равенство *есть* метод.
6. **`split_family` только при двух identity-bearing структурах**, не при naming inconsistency.
7. **Если hold unresolved — overall `insufficient_evidence`.** Ясность второй оси сама по себе не даёт kernel.
8. **`normalize_one` ≠ canonical.** Только normalized candidate. Дальше Safety Review → canonical/rejected → `technique_id` → probe assessment.
9. **Landscape правится provenance'ом, не задним числом.** Исходная hypothesis сохраняется рядом с remap.

---

## 1. Критерии осей (locked)

### `post_exhale_hold`

| Код | Когда |
|-----|--------|
| **N-H1 `required`** | Definition/contrast в preferred class включают post-exhale hold в четырёхфазную / four-side структуру; no-hold паттерн назван *другим* условием; единственное опущение — `absent_but_unaddressed` без claim, что это другой метод или что hold optional. |
| **N-H2 `optional`** | Preferred-class источник прямо говорит: hold можно убрать, метод тот же. |
| **N-H3 `unresolved`** | N-H1 и N-H2 не выполнены. |

N-H2 в этом корпусе **нет** (variant в preferred class не найден).

### `equal_count`

| Код | Когда |
|-----|--------|
| **N-E1 `identity_bearing`** | Источники утверждают, что равная длительность *делает* метод этим методом (неравный счёт = другой метод). |
| **N-E2 `common_parameter`** | Preferred-class источник использует тот же method-label при неравных counts, и никто не аргументирует равенство как identity. «Встречается часто, но не необходимо» из этого набора **разрешено**. |
| **N-E3 `unresolved`** | N-E1 и N-E2 не выполнены. |

### Overall

| Исход | Когда |
|-------|--------|
| **`normalize_one`** | Обе оси resolved (`required`\|`optional` и `identity_bearing`\|`common_parameter`). |
| **`insufficient_evidence`** | Hold остаётся `unresolved`. |
| **`split_family`** | Evidence показывает **две** identity-bearing структуры как разные методы, не одну naming collision. |

---

## 2. Corpus

Family ingest: BHF · SFH · Newcastle.  
Targeted ingest: Marchant 2025 · CAVUHB.

V1 сравнение sequences не отменяется; этот pass проверяет **нарезку семьи**.

---

## 3. Ось `post_exhale_hold` → `required` (N-H1)

| Evidence | Что сообщает |
|----------|----------------|
| BHF / SFH | Definition: four-phase, включая hold после выдоха. |
| Marchant square | Definition: 4-4-4-4 с обоими holds. |
| Marchant 5:5 | Contrast: no-hold equal breathing — *другое named condition*, не square. |
| CAVUHB | Four-side *square* с hold после выдоха (2), даже при неравных counts. |
| Newcastle | `absent_but_unaddressed`: *square* без записанного post-exhale hold. Не утверждает, что отсутствие hold = другой метод, и не говорит, что hold optional. |

Newcastle **не** держит ось в unresolved: опущение без identity-claim не опровергает definition/contrast. Это не голос «1 против 4». N-H2 не выполнен → не `optional`.

---

## 4. Ось `equal_count` → `common_parameter` (N-E2)

| Evidence | Что сообщает |
|----------|----------------|
| BHF / SFH / Marchant square | Равный счёт (обычно 4) **используется**. Никто не доказывает, что равенство = метод. |
| CAVUHB | Тот же ярлык *square* на 4-4-6-2. |

`identity_bearing` (N-E1) защитить нельзя: official_health называет неравный счёт тем же именем. N-E2 выполнен: равенство обычно, не необходимо.

CAVUHB не становится «разрешённым variant канона» в смысле ingest. Это **параметр timing**, после того как identity = фазы, не ratio.

---

## 5. Overall → `normalize_one`

Вопрос V1.1: ошибочно ли landscape склеил square/box **phase structure** и **equal timing ratio** в `family.practice.equal_count_breath`?

Да. Hold required + equal_count common_parameter → одна техника (четырёхфазная структура), не две семьи.

**Почему не `insufficient_evidence`:** hold resolved по N-H1.

**Почему не `split_family`:** нет двух identity-bearing методов. Newcastle — naming inconsistency. Marchant 5:5 — другое условие *того* эксперимента, не вторая landscape family. CAVUHB — тот же four-phase square с другим timing.

---

## 6. Remap landscape (не стирание V1)

`family_id` = `family.practice.equal_count_breath` остаётся **ключом нити**. Это не утверждение, что equal count — ядро.

| Поле | Landscape V1 (сохранено) | После V1.1 |
|------|--------------------------|------------|
| `mechanism_shape_at_landscape_v1` | four equal phases; ratio identity is the kernel | (история) |
| `mechanism_shape` | — | four timed phases including post-exhale hold; equal duration is a common parameter |
| `candidate_family_at_landscape_v1` | equal-count / square breathing | (история) |
| `candidate_family` | — | four-phase square / box breathing |

Normalized candidate:

- **Kernel:** четыре timed фазы, включая hold после вдоха и после выдоха.
- **Common parameters:** длина счёта; равны ли стороны; циклы; поза; обвести квадрат.
- **Не kernel / не variant:** Marchant 5:5 (другое имя в том исследовании); Newcastle 3-phase (naming inconsistency, по-прежнему не variant).

Probe `box_breathing` остаётся expression hypothesis. 4-4-4-4 payload совместим с kernel, но type не attested до canonical.

---

## 7. Запрещено

- Писать `technique_canon_v1.json`.
- Ставить `technique_id`.
- Считать probe attested.
- Объявлять hold optional.
- Голосовать loci.
- Split из-за ярлыка *square* на разных counts.
- Стереть V1 `insufficient_evidence` или исходный landscape kernel.
- Открывать остальные семьи.

---

## 8. Что дальше

```text
Normalized candidate → Safety Review (closed: insufficient_safety)
  → Targeted Safety Shortlist (stop A)
  → Targeted Safety Ingest (observations, not a who-list)
  → Safety Review V1.1
  → (if later may_release) canonical | rejected → technique_id → probe assessment
```

1. V1.1 = `normalize_one` (история). Safety Review = `insufficient_safety`. Targeted Safety Shortlist = stop A. Targeted Safety Ingest = two observations. Canon пуст.
2. Исторический next этого pass: Safety Review V1.1 (**не открывать**). Не следующая семья.
3. `technique_id` — только при `canonical`.

**Live (2026-08-26):** research escalation archived, non-blocking. Safety Review V1.1 is **not** the next Product and is not opened. Next = [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). `box_breathing` = skipped_for_now.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | research archive / non-blocking; live next = library fill, not Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Ingest V1 closed; next = Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Shortlist V1 = stop A; next = Targeted Safety Ingest |
| 2026-08-26 | pointer: Safety Review V1 = insufficient_safety; next = owner decides |
| 2026-08-25 | v1.1 ACCEPTED — axes: hold required, equal_count common_parameter; overall normalize_one; landscape remapped; candidate ≠ canon |
