# Number Base v1 — digit meaning SoT

**Status:** ACTIVE (2026-08-02)  
**Type:** static user-facing base meanings (lookup)  
**Data:** `DATA/reference/numerology/number_base_v1/numbers.json`  
**Loader:** `todayflow_backend.data.number_base_v1`  
**Related:** [DAY_SYMBOL_REVEAL_CANON_V1.md](../audits/DAY_SYMBOL_REVEAL_CANON_V1.md) · foundation constants §8 draft

---

## 0. Why

`numerology_explainer` must **not** invent digit archetypes. Same rule as tarot `card_base_v1` / color catalog: generators personalize a **bridge**; they do not own meaning.

---

## 1. Scope

| | |
|--|--|
| Core digits | **1–9** |
| Masters in use | **11, 22, 33** (product `master_numbers`) |
| Master documented, not live | **44** (`in_use: false` → reduce as 4+4=8) |
| Karmic debts | **13, 14, 16, 19** (lookup when surfaced) |
| Locale | `ru` |

**Reduction rule:** sum digits to a single digit, except stop on 11/22/33. Do not treat 20/44 as unreduced masters unless product flips `in_use` for 44.

---

## 2. Finding: FE key `"20"`

| Question | Answer |
|--|--|
| Is 20 a master or karmic debt? | **No** |
| Does `NumerologyService._reduce` emit 20? | **No** — only masters in `[11,22,33]` are kept |
| Where did `"20"` live? | Only FE `NUMBER_RHYTHM_BY_VALUE` + spine tests |
| Verdict | **Bogus FE/test fixture**, not a reduction bug. Removed. |

---

## 3. Consumers

| Surface | Use |
|--|--|
| `hook_reveal_v1` / day symbols | `base_meaning` + keywords |
| `numerology_explainer` | prompt block «Базовое значение»; force `meaning` from bank; fallback from bank |
| FE `NUMBER_RHYTHM_BY_VALUE` | mirror of `base_meaning` for spine facets (no independent dictionary) |

`number_type` (day / life_path / personal_year) does **not** get a separate archetype table — only bridge text changes scale.

---

## 4. Canon notes

- **16 (karmic):** classical Hans Decoz (ego/pride → humility crisis). Alternate “love difficulties” rejected for product unity.
- **44:** kept in JSON for completeness; validation fails if marked `in_use: true` while product masters stay 11/22/33.
