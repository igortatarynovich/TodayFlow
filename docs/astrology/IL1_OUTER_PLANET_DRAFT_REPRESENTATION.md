# Outer Planet Draft Representation V1

**Date:** 2026-08-21  
**Status:** LOCKED (schema/model). **Not** ingest. **Not** objects. **Not** CORE. **Not** `active`.  
**Rows:** KC-P-URA · KC-P-NEP · KC-P-PLU.  
**Parent:** [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) (owner-approved freeze). Definition: [IL1_LAYER1_OUTERS_DEFINITION.md](./IL1_LAYER1_OUTERS_DEFINITION.md) (1.3.70). Analog: IL 1.3.67 (signs) then 1.3.68 (materialize later).

This pass answers **representation**, not knowledge. Claims already exist. Calc already emits all three. No source is opened.

---

## Architecture impact

- **SoT before:** Layer 1 schema required `function` · `themes` · `positive_expression` · `shadow` · `domains` · `tempo` on every `celestial_object`. Outer objects stayed withheld because filling those keys from Hand (or averaging three schools) was a single-school fake. Inventory owner chose this schema pass before ASC/MC and before composition.
- **SoT after:** those keys stay in the model. On IL-1 **draft** Uranus / Neptune / Pluto they are **optional**. Sun–Saturn requiredness is unchanged. School-specific packages stay in the **claims ledger**, not collapsed onto one object `function`. `domains` four natal keys and `tempo` stay omitted on any future structural draft (unattested / not automatically structural). `status=active` with omitted meaning keys is forbidden. No objects this pass (analog 1.3.67).
- **Public contract changed?** yes — JSON Schema `astrology_interpretation_v1`: Layer 1 meaning keys are not required when `object_id` is `astro.object.uranus` | `neptune` | `pluto`. Classical seven unchanged.
- **Migration required?** no — catalog still has 0 outer objects; runtime still ignores `draft`.
- **Canon updated?** yes — this file · IL §6.26 / 1.3.72 · schema
- **Backward compatible?** yes for runtime (nothing `active`). A validator that required meaning keys on every Layer 1 object will reject a future structural outer draft.

---

## Field map (locked)

| Field | Band | Outer draft (`status=draft`) | Before `active` | Notes |
|-------|------|------------------------------|-----------------|-------|
| `object_id` · `type` · `layer` · `phenomenon` · `machine_entity_code` | identity | **required** | required | Calc emit. Not IL meaning. |
| `theme_clusters` · `polarity` · `temporal_class` | structural / clustering | **required** (every knowledge object) | required | May be schematic (`timing` / `neutral` / `natal` or `slow`) like signs. Not a meaning package. |
| `composed_from` · `provenance` · `status` · `version` | catalog | **required** | required | Provenance must not copy a school `function` sentence in order to exist. |
| `function` · `themes` · `positive_expression` · `shadow` | later-interpretive (outer) | **optional on draft** | required, and must not be a synthetic collapse | School meaning packages. Not Sun–Saturn elemental `function`. |
| `domains` | later-interpretive | **optional on draft; omit on structural draft** | required only after natal four-key set is attested | Schema four keys (relationships / money / work / self) are **unattested**. Collective/tech/art stay ledger-only. |
| `tempo` | not automatically structural | **optional on draft; omit on structural draft** | later named pass | 84y = Rudhyar; cumulative = Hand; Swiss period = astronomy `facts_only`. |
| school-specific packages | claims ledger | **allowed as multiple `school_specific` rows** | still not CORE | Do **not** add a `packages[]` object field. IL does not expand schema “just in case.” |
| TodayFlow synthesis / CORE average | — | **forbidden** | forbidden until a named synthesis SoT | Uranus ≠ change. Neptune ≠ intuition. Pluto ≠ transformation. |

**Forbidden slogans (do not write into object slots):**

- Uranus = change / rebellion / freedom / disruption-as-universal
- Neptune = dreams / intuition / spirituality / dissolution-as-universal
- Pluto = transformation / death / power-as-universal

Disruption ≠ transform ≠ Prometheus. Dissolution ≠ ecstasy ≠ ocean-of-consciousness. Reconstruction ≠ seed/hierophant ≠ life-force-in-substance. Those remain **claims**.

---

## Can the ledger support three honest drafts?

**Yes — as structural drafts only**, same ceiling as 1.3.68 signs: identity + clustering; later-interpretive omitted.

| Check | Result |
|-------|--------|
| Evidence exists | Yes. Three `school_specific` classes on each body. CORE = 0. |
| Schema no longer forces a fake `function` | Yes, this pass. |
| `domains` natal four-key | Still unattested (Pluto 0; Uranus/Neptune collective/tech/art). **Omit.** |
| `tempo` | Would pick a school or copy Swiss. **Omit.** |
| Object-slot school | **Do not pick in this pass.** Hand is not Lilly-for-outers. Materialize (next named) must omit meaning keys, not fill from Hand. |
| `active` | Forbidden while meaning keys are omitted (runtime would read absence as “no function”). |

If a future pass cannot omit the meaning keys without pretending consensus, the honest state remains **withheld**. That is still a correct catalog state.

**Not this pass:** three objects · Hand as object factory · CORE · literature · ASC/MC.

---

## Next

Named: **TodayFlow Canon selection (1.3.73) before any outer `function`.** Materialize Uranus / Neptune / Pluto as `status=draft` structural objects only after Canon criteria exist; omit later-interpretive until Canon lock. Then ASC/MC definition (parent steps 1–4), not a book.
