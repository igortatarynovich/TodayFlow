# Personal Model — code compliance audit (2026-07-21)

**Статус:** audit (канон уже есть; новых принципов нет)  
**Метод:** сверка существующих SoT с backend call sites  
**Канон (читать, не дублировать):**

- [TODAYFLOW_PRODUCT_MODEL.md](../TODAYFLOW_PRODUCT_MODEL.md) — Personal Model · экраны = проекции  
- [PERSONAL_INTELLIGENCE_LAYER.md](../PERSONAL_INTELLIGENCE_LAYER.md) — Experience → CUM → результат → signal  
- [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](../DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md) — snapshot write / module read  
- [PROFILE_CONTENT_CANON_V1.md](../PROFILE_CONTENT_CANON_V1.md) — read-path без portrait LLM  

**Формат строк:** канон → фактический код → нарушение → минимальное исправление.

**P0 status (2026-07-21 code):** read-path `build()` closed · portrait publisher gate · Compat life_path from Personal Model · GenerationLog snapshot provenance.  
Tests: `tests/test_core_profile_read_path_no_llm_v1.py`.

**P1 next:** [PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md](./PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) — единый Experience slice (не C3).

---

## 0. Вердикт

| Слой | В каноне | В коде |
|------|----------|--------|
| CoreProfileSnapshot таблица + hash | да | **есть** (`core_profile_snapshots`, `profile_hash`) |
| Portrait LLM только на publish/job | да | **P0 done** — `build(publish_portrait=True)` only; GET → cached/baseline |
| Today first paint читает snapshot без LLM | да | **да** (`build_cached_or_baseline`) |
| CUM на каждом Experience | да | **частично** — endpoint без LLM; Experiences still rarely consume CUM |
| Knowledge Atoms / ILR / Prompt Refinement | да | **частично / backlog** (см. PIL status table) |
| Compatibility life_path | Snapshot / shared numerology | **P0 done** — preferred from Snapshot/store; else shared `NumerologyService` |
| Snapshot provenance on generations | diagnostic | **P0 done** — `log_generation` enriches hash/version/`generated_from_snapshot` |
| `profile_content_v1` architecture | target | **не wired** в API (tests/evals only) — C3 next |

Главный разрыв P0 (LLM-on-read) **закрыт**. Остаётся P1: Experiences реально читают CUM/contract slice; Compat `profile_a/b` = snapshot payload.

---

## 1. Где создаётся CoreProfileSnapshot

| | |
|--|--|
| **Модель** | `db/models.py` → `CoreProfileSnapshot` (`user_id`, `profile_hash`, `profile_version`, `payload`) |
| **Запись** | `CoreProfileService._save_snapshot()` из `build()` после `build_profile_portrait_v1()` |
| **Hash** | SHA1: name/gender/birth/location/sun/life_path/expression + prompt versions (`core_profile.py`) |
| **Чтение** | `_load_snapshot(user_id, profile_hash)`; также «latest» helpers в morning/narrative/editors |

**Канон:** snapshot = единственный published портрет.  
**Факт:** snapshot пишется при успешном `build()`.  
**Нарушение:** нет отдельного job-only publish; любой caller `build()` может создать/обновить портрет.  
**Fix:** `build()` → только job / explicit refresh; modules → `build_cached_or_baseline` или load-by-hash.

---

## 2. Compact User Model

| | |
|--|--|
| **Сборка** | `build_compact_user_model_v0(db, user_id, core_profile, …)` |
| **Endpoint** | `GET /account/compact-user-model` → внутри сначала `service.build()` (**LLM risk**) |
| **Persist** | ephemeral; отдельно `cum_confidence_snapshots` |

**Канон (PIL):** каждый экран читает CUM.  
**Факт:** CUM почти никто из Today/Compat/Tarot не вызывает; FE может дергать endpoint, но backend pipelines обходят.  
**Нарушение:** Experience → narrative/LLM без CUM slice.  
**Fix:** (1) CUM endpoint на `build_cached_or_baseline`; (2) day_story / compat / tarot context принимают CUM или тот же snapshot slice, что и Profile UI.

---

## 3. Что реально получают модули

| Модуль | Канон | Факт | Нарушение | Минимальный fix |
|--------|-------|------|-----------|-----------------|
| **Today** (`/today`, contract, sync) | Snapshot/CUM, без portrait LLM | `build_cached_or_baseline` | нет (read-path OK) | держать; не переводить на `build()` |
| **morning_ritual** | то же | `build_cached_or_baseline` | нет | — |
| **day_story** | snapshot id в fingerprint | fingerprint + snapshot id есть | слабый CUM | передавать decision_style/helps из snapshot contract, не сырой birth |
| **POST /today/narrative** | CUM → refine → LLM | `build()` | **да** — LLM-on-read | `build_cached_or_baseline` |
| **Compatibility signs/natal GET** | Snapshot | `build_cached_or_baseline` | нет для strip | — |
| **Compatibility content v1** | Snapshot A×B | `profile_a`/`profile_b` dict + signs; `source_depth` | **частично** — не гарантия, что dict = `core_profile_snapshots.payload` | брать payload snapshot по profile id; запретить personality claims при `zodiac_only`/`birth_dates` |
| **compatibility_engine** | numerology из Snapshot | life_path **пересчёт** из birth_date | **да** | читать `numerology.life_path` из snapshot |
| **Tarot spread context** | Snapshot | `build()` в `tarot.py` | **да** | `build_cached_or_baseline` |
| **Tarot synthesis / guidance LLM** | Snapshot + domain | modular profile dict; нет snapshot_id в логах | **да** (трассировка) | обязательный `core_profile_snapshot_id` в GenerationLog |
| **GET /account/core-profile** | publish или cached | `build()` | **да** | cached read; refresh = POST job |
| **GET /account/compact-user-model** | CUM from snapshot | `build()` | **да** | cached |
| **GET /natal-chart** | calc + snapshot editorial | `build()` | **да** | cached + editorial job |
| **Questions / day_flow / numerology day** | Snapshot | `build()` | **да** | cached |
| **profile_content_v1** | target architecture | не wired в API | **docs/code gap** | wire publish gate или не ссылаться как prod |

