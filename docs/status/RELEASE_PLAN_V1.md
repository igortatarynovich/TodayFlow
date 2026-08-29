# Release Plan v1 — TodayFlow Soft Launch

**Status:** ACTIVE  
**Date:** 2026-08-28  
**Owner:** Product + Engineering  
**Scope:** web soft launch v1 (iOS parity — parallel wave, not blocker).

**Canonical anchors:**
- Product / launch contour: [TODAYFLOW_PRODUCT_CANON_UNIFIED.md](../TODAYFLOW_PRODUCT_CANON_UNIFIED.md) §12 Launch MVP contour
- Ship gate / behavior test: [BEHAVIOR_CHANGE_TEST_V0.md](./BEHAVIOR_CHANGE_TEST_V0.md)
- Today product cycle: [today/TODAY_PRODUCT_FLOW_V1.md](../today/TODAY_PRODUCT_FLOW_V1.md)
- Compute lifecycle: [COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md](../COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md)
- Practice library fill: [practices/PRACTICE_CONTENT_COVERAGE_V1.md](../practices/PRACTICE_CONTENT_COVERAGE_V1.md)
- Historical launch execution doc: [WEB_LAUNCH_EXECUTION_PLAN.md](./WEB_LAUNCH_EXECUTION_PLAN.md) (SUPERSEDED for execution)

**Purpose:** one place for the path from today to soft launch, success criteria, phases, gates, and immediate next steps. Supersedes the stale `WEB_LAUNCH_EXECUTION_PLAN.md` for active execution.

---

## 1. Definition of Release Success

Soft launch is **done** when all of the following are true:

1. **Minimum Day Cycle ship gate passed:** a new user can complete `Landing → Signup → Onboarding → Today → Evening Close → D2+ Continuity` without manual workarounds.
2. **Behavior test cohort started:** 5–10 real people using the product for 14 days, with the Day-14 question measurable.
3. **Compute lifecycle stable:** no 402/billing blockers, clean COGS baseline recorded, GET `/today` does not trigger LLM.
4. **Practice Library P0 cells fully sourced:** 26/26 need cells covered by `accepted` techniques (not `llm_provisional`).
5. **Personal Model read-path hygiene:** no `build()` LLM-on-read in Today/Compat/Tarot/Account GETs; `snapshot_id` provenance in generation logs.
6. **Production deploy & monitoring ready:** deploy workflow or documented manual runbook, alerts for availability and LLM spend.

Launch v1 **does not require** iOS parity, full paywall, all JTBD packs, or full Growth/Maps surfaces. Those are wave 2.

---

## 2. Freeze Rules (active until launch)

| Allowed | Not allowed |
|---------|-------------|
| Fixes that unblock the ship gate | New surfaces, entities, or JTBD packs |
| Bug fixes in launch path | Design-only polish without story-gate failure |
| Practice library fill (1 cell at a time) | Expanding Knowledge Core atoms / Layer 5 recipes |
| iOS parity work (parallel, not blocking web) | iOS blocking web launch decisions |
| Compute lifecycle / cost containment | Model downgrades that degrade paid synthesis quality |

---

## 3. Phases, Gates & Acceptance Criteria

### Phase 0 — Unblock & Baseline (0–3 days)

| # | Task | Acceptance Criteria | Owner |
|---|------|---------------------|-------|
| 0.1 | Merge current practice fill changes | `test_content_library_v1.py` green; coverage counts 5/26 sourced | Backend + Content |
| 0.2 | Fix Token Factory billing / top-up | `POST /chat/completions` = 200; `/models` 200 is not enough | Ops |
| 0.3 | Reset `llm_spend.json` latch | `tripped=false`, `spent_usd=0` for current UTC date | Ops |
| 0.4 | Run 4-step COGS clean baseline | 1 real profile × 30 Today opens + retries + 1 Tarot; USD total recorded in tracker | Backend + Ops |
| 0.5 | Server check live `/today` | Global accepted = 1; Personal accepted = 2; reopen = 0 LLM; force rebuild works | Backend |

**Gate G0:** billing unblocked and baseline recorded. No G0 = no further work on ship gate.

---

### Phase 1 — Ship Gate: Core Daily Loop (Week 1–2)

