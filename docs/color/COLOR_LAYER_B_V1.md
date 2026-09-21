# Color catalog — Layer B v1

**Status:** ACTIVE — **6 colors** (2026-08-03; Champagne wired)  
**Catalog:** `day_color_catalog_v1.COLOR_CATALOG_V1` (20 rows = 8+A6+B6)  
**Generator:** `day_scenario_v1._needed_color_tags` from F05 8-set + F09 domain + `day_favorable` → celebration tags

---

## Shipped (with generator branches)

| Color | Tags | Trigger |
|--|--|--|
| Шафрановый | `creative_spark`, `generous_warmth` | F05 `radiance` |
| Терракотовый | `home_warmth`, `belonging` | catalog knowledge; not a scene-sphere trigger |
| Хризолитовый | `confident_abundance`, `steady_growth` | F09 domain `money` |
| Гранатовый | `passionate_assertion`, `vital_courage` | F05 `momentum` |
| Дымчато-сиреневый | `gentle_closure`, `honor_loss` | catalog knowledge; not a trap-keyword trigger |
| Шампань | `quiet_celebration`, `light_gratitude` | `day_favorable` from domain_verdicts on F09 activations |

`money` keeps `{focus, decision, calm_clarity}` and **adds** abundance tags. Scene `work_decisions` / trap text are not K15 input.

### Closure pattern vs `отпуск`

Bare substring `отпус` is retired with the scene-keyword generator. Live K15 tags come from F05/F09 closed lookups only.

---

## Шампань — `day_favorable`

**Where:** `build_scenario_props_v1(..., day_favorable=)` called from native LLM assembly, deterministic engine, and project heal — after `personal_natal_activations` are on the foundation.

**How:** same `compute_domain_verdicts(activations)` as live `today_day_facts_v1` (pure function; no pipeline reorder).

**Heuristic** (`is_day_favorable` in `today_domain_verdicts_v1`):

- any domain `friction` → False
- else `count(verdict == "open") >= DAY_FAVORABLE_MIN_OPEN` (default **2**)

`DAY_FAVORABLE_MIN_OPEN = 2` is a **calibration starting point** — tune on live days if Champagne fires too often/rarely. Do **not** recalibrate `domain_magnitude` weights for this.

Champagne is reachable via scoring specialty bonus, not a forced override.

---

## Anti-orphan

- Catalog tags ⊆ `LIVE_NEEDED_COLOR_TAGS`; `PENDING_LAYER_B_COLORS` empty while all B rows are live.
- Tests: F05 8-set + F09 4-set + `day_favorable` emit live tags; Champagne wins scoring when `day_favorable` and F05 has no competing Layer-B specialty.
