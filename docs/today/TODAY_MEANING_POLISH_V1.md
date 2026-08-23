# Today Meaning Polish V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — Today native binds astrology chorus to IL-4 packs. **Not** public JSON. **Not** Today prompts as meaning SoT. **Not** post-LLM hard overwrite. **Not** `active`. **Not** freeze / IL-2 / IL-3 / IL-4 / wire / attach / consume reopen. **Not** user relevance.  
**Canon:** [TODAY_CONTENT_PIPELINE_V1.md](./TODAY_CONTENT_PIPELINE_V1.md) I0 · [IL4_EDITORIAL_CONSUME_V1.md](../astrology/IL4_EDITORIAL_CONSUME_V1.md). Inventory: step 42 · KC-C-TODAY-POLISH. AGENTS.md Architecture impact.

This pass answers: **how Today native scenario generation uses IL-4 consume on the astrology chorus voice** without making prompts meaning SoT or rewriting IL lemmas.

Catalog **38 draft / 0 `active`**. Unchanged.

---

## Architecture impact

- **SoT before:** Consume 1.3.113 put `IL4_MEANING` on LLM input and reject-invalid at pack level. Native system prompt still let `interpretive_chorus.astrology` invent parallel astrology from flat facts. Today meaning polish stayed PAUSED.
- **SoT after:** **Today Meaning Polish V1** binds the astrology chorus voice to IL-4 lemmas when a pack is present. Native system adds `TODAY_IL4_CHORUS` instruction; empty astrology chorus is rejected; empty `human_meaning` may fill from pack primary `text` only. Conflict / scenes remain DRAMATURGY_BRIEF + I0. Public contracts unchanged. Consume 1.3.113 stands.
- **Public contract changed?** no — polish is LLM input / editorial gate only
- **Migration required?** no — refresh/force_rebuild picks up prompt `day-scenario-native-c4.2`
- **Canon updated?** yes — this file · IL §6.68 · inventory KC-C-TODAY-POLISH + step 42 · handoff · tracker
- **Backward compatible?** yes — missing pack → previous native path

---

## 0. Contract

| Rule | Do | Do not |
|------|----|--------|
| Astrology chorus | Phrase IL4_MEANING lemmas / construction | Invent new sky meaning beside the pack |
| Conflict / scenes | DRAMATURGY_BRIEF + I0 | Replace plot with IL-4 |
| Fill | Empty `human_meaning` only | Overwrite valid LLM prose |
| Reject | Missing / empty astrology chorus when pack has lines | Scrub phrasing because lemmas are English |
| Surfaces | Today native only | Profile · Compatibility · personality_v1 |

`services/today_meaning_polish_v1.py` does **not** import calc wire or consume internals beyond `pack_present` / `fill_empty_slot`.

---

## 1. Hook

| Step | Location |
|------|----------|
| System augment | `day_scenario_native_llm_c1` after consume augment |
| Reject-invalid | after consume reject, before schema normalize |
| Fill-empty | after normalize, before soft heals |

Prompt version: `day-scenario-native-c4.2`.

---

## 2. This pass does not do

- Public JSON · set `active` · lemma rewrite · IL engine reopen
- Profile / Compatibility polish · synastry chart plumbing · personality_v1 IL-4
- Hard overwrite of filled slots · Relevance / Prioritization
- Deploy / merge to `main` without owner
- Split Global / Personal LLM (I0 violation fix) — separate pass

---

## Changelog

- **1.0 (2026-08-23)** — 1.3.114. Today native binds astrology chorus to IL-4 packs. Public contracts unchanged.
