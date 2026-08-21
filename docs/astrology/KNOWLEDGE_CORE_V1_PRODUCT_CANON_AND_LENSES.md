# Knowledge Core V1 — Product Canon and Lenses

**Date:** 2026-08-21  
**Status:** LOCKED (fundamental split). **Not** ingest. **Not** objects. **Not** schema. **Not** CORE scoring. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.30. Selection method: [TODAYFLOW_CANON_V1.md](./TODAYFLOW_CANON_V1.md). Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md). Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Co–Star check: [COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md](../audits/COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md).

This file is the Knowledge Core V1 split. Do not change another object until this split is the SoT.

---

## Architecture impact

- **SoT before:** product meaning was still being designed as school-convergence or as a short pass over the 491-claim ledger (1.3.73–1.3.74). IL architecture then froze pending a Co–Star in-app teardown (1.3.75). The research corpus was treated as the arbiter of what Saturn “is.” Disagreement between schools looked like a hole.
- **SoT after:** two jobs, two datasets. **Product Canon** = mainstream contemporary Western convention, then uniquely *structured* by TodayFlow. **Research Corpus** = interpretive lenses (classical / traditional / psychological / humanistic / professional) for education, deep dives, SEO, provenance. They are not averaged. CORE is not a product gate. Co–Star is a **recognition check**, not a meaning source and not a blocker. No new books. No object rewrite this pass.
- **Public contract changed?** no
- **Migration required?** no — catalog 36 draft / 0 `active`; claims unchanged
- **Canon updated?** yes — this file · IL §6.30 · TODAYFLOW_CANON_V1 pipeline · inventory execution order · parent · handoff
- **Backward compatible?** yes for runtime. Deprecated: school-intersection as product meaning; scoring the historical ledger as the next Canon pass; Co–Star Phase 1 as the IL unlock.

---

## 0. The split (do not mix)

```text
Mainstream conventions  →  TodayFlow Canon  →  main runtime
  (Today · Profile · Compatibility · Composition Engine)

Historical / research corpus  →  Lenses  →  education / deep dives / SEO / provenance
```

| Layer | Job | User sees it as | Must not do |
|-------|-----|-----------------|-------------|
| **Mainstream Western Astrology V1** | Lock the contemporary convention | The default “what this symbol means” | Prove historical truth. Google-frequency. One author. One school. |
| **TodayFlow Canon** | Unique **structuring** of that convention | Compact atoms the engine can compose | Invent a private astrology. Copy Cafe Astrology / Astrodienst / Co–Star prose. |
| **Research Corpus / Lenses** | Keep the schools distinct | Optional other ways to look at the same symbol | Average them. Gate runtime on CORE. Throw the ledger away. |

The already-collected corpus is not wasted. It was a good research dataset used for the wrong product job.

Author wording stays in research/provenance. It is not copied into user-facing Canon.

---

## 1. What “mainstream” means (operational)

Not one book. Not Google frequency. Not CORE.

**Mainstream meaning** = a meaning that independently and regularly appears in several major **contemporary** sources of Western astrology, and is not a specialty of one school or one author.

We do not have to prove it. We have to **fix the convention**.

A lemma is *not* mainstream if:

- it appears in only one of the panel sources
- it is a Greene-only, Lilly-only, Rudhyar-only, or Hand-only category
- it is a slogan invented at runtime by an LLM
- it is the most-Googled word with no second independent modern source

Owner preliminary pass (not yet the locked map): Astrodienst gives Sun identity/will/vitality; Moon emotions/subconscious; Mercury thought/communication; Venus attraction/relationships; Mars assertion/aggression; Jupiter expansion/meaning; Saturn limitation/form; Uranus liberation/disruption; Neptune dissolution of limits/mysticism; Pluto transformation. Other modern sources repeat the same frame and extend it (Mars action/desire, Saturn structure/limits/maturity, Uranus change/freedom/originality, Neptune imagination/dissolution, Pluto power/transformation).

That stability is the V1 foundation. It is convention, not objective truth.

---

## 2. Finite map (no infinite research)

**No new books now.**

Order:

```text
Planets → Signs → Houses → Aspects → ASC/MC
```

For each entity: collect repeating modern meanings from a **bounded** modern panel → write Mainstream territory → **once** synthesize TodayFlow Canon structure.

This is a finite task. It is the task that should have been first.

### 2.1 Modern panel (bounded)

Meaning sources for Mainstream V1 (encyclopedia/reference class, not monographs):

