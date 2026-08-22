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

**Mainstream meaning** = a **concept family** that independently shows up in the bounded contemporary panel, even if the wording differs. Sources sketch territory. Near-synonyms collapse (`assertion` / `taking action` / `readiness for action` = one family). We do not prove it. We do not run a 2/3 literal-word vote.

A family is *not* mainstream if:

- it is a Greene-only, Lilly-only, Rudhyar-only, or Hand-only category
- it is a slogan invented at runtime by an LLM
- it is the most-Googled word with no panel support
- it belongs to another planet’s stem

**Panel (locked 1.3.77):** Astrodienst · Cafe Astrology · **Astrology.com**.

Planet map: [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). Sign map: [MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md). Sign grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md).

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
| 3 | **Astrology.com** | Mass contemporary reference (locked 1.3.77) |

**Recognition check (not a meaning source):** Co–Star and other successful products. After a Mainstream row exists, ask: would a contemporary user recognize this as “what astrology says”? If our Saturn is academically neat and unrecognizable next to Co–Star’s discipline/limits language, the row is wrong for the product.

Do not ingest Co–Star, Cafe Astrology, or Astrodienst paragraphs into `claims/` as product text. Cite concept → source. Write TodayFlow lemmas.

---

## 3. Planet Mainstream territory

**Status:** locked as territory in [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md) (1.3.77). **Not** Canon. **Not** objects.

| Planet | Mainstream semantic territory |
|--------|-------------------------------|
| Sun | self · identity · vitality · will · purpose |
| Moon | emotions · needs · instincts · security · subconscious |
| Mercury | thinking · communication · learning · information |
| Venus | love · attraction · relationships · values · pleasure |
| Mars | action · drive · desire · assertion · conflict |
| Jupiter | growth · expansion · opportunity · belief · meaning |
| Saturn | limits · responsibility · structure · discipline · maturity |
| Uranus | change · disruption · freedom · independence · innovation |
| Neptune | imagination · ideals · sensitivity · illusion · dissolution |
| Pluto | power · intensity · compulsion · transformation · regeneration |

Words that IL previously forbade as CORE slogans (`Uranus = change`, `Pluto = transformation`) **may appear here as Mainstream territory**. They still must not be:

- taught as laboratory truth or CORE
- used as the only unstructured `function`
- copied as vendor prose

TodayFlow’s job is to **structure** that territory, not to invent a different astrology.

---

## 4. TodayFlow Canon = unique structuring, not unique astrology

Mainstream says: Mars = action, desire, assertion, aggression, drive.

Grammar locked in [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md) (1.3.78): `core_function` · `drive` · `needs` · `constructive` · `distorted` · `domains`. `needs` ≠ `drive`. `tempo` is Foundation/runtime, not Canon. Schema mapping is a later named pass. Do not shrink the grammar to old IL keys.

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
- Start the Astrodienst / Cafe Astrology extract as IL claims
- Unlock Co–Star in-app scraping
- Require 2/3 literal-word overlap

**Next named (one task):** smoke-test locked (1.3.82). Sign map locked (1.3.83). Sign grammar locked (1.3.84). Sign Canon fill locked (1.3.85). Sign Canon storage locked (1.3.86). Sign Canon materialization locked (1.3.87). Planet × Sign smoke-test locked (1.3.88). Houses Mainstream map locked (1.3.89). House Canon grammar locked (1.3.90). House Canon fill locked (1.3.91). House Canon storage/materialization — **done 1.3.92.** Planet × House smoke — **done 1.3.93.** Mainstream Aspect Semantic Map — **done 1.3.94.** Aspect Canon grammar — **done 1.3.95.** Aspect Canon fill — **done 1.3.96.** Aspect Canon storage/materialization — **done 1.3.97.** Stored Planet × Aspect smoke — **done 1.3.98.** Angle Canon model — **done 1.3.99.** Mainstream Angle Semantic Map — **done 1.3.100.** **STOP Aspects.** Next = **Angle Canon grammar**. STOP Houses. STOP Signs. Do not rewrite `function`.

---

## Changelog

- **1.19 (2026-08-22)** — 1.3.100 Mainstream Angle Semantic Map. Same panel. Next = Angle Canon grammar.
- **1.18 (2026-08-22)** — 1.3.99 Angle Canon model. Orientation loci. Mainstream Angle map — **done 1.3.100.**
- **1.17 (2026-08-22)** — 1.3.98 stored Planet × Aspect smoke PASS. STOP Aspects. Angle model — **done 1.3.99.**
- **1.16 (2026-08-22)** — 1.3.97 Aspect Canon storage/materialization. Five drafts carry `canon.relation`. Next = 1.3.98 stored Planet × Aspect smoke. **Done 1.3.98.**
- **1.15 (2026-08-22)** — 1.3.96 Aspect Canon fill. Five packs. Next = storage/materialization. **Done 1.3.97.**
- **1.14 (2026-08-22)** — 1.3.95 Aspect Canon grammar. One slot (`relation`). Next = Aspect Canon fill. **Done 1.3.96.**
- **1.13 (2026-08-22)** — 1.3.92 House Canon storage/materialization. Twelve drafts carry `canon.arena`. Next = Planet × House smoke.
- **1.12 (2026-08-22)** — 1.3.91 House Canon fill. Twelve packs. Destination-noun test. Next = storage/materialization. **Done 1.3.92.**
- **1.11 (2026-08-22)** — 1.3.90 House Canon grammar. One slot (`arena`). planet.domains ≠ house.arena. Next = fill, not objects. **Done 1.3.91.**
- **1.10 (2026-08-22)** — 1.3.89 Mainstream House Semantic Map. Same panel. House ≠ angle. House ≠ natural sign. Next = House Canon grammar, not fill. **Done 1.3.90.**
- **1.9 (2026-08-22)** — 1.3.88 Planet × Sign smoke-test. PASS. STOP Signs. Next = Houses Mainstream. **Done 1.3.89.**
- **1.8 (2026-08-21)** — 1.3.87 Sign Canon materialization. Twelve drafts. Next = 1.3.88 smoke-test, not houses. **Done 1.3.88.**
- **1.7 (2026-08-21)** — 1.3.86 Sign Canon storage. Optional `canon` on signs. Next = write packs, not houses. **Done 1.3.87.**
- **1.6 (2026-08-21)** — 1.3.85 Sign Canon fill. Twelve packs. Four gates. Next = storage, not objects. **Done 1.3.86.**
- **1.5 (2026-08-21)** — 1.3.84 Sign Canon grammar. Two slots. Sign = how. Next = fill, not houses. **Done 1.3.85.**
- **1.4 (2026-08-21)** — 1.3.83 sign map. Same panel. Classification is not proof. Trait ≠ manner named, not split. Next = Sign Canon grammar, not fill. **Done 1.3.84.**
- **1.3 (2026-08-21)** — 1.3.79 Planet Canon V1 locked with direct/derived provenance.
- **1.2 (2026-08-21)** — 1.3.78 Planet Canon grammar. Six slots. tempo out. needs ≠ drive. Next = 1.3.79 fill, not schema. **Done 1.3.79.**
- **1.1 (2026-08-21)** — 1.3.77 planet map. Astrology.com locked as panel #3. Concept families, not 2/3 word vote. Territory table first-term order updated. Next = Canon shape, not JSON. **Done 1.3.78.**
- **1.0 (2026-08-21)** — Product Canon vs Lenses locked. Mainstream operational definition. Planet territory = working draft. Co–Star = recognition check. CORE not a gate. No objects.