| # | Task | Acceptance Criteria | Depends On |
|---|------|---------------------|------------|
| 1.1 | End-to-end walkthrough Run 3 | All cells in `BEHAVIOR_CHANGE_TEST_V0.md` Run 3 checklist are OK/BROKEN with notes | G0 |
| 1.2 | Fix signup/onboarding UI blockers | Repeatable pass without manual workarounds | 1.1 |
| 1.3 | Real D+1 continuity after evening close | 1 user × 2 calendar days; S0 continuity line appears without localStorage substitution | 1.2 |
| 1.4 | Team walkthrough 2 people × 2 days | Ship gate DoD 6/6 from `BEHAVIOR_CHANGE_TEST_V0.md` | 1.3 |
| 1.5 | Start behavior test cohort | 5–10 people, 14 days, metrics collection live | 1.4 |
| 1.6 | Parallel: Practice Library fill | +1 sourced P0 cell per week starting from `need.motivation.activate` | 0.1 |

**Gate G1:** ship gate passed and behavior test started.

---

### Phase 2 — Today Cutover & Personal Model Hygiene (Week 2–3)

| # | Task | Acceptance Criteria | Depends On |
|---|------|---------------------|------------|
| 2.1 | FE cutover: default `/today` uses 4-surface ScreenFlow | `?core_loop=1` becomes default; no regression in ship gate walkthrough — **done 2026-08-29** (`?core_loop=1` experiment removed; `TodayCoreLoopViabilitySurface` deleted; audit doc `docs/audits/TODAY_4_SURFACE_CUTOVER_2026-08-29.md`) | G1 |
| 2.2 | Theme / Action / Progress first-class | `TODAY_CANON_VS_CODE_DIFF.md` closed with new facts — **done 2026-08-29** (status updated to CLOSED; Phase 2.2 closure section added; route map and block table reflect post-cutover state) | 2.1 |
| 2.3 | Evening as time-gated surface | No evening block in morning scroll — **done 2026-08-29** (`TodayProductScreenFlow.showEvening`; `TodayCompositionSurface` gates by `getTimeOfDayByHour()`; audit doc `docs/audits/EVENING_TIME_GATE_2026-08-29.md`) | 2.1 |
| 2.4 | Caller audit: replace `build()` with `build_cached_or_baseline` | No LLM-on-read GETs in Today/Compat/Tarot/Account — **done 2026-08-28** (`test_tarot_daily_explain_no_llm_v1.py` green; audit doc `docs/audits/CALLER_AUDIT_LLM_ON_READ_2026-08-28.md`) | G1 |
| 2.5 | Provenance: `snapshot_id` in Tarot/Compat generation logs | `core_profile_snapshot_id` present in Tarot/Compatibility generation logs and Compatibility job result payload — **done 2026-08-28** (`test_compat_generation_provenance_v1.py` + `test_tarot_spread_context_provenance_v1.py` green; audit doc `docs/audits/TAROT_COMPAT_PROVENANCE_2026-08-28.md`) | 2.4 |
| 2.6 | Profile Selection audit | Report: which of ~24 IL-3 themes K3 uses / ignores / competes on — **harness implemented**, live K3 run blocked on billing top-up | 2.4 |

**Gate G2:** Today cutover stable and Personal Model read-path closed.

---

### Phase 3 — Content & iOS Parity (Week 3–5)

| # | Task | Acceptance Criteria | Depends On |
|---|------|---------------------|------------|
| 3.1 | Practice Library 26/26 sourced | `content_coverage_matrix_v1.json`: 26 covered, 0 seed; `content_library_v1.json` not `llm_provisional` — **9/26 covered 2026-08-29** (`need.sleep.prepare` sourced via `technique.sleep`; next cell `need.sleep.discipline`) | 1.6 |
| 3.2 | Finalize skipped techniques | `box_breathing`, `energizing_breath`, `self_trust` — either accepted or permanently skipped with reason | 3.1 |
| 3.3 | iOS parity wave 1 | Catalog, Reports, Forecast, Library, Discover, Growth surfaces present per `IOS_TODAYFLOW_STATUS.md` | G2 |
| 3.4 | Maps surfaces cleanup | No orphan `/affirmations/tracker`, `/asceticisms/tracker`; routes unified under `/maps/*` — **done 2026-08-29** (redirects in `next.config.mjs`; orphan pages deleted; links updated to `/maps/wish` and `/maps/ascetic`; iOS deep-link routing updated; backend docstring updated) | G2 |
| 3.5 | Profile Selection Engine | Deterministic selection of ~24 IL-3 themes; repeatable portraits — **v0 implemented** in `services/il4_selection_v1.py`; **object→topic connections implemented** (planets/houses/angles/signs → `ProfileTopicDomain`); usage audit waits for K3/billing | 2.6 |

**Gate G3:** content P0 complete and iOS P0 surfaces present.

---

### Phase 4 — Launch Readiness (Week 5–6)

