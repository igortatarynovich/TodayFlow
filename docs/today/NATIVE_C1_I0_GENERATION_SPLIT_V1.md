# Native C1 I0 Generation Split V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — native C1 uses two LLM stages (Global then Personal overlay). **Not** public JSON. **Not** meaning SoT rewrite. **Not** post-LLM hard overwrite. **Not** `active`. **Not** IL-4 attach/consume/polish reopen.  
**Canon:** [TODAY_CONTENT_PIPELINE_V1.md](./TODAY_CONTENT_PIPELINE_V1.md) I0 · [TODAY_MEANING_POLISH_V1.md](./TODAY_MEANING_POLISH_V1.md). Inventory: step 44 · KC-C-I0-SPLIT. AGENTS.md Architecture impact.

This pass answers: **how native C1 respects I0** so one LLM call no longer decides chorus + conflict + natal together.

Catalog **38 draft / 0 `active`**. Unchanged.

---

## Architecture impact

- **SoT before:** `day_scenario_native_llm_c1` used one LLM call for astrology chorus, card/number voices, conflict, scenes, natal, and personalization traces. I0 required Global then Personal authorities; monolith let the model choose cross-layer meaning in one shot.
- **SoT after:** **Native C1 I0 Generation Split V1** runs **Global stage** (chorus sky/card/number + conflict + scenes + prop_material; no natal / no personal traces) then optional **Personal stage** (natal voices, `why_personal`, personalization traces only). Personal consumes `GLOBAL_LOCKED` snapshot; merge applies overlay fields only. Personal failure degrades to Global-only. IL-4 attach/consume/polish stay downstream on Global astrology voice. Prompt `day-scenario-native-c5.1` (see [NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1](./NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md)). Public JSON unchanged.
- **Public contract changed?** no — internal generation order / LLM stages only
- **Migration required?** no — refresh/force_rebuild picks up c5.0
- **Canon updated?** yes — this file · IL §6.70 · inventory KC-C-I0-SPLIT + step 44 · handoff · tracker · TODAY_MEANING_POLISH (split done)
- **Backward compatible?** yes — same `day_scenario_v1` projection; cached c4.x days until regenerate

---

## 0. Contract

| Rule | Do | Do not |
|------|----|--------|
| Order | `global` → `personal` when `evidence_depth` is light/deep | Personal before Global |
| Global stage | Phrase sky/card/number + conflict + scenes | natal[] · why_personal · personal traces |
| Personal stage | Phrase natal + personal traces from pack | Mutate title/forces/why_today/scene bodies |
| Merge | Overlay personal fields onto Global norm | Replace Global from personal JSON |
| Degrade | Personal fail → Global-only story | Invent personal on transport fail |
| IL-4 | Consume/polish on Global astrology (unchanged) | Reopen attach/consume/polish lemmas |
| Surfaces | Today native C1 only | Profile · Compatibility |

`services/native_c1_i0_generation_split_v1.py` orchestrates stages; `day_scenario_native_llm_c1` calls it.

---

## 1. Regression gate (smoke)

| Check | Mechanism |
|-------|-----------|
| Deterministic order | `generation_stages(pack)` → `["global"]` or `["global","personal"]` |
| Global not mutated | `detect_global_mutation` + merge ignores global keys from personal raw |
| Natal does not recalc astrology | Personal input = `GLOBAL_LOCKED`; no sky facts in personal user message |
| LLM phrases, not chooses atoms | IL-4 consume/polish still on Global astrology output |
| IL-4 downstream | attach/consume/polish hooks unchanged in Global stage processor |
| Public JSON | `native_llm_to_day_scenario_v1` unchanged projection |

Tests: `backend/tests/test_native_c1_i0_generation_split_v1.py`.

---

## 2. This pass does not do

- Public JSON fields · set `active` · full pipeline redesign (Global Day Engine nests)
- Deploy · merge to `main` without owner
- Third LLM for card/number split (minimal I0 only)
- Reopen IL-2/3/4 · wire/attach/consume/polish/compat editorial

Profile meaning polish — **done 1.3.123.** This I0 file does not reopen.

---

## Changelog

- **1.0 (2026-08-23)** — 1.3.116. Native C1 I0 split Global/Personal LLM stages. Prompt c5.0. Public contracts unchanged.
