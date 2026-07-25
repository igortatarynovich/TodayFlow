# Character Engine — Architecture Impact (D1–D4)

**Status:** ACCEPTED — Architecture Impact for Character Engine wiring  
**Version:** 1.0 (2026-07-25)  
**Input SoT:** [CHARACTER_ENGINE_RUNTIME_INVENTORY_V0.md](./CHARACTER_ENGINE_RUNTIME_INVENTORY_V0.md)  
**Canon:** [PROFILE_EXPERIENCE_SCENARIO_V1.md](../profile/PROFILE_EXPERIENCE_SCENARIO_V1.md)  
**Parent rule:** root `AGENTS.md` · `.cursor/rules/architecture-impact.mdc`

**Не входит в этот документ:** полная JSON/schema структура полей. Schema — следующий трек **после** принятия D1–D4.

---

## Architecture impact (summary)

| | |
|---|---|
| **SoT before** | `profile_contract_v1` (± disclosure funnel / oneshot / `interpretation.life_areas`) как de-facto portrait; matrix dual roots; GET ephemeral projections |
| **SoT after** | Единый **Character Engine** в `core_profile_snapshots.payload.character_engine_v1`; legacy DTO = deterministic adapters; funnel/oneshot killed at cutover |
| **Public contract changed?** | yes — после schema+cutover: новый nest `character_engine_v1`; legacy fields остаются как projections до reader migration |
| **Migration required?** | yes — staged pipeline · Shadow · adapters · reader cutover · kill old roots |
| **Canon updated?** | yes — Scenario §8 · this doc · inventory §6 closed |
| **Backward compatible?** | transitional yes via adapters; long dual-SoT publish **запрещён** |

---

## D1 — Где живёт versioned Character Engine Snapshot

### Verdict

```text
core_profile_snapshots.payload.character_engine_v1
```

**Не** создавать отдельную таблицу `character_engine_snapshots` сейчас.

### Почему

`core_profile_snapshots` уже:

- publish destination;
- источник `GET /account/core-profile`;
- точка кэша;
- носитель `profile_contract_v1`;
- чтение Profile + Experience assembler.

Вторая snapshot-таблица = инфраструктурный dual-SoT (кто опубликован первым, partial success, active id, downstream foreign keys) **до** удаления смыслового dual-SoT.

### Целевая ответственность envelope

`core_profile_snapshots` = **publish envelope**. Внутри payload:

- metadata публикации · status · input/fact versions;
- **`character_engine_v1`** (единственный смысловой portrait);
- временные legacy projections (adapters);
- generation diagnostics (в т.ч. shadow), не второй portrait.

На переходном этапе `profile_contract_v1` = **совместимая проекция** из `character_engine_v1`, не второй портрет.

### Write authority

Единственный writer: `CoreProfileService._publish_portrait`.

Publish transaction:

1. получить / обновить facts;  
2. построить Character Engine (стадии D3);  
3. собрать adapters (D4);  
4. валидировать;  
5. атомарно опубликовать snapshot.

`GET` — без LLM и без сборки нового смысла.

### Когда отдельная таблица всё же нужна

Только при реальных требованиях (сейчас в inventory нет): история версий как продукт · несколько активных моделей по времени · независимая ретенция больших evidence-графов · отдельные ACL · partial CE update без Core Profile publish.

---

## D2 — Evidence Graph ↔ raw facts ↔ claims

### Verdict

Evidence Graph = **внутренний слой** Character Engine (не UI-проза, не ссылки, размазанные по слотам).

Цепочка:

```text
raw_fact_id → evidence_edge → claim_id → cascade section
```

### Сущности

**Raw fact** (детерминированный / вычисленный): Солнце, Луна, ASC, дом, аспект, life path, китайский год, тибетский элемент, …

Поля: `fact_id` · `fact_type` · value · calc source · capability · calculation version · confidence/authority · provenance.

**Claim** (тезис о человеке): автономия, «сначала анализ потом действие», напряжение близость↔независимость, …

Поля: `claim_id` · normalized thesis · cascade role · supporting evidence · contradicting evidence · confidence · eligibility/capability · generation stage.

**Evidence edge** (typed, не только «supports»):

- `supports` · `strengthens` · `qualifies` · `contradicts` · `limits` · `contextualizes`

### Authority для вычислимых астро/числовых фактов

**Swiss Ephemeris + deterministic calculators** = authority для положений, домов, аспектов, углов, координат, вычислимой нумерологии.

`profile.natal_facts.v1` — временно **нормализатор / bridge**, не математический SoT. LLM **не** создаёт новые астрономические факты.

Граница:

| Layer | Роль |
|-------|------|
| Calculator / reference | что фактически существует |
| Evidence Graph | как факты связаны с тезисами |
| LLM | связная интерпретация **только** в пределах facts + evidence candidates |

### Не хранить в Evidence Graph

UI-абзацы · энциклопедии планет/домов · editorial · советы · Compass · paraphrase-дубли claims.

Evidence Graph = объяснимость и происхождение смысла.

---

## D3 — Один проход vs управляемые стадии

### Verdict

**Управляемый staged pipeline** с одним смысловым корнем и **атомарной** публикацией.

Не monolithic LLM-call.  
Не старый disclosure funnel (параллельные prompt roots).

### Почему не один проход

Сложно валидировать одно ядро · provenance · contradictions из Internal Engine · отделение Compass · partial failure · пропуск актов · непрозрачный shadow.

### Почему не funnel

Сегодняшние стадии (`identity` / `styles` / `patterns` / `spheres` / `chart_reading`) имеют право **заново** определить человека = несколько semantic roots.

### Стадии

