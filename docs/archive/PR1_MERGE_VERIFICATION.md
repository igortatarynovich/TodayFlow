# PR1 — merge verification (evidence, not design)

**Дата:** 2026-06-23  
**Статус:** **READY FOR MERGE** (оба binary gate пройдены 2026-06-23)  
**Код:** Gate 1 **IN PROGRESS** → **READY FOR MERGE**

---

## Binary gates — результат (2026-06-23)

### Gate 1 — Live S5 (3 api_live дня → Daily Focus copy)

Проверка **восприятия**, не regex. Payloads: `generation_logs` id **688**, **671**, **657** (guide, ru).

| log | S5 title | S5 line | Восприятие |
|-----|----------|---------|------------|
| 688 | Этот день не требует размаха. | Источники в основном согласованы | ✓ описание, не инструкция |
| 671 | Этот день не требует размаха. | Источники в основном согласованы | ✓ |
| 657 | Этот день не требует размаха. | Источники в основном согласованы | ✓ |

**До правки sentence-filter:** title содержал «выбрать один приоритет», lines — «Что происходит» + чек-ин metadata → **FAIL** по продуктовому критерию.  
**После:** `buildDailyFocusModel` берёт первое описательное предложение из `day_model.vector`, отсекает guidance и internal dump.

**Experience Gate:** ✓

### Gate 2 — Live PIM audit (один реальный проход)

Скрипт: `backend/scripts/pr1_live_pim_audit_pass.sh` → Docker `:8080`, Postgres.

| Артефакт | Значение |
|----------|----------|
| `generation_log_id` | **692** |
| `meaning_events` (6 типов) | day_opened, day_sky_fact_viewed, tarot_selected, tarot_revealed, number_selected, first_synthesis_viewed |
| `first_synthesis_viewed.payload.generation_id` | **692** (= log id) |
| `orchestration.pim_read_audit` | present, contract `today_pim_read_audit_v1` |
| `dre_fields_used` | 8 полей (ritual_context.*, fusion_dump.scores, layers.day_model, …) |

**Architecture Gate (live):** ✓ — Experience → Signals → DRE → Generation **не на бумаге**.

---

## Вердикт PR1

PR1 доказал главное: **Today читает PIM** (read-path auditable). Goal Loop / write-path — **PR2**.

**PR1: READY FOR MERGE.**

---

## Проверка №1 — S5 boundary (результат, не код)

**Риск:** `guide` payload несёт `best_move`, `do_hint`, imperative `core_message` — PR1 не должен показывать их в S5.

**Защита в коде:** `todayDailyFocusBoundary.ts` + `buildDailyFocusModel` берёт только `core_message.body` (не `best_move`/`risk`), не `do_hint`, фильтрует guidance-паттерны; fallback — `day_engine_brief.anchor_summary`.

**Фикстуры (jest `todayDailyFocus.test.ts`):**

| Кейс | Вход | Ожидание |
|------|------|----------|
| User ❌ bad | «стоит сосредоточиться… обсуди до обеда» | `isDailyFocusGuidanceLeak` = true, в S5 не попадает |
| User ✅ good | «внимание смещается… разговоры важнее планов» | в `lines`, без «до обеда» |
| Hidden guidance | `best_move` + `do_hint` в payload | joined title+lines **без** «до обеда», «звонок» |
| Body-only leak | imperative body | fallback на `anchor_summary` |

**Перед merge — руками:** 3 реальных дня `/today` → S5 текст читается как **описание**, не инструкция. Если LLM стабильно льёт imperative в `body` — это TL-1, не расширение PR1 scope.

---

## Проверка №2 — PIM read не фиктивный

**Риск:** audit есть, `dre_fields_used[]` всегда `[]`.

**Факт из unit tests (`test_today_pim_read_audit_v1.py`):**

### Day 1 (пустой slice)

```json
{
  "pim_slice_used": { "atom_count": 0, "atom_ids": [] },
  "dre_fields_used": [
    "fusion_dump.scores",
    "ritual_context.numerology_value",
    "ritual_context.tarot_main_id"
  ]
}
```

→ **Путь есть**, atoms пустые — OK для day-1.

### Day N (slice с atoms)

```json
{
  "pim_slice_used": { "atom_count": 2, "atom_ids": ["k1", "k2"] },
  "dre_fields_used": ["layers.knowledge_context_slice", ...]
}
```

→ **Тот же контракт**, непустой slice — доказывает, что audit реагирует на knowledge.

**Где живёт audit:** `generation_logs.input_payload.orchestration.pim_read_audit` (после `POST /today/narrative`, surface=guide).

**Перед merge — SQL/лог sample:** один проход S0–S5 → вытащить `pim_read_audit` из последнего generation log; убедиться `dre_fields_used` **не пустой** при ritual_context.

---

## PIM Diff (шаблон для PR description)

После **одного** полного прохода S0–S5:

| Артефакт | Ожидание |
|----------|----------|
| `meaning_events` | 6 типов: `day_opened`, `day_sky_fact_viewed`, `tarot_selected`, `tarot_revealed`, `number_selected`, `first_synthesis_viewed` |
| `generation_logs` | 1+ row surface=guide с `ritual_context` |
| `pim_read_audit` | `pim_slice_requested` + `pim_slice_used` + `dre_fields_used` length ≥ 1 |

---

## Today Disappearance

Убрать UI Today → должны остаться:

| Артефакт | Owner |
|----------|-------|
| `meaning_events` | ingestion API |
| `generation_logs` + `orchestration.pim_read_audit` | narrative pipeline |
| `daily_focus_id` в generation payload | DRE output (не только React state) |

**Fail:** synthesis только в `localStorage` без server events + generation log.

---

## Learning Δ (PR1 достаточно)

Цель PR1 = **существование потока сигналов**, не обучение личности. Шесть events + auditable read — достаточно для merge.

**PR2 stress:** Intent Record, Goal Loop, первый PIM write.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | Вердикт ~85%: Arch+Learning green; merge blockers = 3 live S5 days + 1 live generation log |
