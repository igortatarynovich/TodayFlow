# TodayFlow Canon V1 — semantic selection

**Date:** 2026-08-21  
**Status:** LOCKED (architecture + methodology). **Product vs Lenses split: 1.3.76.** **Not** ingest. **Not** objects. **Not** CORE scoring. **Not** LLM synthesis run. **Not** Sun–Pluto fill. **Not** Outer fill. **Not** ASC/MC.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.27–§6.30. Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md). Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Outer schema: [IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md](./IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md).

The original architecture was right: a prepared knowledge layer, not astrology generated on the fly.

```text
calc  →  stable semantic atoms  →  composition rules  →  LLM only formulates
```

That is what buys TodayFlow four properties: **cheap inference**, **repeatable results**, **a testable system**, and **swappable LLM** without changing astrological logic.

The error was the optimization criterion: “prove meanings through independent schools” (Ptolemy → Lilly → Greene → Hand → Rudhyar → gaps → CORE → more books). That is not the library we needed.

The other extreme is also forbidden: LLM inventing “popular” meanings at runtime. That destroys the four properties.

**Third model:** a static **TodayFlow Semantic Canon**. LLM is a build-time research tool. It is not the runtime source of meaning.

---

## Architecture impact

- **SoT before:** product meaning waited on `evidence_tier=core` ≈ same lemma across independent school classes. Disagreement (Pluto = power vs transformation vs death/rebirth vs unconscious forces) was treated as a hole that more authors should close. Outer schema (1.3.72) was next to fill. Engine rule: primary theme from `core` ∪ `supported`. `editorial` could not be the sole user-facing basis.
- **SoT after:** two datasets. **Mainstream Western Astrology V1** (contemporary convention from a bounded modern panel) → **TodayFlow Canon** (our structuring) → runtime. **Research Corpus** → Lenses (education / SEO / deep dives / provenance), not averaged. CORE is not a product gate. Co–Star is a recognition check. 491 claims stay as lens material. **1.3.76** supersedes “next = short corpus pass” and “next = Co–Star Phase 1 as IL unlock.”
- **Public contract changed?** no JSON Schema this pass. Future IL-3 reads Canon object slots, not `evidence_tier=core`.
- **Migration required?** no — catalog 36 draft / 0 `active`; claims unchanged; CORE still unscored
- **Canon updated?** yes — this file · [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md) · IL §6.30 · 1.3.76
- **Backward compatible?** yes for runtime (`draft` ignored). Deprecated as product gate: wait-for-CORE; score-the-historical-ledger; Co–Star in-app as unlock.

---

## 0. Three layers (do not mix)

| Layer | Holds | Does not hold |
|-------|-------|----------------|
| **Mainstream V1** (was “Semantic Consensus”) | Contemporary Western convention from a bounded modern panel. Operational definition in the split file. | Google frequency. One author. Historical heat/dry as Today function. |
| **TodayFlow Canon** | Unique structuring of that convention (`core_function` / `drive` / `needs` / `constructive` / `distorted` / `domains` — our lemmas). | Copied paragraphs. Runtime LLM invention. A private astrology. `tempo` as meaning. |
| **Research Corpus / Lenses** (was “Evidence Corpus”) | What classical / traditional / psychological / humanistic / professional sources assert. Existing claims + provenance. | Product default. CORE permission. |

Then:

```text
TodayFlow Canon  →  Composition Engine  →  LLM realization
```

Saturn is stable data. At request time the LLM receives those atoms and only composes / formulates (`Mars + Capricorn + square Saturn + transit`). It does not re-decide what Saturn means.

**Weighting (locked):** Ptolemy/Lilly get no extra vote for being older. Greene/Hand get no extra vote because a chapter happened to be readable. Historical sources do **not** vote for Product Canon; they populate Lenses. Mainstream is judged on a bounded modern panel (Astrodienst, Cafe Astrology, one more reference of that class) — not Google, not the 491-claim ledger.

**Legal (locked):** sources give facts about *concept prevalence*. TodayFlow writes its own ontology and lemmas. `Mars → action / drive / assertion` is not a copied author paragraph. Provenance stays: concept → sources where the concept was found. Verifiability without copyrighted dump.

**LLM (locked):**

| When | Role |
|------|------|
| Build-time | Research assistant on a **supplied** Mainstream panel field (or a Lens field). Cluster / draft. Never the field. Never the lock. |
| Runtime | IL-4 Expression only. Receives Canon atoms. Does not choose meaning. |

---

## 1. What TodayFlow Canon is

A **TodayFlow Canon** slot is the semantic function an object has in *this* product: recognizable in contemporary Western astrology, internally consistent, distinct from sibling atoms, and usable in composition.

It is **not**:

- the true meaning of Pluto
- the intersection of schools
- the most Googled keyword
- one author’s system copied into JSON
- an LLM dump of “what astrology usually says”

IL V1 still does not need complete astrology. It needs the minimum controlled primitives so Today / Profile / Compatibility can run without the LLM inventing meanings. Canon is how those primitives are *chosen*.

---

## 2. Pipeline (locked)

Old:

```text
author → claim → school → convergence → CORE → product
```

New:

```text
Bounded modern panel (Astrodienst · Cafe Astrology · one more reference)
        ↓
Mainstream Western Astrology V1 (convention, not proof)
        ↓
TodayFlow Canon (owner lock, our structuring, composition-shaped)
        ↓
Composition Engine
        ↓
LLM realization

Research corpus (classical / traditional / psychological / humanistic / professional)
        ↓
Lenses (education / SEO / deep dives / provenance)
```

Literature is not thrown away. It stops voting for product meaning. Co–Star is a recognition check on the Mainstream row, not a third astrology.

