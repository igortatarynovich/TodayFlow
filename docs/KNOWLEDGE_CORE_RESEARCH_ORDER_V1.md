# Knowledge Core research order v1

**Статус:** ACCEPTED (порядок работы для семантических ядер).  
**Версия:** 1.1 (2026-08-17).  
**Владелец:** Product + Research.  
**Не является:** Meaning SoT дня · IL lookup · Machine Contract · KASP (сбор данных пользователя).

**Связь:** [Interpretation Library](./astrology/INTERPRETATION_LIBRARY_V1.md) (астрологический lookup; IL-1 уже в полёте) · [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (машинные/контентные контракты справочника — другой порядок) · [NUMBER_BASE_V1.md](./numerology/NUMBER_BASE_V1.md) · [TAROT_CARD_BASE_V1.md](./tarot/TAROT_CARD_BASE_V1.md) · [PRACTICES_SCREEN_V1.md](./practices/PRACTICES_SCREEN_V1.md) (экран ≠ knowledge core).

---

## Architecture impact

- **SoT before:** корпус и ingest начинались от доступных авторов и открытых страниц. IL-1 хорошо зафиксировал provenance/claims, но слишком рано превратил Greene и Hand из сильных кандидатов в обязательные источники. Архитектура исследования частично зависела от доступности двух книг.
- **SoT after:** семантическое ядро проектируется **до** выбора литературы. Источники подбираются под модель, а не модель под первого доступного автора. Порядок ниже — стандарт для любого следующего ядра (астрология CORE, нумерология, психология, практики, медицина и прочие системы знаний).
- **Public contract changed?** no
- **Migration required?** no — IL-1 claims / `object.function` / evidence tiers не переписываются этим документом
- **Canon updated?** yes — этот файл; IL §6.9 указывает сюда как на parent; трекер
- **Backward compatible?** yes для runtime. Для **нового** ядра ingest до шага 9 запрещён.

---

## 0. Зачем отдельный порядок

Reference Layer отвечает, **куда** смысл кладётся в продукт.  
Этот документ отвечает, **как исследовать** систему знаний, прежде чем что-то станет `core`.

Типичная ошибка: открыть сильную книгу → извлечь claims → объявить автора обязательным → остальная литература подстраивается под его категории и его доступность.

IL-1 это уже показал. Provenance и atomic claims — правильный слой. Слишком ранний author-lock — нет. Greene и Hand остаются кандидатами внутри большего source landscape, не каркасом исследования.

**Правило одной фразой:** сначала модель знания, затем всё доступное поле литературы, затем shortlist, затем ingest и сравнение. Не наоборот.

---

## 1. Locked sequence

Для **следующего** семантического ядра, и для любого нового ядра после него:

```text
1. предмет
2. границы
3. полный набор составляющих
4. определение каждой составляющей
5. школы / традиции
6. типы источников
7. карта потенциальной литературы
8. критерии отбора
9. shortlist корпуса
10. только потом ingest и сравнение
```

Шаги 1–4 — модель. Шаги 5–9 — ландшафт и отбор. Шаг 10 — добыча.  
Сравнение (конвергенция / конфликт / CORE) **после** ingest, не вместо модели.

Запрещено перескакивать к шагу 10, потому что «нашлась хорошая открытая глава». Доступность влияет на *какой locus из shortlist открыть первым*, не на состав модели и не на состав ландшафта.

---

## 2. Что такое составляющая

Составляющая — слот модели, который ядро обязано уметь держать (или явно исключить).

Примеры (не шаблон для копирования в другой домен):

| Ядро | Составляющие — вопрос модели, не вопрос книги |
|------|-----------------------------------------------|
| Астрологический объект | function · themes · polarity · shadow · domains · tempo — уже в IL schema; CORE = пересечение **школ** по **одному lemma**, не «что написал первый автор» |
| Нумерология | какие числа вообще входят в ядро (1–9 / masters / karmic) · что такое «значение цифры» vs цикл vs имя |
| Психология (если станет ядром) | конструкты, уровень описания (trait / process / state), что **не** является психологией продукта |
| Медицина / тело | что вообще имеет право быть утверждением; что остаётся symbolic/ledger-only |

Полный набор составляющих фиксируется **до** карты литературы. Иначе «первый попавшийся» автор определяет, каких слотов у нас как будто нет.

Определение составляющей — однозначное: что считается этим слотом, что не считается, чем оно не является. Без этого нельзя решать, покрыл ли источник слот или подменил его своей моделью.

---

## 3. Школы, типы источников, ландшафт

**Школы/традиции** — независимые интеллектуальные линии, которые модель обязана различать. Авторы внутри школы не взаимозаменяемы. Разные модели одного объекта — полезный конфликт, не баг.

**Типы источников** — класс текста, не фамилия: первоисточник · учебник школы · профессиональный синтез · авторизованный архив · обзор. SEO, анонимные explainer'ы, jacket, рецензии, агрегаторы, pirate dumps, память модели — не evidence.

**Карта потенциальной литературы** — обзор поля: кто пишет в каких школах, какие тома покрывают какие составляющие, что закрыто юридически. Это ещё не корпус.

**Критерии отбора** задаются от модели: quality × independence × relevance к составляющей × legal accessibility. Не «кто первый открылся».

**Shortlist** — кандидаты в корпус. Сильный автор = кандидат. Обязательным он становится только после отбора под модель, не потому что его главу удалось прочитать.

IL `NEED_OWNER(author/locus)` ≠ `NEED_EVIDENCE(slot)` — частный случай этого правила ([IL §6.9](./astrology/INTERPRETATION_LIBRARY_V1.md)).

IL `ACCESS_BLOCKED(slot)` (1.3.57) — если для пустого слота найдены ≥3 качественных независимых dedicated loci и все закрыты по доступу, discovery **этого слота** прекращается. Это статус слота, не локуса. Локусы остаются NEED_OWNER. Когда один из названных локусов станет читаемым: только extraction, без нового discovery ([IL §6.11](./astrology/INTERPRETATION_LIBRARY_V1.md)).

---

## 4. Два разных принципа доказательности

Не смешивать.

| Домен | Чем держится «ядро» |
|-------|---------------------|
| Астрология (IL) | межшкольная конвергенция по **одному lemma** (`core` / `supported` / `school_specific`). Два классика ≠ CORE. Watters+Hand оба `professional` ≠ две школы |
| Психология, медицина, клинические утверждения о теле/поведении | **иерархия доказательности** задаётся заранее (шаг 6–8): исследование / консенсус / учебник / школа / anecdote. Межшкольная конвергенция астрологии **не** заменяет эту иерархию и не повышает клинический вес |

Если домен смешанный (psychological astrology, «healing» в астрологическом тексте): астрологический lemma остаётся school-convergence; медицинское/клиническое утверждение либо вне ядра (ledger-only, как IL body rows), либо проходит свою иерархию. Не усреднять.

---

## 5. Что этот канон не делает

- Не откатывает IL-1 claims, provenance, `humanistic` class, Rudhyar Venus.
- Не переписывает `object.function` и не scoring CORE.
- Не заменяет [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (порядок JSON/Machine Contract).
- Не заменяет [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md) (данные пользователя).
- Не заменяет [HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md](./audits/HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md) (почему объяснительные системы удерживают людей).
- Не требует купить книги, чтобы «закрыть ландшафт». Карта включает закрытые тома как *известные, непрочитанные*.

**IL-1 in flight:** наполнение модели планет (Sun→Pluto) **research-stable** (IL **1.3.59**). §6.10 remaining psych budget closed 1.3.57. Дальше планеты — только opportunistic extract уже названных NEED_OWNER loci, не hunt ради coverage. Это **не** шаблон для следующего ядра. CORE по астрологии по-прежнему не scored, не KPI, и не строится из «кто оказался читаемым».

**Следующее IL-ядро = Layer 2 Signs.** Definition through shortlist (§6.13–§6.17) · first extract Houlding ontology (§6.18 / 1.3.64). Продолжать с шага 10: следующий named ingest = Rudhyar *Pulse of Life* Part One (**humanistic**). Ячейка C остаётся cell, не победитель, пока principle-глава не читаема. Не ingest 12 portraits. Не материализовать 12 sign objects до Architecture impact по required later-interpretive слотам. Houses/aspects уже имеют classical draft objects; ASC/MC и outers — отдельные ворота. Для любого **нового** ядра вне этого трека: шаги 1–9 обязательны до первого ingest.

---

## 6. Запрещено

- Фиксировать обязательных авторов до shortlist.
- Строить архитектуру исследования вокруг доступности 1–2 книг.
- Охотиться за 20-м источником пустого слота, когда ≥3 dedicated loci уже найдены и все закрыты по доступу (`ACCESS_BLOCKED`).
- Читать новый источник к уже извлечённым категориям другого автора.
- Объявлять CORE / product meaning, пока не определены составляющие и не виден ландшафт, а не только shortlist.
- Копировать астрологический `core` = school intersection в психологию или медицину.
- Открывать параллельный «research v2» без указателя сюда.

---

## 7. Changelog

- **1.0 (2026-08-17)** — locked sequence для семантических ядер. Урок IL-1: provenance раньше author-lock. Parent для IL §6.9. Обязателен для следующего ядра и для нумерологии / психологии / практик / медицины как систем знаний.
- **1.1 (2026-08-17)** — IL-1 in-flight remaining planet budget (IL §6.10 / 1.3.45) is psychological coverage of empty slots. This file's sequence for the *next* core is unchanged. CORE=0 is not a KPI.
- **1.1 note (2026-08-17)** — IL-1.3.46 filled Uranus psychological from Tarnas official intro. Remaining empty slots: Neptune → Venus → Mars. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-17)** — IL-1.3.47 filled Neptune psychological from the same Tarnas intro PDF (Neptune section, after field check). Remaining empty slots: Venus → Mars. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-17)** — IL-1.3.48 filled Venus psychological from Sullivan official-site *Venus and Jupiter* excerpt. Remaining empty slot: Mars. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-17)** — IL-1.3.49 re-checked Mars psychological field: still empty (no legally readable dedicated principle locus). Remaining empty slot: Mars. Next inside IL §6.10: densify Sun / Moon / Mercury / Saturn. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-17)** — IL-1.3.50 densified Sun psychological from Greene Apollon Issue 1 (not Apollo's Chariot). Remaining empty slot: Mars. Next inside IL §6.10: densify Moon / Mercury / Saturn. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.51 re-checked Moon psychological field: still only Luminaries preview (Costello still NEED_OWNER). Remaining empty slot: Mars. Next inside IL §6.10: densify Mercury / Saturn. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.52 re-checked Mercury psychological field: still only Inner Planets Hermes (remaining chapters unread). Remaining empty slot: Mars. Next inside IL §6.10: densify Saturn. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.53 densified Saturn psychological from Tarnas official intro Saturn/senex (Greene Introduction not re-ingested; `themes` unchanged). Remaining empty slot: Mars. Densify Sun/Moon/Mercury/Saturn complete. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.54 re-checked Mars psychological field: still empty (p.138 NEED_OWNER). Do not loop Mars without a new readable locus. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.55 cataloged Sasportas *Dynamics of the Unconscious* Part 1 unread (NEED_OWNER; no ingest). Mars psych still empty. Do not ingest forum quotes. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.56 cataloged Huber *The Planets* Mars chapter unread (NEED_OWNER; no ingest). Do not ingest masculine/tool-planet from TOC. Recount still deferred. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.57: Psychological Mars `ACCESS_BLOCKED` (3 dedicated loci, 0 bodies, 0 claims). §6.10 empty-slot + densify budget closed. Recount now allowed. Discovery for this slot stops. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.58: live Sun→Pluto recount. 1.3.44 dashboard retired. Psych: COVERED 7 · THIN 2 · ACCESS_BLOCKED 1 · EMPTY 0. Access queue is opportunistic, not a discovery hunt. This file's sequence for the *next* core is unchanged.
- **1.1 note (2026-08-18)** — IL-1.3.59: planet fill research-stable. Do not generate planet research to raise coverage. CORE scoring stays blocked. Next IL core = Layer 2 Signs; definition pass (steps 1–4) in IL §6.13; continue from step 5 before bibliography/ingest. Do not start from Arroyo/Rudhyar.
- **1.1 note (2026-08-18)** — IL-1.3.60: Layer 2 schools + source types in IL §6.14. Reuse `source_class` enum; no new class. Literature map is next (step 7) from that table, not from Arroyo/Rudhyar pending IDs.
- **1.1 note (2026-08-18)** — IL-1.3.61: Layer 2 literature map. Classical classification saturated. Minimal corpus named. First proposed ingest = Houlding triplicity ontology (not extracted). Criteria locked separately in 1.3.62.
- **1.1 note (2026-08-18)** — IL-1.3.62: Layer 2 selection criteria locked (parent step 8). Epistemic ≠ access. Cell C unscored. Shortlist done in 1.3.63.
- **1.1 note (2026-08-18)** — IL-1.3.63: Layer 2 shortlist locked (parent step 9). Houlding ontology IN; Pulse Part One IN; Cell C remains a cell; Hand Ch.10 later. First extract done in 1.3.64.
- **1.1 note (2026-08-18)** — IL-1.3.64: Houlding triplicity ontology extracted (classification ledger only; rulers out; no sign objects). Next named ingest = Pulse of Life Part One (humanistic). Cell C still a cell.
