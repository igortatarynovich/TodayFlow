# House Canon Storage + Materialization V1

**Date:** 2026-08-22  
**Status:** LOCKED (schema + catalog copy). **Not** synthesis. **Not** lemma rewrite. **Not** `active`. **Not** smoke-test. **Not** CORE. **Not** a book. **Not** ASC/MC.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.46. Packs: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md). Grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). Sign analog: [SIGN_CANON_STORAGE_V1.md](./SIGN_CANON_STORAGE_V1.md) · [SIGN_CANON_MATERIALIZATION_V1.md](./SIGN_CANON_MATERIALIZATION_V1.md). Schema: [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json).

Signs split schema and catalog copy. Houses do not: one atomic pass writes the nest **and** copies locked 1.3.91 packs onto the twelve `astro.house.*` drafts. Lemma strings are identical to the locked text blocks. Origin tables stay in HOUSE_CANON_V1.md.

Smoke-test is **not** this pass. That gate is **1.3.93**.

---

## Architecture impact

- **SoT before:** House Canon lived in a doc. Twelve house drafts were Lilly `domain` / `people` / `activities` only. Schema forbade `canon` on `type=house`.
- **SoT after:** `type=house` may carry optional `canon` as `$defs.house_canon_pack` (`arena` only). Twelve drafts carry that pack. Lilly classical fields unchanged. Status `draft`. Aspects still omit `canon`. ASC/MC not materialized. Runtime still ignores `draft`.
- **Public contract changed?** yes — optional house `canon` nest; twelve draft houses now include `canon`
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — this file · IL §6.46 · schema `$defs.house_canon_pack` · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`). Clients that only read Lilly `domain` still see CA I.7.

---

## 0. Mapping (locked)

| Grammar slot | JSON | Shape |
|--------------|------|--------|
| `arena` | `canon.arena` | lemma list |

If `canon` is present on a **house**, **`arena` is required**. Partial packs are invalid. No second slot. No `domains` key on the house pack.

`type=celestial_object` still requires the six-slot planet pack. `type=sign` still requires `manner` · `excess`. Aspects / combos must **omit** `canon`.

Atom origin (`direct` / `derived`) stays in [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md). Do not duplicate provenance tables onto every object this pass.

---

## 1. What the old keys are now

| Legacy key | Job after 1.3.92 | Must not |
|------------|------------------|----------|
| `domain` | Lilly CA I.7 classical prose (school_specific) | Be read as House Canon arena |
| `people` / `activities` / `resources` / `risks` / `internal_meaning` / `external_manifestations` | Classical research storage | Substitute for `arena` |
| `canon.arena` | Product destination lemmas (1.3.91 packs) | Copy planet.domains; copy Cancer/Moon; copy ASC/MC |

Two different “where” fields:

- **Canon** `canon.arena` = chart sphere for composition.
- **Legacy** `domain` = Lilly topical sentence. Unchanged. Not the grammar slot.

Do not overwrite Lilly `domain` with arena lemmas.

---

## 2. Copy rule (locked)

| Allowed | Forbidden |
|---------|-----------|
| Write the `arena` list from 1.3.91 onto `canon` | New lemmas, new families, reordering as “cleanup” |
| Leave Lilly `domain` · `people` · `activities` · provenance rows | Derive arena from natural sign / angularity / Lilly |
| Keep status `draft` | `active` · CORE · books · Co–Star · Aspect work · engine · ASC/MC objects |

If a later smoke-test needs a different lemma, that is a **grammar/pack** change (named pass), not a silent object edit.

---

## 3. What is now on the object

```text
object.canon.arena   = product destination (1.3.91 packs)
object.domain        = Lilly CA I.7 (not an operator)
```

Twelve `type=house` drafts. Aspects still omit `canon`. Sign and planet packs unchanged. No ASC/MC house objects.

Engine read (not wired):

```text
planet.canon.core_function  ×  house.canon.arena
  →  function routed into this sphere
```

IL-4 still formulates. It must not be given only Lilly `domain` and asked to invent the 4th.

---

## 4. This pass does not do

- Lemma / family revision
- 1.3.93 Planet × House smoke-test
- Aspect / ASC/MC maps or objects
- IL-2 engine · runtime wiring
- `active`
- Overwrite Lilly `domain`

**Next named:** **1.3.93 Planet × House Composition Smoke V1.** Discrimination: Moon × 4th ≠ Moon × 10th. Composability: same stored 4th pack on Moon / Mars / Venus. Historical 1.3.82 Moon × 4th PARTIAL must become PASS from **stored** `house.canon.arena`. Then **STOP Houses.** Do not enrich packs.

---

## Changelog

- **1.0 (2026-08-22)** — 1.3.92. `$defs.house_canon_pack` (`arena`). Twelve house drafts carry locked 1.3.91 packs. Lilly fields unchanged. Next = 1.3.93 Planet × House smoke-test.
