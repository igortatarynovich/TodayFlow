# Profile Meaning Polish V1

**Date:** 2026-08-25  
**Status:** **LOCKED** — Natal Decode Depth binds sky theses to IL-4 packs. **Not** public JSON. **Not** CE / `identity_core` overwrite. **Not** personality_v1 inject. **Not** Today prompts as meaning SoT. **Not** post-LLM hard overwrite. **Not** `active`. **Not** freeze / IL-2 / IL-3 / IL-4 / wire / attach / consume / Today polish reopen. **Not** user relevance.  
**Canon:** [PROFILE_NATAL_DECODE_DEPTH_V1.md](./PROFILE_NATAL_DECODE_DEPTH_V1.md) · [TODAY_MEANING_POLISH_V1.md](../today/TODAY_MEANING_POLISH_V1.md) (mirror) · [IL4_EDITORIAL_CONSUME_V1.md](../astrology/IL4_EDITORIAL_CONSUME_V1.md) · [TODAY_CONTENT_PIPELINE_V1.md](../today/TODAY_CONTENT_PIPELINE_V1.md) I0. Inventory: step 45 · KC-C-PROFILE-POLISH. AGENTS.md Architecture impact.

This pass answers: **how Profile's sky-facing LLM (Natal Decode) uses IL-4 consume** without making CE the astrology SoT or rewriting IL lemmas.

Catalog **38 draft / 0 `active`**. Unchanged.

---

## Architecture impact

- **SoT before:** Today polish 1.3.114 bound native `interpretive_chorus.astrology` to IL-4. Live Profile is Character Engine (`CHARACTER_ENGINE_PUBLISH_READY=1`); legacy `profile_contract_v1` oneshot with IL-4 never runs. Natal Decode Depth still asked the model to invent sky meaning from compact `natal_pack` facts (signs/houses/angles) with Identity Core fixed — parallel astrology beside IL-4, same defect Today had on the chorus.
- **SoT after:** **Profile Meaning Polish V1** binds Natal Decode `pattern_thesis` / `section.thesis` to IL-4 lemmas when a pack is present (cached natal geometry → existing attach gateway, surface=`profile`). System adds `PROFILE_IL4_DECODE`; consume `IL4_MEANING` + reject-invalid; empty theses may fill from pack primary `text` only. Identity Core / `because_core` stay CE. `day_hooks` stay now-gestures. Public natal-decode JSON unchanged (no `il4_expression_pack` on the artifact). Consume 1.3.113 and Today polish 1.3.114 stand.
- **Public contract changed?** no — polish is LLM input / editorial gate only
- **Migration required?** no — next explicit POST after `natal_decode_depth_v0.3` fingerprint miss; cached v0.2 artifacts stay until that POST
- **Canon updated?** yes — this file · IL §6.71 · inventory KC-C-PROFILE-POLISH + step 45 · natal decode · handoff · tracker
- **Backward compatible?** yes — missing geometry → previous decode path

---

## 0. Contract

| Rule | Do | Do not |
|------|----|--------|
| Sky theses | Phrase IL4_MEANING lemmas / construction | Invent new sky meaning from `natal_pack` beside the pack |
| Identity Core | Keep CE `thesis_key` / `surface_text` | Overwrite portrait; inject IL-4 into CE / personality_v1 |
| `because_core` | Link section → CE core | Replace IL-4 meaning or fill from pack |
| `day_hooks` | Moves for now | Replace with IL-4 plot |
| Fill | Empty `pattern_thesis` / `section.thesis` only | Overwrite valid LLM prose |
| Reject | Missing theses when pack has lines | Scrub phrasing because lemmas are English |
| Surfaces | Natal Decode Depth only | CE cascade · personality_v1 · Today native · first-paint Profile |

`services/profile_meaning_polish_v1.py` does **not** import calc wire or consume internals beyond `pack_present` / `fill_empty_slot`.

---

## 1. Hook

| Step | Location |
|------|----------|
| Attach | `natal_decode_depth_v0` via `il4_surface_attach_v1` (cached natal chart · surface=`profile`) |
| System augment | consume + `PROFILE_IL4_DECODE` after persona |
| Protected prefix | `IL4_MEANING` on the user message |
| Reject-invalid | consume + empty theses, before persist |
| Fill-empty | after normalize, empty theses only |

Prompt version: `profile.natal_decode_depth.v1` **1.1.0**. Decode artifact version: `natal_decode_depth_v0.3` (fingerprint).

---

## 2. This pass does not do

- Public JSON · set `active` · lemma rewrite · IL engine reopen
- CE / personality_v1 astrology inject · identity_core fill from pack
- Hard overwrite of filled slots · Relevance / Prioritization
- Today native polish reopen (1.3.114 stands)
- Deploy / merge to `main` without owner
- Frontend chrome (login / scroll / Practices)

---

## Changelog

- **1.0 (2026-08-25)** — 1.3.123. Natal Decode binds sky theses to IL-4 packs. Public contracts unchanged.
