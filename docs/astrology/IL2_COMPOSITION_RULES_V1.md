# IL-2 Composition Rules V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — composition **rules** (weights, conflict, merge). **Not** a pair catalog. **Not** Layer 5 essays. **Not** pack rewrite. **Not** `active`. **Not** freeze reopen. **Not** a new “canonical v2.” **Not** IL-3 ranking. **Not** LLM copy.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) Sequence · Layer 5 · §6.60 · §6.61 · §7 IL-2 row. Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) § Freeze (primitives) · KC-C-RULES · step 35. Atoms: [KNOWLEDGE_CORE_V1_FREEZE.md](./KNOWLEDGE_CORE_V1_FREEZE.md). Joint diagnostic: [ATOMIC_CANON_COMPOSITION_SMOKE_V1.md](./ATOMIC_CANON_COMPOSITION_SMOKE_V1.md). Machine freeze: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md) (atoms vs derived; this file is the **lemma** Rules doc ACM §3 named). Handoff: [IL1_HANDOFF.md](./IL1_HANDOFF.md) §3. AGENTS.md Architecture impact.

This pass answers: **how to stack the five frozen atoms without LLM-invented meanings and without cookbook objects.** It starts from stored primitives, not gold-set 41 and not CORE.

```text
planet.canon.core_function     what
sign.canon.manner              how
house.canon.arena              where
aspect.canon.relation          relation
angle.canon.orientation        orientation locus
```

Catalog **38 draft / 0 `active`**. Unchanged this pass. Runtime still ignores `draft`.

---

## Architecture impact

- **SoT before:** Knowledge Core V1 **FROZEN** on five stored families (1.3.106). ACM §3 was a machine-vector sketch (`w_p=0.55 / w_s=0.45`) with “exact weights → Rules doc.” Inventory KC-C-RULES was `DEFERRED_V1`. Layer 5 gold list = **candidates** (suspicion, not proof). Next named was IL-2, so the product could still treat pairs as a catalog, collapse House 1 into ASC, read `interaction` as `relation`, or wait for CORE / gold-set 41.
- **SoT after:** IL-2 composition **rules** are the compose SoT for lemma frames. Five jobs stay five jobs. Weights are **role weights** (subject vs modifier / two functions vs operator) — not a blend of lemma strings, not a new Canon slot. Conflict rules forbid occupancy = conjunction, House 1 = ASC, MC = career, `interaction` as relation. Merge **copies** stored lemmas into a typed frame. Layer 5 gold rows that the five families can produce are **demoted to composed** (0 objects). Rows that need Uranus/Neptune/Pluto stay **candidates** (missing atom; not invented; not catalogued). ACM machine-vector sketch is **not** replaced; it remains the P0.8 numeric layer. Next named = **IL-3** engine (sky → ranked themes). Not a “canonical v2.”
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.61 · inventory KC-C-RULES + step 35 · ACM §3 pointer · freeze §3 next · handoff §3 (IL-3 rank ≠ user relevance) · tracker NOW
- **Backward compatible?** yes (`draft`). Deprecated as next: pair catalog; Layer 5 essays; ASC cookbooks; outer objects; CORE scoring; freeze reopen; occupancy = conjunction; House 1 = ASC; MC = career; `interaction` as relation; lemma-string averaging.

---

## 0. Inputs (frozen)

Only stored `canon` slots on draft objects. Not `function` prose. Not Lilly `domain`. Not `interaction`. Not sign `mode` / `element` / `orientation`. Not CORE lemmas. Not gold-set 41 as a gate.

| Family | Count | Slot | Job |
|--------|-------|------|-----|
| Planet | 7 (Sun–Saturn) | `canon.core_function` | what |
| Sign | 12 | `canon.manner` | how |
| House | 12 | `canon.arena` | where |
| Aspect | 5 | `canon.relation` | relation |
| Angle | 2 (ASC · MC) | `canon.orientation` | orientation locus |

**Missing atom (refuse, do not invent):** Uranus / Neptune / Pluto (claims, no objects). DSC / IC (out of V1).

---

## 1. Construction types

Six typed frames. Not 10 000 JSON horoscopes. Not Layer 5 essays.

| Type | Jobs filled | Temporal |
|------|-------------|----------|
| `planet_in_sign` | what + how | natal |
| `planet_in_house` | what + where | natal |
| `planet_at_angle` | what + orientation | natal |
| `aspect_pair` | what_a + what_b + relation | natal |
| `transit_to_natal` | what_a + what_b + relation | transit |
| `transit_through_house` | what + where | transit |

A planet that is in a sign **and** in a house **and** on an angle yields **three frames**, not one cookbook. Chart-level ranking is **IL-3**.

`transit_to_natal` uses the same merge as `aspect_pair`. Temporal class does not invent meaning.

---

## 2. Weights (role, not soup)

ACM §3.1 numeric blend applies to **machine vectors**, not Canon lemmas. IL-2 does **not** average `act` + `initiating` into a new lemma.

Role weights declare which job is the **subject** of a later sentence (IL-4) and which is the **modifier**. Lemmas stay partitioned.

