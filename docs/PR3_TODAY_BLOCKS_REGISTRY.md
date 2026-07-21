# Today Production Blocks Registry (PR-3 entry)

**Status:** DRAFT — contract inventory for Today Surface (not UI redesign)  
**Depends on:** [PR2_APP_SHELL.md](./PR2_APP_SHELL.md) · [PR3_TODAY_PRODUCTION_SURFACE.md](./PR3_TODAY_PRODUCTION_SURFACE.md) · `day_story_v1` explainable trace  
**Rule:** no Source / Appear-when → block is not designed.

---

## Block passport template

| Field | Value |
|-------|-------|
| Block | |
| Route | `/today` (+ query modes) |
| Component | |
| Source | |
| Contract fields | |
| Appear when | |
| Loading / Ready / Empty / Partial / Error | |
| Primary action | |
| No-data | |
| Foundation surface | |

---

## Confirmed blocks (from live contracts)

### T1 · Day story (authoritative narrative)

| Field | Value |
|-------|-------|
| Block | Day story |
| Route | `/today` |
| Component | `TodayCompositionSurface` via `usesDayStorySingleVoice` / `todayContractMapper` |
| Source | `GET /today/contract` → `day_story` (+ `trace`) |
| Contract fields | theme, direction, story, do, avoid, today_move, talisman, practice_recommendation, **trace** (evidence, derived_claims, confidence, limitations, domains_present/absent) |
| Appear when | Authenticated + contract ready with `day_story` |
| Loading | ProductShell loading |
| Ready | Composition single-voice |
| Empty / Partial | Fallback story with `trace.used_fallback`; limitations in progress |
| Error | ProductShell error + retry |
| Primary action | Reveal / refresh story when stale |
| No-data | Do not invent prose client-side |
| Foundation | Hero Medium (later surface pass) |

### T2 · Domain lenses (partial)

| Field | Value |
|-------|-------|
| Block | Domain cards (relationships / money_work / family) |
| Source | `contract.domains.*.evidence_status` |
| Appear when | `evidence_status === "present"` and slots non-empty |
| No-data | **Hide** domain when `evidence_status === "absent"` |
| Note | Never fill from catalog fallback as personal |

### T3 · Day symbol reveal

| Field | Value |
|-------|-------|
| Block | Card / number reveal |
| Source | `/today/symbols/*` · morning ritual · day_symbol_state |
| Appear when | Ritual path / reveal state |
| No-data | Redacted until reveal |

### T4 · Morning ritual / spine (optional `?full=1`)

| Field | Value |
|-------|-------|
| Block | Ritual flow |
| Source | morning + contract + tracking supplementary |
| Appear when | `?full=1` or ritual mode |
| Note | Content redesign out of this inventory slice |

### T5 · Guest / auth gates

| Field | Value |
|-------|-------|
| Block | Guest gate / first-today |
| Source | auth session · guest draft |
| Appear when | unauthenticated |
| Primary action | Login / create |

---

## Deferred (not Surface-ready)

| Block | Why |
|-------|-----|
| Independent stone/color generators | DailyState / Recommendation Engine only |
| Synthetic weekly rail | Closed in PR-2 |
| Fallback contract unmarked as personal | V5 — mark or hide in Surface pass |
| Soft “почему” from kitchen `trace.limitations` | Kitchen text; later only meaning-facing claims |

---

## Next Surface step

1. ~~FE: hide domain glance when `evidence_status === "absent"`~~ — **DONE** (`isDomainLensPresent`).  
2. Composition-only polish: no competing overview chrome; rail stays data-only (PR-2).  
3. Optional: soft “почему так” from meaning-facing `derived_claims`.
