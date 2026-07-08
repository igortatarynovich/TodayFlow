# Contradiction & Re-evaluation v1 (C15)

**Статус:** `ACCEPTED` — канон **как система меняет мнение** о человеке.  
**Версия:** 1.1 (2026-06-23)  
**Владелец:** Product + Intelligence

**Это не:** тихое `confidence -= 0.05` · перезапись профиля · игнор нового сигнала.

**Это:** явная сущность **Contradiction Event** + процесс **Re-evaluation** — когда новые наблюдения **подтверждают**, **оспаривают** или **заменяют** существующую интерпретацию.

**Связь:**

| Документ | Роль |
|----------|------|
| [TEMPORAL_IDENTITY_V1.md](./TEMPORAL_IDENTITY_V1.md) | C16 — `change_nature`, validity windows |
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) | PIM; цепочка после C14 |
| [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) | Atoms, `decay_strategy: contradiction`, `evidence_chain` |
| [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md) | Конкурирующие interpretations до promotion |
| [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) | Intent outcomes как contradiction triggers |
| [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) | Contradiction events = **primary training asset** |

**North star:**

> Настоящая персональная модель **замечает, что человек изменился** — иначе PIM станет архивом старых представлений.

**После C14** появляется обучаемая цепочка:

```
Observation → Signal → Interpretation → Confirmation → Knowledge
```

**C15** добавляет ветку, когда мир **не совпал** с тем, что уже знаем:

```
New Signal → Conflict detect → Contradiction Event → Re-evaluation → Atom update | retire | supersede
```

---

## 0. Зачем (training asset quality)

### Вариант A — непригоден для обучения

```
user_123 = avoids conflicts
user_123 = prone to overload
user_123 = achievement-oriented
```

Непонятно: кто решил · когда · почему · на основании чего.

### Вариант B — пригоден для reasoning-model

```
17 Intent Records
42 Behavioral Events
9 Discovery Answers
3 competing interpretations
1 confirmed hypothesis (confidence 0.81)
evidence_chain → concrete observations
2 Contradiction Events with resolution trace
```

Модель видит **путь к выводу** и **как мнение менялось** — не только label.

**Own model** учится на Variant B, не на Variant A.

---

## 1. Три исхода нового сигнала

| Исход | Что происходит | Артефакт |
|-------|----------------|----------|
| **Reinforce** | подтверждает atom / hypothesis | `last_confirmed_at` ↑; optional `evidence_chain` append |
| **Contradict** | ослабляет или оспаривает | **Contradiction Event** → Re-evaluation |
| **Supersede** | старая интерпретация устарела; нужна новая рамка | Contradiction Event → retire atom + spawn hypothesis |

**Правило:** contradict / supersede **не** сводятся к silent confidence tweak без Contradiction Event (кроме micro-reinforce внутри того же interpretation window).

---

## 2. Contradiction Event (сущность)

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `contradiction_id` | string | ✓ | stable id |
| `user_id` | string | ✓ | |
| `triggered_at` | datetime | ✓ | |
| `status` | enum | ✓ | `open` \| `re_evaluating` \| `resolved` \| `deferred` |
| `target_atom_id` | string | ○ | существующий Knowledge Atom |
| `target_interpretation_instance_id` | string | ○ | если ещё не promoted |
| `conflict_type` | enum | ✓ | `reinforcing` \| `contradicting` \| `superseding` |
| `conflicting_evidence` | object[] | ✓ | signals/events/intent_records — как `evidence_chain` |
| `interpretation_ref_ids` | string[] | ○ | ILR rules involved |
| `prior_confidence` | float | ○ | snapshot до re-eval |
| `resolution` | object | ○ | см. §3; **must include** `change_nature` (C16) |
| `learning_eligible` | bool | ✓ | default true — training row |

### Пример (конфликт избегания)

**Было (atom):** `trait.conflict_avoidance` — confidence 0.83, stable 6mo.

**Новые signals:**

- 3× Intent Records: high social-risk goals, outcomes achieved
- 2× self-initiated difficult conversation (behavioral)
- Discovery: «скорее иду в разговор, чем откладываю»

→ `contradiction_id` created, `conflict_type: superseding`  
→ Re-evaluation: не «0.83 → 0.71», а явный fork:

- retire / decay old atom with reason
- spawn `trait.conflict_avoidance_contextual` hypothesis @ 0.45
- или split: «избегание в work, не в relationships» — две domain-specific hypotheses

---

## 3. Re-evaluation (процесс)

**Re-evaluation Engine** (детерминированный сейчас; own model позже):

1. **Detect** — ILR / rule: new signal ∩ active atom claim = potential conflict.  
2. **Open** Contradiction Event (`status: open`).  
3. **Gather** — pull `evidence_chain` atom + new `conflicting_evidence`; sibling interpretations from Instance.  
4. **Resolve** (`re_evaluating` → `resolved`):

| Resolution | Действие над atom | Training note |
|------------|-------------------|---------------|
| `reinforced` | confidence ↑; append evidence | positive example |
| `weakened` | confidence ↓; `stability → decaying` | partial contradict |
| `retired` | atom `confirmation_stage: rejected` or archived | hypothesis destroyed — **high value** |
| `superseded` | old retired + new hypothesis spawned | model change trace + **`change_nature`** |
| `user_corrected` | `suppressed_by_user` or explicit edit | human ground truth |

5. **Emit** learning events: `contradiction_opened`, `contradiction_resolved` (web + iOS parity).

**Запрещено:**

- новый contradicting signal → только `confidence -= Δ` без event;
- старый stable atom остаётся в LLM slice после `retired`;
- L4 trait label («ленивый») как resolution без policy gate.

---

## 4. Место в PIL stack

```
Signal
  → ILR (match + conflict detect)
  → [Reinforce path] → atom update
  → [Contradict path] → Contradiction Event
        → Re-evaluation Engine
        → atom retire | weaken | supersede
        → optional new Interpretation Instance
  → Confirmation (for new hypothesis)
  → Knowledge Atom (with fresh evidence_chain)
```

**Contradiction Event** — между ILR и UKM, **не** замена atom.

**DRE / LRE:**

- **DRE** читает **resolved** atoms only; open contradictions → fallback to day context (no stale «обычно ты»).
- **LRE** может **приоритизировать** open contradictions для Discovery («уточнить, изменилось ли…»).

---

## 5. Atom fields при C15

На atom добавляется (UKM):

| Поле | Описание |
|------|----------|
| `contradiction_count` | сколько раз оспаривался |
| `last_contradiction_at` | последний open/resolve |
| `superseded_by_atom_id` | если заменён |
| `supersedes_atom_id` | если вырос из retire |

`decay_strategy: contradiction` — активируется при unresolved или post-retire TTL.

---

## 6. Gates (engineering)

| ID | Gate |
|----|------|
| **C15** | Contradicting signal → **Contradiction Event**; no silent overwrite of stable atom |
| **C15a** | Resolution **trace** persisted (`resolution` on event + atom lineage) |
| **C15b** | Retired atoms **не** в `llm_eligible` slice |
| **C15c** | Contradiction rows **learning_eligible** for own model dataset |

**Reject PR:** код обновляет atom confidence при conflict без `contradiction_id` в audit.

---

## 7. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0 ACCEPTED — Contradiction Event; Re-evaluation; Variant A/B training rationale; C15 gates |
| 2026-06-23 | v1.1 — C16 cross-ref; `change_nature` required on resolution |
