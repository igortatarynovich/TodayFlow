# Angle Canon Storage + Materialization V1

**Date:** 2026-08-22  
**Status:** LOCKED (schema + catalog copy). **Not** synthesis. **Not** lemma rewrite. **Not** `active`. **Not** smoke-test. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.57. Packs: [ANGLE_CANON_V1.md](./ANGLE_CANON_V1.md). Grammar: [ANGLE_CANON_GRAMMAR_V1.md](./ANGLE_CANON_GRAMMAR_V1.md). Aspect analog: [ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md](./ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md). Schema: [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json).

Houses and aspects: one atomic pass writes the nest **and** copies locked packs onto drafts. Angles follow that pattern. Lemma strings are identical to the locked 1.3.102 text blocks. Origin tables stay in ANGLE_CANON_V1.md.

Smoke-test is **not** this pass. That gate is stored Planet×Angle.

---

## Architecture impact

- **SoT before:** Angle Canon lived in a doc. Catalog had 36 drafts and no ASC/MC objects. Schema had no `type=angle` and no `angle_canon_pack`. Layer 1 forced `celestial_object` and planet meaning keys.
- **SoT after:** `type=angle` (Layer 1) may carry optional `canon` as `$defs.angle_canon_pack` (`orientation` only). Two drafts (`astro.object.asc` · `astro.object.mc`) carry locked 1.3.102 packs. Status `draft`. Combos still omit `canon`. House 1 / House 10 packs unchanged. Runtime still ignores `draft`.
- **Public contract changed?** yes — new `type=angle`; optional angle `canon` nest; two draft angle objects
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — this file · IL §6.57 · schema `$defs.angle_canon_pack` · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`). Clients that never read angles still see 7 planets / 12 signs / 12 houses / 5 aspects.

---

## 0. Mapping (locked)

| Grammar slot | JSON | Shape |
|--------------|------|--------|
| `orientation` | `canon.orientation` | lemma list |

If `canon` is present on an **angle**, **`orientation` is required**. Partial packs are invalid. No second slot. No `arena` / `manner` / `relation` on the angle pack.

Root `orientation` remains Lilly sign polarity (`positive` / `negative`). It is **forbidden** on `type=angle`. Angle lemmas live only at `canon.orientation`.

`type=celestial_object` still requires the six-slot planet pack (non-outers). `type=sign` still requires `manner` · `excess`. `type=house` still requires `arena`. `type=aspect` still requires `relation`. Combos must **omit** `canon`.

Atom origin (`direct`) stays in [ANGLE_CANON_V1.md](./ANGLE_CANON_V1.md). Do not duplicate fill provenance tables onto every object this pass. New drafts need one `internal_normalization` provenance row because schema `provenance` is required and these objects have no Lilly ingest.

---

## 1. What these objects are not

| Key / type | Job after 1.3.103 | Must not |
|------------|-------------------|----------|
| `type=angle` | Orientation locus (horizon / meridian) | Become a planet (`celestial_object`); become House 1 / House 10 |
| `canon.orientation` | Product chart-edge lemmas (1.3.102 packs) | Copy House 1 / House 10 `arena`; copy planet `core_function`; carry appearance / career |
| Root `orientation` | Lilly sign polarity (signs only) | Store angle lemmas |
| `object.angle` | Aspect geometry (degrees) | Exist on an angle object |
| Occupancy | House placement (elsewhere) | Equal conjunction with ASC/MC |

Geometric guard (stored for smoke, not rewritten here): a planet can occupy House 1 without conjuncting ASC. Occupancy ≠ conjunction.

---

## 2. Copy rule (locked)

| Allowed | Forbidden |
|---------|-----------|
| Write the `orientation` list from 1.3.102 onto `canon` | New lemmas, leftover include (`personal-facing` / `public-facing`), secondary collision-zone |
| Keep status `draft` | `active` · CORE · books · Co–Star · engine · Sign/House/Aspect pack edits |
| One editorial provenance row pointing at ANGLE_CANON_V1.md | Copy House 1 / House 10 Lilly provenance onto ASC/MC |

If a later smoke-test needs a different lemma, that is a **grammar/pack** change (named pass), not a silent object edit.

Copied packs (verbatim):

| Object | `canon.orientation` |
|--------|---------------------|
| `astro.object.asc` | `doorway-meeting` · `how-met` · `automatic-response` |
| `astro.object.mc` | `culmination` · `outer-mark` · `aiming` |

Collision vs House 1/10 (stored lists):

- ASC pack has no `self-presentation` · `appearance` · `first-impression` · `mask`
- MC pack has no `career` · `public-role` · `reputation` · `calling` · `profession`

`personal-facing` / `public-facing` stay include leftover. Not copied.

---

## 3. What is now on the object

```text
object.canon.orientation   = product chart-edge (1.3.102 packs)
object.type                = angle (not celestial_object, not house)
```

Two `type=angle` drafts. Catalog **38** draft / 0 `active`. Combos still omit `canon`. Sign, house, aspect, and planet packs unchanged. House 1 and House 10 `arena` unchanged.

Engine read (not wired):

```text
planet.canon.core_function  AT  angle.canon.orientation
  →  a known function hung on this chart edge
```

Not:

```text
planet IN house.canon.arena
```

IL-4 still formulates. It must not be given House 1 `arena` and asked to invent rising.

---

## 4. This pass does not do

- Lemma / family revision
- Stored Planet×Angle smoke
- DSC / IC objects
- Rising-sign portraits · MC-in-sign careers
- IL-2 engine · runtime wiring
- `active`
- Sign / House / Aspect / Planet pack edits
- Fill leftover include for symmetry

**Next named:** stored Planet×Angle composition smoke — **done 1.3.104.** Discrimination: Mars AT ASC ≠ Mars AT MC ≠ Mars IN 1st ≠ Mars IN 10th, from **stored** `canon.orientation` vs `house.canon.arena`. **STOP Angles.** Final atomic smoke — **done 1.3.105.** Knowledge Core V1 FREEZE — **done 1.3.106.** Next = IL-2. **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not enrich packs.

---

## Changelog

- **1.1 (2026-08-23)** — 1.3.104 stored Planet×Angle smoke PASS. Storage unchanged. STOP Angles. Final atomic smoke — **done 1.3.105.** Next = Knowledge Core V1 FREEZE.
- **1.0 (2026-08-22)** — 1.3.103. `$defs.angle_canon_pack` (`orientation`). Two angle drafts carry locked 1.3.102 packs. stored Planet×Angle smoke — **done 1.3.104.**
