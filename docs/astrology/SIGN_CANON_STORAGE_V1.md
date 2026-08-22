# Sign Canon Storage V1

**Date:** 2026-08-21  
**Status:** LOCKED (schema/model). **Not** object fill. **Not** `active`. **Not** House Canon. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.40. Meaning: [SIGN_CANON_V1.md](./SIGN_CANON_V1.md). Grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). Planet analog: [PLANET_CANON_STORAGE_V1.md](./PLANET_CANON_STORAGE_V1.md). Schema: [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json).

This pass answers **where the two Sign Canon slots live in JSON**. It does not copy packs onto `objects_v1.json`. It does not write manner into later-interpretive `excess` / `motivation` / `expression`.

---

## Architecture impact

- **SoT before:** Sign Canon V1 locked in a doc (1.3.85). Storage was still the planet six-slot `canon_pack`. Risk: next fill would stuff `manner` into planet keys, or write Sign Canon `excess` into Layer 2 later-interpretive `excess`.
- **SoT after:** product meaning for a sign is the same optional nested object `canon`, type-discriminated: signs use `$defs.sign_canon_pack` (`manner` · `excess`). Planets keep `$defs.canon_pack`. Legacy later-interpretive keys stay as Layer 2 research storage. Catalog unchanged (no `canon` on live sign drafts yet). Example fixture may illustrate the nest.
- **Public contract changed?** yes — optional `canon` on `type=sign` now has a legal shape. Runtime still ignores `draft`.
- **Migration required?** no — nothing `active`; existing sign objects remain valid without `canon`. Planet `canon` unchanged.
- **Canon updated?** yes — this file · IL §6.40 · schema `$defs.sign_canon_pack`
- **Backward compatible?** yes for current catalog. A client that only reads `mode` / `element` / `orientation` will not see Canon until a named fill + engine read.

---

## 0. Mapping (locked)

| Grammar slot | JSON | Shape |
|--------------|------|--------|
| `manner` | `canon.manner` | lemma list |
| `excess` | `canon.excess` | lemma list |

If `canon` is present on a **sign**, **both** keys are required. Partial packs are invalid.

`type=celestial_object` still requires the six-slot planet pack. Houses / aspects / combos must **omit** `canon` until a named House/Aspect storage pass.

Atom origin (`direct` / `derived`) stays in [SIGN_CANON_V1.md](./SIGN_CANON_V1.md). Do not duplicate provenance tables onto every object this pass.

---

## 1. What the old keys are now

| Legacy key | Job after 1.3.86 | Must not |
|------------|------------------|----------|
| `mode` / `element` / `orientation` | Stored classification fact (Lilly grid on drafts) | Generate manner (`earth` → practical, `cardinal` → initiating) |
| `excess` (object top-level) | Later-interpretive Layer 2 slot (optional; currently omitted) | Hold Sign Canon excess lemmas (`withholding`, `hardening`) |
| `motivation` / `expression` / `strengths` / `deficiency` / `behavioral_tendencies` | Later-interpretive; still optional and unfilled | Substitute for `manner` |
| `function` | Planet classical elemental quality | Exist on signs |

Two different things named “excess”:

- **Canon** `canon.excess` = the sign’s manner overdone (operator lemmas).
- **Legacy** `excess` = later-interpretive personality dump. Unattested on current drafts. Not the grammar slot.

Do not rename the grammar slot to avoid the collision. Do not fill the later-interpretive key in this pass.

---

## 2. Requiredness

| Object | `canon` | Legacy meaning keys |
|--------|---------|---------------------|
| `type=sign` drafts | **optional** until fill | classification still required; later-interpretive still optional/omitted |
| Sun–Saturn drafts | six-slot planet pack (already filled 1.3.81) | unchanged |
| Uranus/Neptune/Pluto | still withheld | unchanged (1.3.72) |
| Houses / aspects | omit | unchanged |
| `status=active` | required on signs before activation (later gate) | still cannot be active with omitted classification |

This pass does **not** require `canon` on any sign in 1.3.86. Fill = next named (write packs onto sign drafts).

---

## 3. Engine read (not wired)

```text
planet product meaning  = object.canon          (six slots)
sign product meaning    = object.canon          (manner · excess)
classification          = mode / element / orientation   (not an operator)
later-interpretive      = motivation / top-level excess / …   (not default Today/Profile)
```

```text
planet.canon.core_function  ×  sign.canon.manner
  →  function done this way
  ×  sign.canon.excess     when the construction is on a distorted branch
```

IL-4 still formulates. It must not be given only `mode=cardinal` and asked to invent Capricorn.

---

## 4. This pass does not do

- Write `canon` onto `objects_v1.json` sign drafts
- Repeat 1.3.82 smoke-test (Venus × Capricorn stays PARTIAL until fill)
- House Mainstream map / House Canon
- Reopen 1.3.83 research · books · CORE · Co–Star ingest
- Fill later-interpretive `excess`
- Copy planet six slots onto signs

**Next named:** write `canon` onto the twelve sign drafts from [SIGN_CANON_V1.md](./SIGN_CANON_V1.md) — **done 1.3.87.** Planet × Sign smoke-test — **done 1.3.88.** Next = Houses Mainstream map → House Canon grammar. STOP Signs.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.86. Nested `sign_canon_pack` on `object.canon` for `type=sign`. Legacy later-interpretive `excess` not the product map. No object fill.
