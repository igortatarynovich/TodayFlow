# IL-4 Editorial Consume V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — generation phrases IL-4 packs. **Not** public JSON. **Not** Today prompts as meaning SoT. **Not** post-LLM hard overwrite. **Not** `active`. **Not** freeze / IL-2 / IL-3 / IL-4 / wire / attach reopen. **Not** user relevance.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) Sequence · §6.67 · §7. Inventory: step 41 · KC-C-CONSUME. Attach: [IL4_SURFACE_ATTACH_V1.md](./IL4_SURFACE_ATTACH_V1.md). Expression: [IL4_EXPRESSION_V1.md](./IL4_EXPRESSION_V1.md). Day Meaning SoT: [TODAY_CONTENT_PIPELINE_V1.md](../today/TODAY_CONTENT_PIPELINE_V1.md) I0. AGENTS.md Architecture impact.

This pass answers: **how editorial generation consumes an already attached pack.** Meaning stays stored lemmas + IL-2/3. IL-4 voices. LLM may phrase; it does not choose Saturn □ Venus. Today prompts stay editorial / transport.

Catalog **38 draft / 0 `active`**. Unchanged.

---

## Architecture impact

- **SoT before:** Attach 1.3.112 put `il4_expression_pack` on Today / Profile / Compatibility LLM inputs. Prompts still treated interpretation / DRAMATURGY_BRIEF as if the model could choose astrological meaning. Today meaning polish stayed PAUSED.
- **SoT after:** **IL-4 Editorial Consume V1** is the generation contract. When a pack is present: system prompt + protected `IL4_MEANING` prefix tell the model to phrase lemmas; empty slots may fill from pack `text` (fill-empty); invalid output (empty / `llm_chose_meaning` / voiced refused atoms / mutated lemmas) is rejected. Public contracts unchanged. Day plot SoT remains TODAY_CONTENT_PIPELINE I0. Freeze, IL-2, IL-3, IL-4, scale, wire, and attach stand.
- **Public contract changed?** no — consume is LLM input / editorial gate only
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.67 · inventory KC-C-CONSUME + step 41 · handoff §3 · tracker NOW
- **Backward compatible?** yes — missing pack → previous editorial path (no invented meaning)

---

## 0. Contract

| Rule | Do | Do not |
|------|----|--------|
| Prompt | Phrase from pack lemmas | Choose Saturn □ Venus; add themes; swap lemmas |
| Fill | Empty slots only | Overwrite LLM / event-derived prose |
| Reject | Empty output · voiced dropped outers · mutated pack lemmas · `llm_chose_meaning` | Scrub valid phrasing because lemmas are English |
| Day plot | DRAMATURGY_BRIEF / Global Day Engine | Replace I0 with IL-4 |
| Surfaces | Today native · Profile legacy LLM · Compatibility when pack present | Personality/CE path (person layer); synastry editorial without charts |

`services/il4_editorial_consume_v1.py` does **not** import the calc wire. It reads the attached pack dict.

---

## 1. Surfaces

| Surface | Consume hook |
|---------|----------------|
| Today | `day_scenario_native_llm_c1` — augment native system prompt; protect `IL4_MEANING` above DRAMATURGY_BRIEF; reject-invalid before schema accept |
| Profile | `call_profile_contract_llm_v1` — augment system prompt when `llm_pack` has the pack |
| Compatibility | `generate_llm_product_surface` — augment system prompt when payload has the pack |

Personality / Character Engine still does not read astrology (I0). Compatibility editorial without `chart1` still has no pack (attach 1.3.112 limitation).

---

## 2. This pass does not do

- Public JSON fields · set `active` · lemma rewrite · IL engine / wire / attach reopen
- Today prompts as meaning SoT · Relevance / Prioritization
- Hard overwrite of filled slots
- Deploy / merge to `main` without owner
- Personality_v1 / CE astrology inject · synastry chart plumbing

Today *meaning polish* may resume as an **owner-directed** pass after consume 1.3.113. **Done 1.3.114.** This consume file does not reopen.

---

## Changelog

- **1.1 (2026-08-25)** — Profile meaning polish 1.3.123: natal decode consumes packs. This consume stands.
- **1.0 (2026-08-23)** — 1.3.113. Editorial generation consumes IL-4 packs. Public contracts unchanged.
