# Character Engine — Schema Contracts v0

**Status:** DRAFT — identity/provenance-first schema (не prose catalog)  
**Version:** 0.2 (2026-07-25)  
**Parents:** [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) (D1–D4 ACCEPTED) · [CHARACTER_ENGINE_RUNTIME_INVENTORY_V0.md](./CHARACTER_ENGINE_RUNTIME_INVENTORY_V0.md) · [PROFILE_EXPERIENCE_SCENARIO_V1.md](../profile/PROFILE_EXPERIENCE_SCENARIO_V1.md)  
**Home:** `core_profile_snapshots.payload.character_engine_v1`  
**Machine schema:** [character_engine_v1.schema.json](../schemas/character_engine_v1.schema.json) · validate `scripts/validate_character_engine_contract.py` · ids `services/character_engine_ids_v0.py`  
**CI note:** job `character-engine-schema` prepared in local `.github/workflows/ci.yml` but not pushed (OAuth lacks `workflow` scope) — run validator locally / add job with workflow-capable token.

### Out of scope (explicit)

- финальная Profile prose / editorial catalog  
- UI taxonomy · Freeze rows  
- новые life-area сущности как корни  
- отдельные схемы Relationships / Career / Money  
- полные downstream Experience schemas  

### In scope (order)

1. Envelope + обязательные секции каскада  
2. Raw Fact reference  
3. Evidence Graph (claims · typed edges · provenance · capability)  
4. Stage artifacts + validation boundaries  
5. Deterministic Compass  
6. Legacy adapter map  
7. Shadow diagnostics  

**Главный риск этого трека:** стабильность идентификаторов. `fact_id` · `claim_id` · stage ownership · adapter refs должны переживать повторную генерацию и **не** зависеть от текста LLM.

---

## 0. Version axes (разделены жёстко)

| Axis | Field / artifact | Меняется когда |
|------|------------------|----------------|
| **Snapshot contract** | `character_engine_v1` (`schema_version`) | Ломается/расширяется публичная структура nest |
| **Generation recipe** | `character_engine_recipe_v1` (`recipe_version`) | Меняется порядок/границы стадий, не обязательно JSON shape |
| **Stage prompt IDs** | e.g. `profile.character_engine.stage2.v1` | Меняется формулировка/модель стадии |
| **Projection adapter** | `character_engine_adapter_v1` (`adapter_version`) | Меняется map legacy ← CE без смены CE schema |

Invariant: смена prompt **не** требует нового `schema_version`. Смена `schema_version` **не** обязана менять prompt.

---

## 1. Identity & provenance rules (SoT этого документа)

### 1.1 Stable IDs

| ID | Scope | Stability rule |
|----|-------|----------------|
| `fact_id` | Raw fact | Детерминирован от `(fact_type, normalized_key, calc_authority, calc_version)` — **не** от LLM prose |
| `claim_id` | Claim | Детерминирован от `(claim_kind, normalized_thesis_key, primary_fact_ids_fingerprint)` — thesis_key = нормализованный код/слот, **не** surface sentence |
| `edge_id` | Evidence edge | Детерминирован от `(fact_id, claim_id, edge_type)` |
| `section_ref` | Cascade section | Fixed enum: `identity_core` · `source_roles` · `internal_engine` · `primary_tension` · `secondary_tensions` · `scenes` · `potential` · `blind_spots` · `compass` · `life_path` |
| `scene_id` | Life scene | Детерминирован от `(scene_kind, tension_or_mechanism_ref)` — kinds = situation codes, не UI labels |
| `adapter_field` | Legacy DTO key | Stable string matching today’s public fields (`relationship_style`, …) |

**Запрещено:**

- `fact_id` / `claim_id` = hash от русского/английского абзаца LLM  
- новые ID при каждом regen при тех же facts + том же normalized thesis key  
- UI copy как часть identity fingerprint  

**Разрешено:**

- `surface_text` / `prose` рядом с ID — ephemeral для человека; regen может менять wording при том же `claim_id`  
- `content_hash` отдельно от identity (для cache/diff), если нужен  

### 1.2 Ownership

| Object | Owner stage | Downstream may |
|--------|-------------|----------------|
| Raw facts | Stage 0 | read only |
| Evidence Graph | Stage 1 | Stage 2+ cite; Stage 3+ **cannot** invent new facts |
| Identity core (one) | Stage 2 | Stage 3–6 explain/project; **cannot rewrite core** |
| Internal Engine · tensions | Stage 3 | Stage 4–5 derive; cannot change core |
| Scenes · potential · blind spots | Stage 4 | Stage 5–6 project |
| Compass · adapters · matrix | Stage 5 | Stage 6 render only |
| Narrative projection | Stage 6 | no new claims |

### 1.3 Provenance minimum

Каждый claim и каждая cascade section, видимая readers, обязана иметь:

- `claim_ids[]` или `section_ref`  
- `supporting_fact_ids[]` (может быть empty только с explicit `evidence_status=insufficient`)  
- `produced_by_stage`  
- `recipe_version` · `prompt_id` (если LLM stage)  
- `confidence` · `capability_floor`  

