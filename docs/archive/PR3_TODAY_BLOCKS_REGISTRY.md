# Today Production Blocks Registry (PR-3 entry)

**Status:** ACTIVE — Composition Surface honesty pass  
**Depends on:** [PR2_APP_SHELL.md](../PR2_APP_SHELL.md) · [PR3_TODAY_PRODUCTION_SURFACE.md](./PR3_TODAY_PRODUCTION_SURFACE.md) · `day_story_v1` explainable trace  
**Rule:** no Source / Appear-when → block is not designed.

---

## Block gate (каждый блок Today)

Перед появлением в production Composition блок обязан ответить на три вопроса:

1. **Почему появился?** — `Source` + `Appear when` (нет источника → нет блока).
2. **Что понял за 10–20 секунд?** — одно meaning-facing сообщение, не кухня.
3. **Что сделать сегодня?** — конкретное действие из контракта, не invent.

| Поле паспорта | Соответствие gate |
|---------------|-------------------|
| Source / Appear when | Почему появился |
| Ready copy / Contract fields | Что понял |
| Primary action / No-data | Что сделать / честный empty |

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
| Why (10–20s) | |
| User can do | |
| Loading / Ready / Empty / Partial / Error | |
| No-data | |
| Foundation surface | |

---

## Confirmed blocks (from live contracts)

### T1 · Day story (authoritative narrative)

| Field | Value |
|-------|-------|
| Block | Day story reading |
| Route | `/today` |
| Component | `TodayPersonalizedProductSection` via `TodayCompositionSurface` |
| Source | `GET /today/contract` → `day_story` (+ `trace`) |
| Contract fields | theme, direction, story, advantage, abstain, today_move, **trace.derived_claims** |
| Appear when | Authenticated + contract ready with `day_story` |
| Why (10–20s) | Soft «Почему это важно сегодня» **только** из `trace.derived_claims` (meaning kinds). Нет claims → блок скрыт. `practice_recommendation.reason` остаётся в detail инструмента, не как soft why. Limitations никогда. |
| User can do | Прочитать; зафиксировать обещание своими словами |
| Empty / Partial | Fallback story with `trace.used_fallback`; hide absent domains |
| Error | ProductShell error + retry |
| No-data | Do not invent prose client-side |

### T2 · Domain lenses (partial)

| Field | Value |
|-------|-------|
| Block | Domain accents (relationships / money_work / family) |
| Source | `contract.domains.*.evidence_status` |
| Appear when | `evidence_status === "present"` and slots non-empty (`isDomainLensPresent`) |
| Why (10–20s) | Только если есть present evidence |
| User can do | Учесть акцент в lean/ease reading |
| No-data | **Hide** when absent |

### T3 · Strengthen / practice (honest)

| Field | Value |
|-------|-------|
| Block | One strengthen tool |
| Source | `day_story.practice_recommendation` (`kind` ≠ `none` + `text`) |
| Appear when | Recommendation present; catalog overlay **only** if practice slot already exists |
| Why (10–20s) | `reason` or soft why from claims |
| User can do | Start/complete practice or read affirmation — when kind maps |
| No-data | **Hide zone** — no five-tool invent |

### T4 · Day symbol reveal

| Field | Value |
|-------|-------|
| Block | Card / number reveal |
| Source | `/today/symbols/*` · morning ritual · day_symbol_state |
| Appear when | Ritual path / reveal state |
| No-data | Redacted until reveal |

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
| Soft “почему” from kitchen `trace.limitations` | Kitchen text — never user-facing |
| Synthesis symbol tags on product reading | Removed — competed with single voice |

---

## Next Surface step

1. ~~FE domain honesty~~ · ~~strengthen invent~~ · ~~soft why from claims~~  
2. Smoke on prod Composition: one reading line + optional soft why + optional one tool.  
3. Typography / motion only after this honesty pass holds.
