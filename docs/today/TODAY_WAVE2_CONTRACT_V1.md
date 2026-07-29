# Today Wave 2 — Data Contract `day_facts_v1`

**Status:** CONTRACT (docs only — not implemented)  
**Execution order:** [TODAY_WAVE2_EXECUTION_PLAN.md](./TODAY_WAVE2_EXECUTION_PLAN.md)  
**Motion (pilot):** [TODAY_MOTION_PILOT_V1.md](./TODAY_MOTION_PILOT_V1.md)

## Architectural decision

`day_facts_v1` is computed **once** per user×local-day (same layer that feeds `conflict` / `why_arose` for Act 3).

| Consumer | Role |
|----------|------|
| Act 3 chapters | Narrative over `conflict` + `scenes` |
| VerdictStrip | Pure view of `domain_verdicts` |
| GlanceTimeline | Pure view of `glance_timeline` |
| TapWidget | Reads `scenes[]`; writes `tap_event_v1` |

**No separate ranking** for strips. **No per-slot compute endpoints** for Verdict/Glance.  
Separate endpoints only for **write** (tap) and **multi-day aggregate** (accuracy summary).

Exact-time for glance is computed **inside** day_facts generation (§4), then stored on the object — UI does not call a second ranker.

---

## 1. `day_facts_v1` shape

```text
day_facts_v1 {
  schema_version: "v1"
  id: string                        # {user_id}:{date} — FK from tap events
  user_id: string
  date: date                        # user local date
  timezone: string                  # IANA, e.g. Europe/Minsk
  generated_at: datetime
  profile_id: string                # natal ref — do not duplicate chart blob
  profile_depth: "light" | "deep"
  day_card: "not_revealed" | string

  sky_drivers: [{
    planet: string, sign: string, degree_in_sign: float,
    retrograde: bool
  }]
  moon_phase: {
    illumination_pct: number
    phase: "waxing" | "waning"
    is_new: bool
    is_full: bool
  }

  natal_activations: [{
    id: string                      # stable; referenced by conflict/scenes/verdicts/timeline
    transiting_planet: string
    aspect: "conjunction"|"sextile"|"square"|"trine"|"quincunx"|"opposition"
    natal_point: string             # planet | ASC | MC | Node | house_cusp_N
    orb_deg: float
    exact_time_local: datetime | null   # null until exact-time pass; may stay null
    rank: int                       # 1 = strongest day signal
  }]

  numerology: { personal_day: int, source: "classic_reduce_v0" }

  conflict: {
    short_name: string
    thesis: string
    opposing_forces: { a: string, b: string }
    why_arose: string
    why_personal: string | "omit"
    driver_ids: [string]            # → natal_activations
  }

  scenes: [{
    id: string                      # trap_id for tap = scene.id
    sphere: string
    role_in_story: "primary"|"support"|"caution"
    what_happens: string
    opportunity: string
    trap: string
    recommended_action: string
    do_not: string
    domestic_example: string | null
    driver_ids: [string]
  }]

  domain_verdicts: [{               # VerdictStrip source
    domain: "work"|"money"|"relationships"|"energy"
    verdict: "favorable"|"neutral"|"caution"|"avoid"
    why_short: string               # ≤ 10 words
    driver_ids: [string]
    logic_source: "sphere_score_v0"
  }]

  glance_timeline: [{               # GlanceTimeline source; max 3
    time_local: datetime
    label_short: string             # ≤ 4 words
    valence: "favorable"|"caution"
    driver_id: string
  }]

  props: {
    color: { name, link_to_conflict, where_to_use },
    avoid_color: { name, amplifies_trap } | null,
    practice_or_promise: { text, window, serves_conflict },
    affirmation: { text, compensates_trap },
    humor: { text, serves_conflict },
    evening_payoff: string
  }

  generation_provenance: {          # debug / calib only — not UI
    conflict_driver_ids: [string],
    verdict_driver_ids: {
      work: [string], money: [string],
      relationships: [string], energy: [string]
    },
    timeline_driver_ids: [string]
  }
}
```

### Screen fetch

- **One call:** `GET /today/day-facts?date=YYYY-MM-DD` → full `day_facts_v1`
- Three slots render client-side from that payload
- Extra calls: tap write; optional accuracy summary (non-blocking)

---

## 2. Fixed domain → natal mapping

Order and set of domains **never** change day-to-day (scanability).

| Domain | Houses | Planets / points | Counts as activation when transit hits |
|--------|--------|------------------|----------------------------------------|
| work | VI, X | Sun, Mars, Saturn, MC | natal Sun/Mars/Saturn; cusp VI/X; MC |
| money | II, VIII | Venus, Jupiter, Pluto | natal Venus/Jupiter/Pluto; cusp II/VIII |
| relationships | V, VII | Venus, Moon, Descendant (VII cusp) | natal Venus/Moon; cusp V/VII |
| energy | I, VI | Sun, Mars, Moon, ASC | ASC; natal Sun/Mars/Moon; cusp VI |

