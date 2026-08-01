# Tarot Knowledge Base v1

**Статус:** ACTIVE (2026-07-25) — content SoT for Context Pack · stack frozen ([engine](./TAROT_INTERPRETATION_ENGINE_V1.md))  
**Тип:** reference / meaning facts (не user-facing prose)  
**Владелец:** Product + Content  
**Связанные:** [TAROT_INTERPRETATION_ENGINE_V1.md](./TAROT_INTERPRETATION_ENGINE_V1.md) · `DATA/astrology_reference/tarot_full_deck.json` (identity) · Machine Contract vectors remain separate (`DATA/reference/tarot/machine/`)

---

## 0. Зачем

Engine умеет собирать pack и вызывать LLM. Качество ответа упирается в **семантические факты** карт, а не в новые ветки кода.

Knowledge Base = факты для LLM. **Не** готовые абзацы ответа. **Не** шаблоны «если Шут+работа → …».

---

## 1. SoT stack

| Слой | Путь | Роль |
|------|------|------|
| Card identity | `DATA/astrology_reference/tarot_full_deck.json` | id, `name_ru`, suit |
| **Base meanings (system)** | `DATA/reference/tarot/card_base_v1/cards.json` | upright/reversed **user-facing base** — [TAROT_CARD_BASE_V1.md](./TAROT_CARD_BASE_V1.md) |
| **Semantic facts (KB v1)** | `DATA/reference/tarot/knowledge_v1/cards.json` | архетип + Q1 profile fields for packs |
| Machine vectors | `DATA/reference/tarot/machine/` | DayModel / numeric axes — **не** текст интерпретации |
| Pack builder | `tarot_interpretation_engine_v1._meaning_range` | merge KB → pack `meaning_range` |
| Day-bridge / instruction | chorus + optional gen | не переписывает `card_base_v1` |
| Question answer prose | LLM | author ответа на вопрос — поверх base + pack |

`card_base_v1` — единственный словарь базовых значений для всех tarot-поверхностей. KB не заменяет его.

Rebuild: `scripts/build_tarot_knowledge_v1.py` (committed JSON = runtime SoT).

---

## 2. Card record (v1 base + Q1 deepen)

### 2.1 Base fields (already in pack)

| Field | Meaning |
|-------|---------|
| `central_archetype` | одно ядро (не синоним названия) |
| `light` / `shadow` | светлые / теневые грани |
| `inner_conflict` / `outer_expression` | внутри / снаружи |
| `domains.*` | relationships / work / money / growth |
| `reversed.*` | central / themes / trap |
| `amplifies_questions` / `intensifies_with` / `softens_with` | связи |
| `upright_themes` / `reversed_themes` | короткие темы |

**Editorial reverse school:** `reversed.central` / `reversed.themes` = classical **тень / блок / перекос** (as majors). Do **not** switch suit-by-suit to soft “internalized same theme” reverses. Scene (`central`) ≠ first theme tag. Detail: [TAROT_CARD_BASE_V1.md](./TAROT_CARD_BASE_V1.md) §5.

### 2.2 Q1 semantic profile (minors — editorial deepen)

**Цель Q1:** каждая из 56 младших карт — **уникальный психологический архетип**, не комбинация rank × suit.

| Field | Meaning |
|-------|---------|
| `core_scene` | какая человеческая ситуация изображена |
| `central_conflict` | внутреннее противоречие карты |
| `driving_need` | чего человек пытается добиться |
| `shadow_pattern` | типичная ловушка |
| `growth_direction` | куда ведёт зрелое проживание |
| `work_lens` | работа / роль |
| `relationship_lens` | отношения |
| `money_lens` | деньги / материя |
| `inner_lens` | внутренний рост / состояние |
| `reversed_shift` | как меняется динамика в перевороте (не «просто наоборот») |
| `adjacent_distinction` | чем отличается от соседних рангов той же масти |

**Gate:** если нельзя ответить «чем 9 Кубков отличается от 8 и 10» — карта не готова.

**Тест:** [engine](./TAROT_INTERPRETATION_ENGINE_V1.md) principle *card-name ablation*.

**Запрещено:** абзацы-ответы; «Аркан»; категоричные предсказания; Profile-paste; копипаст suit×rank без `adjacent_distinction`.

---

## 3. Pack projection (engine)

`meaning_range` получает KB fields +:

- `domain_lens` — один доменный факт под вопрос
- `intensifies_drawn` / `softens_drawn` — имена карт из текущего расклада
- Q1 fields when present (`core_scene`, `central_conflict`, …) — facts for LLM, not prose

Public `tarot_answer_v1` **не** меняется.

---

## 4. Coverage policy

| Slice | Policy |
|-------|--------|
| Majors 0–21 | Hand-authored; keep rich; optional Q1 fields |
| Minors 22–77 | **Q1 required:** unique archetype profile (SoT = `scripts/tarot_minors_q1_archetypes.py` → rebuild JSON) |
| Missing Q1 on minor | Build/validate fails; pack incomplete |

---

## 5. Acceptance

- [x] Schema + loader + 78 base records
- [x] Pack prefers KB when present
- [x] Q1: all 56 minors have full semantic profile + non-empty `adjacent_distinction`
- [ ] Card-name ablation pass on sample spreads
- [ ] Golden Dataset / Eval (separate track; after Q1)
