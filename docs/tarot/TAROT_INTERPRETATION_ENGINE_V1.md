# Tarot Interpretation Engine v1

**Статус:** ACTIVE (2026-07-25) — **Interpretation Stack v1 FROZEN** until Golden Eval results  
**Тип:** generation / meaning contract (SoT для ответа расклада)  
**Владелец:** Product + Backend  
**Связанные:** [SCREEN_CONTRACTS_V1.md](../SCREEN_CONTRACTS_V1.md) §6.4–§6.5 · [PRODUCT_GENERATION_CONTRACTS.md](../PRODUCT_GENERATION_CONTRACTS.md) · [TAROT_DESIGN_LANGUAGE_V1.md](./TAROT_DESIGN_LANGUAGE_V1.md) · [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md) · [TAROT_POSITION_SEMANTICS_V1.md](./TAROT_POSITION_SEMANTICS_V1.md) · [TAROT_QUESTION_ONTOLOGY_V1.md](./TAROT_QUESTION_ONTOLOGY_V1.md)

### Interpretation Stack v1 — hard freeze (owner, 2026-07-25)

```
Question
   → Question Ontology
   → Context Pack (Card KB · Position Semantics · Profile Tint · Draw Facts)
   → LLM (один автор)
   → Validation
   → UI
```

Стек **завершён и заморожен**. До появления результатов **Golden Eval** запрещены:

- новые слои / ветки engine;
- новые поля `tarot_answer_v1`;
- отдельные prompt-ветки по типу вопроса / расклада;
- новые типы раскладов и Tarot UI как основной трек;
- любое «умное» усложнение пайплайна «ради качества».

Дальше только **редакторское качество** (три независимых направления ниже). Новый архитектурный слой без доказанного прироста на Golden Eval — отказ по умолчанию.

Ledger: `fb8cd34` · `c4bbe56` · `1e53497` (KB) · `56d753a` (positions) · `724d958` (ontology + stack freeze).

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

### Principle: LLM is author of one story

**LLM — автор, а не толкователь отдельных карт.**

Задача модели — **ответить на вопрос пользователя**, используя карты как символический материал Context Pack (KB + Position Semantics + Question Ontology + profile tint).

| Плохо | Хорошо |
|-------|--------|
| Луна = X. Дьявол = Y. Шут = Z. | Один конфликт/картина: карты складываются в **одну** историю под вопрос |
| Энциклопедия значений | Ответ + один шаг; символика объяснена естественно внутри сюжета |

Не перечислять значения карт по очереди. Validation уже банит механический список; канон закрепляет продуктовый смысл запрета.

### Principle: answer this question, not demonstrate the deck

**Каждый расклад должен ощущаться как ответ именно на этот вопрос, а не как демонстрация знаний о картах.**

Редакторский приоритет при любом выборе:

1. лучше ответить человеку;
2. чем «рассказать ещё про карту».

Если после правки текст стал богаче по символике, но слабее отвечает на вопрос — правка отклоняется.

### Principle: card-name ablation test (KB distinctness)

**Если после удаления названий карт текст почти не меняется, Knowledge Base недостаточно различает карты.**

Практика: взять несколько раскладов, убрать из ответа имена карт.

| Результат | Вывод |
|-----------|--------|
| Остаются **разные человеческие истории** | KB различает карты |
| Один и тот же текст с переставленными существительными | продолжать Q1 deepen minors |

**Слои ответственности (Interpretation Stack v1 — frozen):**

| Слой | Отвечает на |
|------|-------------|
| Knowledge Base | что символизирует карта |
| Position Semantics | как читать её в этой позиции |
| Question Ontology | какой тип решения нужен пользователю |
| LLM | одна история / ответ / шаг |
| Validation | качество и запреты |
| UI | только отображение |

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
| **Position role** | Pack несёт `position_semantics` (purpose / extract / do_not / result_type) — LLM обязан учитывать |

---

## 3. Context Pack (facts for LLM)

Для каждой карты — **диапазон**, не одна фраза:

- `central_symbol`
- `light_side` / `shadow_side`
- `upright_themes` / `reversed_themes`
- `upright_meaning` / `reversed_meaning` (catalog)
- масть + light/shadow масти (minor)
- стихия (`element` / `element_ru`)
- роль позиции + **Position Semantics** (`purpose`, `answers_question`, `extract_from_card`, `do_not`, `result_type`)
- `question_lens` (как читать под тип вопроса)
- соседи

Для сессии:

- вопрос, spread kind, **`question_ontology`** (type / domain / intent / horizon + interpretation instructions)
- `profile_relevant`: **1–2 поля, выбранные под ontology domain**  
  (work → decision_style / motivation / helps; relationship → communication/conflict; …)  
  Не натальный dump.
- `response_shape` (блоки; choice_compare; order=`conflict_first_then_answer`; next_step_kind)

**Запрещено** класть в pack готовые абзацы-ответы.

---

## 4. LLM job (universal prompt)

Порядок: конфликт → связь с вопросом → ответ → шаг.

Запреты: механический список карт; повтор вопроса >1; спам названий позиций; цитата профиля; карты как факты о внешнем мире; пустые формулы; «Аркан».

Prompt ver: `tarot-interpretation-v1.4` (single author prompt: ontology + position_semantics + KB + profile tint)

---

## 4.1 Validation / quality gates

Структура **и** качество:

