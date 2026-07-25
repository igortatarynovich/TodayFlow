# Tarot Interpretation Engine v1

**Статус:** ACTIVE (2026-07-25)  
**Тип:** generation / meaning contract (SoT для ответа расклада)  
**Владелец:** Product + Backend  
**Связанные:** [SCREEN_CONTRACTS_V1.md](../SCREEN_CONTRACTS_V1.md) §6.4–§6.5 · [PRODUCT_GENERATION_CONTRACTS.md](../PRODUCT_GENERATION_CONTRACTS.md) · [TAROT_DESIGN_LANGUAGE_V1.md](./TAROT_DESIGN_LANGUAGE_V1.md)

---

## 0. Зачем

Tarot показывает карты, но долго вёл себя как Profile/Today с подстановкой названий: шаблонные склейки, повтор вопроса, дословный Profile-параграф, fallback «Аркан».

**Продуктовая единица:** один вопрос → один конфликт → сравнение путей (если расклад про выбор) → один конкретный вывод.

Карты — аргументы внутри ответа, не шесть независимых трактовок.

---

## 1. Hard gates

| Gate | Правило |
|------|---------|
| **Resolved cards** | Каждая карта расклада должна резолвиться в `name_ru` из полной колоды `0…77`. |
| **No «Аркан»** | Строка «Аркан» / «то, что просит быть замеченным» **запрещена** в production narrative. |
| **Unresolved → no story** | Если `unresolved_cards.length > 0`: не публиковать полноценный ответ; technical fallback + mapping error в generation log; UI предлагает пересобрать / открыть снова. |
| **Profile** | Experience slice может влиять на **тон** next step. **Запрещено** дословно вставлять `decision_style` / identity в основной ответ. |
| **Position × card** | Одна карта в «даёт» / «риск» / «учитывать» / «шаг» трактуется по роли позиции, не одной универсальной фразой. |

---

## 2. Общий выход (`tarot_answer_v1`)

Сохраняются legacy-поля для клиентов. Добавляются поля Interpretation Engine:

```yaml
tarot_answer_v1:
  contract_version: tarot_answer_v1
  synthesis_mode: interpretation_engine_v1 | unresolved_blocked
  synthesis_status: ok | unresolved_cards
  unresolved_cards: { card_id, position_id, reason }[]
  main_answer: string          # direct_answer — одна мысль на вопрос
  story_narrative: string      # отношения карт, не список «карта → фраза»
  insights:
    holding: string            # что мешает / удерживает
    shifting: string           # где сдвиг / контраст путей
    attention: string          # что заметить (без Profile-paste)
  today_suggestion: string     # один практический шаг
  # choice spreads only (optional nest):
  choice_story:
    option_a_summary: string
    option_a_gain: string
    option_a_risk: string
    option_b_summary: string
    option_b_gain: string
    option_b_risk: string
    hidden_tension: string
    recommended_next_step: string
    confidence_note: string
  profile_lens: string | null  # meta only — не UI body
  profile_lens_applied: boolean
```

При `synthesis_status: unresolved_cards` поля ответа — technical fallback; `choice_story` отсутствует.

---

## 3. Расклад «Выбор между двумя вариантами»

**Spread ids:** `guidance_choice_two` · `choice`

**Позиции → роли:**

| position_id | Роль |
|-------------|------|
| `a_gives` / option A gain | что даёт путь A |
| `a_risk` | риск пути A |
| `b_gives` | что даёт путь B |
| `b_risk` | риск пути B |
| `weights` | скрытое напряжение / что нельзя игнорировать |
| `best_step` | лучший следующий шаг в реальности |

**Формула смысла:**  
`карта × ориентация × роль позиции × вопрос × соседние карты`

**Структура UI (один рассказ):**

1. Главный вывод (`main_answer`)
2. Сравнение A / B (`choice_story` + сжатый `story_narrative`)
3. Что мешает увидеть решение (`insights.holding` ← `hidden_tension`)
4. Следующий шаг (`today_suggestion` ← `recommended_next_step`)

**Удалить / не дублировать:** отдельные блоки «История» + «Ответ» + «Почему важно» + «Что говорят карты» с одним и тем же смыслом.

**Мост:** один контекстный primary CTA (для work/decision choice — «Зафиксировать условия решения»), плюс опционально «Сохранить расклад». Не меню из пяти продуктовых ссылок как главный финал.

---

## 4. SoT текста

| Слой | SoT |
|------|-----|
| Имя карты | `DATA/astrology_reference/tarot_full_deck.json` → `name_ru` |
| Голос major (0–21) | curated speak bank в Interpretation Engine |
| Голос minor (22–77) | suit × orientation × position-role templates (v1); later — dedicated RU bank |
| Сборка ответа | `tarot_interpretation_engine_v1` / `compose_question_first_reading` |
| Публичный контракт | `tarot_answer_v1` |

Editorial default: fill-empty / reject-invalid. Не hard-overwrite чужого LLM-текста постфактум (v1 = template engine).

---

## 5. Non-goals v1

- Полный LLM-авторский слой для всех 78 карт
- iOS/Android parity (отдельный item после web)
- Смена ritual / deck assets

---

## 6. Acceptance

- [ ] Ни один live result не содержит «Аркан» / «просит быть замеченным» как fallback
- [ ] Minor ids 22–77 резолвятся в `name_ru`
- [ ] `unresolved_cards` блокирует narrative
- [ ] Profile paragraph не появляется в `insight_attention` / UI body
- [ ] `guidance_choice_two` сравнивает A и B и даёт один next step
- [ ] Result UI не повторяет один смысл в четырёх блоках
