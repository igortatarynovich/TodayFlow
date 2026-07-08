# Astrology Machine Contract (AMC)

**Статус:** принято (канон **P0.7** — структура Machine Layer для астрологии).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Роль:** определить **источник истины** для астрологического Machine Layer до drafts (P0.8), cross-domain validation (P0.9) и DayModel aggregation (**P1.0**, не раньше).

**Почему до DayModel:** DayModel по Dependency Map — Tarot 0.4 + Numerology 0.3 + **Astrology 0.3**. Агрегатор на двух доменах = временный агрегатор неполного мира ([ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md) фаза 1).

**Связь:** [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) (**atomic-only P0.8 gate**), [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) §5.3, [reference_machine_contract_v1.schema.json](./schemas/reference_machine_contract_v1.schema.json), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) §6, [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md), [CROSS_DOMAIN_MACHINE_VALIDATION.md](./CROSS_DOMAIN_MACHINE_VALIDATION.md) (P0.9).

**Freeze P0.7:** без UI, без generation, без DayModel aggregator wiring.

---

## 0. Scope P0.7 → P0.8 → P0.9 → P1.0

| Step | ID | Deliverable |
|------|-----|-------------|
| **Contract + taxonomy** | **P0.7** | этот документ; entity codes; mapping rules; schema decision |
| **Draft records** | **P0.8** | `DATA/reference/astrology/machine/` — signs, planets, houses, aspects (`draft`) |
| **Same coordinate system** | **P0.9** | [CROSS_DOMAIN_MACHINE_VALIDATION.md](./CROSS_DOMAIN_MACHINE_VALIDATION.md) — Tarot + Numerology + Astro on one scale |
| **Aggregation rules** | **P1.0** | DayModel v1 multi-source (0.4 / 0.3 / 0.3) — **фаза 2** |

Legacy `DATA/astrology_reference/*.json` — **content + calc metadata**; **не** мигрируем bulk в P0.7. Machine layer — **новые** файлы по контракту.

---

## 1. Четыре базовых reference-сущности (P0.7)

Порядок наполнения:

1. **Identity reference** (что существует) — привязка к legacy id  
2. **Machine mappings** — vector, tempo, risk, confidence на общей шкале DayModel  

| Entity | entity_type | entity_code pattern | Legacy source | P0.8 count |
|--------|-------------|---------------------|---------------|------------|
| **ZodiacSign** | `ZodiacSign` | `astrology.sign.{id}` | `zodiac_signs.json` | 12 |
| **Planet** | `Planet` | `astrology.planet.{id}` | `planets.json` | 10 (sun…pluto) |
| **House** | `House` | `astrology.house.{nn}` | `houses.json` | 12 |
| **Aspect** | `Aspect` | `astrology.aspect.{id}` | `aspects.json` | 5 major (conj, sext, square, trine, opp) |

**Ids:** lowercase slug (`aries`, `mars`, `square`, `01`…`12` zero-padded for houses).

### 1.1 Storage layout (P0.8)

```
DATA/reference/astrology/machine/
  sign_aries.json
  planet_mars.json
  house_01.json
  aspect_square.json
  ...
```

Один JSON = одна запись `reference_machine_contract_v1`, `domain: "astrology"`.

---

## 2. Machine contract — базовые сущности

### 2.1 Решение P0.7: базовый контракт **достаточен**

Для **Planet, ZodiacSign, House, Aspect** используется **тот же** `daymodel_source_machine_contract`, что у Tarot/Numerology:

```json
{
  "contract_version": "reference_machine_contract_v1",
  "domain": "astrology",
  "entity_code": "astrology.planet.mars",
  "entity_type": "Planet",
  "version": "0.1.0",
  "status": "draft",
  "machine_contract": {
    "vector": {
      "action_reflection": 0.65,
      "expansion_consolidation": 0.40,
      "self_others": 0.10,
      "structure_flow": 0.55
    },
    "tempo": "dynamic",
    "risk": "medium",
    "risk_modifier": 0.25,
    "emotional_load": "intense",
    "confidence": 0.85
  }
}
```

**Editorial mapping guidelines (draft scores P0.8):**

| Astro dimension | Vector axis bias |
|-----------------|------------------|
| Cardinal / initiating signs & Mars-like | ↑ `action_reflection`, ↑ `expansion` |
| Fixed / earth | ↑ `structure_flow`, ↓ tempo |
| Mutable / air | ↑ `structure_flow` negative (flow), balanced `self_others` |
| Benefic / trine / sextile aspect | ↓ `risk_modifier`, calmer `emotional_load` |
| Malefic / square / opposition | ↑ `risk`, ↑ `risk_modifier` |
| Saturn, 12th house themes | ↑ `structure`, ↓ tempo, reflection bias |

### 2.2 Что **не** в базовой записи

- `keywords`, `psychology`, `description` → **Content Contract** (legacy JSON или future content files)  
- `angle`, `orb` → **calc reference** в legacy `aspects.json`, не machine vector  
- `energy_0_100` → только **composite signals** (§3)

---

## 3. Composite signals (post P0.8 — **not** in Reference JSON)

DayModel §5.3 описывает **DailyAstroSignal** (transit, spine) — **производная** сущность.

**Freeze:** см. [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) — **запрещены** composite machine files в P0.8.

