# Knowledge Core research order v1

**Статус:** ACCEPTED (порядок работы для семантических ядер).  
**Версия:** 1.12 (2026-08-21).  
**Владелец:** Product + Research.  
**Не является:** Meaning SoT дня · IL lookup · Machine Contract · KASP (сбор данных пользователя).

**Связь:** [Interpretation Library](./astrology/INTERPRETATION_LIBRARY_V1.md) (астрологический lookup; IL-1 уже в полёте) · [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (машинные/контентные контракты справочника — другой порядок) · [NUMBER_BASE_V1.md](./numerology/NUMBER_BASE_V1.md) · [TAROT_CARD_BASE_V1.md](./tarot/TAROT_CARD_BASE_V1.md) · [PRACTICES_SCREEN_V1.md](./practices/PRACTICES_SCREEN_V1.md) (экран ≠ knowledge core).

---

## Architecture impact

- **SoT before:** корпус и ingest начинались от доступных авторов и открытых страниц. IL-1 хорошо зафиксировал provenance/claims, но слишком рано превратил Greene и Hand из сильных кандидатов в обязательные источники. Архитектура исследования частично зависела от доступности двух книг.
- **SoT after:** семантическое ядро проектируется **до** выбора литературы. Для астрологии IL продуктовый смысл с **1.3.76** = Mainstream convention → TodayFlow Canon. Исторический корпус = lenses, не arbiter. CORE не gate. Co–Star = recognition check. Источники подбираются под модель, а не модель под первого доступного автора. Порядок ниже — стандарт для любого следующего ядра (астрология, нумерология, психология, практики, медицина и прочие системы знаний).
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
| Астрология (IL **продуктовый смысл**) | **Mainstream V1 → TodayFlow Canon** (1.3.76): contemporary convention from a bounded modern panel, then our structuring. Не intersection школ. Не Google. Не 491-claim vote. |
| Астрология (IL **research / lenses**) | Existing corpus as interpretive lenses. `evidence_tier=core` = optional cross-tradition metadata. Это **не** product gate. |
| Психология, медицина, клинические утверждения о теле/поведении | **иерархия доказательности** задаётся заранее (шаг 6–8): исследование / консенсус / учебник / школа / anecdote. Межшкольная конвергенция астрологии **не** заменяет эту иерархию и не повышает клинический вес |

Если домен смешанный (psychological astrology, «healing» в астрологическом тексте): астрологический lemma идёт в Canon + school range; медицинское/клиническое утверждение либо вне ядра (ledger-only, как IL body rows), либо проходит свою иерархию. Не усреднять.

---

## 5. Что этот канон не делает

- Не откатывает IL-1 claims, provenance, `humanistic` class, Rudhyar Venus.
- Не переписывает `object.function` и не scoring CORE.
- Не заменяет [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (порядок JSON/Machine Contract).
- Не заменяет [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md) (данные пользователя).
- Не заменяет [HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md](./audits/HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md) (почему объяснительные системы удерживают людей).
- Не требует купить книги, чтобы «закрыть ландшафт». Карта включает закрытые тома как *известные, непрочитанные*.

**IL-1 in flight:** наполнение модели планет (Sun→Pluto) **research-stable** (IL **1.3.59**). §6.10 remaining psych budget closed 1.3.57. Дальше планеты — только opportunistic extract уже названных NEED_OWNER loci, не hunt ради coverage. Это **не** шаблон для следующего ядра. CORE по астрологии по-прежнему не scored, не KPI, и не строится из «кто оказался читаемым».

**Layer 2 Signs closed 1.3.69** as classification-complete / interpretation-deferred. Definition through shortlist (§6.13–§6.17) · Houlding ontology (§6.18 / 1.3.64) · Cell C `ACCESS_BLOCKED` (§6.19 / 1.3.65) · Pulse Part One (§6.20 / 1.3.66) · later-interpretive optional (§6.21 / 1.3.67) · Lilly classification drafts (§6.22 / 1.3.68) · close-out (§6.23 / 1.3.69). Шаг 10 (ingest) readable start-set **done** — не продолжать с шага 10 для Layer 2 literature.

**IL V1 literature freeze (1.3.71, owner-approved):** new **books** only against a named row in [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./astrology/KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md). **1.3.76:** Product Canon vs Lenses — [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./astrology/KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). **1.3.77:** Mainstream planet map — [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). **1.3.78:** Planet Canon grammar — [PLANET_CANON_GRAMMAR_V1.md](./astrology/PLANET_CANON_GRAMMAR_V1.md). **1.3.79:** Planet Canon V1 — [PLANET_CANON_V1.md](./astrology/PLANET_CANON_V1.md). **1.3.80:** Planet Canon storage — [PLANET_CANON_STORAGE_V1.md](./astrology/PLANET_CANON_STORAGE_V1.md). **1.3.81:** Sun–Saturn fill — [PLANET_CANON_SUN_SATURN_FILL_V1.md](./astrology/PLANET_CANON_SUN_SATURN_FILL_V1.md). **1.3.82:** composition smoke — [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./astrology/PLANET_CANON_COMPOSITION_SMOKE_V1.md). **1.3.83:** Mainstream sign map — [MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md). **1.3.84:** Sign Canon grammar — [SIGN_CANON_GRAMMAR_V1.md](./astrology/SIGN_CANON_GRAMMAR_V1.md). **1.3.85:** Sign Canon fill — [SIGN_CANON_V1.md](./astrology/SIGN_CANON_V1.md). **1.3.86:** Sign Canon storage — [SIGN_CANON_STORAGE_V1.md](./astrology/SIGN_CANON_STORAGE_V1.md). **1.3.87:** Sign Canon materialization — [SIGN_CANON_MATERIALIZATION_V1.md](./astrology/SIGN_CANON_MATERIALIZATION_V1.md). **1.3.88:** Planet × Sign smoke — [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./astrology/SIGN_CANON_COMPOSITION_SMOKE_V1.md). **1.3.89:** Mainstream house map — [MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md). **1.3.90:** House Canon grammar — [HOUSE_CANON_GRAMMAR_V1.md](./astrology/HOUSE_CANON_GRAMMAR_V1.md). **1.3.91:** House Canon fill — [HOUSE_CANON_V1.md](./astrology/HOUSE_CANON_V1.md). **1.3.92:** House Canon storage/materialization — [HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md](./astrology/HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md). **1.3.93:** Planet × House smoke PASS — [HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./astrology/HOUSE_CANON_COMPOSITION_SMOKE_V1.md). **STOP Houses.** **1.3.94:** Mainstream aspect map — [MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md). **1.3.95:** Aspect Canon grammar — [ASPECT_CANON_GRAMMAR_V1.md](./astrology/ASPECT_CANON_GRAMMAR_V1.md). **1.3.96:** Aspect Canon fill — [ASPECT_CANON_V1.md](./astrology/ASPECT_CANON_V1.md). **1.3.97:** Aspect Canon storage/materialization — [ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md](./astrology/ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md). 1.3.98 stored Planet × Aspect smoke done. **1.3.99** Angle Canon model (orientation loci). **1.3.100** Mainstream Angle map. **1.3.101** Angle Canon grammar (`orientation`). **1.3.102** Angle Canon fill. Next IL = Angle Canon storage/materialization. Aspect objects stay `DRAFT_CLASSICAL` with stored `canon.relation`. Для любого **нового** ядра вне IL V1: шаги 1–9 обязательны до первого ingest.

---

## 6. Запрещено

- Фиксировать обязательных авторов до shortlist.
- Строить архитектуру исследования вокруг доступности 1–2 книг.
- Охотиться за 20-м источником пустого слота, когда ≥3 dedicated loci уже найдены и все закрыты по доступу (`ACCESS_BLOCKED`).
- Читать новый источник к уже извлечённым категориям другого автора.
- Объявлять CORE как product meaning. Для астрологии IL продукт = TodayFlow Canon (1.3.73), не intersection. Не объявлять Canon, пока нет representative field и owner lock.
- Копировать астрологический `core` = school intersection в психологию или медицину.
- Открывать параллельный «research v2» без указателя сюда.
- Начинать новый IL literature/ingest pass, пока V1 Semantic Inventory не утверждён владельцем.
- Менять архитектуру Interpretation Library, пока не зафиксировано разделение Product Canon / Lenses (IL 1.3.76). После фиксации — не открывать книги; Mainstream planet map = 1.3.77; grammar = 1.3.78; Planet Canon V1 = 1.3.79; storage = 1.3.80; Sun–Saturn fill = 1.3.81; smoke-test = 1.3.82; Signs Mainstream map = 1.3.83; Sign Canon grammar = 1.3.84; Sign Canon fill = 1.3.85; Sign Canon storage = 1.3.86; Sign Canon materialization = 1.3.87; Planet × Sign smoke-test = 1.3.88; Houses Mainstream map = 1.3.89; House Canon grammar = 1.3.90; House Canon fill = 1.3.91; House Canon storage/materialization = 1.3.92; Planet × House smoke = 1.3.93; Mainstream Aspect Semantic Map = 1.3.94; Aspect Canon grammar = 1.3.95; Aspect Canon fill = 1.3.96; Aspect Canon storage/materialization = 1.3.97; stored Planet × Aspect smoke = 1.3.98; Angle Canon model = 1.3.99; Mainstream Angle map = 1.3.100; Angle Canon grammar = 1.3.101; Angle Canon fill = 1.3.102; следующий проход = Angle Canon storage/materialization. STOP Houses. STOP Signs.

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
- **1.1 note (2026-08-18)** — IL-1.3.64: Houlding triplicity ontology extracted (classification ledger only; rulers out; no sign objects). Cell C discovery closed as ACCESS_BLOCKED in 1.3.65.
- **1.1 note (2026-08-18)** — IL-1.3.65: Layer 2 psychological later-interpretive (Cell C) `ACCESS_BLOCKED`. Three dedicated loci, 0 bodies, 0 claims. Discovery for that slot stops. Pulse Part One extracted in 1.3.66. Do not fill required psych slots from Rudhyar.
- **1.1 note (2026-08-18)** — IL-1.3.66: Rudhyar *Pulse of Life* Part One extracted as humanistic cycle (classification ledger; no sign objects). Part Two out. Cell C still ACCESS_BLOCKED. Schema requiredness demoted in 1.3.67.
- **1.1 note (2026-08-21)** — IL-1.3.67: later-interpretive slots optional on IL-1 draft `type=sign`. Still unattested. Classification-only drafts followed in 1.3.68.
- **1.1 note (2026-08-21)** — IL-1.3.68: twelve `type=sign` drafts from Lilly CA I.16 classification. Later-interpretive omitted. Collisions remain claims. Nothing active. Do not CORE.
- **1.1 note (2026-08-21)** — IL-1.3.69: Layer 2 Signs close-out. Classification-complete / interpretation-deferred. No ingest. Cell C is a future evidence dependency, not a Layer 2 blocker. Do not reopen sign literature.
- **1.1 note (2026-08-21)** — IL-1.3.70: Layer 1 Outers definition/readiness (parent steps 1–4). No ingest. No objects. Outer `function` ≠ classical elemental `function`. Do not assemble Uranus from Hand. Next named = scoped optional-on-draft or keep withheld.
- **1.1 note (2026-08-21)** — IL-1.3.71: Knowledge Core V1 Semantic Inventory. Owner-approved freeze map. Literature only against a named `KC-*` row. IL-1 done criterion = minimum controlled primitives, not bibliography.
- **1.1 note (2026-08-21)** — IL-1.3.72: Outer Planet Draft Representation. Meaning keys optional on IL-1 draft outers. Sun–Saturn unchanged. No objects. Fill waits for Canon (1.3.73).
- **1.2 (2026-08-21)** — IL-1.3.73: TodayFlow Canon. Astrology product meaning is no longer school-intersection. §4 split: Canon vs research `core`.
- **1.2 note (2026-08-21)** — IL-1.3.74: Evidence Corpus / Semantic Consensus / TodayFlow Canon. 491 claims stay. Next = short corpus pass, not a research cycle.
- **1.3 (2026-08-21)** — IL-1.3.75: reverse-engineer Co–Star before another IL architecture or Canon-scoring pass. Phase 0 teardown in. IL frozen.
- **1.30 (2026-08-22)** — IL-1.3.102: Angle Canon fill. Two packs. Origin direct. House 1/10 collision. Next = storage/materialization.
- **1.29 (2026-08-22)** — IL-1.3.101: Angle Canon grammar. One slot (`orientation`). Include-first. Secondary = collision-zone. Angle Canon fill — **done 1.3.102.**
- **1.28 (2026-08-22)** — IL-1.3.100: Mainstream Angle Semantic Map. Same panel. House 1/10 not proof. Angle Canon grammar — **done 1.3.101.**
- **1.27 (2026-08-22)** — IL-1.3.99: Angle Canon model. Parent 1–4. Orientation loci. Named slots unspecified. Mainstream Angle map — **done 1.3.100.**
- **1.26 (2026-08-22)** — IL-1.3.98: stored Planet × Aspect composition smoke PASS. Four gates. STOP Aspects. Angle model — **done 1.3.99.**
- **1.25 (2026-08-22)** — IL-1.3.97: Aspect Canon storage/materialization. Five drafts carry `canon.relation`. `interaction` unchanged. Next = 1.3.98 stored Planet × Aspect smoke. **Done 1.3.98.**
- **1.24 (2026-08-22)** — IL-1.3.96: Aspect Canon fill. Five packs. Origin direct. Mixed-valence guard. Next = storage/materialization. **Done 1.3.97.**
- **1.23 (2026-08-22)** — IL-1.3.95: Aspect Canon grammar. One slot (`relation`). Effort / `requires_action` surplus. Next = Aspect Canon fill. **Done 1.3.96.**
- **1.22 (2026-08-22)** — IL-1.3.94: Mainstream Aspect Semantic Map. Same panel. Relation ≠ theme. Next = Aspect Canon grammar. **Done 1.3.95.**
- **1.21 (2026-08-22)** — IL-1.3.93: Planet × House composition smoke. PASS. STOP Houses. Historical PARTIAL = snapshot. Next = Aspects Mainstream. **Done 1.3.94.**
- **1.20 (2026-08-22)** — IL-1.3.92: House Canon storage/materialization. Twelve drafts carry `canon.arena`. Next = Planet × House smoke. **Done 1.3.93.**
- **1.19 (2026-08-22)** — IL-1.3.91: House Canon fill. Twelve packs. Next = storage/materialization. **Done 1.3.92.**
- **1.18 (2026-08-22)** — IL-1.3.90: House Canon grammar. One slot (`arena`). Next = House Canon fill. **Done 1.3.91.**
- **1.17 (2026-08-22)** — IL-1.3.89: Mainstream House Semantic Map. Same panel as planets/signs. House ≠ angle. Next = House Canon grammar. **Done 1.3.90.**
- **1.16 (2026-08-22)** — IL-1.3.88: Planet × Sign composition smoke. PlanetInSign PASS. STOP Signs. Next = Houses Mainstream map → House Canon grammar. **Done 1.3.89.**
- **1.15 (2026-08-21)** — IL-1.3.87: Sign Canon materialization. Twelve drafts. Next = 1.3.88 Planet × Sign smoke-test. **Done 1.3.88.**
- **1.14 (2026-08-21)** — IL-1.3.86: Sign Canon storage. Optional `canon` on `type=sign`. Next = write packs onto sign drafts. **Done 1.3.87.**
- **1.13 (2026-08-21)** — IL-1.3.85: Sign Canon fill. Twelve packs. Four gates. Next = Sign Canon storage. **Done 1.3.86.**
- **1.12 (2026-08-21)** — IL-1.3.84: Sign Canon grammar. Two slots (`manner` · `excess`). Sign = how. Next = Sign Canon fill. **Done 1.3.85.**
- **1.11 (2026-08-21)** — IL-1.3.83: Mainstream Sign Semantic Map. Same panel as planets. Classification is not proof. Next = Sign Canon grammar. **Done 1.3.84.**
- **1.10 (2026-08-21)** — IL-1.3.82: composition smoke-test. Aspect PASS. Sign/house PARTIAL. Next = Signs Mainstream for Sign Canon grammar. **Done 1.3.83.**
- **1.9 (2026-08-21)** — IL-1.3.81: Sun–Saturn `canon` fill. Next = 1.3.82 smoke-test, not Signs. **Done 1.3.82.**
- **1.8 (2026-08-21)** — IL-1.3.80: Planet Canon storage. Optional `canon` nest. Next = write packs onto Sun–Saturn drafts. **Done 1.3.81.**
- **1.7 (2026-08-21)** — IL-1.3.79: Planet Canon V1. Ten packs + direct/derived. Next = schema pass. **Done 1.3.80.**
- **1.6 (2026-08-21)** — IL-1.3.78: Planet Canon grammar. Six slots. tempo = Foundation. Next = 1.3.79 fill, not schema. **Done 1.3.79.**
- **1.5 (2026-08-21)** — IL-1.3.77: Mainstream Planet Semantic Map. Panel = Astrodienst · Cafe Astrology · Astrology.com. Concept families, not 2/3 word vote. Next = Planet Canon shape, not JSON. **Done 1.3.78.**
- **1.4 (2026-08-21)** — IL-1.3.76: Product Canon vs Lenses. Mainstream convention is product meaning. Research corpus is lenses. CORE not a gate. Next = Mainstream planet map, not books. **Done 1.3.77.**
