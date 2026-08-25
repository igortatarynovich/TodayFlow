# IL-3 → product surface payload audit (2026-08-25)

**Status:** facts for [COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md](../COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md). **Not** IL-3 rank rewrite. **Not** user-relevance inside Astrology (IL-3 stays sky-internal). **Not** Layer 5 recipes. **Not** Knowledge Core expand.

**Question:** what does IL-3 emit, what does the product keep, what does Kimi still have to throw away?

IL-3 SoT: [IL3_INTERPRETATION_ENGINE_V1.md](../astrology/IL3_INTERPRETATION_ENGINE_V1.md) — rank ≠ person priority. Attach: [IL4_SURFACE_ATTACH_V1.md](../astrology/IL4_SURFACE_ATTACH_V1.md). Express: [IL4_EXPRESSION_V1.md](../astrology/IL4_EXPRESSION_V1.md).

---

## Architecture impact

- **SoT before:** IL-4 attach named “today = primary theme only; profile/compat = full rank.” No measured bag size on the LLM side, so Kimi could still be treated as the selector.
- **SoT after:** This audit is the **payload fact sheet**. Today IL meaning is 1 line before Kimi. Profile natal decode and Compatibility send the **entire composed IL-3 list** (no 5–8 cut). Rank is position, not a score. 245+84 is library cartesian coverage, not activations in the prompt. Next engineering (owner-directed): **selection after IL-3** for Profile/Compat (and drop `dropped` refusals from Today prompts). Do not reopen IL-3 as user relevance. Do not add atoms.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · compute lifecycle §7 · tracker
- **Backward compatible?** yes (read-only)

---

## 0. What IL-3 actually does

Code: `knowledge/il3_interpretation_v1.py` → `interpret()`.

1. Each sky fact → IL-2 compose; missing atom → `dropped`.
2. Sort: transit band before natal band; **within a band, input order**.
3. `rank` = 1…N. `role=primary` iff `rank==1`. **No float score.** No CE, goals, or person fields.

This is sky-internal order. It is **not** “what to show this user.” Downstream selection may filter; it must not rewrite this order ([IL3](../astrology/IL3_INTERPRETATION_ENGINE_V1.md) R6).

Library cartesian (not prompt size): `transit_to_natal` **245** + `transit_through_house` **84** inside **616** covered cells ([LIBRARY_SCALE_V1.md](../astrology/LIBRARY_SCALE_V1.md)).

---

## 1. Cut at IL-4 (the only product filter today)

`knowledge/il4_expression_v1.py` → `express()`:

```text
selected = themes.themes[:1]  if surface == "today" else themes.themes
```

No N=5 / N=8 anywhere in wire / attach / express.

| Surface | Lines in `il4_expression_pack` | Typical composed themes (synthetic full 10-planet natal+transit) |
|---------|--------------------------------|------------------------------------------------------------------|
| Today | **1** (primary; transit-first) | ~35 composed; ~40 dropped still serialized on the pack |
| Profile | **all** | ~24 natal-only / ~35 with transit band |
| Compatibility | **all** (partner chart as transit band) | same order of magnitude when both charts exist |

Pack fields: `surface, tone, meaning_source, lines[{rank,band,role,construction,jobs,text}], dropped[]`. Compact for prompts drops `role` / job splits but **does not truncate theme count**. Dropped refusals are included.

---

## 2. Per surface: what Kimi sees besides IL

### Today (native C1)

| Piece | Pre-LLM? | Size / rule |
|-------|----------|-------------|
| IL-4 lines | yes — 1 theme | `express(today)` |
| IL-4 `dropped` | dumped | ~40 rows; prompt says not to voice them |
| Dramaturgy brief | **yes** | `must_dramatize` ≤3, `supporting_facts` ≤2 |
| Day events | slim | driver rows in interpretation nest |
| Natal activations | partial | personalization pack cap **6**; conflict top **3** |
| Raw ephemeris | no | slim moon / ingresses[:3] / aspects[:2] |
| User message cap | yes | `max_chars=16000` |

**Verdict:** astrology *meaning* is already 1 theme. Cost/quality leak is **dropped refusals + non-IL context**, not “50 IL meanings.” Plot selection for the day is the dramaturgy brief (≤5 drivers), separate from IL-3.

GET `/today/contract` does not call LLM. Native LLM runs on `force_rebuild` (refresh / prewarm / ops).

### Profile — Natal Decode (K3)

- IL-4: **full rank** (~24 natal-only lines).
- **Also** raw `natal_pack` (planets ≤14, houses, angles) + Identity Core + numerology + tension.
- GET never rebuilds; `ops_force` / POST on cache miss only.

Kimi must not invent beyond IL lemmas **and** still sees a second geometry dump. That is double SoT in one prompt — a quality risk, not just tokens.

### Character Engine

**No IL-4.** Stage 2 context ≈ raw facts + grounded claims. Portrait SoT is CE, not IL ([IL1_HANDOFF.md](../astrology/IL1_HANDOFF.md)).

### Compatibility

Template / encyclopedia first on read. LLM editorial when charts exist: **full IL-3 bag** + structured synastry. Quick-compat without charts → no IL-4.

---

## 3. The hole (IL-3 ranked themes → surface)

```text
IL-3 ranked themes  →  ??? selection ???  →  product / Kimi
```

| Surface | Selection today | Gap |
|---------|-----------------|-----|
| Today IL meaning | 1 primary line | too coarse if we ever need 5–8 day themes; `dropped` still in prompt |
| Today plot | dramaturgy ≤5 drivers | exists; not IL-3 |
| Profile decode | **none** (full bag + natal_pack) | Kimi ranks ~24 themes herself |
| Compat | **none** (full bag) | same |
| Relevance engine | **not implemented** (out of IL-3 scope) | do not put person-relevance inside IL-3 |

**Next cut without new atoms:** curated **5–8** already-ranked IL-3 themes into Natal Decode / Compatibility prompts; strip `dropped` from Today `IL4_MEANING`; stop sending raw natal_pack as a parallel meaning source once IL-4 lines are the sky theses.

---

## 4. This audit does not do

- Change `express()` / IL-3 sort / public JSON
- Implement Relevance as meaning SoT
- Open Layer 5 pair essays
- Measure production JSONL (Token Factory still the ops gate)

---

## Changelog

- **1.0 (2026-08-25)** — Payload facts. Today 1 IL line; Profile/Compat full bag. Next = selection, not atoms.
