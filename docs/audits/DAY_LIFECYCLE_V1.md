# DAY_LIFECYCLE_V1 — когда собирается и выдаётся день

**Status:** CANON — assemble-once clock locked 2026-07-26; **ready_at → 05:00** (2026-08-03)  
**Date:** 2026-08-03  
**Related:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md) · [DAY_SYMBOL_REVEAL_CANON_V1.md](./DAY_SYMBOL_REVEAL_CANON_V1.md) · [DAY_SCENARIO_DRAMATURGY_BRIEF_C4.md](./DAY_SCENARIO_DRAMATURGY_BRIEF_C4.md) · push `DEFAULT_SCHEDULE`

## Product rule (SoT)

**День собирается один раз на `(user, local_date)` сервером. Пользовательский запрос день не собирает.**

Мы сами считаем и раскладываем пакет дня (сценарий, рекомендации, астро/небо, цвет/камень, **карта**, **число** и т.д.). Пользователь только открывает готовое: красивая загрузка → чтение → ритуал (reveal) → продолжение. Ритуал **не** пересобирает день и **не** должен затирать уже показанный контент.

Карта и число — слой интерпретации уже собранного дня (как эта карта/число сказываются именно сегодня). Identity карты/числа **заранее** лежит в `day_symbol_states`; ритуал только открывает (reveal).

### Когда (local TZ пользователя)

| Событие | Время (default) | Поведение |
|---------|-----------------|-----------|
| Date boundary | local midnight | новый `local_date` |
| **Assemble window** | **03:00–05:00** | cron pre-warm: полная сборка пакета дня (до ready) |
| Catch-up | после `ready_at`, если пакет ещё не ready | cron дособирает (не GET) |
| **Ready** | **`ready_at` = morning_time / 05:00** | пуш «Твой день готов»; UI отдаёт пакет |
| До `ready_at` | midnight → ready_at | `day_not_ready` — «день ещё не готов», без сюжета |
| После ready, пакет нет | — | `assembling` shell + красивая загрузка; **без** LLM на GET |
| System close | ≥23:00 | закрытие дня системой |
| Следующий день | close / следующее assemble окно | новая сборка |

### Пользовательский цикл

1. К **05:00** день уже готов → пуш **«Твой день готов»** (только если пакет product-ready)
2. Открыл Today → **сразу пользуется** готовым пакетом (кэш / быстрый GET serve-only). Никаких пересборок, enrichment-poll и долгой загрузки «сборки»
3. Ритуал: карта / число (reveal only) → дальше по сценарию; контент дня на месте
4. Делает предложенное или своё
5. Вечером закрывает сам **или** система закрывает за него
6. До `ready_at` (например час ночи) → `day_not_ready` + время готовности

## Public progress nest

```json
"progress": {
  "day_lifecycle": {
    "contract_version": "day_lifecycle_c5",
    "status": "day_not_ready | assembling | ready | closed",
    "local_date": "YYYY-MM-DD",
    "ready_at": "<ISO with offset>",
    "ready_time": "05:00",
    "close_time": "23:00",
    "timezone": "Europe/Warsaw",
    "assemble_window": { "start": "03:00", "end": "05:00", "active": false }
  }
}
```

## Runtime (honest)

| Правило | Сейчас |
|---------|--------|
| Одна сборка / не по GET | **да** — GET `allow_rebuild_on_miss=False`; miss → assembling shell |
| Serve ready native | **да** |
| Pre-warm cron 03–05 + catch-up | **да** (`run_day_lifecycle_due`) — celestial + fusion + symbols; candidates: **AstroProfile (self/primary)** + push + schedule + recent DayConnection/MeaningEvent/DayStoryState |
| Prebake card+number | **да** (в pre-warm; reveal только открывает) |
| Push on ready | **да** — gated on product-ready scenario; default `morning_time`/`quiet_end` **05:00** |
| System evening close | **да** |
| `day_not_ready` gate | **да** |
| Reveal ≠ rebuild | **да** (`symbol_overlay_only`) |
| GET assembling → background catch-up | **да** — enqueue `day_prewarm` job (daemon); **no LLM on GET** |

## C5.1–C5.3 jobs

Hook: cron `POST /internal/push/run-due` → `run_day_lifecycle_due` then `run_due_notifications`.

| Job | When | Behavior |
|-----|------|----------|
| Pre-warm | local 03:00–05:00 **или** после ready_at если пакет не ready | assemble story/scenario + prebake symbols; max 8 rebuilds/run |
| Ready push | `morning_time` window (default 05:00) | skip + `blocked_not_ready` until scenario ready |
| System close | ≥23:00 today; or ≥03:00 catch-up for yesterday | `evening_completed` + `system_close_c5` |

Engine: `day_lifecycle_clock_c5.py`, `day_lifecycle_jobs_c5.py`

```markdown
## Architecture impact
- **SoT before:** ready_at / morning_time default **08:30**; assemble **05:00–07:00**; quiet_end **08:00**
- **SoT after:** ready_at / morning_time default **05:00**; assemble **03:00–05:00** (finish before ready); quiet_end **05:00** so morning push is not quiet-blocked
- **Public contract changed?** yes — `progress.day_lifecycle.ready_time` / `ready_at` / `assemble_window` defaults; earlier morning gate
- **Migration required?** soft — existing `UserPushSchedule.morning_time` / `quiet_end` rows keep stored values; new rows and no-schedule users use 05:00
- **Canon updated?** yes — this doc
- **Backward compatible?** yes for clients that read `ready_at` dynamically; fixed 08:30 copy would be wrong
```

## Implementation order (status)

1. **C4.1 Delivery integrity** — landed
2. **C5 Lifecycle clock** — landed
3. **C5.1 Pre-warm job** — landed (+ catch-up + symbol prebake)
4. **C5.2 Ready push** — landed
5. **C5.3 System close** — landed
6. **Assemble-once hard gate (GET never builds)** — landed 2026-07-26
7. **Ready_at → 05:00** — landed 2026-08-03

Ops: crontab every 10 min → `scripts/run_day_lifecycle_cron.sh` → `POST /internal/push/run-due` (needs `PUSH_DISPATCH_SECRET`, `--max-time 600`). Cover **03–06** and 22–00 local bands for active TZs. Missed openers: GET assembling enqueues background `day_prewarm` job.
