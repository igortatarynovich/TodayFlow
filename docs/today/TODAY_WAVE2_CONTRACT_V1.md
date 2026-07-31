# Today Wave 2 — Data Contract `day_facts_v1`

**Status:** Phase D.2 **LIVE** · D.2b generation SoT **LIVE** (`conflict.driver_ids` ← natal `pt-*` when present)  
**Execution order:** [TODAY_WAVE2_EXECUTION_PLAN.md](./TODAY_WAVE2_EXECUTION_PLAN.md)  
**Motion (pilot):** [TODAY_MOTION_PILOT_V1.md](./TODAY_MOTION_PILOT_V1.md)

## Architectural decision

`day_facts_v1` is computed **once** per user×local-day (same layer that feeds `conflict` / `why_arose` for Act 3).

| Consumer | Role |
|----------|------|
| Act 3 chapters | Narrative over `conflict` + `scenes` |
| VerdictStrip | View of `domain_verdicts` — **full 4-row** when used standalone; **Glance Screen 0** applies presentation compression (see §3.4 / SCREEN_FLOW) |
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
    why_short: string               # ≤ 10 words — from top driver transit
    driver_ids: [string]            # primary = top_driver id; optional runners-up for debug
    logic_source: "top_driver_v1"   # max |weight| driver sets sign+intensity; see §3
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

## 3. Verdict logic — `top_driver_v1` (APPROVED after 0.5.2)

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

### 3.1b Calib pass 2a — dictionary works; sample bias found

| Finding | Detail |
|---------|--------|
| Descriptive dictionary | **APPROVED.** avoid→charged / caution→friction makes a stable “work charged” season honest and safer than “avoid work for months”. |
| Per-domain valence alone | Did **not** unlock day-to-day color changes inside the 8-date sample (work still charged 8/8). |
| Why | Methodological, not formula: all 8 calib-igor dates sit in one ~5-week window (27.07–28.08). Transit Sun in Leo opposes natal Aquarius Sun+MC cluster for that whole month — a real **career-friction season**, not a scoring bug. |
| Year-spread check | 12 dates, one per month: work shows calm (Jan–Feb), open (Mar–Apr, Jun), charged (May, Jul–Nov) — dictionary **does** differentiate across the year. |

### 3.1c Calib pass 0.5.2b — full August (31 days) → **CLOSED**; aggregation model change

Ran **all 31 days of August** (not only 10–14) with descriptive dictionary + per-domain valence.

| Aggregation | work flips in August | Notes |
|-------------|----------------------|-------|
| **Sum** (`sphere_score_*`) | **2** (charged 29/31) | FAILS inside-month differentiation |
| **Top-driver** (`top_driver_v1`) | **8** | usable; money 2, relationships 3, energy 6 |

**Why sum fails inside one month (not just sample bias):** the four work points (Sun, Mars, Saturn, MC) are physically close for this natal (~45° span: Sun+MC Aquarius, Mars+Saturn Capricorn). A transit that hard-aspects the cluster loads **all** points at once; summing them keeps the domain score stuck for weeks. Reproducible inside a single month — structural, not “we picked a bad 8-day window again.”

**Top-driver fix:** for each domain, take only the activation with max `|weight|`. That driver’s **sign** → verdict word; its **|weight|** → intensity (feeds `why_short` / provenance — already the strongest story, now also the decision).

Compromise accepted: money/relationships flip less often under top-driver (2–3 vs 3–4) — feels correct (money slower than mood), not a bug.

**Rejected for VerdictStrip:** domain sum aggregation.  
**Approved:** `logic_source: "top_driver_v1"`. Dictionary + thresholds unchanged.

### 3.2 Locked product rules

1. **Valence is per-domain**, not universal (Mars square in `work` ≠ Venus square in `relationships`).
2. **Verdict vocabulary is descriptive** — **APPROVED**:

| Key | RU (strip) | Intent |
|-----|------------|--------|
| `calm` | спокойно | low charge / even field |
| `charged` | заряжено | pressure / drive — actable, not “bad” |
| `friction` | трение | grit / misalignment — careful, still descriptive |
| `open` | открыто | support / opening |

**Rejected for daily strip:** `favorable` / `avoid`.

3. **Aggregation is top-driver**, not sum — **APPROVED 2026-07-29 (0.5.2 closed).**

### 3.3 `top_driver_v1` (APPROVED — Phase B may ship)