| Gate | Правило |
|------|---------|
| bans | нет «Аркан», «просит быть замеченным», empty formulas |
| no profile paste | profile_relevant не скопирован дословно |
| question once | вопрос ≤1 раз во всём ответе |
| cards linked | ≥2 имён карт в тексте (если карт ≥2) |
| concrete step | next_step с действием / критерием |
| no cross-dup | блоки не дублируют друг друга |
| length | разумные пределы |
| choice | A/B notes различимы (или явный контраст в story) |

Reject → retry → иначе `tarot_fallback_v1`.

---

## 4.2 Fallback honesty

`tarot_fallback_v1` — короткий и честный:

> Не удалось собрать полноценную интерпретацию. Ниже — только базовые значения карт без персонального синтеза.

Не имитировать полноценный разбор.

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
| Meaning ranges (facts) | **Tarot Knowledge Base v1** — `DATA/reference/tarot/knowledge_v1/cards.json` · canon [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md) |
| Position function | **Position Semantics v1** — `DATA/reference/tarot/position_semantics_v1/roles.json` · [TAROT_POSITION_SEMANTICS_V1.md](./TAROT_POSITION_SEMANTICS_V1.md) |
| Question type | **Question Ontology v1** — `DATA/reference/tarot/question_ontology_v1/types.json` · [TAROT_QUESTION_ONTOLOGY_V1.md](./TAROT_QUESTION_ONTOLOGY_V1.md) |
| User-facing prose | **LLM** (`tarot_interpretation_llm_v1`) |
| Structure / gates | code |
| Public fields | `tarot_answer_v1` (**frozen**) |

Editorial default: reject-invalid LLM → thin fallback. **Do not** hard-overwrite good LLM prose with formula banks.

### Quality track (only work allowed under stack freeze)

Порядок после freeze:

1. **Q1** Editorial Deepen Minors  
2. **Golden Dataset** (эталонные сценарии без оценок)  
3. **Golden Eval** (рубрикатор + прогон по датасету)  
4. **Q3** Prompt iteration (wording only)

Dataset и Eval — **разные** артефакты: набор сценариев расширяется независимо от рубрикатора.

#### Q1 — Editorial Deepen Minors

**Цель (формулировка):** сделать каждую из **56** младших карт **уникальным психологическим архетипом**, а не комбинацией rank × suit.

Не «углубить поля», а добиться, что 8 / 9 / 10 Мечей — **три разные человеческие истории**.

Semantic profile на карту (семантика, не литература) — SoT в [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md) § Q1:

| Field | Meaning |
|-------|---------|
| `core_scene` | какая человеческая ситуация изображена |
| `central_conflict` | внутреннее противоречие |
| `driving_need` | чего человек пытается добиться |
| `shadow_pattern` | типичная ловушка |
| `growth_direction` | куда ведёт зрелое проживание |
| `work_lens` / `relationship_lens` / `money_lens` / `inner_lens` | доменные линзы |
| `reversed_shift` | как меняется динамика (не «просто наоборот») |
| `adjacent_distinction` | чем отличается от соседних рангов той же масти |

**Gate:** если нельзя ответить «чем 9 Кубков отличается от 8 и 10» — карта не готова.

Тест: principle *card-name ablation* выше.

#### Golden Dataset (before Eval)

Фиксированные сценарии **без баллов**:

- вопрос · профиль · расклад/карты · ожидаемый `question_type` (ontology)

Расширяется независимо от рубрикатора. Path (target): `backend/tests/fixtures/tarot_golden_dataset_v1.json` (создаётся в Q2 prep).

#### Golden Eval (after Dataset)

Механизм оценки ответов по датасету. Рубрикатор **1–5**:

| Критерий | 1–5 |
|----------|-----|
| Ответил на вопрос | |
| Понятность | |
| История вместо списка карт | |
| Символика раскрыта естественно | |
| Практическая польза | |
| Нет повторов | |
| Нет ложной уверенности | |
| Хочется дочитать | |

Отдельно (да/нет): **«Я бы заплатил за такой разбор.»**

**Anti-sameness:** ~30 раскладов подряд — не звучат ли все ответы одинаково?

Без результатов Golden Eval — **не** поднимать architecture freeze.

#### Q3 — Prompt iteration (wording only)

Только после Eval: wording · ритм · длина · баланс символика/практика · голос. Не pipeline / контракт / новые слои.

---

## 7. Non-goals

- Hand-authored work+Moon+Devil+Fool branch as primary path
- Hundreds of if/else combination texts
- Suit-templates as final narrative author
- iOS/Android parity (follow-up)

---

## 8. Acceptance

- [x] Live path prefers LLM when configured
- [x] Pack never emits «Аркан»
- [x] Unresolved blocks LLM
- [x] UI shows four universal blocks
- [x] Pack carries central/light/shadow + element + question_lens
- [x] Profile fields selected by question domain
- [x] Quality gates beyond JSON schema
- [x] Fallback honest / non-imitative
- [x] Architecture freeze declared (no new contract/UI/spreads/engine branches as primary track)
- [x] Knowledge Base v1 · Position Semantics v1 · Question Ontology v1 landed
- [x] Interpretation Stack v1 **hard-frozen** until Golden Eval results
- [x] Canon principles: LLM = one story · answer this question · card-name ablation
- [x] Q1 Editorial deepen minors (unique archetype per card, not rank×suit)
- [ ] Golden Dataset (scenarios without scores)
- [ ] Golden Eval (rubric + paid-worth + anti-sameness) — freeze lift gate
- [ ] Q3 Prompt iteration from eval deltas only
