# Native C1 Evidence Pack Binding V1

**Date:** 2026-08-24  
**Status:** **LOCKED** — close `unknown_evidence` on thin / no-profile Global by binding cite ids to the packs the LLM already sees. **Not** editorial calibration. **Not** I0 split reopen. **Not** IL-4. **Not** gate weakening. **Not** `active`.  
**Canon:** [NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1](./NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md) · [NATIVE_C1_I0_GENERATION_SPLIT_V1](./NATIVE_C1_I0_GENERATION_SPLIT_V1.md) · [DAY_SCENARIO_GATE_MATURITY_C36](../audits/DAY_SCENARIO_GATE_MATURITY_C36.md)

---

## Architecture impact

- **SoT before:** `collect_allowed_evidence_ids` took interpretation `evidence` / `derived_claims` plus **dict** event rows. `ranked_drivers` / `ambient` as strings were skipped. Foundation beats live on `daily_foundation` / `day_foundation`; the model cites nest paths (`ev.foundation.lunar.{beat_id}`). Interpretation evidence uses `ev.claim.foundation.{layer}.{beat_id}`. Mismatch → hard `unknown_evidence` → `unavailable_after_llm` (prod gen **1092**, user 4, no profile).
- **SoT after:** **Native C1 Evidence Pack Binding V1** — allowlist = events pack (string ids + dicts) ∪ foundation beat aliases ∪ interpretation evidence ∪ personalization pack refs. `DRAMATURGY_BRIEF.allowed_evidence_ids` lists canonical ids. `unknown_evidence` retry names that list. Gate still rejects invented ids (`invented-planet-42`). Prompt stays `day-scenario-native-c5.1`. Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — `force` rebuild / refresh picks up binding
- **Canon updated?** yes — this file · tracker 1.3.118
- **Backward compatible?** yes — same `unknown_evidence:` hard marker; larger closed set only

---

## Problem (production gen 1092)

```
unknown_evidence:conflict:ev.foundation.lunar.aspect.sky-moon-opposition-mars
unknown_evidence:conflict:ev.foundation.lunar.ingress.Moon
unknown_evidence:scene[0]:…
unknown_evidence:scene[1]:…
```

Those ids are lunar beat paths from `daily_foundation` (`beat_id` = `aspect.{event}` / `ingress.Moon`). They were on CONTEXT, not on the allowlist.

This is pack binding, not scene/astro editorial quality.

---

## Contract

| Cite source | Allowed forms |
|-------------|----------------|
| Events pack | `id`; `ranked_drivers` / `ambient` **strings**; `ev.driver.{id}` |
| Foundation beats | `{beat_id}`; `claim.foundation.{layer}.{beat_id}`; `ev.claim.…`; **`ev.foundation.{layer}.{beat_id}`**; `foundation.{layer}.{beat_id}`; `evidence_ref` |
| Interpretation | `evidence[].id`; `derived_claims[].id` / `evidence_ids` |
| Ritual | `day_card` · `day_number` · `tarot:` / `number:` |
| Personal pack | `pack_allowed_refs` + sphere_selection `evidence_refs` (Personal stage) |
| Chorus tokens | `astrology` · `natal` · `conflict` · `day_card` · `day_number` |

**Still reject:** ids not in that closed set. Do not drop `unknown_evidence` from `HARD_NATIVE_VALIDATE_MARKERS`.

**Brief:** `allowed_evidence_ids` = canonical subset (must_dramatize + pack/ritual tokens). Path aliases stay validate-only so the model is not taught to emit them.

---

## Out of scope

- Reopen I0 / `GLOBAL_LOCKED` / IL-4 attach/consume/polish
- Weaken C3.1 editorial gates
- Post-LLM overwrite of meaning slots
- GET `/today/contract` auto-rebuild on cached `unavailable` (assemble-once)

## Cached unavailable shells

GET `/today/contract` uses `allow_rebuild_on_miss=False`. A fingerprint-matched `unavailable_after_llm` shell stays until:

```bash
POST /today/story/refresh  {"force": true, "timezone": "Europe/Berlin"}
# or ops:
python backend/scripts/list_unavailable_native_shells_v1.py --days 2
python backend/scripts/native_c1_regression_matrix_v1.py --user-id 4 --date YYYY-MM-DD
```

Do not invent story text on GET.

---

## Tests

`backend/tests/test_native_c1_evidence_pack_binding_v1.py` — gen 1092 aliases PASS; invented id FAIL; string `ranked_drivers` collected.