```text
for each domain D:
  candidates = natal_activations whose natal_point/house ∈ map(D)
  for each a in candidates:
    weight(a) = valence_domain(D, a.aspect, a.transiting_planet, a.natal_point)
                * (1 − a.orb_deg / max_orb)
                * speed_factor(a.transiting_planet)   # optional dampen; alone insufficient
  top = argmax_a |weight(a)|
  verdict = map_signed_weight_to_label(sign(weight(top)), |weight(top)|)  # calm|charged|friction|open
  why_short = label from top transit (≤10 words)
  driver_ids = [top.id]   # provenance may still list runners-up for debug
```

`max_orb`: 6° conj/trine/square/quincunx; 3° sextile; 8° opposition.

**Score → label** (same bands as earlier descriptive pass; tune later only if needed):

| Signed weight of top | verdict |
|----------------------|---------|
| strong + | open |
| mild + / near 0 with drive aspect | charged |
| mild − | friction |
| near 0 / quiet | calm |

Exact numeric cutovers stay calibratable; the **aggregation rule** (top, not sum) is the locked SoT change.

**Illustrative valence_work (draft, still per-domain):**

| Aspect → natal | Draft valence_work | Why |
|----------------|--------------------|-----|
| square → Mars | toward **charged** (+) | pressure to act |
| square → Venus (work map rare) | toward **friction** (−) | style clash more than drive |
| trine / sextile → Sun/Mars/MC | toward **open** (+) | support |

**Unchanged:** fixed 4 domains and scan order (work → money → relationships → energy).

**Out of scope for this close:** splitting “seasonal” vs “daily” domains onto different refresh cadences — not needed once top-driver restores inside-month flips.

### 3.4 Glance Screen 0 — presentation compression (FE)

**Data SoT unchanged:** still fixed-4 `domain_verdicts` from `top_driver_v1`. No new domain inventory in this change (expanding past 4 = separate Architecture + contract).

**Composition SoT (Glance only):** summary ≠ four equal cards.

1. Thesis is the primary summary (visual hero).
2. If **≥3** domains share the same `verdict` → those collapse to **one compact line** (`Работа · Деньги · Энергия — открыто`); only **outliers** get a full card.
3. If **all** domains share the same verdict → **one unanimous line** (no cards) — e.g. open → «День ровный по всем направлениям…».
4. If no majority of 3+ → keep full cards (mixed day).
5. Space freed by collapsed cards → **promoted nearest** timed signal (actionable).
6. Teasers 1–5 unchanged.
7. Identical `why_short` across 4 (silent bank) still → transport honesty, not fake meaning.

Canon UI: [SCREEN_FLOW_V1 §4](../foundation/SCREEN_FLOW_V1.md). Helper: `compressGlanceDomainVerdicts`.

---

## 4. GlanceTimeline — exact time (inside day_facts)

**Input:** `natal_activations` in strength `rank` order (same pool as conflict — **no second ranking**). Exact-time walk covers ranks 1…12 until ≤3 timed rows (skips aspects without a known angle or no zero-cross in the local day).

**Algorithm:** step search (30 min samples + bisect) within user local day for when  
`|transit_longitude(t) − natal_point_longitude|` equals aspect angle (0/60/72/90/120/144/150/180°).

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

**D.2 (day_facts honesty, not Act 3 readiness):** Project conflict/scenes onto day_facts **only** when every `conflict.driver_id` is natal-style (`pt-…`) and ⊆ the same-request activation pool. Pack-ranked ids (`sky-`/`phase-`/`moon-`/…) fail the gate → omit narrative, `partial: true`. Act 3 continues to read `day_story.day_scenario` (no demotion by this gate).

**D.2b (generation SoT):** When `foundation.personal_natal_activations` has `pt-*` rows, `build_scenario_conflict_v1` / native LLM map set `conflict.driver_ids` to top-N natal ids (same pool as Strip). Pack ranked_drivers stay on foundation for dramaturgy provenance. Stale cached scenarios with pack ids remain gated by D.2 until regenerate — no serve-time invent.

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

### Phase B (VerdictStrip) — code PR

- **SoT before:** empty Act 1 verdict slot; domain tone not user-facing
- **SoT after:** `domain_verdicts[4]` via **`top_driver_v1`** (max `|weight|` driver per domain); dictionary `calm|charged|friction|open`; Act 1 strip is pure view
- **Public JSON:** yes — interim `GET /today/domain-verdicts` (until Phase D folds into `day_facts_v1`)
- **Migration:** none
- **Canon:** this file §3.3 · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase B
- **Backward compatible:** old clients ignore strip; no change to existing day_story / today_contract fields

### Phase B′ (activation consolidation) — pre-C

