# Calc → IL Wire V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — library-layer wire from calc snapshots to IL-4 packs. **Not** Swiss in this module. **Not** Today prompts as meaning SoT. **Not** public JSON. **Not** `active`. **Not** pair catalog. **Not** freeze / IL-2 / IL-3 / IL-4 / scale reopen. **Not** a new “canonical v2.” **Not** user relevance.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) Sequence · §6.64 · §6.65 · §7. Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) step 39 · KC-C-WIRE. Scale: [LIBRARY_SCALE_V1.md](./LIBRARY_SCALE_V1.md) §4. Voice: [IL4_EXPRESSION_V1.md](./IL4_EXPRESSION_V1.md). Themes: [IL3_INTERPRETATION_ENGINE_V1.md](./IL3_INTERPRETATION_ENGINE_V1.md). Frames: [IL2_COMPOSITION_RULES_V1.md](./IL2_COMPOSITION_RULES_V1.md). Atoms: [KNOWLEDGE_CORE_V1_FREEZE.md](./KNOWLEDGE_CORE_V1_FREEZE.md). Boundary: [IL1_HANDOFF.md](./IL1_HANDOFF.md) §3 · §5. AGENTS.md Architecture impact.

This pass answers: **how a calc snapshot becomes IL-4 packs at the library layer.** It does not attach those packs to Today / Profile / Compatibility UI. Product surfaces still do not read IL-4.

Catalog **38 draft / 0 `active`**. Unchanged this pass. The wire consumes draft; it does not filter by `active`. Runtime product surfaces still ignore `draft`.

---

## Architecture impact

- **SoT before:** Library Scale V1 named the wire (1.3.110) and left it not live. Calc charts and IL engines existed side by side. A next pass could still treat Today prompts as meaning SoT, call Swiss inside the wire, collapse House 1 into ASC, or set `active`.
- **SoT after:** **Calc → IL Wire V1** is live **at the library layer**. Input = natal snapshot + optional transit snapshot (duck-typed `positions` / `houses`; no Swiss import). Output = IL-4 `ExpressionPack` after IL-2 compose and IL-3 interpret. Occupancy ≠ conjunction. House 1 ≠ ASC. House 10 ≠ MC. MC ≠ career. Two constructions stay two. Outers emit and IL-2 refuses. DSC / IC / Chiron / Lilith / nodes are not emitted. Draft catalog is consumed. Product surfaces are **not** attached. Freeze, IL-2, IL-3, IL-4, and scale stand. Not a “canonical v2.”
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.65 · inventory KC-C-WIRE + step 39 · ACM pointer · freeze §3 · handoff §3 · tracker NOW
- **Backward compatible?** yes (`draft`). Deprecated as next: Today prompts as meaning SoT; set `active`; Swiss as a meaning source; pair catalog; occupancy = conjunction; House 1 = ASC; MC = career; Relevance / Prioritization as meaning engines.

---

## 0. Inputs

| Input | Allowed | Forbidden |
|-------|---------|-----------|
| Natal / transit snapshot | duck-typed `positions[]` + `houses{}` (dict or object) | Swiss / ephemeris calls inside this module |
| Bodies | sun–pluto (outers emitted so IL-2 can refuse) | rising as a planet; Chiron / Lilith / nodes; DSC / IC |
| Houses | occupancy 1–12 from the `house` field; natal cusps for transits | house 1 as ASC; house 10 as MC |
| Angles | planet longitude within **8°** of ASC (`rising`) or MC (`house_10.longitude`) | occupancy of house 1 / 10 as angle proof |
| Aspects | five majors, foundation orbs; all mapped-planet pairs | curated callout lists; minors |
| Catalog | `load_objects()` including **draft** | `active` filter; lemma rewrite |

A snapshot is geometry. It is not a cookbook object and not a Today prompt.

---

## 1. Pipeline (library layer)

```text
calc snapshot {positions, houses}
  → SkyFact {construction, astro.* ids}
  → IL-2 compose | refuse missing atom
  → IL-3 interpret (transit band before natal; input order)
  → IL-4 express(surface ∈ {today, profile, compatibility})
```

Transit SkyFacts are emitted **before** natal so IL-3 band order is stable. IL-3 still re-sorts by band.

Surfaces differ in tone / length / focus. Lemmas stay verbatim. Rank unchanged. LLM does not choose Saturn □ Venus.

**Today** still voices the primary theme only. **Profile** / **compatibility** keep the full ranked list. Product UI does not read these packs in this pass.

---

## 2. Constructions emitted

| Construction | When |
|--------------|------|
| `planet_in_sign` | mapped planet with a sign (not `rising`) |
| `planet_in_house` | mapped planet with house 1–12 |
| `planet_at_angle` | planet longitude within 8° of ASC or MC **longitude** |
| `aspect_pair` | five majors among mapped planets, including outers |
| `transit_to_natal` | transiting planet to natal planet, five majors |
| `transit_through_house` | transiting longitude placed in **natal** cusps |

House 1 occupancy without the 8° ASC test is **only** `planet_in_house`. House 10 occupancy without the 8° MC test is **only** `planet_in_house`. Both may fire together when geometry actually meets both tests. They stay two facts.

---

## 3. Conflict (still hold on the wire)

Occupancy ≠ conjunction. House 1 ≠ ASC. House 10 ≠ MC. MC ≠ career. `interaction` ≠ `relation`. Two constructions stay two frames / themes / lines. Five jobs stay partitioned.

If the model does not hold a calc emit — fix ontology (named Architecture impact). Do not proliferate objects. Do not touch Today prose.

---

## 4. This pass does not do

- Lemma rewrite · pack enrich · schema · `objects_v1.json`
- Set `active` · attach product surfaces · Today prompt rewrite as meaning SoT
- Swiss / ephemeris inside the wire · public JSON change
- Books · CORE scoring · Co–Star ingest
- Pair catalog · Layer 5 essays · ASC cookbooks · outer objects
- Occupancy = conjunction · House 1 = ASC · MC = career · `interaction` as relation
- User relevance · Character Engine · Prioritization / Continuity / Trust as meaning engines
- IL-2 rules rewrite · IL-3 rank rewrite · IL-4 meaning rewrite · library-scale reopen
- Merge to `main` · deploy
- Reopen FREEZE / IL-2 / IL-3 / IL-4 / SCALE / Angles / Aspects / Houses / Signs
- A parallel “canonical v2”

**Next named:** **attach IL-4 packs to product surfaces** (Today / Profile / Compatibility). Not `active`. Not Today prompts as meaning SoT. Not Relevance. Today meaning polish stays **PAUSED** until those surfaces **read** IL-4 packs. **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do **not** start CORE scoring. Do **not** start ASC cookbooks. Do **not** start Relevance / Prioritization engines. Layer 2 Signs stays classification-complete / interpretation-deferred.

---

## Changelog

- **1.0 (2026-08-23)** — 1.3.111. Calc → IL wire at the library layer. Product surfaces not attached. Catalog unchanged.
