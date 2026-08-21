# Sign Canon Materialization V1

**Date:** 2026-08-21  
**Status:** LOCKED (catalog copy). **Not** synthesis. **Not** schema. **Not** lemma rewrite. **Not** later-interpretive fill. **Not** `active`. **Not** House Canon. **Not** smoke-test. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.41. Packs: [SIGN_CANON_V1.md](./SIGN_CANON_V1.md). Storage: [SIGN_CANON_STORAGE_V1.md](./SIGN_CANON_STORAGE_V1.md). Planet analog: [PLANET_CANON_SUN_SATURN_FILL_V1.md](./PLANET_CANON_SUN_SATURN_FILL_V1.md).

This pass copies the twelve locked 1.3.85 packs onto existing `astro.sign.*` drafts as `object.canon.{manner, excess}`. Lemma strings are identical to the locked text blocks. Origin tables stay in SIGN_CANON_V1.md.

Smoke-test is **not** this pass. That gate is **1.3.88**.

---

## Architecture impact

- **SoT before:** Sign Canon lived in a doc + optional schema nest. Twelve sign drafts were classification-only (`mode` · `element` · `orientation`).
- **SoT after:** twelve sign drafts carry product meaning in `canon` and Lilly classification in legacy keys. Later-interpretive `excess` stays omitted. Status stays `draft`. Engine must later read `canon.manner`, not `mode`.
- **Public contract changed?** yes — twelve draft signs now include `canon` (still ignored while `draft`)
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — this file · IL §6.41 · catalog `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`). Clients that only read classification still see the Lilly grid.

---

## 0. Copy rule (locked)

| Allowed | Forbidden |
|---------|-----------|
| Write the two lists from 1.3.85 onto `canon` | New lemmas, new families, reordering as “cleanup” |
| Leave `mode` · `element` · `orientation` · provenance rows | Derive manner from classification |
| Keep later-interpretive keys omitted | Fill top-level `excess` / `motivation` / `expression` |
| Keep status `draft` | `active` · CORE · books · Co–Star · House work · engine |

If a later smoke-test needs a different lemma, that is a **grammar/pack** change (named pass), not a silent object edit.

---

## 1. What is now on the object

```text
object.canon                     = product manner (1.3.85 packs)
object.mode / element / orientation = Lilly classification (not an operator)
object.excess (top-level)        = later-interpretive research field (still omitted)
```

Twelve `type=sign` drafts. Houses / aspects still omit `canon`. Sun–Saturn planet packs unchanged.

---

## 2. This pass does not do

- Schema change
- Lemma / family revision
- 1.3.88 Planet × Sign smoke-test
- House Mainstream / House Canon
- IL-2 engine
- `active`

**Next named:** **1.3.88 Planet × Sign Composition Smoke V1** (separate gate). After PASS: STOP Signs; House Canon. Do not improve packs after a passing smoke-test without a named Composition Engine failure.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.87. Twelve sign `canon` packs copied from 1.3.85. Later-interpretive `excess` omitted. Next = 1.3.88 smoke-test, not House Canon.
