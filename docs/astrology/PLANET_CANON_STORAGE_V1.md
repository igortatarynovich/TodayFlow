# Planet Canon Storage V1

**Date:** 2026-08-21  
**Status:** LOCKED (schema/model). **Not** object fill. **Not** `active`. **Not** Signs. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.34. Meaning: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Schema: [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json).

This pass answers **where the six slots live in JSON**. It does not copy packs onto `objects_v1.json`. It does not shrink the grammar into `function` / `themes` / `positive_expression` / `shadow` / four-key `domains` / `tempo`.

---

## Architecture impact

- **SoT before:** Planet Canon V1 locked in a doc (1.3.79). Storage was still IL-0 keys. Risk: next fill would stuff verbs into elemental `function` or routing lemmas into natal four-key `domains`.
- **SoT after:** product meaning for a planet is an optional nested object `canon` with the **same six names** as the grammar. Legacy keys stay as IL-0 / classical draft storage. `tempo` stays out of Canon. Catalog unchanged (no `canon` on live drafts yet). Example fixture may illustrate the nest.
- **Public contract changed?** yes — optional `canon` on `knowledge_object`. Runtime still ignores `draft`.
- **Migration required?** no — nothing `active`; existing objects remain valid without `canon`.
- **Canon updated?** yes — this file · IL §6.34 · schema `$defs.canon_pack`
- **Backward compatible?** yes for current catalog. A client that only reads `function` will not see Canon until a named fill + engine read.

---

## 0. Mapping (locked)

| Grammar slot | JSON | Shape |
|--------------|------|--------|
| `core_function` | `canon.core_function` | lemma list |
| `drive` | `canon.drive` | lemma list |
| `needs` | `canon.needs` | lemma list |
| `constructive` | `canon.constructive` | lemma list |
| `distorted` | `canon.distorted` | lemma list |
| `domains` | `canon.domains` | lemma list |

If `canon` is present, **all six** keys are required. Partial packs are invalid.

Atom origin (`direct` / `derived`) stays in [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Do not duplicate provenance tables onto every object this pass.

---

## 1. What the old keys are now

| Legacy key | Job after 1.3.80 | Must not |
|------------|------------------|----------|
| `function` | Sun–Saturn: classical elemental quality. Outers: still optional school package (1.3.72). | Hold Canon verbs (`act`, `limit`, `transform`) |
| `themes` | IL-0 noun bag on drafts | Be the engine’s process/domain/shadow mix |
| `positive_expression` / `shadow` | IL-0 prose-ish lemmas | Substitute for `constructive` / `distorted` |
| `domains` (object) | Four natal keys: relationships / money / work / self | Hold Canon routing lemmas (`action`, `competition`) |
| `tempo` | Legacy object pace enum | Be Canon; Foundation `temporal_class` remains the pace metadata |

Two different things named “domains”:

- **Canon** `canon.domains` = semantic arenas (lemma list).
- **Legacy** `domains` = four life-area strings. Unattested on outers. Not the grammar slot.

Do not rename the grammar slot to fit the four-key object. Do not replace the four-key object in this pass (Sun–Saturn drafts still required to have it).

---

## 2. Requiredness

| Object | `canon` | Legacy meaning keys |
|--------|---------|---------------------|
| Sun–Saturn drafts | **optional** until fill | still required (1.3.72) |
| Uranus/Neptune/Pluto drafts | **optional**; may exist without `function` | still optional (1.3.72) |
| Signs / houses / aspects | omit | unchanged |
| `status=active` | required on planets before activation (later gate) | still cannot be active with omitted Sun–Saturn legacy keys |

This pass does **not** require `canon` on anything in 1.3.80. Fill = **1.3.81** (Sun–Saturn).

---

## 3. Engine read (not wired)

```text
product meaning  = object.canon
classical lens   = object.function / themes / …   (not default Today/Profile)
pace             = temporal_class (Foundation), not canon, not object.tempo
```

IL-4 still formulates. It must not be given only `function` and asked to invent Mars.

---

## 4. This pass does not do

- Write `canon` onto `objects_v1.json`
- Materialize outers
- Overwrite `function`
- Signs Mainstream map
- Books · CORE · `active`

**Next named:** Sun–Saturn fill — **done 1.3.81.** Smoke-test — **done 1.3.82.** Sign map — **done 1.3.83.** Sign grammar — **done 1.3.84.** Sign Canon fill — **done 1.3.85.** Sign Canon storage — **done 1.3.86.** Next = write packs onto sign drafts.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.80. Nested `canon` pack in schema. Legacy keys not the product map. No object fill.
