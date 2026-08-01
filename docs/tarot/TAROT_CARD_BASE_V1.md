# Tarot Card Base v1 — system meaning SoT

**Status:** ACTIVE (2026-08-01)  
**Type:** static user-facing base meanings (lookup)  
**Data:** `DATA/reference/tarot/card_base_v1/cards.json`  
**Loader:** `todayflow_backend.data.card_base_v1`  
**Related:** [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md) (semantic facts for LLM packs) · [DAY_SYMBOL_REVEAL_CANON_V1.md](../audits/DAY_SYMBOL_REVEAL_CANON_V1.md)

---

## 0. Why

Day card, morning ritual, question tarot, and library must show the **same** traditional meaning for `(card_id, orientation)`. That text is **not** generated per day.

Knowledge Base (`knowledge_v1`) remains facts for interpretation packs — not a second prose dictionary for day hooks.

---

## 1. Scope

| | |
|--|--|
| Cards | **78** (ids 0…77) |
| Orientations | **upright** and **reversed** (both required) |
| Locale | `ru` (product) |
| Identity | aligned with `tarot_full_deck.json` ids / `name_ru` |

---

## 2. Record shape

```text
card_base_v1 {
  contract_version: "card_base_v1"
  locale: "ru"
  cards: [{
    id: int                 # 0…77
    name_ru: string
    type: "major" | "minor"
    upright: { base_meaning: string, keywords: [string] }
    reversed: { base_meaning: string, keywords: [string] }
  }]
}
```

Lookup API: `get_base_meaning(card_id, orientation) → { meaning, keywords, name_ru }`.

---

## 3. Consumers (must not fork)

- Day symbol reveal / `hook_reveal` base layer
- Morning ritual card display (`tarot_card.meaning` / free `tarot_explanation.summary`)
- Card-of-day / library / spread strip — `TarotService` `upright`/`reversed`/`meaning` via `card_base_v1.prose_sides`
- Question-tarot interpretation pack catalog strings (`upright_meaning` / `reversed_meaning`)
- Daily card explainer — `meaning` forced from bank; LLM only personalization fields (`tarot-explainer-v4`)

Deprecated as parallel meaning SoT: ad-hoc explainer `meaning` as dictionary, EN `tarot_full_deck` upright/reversed as product prose.

FE `TODAY_TAROT_CARDS_RU` is **labels + sphereBump only** (no lead/body/risk/focus/evening/question). User-facing card prose comes from BE `card_base_v1` via symbols/morning/explainer.

---

## 4. What LLM may still do

Only **bridge_to_day** (from chorus), **instruction**, **personal_angle** — never rewrite `base_meaning`.

---

## 5. Rebuild note (minor-arcana glue, 2026-08-01)

`scripts/build_card_base_v1.py` is the only writer for `cards.json`.

**Bug (fixed):** minor KB rows store semicolon-blobs in both `reversed.central` and `themes[0]`. The first builder did `central + " — " + join(themes)`, producing duplicated prose and blob keywords.

**Editorial schema (all minors 22–77 done — wands/cups/swords/pentacles):** `central` = short scene (1 sentence), must **not** equal `themes[0]`; `themes` = 3–5 atomic tags. No borrowing between the two fields. Ledgers: `docs/tarot_editorial_{cups,swords,pentacles}_v1.json` (+ wands in KB history).

**Reversed school (whole deck):** classical RWS **тень / блок / перекос** — not the softer modern “same theme, internalized” school (e.g. Biddy soft reverses). Majors already use this; minors editorial batches must match. Soft-internalized reverse is out of scope for `card_base` / KB scene+themes.

**Calibration:** upright/reversed scenes must stay on the RWS archetype (cross-check Biddy/Golden Dawn for *identity*, not for soft-reverse tone). One locked correction: Three of Wands upright = horizon expansion / look beyond the threshold — not patience-only.

**Builder rules now:** atomicize tags on `;`; if `central` is a distinct scene → `base_meaning = central` only and `keywords = themes` (no theme re-append); if `central` is still a legacy blob → synthesize meaning from tags only; never keep `;` inside a keyword; normalize `парanoia` → `паранойя`. Validate via `card_base_v1.validate_card_base_v1()`.
