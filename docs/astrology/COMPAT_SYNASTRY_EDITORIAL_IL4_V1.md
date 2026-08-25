# Compatibility Synastry Editorial IL-4 V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — synastry editorial phrases IL-4 packs when charts are supplied. **Not** public JSON. **Not** meaning SoT. **Not** post-LLM hard overwrite. **Not** `active`. **Not** freeze / IL-2 / IL-3 / IL-4 / wire / attach / consume / polish reopen.  
**Canon:** [IL4_SURFACE_ATTACH_V1.md](./IL4_SURFACE_ATTACH_V1.md) · [IL4_EDITORIAL_CONSUME_V1.md](./IL4_EDITORIAL_CONSUME_V1.md). Inventory: step 43 · KC-C-COMPAT-EDITORIAL. AGENTS.md Architecture impact.

This pass answers: **how synastry editorial generation consumes IL-4** when natal charts are already computed. Quick-compat paths without charts stay unchanged.

Catalog **38 draft / 0 `active`**. Unchanged.

---

## Architecture impact

- **SoT before:** Compatibility dynamics LLM (`compatibility_llm`) read IL-4 when `chart1` was passed (attach 1.3.112 + consume 1.3.113). Synastry `generate_compatibility_editorial` ignored IL-4 even when charts existed upstream.
- **SoT after:** Synastry editorial accepts optional `chart1` / `chart2`, attaches IL-4 via existing gateway, consumes pack (system augment + protected `IL4_MEANING` prefix + reject-invalid). Public `CompatibilityEditorial` contract unchanged. Attach / consume / polish stand.
- **Public contract changed?** no — internal LLM input / editorial gate only
- **Migration required?** no — prompt `compatibility-editorial-v1.1`; synastry refresh regenerates editorial
- **Canon updated?** yes — this file · IL §6.69 · inventory KC-C-COMPAT-EDITORIAL + step 43 · handoff · tracker
- **Backward compatible?** yes — missing charts → previous editorial path

---

## 0. Contract

| Rule | Do | Do not |
|------|----|--------|
| Charts | Pass when synastry endpoint already computed them | Require charts on quick-compat paths |
| Prompt | Phrase from pack lemmas | Choose synastry meaning beside IL-4 |
| Reject | consume reject-invalid → structured fallback | Invent meaning on LLM failure |
| Surfaces | `generate_compatibility_editorial` on synastry | personality_v1 · Today native |

---

## 1. Hooks

| Location | Change |
|----------|--------|
| `compatibility_editorial.generate_compatibility_editorial` | optional `chart1` / `chart2` → attach + consume |
| `api/compatibility.py` synastry | pass charts on fresh + cache-miss editorial |

Prompt version: `compatibility-editorial-v1.1`.

---

## 2. This pass does not do

- Public JSON · set `active` · lemma rewrite · IL engine reopen
- Quick-compat editorial without charts · personality_v1 IL-4
- Deploy / merge to `main` without owner

---

## Changelog

- **1.0 (2026-08-23)** — 1.3.115. Synastry editorial consumes IL-4 when charts supplied. Public contracts unchanged.
