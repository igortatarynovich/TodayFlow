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
    verdict: "calm"|"charged"|"friction"|"open"   # descriptive — NOT favorable/avoid
    why_short: string               # ≤ 10 words
    driver_ids: [string]
    logic_source: "sphere_score_v0_1"   # v0 failed calib; see §3
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

## 3. Verdict logic — `sphere_score_v0` → `sphere_score_v0_1`

### 3.1 Calib pass 1 (FAILED — do not ship)

Manual run of `sphere_score_v0` (universal valence + favorable/avoid map) on all **8** dates in [`day_scenario_style_calib_igor_v1`](../audits/day_scenario_style_calib_igor_v1/):

| Domain | Result |
|--------|--------|
| work | **avoid on 8/8** |
| money | **avoid on 6/8** |
| relationships | alternates favorable / caution / avoid — usable |
| energy | alternates — usable |

**Why this is a calibration failure, not a threshold tweak:** a strip that says `work: avoid` every day for months stops being scanned — today looks like yesterday. Root cause is structural for this natal, not random noise:

- Capricorn stellium (Venus, Mars, Uranus, Neptune, Saturn clustered)
- Slow transit Saturn squaring several of those points for months
- Same background transit continuously loads **work** and **money**, independent of “what is special today”

Mitigation tried (×0.3 dampen Saturn/Uranus/Neptune/Pluto): work still avoid on **7/8** — so speed/threshold alone cannot fix it.

**Deeper failure:** universal valence encodes square/opposition as unconditionally “bad” (−1). For domain **work**, a Mars square is often pressure that *pushes doing* — a **charged** day, not “avoid work”. One valence table for all domains is wrong in principle.

### 3.1b Calib pass 2 — dictionary works; sample bias found

| Finding | Detail |
|---------|--------|
| Descriptive dictionary | **APPROVED.** avoid→charged / caution→friction makes a stable “work charged” season honest and safer than “avoid work for months”. |
| Per-domain valence alone | Did **not** unlock day-to-day color changes inside the 8-date sample (work still charged 8/8). |
| Why | Methodological, not formula: all 8 calib-igor dates sit in one ~5-week window (27.07–28.08). Transit Sun in Leo opposes natal Aquarius Sun+MC cluster for that whole month — a real **career-friction season**, not a scoring bug. |
| Year-spread check | 12 dates, one per month: work shows calm (Jan–Feb), open (Mar–Apr, Jun), charged (May, Jul–Nov) — dictionary **does** differentiate across the year. |

**Still open before fully closing 0.5.2:** consecutive-day run (10–14 days inside one charged month, e.g. August) to see if **intensity / driver_ids / why_short** move day-to-day inside the season — not only the color word. If nothing moves even in details → separate conversation: seasonal domains vs lunar/Mercurial daily domains on different refresh frequencies (not the same daily strip).

Does **not** block Phase A (Tap). Dictionary lock **does** unblock Phase B vocabulary; consecutive run may still gate shipping strip UX polish.

### 3.2 Required contract fixes (dictionary APPROVED; valence still open)

1. **Valence is per-domain**, not universal.  
   Example: Mars square in `work` ≠ Venus square in `relationships`.  
   Per-domain valence alone did **not** create day-to-day variation inside one charged season (see §3.1b) — still required for meaning, not for seasonal differentiation.
2. **Verdict vocabulary is descriptive** — **APPROVED 2026-07-29** (calib pass 2).  
   Closed dictionary (schema keys → RU UI):

| Key | RU (strip) | Intent |
|-----|------------|--------|
| `calm` | спокойно | low charge / even field |
| `charged` | заряжено | pressure / drive — actable, not “bad” |
| `friction` | трение | grit / misalignment — careful, still descriptive |
| `open` | открыто | support / opening |

**Rejected for daily strip:** `favorable` / `avoid` (and similar “good/bad day at work” framing).

Pass 2 finding: swapping avoid→charged / caution→friction already makes an 8/8 “work charged” month **honest and safer** than “avoid work for two months”, even when the color word stays stable inside that season.

### 3.3 `sphere_score_v0_1` (OPEN — calib pass 2)

Status: **not closed**. Formula rewrite in progress; Phase B gated on pass 2.

Still true from v0:

```text
weight = valence_domain(domain, aspect, transiting_planet, natal_point)
         * (1 − orb_deg / max_orb)
         * speed_factor(transiting_planet)   # optional; alone insufficient
```

`max_orb`: unchanged (6° conj/trine/square/quincunx; 3° sextile; 8° opposition).

**Must change:**

| Piece | v0 (rejected) | v0.1 direction |
|-------|---------------|----------------|
| `valence(...)` | one table for all domains | `valence_work` / `valence_money` / `valence_relationships` / `valence_energy` |
| score → label | favorable / neutral / caution / avoid | calm / charged / friction / open |
| slow planets | full weight | dampen *and* still require per-domain meaning (dampen alone failed) |

**Illustrative (not final) — work only:**

| Aspect → natal | Draft valence_work | Why |
|----------------|--------------------|-----|
| square → Mars | toward **charged** (+) | pressure to act |
| square → Venus (work map rare) | toward **friction** (−) | style clash more than drive |
| trine / sextile → Sun/Mars/MC | toward **open** (+) | support |
| Saturn transit square stellium | reduced weight + prefer **friction**/**charged**, never month-long **avoid** | background weather ≠ daily ban |

Full per-domain tables + score→label thresholds: fill after calib pass 2 on the same 8 dates. Until then `logic_source` remains draft `sphere_score_v0_1`.

**Unchanged principle:** fixed 4 domains and scan order (work → money → relationships → energy).

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

### Phase A (Tap) — first code PR

- **SoT before:** Wave 1 stub buttons; no trap accuracy store
- **SoT after:** `tap_event_v1` via `POST /today/tap-widget/response`; prompt from `day_scenario.scenes[].trap` (alias until full `day_facts_v1`); accuracy via `GET /today/accuracy-summary`
- **Public JSON:** yes — new endpoints
- **Migration:** `today_tap_events` table
- **Canon:** this file §5–6 · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase A
- **Backward compatible:** old clients ignore slots; no break of existing contract fields

Opens with the **first code PR** (Phase A), not with docs lock alone.

---

## Related

- Wave 1 layout: ActShell slots already reserved in FE  
- Calib corpus: [`docs/audits/day_scenario_style_calib_igor_v1/`](../audits/day_scenario_style_calib_igor_v1/)  
- Foundation UI QA: remove text → expensive composition remains