**Prevalence is a plus**, not a defect. “Take whatever is most Googled” is still forbidden. Mainstream ≠ internet horoscope. Mainstream = repeating convention in a named modern panel.

---

## 3. Criteria (locked)

Every candidate lemma is scored on all five. None of them alone is enough.

| Axis | Question | Fail if |
|------|----------|---------|
| **Prevalence** | Does it show up systematically in contemporary Western astrology, not one author? | Single-locus slogan; Rudhyar-only celestial seed as base |
| **Recognition** | Would a user of an astrological product expect roughly this reading? | Internal jargon the field does not use |
| **Product utility** | Can Profile, Today, Compatibility, and composition *do work* with it? | Pretty definition that never lands in a day or a relationship |
| **Distinctiveness** | If the same unstructured word equally fits Pluto, Uranus, Scorpio, and House 8, the word is not the atom. Structure it (function / need / shadow). Mainstream *territory* may repeat (`transformation` on Pluto). | The same unstructured slogan on four objects |
| **Composability** | Can the atom combine: planet×sign, planet□planet, transiting A □ natal B? | A closed essay that cannot enter IL-2 |

Product question (replaces “what is the true meaning?”):

> What semantic function must this object have in the TodayFlow model so that it is recognizable in modern astrology, internally consistent, and composable?

---

## 4. Disposition of a lemma

Used in the next Sun–Pluto audit. Not schema enums this pass.

| Disposition | Meaning |
|-------------|---------|
| `canon_base` | Base mechanism in TodayFlow Canon. May still need distinctiveness sharpening. |
| `canon_specify` | Prevalent and useful, too generic as a single word. Keep and specify the mechanism vs siblings. |
| `canon_careful` | High recognition, constrained use (charge, fatalism, medical bleed). |
| `school_tint` | Keep on the claims ledger; not the base slot. |
| `out` | Do not use in product meaning. |

Illustrative only — **not** a Pluto Canon lock:

| Lemma | Prevalence | Distinctiveness | Utility | Disposition |
|-------|------------|-----------------|---------|-------------|
| Pluto = transformation | very high | medium | high | `canon_specify` |
| Pluto = power / control | high | high | high | `canon_base` (candidate) |
| Pluto = death / rebirth | high | high | medium | `canon_careful` |
| Pluto = celestial seed | low | high | low | `school_tint` |
| Pluto = reconstruction after total crisis | Hand-specific | high | high | `school_tint` |

Do not write `function: transformation` from this table. Distinctiveness is unfinished until Uranus / Scorpio / House 8 mechanisms are named beside it.

Target **shape** of a locked Canon object (illustrative Mars — **not** a Mars lock, not a schema change):

```text
function:     drive_and_action
themes:       initiative · assertion · desire · competition · courage · conflict
constructive: decisive action · healthy assertion · persistence · courage
              → maps to schema `positive_expression`
shadow:       aggression · impulsivity · conflict · force
domains:      action · motivation · competition · sexual drive · conflict
              → thematic pack; schema four-key natal `domains` mapping is a later pass
```

This lies as **data**. Consensus example (also not a lock): `action` / `drive` very prevalent; `assertion` / `desire` / `courage` prevalent; `aggression` prevalent as shadow; `survival` more specific; `heat/dry` historical classification, nearly useless for Today.

---

## 5. CORE (demoted)

`evidence_tier=core` **stays in the schema** as research metadata: the lemma is attested across independent traditions.

It does **not** decide whether TodayFlow may use the lemma.

- Intersection of schools ≠ truth.
- Absence of intersection ≠ “find a fifth author.”
- Two classical authors still ≠ CORE. Two `professional` authors still ≠ two schools. That provenance hygiene is unchanged.
- CORE scoring is **not** the next product pass.

IL-3 (when wired) reads **owner-locked Canon slots** on the knowledge object. It does not wait for `core` to become non-empty.

---

## 6. Synthesis method (locked)

Order. Do not skip to a model writing ontology from memory.

1. **Field.** Representative range from the existing claims ledger (and only then a named inventory row if a V1 constituent is actually missing). Human names the field. LLM does not decide what belongs in it.
2. **Cluster.** Group paraphrases into semantic clusters (duplicates collapse; real conflicts stay distinct). LLM may propose clusters from that field.
3. **Score.** Human scores clusters on the five criteria. LLM may draft a score sheet; it does not certify prevalence or recognition.
4. **Disposition.** Assign `canon_base` / `canon_specify` / `canon_careful` / `school_tint` / `out`.
5. **Mechanism.** Write the TodayFlow function as a process that composes, not a synonym list.
6. **Owner lock.** Only then is it Canon for that object. Only then may object slots be filled (including outer `function`).

**LLM may:** cluster and draft a synthesis *from a supplied field*.  
**LLM must not:** invent the field, vote Google popularity, copy one author, or emit unstructured slogans as the only `function`. Mainstream territory may include `change` / `transformation`; Canon must still structure them.

This is **not** IL-4 Expression. Expression still cannot choose meaning. Canon synthesis is an IL-1 research tool with a human gate.

---

## 7. What this pass does not do

- No ingest, no new book, no CORE scoring.
- No rewrite of Sun–Saturn `function` (still classical elemental on drafts).
- No Uranus / Neptune / Pluto objects.
- No LLM clustering run.
- No schema change.
- The Pluto table in §4 is a **method example**, not product text.

**Next named (1.3.82):** smoke-test in ([PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md)). Sign map in ([MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md)). Next = Sign Canon grammar. Not QUALITY. Not rewrite `function`. Not CORE.

Hypothesis (still true, not executing as a ledger-scoring pass): the 491 planet claims are a usable **Lens** dataset; they were asked to pick product meaning. Schema 1.3.72 remains valid. Co–Star remains a recognition check.
