# IL-4 Surface Attach V1

**Date:** 2026-08-23  
**Status:** **LOCKED** — product surfaces read IL-4 packs on LLM input. **Not** public JSON. **Not** Today prompts as meaning SoT. **Not** `active`. **Not** freeze / IL-2 / IL-3 / IL-4 / wire reopen. **Not** user relevance.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) Sequence · §6.66 · §7. Inventory: step 40 · KC-C-ATTACH. Wire: [CALC_IL_WIRE_V1.md](./CALC_IL_WIRE_V1.md). Expression: [IL4_EXPRESSION_V1.md](./IL4_EXPRESSION_V1.md). Boundary: [IL1_HANDOFF.md](./IL1_HANDOFF.md) §3 · §5. AGENTS.md Architecture impact.

This pass answers: **where product surfaces read IL-4 packs.** Meaning still comes from stored lemmas + IL-2/3. IL-4 voices. LLM may phrase; it does not choose Saturn □ Venus. Today prompts stay editorial / transport; they are not meaning SoT.

Catalog **38 draft / 0 `active`**. Unchanged. Draft catalog consumed through the wire.

---

## Architecture impact

- **SoT before:** Calc → IL wire (1.3.111) was live at the library layer only. Today / Profile / Compatibility LLM inputs ignored IL-4. Today meaning polish stayed PAUSED.
- **SoT after:** **IL-4 Surface Attach V1** is the product gateway. `services/il4_surface_attach_v1.py` resolves chart snapshots → `wire_calc_to_il(surface)` → serializes `il4_expression_pack` onto **internal LLM payloads** for Today (`day_story_wire_v1`), Profile (`profile_contract_v1`), and Compatibility (`compatibility_llm` when charts are supplied). Public contracts unchanged. Freeze, IL-2, IL-3, IL-4 engine, and wire stand.
- **Public contract changed?** no — `il4_expression_pack` is LLM input / trace only
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.66 · inventory KC-C-ATTACH + step 40 · handoff §3 · tracker NOW
- **Backward compatible?** yes — missing geometry → omit pack (no invented meaning)

---

## 0. Gateway (single product import)

| Module | Role |
|--------|------|
| `knowledge/calc_il_wire_v1.py` | Library wire (unchanged 1.3.111) |
| `services/il4_surface_attach_v1.py` | **Only** product module that imports the wire |

`runtime_is_not_wired()` allows `calc_il_wire_v1` **only** in the attach gateway. Other services import the gateway, not IL engines directly.

---

## 1. Surfaces

| Surface | Hook | Chart source | IL-4 surface |
|---------|------|--------------|--------------|
| Today | `day_story_wire_v1` → `llm_input["il4_expression_pack"]` | `celestial_events.ephemeris` natal + transit_noon | `today` (primary theme only) |
| Profile | `profile_contract_v1` → `llm_pack["il4_expression_pack"]` | `profile_input.natal` positions/houses | `profile` (full rank) |
| Compatibility | `compatibility_llm` + synastry `generate_compatibility_editorial` when charts passed | chart1 natal · chart2 as transit band | `compatibility` (full rank) |

Compatibility maps partner chart → transit geometry for `transit_to_natal` / `transit_through_house` (wire 1.3.111). Not synastry cookbook prose.

---

## 2. This pass does not do

- Public JSON fields on `today_contract_v1` / `profile_contract_v1` / `compatibility_contract_v1`
- Set `active` · lemma rewrite · IL engine reopen
- Today prompts as meaning SoT · Relevance / Prioritization
- Swiss inside attach gateway (charts resolved upstream)
- Deploy / merge to `main` without owner

Today *meaning polish* may resume as an **owner-directed** pass after consume 1.3.113. This attach file does not reopen.

---

## Changelog

- **1.2 (2026-08-25)** — Profile meaning polish 1.3.123: natal decode is an attach consumer. This attach stands.
- **1.1 (2026-08-23)** — Editorial consume done 1.3.113. This attach stands.
- **1.0 (2026-08-23)** — 1.3.112. Product surfaces read IL-4 packs on LLM input. Public contracts unchanged.
