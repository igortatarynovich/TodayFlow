# Temporal Identity v1 (C16)

**Статус:** `ACCEPTED` — канон **времени и природы изменений** в PIM.  
**Версия:** 1.0 (2026-06-23)  
**Владелец:** Product + Intelligence

**Это не:** календарный UX «вчера / неделя» · `valid_from` справочника Reference · TTL без семантики.

**Это:** ответ на вопрос **«что считается изменением человека?»** — и как atom / Contradiction Event **различают** ошибку модели, рост человека и смену контекста.

**Связь:**

| Документ | Роль |
|----------|------|
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) | PIM — историческая модель |
| [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) | Temporal fields на atoms |
| [CONTRADICTION_AND_REEVALUATION_V1.md](./CONTRADICTION_AND_REEVALUATION_V1.md) | C15 + `change_nature` при resolve |
| [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) | Intent history как temporal evidence |

**North star:**

> Человек — **не статичный объект**. PIM должен различать **рост человека** и **ошибки собственных выводов**, иначе через годы начнёт путать evolution с model failure.

**После C14–C15** atom отвечает: *почему мы так думаем?*  
**C16** добавляет: *когда это было правдой? · всё ещё правдой? · **что именно изменилось?***

---

## 0. Три природы «противоречия»

C15 фиксирует **что** противоречие есть. C16 фиксирует **природу**.

| `change_nature` | Смысл | Пример |
|-----------------|-------|--------|
| **`model_error`** | система ошибалась; человек не «изменился» | `conflict_avoidance @ 0.83` → новые данные показывают, гипотеза была неверна с начала |
| **`person_evolution`** | человек **реально изменился** во времени | 5 лет назад избегал конфликтов; последние 8 мес. инициирует сложные разговоры |
| **`context_shift`** | изменился **контекст**, не личность | на работе избегает; в семье нет; или ситуация 2025 исчезла к 2027 |

**Для own model** — три **разных training signal**. Нельзя сводить к одному `confidence -= Δ`.

### Пример (conflict avoidance)

**Было:** atom `trait.conflict_avoidance`, confidence 0.83, `valid_from` 2020, `temporal_scope: enduring`.

**Новое:** 8 мес. social-risk goals achieved + self-initiated talks.

**Re-evaluation (C15) + классификация (C16):**

| Гипотеза | `change_nature` | Действие |
|----------|-----------------|----------|
| Модель переобобщила ранние данные | `model_error` | retire atom; `resolution_note` |
| Устойчивый сдвиг поведения 8+ мес. | `person_evolution` | retire old; new atom `valid_from` = shift start |
| Только work context | `context_shift` | narrow atom scope → `context_bound` + domain `work`; spawn family atom |

**Narrative (DRE, не fact):**

> Раньше наблюдали устойчивое избегание конфликтов. Последние 8 месяцев — обратное. Вероятнее **изменение поведения**, не ошибка предыдущей модели.

---

## 1. Temporal fields на Knowledge Atom

Дополнение к UKM §2 (обязательно для pattern / hypothesis / trait-like claims):

| Поле | Тип | Описание |
|------|-----|----------|
| `valid_from` | datetime | с когда claim **поддерживался** evidence |
| `valid_until` | datetime | ○ — когда retired / superseded; `null` = current |
| `validity_status` | enum | `current` \| `historical` \| `context_specific` |
| `temporal_scope` | enum | см. §1.1 |
| `context_binding` | object | ○ — domain / life_sphere / situation_id |
| `still_valid` | bool | derived: `validity_status == current` ∧ confidence gate |
| `observation_window_days` | int | окно, на котором построен claim |

### 1.1 `temporal_scope`

| Значение | Когда | Contradict → чаще |
|----------|-------|-------------------|
| `enduring` | устойчивый trait / pattern | `person_evolution` или `model_error` |
| `phase` | фаза жизни (месяцы–годы) | `person_evolution` |
| `context_bound` | верно **в контексте** | `context_shift` |
| `situational_episode` | короткий эпизод | retire по TTL; rarely enduring promotion |

**Правило:** promote to `enduring` только после window + confirmation; иначе default `phase` или `context_bound`.

### 1.2 `context_binding` (для `context_bound`)

```json
{
  "domain": "work",
  "life_sphere_hint": "career",
  "situation_id": null,
  "note_key": "optional_display"
}
```

Два atoms **не противоречат**, если `context_binding` disjoint (work vs family).

---

## 2. Contradiction Event + C16

На [Contradiction Event](./CONTRADICTION_AND_REEVALUATION_V1.md) при `resolved`:

| Поле | Тип | Обязательно |
|------|-----|-------------|
| `change_nature` | enum | ✓ — `model_error` \| `person_evolution` \| `context_shift` |
| `change_nature_confidence` | float | ✓ |
| `change_rationale` | object | ○ — rules / evidence summary (machine) |
| `old_atom_valid_until` | datetime | ○ — close temporal window старого |
| `new_atom_valid_from` | datetime | ○ — open window нового |

**Запрещено:** resolve Contradiction без `change_nature` (кроме `reinforced` path).

### 2.1 Эвристики классификации (v1, deterministic)

| Сигнал | Склонность |
|--------|------------|
| Новые данные **с первых** observation противоречат старому atom | `model_error` |
| Старый atom долго stable; новый паттерн **≥ N мес.** однонаправленный | `person_evolution` |
| Contradiction только в одном `context_binding` | `context_shift` |
| User: «это было только на работе» | `context_shift` (T1 confirm) |

N и пороги — ILR / Re-evaluation rules (не LLM invention).

---

## 3. Исторический PIM

PIM хранит **не только текущее мнение**, но **линию времени**:

```
trait.conflict_avoidance (historical)
  valid_from: 2020-03 — valid_until: 2026-01
  change_nature at retire: person_evolution

trait.conflict_engagement (current)
  valid_from: 2026-01
  temporal_scope: phase
  evidence_chain → last 8 months
```

**LLM / DRE slice:** по умолчанию `validity_status: current` only.  
**Historical** — для Weekly Review, evolution narrative, own model training export.

**Запрещено:** historical atom в guidance «обычно ты» без explicit temporal framing.

---

## 4. Вопросы, на которые PIM обязан отвечать (C16)

| Вопрос | Источник |
|--------|----------|
| Почему мы так думаем? | C14 `evidence_chain` |
| Почему мнение изменилось? | C15 Contradiction + resolution |
| **Когда это было правдой?** | `valid_from` / `valid_until` |
| **Всё ещё правдой?** | `still_valid` / `validity_status` |
| **Ошибка модели или рост человека?** | `change_nature` |
| **Глобально или в контексте?** | `temporal_scope` + `context_binding` |

---

## 5. Gates (engineering)

| ID | Gate |
|----|------|
| **C16** | Retire/supersede atom → temporal close (`valid_until`) + `change_nature` on Contradiction |
| **C16a** | `enduring` promotion требует min window + confirmation |
| **C16b** | `context_bound` atoms must have `context_binding` |
| **C16c** | Training export includes historical atoms + `change_nature` labels |

**Reject:** contradiction resolved без `change_nature`; два global enduring traits contradict without context split attempt.

---

## 6. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0 ACCEPTED — Temporal Identity; change_nature; atom validity windows; historical PIM |
