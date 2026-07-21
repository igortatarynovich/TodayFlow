# P5 First Slice — Canonical Context Engine (question → ContextPack)

**Status:** first slice **implemented** (types · question registry · ContextPack · synthesis adapter)  
**Date:** 2026-07-21  
**RFC:** [RFC_CANONICAL_CONTEXT_ENGINE_V0.md](../rfc/RFC_CANONICAL_CONTEXT_ENGINE_V0.md)  
**Proven precursor:** [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md) · wire `ad7b919`  
**Code:** `backend/src/todayflow_backend/context_engine_v0/` · tests `test_context_engine_v0.py`

> Do **not** add new life spheres.  
> Extract the shared pattern: question → eligible facts → prepared cues → ContextPack.

---

## 0. Passport

| Field | Value |
|-------|--------|
| `slice_id` | `context_engine_p5_first_slice_v0` |
| `purpose` | Make spheres synthesis the first consumer of a reusable Context Builder |
| `in_scope` | Types · question registry (3 questions) · `build_context_pack_v0` · fingerprint · adapter into synthesis runner |
| `out_of_scope` | New spheres · DayContext rewrite · living FactAtoms materialization · compatibility · chat |
| `appear_when` | Same natal-presence gate as spheres (`spheres_projection_allowed`) |
| `fail` | Empty ContextPack / omit question — never projector phrase tables |
| `code` | `backend/src/todayflow_backend/context_engine_v0/` |

---

## 1. Question registry (v0)

| question_id | Domain | Profile sphere_id (legacy chrome) | prompt_id | style fact | natal preference |
|-------------|--------|-----------------------------------|-----------|------------|------------------|
| `q.relationships.v1` | `relationships` | `love` | `profile.spheres.synthesis.v1` | `profile.style.relationship` | venus → sun; house 7 if eligible |
| `q.money.v1` | `money` | `money` | `profile.spheres.synthesis.v1` | `profile.style.money` | jupiter → saturn → sun; houses 2/8 |
| `q.decisions.v1` | `decision_making` | `decisions` | `profile.spheres.synthesis.v1` | `profile.style.decision` | saturn → mercury → sun; house 9 |

Each QuestionSpec also carries: `user_question`, `user_value`, required fact id prefixes, living/patterns optional ids (gated off in v0 pack unless eligible).

---

## 2. ContextPack shape

```text
{
  contract_version: "context_pack_v0",
  question_id,
  domain,
  locale,
  user_question, user_value,
  identity_core, strengths[], growth_zones[],
  relevant_style,
  cues: [{id, text, fact_ids[]}],
  house_cues: [{id, text, fact_ids[]}],
  fact_ids: [...],          # flat union used
  omitted_facts: [{id, reason}],
  context_version: "context_engine_v0.1",
  fingerprint: sha256(...)
}
```

Cue **text** = behavioral; kitchen `fact_ids` retain natal/style provenance.

---

## 3. Adapter rule

`synthesize_life_spheres_v0` may keep sphere_id loop for Snapshot chrome, but **must** build each sphere’s input via:

```text
question_id = SPHERE_TO_QUESTION[sphere_id]
pack = build_context_pack_v0(question_id, foundations)
→ format_synthesis_user_message(from ContextPack)
```

`life_spheres_cues_v0.build_sphere_cues` remains the cue renderer behind the builder (no duplicate cue tables in P5.1).

---

## 4. Acceptance

1. Unit tests: three question_ids produce ContextPack with non-empty cues when foundations valid.  
2. House cues empty when `houses_available=false`.  
3. Fingerprint stable for identical foundations.  
4. Synthesis runner kitchen includes `question_id`, `fact_ids`, `context_fingerprint`.  
5. Case A/B behavior unchanged in spirit: patterns skip ≠ spheres skip; fail ⇒ omit.  
6. No new sphere ids.

---

## 5. Next after this slice

P5.2 — materialize richer natal FactAtoms (Venus/Jupiter/…) from calc so scenarios are not sun-only.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | First slice opened with RFC |
