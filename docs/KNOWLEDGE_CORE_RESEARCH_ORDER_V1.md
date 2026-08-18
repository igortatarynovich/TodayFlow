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

**IL-1 in flight:** наполнение уже открытой модели планет (Sun→Pluto claims) продолжается по IL §6.9 (school-first, one locus) внутри **§6.10 remaining psych budget**. Это **не** шаблон для следующего ядра. CORE по астрологии по-прежнему не scored, не KPI, и не строится из «кто оказался читаемым».

**Следующее ядро** (новый слой IL, пересборка нумерологического смысла, психология, практики-как-знание, медицина): шаги 1–9 обязательны до первого ingest.

---

## 6. Запрещено

- Фиксировать обязательных авторов до shortlist.
- Строить архитектуру исследования вокруг доступности 1–2 книг.
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