| # | Source | Role |
|---|--------|------|
| 1 | Astrodienst / astro.com | Independent modern reference |
| 2 | Cafe Astrology | Independent modern popular reference |
| 3 | One more source of the **same class** | Named at the start of the planet pass. Not a book. Not a school monograph. |

**Recognition check (not a meaning source):** Co–Star and other successful products. After a Mainstream row exists, ask: would a contemporary user recognize this as “what astrology says”? If our Saturn is academically neat and unrecognizable next to Co–Star’s discipline/limits language, the row is wrong for the product.

Do not ingest Co–Star, Cafe Astrology, or Astrodienst paragraphs into `claims/` as product text. Cite concept → source. Write TodayFlow lemmas.

---

## 3. Working draft — planet Mainstream territory

**Status:** owner working draft. **Not** written into objects. **Not** Canon lock. Next named pass confirms or edits this table against the panel in §2.1.

| Planet | Mainstream semantic territory |
|--------|-------------------------------|
| Sun | identity · self · vitality · will · purpose |
| Moon | emotions · needs · instincts · security · subconscious |
| Mercury | thinking · communication · learning · information |
| Venus | attraction · love · relationships · values · pleasure |
| Mars | action · drive · desire · assertion · conflict |
| Jupiter | growth · expansion · opportunity · belief · meaning |
| Saturn | limits · responsibility · structure · discipline · maturity |
| Uranus | change · disruption · freedom · independence · innovation |
| Neptune | imagination · ideals · dissolution · sensitivity · illusion |
| Pluto | power · intensity · compulsion · transformation · regeneration |

Words that IL previously forbade as CORE slogans (`Uranus = change`, `Pluto = transformation`) **may appear here as Mainstream territory**. They still must not be:

- taught as laboratory truth or CORE
- used as the only unstructured `function`
- copied as vendor prose

TodayFlow’s job is to **structure** that territory, not to invent a different astrology.

---

## 4. TodayFlow Canon = unique structuring, not unique astrology

Mainstream says: Mars = action, desire, assertion, aggression, drive.

TodayFlow may structure that as (shape example, **not** an object lock, **not** a schema change this pass):

```text
function     → initiate / pursue
need         → agency
constructive → courage, decisive action, assertion
shadow       → aggression, impulsivity, conflict
domains      → action, desire, competition
```

That is **our data**. No runtime research.

Schema today still uses `function` · `themes` · `positive_expression` · `shadow` · `domains`. Mapping of `need` / `constructive` onto those keys is a later named schema pass. Do not add keys in this file’s wake.

Do the same structuring for signs, houses, aspects, then ASC/MC. Then check Co–Star (recognition), not copy.

---

## 5. Lenses (keep the corpus)

The existing classical / traditional / psychological / humanistic / professional ledger stays.

Schools **should not** converge. That is now a product advantage.

Example — one Saturn, several views:

| Surface | What it holds |
|---------|----------------|
| **TodayFlow (default)** | limits · responsibility · structure · discipline · maturity |
| **Classical lens** | cold · dry · slow · restrictive / malefic |
| **Psychological lens** | inner limits, fear, development through meeting them |
| **Humanistic lens** | growth through limitation and a maturing process |
| **Traditional lens** | that tradition’s own terms, not rewritten into modern keywords |

Possible later product (not this pass): “How modern astrology sees Saturn”, “Saturn through four traditions”, “Why Saturn does not mean the same thing in every school.” SEO, education, long-form, premium deep dives.

`evidence_tier=core` may remain as **cross-tradition convergence metadata**. It does not decide product meaning. CORE scoring is not a gate and is not the next task.

---

## 6. Runtime

```text
calc  →  TodayFlow Canon atoms  →  composition  →  LLM formulates
```

Lenses are not on that path unless a named surface (education / premium) asks for a lens.

IL-4 still cannot choose meaning. It receives Canon atoms.

---

## 7. This pass does not do

- Rewrite Sun–Saturn `function` or any object slot
- Materialize outers
- Open a book
- Score CORE
- Change JSON Schema
- Start the Astrodienst / Cafe Astrology extract
- Unlock Co–Star in-app scraping

**Next named (one task):** Mainstream Western Astrology V1 **planet** map from the §2.1 panel. Confirm or edit §3. Still no object rewrite until that map is owner-locked.

---

## Changelog

- **1.0 (2026-08-21)** — Product Canon vs Lenses locked. Mainstream operational definition. Planet territory = working draft. Co–Star = recognition check. CORE not a gate. No objects.
