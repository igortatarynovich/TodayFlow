# DAY_LIFECYCLE_V1 — когда собирается и выдаётся день

**Status:** CANON DRAFT — **C4.1 + C5 + C5.1–C5.3 landed**  
**Date:** 2026-07-26  
**Related:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md) · [DAY_SCENARIO_DRAMATURGY_BRIEF_C4.md](./DAY_SCENARIO_DRAMATURGY_BRIEF_C4.md) · [DAY_STORY_GENERATION_LIFECYCLE_V0.md](./DAY_STORY_GENERATION_LIFECYCLE_V0.md) · push `DEFAULT_SCHEDULE`

## Product rule

**День собирается один раз на `(user, local_date)` и не пересобирается от каждого GET.**

Пользовательский цикл:

1. Утром день уже готов → пуш «Твой день готов»
2. Открыл → читает → карта / число → дальше по сценарию
3. Делает предложенное или своё
4. Вечером закрывает сам **или** система закрывает за него
5. После close / в pre-dawn окне собирается следующий день
6. Запрос до `ready_at` (например час ночи) → `day_not_ready` + время готовности

## Clock (user local TZ)

| Параметр | Дефолт | Роль |
|----------|--------|------|
| Date boundary | local midnight | ключ `local_date` |
| Quiet hours | 22:00–08:00 | уже в push |
| Assemble window | 05:00–07:00 | pre-warm до morning push |
| Ready push | `morning_time` 08:30 | только если product-ready scenario |
| Close deadline | 23:00 или следующий assemble | system close |
| Not-ready | midnight → `ready_at` | час ночи = ещё не готов |

## Runtime today (honest)

| Правило | Сейчас |
|---------|--------|
| Одна сборка | **частично** — GET не зовёт LLM; refresh/enrichment могут переписать |
| Serve ready native | **да** (C4 delivery fix) |
| Pre-dawn assemble cron | **да (C5.1)** — `run_day_lifecycle_due` в `/internal/push/run-due`, окно 05–07, budget/run |
| Push on ready | **да (C5.2)** — `morning_rhythm` только если ready scenario; copy «Твой день готов» |
| System evening close | **да (C5.3)** — `DayConnection.evening_completed` + `evening_observations.system_close_c5` |
| `day_not_ready` gate | **да (C5)** — shell до `ready_at`; FE wait surface |

## C5 clock

Public progress nest:

```json
"progress": {
  "day_lifecycle": {
    "contract_version": "day_lifecycle_c5",
    "status": "day_not_ready | ready | closed",
    "local_date": "YYYY-MM-DD",
    "ready_at": "<ISO with offset>",
    "ready_time": "08:30",
    "close_time": "23:00",
    "timezone": "Europe/Warsaw",
    "assemble_window": { "start": "05:00", "end": "07:00", "active": false }
  }
}
```

- Query: `GET /today/contract?timezone=…&target_date=…`
- `closed` ← `DayConnection.evening_completed` (user or system)
- Engine: `day_lifecycle_clock_c5.py`

## C5.1–C5.3 jobs

Hook: same cron `POST /internal/push/run-due` → `run_day_lifecycle_due` then `run_due_notifications`.

| Job | When | Behavior |
|-----|------|----------|
| Pre-warm | local 05:00–07:00 | force assemble if no ready native/det; max 8 rebuilds/run; users with push devices |
| Ready push | `morning_time` window | skip + `blocked_not_ready` until scenario ready (no mark-sent) |
| System close | ≥23:00 today; or ≥05:00 catch-up for yesterday | set evening_completed; marker `system_close_c5` |

Engine: `day_lifecycle_jobs_c5.py`

```markdown
## Architecture impact
- **SoT before:** wall-clock morning push «открой Today»; no server evening close; no pre-warm
- **SoT after:** morning push gated on product-ready day_scenario; pre-warm in assemble window;
  system close writes DayConnection/DayRitual; progress.day_lifecycle.status may be closed
- **Public contract changed?** yes — day_lifecycle.close_*; push copy; run-due response.lifecycle
- **Migration required?** no
- **Canon updated?** yes — this doc
- **Backward compatible?** yes; clients ignore new fields
```

## Implementation order (status)

1. **C4.1 Delivery integrity** — landed
2. **C5 Lifecycle clock** — landed
3. **C5.1 Pre-warm job** — landed
4. **C5.2 Ready push** — landed
5. **C5.3 System close** — landed

Ops: crontab every 10 min → `scripts/run_day_lifecycle_cron.sh` → `POST /internal/push/run-due` (needs `PUSH_DISPATCH_SECRET`). Cover 05–09 and 22–00 local bands for active TZs.