| Entity | Where | Create method |
|--------|-------|---------------|
| **PlanetInSign** | Composition Engine output (DD) | Derived from atoms |
| **PlanetInHouse** | Composition Engine output | Derived |
| **AspectPair / TransitSignal** | Daily Engine | Generated |
| **DailySpine** | Daily Engine | Generated |

### 3.1 Extension `astrology_signal_machine_contract` (v1.1 proposal)

Если composite signals не reducible к base atoms, добавить **optional** поля (schema `allOf` для `entity_type: TransitSignal`):

| Field | Type | Purpose |
|-------|------|---------|
| `energy_0_100` | 0–100 | Tempo partial input (DAYMODEL §5.3) |
| `direction_hint` | enum | `acceleration` \| `stabilization` \| `release` \| `focus` |
| `tension_weight` | 0–1 | multi-transit aggregation weight |
| `source_aspect_code` | string | link to `astrology.aspect.*` |

**Gate:** не менять root schema до **P0.9** cross-domain test. Если «Марс в Овне» = weighted sum of planet + sign passes P0.9 — extension **не нужен** для v1.

---

## 4. Mapping rules (legacy → machine)

### 4.1 Identity map (read-only in P0.7)

| Legacy field | Machine record |
|--------------|----------------|
| `zodiac_signs[].id` | `entity_code` suffix |
| `planets[].id` | `entity_code` suffix |
| `houses[].id` | `house_{id:02d}.json` |
| `aspects[].id` | `aspect_{id}.json` |

### 4.2 Machine score derivation (P0.8 editorial)

1. Expert draft vector/tempo/risk per entity (human, not LLM-in-prod).  
2. Cross-check polarity from legacy: `aspects[].polarity` → risk tier prior.  
3. `tension_level` string → initial `risk_modifier` band (high friction → +0.3…+0.5).  
4. `confidence`: base entities **0.80–0.95**; aspects **0.75–0.90** (interpretation variance).

### 4.3 Composition (runtime, P1.0 prep)

**Planet in Sign** (example Mars + Aries):

```
vector_composed = normalize( w_p * V_planet + w_s * V_sign )   # w_p=0.55, w_s=0.45 default draft
tempo = max_tempo(planet.tempo, sign.tempo)  # per DAYMODEL tempo merge rules
risk_modifier = planet.risk_modifier + sign.risk_modifier * 0.5, clamp [-1,1]
```

Exact weights — **P0.9** calibration against Tarot/Numerology anchors.

---

## 5. Consumers (read-only declaration)

Astrology Machine питает (позже, после P0.8+):

| Consumer | Reads | When |
|----------|-------|------|
| Profile Engine | planet, sign, house natal codes | profile build |
| Horoscope | sign, transit composites | category lenses |
| Daily Engine | transit signals, spine | day build |
| **DayModel** | aggregated astro slice | **P1.0 only** |
| Compatibility | aspect, planet_in_sign | synastry product |
| Symbolic Commerce | sign, planet themes | ranking rules |
| PIL | codes in SN, not bulk JSON | context selection |

**Запрет P0.7–P0.9:** подключать consumers до `draft` CI green + P0.9 pass.

---

## 6. Validation (P0.8 CI)

Extend `validate_reference_machine_contract.py`:

| Check | Expected |
|-------|----------|
| Sign files | 12 |
| Planet files | 10 |
| House files | 12 |
| Aspect files | 5 |
| entity_code set | exact match §1 table |
| schema | `reference_machine_contract_v1` |

Loader: `load_astrology_machine_contracts()` in `reference_machine_loader.py` — **P0.8**, not P0.7.

---

## 7. Relationship to three pillars

После P0.8 green:

| Domain | Machine layer | Status |
|--------|---------------|--------|
| Tarot | 22 major | ✅ P0.3 |
| Numerology | 39 records | ✅ P0.5 |
| Astrology | 39 atomic records | ✅ P0.8 |

**Три столпа Machine Layer на месте** → следующий шаг **P0.9** → **P1.0**.

---

## 8. Risks & contract break triggers

Астрология первая может потребовать:

| Symptom | Response |
|---------|----------|
| `tempo` enum too coarse for moon/fast transits | map `tempo_score` → enum bands in composer; or §3.1 |
| `energy_0_100` required for Tempo 40% astro weight | §3.1 on composite only |
| Multi-transit merge | `tension_weight` + aspect machine; not in P0.8 base set |
| Profile vs daily different confidence | separate `confidence` on composite, not base planet |

**Правило:** ломать schema **до P1.0**, не после.

---

## 9. Checklist P0.7 (this doc)

- [x] Entity taxonomy: Sign, Planet, House, Aspect  
- [x] entity_code conventions  
- [x] Storage path `DATA/reference/astrology/machine/`  
- [x] Base machine = existing `daymodel_source_machine_contract`  
- [x] Composite / extension documented; gate at P0.9  
- [x] Legacy map; no bulk migration  
- [x] Consumer list declared; no wiring  
- [x] P0.8 drafts + CI counts  
- [ ] P0.9 cross-domain validation  
- [ ] P1.0 DayModel aggregation  

---

## 10. Changelog

- **1.0 (2026-05-31)** — AMC v1; defer P0.6 → P1.0; four base entities; composition rules sketch; extension proposal gated at P0.9.

---

*P0.8: editorial drafts only. P1.0: aggregation — фаза 2 Rules.*
