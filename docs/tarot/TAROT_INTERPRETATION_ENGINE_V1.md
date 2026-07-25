# Tarot Interpretation Engine v1

**Статус:** ACTIVE (2026-07-25) — **architecture frozen**; quality work is content/prompt only  
**Тип:** generation / meaning contract (SoT для ответа расклада)  
**Владелец:** Product + Backend  
**Связанные:** [SCREEN_CONTRACTS_V1.md](../SCREEN_CONTRACTS_V1.md) §6.4–§6.5 · [PRODUCT_GENERATION_CONTRACTS.md](../PRODUCT_GENERATION_CONTRACTS.md) · [TAROT_DESIGN_LANGUAGE_V1.md](./TAROT_DESIGN_LANGUAGE_V1.md)

### Architecture freeze (owner, 2026-07-25)

Pipeline `Context Pack → LLM → validation → UI` and public `tarot_answer_v1` shape are **frozen**.

**Do not** (until freeze lifts): new contract fields · new engine branches · new spread types · new Tarot UI as primary work.

**Primary risk** is no longer architecture — it is **knowledge quality + prompt**. Next work is content SoT feeding the pack, not more pipeline code.

Ledger anchors: `fb8cd34` (engine v1) · `c4bbe56` (pack/gates) · `f2ac8c2` / `8c7bd2e` (CE scrub from tarot path).

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

- вопрос, spread kind, `question_domain`
- `profile_relevant`: **1–2 поля, выбранные под домен вопроса**  
  (work → decision_style / motivation / helps; relationships → communication/conflict; …)  
  Не натальный dump.
- `response_shape` (блоки; choice_compare; order=`conflict_first_then_answer`)

**Запрещено** класть в pack готовые абзацы-ответы.

---

## 4. LLM job (universal prompt)

Порядок: конфликт → связь с вопросом → ответ → шаг.

Запреты: механический список карт; повтор вопроса >1; спам названий позиций; цитата профиля; карты как факты о внешнем мире; пустые формулы; «Аркан».

Prompt ver: `tarot-interpretation-v1.3` (KB + `position_semantics`: purpose / extract / do_not / result_type)

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
| Question type | `question_domain` / lens · **next:** Question Ontology |
| User-facing prose | **LLM** (`tarot_interpretation_llm_v1`) |
| Structure / gates | code |
| Public fields | `tarot_answer_v1` (**frozen**) |

Editorial default: reject-invalid LLM → thin fallback. **Do not** hard-overwrite good LLM prose with formula banks.

### Content backlog (quality, not architecture)

1. **Tarot Knowledge Base v1** — **ACTIVE** — [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md) · 78 semantic records in pack. Next: editorial deepen minors.
2. **Position Semantics** — **ACTIVE** — [TAROT_POSITION_SEMANTICS_V1.md](./TAROT_POSITION_SEMANTICS_V1.md) · role library in pack.
3. **Question Ontology** — choice · relationships · work · money · purpose · inner state · decision · conflict · growth · undefined; drives interpretation logic in pack + prompt. **← next**
4. **Prompt Evaluation** — golden set (~50 real questions); after each content/prompt change score: has answer · no loops · no fluff · no categorical claims · clear takeaway · worth finishing. Prefer this over more unit tests of glue.
5. **KB editorial deepen (minors)** — central scene · unique conflict · vs neighbor ranks · upright/reversed · domain nuance (before golden eval).

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
- [x] Knowledge Base v1 landed (78 cards → pack; prompt v1.2 reads KB fields)
- [x] Position Semantics v1 landed (role library → pack `position_semantics`; prompt v1.3)
- [ ] Live eval 10–15 scenarios (script: `scripts/tarot_interpretation_live_eval.py --live`) — owner scores text usefulness
- [ ] Question Ontology · Prompt golden eval (~50) — next content track
- [ ] KB editorial deepen (majors review · weak minors rewrite) — before golden eval
