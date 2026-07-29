# Today Wave 2 — Execution Plan

**Status:** Phase A **LIVE** · Phase 0.5.2 **CLOSED** (`top_driver_v1`) · Phase B **UNBLOCKED**  
**Depends on:** Wave 1 ActShell LIVE (`TodayActShell` + reserved slots)  
**Canon companions:**
- [TODAY_WAVE2_CONTRACT_V1.md](./TODAY_WAVE2_CONTRACT_V1.md) — `day_facts_v1`, slots, tap, accuracy
- [TODAY_MOTION_PILOT_V1.md](./TODAY_MOTION_PILOT_V1.md) — attention hierarchy; pilot = TapWidget

**Rule:** one compute per user×day. Slots are views. Only Tap write + accuracy aggregate need separate endpoints.

**Parallelism note:** Phase A shipped without waiting on verdict calib. Phase B may start now — uses `top_driver_v1`, not domain sum.

---

## North star

Practical Today on phone: scan verdict in 1s → see when today bites → one tap that builds personal accuracy over weeks — **without** Act 3 story contradicting the strips.

Trust bug to avoid: VerdictStrip says «money: friction» while Act 3 narrates a different money story. Both must read the same `day_facts_v1.driver_ids` pool. (Evaluative «avoid work every day» is also a product trust/health failure — see contract §3.1.)

---

## Phases

### Phase 0 — Spec lock (docs only) ✅

| Step | Deliverable | Done when |
|------|-------------|-----------|
| 0.1 | `day_facts_v1` shape + sphere map + score draft | Contract doc merged |
| 0.2 | Tap event + accuracy summary API | Contract doc merged |
| 0.3 | Slot data sources table (no extra ranking) | Contract doc merged |
| 0.4 | Motion pilot scope (TapWidget only) | Motion pilot doc merged |
| 0.5 | Tracker: Wave 2 → CONTRACT LOCKED | Tracker line updated |

**Gate:** owner accepts docs. Architecture impact opens at first **code** PR (Phase A).

---

### Phase 0.5 — Manual calibration (verdict formula) ✅ CLOSED

| Step | Work | Status |
|------|------|--------|
| 0.5.1 | Run `sphere_score_v0` on 8 calib-igor dates | **DONE — FAILED** (work avoid 8/8; money avoid 6/8) |
| 0.5.1b | Slow-planet dampen 0.3 retry | **DONE — insufficient** |
| 0.5.2a | Descriptive dictionary `calm|charged|friction|open` + year-spread check | **APPROVED** |
| 0.5.2b | Full August (31 days) consecutive inside charged month | **DONE** — sum fails (work charged 29/31, 2 flips); **top_driver_v1** approved (work 8 flips; money 2; rel 3; energy 6) |
| 0.5.3 | Confirm scene.id = `trap_id` for tap | **DONE** with Phase A (`scene_id` alias) |

**Gate for Phase B:** 0.5.2 ✅ — dictionary + `top_driver_v1` aggregation locked.  
**Does not gate Phase A** (already live).

---

### Phase A — TapWidget + accuracy loop (FIRST code) — **START NOW**

**Why first / why parallel:** cheapest slot, highest retention payoff; **zero dependency** on `domain_verdicts`. Motion pilot rides the same PR.

| Step | Work | Notes |
|------|------|-------|
| A.0 | **Architecture impact** section in PR + short canon pointer | Required — new SoT for tap + accuracy UI |
| A.1 | Persist / expose `day_facts_v1` minimal subset needed for tap (`id`, `scenes[]`, `props.practice_or_promise.window`) | May start as projection from existing day_scenario if full object not ready — **must** still share conflict/scene ids with Act 3 |
| A.2 | `POST /today/tap-widget/response` → `tap_event_v1` | Store `prompted_text` snapshot |
| A.3 | `GET /today/accuracy-summary?window=14d` | `correct` = `avoided_trap`; skip n/a & skipped in denominator |
| A.4 | Fill Act 5 `today-slot-tap-widget`: prompt from primary/caution scene; 3 responses + optional free_text | Replace Wave 1 stub |
| A.5 | Minimal readable summary near tap («за 14 дней: N из M») | Empty state OK if total=0 |
| A.6 | **Motion pilot:** attention breathe on TapWidget until tap recorded; static badge under reduced-motion; `today_ui_state` only if needed beyond tap_event | See motion pilot doc |
| A.7 | Tests: event schema, denominator rules, slot renders from day_facts | FE + BE |