| Construction | Role weights |
|--------------|----------------|
| `planet_in_sign` | what **0.55** (head) · how **0.45** (manner modifier) |
| `planet_in_house` | what **0.55** · where **0.45** |
| `planet_at_angle` | what **0.55** · orientation **0.45** |
| `aspect_pair` / `transit_to_natal` | what_a **0.50** · what_b **0.50**; relation is the **operator**, not a third function |
| `transit_through_house` | what **0.55** · where **0.45** |

On an aspect, neither planet is the other’s modifier. Square `relation` attaches **between** the two functions. `interaction` is not a weight source.

---

## 3. Conflict (do not collapse)

| ID | Rule |
|----|------|
| C1 | **Occupancy ≠ conjunction.** `planet_in_house` is not `aspect_pair(conjunction)`. A planet can occupy House 1 without conjuncting ASC. |
| C2 | **House 1 ≠ ASC.** House 1 `arena` is not ASC `orientation`. |
| C3 | **House 10 ≠ MC.** House 10 `arena` is not MC `orientation`. |
| C4 | **MC ≠ career.** Career is House 10 `arena`. MC `orientation` does not carry `career`. |
| C5 | **`interaction` ≠ `relation`.** Trine ≠ Sextile when both `interaction=flow`. Operator is stored `canon.relation`. |
| C6 | **Classification ≠ manner.** Sign `mode` / `element` / `orientation` are not `canon.manner`. |
| C7 | **Five jobs stay five jobs.** Do not union lemmas across jobs into one bag as “the meaning.” |
| C8 | **Missing atom → refuse.** Do not fill Uranus/Neptune/Pluto/`DSC`/`IC` from gold-set, CORE, or LLM. |
| C9 | **Two constructions stay two frames.** Mars IN 1st and Mars AT ASC are not merged. |
| C10 | **No cookbook.** No pair essay. No “Mars in Aries = look aggressive.” No “planet in 1st = on ASC.” No “MC = career.” |

---

## 4. Merge (copy, don’t rewrite)

| ID | Rule |
|----|------|
| M1 | Copy stored lemmas **verbatim**. Never rewrite, translate, or average. |
| M2 | Partition by job: what / how / where / relation / orientation. |
| M3 | Fill **only** the slots the construction type requires. Do not copy a sibling construction’s job. |
| M4 | Conjunction is `aspect_pair` with stored conjunction `relation`, not occupancy of a house. |
| M5 | Merge of several frames into one theme list is **IL-3**. IL-2 emits a bag of typed frames. |
| M6 | Layer 5 gold row that these rules can emit → **composed** (no object). Row that needs a missing atom → remains **candidate**. |

Frame shape (engine / tests; not a catalog record):

```text
type, jobs{what, how, where, relation, orientation},
weights, source=stored_canon, status=composed|refused,
essay=FORBIDDEN
```

---

## 5. Layer 5 demotion

IL-1 gold list was **suspicion**, not proof of `non_compositional`. IL-2 confirms compose-default where atoms exist.

**Composed (0 objects):** all `planet_in_sign` gold (10) · all `planet_in_house` gold (11) · natal aspects among Sun–Saturn · transits among Sun–Saturn · Saturn/Jupiter through-house rows.

**Remain candidates (missing atom, still 0 objects):** natal or transit rows that name Uranus / Neptune / Pluto. Do not invent outer `core_function`. Do not open ASC cookbooks to “complete” them.

No Layer 5 JSON. ACM freeze on composite **machine** files stands.

---

## 6. This pass does not do

- Lemma rewrite · pack enrich · `function` rewrite · schema change · `objects_v1.json` edits
- Set `active` · runtime wiring · LLM copy · Today prompts
- Books · CORE scoring · Co–Star ingest
- Pair catalog · Layer 5 essays · ASC cookbooks · outer objects
- Occupancy = conjunction · House 1 = ASC · MC = career · `interaction` as relation
- IL-3 ranking / clustering · IL-4 expression
- Merge to `main` · deploy
- Reopen FREEZE / Angles / Aspects / Houses / Signs
- A parallel “canonical v2”

**Next named:** library scale — **done 1.3.110.** Wire calc → IL — **done 1.3.111.** Next = attach IL-4 packs to product surfaces. **IL-3 rank ≠ user relevance rank.** **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do **not** start CORE scoring. Do **not** start ASC cookbooks. Do **not** start Relevance / Prioritization engines. Layer 2 Signs stays classification-complete / interpretation-deferred.

---

## Changelog

- **1.5 (2026-08-23)** — Calc → IL wire done 1.3.111. These rules stand. Next named = attach IL-4 packs to product surfaces.
- **1.4 (2026-08-23)** — Library scale done 1.3.110. These rules stand. Next named = wire calc → IL. **Done 1.3.111.**
- **1.3 (2026-08-23)** — IL-4 Expression done 1.3.109. These rules stand. Next named = library scale. **Done 1.3.110.**
- **1.2 (2026-08-23)** — IL-3 engine done 1.3.108. These rules stand. Next named = IL-4. **Done 1.3.109.**
- **1.1 (2026-08-23)** — IL-3 next named: sky-internal theme rank ≠ user relevance. Pointer: [IL1_HANDOFF.md](./IL1_HANDOFF.md) §3. No rules change. **Done 1.3.108.**
- **1.0 (2026-08-23)** — 1.3.107. IL-2 composition rules. Role weights · conflict · merge. Layer 5 gold demoted to composed where atoms exist. Catalog unchanged. Next named = IL-3. **Done 1.3.108.**
