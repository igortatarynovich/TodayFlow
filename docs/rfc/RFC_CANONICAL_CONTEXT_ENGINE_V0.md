# RFC — Canonical Context Engine v0 (P5)

**Status:** DRAFT · ready for first-slice implementation  
**Date:** 2026-07-21  
**Stage after:** life_spheres synthesis wire (`ad7b919`)  
**Canon:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md) · [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Related:** [DAY_CONTEXT_V0.md](../DAY_CONTEXT_V0.md) · [RFC_DAILY_STATE_V0.md](./RFC_DAILY_STATE_V0.md) · [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](../audits/PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md) · [PERSONAL_INTELLIGENCE_LAYER.md](../PERSONAL_INTELLIGENCE_LAYER.md)  
**First slice passport:** [CONTEXT_ENGINE_P5_FIRST_SLICE.md](../audits/CONTEXT_ENGINE_P5_FIRST_SLICE.md)

> Stop thinking only in `life_spheres`.  
> Spheres proved the pattern. P5 makes it **product infrastructure**.

---

## 0. Goal

One mechanism for the whole of TodayFlow:

```text
Foundations
  → Calculated Facts (registry)
  → Context Builder (question → relevant facts → prepared cues)
  → Prompt (clear job)
  → Validation
  → Snapshot (facts + context version + generated block)
```

Adding a new block becomes three things only:

1. What question does the user have?  
2. Which facts are relevant (and eligible)?  
3. One quality prompt.

Everything else — selection, validation, Snapshot kitchen — is shared.

---

## 1. Kickoff decisions (must lock)

### K1. Three layers — never mix

| Layer | Owns | Examples |
|-------|------|----------|
| **facts** | Already calculated / confirmed atoms | `natal.venus_sign`, `style.relationship`, `living.checkin_streak` |
| **context** | Selected + rendered pack for one question | `ContextPack` with cue texts, no kitchen astrology in user message |
| **generation** | Prompt output after validation | sphere fields, day story, compatibility prose |

LLM does **not** re-interpret raw ephemeris.  
UI does **not** invent rules.  
DayContext / DailyState remain day-scoped consumers of the same fact layer — not a second registry.

### K2. Fact atom contract

Every fact in the registry:

| Field | Meaning |
|-------|---------|
| `id` | Stable string, e.g. `natal.venus.sign`, `profile.style.relationship` |
| `domain` | Meaning bucket: `relationships`, `money`, `decisions`, `energy`, … |
| `source` | Where it came from (`natal_calc`, `profile_funnel`, `living`, …) |
| `value` | Typed payload (sign, text, number, struct) |
| `confidence` | `high` · `medium` · `low` · `unknown` |
| `eligibility` | May this fact be shown / used for this user now? |
| `dependencies` | Fact ids that must be present (e.g. houses need birth time) |
| `calculation_version` | When computed by code |
| `limitations` | Honest bounds (e.g. sun-only scenario) |

No fact → no cue from that atom. Missing dependency → omit atom (Product Truth First).

### K3. Context Builder answers a question — not “give Venus”

Prompt authors declare:

```text
question_id: q.relationships.v1
```

Builder selects eligible facts (identity, venus/moon cues, 7H if available, relationship_style, living/patterns if eligible) and renders **prepared cues** (behavioral text). Kitchen may retain planet/sign used to build cues.

### K4. Surfaces share the engine

Profile · Today · Compatibility · Tarot · Chat / companion — same Context Builder + Prompt Registry pattern.  
Surface-specific: question_id, prompt_id, validator, Snapshot field.  
Shared: facts registry, selection, fingerprint, eligibility gates.

### K5. Snapshot stores product truth, not raw astrology homework

```text
Snapshot block kitchen:
  fact_ids[]
  context_version
  context_fingerprint
  prompt_id + prompt_version
  generated payload (validated)
```

User-facing copy never requires planet names. Kitchen always reconstructible.

### K6. No phrase-table content engine

Hand-authored `planet × sign × field` user copy is **not** the product path.  
Deterministic code may build **cues** and **gates**. Prose = prompt synthesis (or omit).

---

## 2. Domains (v0 catalog — extend, don’t freeze product UI)

Meaning domains for registry layout (not 1:1 with Profile sphere chrome):

| domain_id | Intent |
|-----------|--------|
| `identity` | Who / strengths / growth |
| `relationships` | Closeness, partnership |
| `money` | Value, resource |
| `career` | Work, visibility |
| `communication` | Speech, mercury-mode |
| `energy` | Body / load / recovery |
| `stress` | Pressure patterns |
| `decision_making` | Choice hygiene |
| `learning` | Growth, study |
| `purpose` | Direction / mission (gated) |
| `daily_transits` | Day sky facts |
| `compatibility` | Dyad facts |
| `living` | Check-ins, longitudinal |

Spheres `love` / `money` / `decisions` map onto `relationships` / `money` / `decision_making` — they are **questions**, not the registry taxonomy.

---

## 3. Pipeline (canonical)

```text
1. Foundations available for user (birth, styles, living, …)
2. Materialize / refresh Calculated Facts → Fact Registry view
3. Resolve question_id (+ locale, surface)
4. Context Builder:
     - load QuestionSpec (relevant fact ids, gates, prompt_id)
     - filter by eligibility / dependencies
     - render Cue[] (behavioral)
     - emit ContextPack + fingerprint
5. Prompt Registry → system + user message from ContextPack
6. LLM → JSON/text
7. Validator (schema + bans + cue grounding)
8. Snapshot merge: validated block + kitchen
```

Fail at 4–7 ⇒ omit block / partial — never fill with fake personal copy.

---

## 4. Relation to existing systems

| Existing | Role after P5 |
|----------|----------------|
| `life_spheres_cues_v0` + synthesis | **First consumer** of QuestionSpec; migrate mapping into question registry |
| `life_spheres_projector_v0` | Cue/trait kitchen + A/B baseline — not user-copy SoT |
| `DayContext` | Day-scoped assembler; should **read** shared facts over time, not fork a second registry |
| `RFC_DAILY_STATE_V0` | Day evidence/interpretation/recommendations — facts layer feeds evidence |
| `profile_engine/selector.py` | Precursor topic→slice; converge toward QuestionSpec |
| `prompts/registry_v1.py` | Remains prompt_id SoT; Context Engine supplies user packs |
| Capture `calculated_facts` | Becomes a view over Fact Registry, not a one-off dict |

---

## 5. Non-goals (this RFC)

- Expanding Profile spheres beyond love/money/decisions  
- Replacing DayContext in one PR  
- Full UKM / Reference Layer merge  
- Chat companion product UI  
- New phrase tables

---

## 6. First slice (implementation gate)

See [CONTEXT_ENGINE_P5_FIRST_SLICE.md](../audits/CONTEXT_ENGINE_P5_FIRST_SLICE.md).

**Done when:**

1. RFC + first-slice passport accepted in repo.  
2. Shared types: FactAtom, Cue, QuestionSpec, ContextPack, fingerprint.  
3. Question registry v0 for `q.relationships.v1` · `q.money.v1` · `q.decisions.v1` (maps today’s spheres).  
4. `build_context_pack_v0(question_id, foundations)` used by spheres synthesis path (adapter OK).  
5. Kitchen on Snapshot/capture lists `fact_ids` / `context_fingerprint` for those three questions.  
6. No new spheres; no projector reinstated as copy SoT.

---

## 7. Later slices (ordered)

| Slice | Deliverable |
|-------|-------------|
| P5.1 | First slice (this) — question registry + ContextPack for three profile questions |
| P5.2 | Materialize natal FactAtoms from calc/cache (not sun-only scenarios) |
| P5.3 | Living/patterns fact atoms with eligibility (reuse patterns gate) |
| P5.4 | One Today surface question via same builder (read-only facts) |
| P5.5 | Compatibility question pack |
| P5.6 | Converge DayContext evidence onto registry view |

---

## 8. Acceptance (engine-level)

1. For any generated block: can answer “which fact ids fed this prompt?”  
2. House/ASC facts never enter ContextPack when `houses_available=false`.  
3. Patterns/living facts never enter when generation gate closed.  
4. Prompt never receives raw “Venus = Cancer” as sole homework — cues only.  
5. Fingerprint stable for same foundations + question_id.  
6. New block = QuestionSpec + prompt + validator — no new ad-hoc assembler.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | RFC opened after spheres synthesis wire; product formula promoted to engine |
