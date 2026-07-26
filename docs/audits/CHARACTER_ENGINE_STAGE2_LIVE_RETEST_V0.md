# Character Engine — Live Retest v0 (Stage 2 exit hold)

**Date:** 2026-07-26  
**Status:** **HOLD on Stage 3** — live diagnostics collected; exit criterion §1.4 not closed  
**Code / registry / architecture changed?** **No** (diagnostics-only retest)  
**Flags:** `STAGE01_SHADOW=1` · `STAGE2_SHADOW=1` · `PUBLISH_READY=0`  
**Prompt on server:** `profile.character_engine.stage2.v1` **1.1.0**  
**Parents:** [CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md](./CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md) · [CHARACTER_ENGINE_STAGE2_STAGING_EVAL_V0.md](./CHARACTER_ENGINE_STAGE2_STAGING_EVAL_V0.md) · canon [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0 §1.4](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md)

## Order (locked)

1. ~~Staging expand/calibrate~~  
2. **This doc — live retest + skim checklist**  
3. Owner confirms exit criterion → separate Stage 2 close-out audit  
4. Only then Stage 3  

Staging metrics alone do **not** satisfy §1.4.

## Sample

| | |
|--|--|
| Attempted users with settings | 7 |
| Usable packs | **6** |
| Build errors (outside CE) | 1 — user 19 `ChartResponse.positions` dict (pre-existing) |
| Full natal | 3 (Gemini, Aquarius, Pisces) |
| Date-only | 3 (Taurus lp=3 — same input family) |

## Aggregate checklist

| Criterion | Live result | Notes |
|-----------|-------------|--------|
| **Coverage** | Stage 1 nonempty on **6/6** usable | Gemini air_mind · Aquarius autonomy · Taurus earth · Pisces water_care + presence |
| **Diversity** | 4 unique Stage 1 claim-sets · 4 identity theses | Limited by tiny N and 3× Taurus clones |
| **Dominance** | max Stage 1 share **0.50** (`stability_through_earth`) · max identity share **0.50** | Borderline — driven by three near-identical Taurus packs, not one thesis across distinct charts |
| **Insufficient rate** | **0/6** | No empty Stage 1 on this sample (Leo-style negative not present live) |
| **Logline quality** | See skim below | RU · no «Вы» · no systemish · mix «Ты — человек…» / «Человек, который…» |
| **Repetition** | High among u20–22 | Same chart family → same thesis + similar earth-stability wording (expected) |
| **Traceability** | **0** contract-error packs | Grounded cores cite Stage 1 claim ids / facts in rationales |
| **Exit §1.4** | **OPEN — owner** | Staging success ≠ «one Identity Core can explain the later story» |

Voice counters (grounded): formal_vy=0 · systemish=0 · cyrillic=6/6.

## Pack skim (anonymized)

### u1 — Gemini full · `builds_through_air_mind`

- Stage 1: `direction_through_air_mind`, `presence_through_water_asc`
- Surface: путь через идеи/связи; ASC water as secondary color in prose  
- **§1.4 probe:** Can later tensions/scenes stay “manifestations of air-mind direction”? Plausible if Stage 3+ does not rebrand as emotional-water core. Presence should stay qualifier.

### u2 — Aquarius full · `builds_through_autonomy`

- Stage 1: `autonomy_high`, `presence_through_water_asc`  
- Surface: независимость / понимание / уединение / стратегическое действие  
- **§1.4 probe:** Strongest live candidate for exit feel — autonomy as sole SoT matches prior owner Profile complaint (old day-rhythm trap is absent here). Confirm ASC water does not steal the story in Stage 3.

### u20–22 — Taurus date_only · `builds_through_earth_stability` (×3)

- Single Stage 1 claim family; loglines vary but rhyme (медленно / осязаемо / надёжно)  
- **§1.4 probe:** Fine for date-only thin evidence; treat as **one** production-like archetype, not three independent confirmations of diversity.

### u26 — Pisces full · `builds_through_water_care`

- Stage 1: `care_through_water_sun`, `presence_through_air_asc`  
- Surface: эмпатическая забота / растворение границ  
- **§1.4 probe:** Care-as-core can carry intimacy/scenes; ASC air must remain presence, not a second identity. Watch Stage 3 not invent analysis/autonomy.

### Excluded

- u19: not a CE failure — natal chart payload shape breaks core-profile read.

## Verdict

| Question | Answer |
|----------|--------|
| Staging still trustworthy? | Yes (prior GATE PASS unchanged by this retest) |
| Live shadow healthy enough to keep flags on? | **Yes** — grounded, traceable, voice OK on this N |
| Close Stage 2 / start Stage 3? | **No** |
| Why? | §1.4 requires owner judgment that **one** Identity Core can explain the whole later cascade on **live** cores — not only staging scores |

**Recommendation:** keep shadow flags; owner completes exit skim (especially u2 Aquarius + u1 Gemini + u26 Pisces as three distinct full-natal stories). After explicit PASS on §1.4, write **Stage 2 close-out audit**, then Stage 3.

## Next

1. Owner §1.4 skim (checklist above).  
2. Optional: more distinct live packs when available (reduce Taurus-clone weight).  
3. Fix user 19 `ChartResponse` separately (not CE gate).  
4. **Do not** start Stage 3 Internal Engine until Stage 2 close-out.
