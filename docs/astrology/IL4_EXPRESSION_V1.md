# IL-4 Expression V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — voice for already chosen themes. **Not** meaning. **Not** user relevance. **Not** pair catalog. **Not** Layer 5 essays. **Not** pack rewrite. **Not** `active`. **Not** freeze / IL-2 / IL-3 reopen. **Not** a new “canonical v2.” **Not** LLM choosing Saturn □ Venus. **Not** Today prompts as meaning SoT.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) Sequence · §6.62 · §6.63 · §7 IL-4 row. Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) KC-C-ENGINE · KC-C-EXPR · step 37. Themes: [IL3_INTERPRETATION_ENGINE_V1.md](./IL3_INTERPRETATION_ENGINE_V1.md). Frames: [IL2_COMPOSITION_RULES_V1.md](./IL2_COMPOSITION_RULES_V1.md). Atoms: [KNOWLEDGE_CORE_V1_FREEZE.md](./KNOWLEDGE_CORE_V1_FREEZE.md). Boundary: [IL1_HANDOFF.md](./IL1_HANDOFF.md) §3. AGENTS.md Architecture impact.

This pass answers: **how to say an already ranked theme on a surface**, not **what the sky means** and not **what matters to a named person.** Meaning is already in stored lemmas + IL-2 frames + IL-3 rank. IL-4 only voices.

Catalog **38 draft / 0 `active`**. Unchanged this pass. Runtime still ignores `draft`.

---

## Architecture impact

- **SoT before:** IL-3 returns ranked frames with verbatim lemmas (1.3.108). Sequence named Expression as the generative layer. Handoff §3 locked **voice ≠ meaning**, but there was no pack, so a next pass could still let an LLM choose Saturn □ Venus, write Today prompts as meaning SoT, merge House 1 into ASC, or treat user relevance as astrological rank.
- **SoT after:** IL-4 **rules + library** are the voice SoT. Input = IL-3 theme list + surface (`today` · `profile` · `compatibility`). Output = expression pack. Lemmas copied verbatim. Rank order unchanged. Surfaces differ in **tone / length / focus metadata**, not in meaning. No person fields. No LLM call. Next named = **library scale**. **Done 1.3.110.** Freeze, IL-2, and IL-3 stand. Not a “canonical v2.”
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.63 · inventory KC-C-EXPR + step 37 · ACM pointer · freeze §3 · handoff §3 · tracker NOW
- **Backward compatible?** yes (`draft`). Deprecated as next: LLM as meaning chooser; Today prompts as meaning SoT; user relevance inside Astrology; CE/goals as IL-4 input; pair catalog; Layer 5 essays; occupancy = conjunction; House 1 = ASC; MC = career; `interaction` as relation; Swiss/Today wiring; Relevance / Prioritization engines; set `active`.

---

## 0. Inputs

| Input | Allowed | Forbidden |
|-------|---------|-----------|
| Themes | IL-3 ranked frames (already composed) | re-ranking, clustering that merges constructions |
| Surface | `today` · `profile` · `compatibility` | user id, CE, goals, prefs, history, feedback |
| Lemmas | stored `canon` already copied on the frame | lemma rewrite, CORE, gold-set 41 as a gate |

A surface is a **voice slot**, not a second meaning catalog.

---

## 1. Voice, not meaning

1. Read IL-3 themes in rank order. Do not sort. Do not drop a theme because a person “would not care.”
2. Copy every job’s lemmas **verbatim**. Do not translate, average, or add a gloss.
3. Role weights from IL-2 name **subject vs modifier** of the later sentence. They do not invent a sixth job.
4. Missing-atom refusals stay dropped. Do not voice Uranus/Neptune/Pluto/DSC/IC.

IL-2 conflict rules still hold after voice: occupancy ≠ conjunction; House 1 ≠ ASC; House 10 ≠ MC; MC ≠ career; `interaction` ≠ `relation`; two constructions stay two lines.

---

## 2. Surfaces (tone / length / focus — not meaning)

| Surface | Tone | Length | Focus |
|---------|------|--------|-------|
| `today` | `direct_grounded` | primary theme only | sky-now line; still IL-3 primary, not user priority |
| `profile` | `structural` | all ranked themes | same order as IL-3 |
| `compatibility` | `relational` | all ranked themes | same lemmas; relation job stays visible when the construction has it |

All surfaces include **every job** the construction already filled. Length may omit *supporting themes*, not *jobs on a voiced theme*. Primary lemmas are identical across surfaces.

LLM, if wired later, may only phrase a pack. It may not add themes, swap lemmas, or decide Saturn □ Venus.

---

## 3. Output (library / tests; not a catalog record)

```text
surface, tone,
lines[ {rank, band, role, construction, jobs, subject_jobs, modifier_jobs, text} ],
dropped[ refused frames from IL-3 ],
meaning_source=il3_themes,
person_id=FORBIDDEN, user_relevance=FORBIDDEN, llm_chose_meaning=FORBIDDEN
```

`text` is lemma assembly (`job=lemma · lemma`), not invented prose.

Five jobs stay partitioned on every voiced line.

---

## 4. This pass does not do

- Lemma rewrite · pack enrich · schema · `objects_v1.json`
- Set `active` · Swiss / Today / LLM wiring
- Books · CORE scoring · Co–Star ingest
- Pair catalog · Layer 5 essays · ASC cookbooks · outer objects
- Occupancy = conjunction · House 1 = ASC · MC = career · `interaction` as relation
- User relevance · Character Engine · Prioritization / Continuity / Trust as meaning engines
- Re-rank IL-3 · merge House 1 into ASC
- Merge to `main` · deploy
- Reopen FREEZE / IL-2 / IL-3 / Angles / Aspects / Houses / Signs
- A parallel “canonical v2”

**Next named:** library scale — **done 1.3.110.** Wire calc → IL — **done 1.3.111.** Next = attach IL-4 packs to product surfaces (not a pair catalog, not `active`). **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do **not** start CORE scoring. Do **not** start ASC cookbooks. Do **not** start Relevance / Prioritization engines. Layer 2 Signs stays classification-complete / interpretation-deferred.

---

## Changelog

- **1.2 (2026-08-23)** — Calc → IL wire done 1.3.111. These packs stand. Next named = attach IL-4 packs to product surfaces.
- **1.1 (2026-08-23)** — Library scale done 1.3.110. These packs stand. Next named = wire calc → IL. **Done 1.3.111.**
- **1.0 (2026-08-23)** — 1.3.109. IL-4 Expression. Voice packs for already ranked themes. Catalog unchanged. Next named = library scale. **Done 1.3.110.**
