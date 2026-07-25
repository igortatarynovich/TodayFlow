# Tarot Interpretation Engine v1

**Статус:** ACTIVE (2026-07-25) — **architecture correction: LLM is author**  
**Тип:** generation / meaning contract (SoT для ответа расклада)  
**Владелец:** Product + Backend  
**Связанные:** [SCREEN_CONTRACTS_V1.md](../SCREEN_CONTRACTS_V1.md) §6.4–§6.5 · [PRODUCT_GENERATION_CONTRACTS.md](../PRODUCT_GENERATION_CONTRACTS.md) · [TAROT_DESIGN_LANGUAGE_V1.md](./TAROT_DESIGN_LANGUAGE_V1.md)

---

## 0. Зачем

Tarot долго вёл себя как склейка шаблонов (или Profile/Today с подстановкой названий). Качественный разбор не требует заранее написанного абзаца на каждую карту и отдельной ветки под каждый расклад.

**Правильная модель:**

```
Deterministic Tarot Context Pack → LLM interpretation → validation → UI
```

**Не:**

```
Deterministic templates → склейка → UI
```

**Продуктовая единица:** один вопрос → символический материал → одна картина → прямой (не категоричный) ответ → один шаг.

---

## 1. Pipeline

| Stage | Owner | Output |
|-------|--------|--------|
| 1. Resolve cards | Code | `name_ru`, suit/arcana, orientation, position — or **block** |
| 2. Context Pack | Code | Facts only for LLM (never user-facing prose author) |
| 3. LLM interpretation | Model | Four blocks of reading prose |
| 4. Validation | Code | Schema + bans («Аркан», empty, Profile paste) |
| 5. UI | FE | Same four blocks for every spread |

Template/suit banks may exist **only** as pack facts or as **emergency fallback** when LLM is unavailable — never as the preferred author.

---

## 2. Hard gates (deterministic)

| Gate | Правило |
|------|---------|
| **Resolved cards** | Каждая карта → `name_ru` из `tarot_full_deck.json` `0…77` |
| **No «Аркан»** | Запрещено в pack, LLM output и UI |
| **Unresolved → no story** | `unresolved_cards.length > 0` → technical fallback, no LLM |
| **Profile** | В pack — **короткий релевантный фрагмент** (напр. decision_style). Запрещено дословно вставлять длинный Profile-параграф как готовый ответ |
| **Position role** | Pack сообщает роль: gain / risk / weights / step / … — LLM обязан учитывать |

---

## 3. Context Pack (facts for LLM)

Для каждой карты:

- название (`name_ru`);
- major / minor + масть;
- upright / reversed;
- базовый диапазон смыслов (themes / keywords / catalog upright·reversed);
- значение масти (если minor);
- роль позиции + prompt позиции;
- соседи (имена соседних карт).

Для пользователя/сессии:

- точный вопрос;
- `spread_id` / title / kind (`choice` · `one_card` · `general` · …);
- `concern_domain`;
- краткий `profile_relevant` (1–2 поля max);
- `response_shape` (какие блоки обязательны; для choice — сравнить A/B внутри `question_story`).

**Запрещено класть в pack готовые абзацы-ответы** («сейчас карты скорее не советуют…»).

---

## 4. LLM job (universal prompt)

Четыре действия:

1. Объяснить, что обычно символизируют ключевые карты и масти.
2. Показать, как значения меняются из-за позиции и ориентации.
3. Связать карты с вопросом и только релевантной частью профиля.
4. Дать прямой, но не категоричный ответ и один конкретный следующий шаг.

**Правило голоса:** не пересказывай карты по одной как список. Сначала символический материал → единая картина → ответ на вопрос.

JSON output:

```yaml
symbols_overview: string   # Что здесь показывают карты
question_story: string     # Как это связано с вопросом (+ A/B если choice)
direct_answer: string      # Ответ на вопрос
next_step: string          # Что сделать дальше
option_a_note: string|null # optional choice
option_b_note: string|null
confidence_note: string|null
```

---

## 5. Public contract (`tarot_answer_v1`)

```yaml
tarot_answer_v1:
  contract_version: tarot_answer_v1
  synthesis_mode: tarot_llm_v1 | tarot_fallback_v1 | unresolved_blocked
  synthesis_status: ok | unresolved_cards | llm_unavailable
  unresolved_cards: { card_id, position_id, reason }[]
  main_answer: string              # ← direct_answer
  story_narrative: string          # ← question_story
  symbols_overview: string         # ← symbols_overview
  insights:
    holding: string | ""           # optional tension excerpt; not required for UI v1
    shifting: string | ""
    attention: string | ""
  today_suggestion: string         # ← next_step
  choice_story:                    # optional projection for choice spreads
    option_a_summary: string
    option_b_summary: string
    recommended_next_step: string
    confidence_note: string
  profile_lens: string | null      # meta: what was sent in pack
  profile_lens_applied: boolean
```

UI blocks (any spread):

1. Что здесь показывают карты (`symbols_overview`)
2. Как это связано с твоим вопросом (`story_narrative` / choice notes)
3. Ответ на вопрос (`main_answer`)
4. Что сделать дальше (`today_suggestion`)

---

## 6. SoT

| Слой | SoT |
|------|-----|
| Card identity | `DATA/astrology_reference/tarot_full_deck.json` |
| Meaning ranges (facts) | deck keywords + major theme lists in pack builder |
| User-facing prose | **LLM** (`tarot_interpretation_llm_v1`) |
| Structure / gates | code |
| Public fields | `tarot_answer_v1` |

Editorial default: reject-invalid LLM → thin fallback. **Do not** hard-overwrite good LLM prose with formula banks.

---

## 7. Non-goals

- Hand-authored work+Moon+Devil+Fool branch as primary path
- Hundreds of if/else combination texts
- Suit-templates as final narrative author
- iOS/Android parity (follow-up)

---

## 8. Acceptance

- [ ] Live path prefers LLM when configured
- [ ] Pack never emits «Аркан»
- [ ] Unresolved blocks LLM
- [ ] UI shows four universal blocks
- [ ] Choice spreads compare A/B inside `question_story` / notes — same voice
- [ ] Fallback is thin + marked `tarot_fallback_v1`, not rich fake tarot voice
