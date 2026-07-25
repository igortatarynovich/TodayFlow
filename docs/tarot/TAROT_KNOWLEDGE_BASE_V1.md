# Tarot Knowledge Base v1

**Статус:** ACTIVE (2026-07-25) — content SoT for Context Pack  
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
| Card identity | `DATA/astrology_reference/tarot_full_deck.json` | id, `name_ru`, suit, catalog upright/reversed |
| **Semantic facts (KB v1)** | `DATA/reference/tarot/knowledge_v1/cards.json` | архетип, свет/тень, конфликт, домены, reversed, amplify, intensify/soften |
| Machine vectors | `DATA/reference/tarot/machine/` | DayModel / numeric axes — **не** текст интерпретации |
| Pack builder | `tarot_interpretation_engine_v1._meaning_range` | merge KB → pack `meaning_range` |
| User prose | LLM | единственный author ответа |

Rebuild from authoring script: `scripts/build_tarot_knowledge_v1.py` (optional; committed JSON is runtime SoT).

---

## 2. Card record (semantic)

Per `card_id` `0…77`:

| Field | Meaning |
|-------|---------|
| `central_archetype` | одно ядро (не синоним названия) |
| `light` | 2–5 светлых граней (фразы-факты) |
| `shadow` | 2–5 теневых граней |
| `inner_conflict` | что тянет человека внутри |
| `outer_expression` | как это видно снаружи / в ситуации |
| `domains.relationships` / `work` / `money` / `growth` | короткие факты по сфере |
| `reversed.central` | ядро в перевороте |
| `reversed.themes` | 2–4 темы |
| `reversed.trap` | типичная ловушка переворота |
| `amplifies_questions` | типы вопросов, где карта особенно сильна |
| `intensifies_with` | card_id[], обычно усиливают смысл |
| `softens_with` | card_id[], обычно смягчают / балансируют |
| `upright_themes` / `reversed_themes` | короткие темы для pack/UI strip |

**Запрещено:** абзацы-ответы; «Аркан»; категоричные предсказания; Profile-paste.

---

## 3. Pack projection (engine)

`meaning_range` получает KB fields +:

- `domain_lens` — один доменный факт под `question_domain`
- `intensifies_drawn` / `softens_drawn` — имена карт **из текущего расклада**, попадающие в intensify/soften

Public `tarot_answer_v1` **не** меняется (architecture freeze).

---

## 4. Coverage policy

| Slice | Policy |
|-------|--------|
| Majors 0–21 | Hand-authored rich facts |
| Minors 22–77 | Suit × rank semantic matrix + per-card polish; must not collapse to shared suit keywords only |
| Missing card | Engine falls back to legacy thin themes / catalog; log once |

---

## 5. Acceptance

- [x] Schema + loader + 78 records in `cards.json`
- [x] Pack prefers KB when present (`knowledge_source=tarot_knowledge_v1`)
- [x] Domain lens + intensify/soften within spread
- [ ] Owner live text scoring after KB lands (existing eval harness)
- [ ] Editorial pass: majors deep review · minors weak cards rewritten
