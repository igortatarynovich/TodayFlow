# Layer 2 Signs — classification close-out (1.3.69)

**Date:** 2026-08-21  
**Status:** Layer 2 Signs is **classification-complete / interpretation-deferred**.  
**Not:** ingest · CORE scoring · `status=active` · twelve portraits · Cell C extract · Pulse Part Two · Hand Ch.10.

Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Canon: [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.23. Catalog: `DATA/reference/astrology/interpretation_v1/objects_v1.json`.

This pass is a readiness audit of the twelve 1.3.68 drafts. It does not add claims, objects, or schools.

---

## Verdict

| Band | Verdict |
|------|---------|
| Classification objects | **Complete** — 12 `type=sign` `draft` records; Lilly CA I.16 is the object-slot school |
| Claims ledger collisions | **Kept** — Ptolemy / Lilly / Valens / Houlding / Rudhyar stay in claims; not averaged onto objects |
| Later-interpretive | **Deferred** — slots remain in the model, optional on IL-1 draft, unfilled. Cell C stays `ACCESS_BLOCKED` (future evidence dependency, not a Layer 2 blocker) |
| CORE / `active` | **Not this layer's job** — still blocked |

**Do not continue Layer 2 as a literature project.** Structural fullness does not wait on Cell C, Pulse Part Two, or Hand Ch.10.

---

## Split that stays locked

| Layer | Holds | Must not hold |
|-------|-------|----------------|
| Sign object | identity + `mode` / `element` / `orientation`; `status=draft`; Lilly provenance | character of Aries; motivation of Scorpio; QUALITY adjectives; Ptolemy winds; Valens weather; Rudhyar tides |
| Sign claims ledger | Ptolemy · Lilly · Valens · Houlding · Rudhyar as distinct lemmas | a forced average that the object then copies |
| Later-interpretive | empty optional slots; Cell C `ACCESS_BLOCKED` | a fake fill from Pulse / QUALITY / the first readable modern book |

1.3.67 made this split possible. Required `motivation` / `strengths` / `excess` / `deficiency` would have forced either zero signs or a modern cookbook fill. That trap stays closed.

---

## Audit (live 1.3.69 recount)

All twelve: `aries` … `pisces`. Unique object keyset (excluding `provenance`): `composed_from`, `confidence`, `curation_reason`, `element`, `layer`, `machine_entity_code`, `mode`, `object_id`, `orientation`, `phenomenon`, `polarity`, `status`, `temporal_class`, `theme_clusters`, `type`, `version`.

| Check | Result |
|-------|--------|
| Count / status | 12 signs, all `draft` `layer=2` `version=0.1.0`. Catalog 36 draft / 0 `active` |
| Structure | Same keys on all twelve. Later-interpretive keys **absent**. Surface keys **absent** |
| Schema cluster | `theme_clusters=["timing"]` (year-span, not Pulse). `polarity=["neutral"]` (schema polarity, not Lilly gender). `temporal_class=natal`. `composed_from=[]` |
| Object slots | Lilly grid: masculine→`positive`, feminine→`negative`; moveable/cardinal→`cardinal`; common/bicorporeal→`mutable` |
| Mode source | QUALITY one-liner when it names the mode. **Leo** / **Virgo** QUALITY omit mode → Lilly lists already extracted (`claim.sign.fixed_follow_turning`, `claim.sign.bicorporeal`) |
| Provenance | Three rows (`mode` · `element` · `orientation`). All `src.classical.lilly_christian_astrology`, `classical`, `school_specific`, `extracted`. Each `concept_id` exists in the sign ledger or `astro.sign.classifications` |
| QUALITY leakage | Personality adjectives stay in **claims** `original_claim` (and may appear on provenance `original_claim` as the opened Lilly sentence). They are **not** in object slot values or `normalized_claim` |
| Ledger field leftover | Lilly QUALITY claims remain tagged `field=expression` from earlier ingest. That is ledger tagging of a nature line, **not** `object.expression` (that key is omitted) |
| Collisions off objects | No Ptolemy, Valens, Houlding, or Rudhyar `source_id` on sign-object provenance. Classifications ledger still holds all four plus Lilly |
| CORE | 0 `evidence_tier=core` on sign objects |

Lilly grid locked by this recount:

| Sign | mode | element | orientation |
|------|------|---------|-------------|
| Aries | cardinal | fire | positive |
| Taurus | fixed | earth | negative |
| Gemini | mutable | air | positive |
| Cancer | cardinal | water | negative |
| Leo | fixed | fire | positive |
| Virgo | mutable | earth | negative |
| Libra | cardinal | air | positive |
| Scorpio | fixed | water | negative |
| Sagittarius | mutable | fire | positive |
| Capricorn | cardinal | earth | negative |
| Aquarius | fixed | air | positive |
| Pisces | mutable | water | negative |

---

## What this does **not** close

- Cell C (Arroyo / Martin / Hamaker) — `ACCESS_BLOCKED`; extraction-only when a named principle chapter is readable and passes L2-C7+C8
- Pulse Part Two / *Astrology of Personality*
- Hand Ch.10
- CORE scoring
- `status=active`
- Remaining IL-1 gold-set holes: Uranus / Neptune / Pluto objects, ASC / MC (existing withhold gates), Layer 5 candidates

Those are **other named passes**. They are not Layer 2 incompleteness.

---

## Next

Do **not** start another Layer 2 ingest. The next Knowledge Core slice, when named, follows the parent order from step 1 if it is a new semantic core. Houses and aspects already have classical drafts. Do not reopen sign literature to look complete.