A point in multiple domains (e.g. Mars → work + energy) counts in **both** — expected, not a bug.

UI order always: **work → money → relationships → energy**.

---

## 3. Verdict logic — `sphere_score_v0`

Draft; calibrate like `personal_day_source`. Marked `_v0` on purpose.

For each domain: take `natal_activations` whose `natal_point` / house is in the domain map.

```text
weight = valence(aspect, transiting_planet) * (1 − orb_deg / max_orb)
```

`max_orb`: 6° conjunction/trine/square/quincunx; 3° sextile; 8° opposition  
(same thresholds as calib-corpus activation generation).

**valence(aspect, planet):**

| Aspect | Valence |
|--------|---------|
| trine, sextile | +1 |
| square, opposition | −1 |
| conjunction | +1 if transit ∈ {Venus, Jupiter}; −1 if ∈ {Saturn, Mars, Pluto}; else 0 |
| quincunx | −0.5 (tune later) |

`score` = sum of weights. Map:

| score | verdict |
|-------|---------|
| > 0.5 | favorable |
| −0.5 … 0.5 | neutral |
| −1.5 … −0.5 | caution |
| < −1.5 | avoid |

Thresholds = first-pass hypothesis. Wave 2 calib goal: compare to human gut on 8 calib-igor datemarks; retune weights/thresholds, **not** the 4-domain principle.

---

## 4. GlanceTimeline — exact time (inside day_facts)

**Input:** `natal_activations` with `rank` 1–3 (same top drivers as conflict — **no second ranking**).

**Algorithm:** step search (5 min; optional binary refine) within user local day for when  
`|transit_longitude(t) − natal_point_longitude|` equals aspect angle (0/60/90/120/180°).

If no exact within local day (slow bodies): `exact_time_local = null`; activation stays in `natal_activations` / conflict but **not** in `glance_timeline`.

`glance_timeline`: ≤ **3** rows, sorted by `time_local`.  
`label_short`: no degrees, no aspect names (calib corpus purity §2).

---

## 5. Tap event + accuracy

### `tap_event_v1`

```text
tap_event_v1 {
  event_id: string
  user_id: string
  day_facts_id: string             # = day_facts_v1.id
  scene_id: string                 # = scenes[].id (= trap_id)
  prompted_text: string            # exact UI copy at tap time (audit)
  response: "avoided_trap" | "fell_into_trap" | "not_applicable" | "skipped"
  free_text: string | null
  responded_at: datetime
}
```

`prompted_text` is intentional duplication — historical labels stay auditable if scene copy changes later.

### Accuracy summary (multi-day; not inside day_facts)

```text
GET /today/accuracy-summary?window=14d
→ {
  overall: { correct: int, total: int },
  by_domain: {
    work: { correct, total },
    money: { correct, total },
    relationships: { correct, total },
    energy: { correct, total }
  }
}
```

- `correct` = `avoided_trap` where scene was `role_in_story: caution|primary` with an explicit trap  
- `not_applicable` / `skipped` **excluded** from denominator  

### Write

```text
POST /today/tap-widget/response  → tap_event_v1
```

---

## 6. Slot contracts

| Slot | Data source | Separate BE endpoint? |
|------|-------------|------------------------|
| VerdictStrip | `day_facts_v1.domain_verdicts` | No — pure render |
| GlanceTimeline | `day_facts_v1.glance_timeline` | No — pure render (exact-time is part of day_facts gen) |
| TapWidget | reads `scenes[]`; writes `tap_event_v1` | Yes — POST response; GET accuracy-summary |

---

## 7. Provenance / debug

`generation_provenance` is **not** UI. If strip vs Act 3 diverge, compare `driver_ids` — one activation pool, different top-N consumption.

---

## 8. UI state (beside day_facts — not inside it)

Mutating “seen” flags must **not** rewrite `day_facts_v1`.

```text
today_ui_state {
  day_facts_id: string
  hero_seen: bool
  card_opened: bool
  insight_seen: { [insight_id]: bool }
}
```

Tap completion = existence of `tap_event_v1` for that `day_facts_id` (no separate `checkin_completed` flag required).

---

## Architecture impact

Opens with the **first code PR** (Phase A), not with this docs lock:

- **SoT before:** ActShell stubs; narrative from day_scenario / contract fragments  
- **SoT after (phased):** practical strips + tap accuracy from `day_facts_v1` (+ tap store)  
- **Public JSON:** yes when day-facts / tap / accuracy ship  
- **Canon:** this file + execution plan + motion pilot  

---

## Related

- Wave 1 layout: ActShell slots already reserved in FE  
- Calib corpus: [`docs/audits/day_scenario_style_calib_igor_v1/`](../audits/day_scenario_style_calib_igor_v1/)  
- Foundation UI QA: remove text → expensive composition remains