---

## 2. Envelope — `character_engine_v1`

Публичный nest внутри Snapshot payload.

```text
character_engine_v1
├── schema_version: "character_engine_v1"
├── recipe_version: "character_engine_recipe_v1"
├── status: ready | forming | failed   # forming = envelope only, no partial CE body as SoT
├── profile_fingerprint: string        # same family as today’s profile_hash inputs
├── input_fact_set_version: string
├── calc_authority: { swiss: semver|hash, numerology: …, catalogs: … }
├── capability: { … }                  # floor for house/ASC claims
├── generated_at: iso8601
├── raw_facts: RawFact[]               # or refs into shared fact pack — see §3
├── evidence: EvidenceGraph            # §4
├── cascade: CascadeSections           # §2.1 — required keys
├── compass: CompassV1                 # §6 — deterministic
├── legacy_projections: LegacyMap      # §7 — adapters; optional after cutover once readers migrate
├── diagnostics?: { shadow?: ShadowReport }  # §8 — never SoT
└── meta: { adapter_version, stage_prompt_ids, validation_report_id? }
```

### 2.1 Required cascade sections

| Key | Cardinality | Validation |
|-----|-------------|------------|
| `identity_core` | exactly 1 claim-backed logline object | reject multi-core / trait lists |
| `source_roles` | 0..N role bindings | each role → `fact_ids` + contribution claim |
| `internal_engine` | fixed mechanism slots (codes) | no core rewrite |
| `primary_tension` | exactly 1 | required if status=ready |
| `secondary_tensions` | 0..3 | must not equal primary weight |
| `scenes` | 1..N situation scenes | keyed by `scene_kind`, not career/love roots |
| `potential` | 1 growth-direction object | derived from engine+tension |
| `blind_spots` | 0..N | patterns, not flaw list |
| `life_path` | 0..1 finale path object | optional until Stage 6 runs |

Prose fields inside sections are **payload**, not identity. Schema validators gate structure + ID refs first.

### 2.2 Forming / failed

| status | `cascade` / `evidence` | Allowed |
|--------|------------------------|---------|
| `forming` | omit or empty shell | UX retry only; **no** half identity + half old portrait |
| `failed` | omit | error + retry metadata |
| `ready` | full required sections | publish |

---

## 3. Raw Fact reference contract

```text
RawFact
├── fact_id: FactId
├── fact_type: enum|string code   # sun_longitude, house_cusp_7, life_path_number, …
├── value: json                   # normalized machine value
├── display_key?: string          # optional human key, not identity
├── authority: swiss | deterministic_numerology | catalog | bridge_natal_facts_llm
├── calc_version: string
├── capability_required: date_only | full_natal | name | …
├── confidence: high | medium | low
├── provenance: { source_system, input_fingerprint, computed_at }
└── unavailable_reason?: string   # if fact expected but missing
```

### Rules

1. Compute authority: Swiss / deterministic > catalog > LLM bridge.  
2. `authority=bridge_natal_facts_llm` **forbidden** for angles/houses/positions once Swiss pack present for that key.  
3. Missing house/ASC → fact absent + capability, not invented RawFact.  
4. Facts pack may live inside CE or be referenced from `cached_natal_charts` / shared fact store — **IDs must still be stable and shared** with Evidence Graph.

---

## 4. Evidence Graph

```text
EvidenceGraph
├── schema_version: "evidence_graph_v1"
├── claims: Claim[]
└── edges: EvidenceEdge[]
```

### Claim

```text
Claim
├── claim_id
├── claim_kind: code   # autonomy_need, analysis_first, intimacy_independence_tension, …
├── thesis_key: code   # stable; language-agnostic
├── surface_text?: string   # optional; regen-ok
├── cascade_role: section_ref | mechanism_slot | scene_kind
├── supporting_fact_ids: FactId[]
├── contradicting_fact_ids?: FactId[]
├── confidence
├── capability_floor
├── produced_by_stage: 1|2|3|4
├── evidence_status: grounded | insufficient | excluded
└── exclusion_reason?: string
```

### EvidenceEdge

```text
EvidenceEdge
├── edge_id
├── fact_id
├── claim_id
├── edge_type: supports | strengthens | qualifies | contradicts | limits | contextualizes
└── note_key?: code   # optional machine note, not essay
```

### Forbidden in Evidence Graph

UI paragraphs · planet encyclopedia · Compass advice · duplicate paraphrase claims with new IDs.

---

## 5. Stage artifacts & validation boundaries

Internal (may be ephemeral during publish; not public SoT unless embedded in CE ready payload).

| Stage | Artifact | May write | Must not |
|-------|----------|-----------|----------|
| 0 | `facts_pack` | RawFacts · capability · missing | personality claims |
| 1 | `evidence_candidates` | Claims · Edges | identity_core · Compass · scenes |
| 2 | `identity_bundle` | one core · source_roles | multiple cores · trait laundry lists |
| 3 | `engine_bundle` | mechanisms · tensions | mutate identity_core |
| 4 | `life_bundle` | scenes · potential · blind_spots | invent unrelated career/love essays |
| 5 | `assembly_bundle` | Compass · legacy_projections · matrix refs | LLM calls · new claims |
| 6 | `narrative_projection` | path prose refs to existing claims | new claim_ids |