| Stage | Имя | LLM? | Выход |
|-------|-----|------|-------|
| **0** | Facts assembly | no | normalized raw facts · capabilities · missing · calc versions |
| **1** | Evidence + claim candidates | constrained | claims · edges · conflicts · confidence · exclusions (**ещё не книга**) |
| **2** | Identity core + source roles | yes | **одно** ядро · роли источников; reject: списки качеств, равные ядра, claims без evidence, энциклопедия |
| **3** | Internal Engine + tensions | yes | decision/perception/stress/risk/recovery/growth/burnout · primary + secondary tensions; **нельзя менять ядро** — иначе validation failure |
| **4** | Scenes · potential · blind spots | yes | из core + engine + primary tension — **не** из ярлыков career/love/money |
| **5** | Deterministic assembly | **no** | Compass · legacy adapters · ExperienceSlice · matrix/projection · availability · explainability refs |
| **6** | Final narrative projection (optional) | yes, rendering | путь личности / редакционная цельность; **не** новые claims; не меняет модель |

### Publish semantics

Внутренние stage artifacts допустимы.  
Наружу — только завершённый валидный CE Snapshot.

Запрещено состояние: новое ядро опубликовано + старые life areas ещё SoT + Compass из старой модели.

### Prompt IDs (наблюдаемость)

| Role | ID |
|------|-----|
| Новый recipe / stages | **`profile.character_engine.v1`** (+ stage-specific versions) |
| Legacy baseline до kill | `profile.personality.v1` (только shadow/legacy) |

Не переиспользовать один и тот же prompt id для радикально другой schema — иначе generation logs смешивают эпохи.

Версионировать **отдельно**:

- snapshot contract: `character_engine_v1`;
- generation recipe: `character_engine_recipe_v1`;
- stage prompt IDs;
- projection adapter version.

---

## D4 — Legacy fields до reader migration

### Verdict

После cutover конкретного snapshot старые поля собираются **только** deterministic adapters из CE.

**Запрещён dual publish:** CE + независимо сгенерированные `relationship_style` / career / `life_spheres`.

### Adapters (примеры)

| Legacy field | ← CE source |
|--------------|-------------|
| `identity_summary` / `identity_core` | identity core |
| `decision_style` | Internal Engine · decision |
| `emotional_style` | perception / stress / recovery claims |
| `relationship_style` | scenes (intimacy) + relevant tension |
| career / work slots | scenes (responsibility / competition / success) |
| money slots | scenes (resource / risk / security) |
| `strengths` | repeated enabling mechanisms → Compass |
| blind spots | CE blind spots |
| `helps` | Compass actions |
| `life_spheres` | grouped scene projections |
| `interpretation.life_areas` | deprecated compatibility DTO ← scenes |

Adapters **не** вызывают LLM · не добавляют claims · не переписывают значение · не подмешивают zodiac encyclopedia · не гоняют отдельную taxonomy.

### Shadow comparison

Сравнивает CE vs legacy **diagnostics only** — legacy **не** входит в опубликованный SoT после cutover.

Метрики: semantic overlap · contradictions · unsupported claims · missing useful content · regen stability · reader completeness · house/capability correctness.

Legacy builders могут крутиться в фоне publish / batch → только diagnostics.

### Reader migration order

1. Profile Web V2  
2. Profile iOS  
3. ExperienceSlice / Compact User Model  
4. Today  
5. Tarot  
6. Compatibility (две модели + pair-semantics — позже)  
7. Secondary surfaces / reports  

### Kill sequencing

**Сразу после CE publish cutover** (feature flag off):

- disclosure funnel · oneshot  
- `profile.identity.v1` · `styles.v1` · `patterns.v1` · `chart_reading.v1`  
- spheres synthesis как генератор  

**После web/iOS migration:** FE V0 taxonomy · sphere meaning rewrite · iOS `interpretation.life_areas` primary · Personal Lens  

**После downstream:** thematic career/love roots · natal editorial character invent · numerology identity explainer · compat editorial person-fragments  

### Transition window = milestones, не календарь

- CE shadow passes  
- Profile web cut over  
- Profile iOS cut over  
- required adapters covered  
- rollback snapshot available  

После этого legacy generation roots **выключены flag**, cleanup файлов может идти позже.

### Forming shell

Forming = UX/status envelope (facts ready · pending · failed · retry).  
**Не** сохранять старый identity рядом с неполным CE как одну модель.

### Ephemeral GET projections

`profile_matrix_v0` · `portrait_why_v0` · `insight_nodes_v0` · `effort_vector_v0` · `bridge_line_v0` допустимы **только** как чистые функции:

- читают опубликованный snapshot;  
- детерминированы;  
- не добавляют claims;  
- versioned assembler;  
- воспроизводимы из snapshot.

Иначе — в publish pipeline или удалить.

---

## Migration invariants (жёстко)

1. Один active portrait SoT на profile hash: `character_engine_v1`.  
2. Один write authority: `_publish_portrait`.  
3. GET без LLM / без новой personality.  
4. Нет длительного dual publish двух character arcs.  
5. Shadow ≠ SoT.  
6. Adapters = pure projections.  
7. Funnel / oneshot не переживают cutover как live path.  
8. UI Profile до cutover не закрепляет `life_areas` / taxonomy как SoT.

---

## Next (после принятия этого документа)

1. Schema contracts: `character_engine_v1` + Evidence Graph + adapter map (без полной prose catalog).  
2. Recipe `character_engine_recipe_v1` + stage prompt IDs.  
3. Pipeline implementation behind flag · Shadow harness.  
4. Cutover Profile web → iOS → ExperienceSlice → Today → Tarot → Compat.  
5. Kill flags · cleanup.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-25 | v1.0 — D1–D4 ACCEPTED from inventory; no full JSON schema yet |
