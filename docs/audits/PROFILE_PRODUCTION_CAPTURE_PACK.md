# Profile Production-Faithful Capture Pack

**Status:** IMPLEMENTATION — infra only  
**Parent:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Passport:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Date:** 2026-07-21

> Capture around the production path. Do **not** change prompts, Today-frame, Profile UI, Snapshot content, tier rules, or product logic until packs prove the architectural defect class.
>
> **Нет класса `MODEL`.** Несоответствие = дефект нашей цепочки.

---

## Goal

Для **каждого** блока pack должен доказать четыре вещи:

1. Блок **имел право** быть создан (`block_eligibility` / generation gate).  
2. Промпт **точно** описывал требуемый результат.  
3. Ответ **соответствует контракту** (иначе — `PROMPT` / `RESPONSE_SCHEMA` / `VALIDATION` / `INPUT`, не «модель»).  
4. **Именно этот** ответ без изменений дошёл до UI.

Трасса claim:

```text
claim → origin → raw → accepted → Snapshot → API → UI
```

### Defect classes (architectural only)

```text
BLOCK_PURPOSE
INSUFFICIENT_DATA
INPUT
PROMPT
RESPONSE_SCHEMA
VALIDATION
GENERATION_GATE
SNAPSHOT
API
PROJECTION
UI_GATE
```

**Запрещено:** `MODEL`, «модель выдумала», «LLM hallucinated» как финальный диагноз.

---

## What this PR ships

| Piece | Path |
|-------|------|
| Capture session (ContextVar, off by default) | `backend/.../profile_capture_session_v0.py` |
| Funnel adapter (records each attempt: prompt/raw/parse/validation) | `profile_disclosure_funnel_v0.py` |
| Portrait quality hook | `profile_contract_v1.build_profile_portrait_v1` |
| Publisher hook (snapshot + GET body when capture on) | `core_profile._publish_portrait` |
| CLI harness (Case A/B) | `backend/evals/profile_quality/run_production_capture_v0.py` |
| FE QuickMap / visible_blocks | `frontend/.../profileCaptureProjectionHarness.ts` + `scripts/run_profile_capture_projection.mjs` |

**Not shipped:** prompt edits, UI edits, generation gates in production (only *recorded* as defects / eligibility).

---

## Pack schema (one JSON)

```text
manifest
inputs
calculated_facts
source_depth
missing_fields
allowed_claims
block_eligibility.{identity,styles,patterns,spheres}
  may_generate, reason, min_source_depth, ran
steps.{identity,styles,patterns,spheres}.attempts[]
  system_prompt, user_prompt, model_request,
  raw_response, parsed_response, validation_result
final_contract_before_quality
quality_validation
final_contract_after_quality
snapshot_written
core_profile_get_response
frontend_projection
visible_blocks
claim_trace
defects[]
generation_metadata
divergences[]
```

---

## Production-faithful rules

Harness **must** call the real production path (prompt builder, policy, validators, portrait, QuickMap).  
**Must not** re-implement the funnel in eval code. SoT = `run_production_capture_v0.py`.

---

## Safety

- Capture **off by default**
- Sidecars under `evals/profile_quality/runs/capture_*` only
- Personal prompts/raw **not** in `generation_logs`
- `--redact` for name / date / geo
- Do not commit unredacted PII packs

---

## Cases (mandatory)

| Alias | Scenario | Depth | Patterns eligibility (target) |
|-------|----------|-------|-------------------------------|
| A / `pq-001` | Аня birth-only | `birth_data_only` | **must not generate** confirmed patterns |
| B / `pq-007` | Катя check-ins + living | `profile_plus_checkins` | may generate; must use living |

---

## Formalized defect (patterns) — architectural framing

```text
Wrong framing:
  «Модель выдумала recurring patterns при birth_data_only»

Right framing:
  Block = confirmed behavioral repeats only
  → requires longitudinal / living evidence
  → if absent, GENERATION must not run

Current production conflict (prove in pack):
  generation_gate should be CLOSED at birth_data_only
  but funnel always calls patterns
  and RESPONSE_SCHEMA / _patterns_ok require filled patterns + living_changes
  → GENERATION_GATE + RESPONSE_SCHEMA
```

**Do not product-fix in the capture PR** — packs first, then gate/schema until Case A never runs patterns.

---

## How to run

```bash
cd backend
python evals/profile_quality/run_production_capture_v0.py --cases A,B
python evals/profile_quality/run_production_capture_v0.py --cases A,B --redact
python evals/profile_quality/run_production_capture_v0.py --cases A --skip-fe
```

---

## DoD checklist

1. Production entry with capture mode  
2. Pack records what production **actually** ran (including wrongful generation)  
3. `block_eligibility` vs `ran` per step  
4. Attempts + reject reasons  
5. Snapshot + GET body  
6. QuickMap + visible_blocks  
7. Capture off → no user-facing change; no personal raw in generation_logs  
8. Case A + Case B  
9. Divergences = architectural classes only  

---

## Out of scope (after packs)

Gate off patterns without living · rewrite prompts · Screen Master · ad-hoc FE hides · trial/sub · new contract

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Capture harness + Case A/B CLI + FE projection |
| 2026-07-21 | Removed MODEL; eligibility + 4 proofs; patterns = GENERATION_GATE |
