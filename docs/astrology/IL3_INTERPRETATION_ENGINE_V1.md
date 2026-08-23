# IL-3 Interpretation Engine V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — sky → ranked astrological themes. **Not** user relevance. **Not** pair catalog. **Not** Layer 5 essays. **Not** pack rewrite. **Not** `active`. **Not** freeze / IL-2 reopen. **Not** a new “canonical v2.” **Not** IL-4 expression. **Not** LLM copy.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) Sequence · §6.61 · §6.62 · §7 IL-3 row. Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) KC-C-RULES · KC-C-ENGINE · step 36. Frames: [IL2_COMPOSITION_RULES_V1.md](./IL2_COMPOSITION_RULES_V1.md). Atoms: [KNOWLEDGE_CORE_V1_FREEZE.md](./KNOWLEDGE_CORE_V1_FREEZE.md). Boundary: [IL1_HANDOFF.md](./IL1_HANDOFF.md) §3. AGENTS.md Architecture impact.

This pass answers: **which composed frames are stronger in this sky**, not **what matters to a named person today.** Meaning is already in stored lemmas + IL-2 frames. IL-3 only orders a bag of frames.

Catalog **38 draft / 0 `active`**. Unchanged this pass. Runtime still ignores `draft`.

---

## Architecture impact

- **SoT before:** IL-2 emits a bag of typed frames (1.3.107). Sequence still named clustering → primary/supporting. Handoff §3 locked **IL-3 rank ≠ user relevance**, but there was no engine, so a next pass could still read Character Engine, start Relevance, merge House 1 into ASC, or write pair essays as “themes.”
- **SoT after:** IL-3 **rules + library** are the theme-rank SoT. Input = sky facts (construction + stored object ids). Compose via IL-2. Rank is **sky-internal**: `transit` band before `natal` band; within a band, input order. Two constructions stay two themes. Missing atoms are dropped, not invented. No person fields. No essays. Next named = **IL-4** expression. Freeze and IL-2 stand. Not a “canonical v2.”
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.62 · inventory KC-C-ENGINE + step 36 · ACM pointer · freeze §3 · handoff §3 · tracker NOW
- **Backward compatible?** yes (`draft`). Deprecated as next: user relevance inside Astrology; CE/goals as IL-3 input; pair catalog; Layer 5 essays; occupancy = conjunction; House 1 = ASC; MC = career; `interaction` as relation; Swiss/Today wiring; Relevance / Prioritization engines.

---

## 0. Inputs

| Input | Allowed | Forbidden |
|-------|---------|-----------|
| Sky facts | construction type + `astro.*` ids the calc layer can emit | user id, CE, goals, prefs, history, feedback |
| Atoms | stored `canon` via IL-2 | lemma rewrite, CORE, gold-set 41 as a gate |
| Frames | IL-2 `composed` frames | pair essays, Layer 5 objects |

A sky fact is one IL-2 construction. It is not a cookbook object.

---

## 1. Compose then rank

1. Map each sky fact to IL-2 `compose_*`.
2. `composed` → candidate theme. `refused` (missing atom) → dropped. Do not invent Uranus/Neptune/Pluto/DSC/IC lemmas.
3. Rank composed frames. Do not average lemmas. Do not union jobs.

IL-2 conflict rules still hold after rank: occupancy ≠ conjunction; House 1 ≠ ASC; House 10 ≠ MC; MC ≠ career; `interaction` ≠ `relation`; two constructions stay two themes.

---

## 2. Sky-internal rank (not user relevance)

| ID | Rule |
|----|------|
| R1 | **Transit band before natal band.** `temporal_class=transit` is sky-now. `natal` is chart structure. Time class ≠ “important to this user.” |
| R2 | **Within a band, keep input order.** No angularity score. Angular strength is not meaning (1.3.100) and is not an IL-3 rank key. |
| R3 | **Primary** = first composed frame after R1–R2. **Supporting** = the rest, same order. Labels are list shape, not person priority. |
| R4 | **No clustering that merges constructions.** Mars IN 1st and Mars AT ASC remain two themes. Occupancy and conjunction remain two themes. |
| R5 | **Dropped ≠ ranked.** Missing-atom refusals do not occupy primary/supporting. |
| R6 | **Person-blind.** Engine signature has no user / CE / goals. Downstream Relevance may filter; it may not rewrite this order. |
| R7 | **No essay.** IL-4 speaks. IL-3 returns ranked frames with stored lemmas copied verbatim. |

Do **not** rank by Character Engine, goals, “what Igor cares about,” or screen slot.

---

## 3. Output (library / tests; not a catalog record)

```text
themes[ {rank, band: transit|natal, role: primary|supporting, frame} ],
dropped[ refused frames ],
essay=FORBIDDEN, person_id=FORBIDDEN, user_relevance=FORBIDDEN
```

Five jobs stay partitioned on every composed frame.

---

## 4. This pass does not do

- Lemma rewrite · pack enrich · schema · `objects_v1.json`
- Set `active` · Swiss / Today / LLM wiring
- Books · CORE scoring · Co–Star ingest
- Pair catalog · Layer 5 essays · ASC cookbooks · outer objects
- Occupancy = conjunction · House 1 = ASC · MC = career · `interaction` as relation
- User relevance · Character Engine · Prioritization / Continuity / Trust / Expression
- Merge to `main` · deploy
- Reopen FREEZE / IL-2 / Angles / Aspects / Houses / Signs
- A parallel “canonical v2”

**Next named:** IL-4 Expression — **done 1.3.109.** Library scale — **done 1.3.110.** Wire calc → IL — **done 1.3.111.** Next = attach IL-4 packs to product surfaces. **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do **not** start CORE scoring. Do **not** start ASC cookbooks. Do **not** start Relevance / Prioritization engines. Layer 2 Signs stays classification-complete / interpretation-deferred.

---

## Changelog

- **1.3 (2026-08-23)** — Calc → IL wire done 1.3.111. This engine stands. Next named = attach IL-4 packs to product surfaces.
- **1.2 (2026-08-23)** — Library scale done 1.3.110. This engine stands. Next named = wire calc → IL. **Done 1.3.111.**
- **1.1 (2026-08-23)** — IL-4 Expression done 1.3.109. This engine stands. Next named = library scale. **Done 1.3.110.**
- **1.0 (2026-08-23)** — 1.3.108. IL-3 Interpretation Engine. Sky-internal theme rank. Catalog unchanged. Next named = IL-4. **Done 1.3.109.**
