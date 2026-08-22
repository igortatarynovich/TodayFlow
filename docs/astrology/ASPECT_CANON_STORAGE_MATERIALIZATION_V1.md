# Aspect Canon Storage + Materialization V1

**Date:** 2026-08-22  
**Status:** LOCKED (schema + catalog copy). **Not** synthesis. **Not** lemma rewrite. **Not** `active`. **Not** smoke-test. **Not** CORE. **Not** a book. **Not** ASC/MC.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.51. Packs: [ASPECT_CANON_V1.md](./ASPECT_CANON_V1.md). Grammar: [ASPECT_CANON_GRAMMAR_V1.md](./ASPECT_CANON_GRAMMAR_V1.md). House analog: [HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md](./HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md). Schema: [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json).

Signs split schema and catalog copy. Houses did not. Aspects follow houses: one atomic pass writes the nest **and** copies locked 1.3.96 packs onto the five `astro.aspect.*` drafts. Lemma strings are identical to the locked text blocks. Origin tables stay in ASPECT_CANON_V1.md.

Smoke-test is **not** this pass. That gate is **1.3.98**.

---

## Architecture impact

- **SoT before:** Aspect Canon lived in a doc. Five aspect drafts were `angle` / `interaction` / `requires_action` only. Schema forbade `canon` on `type=aspect`.
- **SoT after:** `type=aspect` may carry optional `canon` as `$defs.aspect_canon_pack` (`relation` only). Five drafts carry that pack. Stored `interaction` unchanged and is **not** an alias of Canon. Status `draft`. Combo types still omit `canon`. ASC/MC not materialized. Runtime still ignores `draft`.
- **Public contract changed?** yes — optional aspect `canon` nest; five draft aspects now include `canon`
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — this file · IL §6.51 · schema `$defs.aspect_canon_pack` · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`). Clients that only read `interaction` still see the classical enum.

---

## 0. Mapping (locked)

| Grammar slot | JSON | Shape |
|--------------|------|--------|
| `relation` | `canon.relation` | lemma list |

If `canon` is present on an **aspect**, **`relation` is required**. Partial packs are invalid. No second slot. No `requires_action`, valence, hard/soft, orb, or pair fields on the pack.

`type=celestial_object` still requires the six-slot planet pack. `type=sign` still requires `manner` · `excess`. `type=house` still requires `arena`. Combos must **omit** `canon`.

Atom origin (`direct`) stays in [ASPECT_CANON_V1.md](./ASPECT_CANON_V1.md). Do not duplicate provenance tables onto every object this pass.

---

## 1. What the old keys are now

| Legacy key | Job after 1.3.97 | Must not |
|------------|------------------|----------|
| `interaction` | Classical grain (schema enum: merging / friction / flow / polarization) | Be read as Aspect Canon `relation`; be rewritten to match lemmas |
| `requires_action` | Activation-gate boolean (draft `false` ≠ “no action needed”) | Become a Canon slot |
| `angle` | Geometry | Become topology |
| `canon.relation` | Product topology lemmas (1.3.96 packs) | Copy `interaction`; stamp valence; carry pair essays |

Two different “how they are linked” fields:

- **Canon** `canon.relation` = topology of the link for composition.
- **Legacy** `interaction` = coarse classical enum. Unchanged. Not the grammar slot. Trine and sextile both stay `flow`.

Do not overwrite `interaction` with relation lemmas.

---

## 2. Copy rule (locked)

| Allowed | Forbidden |
|---------|-----------|
| Write the `relation` list from 1.3.96 onto `canon` | New lemmas, new families, reordering as “cleanup” |
| Leave `interaction` · `angle` · `requires_action` · provenance rows | Derive relation from `interaction`, orbs, hard/soft, or a planet pair |
| Keep status `draft` | `active` · CORE · books · Co–Star · ASC/MC · engine · Sign/House pack edits |

If a later smoke-test needs a different lemma, that is a **grammar/pack** change (named pass), not a silent object edit.

Copied packs (verbatim):

| Object | `canon.relation` |
|--------|------------------|
| `astro.aspect.conjunction` | `blend` · `fuse` · `immediate-connection` |
| `astro.aspect.opposition` | `polarity` · `facing` · `the-other` |
| `astro.aspect.square` | `friction` · `blockage` · `cross-purposes` |
| `astro.aspect.trine` | `easy-flow` · `support` · `natural-ease` |
| `astro.aspect.sextile` | `ease-with-participation` · `directed-potential` · `cooperation` |

---

## 3. What is now on the object

```text
object.canon.relation   = product topology (1.3.96 packs)
object.interaction      = classical enum (not an operator)
object.requires_action  = activation gate (not a slot)
object.angle            = geometry
```

Five `type=aspect` drafts. Combos still omit `canon`. Sign, house, and planet packs unchanged. No ASC/MC objects.

Engine read (not wired):

```text
planet.canon.core_function  ×  aspect.canon.relation  ×  planet.canon.core_function
  →  two functions linked under this topology
```

IL-4 still formulates. It must not be given only `interaction=flow` and asked to invent trine vs sextile.

---

## 4. This pass does not do

- Lemma / family revision
- 1.3.98 stored Planet × Aspect smoke-test — **done**
- Overwrite `interaction` or `requires_action`
- Pair essays · minors · orbs · applying/separating
- ASC/MC maps or objects
- IL-2 engine · runtime wiring
- `active`
- Sign / House pack edits

**Next named:** 1.3.98 stored Planet × Aspect composition smoke — **done.** Four gates PASS. **STOP Aspects.** Angle model — **done 1.3.99.** Mainstream Angle map — **done 1.3.100.** Angle Canon grammar — **done 1.3.101.** Angle Canon fill — **done 1.3.102.** Next = Angle Canon storage/materialization. Sequence: storage → stored Planet×Angle smoke → STOP Angles → final atomic smoke → Knowledge Core V1 FREEZE. After freeze: IL-2. **STOP Houses.** **STOP Signs.** Do not enrich packs.

---

## Changelog

- **1.2 (2026-08-22)** — 1.3.99 Angle Canon model locked. Next = Mainstream Angle Semantic Map.
- **1.1 (2026-08-22)** — 1.3.98 stored Planet × Aspect smoke PASS. STOP Aspects. Angle model — **done 1.3.99.**
- **1.0 (2026-08-22)** — 1.3.97. `$defs.aspect_canon_pack` (`relation`). Five aspect drafts carry locked 1.3.96 packs. `interaction` unchanged. Next = 1.3.98 stored Planet × Aspect smoke. **Done 1.3.98.**