**Gate:** user can tap once; event keyed by `day_facts_id` + `scene_id`; summary readable; Act 3 scene text matches prompted_text for that scene.

**Out of scope for A:** VerdictStrip fill, GlanceTimeline times, full natal recompute.

---

### Phase B — VerdictStrip (no new ranking endpoint) — **UNBLOCKED**

| Step | Work | Notes |
|------|------|-------|
| B.0 | Architecture impact if public JSON / meaning SoT changes | Likely yes — strip becomes user-facing SoT |
| B.1 | Compute `domain_verdicts[4]` via **`top_driver_v1`** (max \|weight\| driver) | Fixed order: work → money → relationships → energy; **not** domain sum |
| B.2 | Fill Act 1 `today-slot-verdict-strip` from `domain_verdicts` only | Dictionary: calm / charged / friction / open |
| B.3 | Provenance: `generation_provenance.verdict_driver_ids` (top id primary) | Debug only |
| B.4 | Visual: **no motion** on strip (idle) | Motion pilot doc |

**Gate:** strip always 4 rows; August-style inside-month flips under top-driver; calib 0.5.2 accepted.

---

### Phase C — GlanceTimeline (exact-time BE)

| Step | Work | Notes |
|------|------|-------|
| C.0 | Architecture impact — exact-time compute is new capability | |
| C.1 | Exact-time search for `natal_activations` rank 1–3 (5‑min step / binary refine) | Null if no exact within local day → exclude from glance |
| C.2 | Fill `glance_timeline` ≤3, sorted by `time_local`; clean `label_short` | Same top drivers as conflict — no second ranker |
| C.3 | Fill Act 2 `today-slot-glance-timeline` | Pure render |
| C.4 | Motion: live-now = priority 4 indicator only (static «сейчас» under reduced-motion) | Does not compete with tap |

**Gate:** ≤3 markers; times match Swiss Ephemeris zero-orb; labels have no degrees/aspect jargon.

---

### Phase D — Hardening (after A–C)

| Step | Work |
|------|------|
| D.1 | Single `GET /today/day-facts?date=` for screen; three slots client-render |
| D.2 | Trust audit: Act 3 conflict.driver_ids ⊆ same pool as verdict/timeline provenance |
| D.3 | Motion pilot retrospective: promote motion doc to app-wide or revise classes |
| D.4 | Optional Act 4 if/then copy from `scenes[].recommended_action` / traps (only if still needed after A–C) |

---

## Explicit non-goals (both waves until reopened)

- iOS parity
- Full Foundation Figma redesign
- Multi-panel natal on Today (ActShell full-bleed stack only)
- Rewriting C2 chapter engine wholesale
- Parallel “verdict API” / “glance API” that re-rank drivers

---

## Suggested ticket titles

1. `Today Wave2 Phase0.5 — CLOSED (top_driver_v1 + descriptive dict)`
2. `Today Wave2 PhaseA — TapWidget` ← **live**
3. `Today Wave2 PhaseB — domain_verdicts + VerdictStrip` ← **unblocked now**
4. `Today Wave2 PhaseC — exact-time glance_timeline + GlanceTimeline UI`
5. `Today Wave2 PhaseD — day-facts GET + trust audit + motion retro`

---

## Decision log

| Decision | Choice |
|----------|--------|
| Single SoT | `day_facts_v1` once per user×day |
| Slot endpoints | None for Verdict/Glance render; Tap write + accuracy GET only |
| Wave 2 order | Tap → Verdict → Glance; **Tap parallel with calib pass 2** |
| Domains | Fixed 4: work / money / relationships / energy |
| Verdict labels | Descriptive: calm / charged / friction / open (**not** favorable/avoid) |
| Aggregation | **`top_driver_v1`** (max \|weight\|); domain **sum rejected** after August 31-day run |
| Valence | **Per-domain**; universal table rejected after calib pass 1 |
| Motion pilot | TapWidget only; not app-wide until proven |
| UI persistence | `today_ui_state` beside day_facts; tap completion = tap_event exists |
