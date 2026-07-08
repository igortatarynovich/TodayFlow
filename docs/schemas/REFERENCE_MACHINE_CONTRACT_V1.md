# Reference Machine Contract v1 — JSON Schema

**Статус:** принято (P0.2).  
**Схема:** [reference_machine_contract_v1.schema.json](./reference_machine_contract_v1.schema.json).  
**CI:** job `reference-machine-contract-schema` → `scripts/validate_reference_machine_contract.py`.  
**Связь:** [DAYMODEL_INPUT_CONTRACT.md](../DAYMODEL_INPUT_CONTRACT.md), [REFERENCE_LAYER_AND_BUILD_ORDER.md](../REFERENCE_LAYER_AND_BUILD_ORDER.md).

---

## Назначение

Валидатор **формы** Machine Contract для Reference Layer. Запрещает:

- лишние поля (`additionalProperties: false` на корне и `machine_contract`);
- пропуск обязательных полей;
- vector scores вне диапазона **−1…+1**;
- невалидные `tempo`, `risk`, `emotional_load`;
- отсутствие `confidence`;
- смешивание Machine и Content (поля вроде `advice`, `keywords`, `content_contract` не допускаются на корне).

**Content Contract** — отдельная схема (будущий `reference_content_contract_v1.schema.json`), не в этом файле.

---

## Корневая запись

```json
{
  "contract_version": "reference_machine_contract_v1",
  "domain": "tarot",
  "entity_code": "tarot.major.07",
  "entity_type": "TarotCard",
  "version": "1.0.0",
  "status": "draft",
  "source_type": "expert",
  "valid_from": "2026-05-31",
  "machine_contract": { }
}
```

| Поле | Обяз. | Смысл |
|------|-------|--------|
| `contract_version` | да | Константа `reference_machine_contract_v1` |
| `domain` | да | `tarot` \| `numerology` \| `astrology` \| `emotional_state` |
| `entity_code` | да | Стабильный код (`tarot.major.07`, `numerology.core.7`, …) |
| `version` | да | Semver записи (`1.0.0`) |
| `status` | да | `draft` \| `review` \| `active` \| `deprecated` \| `archived` |
| `machine_contract` | да | См. ниже |
| `entity_type` | нет | Тип из taxonomy (§6 REFERENCE_LAYER) |
| `source_type` | нет | `system` \| `expert` \| `ai_assisted` |
| `valid_from` | нет | ISO date |

---

## `machine_contract` — Tarot / Numerology / Astrology

Единая форма для доменов, питающих DayModel (P0.2):

```json
{
  "vector": {
    "action_reflection": 0.8,
    "expansion_consolidation": 0.3,
    "self_others": -0.2,
    "structure_flow": 0.7
  },
  "tempo": "fast",
  "risk": "medium",
  "risk_modifier": 0.2,
  "emotional_load": "intense",
  "confidence": 0.75
}
```

| Поле | Тип | Диапазон / enum |
|------|-----|-----------------|
| `vector.action_reflection` | number | −1 … +1 |
| `vector.expansion_consolidation` | number | −1 … +1 |
| `vector.self_others` | number | −1 … +1 |
| `vector.structure_flow` | number | −1 … +1 |
| `tempo` | string | `slow` \| `steady` \| `dynamic` \| `fast` |
| `risk` | string | `low` \| `medium` \| `high` |
| `risk_modifier` | number | −1 … +1 |
| `emotional_load` | string | `calm` \| `neutral` \| `intense` |
| `confidence` | number | 0 … 1 |

---

## `machine_contract` — Emotional State

Check-in / operating mode (отдельная ветка схемы):

```json
{
  "emotional_load": "intense",
  "tempo_cap": "steady",
  "energy_band": "low",
  "stress_band": "medium",
  "risk_modifier": 0.3,
  "confidence": 1.0
}
```

Обязательны: `emotional_load`, `risk_modifier`, `confidence`.

---

## P0.3 — Tarot Major Machine Drafts

**Путь:** `DATA/reference/tarot/machine/` — 22 файла `00_fool.json` … `21_world.json`.

- Legacy `DATA/astrology_reference/tarot_major_arcana.json` **не трогаем** (content layer).
- Machine layer — только записи, проходящие эту схему.
- CI: валидатор проверяет все `*.json` в каталоге (ровно 22, `entity_code` `tarot.major.00` … `21`).

**Следующий шаг:** P0.5 — Numerology machine drafts (тот же schema + loader domain path).

### P0.4 — DayModel v1 preview (tarot-only)

Контрактный тест, **не** полноценный DayModel:

| Модуль | Путь |
|--------|------|
| Loader | `backend/src/todayflow_backend/data/reference_machine_loader.py` |
| Aggregator | `backend/src/todayflow_backend/services/day_model_v1_aggregator.py` |
| Tests | `backend/tests/test_day_model_v1_aggregation.py` |

`aggregate_day_model_v1_preview_tarot("tarot.major.07")` → `day_model_v1_preview` с полями vector, tempo, risk, risk_modifier, emotional_load, confidence, sources. Без Numerology/Astrology, без LLM, без UI.

---

## Локальная проверка

```bash
pip install -r scripts/requirements-contract-validation.txt
python scripts/validate_reference_machine_contract.py
```