### Validation gates (publish)

1. `status=ready` ⇒ exactly one `identity_core`; primary_tension present.  
2. Every ready claim with `evidence_status=grounded` has ≥1 supporting fact_id existing in raw_facts.  
3. No Stage 3+ object references unknown claim_id.  
4. Compass fields only reference claim_ids / mechanism slots / scene_ids from cascade.  
5. Legacy adapter outputs cite `source_refs` into CE (claim/scene/compass keys).  
6. House/ASC-dependent claims require `capability` full natal.  
7. Reject dual portrait markers: non-empty independently generated `interpretation.life_areas` alongside CE ready (post-cutover).

---

## 6. Deterministic Compass contract

```text
CompassV1
├── schema_version: "compass_v1"
├── assembler_version: string    # part of adapter/recipe family; no LLM
├── items: CompassItem[]
└── source_refs: { claim_ids[], scene_ids[], mechanism_slots[] }
```

```text
CompassItem
├── item_id          # deterministic from (item_kind, source_refs fingerprint)
├── item_kind: best_conditions | work_style | communication_style | learning_style
│            | energy_sources | recovery | ideal_environment | triggers
│            | red_flags | strengths | growth_directions | …
├── value: string | string[]     # assembled text or codes
└── derived_from: refs
```

**No** `prompt_id` on Compass. Stage 5 only.

---

## 7. Legacy adapter map

```text
LegacyMap
├── adapter_version: "character_engine_adapter_v1"
├── fields: {
│     identity_core?: AdapterOut
│     recognition_line?: AdapterOut
│     decision_style?: AdapterOut
│     emotional_style?: AdapterOut
│     relationship_style?: AdapterOut
│     work_and_realization?: AdapterOut
│     money_patterns?: AdapterOut
│     strengths?: AdapterOut
│     growth_zones?: AdapterOut
│     blind_spots?: AdapterOut
│     helps?: AdapterOut
│     life_spheres?: AdapterOut
│     interpretation_life_areas?: AdapterOut   # deprecated DTO
│     …
│   }
```

```text
AdapterOut
├── value: json
├── source_refs: { claim_ids[], scene_ids[], compass_item_ids[] }
└── omit_reason?: string
```

Rules: pure functions of CE · no LLM · no new claims · no zodiac encyclopedia fill · versioned assembler.

Transitional: `profile_contract_v1` may be filled **only** from `LegacyMap` after CE cutover for that snapshot.

---

## 8. Shadow diagnostics contract

```text
ShadowReport
├── schema_version: "ce_shadow_v1"
├── compared_at
├── legacy_recipe: { prompt_ids[], snapshot_fingerprint? }
├── ce_recipe_version
├── metrics: {
│     semantic_overlap?
│     contradictions: [...]
│     unsupported_claims: claim_id[]
│     missing_useful: code[]
│     regen_stability?
│     reader_completeness?
│     capability_violations: [...]
│   }
├── samples?: { field, legacy_excerpt?, ce_ref }[]   # optional, not SoT
└── recommendation: hold | cutover_ready | block
```

Storage: `character_engine_v1.diagnostics.shadow` and/or `generation_logs` diagnostics module — **never** merged into cascade/Compass as authority.

---

## 9. Scene kinds (codes, не UI spheres)

Situation codes for `scene_id` / `scenes[].scene_kind` (extensible enum):

`responsibility` · `intimacy` · `risk` · `success` · `uncertainty` · `competition` · `recovery_context` · `learning_pressure` · …

UI may **group** scenes under work/love/money labels via adapter — labels are not schema roots.

---

## 10. Acceptance for this schema draft

1. Can regenerate Stage 2–4 prose and keep the same `claim_id`s when thesis_key + facts unchanged?  
2. Can adapter rebuild `relationship_style` from scene/claim refs alone?  
3. Can Shadow run without writing legacy into SoT?  
4. Is Compass free of prompt_id?  
5. Are version axes independently bumpable?  

If no → fix identity rules before implementing pipeline.

---

## 11. Next after acceptance of v0.1

1. ~~Machine-readable JSON Schema~~ → `docs/schemas/character_engine_v1.schema.json` + fixtures + `scripts/validate_character_engine_contract.py`.  
2. ~~ID stability module/tests~~ → `character_engine_ids_v0.py` + `test_character_engine_ids_v0.py`.  
3. Land CI job `character-engine-schema` (needs `workflow` scope on push).  
4. Implement Stage 0–1 fact+evidence builders (deterministic-first).  
5. Wire Stage 2–4 behind flag with ID stability tests on publish.  
6. Stage 5 adapters → fill `profile_contract_v1` from CE only.  
7. Shadow harness.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-25 | v0.1 — identity/provenance-first schema; envelope · facts · evidence · stages · compass · adapters · shadow; no prose/UI catalog |
| 2026-07-25 | v0.2 — JSON Schema + fixtures + `character_engine_ids_v0` + CI validate script |
