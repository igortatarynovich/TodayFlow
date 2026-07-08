# Cross-Domain Machine Validation (CDMV)

**Статус:** принято (**P0.9 DONE** — общая система координат подтверждена).  
**Версия:** 1.1 (2026-05-31).  
**Владелец:** Product + Engineering.

**Роль:** доказать, что Machine scores **Tarot**, **Numerology**, **Astrology** говорят на **одном машинном языке** — **не** агрегировать DayModel (это **P1.0**, фаза 2 Rules).

**Freeze P0.9:** без composite JSON, без Composition Engine в prod, без Today, без LLM.

**Отчёт:** [docs/status/cross_domain_validation_v1.md](./status/cross_domain_validation_v1.md) — **PASS → P1.0 разрешён**.

**Связь:** [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md), [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md), [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) §2–§3, [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md).

---

## 0. Жёсткая формулировка

```
P0.9 = проверка общей системы координат
P1.0 = DayModel aggregation (Rules System)
```

---

## 1. Anchor set

| Domain | entity_code |
|--------|-------------|
| Tarot | `tarot.major.07` (Chariot VII) |
| Numerology | `numerology.personal_year.8` |
| Astrology | `astrology.planet.mars` + `astrology.sign.aries` |

**compose(mars, aries):** только **test helper** в `test_cross_domain_machine_validation.py` — не CD, не prod.

**Ожидание (каждый anchor + compose vector action):**

| Поле | Критерий |
|------|----------|
| `action_reflection` | > 0 (action) |
| `tempo` | ≠ `slow` |
| `risk` | ≠ `low` |
| `emotional_load` | ≠ `calm` |

**Coherence:** сильные архетипы не конфликтуют — pairwise `action_reflection` delta ≤ **0.35**.

---

## 2. Contrast set

| Domain | entity_code |
|--------|-------------|
| Tarot | `tarot.major.09` (Hermit) |
| Numerology | `numerology.core.7` |
| Astrology | `astrology.planet.saturn` |

**Ожидание:**

| Поле | Критерий |
|------|----------|
| `action_reflection` | ≤ 0.15 (reflection) |
| `tempo` | `slow` или `steady` |
| `risk` | `low` или `medium` |
| `emotional_load` | `calm` или `neutral` |

**Separation:** min(anchor action) > max(contrast action).

---

## 3. Что проверяет pytest

| # | Test | Смысл |
|---|------|--------|
| 1 | Identical scale shape | три домена — одна форма machine_contract |
| 2 | Anchor profiles | action, tempo, risk, load |
| 3 | Anchor coherence | нет конфликта сильных архетипов |
| 4 | Contrast profiles | reflection cluster |
| 5 | Anchor vs contrast | реально отличаются |
| 6 | No composite JSON | mars + aries только atoms в DATA |

**Файл:** `backend/tests/test_cross_domain_machine_validation.py`

---

## 4. Достаточность осей (решение P0.9)

| Вопрос | Ответ |
|--------|--------|
| 4 axes достаточны? | **Да** для P1.0 |
| AMC §3.1 extension нужен? | **Нет** (до transit composer, фаза 2) |
| Machine Contract менять? | **Нет** — идти в **P1.0** |

---

## 5. Definition of Done

- [x] `tests/test_cross_domain_machine_validation.py` — green  
- [x] Нет composite JSON  
- [x] Anchor + contrast проверены  
- [x] [cross_domain_validation_v1.md](./status/cross_domain_validation_v1.md)  
- [x] **Решение: P1.0 разрешён**

---

## 6. Changelog

- **1.1 (2026-05-31)** — P0.9 implemented; PASS report; P1.0 gate open; personal_year.8 tempo fix.  
- **1.0 (2026-05-31)** — CDMV canon; anchor/contrast sets.

---

*P1.0: DayModel aggregation 0.4 / 0.3 / 0.3 — фаза 2 Rules System.*
