# Planet Canon Sun–Saturn Fill V1

**Date:** 2026-08-21  
**Status:** LOCKED (catalog copy). **Not** synthesis. **Not** schema. **Not** `function` rewrite. **Not** outers. **Not** Signs. **Not** CORE. **Not** `active`.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.35. Packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Storage: [PLANET_CANON_STORAGE_V1.md](./PLANET_CANON_STORAGE_V1.md).

This pass copies the seven locked 1.3.79 packs onto `astro.object.sun` … `astro.object.saturn` as `object.canon`. Lemma strings are identical to the locked text blocks. Origin tables stay in PLANET_CANON_V1.md.

---

## Architecture impact

- **SoT before:** product meaning existed only in a doc + optional schema nest. Runtime still had to read classical `function` / `themes`.
- **SoT after:** seven planet drafts carry product meaning in `canon` and research/classical meaning in legacy keys. The two are structurally separate. Engine must read `canon`. Outers still withheld. Status stays `draft`.
- **Public contract changed?** yes — seven draft objects now include `canon` (still ignored while `draft`)
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — this file · IL §6.35 · catalog `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`). Clients that only read `function` still see elemental quality.

---

## 0. Copy rule (locked)

| Allowed | Forbidden |
|---------|-----------|
| Write the six lists from 1.3.79 onto `canon` | New lemmas, new derived, reordering as “cleanup” |
| Leave `function` · `themes` · `positive_expression` · `shadow` · four-key `domains` · `tempo` · provenance rows | Overwrite any of those |
| Keep status `draft` | `active` · CORE · books · Co–Star |
| Sun–Saturn only | Uranus / Neptune / Pluto objects |

If a later smoke-test needs a different lemma, that is a **grammar/pack** change (named pass), not a silent object edit.

---

## 1. What is now on the object

```text
object.canon          = product meaning (1.3.79 packs)
object.function/…     = classical / IL-0 research storage
object.temporal_class = Foundation pace
```

Seven celestial_object drafts. Zero outer objects. Signs / houses / aspects have no `canon`.

---

## 2. This pass does not do

- Schema change
- Synthesis
- Outer materialize
- Signs Mainstream map
- IL-2 engine

**Next named:** **1.3.82 composition smoke-test** — **done.** Sign map — **done 1.3.83.** Sign grammar — **done 1.3.84.** Next = Sign Canon fill.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.81. Sun–Saturn `canon` copied from 1.3.79. Next = 1.3.82 smoke-test, not Signs.