| # | Task | Acceptance Criteria | Depends On |
|---|------|---------------------|------------|
| 4.1 | Update stale launch docs | `WEB_LAUNCH_EXECUTION_PLAN.md` archived or marked SUPERSEDED; this plan current | G2 |
| 4.2 | Production deploy runbook | Manual deploy runbook documented (`docs/operations/DEPLOY_RUNBOOK_V1.md`); `.github/workflows/deploy.yml` validates tests, frontend build, and compose/image build | G3 |
| 4.3 | Monitoring live | Alerts for 402s, `/today` availability, LLM daily spend, behavior test metrics | G0 |
| 4.4 | Final QA | All CI green, server check on live, open critical issues = 0 | 4.1–4.3 |
| 4.5 | Go / no-go decision | Recorded in `PRODUCT_EXECUTION_TRACKER.md` | 4.4 |

**Gate G4:** launch ready.

---

## 4. Parallel Tracks (non-blocking)

| Track | Velocity | Start After |
|-------|----------|---------------|
| Practice Library fill | 1 cell / week | Phase 0 | // now at 10/26, next `need.motivation.activate`
| iOS parity wave 1 | 1 surface / week | Phase 2 cutover stable |
| Selection Engine design | 1 pass / week | Phase 2 caller audit |
| Design System Task 3 | Best effort | Phase 2+ |

---

## 5. Immediate Next Steps (today / tomorrow)

1. Phase 2.6 Profile Selection audit: harness is ready (`services/il3_profile_usage_audit_v1.py`); wait for K3/billing top-up, then run it against a real Profile Decode response. Do not blindly cut to 5–8.
2. Fix Token Factory billing / top-up.
3. Run 4-step COGS baseline and record USD.
4. Assign owner for end-to-end walkthrough Run 3 and fill the checklist in `BEHAVIOR_CHANGE_TEST_V0.md`.
5. Freeze new features — no new surfaces, no JTBD packs, no iOS-as-blocker.

---

## 6. Changelog

| Date | Change |
|------|--------|
| 2026-08-28 | v1.0 — Release Plan created; supersedes `WEB_LAUNCH_EXECUTION_PLAN.md` for active execution. |
| 2026-08-28 | Task 2.4 Caller audit closed; `GET /tarot/daily/explain` no longer calls LLM; audit doc added. |
| 2026-08-28 | Task 2.5 Provenance closed; `core_profile_snapshot_id` plumbed through Tarot/Compatibility generation logs; audit doc added. |
| 2026-08-28 | Profile Selection Engine connections: deterministic object→topic mapping (planets/houses/angles/signs) + tests; audit doc added. |
| 2026-08-29 | Profile Selection K3 usage audit harness implemented; blocked on live K3 run until billing top-up. |
| 2026-08-29 | Phase 4.2 Production deploy runbook implemented: `docs/operations/DEPLOY_RUNBOOK_V1.md`; `.github/workflows/deploy.yml` rewrite in local diff (push blocked by token workflow scope). |
| 2026-08-29 | Phase 2.3 Evening time-gated surface implemented: `showEvening` prop in `TodayProductScreenFlow`, gated by `getTimeOfDayByHour()` in `TodayCompositionSurface`; audit doc `docs/audits/EVENING_TIME_GATE_2026-08-29.md`. |
| 2026-08-29 | Phase 2.1 FE cutover: default `/today` uses 4-surface ScreenFlow; `?core_loop=1` experiment and `TodayCoreLoopViabilitySurface` removed; audit doc `docs/audits/TODAY_4_SURFACE_CUTOVER_2026-08-29.md`. |
| 2026-08-29 | Phase 2.2 Theme / Action / Progress first-class: `docs/status/TODAY_CANON_VS_CODE_DIFF.md` closed with new facts; default path now Theme-first 4-surface ScreenFlow, evening time-gated. |
| 2026-08-29 | Phase 3.4 Maps surfaces cleanup: orphan `/affirmations/tracker` and `/asceticisms/tracker` removed; redirects to `/maps/wish` and `/maps/ascetic`; links and iOS deep-link routing updated. |
|| 2026-08-29 | Practice Library fill progress: `need.sleep.discipline` sourced via `technique.sleep_discipline`; 10/26 P0 cells covered; next cell `need.motivation.activate`. |
| 2026-08-29 | Practice Library fill progress: `need.sleep.prepare` sourced via `technique.sleep`; 9/26 P0 cells covered; next cell `need.sleep.discipline`. |
|| 2026-08-29 | Content Library Selection v1: deterministic need→item selector implemented in `services/content_library_selection_v1.py`; exposed as `GET /practices/select`; 12 + 5 tests passed; canon doc added. |
