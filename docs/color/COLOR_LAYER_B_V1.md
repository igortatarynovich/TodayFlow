# Color catalog — Layer B v1

**Status:** ACTIVE — **6 colors** (2026-08-03; Champagne wired)  
**Catalog:** `day_color_catalog_v1.COLOR_CATALOG_V1` (20 rows = 8+A6+B6)  
**Generator:** `day_scenario_v1._needed_color_tags` + `day_favorable` → celebration tags

---

## Shipped (with generator branches)

| Color | Tags | Trigger |
|--|--|--|
| Шафрановый | `creative_spark`, `generous_warmth` | `sphere == "creativity"` |
| Терракотовый | `home_warmth`, `belonging` | `sphere == "home"` |
| Хризолитовый | `confident_abundance`, `steady_growth` | `sphere == "money"` (additive to work focus) |
| Гранатовый | `passionate_assertion`, `vital_courage` | keywords: страст / влечен / желан |
| Дымчато-сиреневый | `gentle_closure`, `honor_loss` | keywords: конец / заверш / потер / отпустить\|… |
| Шампань | `quiet_celebration`, `light_gratitude` | `day_favorable` from domain_verdicts |

`money` keeps `{focus, decision, calm_clarity}` and **adds** abundance tags. `work_decisions` unchanged.

### Closure pattern vs `отпуск`

Bare substring `отпус` false-positives on `отпуск`. Live code uses verb forms only. Covered by unit test.

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
- Tests: layer-B primary tags reachable; Champagne wins scoring when `day_favorable` and no competing specialty trap.