- **SoT before:** Strip via private `_calculate_transits`; day_scenario `personal_natal_activations` from claim prose — two pools
- **SoT after:** shared `compute_natal_activations` + TTL snapshot; foundation prefers `celestial_events.natal_activations`; strip uses same resolve; `is_fallback` on FE
- **Public JSON:** `is_fallback` added (alias of `degraded`); interim GET kept
- **Migration:** none
- **Canon:** §6 intent (one pool) · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase B′
- **Backward compatible:** yes — extra field; FE fallback only when flagged

### Phase C (GlanceTimeline) — code PR

- **SoT before:** empty Act 2 glance slot
- **SoT after:** `glance_timeline` ≤3 from activations rank 1–3 with exact-time within local day; labels without aspect jargon; live-now = static «сейчас»
- **Public JSON:** yes — interim `GET /today/glance-timeline` (until Phase D `day_facts_v1`)
- **Migration:** none
- **Canon:** this file §4 · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase C
- **Backward compatible:** old clients ignore slot; no change to day_story / today_contract fields

### Phase D.1 (day_facts slot envelope) — code PR

- **SoT before:** Strip via `GET /today/domain-verdicts`; Glance via `GET /today/glance-timeline`; both independently resolve activations
- **SoT after:** Screen slots prefer `GET /today/day-facts?local_date=`; one `assemble_day_facts_v1` per load. Interim endpoints reimplemented as **slices** of the same assembler (no second ranker). Experiential `why_short` / `label_short` via `today_activation_copy_v1`
- **Public JSON:** yes — new `day_facts_v1` partial envelope (`partial: true`); old endpoints backward compatible
- **Migration:** none
- **Canon:** this file status · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase D.1
- **Backward compatible:** yes — interim GETs remain; FE day-facts client cache dedupes Act 1/2

### Phase D.1b (narrative projection) — code PR

- **SoT before:** Narrative only on `day_story.day_scenario`; day-facts = slots only (`partial: true`)
- **SoT after:** Cached day_scenario projected onto day-facts when temporal gate passes. Superseded gate semantics: see **Phase D.2**. Act 3 still reads day_scenario nest. `thesis` = `label_ru` or null (no filler); `evening_payoff` null until SH-4. Natal chart body labels indexed with aliases so activations are non-empty when chart rows use lowercase `body`.
- **Public JSON:** yes — additive conflict/scenes/props/sky/moon/numerology; `partial` semantics
- **Migration:** none
- **Canon:** this file status · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase D.1b
- **Backward compatible:** yes — old clients ignore new fields; Act3 gap when scenario not ready = Day Map / legacy (not invent)

### Phase D.2 (day_facts narrative gate — pt-* ⊆ pool) — code PR

- **SoT before:** D.1b soft gate allowed event-pack conflict ids when natal pool non-empty; commit `69bfa59` also demoted Act 3 `ready` via the same rule (live regression risk on pack-majority days)
- **SoT after:** day_facts projects narrative **only** if all `conflict.driver_ids` are `pt-…` and ⊆ fresh activation pool; else omit conflict/scenes/props, `partial: true`. Act 3 demotion **removed** — chapters stay on day_scenario nest. No `trust_ok`. No pack→natal invent. Generation SoT → **D.2b**.
- **Public JSON:** `partial: true` more often on day_facts when pack ranks win; **no live UI impact today** (FE does not consume `day_facts.conflict`/`.scenes`; Act 3 uses nest). When FE starts reading those fields, re-check product-facing copy.
- **Migration:** none
- **Canon:** this file §7 · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) Phase D.2
- **Backward compatible:** yes — additive omission only on day_facts; Act 3 path restored to pre-`69bfa59`

### Phase D.2b (conflict.driver_ids generation SoT) — code PR

- **SoT before:** `conflict.driver_ids` from thesis/pack `ranked_drivers` (sky-/phase-/moon- majority)
- **SoT after:** When foundation has natal `pt-*` activations, conflict.driver_ids = top-N by rank (same pool as Strip). Pack remains on `foundation.ranked_drivers` / thesis for dramaturgy. D.2 serve gate unchanged for stale caches.
- **Public JSON:** after regenerate, day_facts more often `partial: false` with narrative; Act 3 nest driver_ids become natal when rebuilt
- **Migration:** none required; natural regen / force_rebuild clears pack-id caches
- **Canon:** this file §7 · [TODAY_WAVE2_EXECUTION_PLAN](./TODAY_WAVE2_EXECUTION_PLAN.md) D.2b
- **Backward compatible:** yes — pack fallback when no natal pool; no invent on serve

---

## Related

- Wave 1 layout: ActShell slots already reserved in FE  
- Calib corpus: [`docs/audits/day_scenario_style_calib_igor_v1/`](../audits/day_scenario_style_calib_igor_v1/)  
- Foundation UI QA: remove text → expensive composition remains