---

## 4. Кто обходит PIL

Канон PIL: Experience → read CUM → output → write signal.

| Путь | Обход |
|------|--------|
| Today composition / day_story | Нет полного CUM; есть snapshot/baseline + ritual context — **частичный PIL** |
| Compatibility LLM | Часто signs/dates + optional profile dict — **обход CUM** |
| Tarot spread context | `build()` вместо CUM — **обход + LLM risk** |
| Account profile GETs | `build()` — **обход job-publish** |
| Knowledge write-back | signals/atoms есть точечно; Contradiction/C17 ranking — **не в hot path** |

---

## 5. Повторный пересчёт тех же birth/profile inputs

| Место | Что повторяется | Риск разъезда | Fix |
|-------|-----------------|---------------|-----|
| `compatibility_engine` life_path | digits(birth_date) | другой reduce/master, чем в Snapshot | читать Snapshot |
| Sign resolve в Compat по дате | zodiac from date | обычно стабильно | OK если тот же helper, что natal |
| Natal attach на каждом build | engine re-run | perf, не personality | cache by birth fingerprint |
| Portrait funnel на GET | новый LLM текст при cache miss | **противоречия между экранами** | never LLM on GET |

---

## 6. Fingerprint / version

| Артефакт | version/hash | Статус |
|----------|--------------|--------|
| CoreProfileSnapshot | `profile_hash`, `profile_version` | OK |
| day_story | fingerprint + `profile_snapshot_id` | OK |
| Compatibility cache | TTL 7d; sense_fingerprint в content_v1 | partial — не всегда profile_hash A/B |
| Tarot synthesis | часто без snapshot_id | **gap** |
| CUM | `contract_version`, `generated_at` | ephemeral OK; caller must pin snapshot |

Без общего `profile_hash` в GenerationLog модуля два запроса с теми же birth data могут дать разный «характер».

---

## 7. Документы vs код (PIL checklist)

Из [PERSONAL_INTELLIGENCE_LAYER.md](../PERSONAL_INTELLIGENCE_LAYER.md) status table (сверка 2026-07-21):

| Компонент | Канон | Код |
|-----------|-------|-----|
| CoreProfileSnapshot | ✅ | ✅ |
| CUM builder | ✅ | ✅ (endpoint only) |
| Interpretation Layer | ✅ canon | частичный `interpretation_engine_v0` — не полный ILR gate |
| User Knowledge Model / atoms table | ✅ canon | частичный (CUM top_k / active knowledge) — не полный UKM SoT |
| Prompt Refinement Engine | ✅ | ⬜ / bundle в narrative slices |
| Contradiction Events C15 | ✅ | не найден hot path |
| Decision Relevance C17 ranking | ✅ | не найден в CUM rank |

---

## 8. Compatibility: snapshot или локальный payload?

**Канон:** два Profile Snapshot.  
**Факт `compatibility_content_v1`:**

- `resolve_source_depth(profile_a_ready, profile_b_ready, has_signs)`  
- в prompt уходят `profile_a` / `profile_b` как dict  

**Вывод:** это **не автоматически** строки из `core_profile_snapshots`. Нужна проверка call site: откуда dict (astro profile row vs snapshot payload vs ad-hoc). Пока depth может быть `two_profiles` при «готовых» dict, собранных локально — **риск локальной личности**.

**Минимальный fix:**  
`profile_a_ready` только если загружен `CoreProfileSnapshot.payload` (или published profile_contract) для entity id; иначе max depth = `birth_dates` / `zodiac_only`.

---

## 9. Prioritized minimal fixes (код, не доки)

### P0 — DONE 2026-07-21

1. ~~Read-path `build()` → cached/baseline~~ — `build()` defaults to no LLM; `publish_portrait=True` required.  
2. ~~Portrait publisher~~ — `POST /account/core-profile/refresh` + core-setup / astro save.  
3. ~~Compat life_path from Personal Model~~ — `_life_path_from_personal_model` + engine preferred args.  
4. ~~Snapshot provenance~~ — `snapshot_id` on payload; `learning.log_generation` enriches; tarot merges provenance.

### P1

5. Today/Compat/Tarot принимают один и тот же snapshot slice (contract fields: decision_style, conflict_style, helps…).  
6. Compat `profile_*_ready` = snapshot exists.  
7. Experiences call CUM (not only Profile UI).

### P2 / C3

8. Wire или явно пометить `profile_content_v1` как non-prod; **then** C3 Profile quality audit.  
9. PIL Prompt Refinement / C15 / C17 — по существующему backlog.  
10. FIRST_DAY auth-first → align Blueprint (execution docs).

---

## 10. Что сознательно не делать

- Не вводить новый «Canonical Personal Knowledge Principle» / третий базовый закон.  
- Не плодить параллельный Snapshot schema рядом с `core_profile_snapshots` + PIM.  
- Не писать новый Product Model — чинить callers.

---

## Changelog

| Дата | |
|------|--|
| 2026-07-21 | Первый code compliance pass по Snapshot / CUM / module callers |
| 2026-07-21 | P0 implemented: publisher gate, Compat life_path, provenance |
