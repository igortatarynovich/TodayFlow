# Color catalog — Layer B v1

**Status:** ACTIVE for 5 colors (2026-08-02); **Champagne PENDING**  
**Catalog:** `day_color_catalog_v1.COLOR_CATALOG_V1`  
**Generator:** `day_scenario_v1._needed_color_tags`

---

## Shipped (with generator branches)

| Color | Tags | Trigger |
|--|--|--|
| Шафрановый | `creative_spark`, `generous_warmth` | `sphere == "creativity"` |
| Терракотовый | `home_warmth`, `belonging` | `sphere == "home"` |
| Хризолитовый | `confident_abundance`, `steady_growth` | `sphere == "money"` (additive to work focus) |
| Гранатовый | `passionate_assertion`, `vital_courage` | keywords: страст / влечен / желан |
| Дымчато-сиреневый | `gentle_closure`, `honor_loss` | keywords: конец / заверш / потер / отпустить\|отпускать\|… |

`money` keeps the existing `{focus, decision, calm_clarity}` set and **adds** abundance tags. `work_decisions` unchanged.

### Closure pattern vs `отпуск`

Bare substring `отпус` would false-positive on `отпуск` (rest_travel). Live code uses explicit verb forms only (`отпустить`, `отпускать`, `отпустил`, `отпускаю`, `отпусти`). Covered by unit test.

---

## Pending — Шампань

Tags `quiet_celebration` / `light_gratitude` need a **favorable outcome / resolution** signal.

Probed conflict model: `thesis.mode` ∈ {conflict, transition, recovery, stability, …} — trap/force oriented. No `verdict` / `favorable` / “день разрешился благополучно” field on conflict used by `build_scenario_props_v1`.

**Decision:** do **not** merge Шампань into `COLOR_CATALOG_V1` until that signal exists (separate feature). Tracked as `PENDING_LAYER_B_COLORS`.

---

## Anti-orphan

- Merge catalog rows **only** with `_needed_color_tags` branches (this PR).
- `validate_color_catalog_v1` rejects pending names in live catalog; catalog tags ⊆ `LIVE_NEEDED_COLOR_TAGS`.
- Tests assert Layer-B primary tags are reachable and Champagne absent.
