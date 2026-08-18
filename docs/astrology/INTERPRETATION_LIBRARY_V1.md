# Interpretation Library v1 — ontology / schema

**Статус:** ACCEPTED (канон схемы и порядка работ) — **IL-1 in progress** (24 draft objects: classical seven · 12 houses · 5 major aspects; 12 sign *claims* without objects; Uranus Hand-1981 + Rudhyar NMNM + Tarnas intro *claims* without object; Neptune Hand-1981 + Rudhyar NMNM + Tarnas intro *claims* without object; Pluto Hand-1981 + Rudhyar NMNM + Greene/Campion interview *claims* without object; nothing `active`).  
**Версия:** 1.3.60 (2026-08-18).  
**Методология:** слои / evidence tiers / provenance **LOCKED** до закрытия IL-1. Parent research order: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) — модель знания **до** литературы. **1.3.29** school-first остаётся для opportunistic extract уже названных loci. **1.3.30** запрещает строить следующее ядро / CORE от первого доступного автора. **1.3.45** remaining planet budget = empty psychological slots (Pluto→Uranus→Neptune→Venus→Mars). **1.3.46** Uranus psychological filled (Tarnas official intro). **1.3.47** Neptune psychological filled (same Tarnas PDF, Neptune section, after field check). **1.3.48** Venus psychological filled (Sullivan official-site *Venus and Jupiter* excerpt). **1.3.49** Mars psychological field re-checked, still empty. **1.3.50** Sun psychological densified (Greene Apollon Issue 1 / astro.com in_sungod). **1.3.51** Moon psychological field re-checked, still only Luminaries preview. **1.3.52** Mercury psychological field re-checked, still only Inner Planets Hermes. **1.3.53** Saturn psychological densified (Tarnas official intro senex section). **1.3.54** Mars psychological field re-checked, still empty. **1.3.55** Sasportas *Dynamics of the Unconscious* Part 1 identified unread (NEED_OWNER). **1.3.56** Huber *The Planets* Mars chapter identified unread (NEED_OWNER). **1.3.57** `ACCESS_BLOCKED(semantic slot)` — Psychological Mars. **1.3.58** live Sun→Pluto recount (1.3.44 dashboard retired). **1.3.59** planet research-stable; opportunistic/access-driven; Layer 2 definition pass started (no bibliography). **1.3.60** Layer 2 schools + source types (parent steps 5–6); literature map still waits. `source_class=humanistic` с 1.3.29. Дальше — только баги модели.  
**Владелец:** Product + Research.  
**Данные:** `DATA/reference/astrology/interpretation_v1/` — corpus · `claims/` · `objects_v1.json` (draft).  
**Handoff (next agent):** [IL1_HANDOFF.md](./IL1_HANDOFF.md) — что сделано, что locked, откуда продолжать ingest.  
**Gap audit (live 1.3.58 recount):** [IL1_SUN_PLUTO_GAP_AUDIT.md](./IL1_SUN_PLUTO_GAP_AUDIT.md) — 1.3.24/1.3.44 snapshots retired. Owner queue **1.3.25** superseded for *discovery* by **1.3.29**. NEED_OWNER-blocks-locus **1.3.26** still holds for named closed pages. Hand Ch.4 Sun unread **1.3.27**. Corpus QA snapshot **1.3.28** — [IL1_CORPUS_QA.md](./IL1_CORPUS_QA.md). **1.3.29** reopens source discovery (school-first). **1.3.30** parent: knowledge-core research order. **1.3.31** Rudhyar Mars humanistic. **1.3.32** Rudhyar Uranus humanistic. **1.3.33** Rudhyar Neptune humanistic. **1.3.34** Rudhyar Pluto humanistic. **1.3.35** Rudhyar Sun humanistic. **1.3.36** Rudhyar Moon humanistic. **1.3.37** Rudhyar Mercury humanistic. **1.3.38** Greene *By Jove!* Psychology of Jupiter extract (psychological). **1.3.39** Rudhyar Saturn humanistic. **1.3.40** Rudhyar Jupiter humanistic. **1.3.41** Venus psychological discovery (no ingest). **1.3.42** Mars psychological discovery (no ingest). **1.3.43** Uranus psychological discovery (no ingest). **1.3.44** Neptune psychological discovery (no ingest). **1.3.45** psych-budget lock + Pluto psychological ingest (Greene/Campion interview; object withheld). **1.3.46** Uranus psychological ingest (Tarnas official intro; object withheld). **1.3.47** Neptune psychological ingest (Tarnas official intro Neptune section; object withheld). **1.3.48** Venus psychological ingest (Sullivan official-site *Venus and Jupiter* excerpt; `function` unchanged). **1.3.49** Mars psychological discovery (no ingest; p.138 still NEED_OWNER). **1.3.50** Sun psychological densification (Greene Apollon Issue 1; Apollo's Chariot still NEED_OWNER). **1.3.51** Moon psychological densification (no ingest; Costello still NEED_OWNER). **1.3.52** Mercury psychological densification (no ingest; Inner Planets Hermes already ingested). **1.3.53** Saturn psychological densification (Tarnas official intro Saturn/senex; Greene Introduction not re-ingested). **1.3.54** Mars psychological densification (no ingest; p.138 still NEED_OWNER). **1.3.55** Sasportas *Dynamics of the Unconscious* Part 1 cataloged unread (NEED_OWNER; not ingested). **1.3.56** Huber *The Planets and Their Psychological Meaning* Mars chapter cataloged unread (NEED_OWNER; not ingested). **1.3.57** Psychological Mars `ACCESS_BLOCKED` (three dedicated loci, 0 readable bodies, 0 claims). **1.3.58** live Sun→Pluto recount; 1.3.44 dashboard retired. **1.3.59** planet research-stable (opportunistic extract only); Layer 2 definition pass started. **1.3.60** Layer 2 schools + source types (no literature map, no ingest). CORE still unscored.  
**Схема:** [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json) · claims ledger [astrology_claims_v1.schema.json](../schemas/astrology_claims_v1.schema.json).  
**Пример формы (не SoT смысла):** [astrology_interpretation_v1.example.json](../schemas/fixtures/astrology_interpretation_v1.example.json).

**Роль:** семантическая база астрологических примитивов (данные, не пользовательский текст). Для **Today** это шаг 2 pipeline ([TODAY_CONTENT_PIPELINE_V1](../today/TODAY_CONTENT_PIPELINE_V1.md) — **единственный Meaning SoT дня**): «Astrology Interpretation Canon (lookup)». Не второй канон дня. Тот же lookup читают Profile · Compatibility · Tarot-context.

**Публичный язык (не этот файл):** Canon как нормализованное пересечение исторических слоёв + точность NASA/JPL — [Trust Layer](../content/TODAYFLOW_TRUST_LAYER.md). IL = методика и lookup. Бренд / лендинг / реклама читают Trust Layer.

---

## Architecture impact

- **SoT before:** pipeline step 2 («Astrology Interpretation Canon») named as **дыра**; смысл примитивов размазан (Foundation keywords · legacy JSON · AMC vectors · LLM invention).
- **SoT after:** Interpretation Library = that lookup (atoms first, Layer 5 gold list = curated *candidates* until IL-2). Runtime: Swiss/JPL → calculation → IL → engine → expression. Licensing Swiss = parallel gate. Engine clusters + ranks; LLM выражает pack. **Today Meaning SoT остаётся** TODAY_CONTENT_PIPELINE_V1. Activation gates: unevidenced `requires_action: false` cannot become `active`; IL-2 may demote Layer 5 candidates to composed.
- **Public contract changed?** no (пока нет runtime wiring).
- **Migration required?** no until IL-4 (Expression). Legacy content JSON не удалять до `active` атомов.
- **Canon updated?** this doc · pipeline §2 · AMC §2.2 · ACM · Foundation §2 compose rule · DAY_SOURCES цепочка · tracker freeze.
- **Backward compatible?** yes — generators continue until Engine consumes packs.

### Architecture impact — 1.3.29 source discovery

- **SoT before:** author-first queue (Greene then Hand) treated `NEED_OWNER(author/locus)` as blocking the semantic slot; psychological Venus bound to Greene p.69; Rudhyar listed as `psychological` in §6.1; freeze “no new books/authors.”
- **SoT after:** discovery = school class → missing semantic coverage → best accessible primary/direct-read source. `NEED_OWNER(author/locus)` ≠ `NEED_EVIDENCE(semantic slot)` until other independent authorities of that school class are checked. `source_class=humanistic` added so Rudhyar is not parked as psychological (no false CORE with Greene). New reputable authors allowed until semantic saturation. Existing Greene/Hand NEED_OWNER loci remain pending; do not replace them with summaries of those authors.
- **Public contract changed?** no (no runtime wiring).
- **Migration required?** no — unused catalog rows `src.psychological.rudhyar_personality` / `rudhyar_lunation` stay `psychological` until a dedicated reclass. New Rudhyar planet ingest uses `humanistic`.
- **Canon updated?** yes — this doc §6.1 · §6.9 · changelog 1.3.29; `source_class` enum in claims / objects / corpus schemas.
- **Backward compatible?** yes for product JSON. 1.3.25–1.3.28 Greene-first *discovery* queue is superseded; those closed loci stay NEED_OWNER.

### Architecture impact — 1.3.30 knowledge-core research order

- **SoT before:** IL §6.9 school-first discovery inside an already-started author landscape; next cores had no locked research sequence.
- **SoT after:** [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) is the parent: предмет → границы → составляющие → определения → школы → типы источников → карта литературы → критерии → shortlist → ingest. IL-1 planet fill continues §6.9. CORE / next domain cores cannot be architected around whoever was readable first. Psychology/medicine evidence hierarchy ≠ IL school-convergence.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — new doc + this changelog 1.3.30
- **Backward compatible?** yes — no runtime wiring; IL-1 claims unchanged

### Architecture impact — 1.3.45 remaining psych budget

- **SoT before:** IL-1 planet fill was school-first, one locus, any missing class. After 1.3.44 the next named task was Pluto psychological, but classical/humanistic/professional padding was still allowed. CORE=0 was easy to treat as a KPI. Humanistic Rudhyar could be mistaken for a psychological substitute. Discovery could still hunt confirmation of Hand lemmas (reconstruction / disruption / dissolution).
- **SoT after:** remaining IL-1 planet research budget is **psychological coverage of empty slots**, in order **Pluto → Uranus → Neptune → Venus → Mars**, then densify Sun/Moon/Mercury/Saturn. Jupiter psychological is paused (already the dense psych ledger). Humanistic ≠ psychological. Do not search for a second source that confirms Hand. CORE=0 is not a KPI; the CORE rule (same lemma across school classes) is unchanged. Full recount only after those five empty psych slots are non-empty. Outer planets are the stress-test: hold three models without averaging. Greene NEED_OWNER does not block another independent psychological source.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this doc §6.10 · changelog 1.3.45; handoff; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; CORE still unscored; Pluto object still withheld

### Architecture impact — 1.3.46 Uranus psychological ingest

- **SoT before:** Uranus psych slot empty. Ledger = Hand professional + Rudhyar humanistic. Tarnas *Prometheus the Awakener* unread; 1987 client-brief not ingested as a substitute.
- **SoT after:** Uranus psych slot filled from Tarnas official-site *Introduction to Archetypal Astrology* (Uranus/Prometheus section) as `psychological` `school_specific`. Monograph still unread NEED_OWNER. Object withheld. No CORE. Remaining empty psych slots: Neptune → Venus → Mars. Recount still deferred.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.46; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Uranus object still withheld; CORE still unscored

### Architecture impact — 1.3.47 Neptune psychological ingest

- **SoT before:** Neptune psych slot empty. Ledger = Hand professional + Rudhyar humanistic. *The Astrological Neptune* NEED_OWNER.
- **SoT after:** Neptune psych slot filled from Tarnas official-site *Introduction to Archetypal Astrology* (Neptune section) as `psychological` `school_specific`. Same PDF as Uranus 1.3.46 after field check, not auto-picked. Dedicated Greene book still unread NEED_OWNER. Object withheld. No CORE. Remaining empty psych slots: Venus → Mars. Recount still deferred.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.47; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Neptune object still withheld; CORE still unscored

### Architecture impact — 1.3.48 Venus psychological ingest

- **SoT before:** Venus psych slot empty. Ledger = classical moisture + Watters love/desire + Hand bonding + Rudhyar inward-way. Inner Planets p.69 NEED_OWNER. Sullivan *Venus and Jupiter* cataloged unread (CPA page/reviews only).
- **SoT after:** Venus psych slot filled from Sullivan official-site Apollon excerpt of *Venus and Jupiter* (`erinsullivan.com` Eros and Aphrodite) as `psychological` `school_specific`. Dual Goddess seminar body still unread. Inner Planets p.69 still NEED_OWNER. `object.function` unchanged. No CORE. Remaining empty psych slot: Mars. Recount still deferred until Mars is also non-empty.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.48; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Venus `function` still classical moisture; CORE still unscored

### Architecture impact — 1.3.49 Mars psychological discovery (no ingest)

- **SoT before:** Venus psych filled 1.3.48. Remaining empty psych slot: Mars. Inner Planets p.138 NEED_OWNER.
- **SoT after:** Mars psych slot still empty after independent field re-check. No legally readable dedicated principle locus. p.138 still NEED_OWNER. `object.function` unchanged. No CORE. Recount still deferred. Next: densify Sun psychological, one locus.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.49; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Mars `function` still classical heat/dryness; CORE still unscored

### Architecture impact — 1.3.50 Sun psychological densification

- **SoT before:** Sun psych ledger = Luminaries preview (2 claims) + Rudhyar humanistic. Apollo's Chariot NEED_OWNER. Apollon Issue 1 opened 1.3.35, not ingested (humanistic class took priority).
- **SoT after:** Sun psych densified from Greene *The Sun-god and the Astrological Sun* (CPA Apollon Issue 1 official PDF / authorized astro.com `in_sungod`) as `psychological` `school_specific`. Apollo's Chariot still unread NEED_OWNER — not substituted. Luminaries not re-ingested. `object.function` unchanged. No CORE. Remaining empty psych slot: Mars. Next: densify Moon psychological. Recount still deferred.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.50; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Sun `function` still classical heat/dryness; CORE still unscored

### Architecture impact — 1.3.51 Moon psychological densification (no ingest)

- **SoT before:** Moon psych ledger = Luminaries preview (2 claims) + Rudhyar humanistic. Costello *The Astrological Moon* NEED_OWNER.
- **SoT after:** Moon psych still only Luminaries preview after independent field re-check. No legally readable dedicated natal-Moon principle locus besides the already-ingested Luminaries preview. Costello still NEED_OWNER. `object.function` unchanged. No CORE. Remaining empty psych slot: Mars. Next: densify Mercury psychological. Recount still deferred.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.51; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Moon `function` still classical moisture; CORE still unscored

### Architecture impact — 1.3.52 Mercury psychological densification (no ingest)

- **SoT before:** Mercury psych ledger = Inner Planets Hermes (1 claim) + Rudhyar humanistic. Hand Ch.4 Mercury NEED_OWNER.
- **SoT after:** Mercury psych still only Inner Planets Hermes after independent field re-check. No legally readable dedicated natal-Mercury principle locus besides that already-ingested preview. Remaining Inner Planets Mercury chapters unread same-author densification. Hand Ch.4 Mercury still NEED_OWNER. `object.function` unchanged. No CORE. Remaining empty psych slot: Mars. Next: densify Saturn psychological. Recount still deferred.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.52; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Mercury `function` still classical convertibility; CORE still unscored

### Architecture impact — 1.3.53 Saturn psychological densification

- **SoT before:** Saturn psych ledger = Greene Introduction (2 claims) + Rudhyar humanistic + Hand professional. Remaining *Saturn: A New Look* chapters unread same-author densification.
- **SoT after:** Saturn psych densified from Tarnas official-site *Introduction to Archetypal Astrology* (Saturn/senex section) as `psychological` `school_specific`. Greene Introduction not re-ingested. Remaining book chapters still unread. `object.function` and `themes` unchanged (no `structure`). No CORE. Remaining empty psych slot: Mars. Sun/Moon/Mercury/Saturn densify budget complete. Recount still deferred.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.53; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Saturn `function` still classical cold; CORE still unscored

### Architecture impact — 1.3.54 Mars psychological densification (no ingest)

- **SoT before:** Mars psych slot empty after 1.3.49. Inner Planets p.138 NEED_OWNER. Densify Sun/Moon/Mercury/Saturn complete.
- **SoT after:** Mars psych still empty after independent field re-check. No legally readable dedicated natal-Mars principle locus. p.138 still NEED_OWNER. `object.function` unchanged. No CORE. Do not loop a fourth Mars hunt without a new readable locus. Recount still deferred. Jupiter psych paused.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.54; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Mars `function` still classical heat/dryness; CORE still unscored

### Architecture impact — 1.3.55 Mars psychological discovery (Sasportas aggression seminar cataloged unread)

- **SoT before:** Mars psych empty after 1.3.54. Inner Planets p.138 NEED_OWNER. Densify Sun/Moon/Mercury/Saturn complete. Do not loop p.138.
- **SoT after:** Independent field found a **new** dedicated psych Mars/aggression locus: Sasportas *Dynamics of the Unconscious* Part 1 (Weiser 1988 ISBN 0877286744). Body unread (Google Books empty; Archive printdisabled). Cataloged as `src.psychological.sasportas_dynamics_unconscious`, pending on Mars, **not ingested**. Forum/AbeBooks p.18 quotes unused. Not a substitute for p.138. Arroyo still front-matter; George Hellenistic is not this psych slot; Bell official site still jacket. `object.function` unchanged. No CORE. Recount still deferred. Jupiter psych paused.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.55; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Mars `function` still classical heat/dryness; CORE still unscored

### Architecture impact — 1.3.56 Mars psychological discovery (Huber Planets cataloged unread)

- **SoT before:** Mars psych empty after 1.3.55. Inner Planets p.138 and Sasportas Dynamics Part 1 NEED_OWNER. Do not loop those pages.
- **SoT after:** Independent field found a **new** dedicated psych Mars chapter: Huber *The Planets and Their Psychological Meaning* (HopeWell 2006 ISBN 9780954768027) ch. *Mars: The Masculine* p.59, identified from the official API TOC. Chapter body unread. Cataloged as `src.psychological.huber_planets`, pending on Mars, **not ingested**. Parked `psychological` (no Huber enum). Do not ingest tool-planet/masculine from TOC, garden lecture, or review. Not a substitute for p.138 or Dynamics Part 1. `object.function` unchanged. No CORE. Recount still deferred. Jupiter psych paused.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.56; handoff; gap-audit patch; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Mars `function` still classical heat/dryness; CORE still unscored

### Architecture impact — 1.3.57 ACCESS_BLOCKED (Psychological Mars)

- **SoT before:** `NEED_OWNER(author/locus)` ≠ `NEED_EVIDENCE(semantic slot)` (§6.9). An empty slot stayed open for discovery as long as any other independent author of that school class might exist. Mars psych empty after 1.3.56 with **three** dedicated unread loci (Inner Planets p.138; Dynamics Part 1; Huber *The Planets* p.59). Discovery could still hunt a fourth book because the first three were unreadable.
- **SoT after:** If an **empty** semantic slot has **≥3** quality independent dedicated loci identified and **all** are access-closed, the **slot** is `ACCESS_BLOCKED` and discovery for that slot **stops**. `NEED_OWNER` remains a locus status; `ACCESS_BLOCKED` is a slot status. No surrogate extraction. When one of the named loci becomes readable: extraction only, no new discovery. Psychological Mars = `ACCESS_BLOCKED` (3 loci, 0 chapter bodies, 0 claims). §6.10 empty-slot + densify budget **closed**. Pipeline continues. Recount now allowed (owner accepted this empty-slot close). No CORE. `object.function` unchanged.
- **Public contract changed?** no
- **Migration required?** no — not a schema enum; lives in canon + Mars `gap_notes`
- **Canon updated?** yes — this doc §6.9 · §6.10 · **§6.11** · changelog 1.3.57; handoff; gap-audit patch; parent research order; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; Mars `function` still classical heat/dryness; CORE still unscored; 0 psych Mars claims

### Architecture impact — 1.3.58 Sun→Pluto live recount

- **SoT before:** gap-audit dashboard still carried 1.3.24/1.3.44 snapshot language in places (CORE=0 as lead KPI; “next = Pluto psychological”; Mars as empty hunt). Those lines contradicted 1.3.45–1.3.57 (Pluto COVERED; Mars ACCESS_BLOCKED; 491 planet claims).
- **SoT after:** `IL1_SUN_PLUTO_GAP_AUDIT.md` is the live Sun→Pluto recount from current ledgers. KPI order: psychological coverage → school-class coverage → access-blocked slots → unresolved collisions → CORE candidates → CORE. Psych slots classified COVERED / THIN / DISCOVERED / ACCESS_BLOCKED / EMPTY. Semantic gaps ≠ access gaps. Queue rebuilt from that recount. No ingest. No CORE scoring. No object changes.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this changelog 1.3.58; gap audit rewrite; handoff; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; claims/`function` unchanged; CORE still unscored

### Architecture impact — 1.3.59 planet research-stable + Layer 2 definition pass

- **SoT before:** after 1.3.58, the named next task was still an access *queue* that could be read as “keep generating planet research.” Layer 2 fill-rule said wait for Arroyo/Rudhyar — author-first, the same error as Greene/Hand on planets. CORE scoring still tempting as the next planet KPI.
- **SoT after:** Sun→Pluto planet fill is **research-stable**, not semantically finalized. IL-1 must not generate planet research tasks to raise coverage. Planet work is opportunistic: a **named** locus opens → extract; otherwise do not hunt a fourth analog. CORE scoring stays blocked. Next large step is a **definition pass** of Layer 2 Signs (parent research order steps 1–4) **before** schools/bibliography/ingest. “Wait for Arroyo/Rudhyar” withdrawn as author-lock. No schema change this pass. No 12 sign objects. No planet ingest.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this doc §6.12 · §6.13 · Layer 2 fill-rule; changelog 1.3.59; handoff; gap audit queue; parent; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; catalog 24 draft unchanged; CORE still unscored

### Architecture impact — 1.3.60 Layer 2 Signs schools + source types

- **SoT before:** Layer 2 had a definition pass (§6.13) but no school list of its own. Sign claim files still carry `pending_source_ids` Arroyo/Rudhyar — the author-first leftover. Next agent could treat those names as the schools.
- **SoT after:** Layer 2 reuses the existing `source_class` enum as the school lines the model must distinguish (classical · traditional · psychological · humanistic · professional). Mapping is to **constituent bands**, not to surnames. No new enum. Vedic/sidereal is a coordinate identity, not a school of the same object. Evolutionary / Huber-API stay parked until a locus is classified — no new class this pass. Source *types* (step 6) are classes of text, not a bibliography. Literature map / shortlist / ingest still wait. No schema change. No 12 sign objects.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this doc §6.14 · changelog 1.3.60; handoff; parent; tracker FOUNDATION NOW
- **Backward compatible?** yes — no runtime wiring; pending Arroyo/Rudhyar rows unchanged and **not** promoted to shortlist

---

## 0. Зачем останавливать Today-контент

Сейчас продукт пытается получить качественный **персональный** результат раньше, чем есть система знаний, из которой результат собирается.

Pipeline уже назвал дыру: **Astrology Interpretation Canon (lookup) — нужен**. Пока lookup пуст, Global/Personal Narrative продолжают «вспоминать» значения в промпте.

Это не библиотека гороскопов и не тысячи абзацев.  
Один knowledge object → десятки корректных пользовательских выражений.

**Freeze (Today content):** не расширять narrative prompts / formula banks / slot-polish, пока нет IL-3 Engine (темы выбираются до LLM). I0 и product cycle **не** переоткрываются.

**Freeze (методология IL):** не менять слои / evidence tiers / provenance shape до первых ~100 объектов (IL-1). **1.3.29–1.3.30** — исключения: author-first очередь и фиксация ядра от доступных книг. **1.3.45** — remaining planet budget = empty psychological slots. **1.3.57** — `ACCESS_BLOCKED(slot)`. **1.3.59** — planet fill research-stable / opportunistic; Layer 2 definition before bibliography. **1.3.60** — Layer 2 schools + source types before literature map. Следующее ядро: полный research order. Дальше — только баги модели.

**Разрешено параллельно:** транспортная честность, routing, visual foundation, DS, баги, геометрия, ScreenFlow без новой семантики, **Swiss licensing gate** (не блокирует research IL-1).

Сиблинги (уже есть, не дублировать):

| Домен | Meaning SoT | Machine SoT |
|-------|-------------|-------------|
| Tarot | [TAROT_CARD_BASE_V1](../tarot/TAROT_CARD_BASE_V1.md) + [KB](../tarot/TAROT_KNOWLEDGE_BASE_V1.md) | `DATA/reference/tarot/machine/` |
| Numerology | [NUMBER_BASE_V1](../numerology/NUMBER_BASE_V1.md) | `DATA/reference/numerology/machine/` |
| Astrology | **этот документ** (IL-1 draft) | AMC 39 атомов |

**Не путать с ILR** ([INTERPRETATION_LAYER_AND_REFERENCE](../explainability/INTERPRETATION_LAYER_AND_REFERENCE.md)): там signals поведения пользователя. Здесь — символические примитивы.

---

## Sequence (LOCKED)

```text
IL-0 Foundation
  corpus registry · evidence levels · provenance schema · legal/licensing gates (declared)
       ↓
IL-1 Canon primitives   ~100 surface-neutral objects · corpus only · review
       ↓
IL-2 Composition        planet×sign · planet×house · aspect · natal aspect
                        transit→natal · merge of several signals
       ↓
IL-3 Interpretation Engine
  Swiss/JPL → calc facts → knowledge objects → clustering
  → relevance → primary / supporting themes
       ↓
IL-4 Expression         generative layer only here
                        meaning already chosen; voice for Profile / Today / Compatibility
       ↓
scale the library
```

| ID | Что это | Не это |
|----|---------|--------|
| **IL-0** | Foundation: корпус, методика, schema, declared gates | наполнение объектов |
| **IL-1** | ~100 канонических объектов из корпуса | `today_message` / проза экрана |
| **IL-2** | **правила** композиции (не каталог всех пар) | 10 000 JSON-гороскопов |
| **IL-3** | детерминированный engine тем | LLM |
| **IL-4** | выражение уже выбранного смысла | решение «что значит Saturn □ Venus» |

### Activation gates (не методология)

Не меняют sequence / ontology / evidence. Стоп **перед `status: active`**, не перед IL-1 draft.

1. **`requires_action` boolean.** Пока объекты `draft` и runtime их не читает — допустимый компромисс. `false` на неподтверждённом локусе ≠ «аспект не требует действия». До первого `active`: либо representation перестаёт быть двусмысленным boolean, либо ingest/runtime контракт запрещает читать это поле как отрицательное утверждение. `active` с такой двусмысленностью **запрещён**. Схему из-за IL-1 не расширять.
2. **Layer 5 gold list.** ~50–60 комбинаций в IL-1 = **curated candidates**, не доказанные исключения из IL-2. Критерий `non_compositional` окончательно проверяется только после composition rules. IL-2 может разжаловать объект из curated в composed. Sequence не меняется.

Пользовательский provenance позже: школьный слой (*Traditional* · *Modern psychological* · *Cross-tradition* · *TodayFlow synthesis*), не locus («Lilly p.57»). Это [Trust Layer](../content/TODAYFLOW_TRUST_LAYER.md) / Expression, не ingest IL-1.

**IL-0 закрыт** (2026-08-17) как foundation. Следующий execution slice = **IL-1**.  
Масштаб библиотеки — только после IL-4.

### Runtime stack (Swiss *в* IL-системе)

Лицензию Swiss выносим из content/research track. **Эфемериды из IL-системы не выносим.**

Без Swiss (или другого ephemeris source) динамическая часть IL не знает, какие knowledge objects активны сейчас.

```text
Swiss Ephemeris / JPL     что физически где и когда
        ↓
Calculation layer         знаки, дома, аспекты, транзиты, орбисы
        ↓
Interpretation Library    что эти конструкции означают
        ↓
Interpretation Engine     какие значения важны этому человеку сейчас
        ↓
Expression                как показать (Profile / Today / Compatibility)
```

Пример:

```text
Swiss: Saturn = 14° Aries, natal Venus = 14° Cancer
  → calc: transiting Saturn square natal Venus
  → IL: knowledge object astro.combo.transit.saturn.square.natal.venus
  → engine: relevance / aggregation
  → Today (IL-4 pack, surface=today)
```

Ответственность не смешивать:

| Слой | Решает | Не решает |
|------|--------|-----------|
| Swiss / JPL | долгота, время, координаты | смысл Saturn □ Venus |
| Calculation | аспект, дом, орбис, «это square» | трактовку |
| Interpretation Library | каноническое значение конструкции | что показать *этому* человеку *сегодня* |
| Interpretation Engine | активность, кластер, relevance | прозу экрана |
| Expression | формулировку под surface | астрологическое значение |

**IL-1 constraint:** первые ~100 объектов проектировать под сущности, которые реально выдаёт Swiss + наш Astro/calculation layer (`transiting_planet`, `aspect`, `natal_point`, sign, house, major aspect ids). Не вводить в канон конструкции, которых calc не эмитит (квинконс OOS v1 — Foundation §2.4). Иначе получится ontology, которая плохо маппится на вход IL-3.

### Surface-neutral (жёстко, IL-1)

Первые ~100 объектов **не пишутся под Today**.

Запрещены поля и смыслы вида `today_message`, `today_copy`, `profile_blurb`, `compatibility_line`, «сообщение на сегодня», CTA экрана. Saturn = function / themes / domains / polarity — не заготовка строки Today.

Тест объекта шире, чем sky → Today:

> Один knowledge object, если релевантен, должен корректно обслужить **Profile**, **Today** и **Compatibility**. Разница поверхностей — IL-4 Expression pack (tone, length, focus), не разные значения в каноне.

### Swiss licensing — параллельный gate, не отдельный технический мир

Эфемериды = вход runtime IL (см. Runtime stack).  
**Лицензия** Swiss = бинарный legal gate (Foundation §1.4): коммерческое использование текущей `pyswisseph` конфигурации либо покрыто выбранной лицензией, либо до публичного сервиса меняется лицензирование/реализация.

Лицензионный вопрос **не блокирует** research Greene/Hand/Valens и создание первых 100 knowledge objects.  
До проверки полного pipeline `raw sky → knowledge objects → Today` Swiss уже является входом этого pipeline.

Не писать «Swiss вне IL». Писать: **Swiss licensing вне content track IL**.

---

## 1. Слои (строить строго снизу)

Комбинаторный взрыв `planet × planet × aspect × house × sign` **запрещён** как каталог. Согласовано с [ACM-Compose](../ASTROLOGY_COMPOSITION_MODEL.md): атомы в Reference; композиты — runtime. Исключение: **узкий curated Layer 5** только там, где сложение атомов врёт — в IL-1 это **candidates** (activation gate 2).

```
Layer 1 Objects  →  Layer 2 Signs  →  Layer 3 Houses  →  Layer 4 Aspects
        ↓
Layer 5 Combinations (compose default; curated if non-compositional)
        ↓
Meaning normalization (theme clusters)
        ↓
Profile relevance (priority, not meaning)
        ↓
Expression pack → LLM (IL-4; voice only; `surface` lives here)
```

### Layer 1 — Objects

Sun · Moon · Mercury · Venus · Mars · Jupiter · Saturn · Uranus · Neptune · Pluto · ASC · MC.

v1.1: North Node · South Node · Chiron · Lilith (Mean Apogee) — identity уже в Foundation §2.2.

Поля: `function` · `themes[]` · `positive_expression` · `shadow` · `domains` · `tempo`.

Не статья «Что такое Сатурн».

**IL-1 fill:** Valens I.1 — topical/significator catalog (sect, colour, taste), не Ptolemy/Lilly elemental qualities. Saturn injuries from cold+moisture не схлопывать в dryness. Greene Weiser Classics 2021 Introduction — первый `psychological` school_class: psychic process / pain-toward-self-discovery остаются `school_specific`. Houlding *Saturn: The Great Teacher* (Skyscript 2003) — living-traditional: cold/dry/malefic/slow compared; personal boundary and mature-through-constraint остаются `school_specific`. Watters *Astrology For Today* 2003 (Skyscript planet intros) — classification gap: modern general practical, parked `source_class=professional` / `school=modern_general_practical`, not Houlding traditional and not Hand; `school_specific` only. Greene *The Luminaries* preview — Sun/Moon psychological `school_specific` (solar consciousness / embodiment); Greene *The Inner Planets* preview — Mercury Hermes-spontaneity `school_specific`. Greene *By Jove!* authorized astro.com extract — Jupiter individuation-teleology / gluttony-as-unconscious-quest `school_specific` (not CPA page, not Hand expansion). Rudhyar *New Mansions for New Men* (1938; Khaldea archival) Venus, Mars, Uranus, Neptune, Pluto, Sun, Moon, Mercury, Saturn, Jupiter — `humanistic` school_class: inward way / first-gesture / transform-through / ecstasy-realm / celestial-seed / light-as-integration / song-of-life / weaver-of-relationship / I-am-I-boundaries / organizer-of-functions `school_specific`; не psychological и не CORE с Greene или Hand. Do not collapse to consciousness vs unconscious as CORE. Body/health/fertility rows stay in the claims ledger, not `object.domains`. `function` черновиков не усреднять. Не записывать Ptolemy в подтверждающие structure-setting. Uranus, Neptune and Pluto: Hand 1981 + Rudhyar NMNM claims ledger only (objects withheld). Calc already emits all three. Objects withheld — celestial_object slots would force a school fill or invent natal domains. Hand sequence (not CORE): Uranus disrupts; Neptune dissolves distinction; Pluto reconstructs after total crisis. Rudhyar sequence (not CORE, not merged with Hand): Uranus transforms; Neptune ecstasy/prenatal; Pluto sows seed / hierophant of birth. Do not flatten outers to generic transformation. Psychotic-crisis/medication example excluded (not a medical causal model). Not later Hand. ASC/MC still closed.

### Layer 2 — Signs

Aries → Pisces.

Поля: `mode` · `element` · `orientation` · `motivation` · `expression` · `strengths[]` · `excess[]` · `deficiency[]` · `behavioral_tendencies[]`.

Identity (ruler, dates) остаётся в Foundation §2.1 — **не копировать** в IL.

**IL-1 fill:** `motivation` / `strengths` / `excess` / `deficiency` / `behavioral_tendencies` не «ошибка схемы» — они могут быть *later interpretive* составляющими, не обязательным каркасом IL-1 draft object. Классические деления знака (Ptolemy I.14–I.15, I.21; Lilly CA I.16) их не подтверждают. **1.3.59:** не ждать Arroyo/Rudhyar как обязательных авторов. Сначала definition pass (§6.13), затем школы/типы источников (§6.14), затем карта литературы, затем ingest. 12 sign objects не материализовать в этом пассе.

`element` и `mode` **не унифицировать** задним числом: Lilly fiery/earthly/airy/watry и Ptolemy winds/rulers — разные системы; Ptolemy tropical/equinoctial ≠ Lilly moveable/cardinal. Valens I.2 Aries = fiery *и* watery (weather) — не подтверждение Lilly fire. Mismatch со schema (`cardinal|fixed|mutable`, четыре стихии) — gap_note, не silent collapse.

**Commanding / obeying:** группировка summer/winter (Aries–Virgo vs Libra–Pisces) compared (Ptolemy I.17 + Lilly CA I.16 p.91). Pair-relation Ptolemy I.17 (равное расстояние от равноденствия) Lilly list не подтверждает — не схлопывать. Ptolemy I.18 beholding ≠ Lilly Antiscion/Contrantiscion; ссылка Lilly на «PTOL. APHO.» не consensus.

### Layer 3 — Houses

1–12.

Поля: `domain` · `internal_meaning` · `external_manifestations[]` · `people[]` · `activities[]` · `resources[]` · `risks[]`.

**IL-1 fill:** draft-объект `domain` остаётся Lilly CA I.7 (не усреднять). Valens IX XII Places compared только по тонким lemmas (life, brothers, marriage…). Houlding *Houses* extract (1/6/7/12) — первый `traditional` school_class: personality на 1-м и known-enemies rule на 7-м не копировать в `domain`. Derived-place / turned-house — gap, схему не расширять. Lilly «Ptolomeian Doctrine» ≠ Ptolemy+Lilly; Ptolemy I.13 по-прежнему не 12 topical houses.

### Layer 4 — Aspects (major only, v1)

Conjunction · Opposition · Square · Trine · Sextile.

Не готовые трактовки пар, а **характер взаимодействия**:

| Аспект | `interaction` |
|--------|----------------|
| conjunction | merging / amplification |
| square | friction requiring action |
| opposition | polarization / projection |
| trine | easy flow / access |
| sextile | opportunity requiring participation |

Таблица — **смысл слота**, когда локус его подтвердит. Не default для копирования в объект.

**IL-1 fill:** Ptolemy I.16 даёт только harmonious / discordant. Lilly CA I.1 даёт good / enmity / concord — другая качественная система; в `object.interaction` не копировать. Lilly CA I.19 (p.105) уточняет: square = imperfect enmity, opposition = perfect hatred; orbs = planetary moieties (две таблицы, from memory), не aspect-orbs. Houlding 1995/2004: orbs принадлежат планетам; square не «просто плохой»; качество зависит от планет (это IL-2, не Layer 4 default). В объект не копировать. Geometry 0/60/90/120/180 compared. `requires_action` в схеме — boolean (нет `unknown` / `not_evidenced`). `false` = свойство **не установлено данным локусом**, не утверждение «square не требует действия». Схему из-за этого не расширять. **Activation gate:** `status: active` с таким boolean запрещён, пока representation или runtime-контракт не снимут двусмысленность.

Миноры (Foundation §2.4) — не Layer 4 v1.

### Layer 5 — Combinations

Только после атомов.

Типы: `planet_in_sign` · `planet_in_house` · `natal_aspect` · `transit_to_natal` · `transit_through_house`.

**Default (IL-2):** Composition Engine собирает объект из атомов (не JSON на каждую пару).  
**Curated (часть IL-1 gold):** `curation_reason: non_compositional` — *кандидат* на исключение, пока IL-2 не подтвердит, что сложение атомов врёт. IL-2 может разжаловать в composed. Всё равно **surface-neutral**.

Хранить в `DATA/reference/astrology/interpretation_v1/` — **не** в `machine/`. ACM freeze на composite **machine** JSON остаётся.

---

## 2. Knowledge object (данные, не copy)

Пример формы — транзит, не пользовательское предложение:

| Поле | Содержание |
|------|------------|
| phenomenon | Saturn square natal Venus |
| type | `transit_to_natal` |
| base_meaning | ограничения / проверка ценностей, отношений, удовольствия |
| psychological | переоценка привязанностей и собственной ценности |
| domains.relationships | дистанция, серьёзность, проверка отношений |
| domains.money | ограничения, осторожность, пересмотр расходов |
| domains.work | ценность собственного труда, компенсация |
| opportunity | установить более зрелые границы |
| risk | изоляция, холодность, чрезмерный пессимизм |
| action | пересматривать, устанавливать границы, упрощать |
| avoid | окончательные выводы из временного эмоционального состояния |
| intensity | runtime (орбис) — в объекте только `intensity_rule` |
| temporal_class | `medium` |
| polarity | `challenging` + `constructive` |
| theme_clusters | `relationships` · `boundaries` · `values` |
| confidence | после review |
| provenance | source → passage/concept → normalized claim → reviewer → version |

Engine уже может сказать (это **не** хранится в объекте):

- *Relationships may feel more serious than usual today. Don’t mistake temporary distance for a final answer.*
- *Money decisions deserve more scrutiny right now. What feels restrictive may actually be forcing you to clarify what is worth paying for.*

### Запрещено в объекте

- обращение на «ты» / «you»;
- «сегодня», даты, имена;
- поля экрана (`today_message`, `profile_blurb`, `compatibility_line`, …);
- абзацы-гороскопы;
- коммерческие дампы (Co-Star и аналоги);
- текст, единственный источник которого — LLM.

---

## 3. Meaning normalization

Несколько независимых сигналов часто описывают **один** кластер.

Нельзя печатать четыре интерпретации:

- relationships difficult
- relationships serious
- relationships challenged
- emotions intense

Engine поднимает кластер:

`RELATIONSHIPS` / `BOUNDARIES` / `EMOTIONAL_PRESSURE`

Три независимых сигнала об одном → выше `confidence` / relevance темы.  
На экране: **Today’s relationship theme**, не перечень транзитов.

Закрытый набор `theme_clusters` (v1):

`identity` · `emotions` · `relationships` · `boundaries` · `values` · `money` · `work` · `communication` · `body` · `home` · `growth` · `meaning` · `power` · `change` · `timing`

Новый кластер = bump контракта, не свободная строка.

---

## 4. Profile relevance ≠ астрологическое значение

```
Sky × Natal × Profile × Current goals/context  →  Relevance
```

Тот же транзит не занимает одно место у всех. Если сигнал про `work`, а у человека активна карьерная цель — **растёт приоритет показа**. Астрологическое значение **не** переписывается.

Это не персонализация смысла («у тебя Сатурн значит другое»). Это ранжирование.

---

## 5. LLM — только IL-4 Expression

LLM **не** решает, что означает Saturn square Venus.

Вход (expression pack):

```yaml
primary_theme: boundaries in relationships
theme_clusters: [relationships, boundaries]
supporting_signals:
  - astro.combo.transit.saturn.square.natal.venus
  - astro.combo.planet_in_house.moon.07
opportunity: clarify expectations
risk: interpreting distance as rejection
profile_relevance:
  note: relationship goal active
  boost: 0.4
tone: direct_grounded
length_words: [22, 35]
locale: en
surface: today
```

Задача модели: выразить это хорошо.  
Запрет: новые темы, астрожаргон как содержание, прогноз-дата, противоречие pack.

Это тот же паттерн, что Tarot pack: факты в KB, LLM — автор ответа.

---

## 6. Research corpus — как собираем, не «какую базу скачать»

Готовой Interpretation Library не существует. Её нужно **собрать**: традиционная основа + современная интерпретация + собственная нормализация.

Реестр кандидатов: [`DATA/reference/astrology/interpretation_v1/source_corpus_v1.json`](../../DATA/reference/astrology/interpretation_v1/source_corpus_v1.json) (все `status: candidate`).  
Схема: [astrology_source_corpus_v1.schema.json](../schemas/astrology_source_corpus_v1.schema.json).

Ни один источник не `approved` как закрытый product-SoT, пока строка не прошла legal review. **IL-1 не ждёт legal `approved` для research ingest:** при `ingest_rule: research_paraphrase` можно извлекать claims из `candidate`. Копирование текста запрещено. Swiss dual-license **не** условие старта IL-1.

### 6.1 School classes (смысл)

| Уровень | `source_class` | Зачем | Примеры в корпусе / пуле |
|---------|----------------|-------|--------------------------|
| Первоисточники | `classical` | исторический фундамент западной традиции | Ptolemy *Tetrabiblos* · Valens *Anthologies* · Dorotheus *Carmen* · Firmicus *Matheseos* · Lilly *Christian Astrology* |
| Живая традиционная школа | `traditional` | нормализация ontology (аспект ≠ «плохо») | Skyscript · Deborah Houlding (houses, aspects/orbs) |
| Психологическая / depth | `psychological` | человеческая динамика (CPA / Jungian / depth) | Greene · Sasportas · Clare Martin · Lynn Bell · Demetra George. CPA определяет направление шире, чем «метод Greene» (astrology × depth, humanistic and transpersonal psychology) |
| Гуманистическая | `humanistic` | humanistic astrology как отдельная интеллектуальная традиция | Dane Rudhyar (*New Mansions…* и последующая линия). **Не** парковать как `psychological` — иначе ложный CORE с Greene |
| Современный professional / synthesis | `professional` | язык практики / синтеза | Robert Hand · (пул) Stephen Arroyo. Arroyo в каталоге ещё числится `psychological` — unused row; новый ingest классифицирует по открытому локусу, не по фамилии |

**Project Hindsight** (с 1993) — доступ к эллинистическим текстам. Это **программа переводов**, не один том. Древний оригинал может быть public domain; **современный перевод защищён**. Hindsight = research, не копипаст в JSON.

Skyscript: структурированная библиотека (planets, houses, aspects, natal, predictive, stars, rulerships, orbs, history). Houlding по аспектам/орбам нужна именно ontology: planetary orbs vs modern aspect orbs. **Статьи не копировать** — концепт → сверка → своя запись.

Несколько независимых школ обязательны. Не выбираем одного «правильного» автора. Авторы внутри пула **не** взаимозаменяемы (Arroyo ≠ Greene — полезный конфликт, не баг). `source_class` отражает традицию локуса, а не удобство для конвергенции.

### 6.2 Астрономия — вход IL, не источник смысла

Положения тел **не** берутся с astrology websites. Они питают calculation layer, который активирует объекты IL.

| Источник | Роль у нас |
|----------|------------|
| **Swiss Ephemeris** | LIVE runtime вход: `todayflow-astro` · `pyswisseph` · `FLG_SWIEPH` · `astro/ephe`. Сжатые файлы воспроизводят NASA JPL **DE431** (Astrodienst; Swiss 2.00+). Публичные формулировки — [Trust Layer](../content/TODAYFLOW_TRUST_LAYER.md) · [Foundation §1.4.1](../foundation_v1.md) |
| NASA/JPL Horizons | кандидат на независимую сверку позиций; **не wired** — нельзя утверждать в копирайте как live источник |

Swiss Ephemeris — **dual license** (Astrodienst): GNU AGPL **или** Swiss Ephemeris Professional License. Выбор должен быть сделан **до** публичного сервиса. В репозитории **нет** артефакта Professional License. `todayflow.today` уже публичен.

Это **legal gate** (Foundation §1.4), параллельный content/research track. Не стоп для IL-1. Не отдельный от IL технический мир: без эфемерид IL-3 не знает активных объектов.

`ingest_rule: facts_only` — Swiss/JPL не дают трактовок в knowledge object.

### 6.3 Запрещено как фундамент

Не строить IL на: Astro-Seek interpretations · random blogs · Reddit · TikTok/Instagram astrology · Co-Star · The Pattern · Sanctuary · **ChatGPT/LLM-generated interpretation dumps**.

«Создай 5000 трактовок» даёт объём без происхождения. Это противоположность IP, который нам нужен.

### 6.4 Юридическое правило ingest

```text
оригинал / издание  →  исследователь читает
                    →  записывает УТВЕРЖДЕНИЕ (paraphrase)
                    →  указывает locus (глава/стр.), не цитату перевода
                    →  в библиотеку попадает normalized_claim
```

**Запрещено** класть в объект / claim ledger: абзац современного перевода, скрап Skyscript, текст Co-Star, вывод LLM как `source`.

IL-1 research artifacts (pipeline, not a new ontology): `DATA/reference/astrology/interpretation_v1/claims/<object_id>.json` → `objects_v1.json`. Ledger schema: [astrology_claims_v1.schema.json](../schemas/astrology_claims_v1.schema.json). Knowledge-object schema не расширяется «на всякий случай»; дыры фиксируются в `gap_notes` на реальном материале.

`original_claim` в provenance = **наша** короткая формулировка утверждения автора, не его copyrighted prose.

### 6.5 Методика одного объекта (пример: Saturn square natal Venus)

Берём Hand · Greene · traditional (Lilly/Houlding/Skyscript) · ещё 1–2 professional.

Из каждого — не текст, а **утверждения**:

`constraint` · `relationship testing` · `value reassessment` · `financial restraint` · `self-worth` · `distance` · `commitment` · `maturation`

Смотрим пересечение.

Если 4 независимых источника: restriction + relationships + values + maturation → кандидат в **CORE**.

Если один автор: «обязательно произойдёт расставание» → **не** входит в базу автоматически. Максимум `school_specific` после review, чаще `rejected`.

### 6.6 Уровни доказательности

| `evidence_tier` | Смысл | Что можно в продукте |
|-----------------|-------|----------------------|
| **core** | почти все выбранные школы | primary theme Today / Profile |
| **supported** | несколько авторитетных источников | supporting signals |
| **school_specific** | одна школа | tint; не выдавать как «астрология говорит» |
| **editorial** | нормализация TodayFlow | только с reviewer; не маскировать под традицию |

Разница обязательна:

- Пока CORE по Saturn **не scored**: classical cold/dry/malefic, Houlding boundary/constraint и Greene psychic-process — разные категории, не пересечение. Не записывать Ptolemy в `schools_confirming` для structure-setting.
- не CORE: *Saturn square Venus значит, что партнёр отдалится*

Канон — не усреднённая «одна астрология». Provenance держит слои различимыми. Когда приходят Greene, Hand, Rudhyar, Sasportas, Martin, Arroyo, George: смотреть, что с классическим claim произошло (продолжено / переосмыслено / психологизировано / заменено). Классические lemmas **не затирать** современным пакетом. Не объявлять два современных автора одной school class, чтобы получить CORE.

Это следствие **публичное**: бренд не продаёт одну современную трактовку как единственную истину. Копирайт (лендинг, реклама) — [Trust Layer](../content/TODAYFLOW_TRUST_LAYER.md), не этот §6.

Engine: primary theme только из `core` ∪ `supported`. `editorial` не может быть единственным основанием пользовательского утверждения.

### 6.7 Пайплайн (не 50 книг вручную в таблицу)

```text
corpus (classical + traditional + psychological + humanistic + professional)
        ↓
извлечение утверждений
        ↓
нормализация (свои lemmas)
        ↓
сопоставление авторов
        ↓
consensus scoring → evidence_tier
        ↓
human review
        ↓
Interpretation Library object
```

LLM в этом пайплайне **может** помогать извлекать кандидаты-утверждения из текста, который исследователь уже легально читает. Не может быть источником. Каждая строка проходит human review.

### 6.8 Provenance (IP)

Через год «почему Saturn □ Venus = проверка отношений?» → конкретные `concept_id`, авторы, издания, locus, normalized_claim, tier, reviewer — не «так написал GPT».

Поля claim / provenance row:

`concept_id` · `source` · `author` · `edition` · `locus` · `original_claim` (paraphrase) · `normalized_claim` · `school` · `evidence_tier` · `review_status` · `field`

`review_status`: `extracted` → `compared` → `reviewed` | `rejected`.

### 6.9 Source discovery (1.3.29; parent 1.3.30)

Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Модель знания (составляющие + определения) проектируется **до** карты литературы. §6.9 — правило *внутри уже начатого* IL-1 planet fill: не фиксировать обязательных авторов. Это не шаблон для следующего ядра.

Author-first очередь Greene → Hand была методологической ошибкой: сильный источник ≠ обязательный источник. Psychological astrology — не «метод Greene»; CPA описывает школу как соединение astrology с depth, humanistic и transpersonal psychology.

**`NEED_OWNER(author/locus)`** означает только отсутствие этого конкретного источника. Он **не** означает `NEED_EVIDENCE(semantic slot)`, пока не проверены другие независимые авторитетные источники той же school class.

**`ACCESS_BLOCKED(semantic slot)`** (1.3.57) — не NEED_OWNER и не NEED_EVIDENCE. Если для **пустого** слота найдены **≥3** качественных независимых dedicated loci и все закрыты по доступу, discovery **этого слота** прекращается. Локусы остаются NEED_OWNER. См. §6.11.

**Порядок выбора локуса:** качество × независимость × релевантность × легальная доступность. Поиск: официальный сайт автора/школы → издательский preview → профессиональная астрологическая организация / авторизованный архив с авторским текстом → легально читаемая книга/статья. В evidence **не** идут: SEO-астрология, анонимные explainer'ы, рецензии, jacket copy, bookseller TOC, агрегаторы, pirate dumps, reconstruction из памяти модели.

**Пулы (не жёсткая очередь фамилий):**

- psychological/depth: Greene, Sasportas, Clare Martin, Lynn Bell и другие этой линии
- humanistic: Dane Rudhyar и последующая humanistic tradition (не auto-`psychological`)
- modern professional/synthesis: Robert Hand, Stephen Arroyo и др.
- traditional/classical: существующие линии отдельно

Новые reputable авторы/книги **разрешены**. Расширять discovery до **semantic saturation**: новый качественный источник перестаёт давать существенно новые lemmas и не меняет картину конвергенций/конфликтов. Не ставить произвольное «ещё N авторов».

Существующие NEED_OWNER локусы Greene/Hand остаются pending. Другой независимый автор той же school class **может** закрыть semantic gap. Не заменять закрытую страницу пересказом того же автора.

Extraction first. Cross-source comparison только после extraction. No `object.function` rewrite. No automatic CORE promotion.

### 6.10 Remaining IL-1 planet budget (1.3.45)

The live gap after 1.3.44 is **not** “too few planet claims.” It is **psychological coverage imbalance**. Further classical / traditional / humanistic / professional accumulation does not raise canon value until the empty psych slots exist as independent models.

**Budget (locked until the five empty psych slots are non-empty *or* `ACCESS_BLOCKED`):**

```text
Pluto → Uranus → Neptune → Venus → Mars
then densify Sun / Moon / Mercury / Saturn
Jupiter psychological: paused
```

**Rules inside this budget:**

- Search for an authoritative psychological/depth source that independently defines the object. Do **not** search for confirmation of Hand lemmas (reconstruction / disruption / dissolution / bonding / survival).
- Humanistic Rudhyar is a third intellectual line. It is **not** a psychological substitute.
- `NEED_OWNER(Greene/Hand locus)` does not block another independent psychological source.
- Extraction first. Compare only after extraction exists. Do not average Uranus/Neptune/Pluto models.
- CORE=0 is **not** a KPI. The CORE rule stays: same lemma across **school classes**. Library value lives in same / related / different-register / reinterpretation / conflict / school-specific relations, not only in `core`.
- Full Sun→Pluto recount only after Pluto, Uranus, Neptune, Venus, and Mars psychological slots are all non-empty **or** the remaining empty slot is `ACCESS_BLOCKED` (owner-accepted close). Not after each book.

Outer planets are the stress-test: classical absent historically; humanistic Rudhyar + professional Hand exist; psychological was empty. Holding three models without averaging is the proof of the library.

**Progress inside this budget:** Pluto filled 1.3.45 (Greene/Campion interview). Uranus filled 1.3.46 (Tarnas official intro — not the unread monograph). Neptune filled 1.3.47 (same Tarnas PDF, Neptune section, after field check). Venus filled 1.3.48 (Sullivan official-site *Venus and Jupiter* excerpt — not Inner Planets p.69). Sun densified 1.3.50 (Greene Apollon Issue 1 / astro.com in_sungod — not Apollo's Chariot). Moon still only Luminaries preview after 1.3.51 field re-check (Costello still NEED_OWNER). Mercury still only Inner Planets Hermes after 1.3.52 field re-check (remaining chapters unread). Saturn densified 1.3.53 (Tarnas official intro Saturn/senex — not remaining *Saturn: A New Look* chapters). Densify Sun/Moon/Mercury/Saturn complete. **1.3.57:** Psychological Mars = `ACCESS_BLOCKED` (Inner Planets p.138; Dynamics Part 1; Huber *The Planets* p.59 — all NEED_OWNER; 0 readable bodies; 0 claims). Discovery for this slot **stops**. Do not hunt a fourth Mars book. Do not ingest Huber masculine from TOC. When one of those three chapters is readable: extraction only. **§6.10 empty-slot + densify budget closed.** Recount now allowed. Jupiter psych paused.

**1.3.58:** Live Sun→Pluto recount from ledgers. Psych coverage: COVERED 7 · THIN 2 · ACCESS_BLOCKED 1 (Mars) · EMPTY 0. 1.3.44 dashboard retired. Access wait/extract remains; it does **not** reopen planet discovery.

**1.3.59:** Planet fill is **research-stable**, not semantically finalized. IL-1 must not generate planet research to raise coverage. CORE scoring stays blocked. Next large step = Layer 2 Signs definition (§6.13), not a fourth Mars analog.

### 6.11 ACCESS_BLOCKED (1.3.57)

Three research statuses, not interchangeable:

| Status | Applies to | Meaning | Pipeline |
|--------|------------|---------|----------|
| `NEED_OWNER(author/locus)` | one edition + pages | that page is closed | continue; another independent author of the school class may fill the slot (§6.9) |
| `NEED_EVIDENCE(semantic slot)` | school-class coverage of a slot | coverage not yet shown | continue discovery |
| `ACCESS_BLOCKED(semantic slot)` | the **empty** slot itself | ≥3 quality independent dedicated loci identified; all access-closed; 0 readable chapter bodies | **stop discovery for this slot**; do not hunt a 4th/20th source because the first three cannot be read |

`ACCESS_BLOCKED` is not a fill. Claims stay empty. No surrogate extraction, jacket, TOC, forum quotes, pirate dumps, or model memory. `object.function` is not rewritten. CORE is not scored from the absence.

The identified loci remain `NEED_OWNER`. When **one of those named chapters** becomes legally readable: return to that locus and extract only. Do not reopen a new discovery hunt for the slot.

Jacket, webinar pages, Mythic extracts, thin survey paragraphs, and pair/cycle essays do **not** count toward the ≥3 threshold. `ACCESS_BLOCKED` applies only to an **empty** school-class slot — not to a slot that already has ingested claims (Moon Luminaries, Mercury Hermes).

**Applied:** Psychological Mars = `ACCESS_BLOCKED` (1.3.57). Dedicated loci: Greene/Sasportas *The Inner Planets* p.138; Sasportas *Dynamics of the Unconscious* Part 1; Huber *The Planets and Their Psychological Meaning* ch. *Mars: The Masculine* p.59. 0 claims ingested. Mars Quartet remains jacket, not a fourth counted locus.

### 6.12 Planet fill research-stable (1.3.59)

Sun→Pluto planet research-fill is **research-stable**, not semantically finalized. EMPTY psych slots = 0. DISCOVERED = 0. Mars is ACCESS_BLOCKED (access, not missing bibliography). Moon/Mercury are THIN by choice of readable loci, not an open hunt.

IL-1 **must not** generate planet research tasks in order to raise coverage counts (claim n, psych n, CORE=0). Coverage is not a KPI that reopens discovery.

**Opportunistic / access-driven only:**

- A **named** NEED_OWNER locus becomes legally readable → extract that locus (`school_specific`). No `function` rewrite. No CORE. No `active`.
- It does not open → **do not** hunt a fourth analog to fill a counter. Mars: three dedicated independent loci already exist; a fourth book is lower marginal value than the next IL layer.
- Jupiter psych stays paused. Do not pad traditional (`ecb4cbe4`). Do not materialize outer or sign objects to look complete.

**CORE scoring stays blocked.** Five Saturn classical+traditional candidates remain listed. They are not this pass.

### 6.13 Layer 2 Signs — definition pass (1.3.59; parent steps 1–4)

Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). This is the next large IL-1 constituent after planets. Houses and aspects already have classical draft objects; ASC/MC still need an opened locus **and** calc emit; outers stay claims-only. **Signs are the gold-set hole (0 objects).** Do not start from Arroyo, Rudhyar, Greene, or Hand. Do not ingest. Do not materialize 12 sign objects in this pass. Schema required-fields are **not** changed here — Architecture impact must precede any demotion of required psych slots.

**1. Subject.** A Layer 2 *sign* is an IL knowledge object for one of twelve ecliptic spans (Aries…Pisces). It is a semantic primitive of the lookup, not Foundation identity and not a Layer 5 combination.

**2. Bounds.** A sign is not a personality type. Not a planet. Not a house. Not planet-in-sign. Ruler / dates / glyph stay in Foundation §2.1 — do not copy. Medical/body rows stay ledger-only. QUALITY one-liners do not, by themselves, justify 12 `active` or even 12 draft objects until constituents are defined. `element` and `mode` are distinct classification *systems* (Lilly fire/earth/air/water ≠ Ptolemy winds/rulers; tropical/equinoctial ≠ moveable/cardinal). Do not silent-collapse them. Commanding grouping compared; pair-relation stays school_specific.

**3. Constituents (model question, not a book).** Split before literature:

| Band | Slots | Status in this pass |
|------|-------|---------------------|
| Classification | `mode` · `element` · `orientation` (plus commanding/obeying as claims, not extra schema) | Already attested as *systems* with collisions. May later support a draft object **if** required later-interpretive slots are not forcing a fake. |
| Later interpretive | `motivation` · `expression` · `strengths[]` · `excess[]` · `deficiency[]` · `behavioral_tendencies[]` | Unattested classically. Schema currently **requires** them for `type=sign`. That requirement is why objects were withheld — the planet analog of locking Greene/Hand. Do **not** fill them from the first readable modern author. Decide in a later Architecture impact whether they stay required for IL-1 draft, become optional, or move to a later layer. |
| Exclude from Layer 2 | ruler, dates, planet-in-sign recipes, medical correspondences, compatibility one-liners, `today_message` | Already Foundation / Layer 5 / ledger-only / IL-4. |

**4. Definitions (working).**

- **Classification constituent:** a lemma that sorts the twelve spans by a named system (quadruplicity, triplicity-as-used-by-that-school, sect/gender, commanding grouping). Coverage = that system is attested. Collision between systems is kept, not averaged.
- **Later interpretive constituent:** a lemma about how a person *tends to be* in that span (motive, strength, excess, deficiency, behaviour). Coverage ≠ “we found a cookbook.” Same school-class rule as planets: CORE only if the **same lemma** appears in more than one school class after ingest.
- **Not a constituent:** Foundation identity; Layer 5 combinations; product voice.

**Stopped before step 5 in 1.3.59.** Schools and source types continue in §6.14 from this model, not from an open Arroyo chapter.

### 6.14 Layer 2 Signs — schools and source types (1.3.60; parent steps 5–6)

Reuse the existing `source_class` enum. Do **not** add `evolutionary`, `huber`, `vedic`, or `esoteric` this pass. Authors are not schools. Sign-file `pending_source_ids` for Arroyo *Four Elements* and Rudhyar *The Astrology of Personality* are catalog leftovers from author-first Layer 2 fill-rule — **not** the school list, **not** a shortlist, **not** this pass's ingest.

**5. Schools (independent lines the model must distinguish).**

| `source_class` | What a *sign* is in that line | Classification band | Later-interpretive band |
|----------------|-------------------------------|---------------------|-------------------------|
| `classical` | A span with named division systems (quadruplicity, triplicity-as-used, sect/gender, commanding grouping) and, in some loci, QUALITY/nature one-liners. Not a personality type. | Native. Already attested (Ptolemy / Lilly / Valens) with collisions kept. Lilly QUALITY parked in `field=expression` is still a nature line, not a motivation package. | Typically absent. Do not backfill `motivation` / `strengths` / `excess` / `deficiency` / `behavioral_tendencies` from QUALITY. |
| `traditional` | Living traditional ontology of the same divisions — not a modern trait list. | Native. Houlding/Skyscript remain pending; do not pad traditional (`ecb4cbe4`). Lilly already sits in the ledger as `classical` / `school=traditional_horary` — do not reclass. | Not the home of cookbook personality. A living-traditional *character* lemma, if one appears later, stays `school_specific`. |
| `psychological` | How a person *tends to be* in that span (motive, excess, deficiency, behaviour) as depth/process, not a newspaper trait list. | May reuse fire/earth/air/water or cardinal language as psyche. That is a **different lemma** from Lilly fire or Ptolemy winds — not confirmation. | Native home of the later-interpretive band. Authors inside the class are not interchangeable. |
| `humanistic` | The span as a phase of a cyclic / developmental process. | May reuse element/mode as process-phase. Different lemma again — not psychological CORE and not Lilly confirmation. | Native, but cyclic/phase, not a trait cookbook. Do not park as `psychological`. |
| `professional` | Consulting / modern-general synthesis of twelve-sign traits. | Often copies the modern four-element + cardinal grid. Copying the grid ≠ attesting Lilly or Ptolemy. | Cookbook/trait risk. Independence check required (Watters-type `modern_general_practical` stays a classification gap, not a new enum). |

**Not a school of this Layer 2 object:**

- Tropical vs sidereal — coordinate / identity (Foundation tropical lock). Not `source_class`.
- Vedic sign-meanings on a sidereal zodiac — different object identity, not a fifth western school.
- Sun-sign journalism / app copy — forbidden as foundation (§6.3), not a school.
- Evolutionary (Forrest/Green) and Huber-API age-progression — later-interpretive lines that may appear at a locus. Park in `psychological` until that locus is classified. No new enum without Architecture impact.
- Esoteric / theosophical sign scales — out of IL-1 Layer 2 bounds unless a later Architecture impact says otherwise.

CORE for signs, when eventually scored, is still the same rule as planets: the **same lemma** across **school classes**. Two classical authors ≠ CORE. Psychological + humanistic overlap on “growth” ≠ CORE. Modern four-element grid shared by professional and psychological ≠ CORE with Lilly fire.

**6. Source types (class of text, not a surname).**

Needed later, when a literature map is built:

| Type | What counts for Layer 2 | What does not |
|------|-------------------------|---------------|
| Primary treatise | A chapter whose subject is sign *divisions* or sign *nature* as principle | Planet-in-sign recipes; bounds/dignity (Foundation §2.5); medical/corporature accidentalia |
| Living-traditional article | Ontology of sign classes from a traditional school | Sun-sign columns; “Aries personality” listicles |
| School textbook | Dedicated treatment of the twelve signs or of element/mode *as sign systems* | Planet-in-sign cookbooks; compatibility; house-in-sign |
| Professional synthesis | A principle chapter on natal signs, not a survey paragraph inside a planet book | Jacket; webinar page; thin “the signs” sidebar |
| Authorized archive / author-site excerpt | Direct-read author text of a dedicated signs chapter | SEO, aggregators, reviews, pirate dumps, model memory |

A readable planet-in-sign chapter does **not** cover Layer 2. A readable four-element essay covers Layer 2 only if it treats elements as **sign systems**, not as planetary temperament recycled.

**Stopped before step 7.** Literature map, selection criteria, shortlist, and ingest wait. Next agent builds the map **from the school × constituent table above**, not from Arroyo/Rudhyar pending IDs and not from the first open modern cookbook. No 12 sign objects. No schema change. No CORE. No planet coverage hunt.

---

## 7. Масштаб

Фундамент конечен:

12 signs · 12 houses · 12 Layer-1 objects · 5 major aspects · углы уже в Layer 1 · dignity/rulership — Foundation §2.5 (не дублировать в IL).

Дальше комбинации **композиционно**. Вручную curated в IL-1 — **candidates**, где сложение атомов *может* врать; IL-2 подтверждает или разжалует.

Не начинать с 10 000 комбинаций. Не менять методологию до конца IL-1. Порядок = **Sequence (LOCKED)** выше.

| ID | Работа | Выход |
|----|--------|--------|
| **IL-0** | Foundation: корпус, evidence, provenance, declared gates | ✅ 2026-08-17 |
| **IL-1** | ~100 surface-neutral objects из корпуса + review | in progress (24 drafts: planets 7 · houses 12 · aspects 5; signs withheld; Uranus, Neptune and Pluto claims without objects) |
| **IL-2** | Composition rules (не полный каталог пар) | after IL-1; may demote Layer 5 candidates to composed |
| **IL-3** | Interpretation Engine (sky → themes) | after IL-2 |
| **IL-4** | Expression (LLM / voice per surface) | after IL-3 |

Масштаб библиотеки — после IL-4. Если на IL-1 модель не выдерживает источники — чинить ontology, не плодить объекты и не трогать Today-прозу.

---

## 8. IL-1 gold set — первые ~100 (surface-neutral)

Не «контент Today». Слои 1–4 целиком, затем Layer 5 **candidates** (~50–60), которые *могут* оказаться non-compositional. Остальное — IL-2 rules. Не объявлять список окончательными исключениями до composition rules.

### Атомы (41)

- Objects (12): sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto, asc, mc
- Signs (12): aries…pisces
- Houses (12): 01…12
- Aspects (5): conjunction, opposition, square, trine, sextile

### Layer 5 candidates (~50–60)

Не полный декартов продукт. Рабочий критерий отбора в IL-1: объект годен Profile / Today / Compatibility, конструкция есть в output calculation layer (Swiss + Astro), и *подозрение*, что сложение атомов врёт. Это **не** доказанный `non_compositional` до IL-2.

**transit_to_natal:** Saturn□natal Venus, Saturn□Moon, Saturn□Sun, Saturn□Mars, Saturn☍Venus, Saturn☍Moon, Saturn☌Sun, Saturn☌Moon, Jupiter△Sun, Jupiter□Saturn, Uranus□Moon, Uranus☍Venus, Neptune□Venus, Pluto□Sun, Pluto□Venus.

**transit_through_house:** Saturn→7, Saturn→10, Jupiter→10, Uranus→7, Pluto→1.

**natal_aspect:** Moon□Saturn, Moon☍Saturn, Moon☌Saturn, Venus□Saturn, Venus☍Saturn, Mars□Saturn, Sun□Saturn, Moon□Pluto, Venus□Pluto, Mars□Pluto, Sun☌Saturn, Venus☌Mars, Mercury□Neptune, Mars□Uranus.

**planet_in_sign:** Moon Scorpio, Moon Capricorn, Saturn Aries, Saturn Cancer, Venus Capricorn, Venus Aries, Mars Cancer, Mars Libra, Sun Pisces, Mercury Pisces.

**planet_in_house:** Saturn 7/10/4, Moon 7/10/12, Venus 7/2, Mars 1/10, Sun 10.

Итого порядка **90–100** объектов. Gate IL-1: corpus → claims → normalized object → human review. Настоящие дыры ontology вскроются здесь — не в теории.

---

## 9. Связь с уже принятым каноном

| Канон | Что остаётся | Что меняет IL |
|-------|--------------|----------------|
| TODAY_CONTENT_PIPELINE | I0, Global/Personal authority, LLM формулирует | Step 2 lookup = этот файл; IL не Meaning SoT дня |
| Foundation §2 | identity, орбисы, dignity L1–L3 | семантика глубже keywords; **комбинации не синтезирует LLM** |
| AMC | 39 machine vectors | Content Contract = IL, не legacy psychology one-liners |
| ACM | атомы в machine/; compose runtime | Layer 5 curated **interpretation** files allowed |
| DAY_SOURCES | факт (эфемериды) | «значение в системе» = IL |
| EXPLAINABLE_INTERPRETATION | pack → LLM | pack наполняется из IL, не из свободного промпта |
| Daily Interpretation Engine | DailyState / recommendations | IL — вход смысла, не второй день-SoT |

---

## 10. Changelog

- **1.3.60 (2026-08-18)** — IL-1 process (no ingest, no CORE, no schema change, no sign objects): Layer 2 Signs parent steps 5–6. School lines = existing `source_class` enum mapped onto classification vs later-interpretive bands. No new enum. Vedic/sidereal is identity, not a school. Arroyo/Rudhyar pending IDs on sign files are leftovers, not a shortlist. Source types defined as classes of text. Literature map still waits. Planet fill remains research-stable. `object.function` unchanged. Nothing `active`.
- **1.3.59 (2026-08-18)** — IL-1 process (no ingest, no CORE, no schema change, no sign objects): Sun→Pluto planet fill declared **research-stable**, not semantically finalized. Structural psych gap closed (COVERED 7 · THIN 2 · ACCESS_BLOCKED 1 Mars · EMPTY 0 · DISCOVERED 0). IL-1 must not generate planet research tasks to raise coverage. Planet work is opportunistic/access-driven: named locus opens → extract; otherwise do not hunt a fourth analog. Mars: three dedicated loci already exist; a fourth book is lower marginal value than the next IL layer. CORE scoring stays blocked (five Saturn candidates listed only). Layer 2 Signs definition pass started (parent steps 1–4) **before** schools/bibliography/ingest. Fill-rule “wait for Arroyo/Rudhyar” withdrawn as author-lock. Classification vs later-interpretive constituents split documented; schema required psych slots not demoted this pass. `object.function` unchanged. Nothing `active`.
- **1.3.58 (2026-08-18)** — IL-1 live Sun→Pluto recount (no ingest, no CORE, no object changes): recompute from ledgers after 1.3.57. Retire 1.3.44 dashboard. KPI order no longer leads with CORE=0. Psych slots: COVERED 7 · THIN 2 (Moon, Mercury) · DISCOVERED 0 · ACCESS_BLOCKED 1 (Mars) · EMPTY 0. Pluto is COVERED (Greene/Campion). Mars is ACCESS_BLOCKED, not a semantic gap. Queue = access wait/extract, not “next = Pluto psychological.” `object.function` unchanged. Nothing `active`. CORE still unscored.
- **1.3.57 (2026-08-18)** — IL-1 methodology (no ingest, no CORE, no new bibliography): `ACCESS_BLOCKED(semantic slot)` added. Empty slot with ≥3 quality independent dedicated loci, all access-closed → stop discovery for that slot. `NEED_OWNER` stays a locus status. Psychological Mars = `ACCESS_BLOCKED` (Inner Planets p.138; Dynamics Part 1; Huber *The Planets* p.59). 0 readable chapter bodies. 0 claims. No surrogate. No fourth-book hunt. When one of those three chapters is readable: extraction only. §6.10 empty-slot + densify budget closed (densify already complete 1.3.50–1.3.53). Recount now allowed. `object.function` unchanged. Jupiter psych paused. Nothing `active`. CORE still unscored.
- **1.3.56 (2026-08-18)** — IL-1 discovery (no ingest, no CORE): independent Mars psychological field after 1.3.55 Dynamics skip. New dedicated chapter identified: Huber *The Planets and Their Psychological Meaning* (HopeWell 2006 ISBN 9780954768027) ch. *Mars: The Masculine* p.59, from official API TOC. Chapter body unread. Cataloged as `src.psychological.huber_planets`, pending on Mars. Parked `psychological` (no Huber enum). Do not ingest tool-planet/masculine from TOC, garden lecture, or Llewellyn review. Not a substitute for Inner Planets p.138 or Dynamics Part 1. Independent field: Hamaker planets-as-drives still unread (ebin unused); *Development of the Personality* is childhood stages; Clark vocation PDF is one-sentence Mars. Psychological Mars still empty. `object.function` unchanged. Jupiter psych paused. Nothing `active`. CORE still unscored.
- **1.3.55 (2026-08-18)** — IL-1 discovery (no ingest, no CORE): independent Mars psychological field after 1.3.54 skip of p.138. New dedicated locus identified: Sasportas *Dynamics of the Unconscious* Part 1 *The Astrology and Psychology of Aggression* (Weiser 1988 ISBN 0877286744). Body unread (Google Books `M9IEuEmeS0YC` empty viewport; Archive `dynamicsofuncons0000gree` printdisabled). Cataloged as `src.psychological.sasportas_dynamics_unconscious`, pending on Mars. Pirate dumps unused. Forum/AbeBooks quotes of p.18 not ingested. Not a substitute for Inner Planets p.138. Independent field: Arroyo *Four Elements* still front-matter; George *Ancient Practice* is Hellenistic technique, not this psych slot; Lynn Bell official site still Mars Quartet jacket. Psychological Mars still empty. `object.function` unchanged. Jupiter psych paused. Nothing `active`. CORE still unscored.
- **1.3.54 (2026-08-18)** — IL-1 discovery (no ingest, no CORE): Mars psychological field re-check after Saturn densify. Inner Planets p.138 still NEED_OWNER (Google Books empty; Archive printdisabled; pirate dumps unused; no Greene summary; third-party quotes of p.185/p.188 not ingested). Same-author densification skipped (CPA Mars webinars 2024 page re-checked, still description not transcript; astro.com Mythic Mars extract not a substitute). Independent field: Mars Quartet still jacket; Martin Lesson 3 unread; Sullivan official site still has no Mars principle excerpt; Clark *Aphrodite and Ares* is Venus-Mars pair myth; Costello *Desire and the Stars* is general desire/divination; McAdam life-coach and OPA consulting-room are natal/cycle essays; Hand transits Mars is professional densification; Tarnas intro Mars still a thin survey. Psychological Mars still empty. `object.function` unchanged. Do not loop a fourth Mars hunt without a new readable locus. Jupiter psych paused. Nothing `active`. CORE still unscored.
- **1.3.53 (2026-08-18)** — IL-1 ingest (no CORE): Saturn psychological densification field re-check after Mercury skip. Greene Introduction already ingested — not re-ingested. Remaining *Saturn: A New Look* chapters unread same-author densification. CPA Saturn webinars 2015 page re-checked, not transcript. Same-author densification skipped (astro.com Mythic Saturn extract `advent2319spz` opened-not-ingested). Independent field: Relating p.39 unread; Martin Lesson 4 unread; Reinhart *Saturn, Chiron and the Centaurs* jacket; Sullivan *Saturn in Transit* jacket/cycle; Grasse astro.com is karmic-in-sign; Harvey Apollon Saturn-Uranus is a pair. Best accessible dedicated principle text after field check: Tarnas official-site *Introduction to Archetypal Astrology* (Saturn/senex section) as `psychological` `school_specific` (limit-necessity / senex / Chronos-fixing-the-chart / gravitas / birth-labor / skeleton / inner-judge / inner-authority / threshold-guardian — author's categories, not Greene psychic-process, Hand resistance/structure, Houlding personal-boundary, or Rudhyar I-am-I / Ring-Pass-Not). Same PDF as Uranus/Neptune after field check, not auto-picked. Superficial structure/limit overlap with Hand is not equivalence. Karma/Yahweh dump excluded. `object.function` and `themes` unchanged (no `structure`). Next: remaining empty psych slot is Mars. Densify Sun/Moon/Mercury/Saturn complete. Nothing `active`. CORE still unscored.
- **1.3.52 (2026-08-18)** — IL-1 discovery (no ingest, no CORE): Mercury psychological densification field re-check after Moon skip. Inner Planets Hermes already ingested — not re-ingested. Remaining Inner Planets Mercury chapters (Sasportas Tricksters / Interpreting Mercury) unread same-author densification. Hand Ch.4 Mercury still NEED_OWNER. Same-author densification skipped (astro.com Mythic Mercury extract `advent235ikc` opened-not-ingested). Independent field: Martin Mercury unread; Gerhardt / Lockley astro.com are natal/ego essays; Meyer Four Faces and Clark Timelines are cycle densification; Clark *Crossing the Threshold* opened-not-ingested (mythic katabasis/psychopomp, not natal Mercury); Costello MISPA is third-party notes; CPA Planets of Twilight page-only; Reinhart Forensic Mercury is Rx-in-Scorpio cycle; Sullivan official site has no Mercury principle excerpt; Tarnas intro Mercury is a thin survey paragraph — not this locus. Psychological Mercury still only Inner Planets Hermes. `object.function` unchanged. Next: densify Saturn psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.51 (2026-08-18)** — IL-1 discovery (no ingest, no CORE): Moon psychological densification field re-check after Sun fill. Costello *The Astrological Moon* still NEED_OWNER (CPA/author jacket+Harvey review; official-site reprint blurb not chapter body; pirate dumps unused; no Costello summary). Same-author densification skipped (Luminaries Moon preview not re-ingested; astro.com Mythic Moon extract `advent237yqs` opened-not-ingested). Independent field: Martin Lesson 2 unread; Sullivan *Dynasty* Sun/Moon is family-systems; Gerhardt astro.com Moon is natal/mothering essay; Reinhart Moon Talk I–II opened-not-ingested (cycle attunement/meditation, not natal principle); Brian Clark Apollon Issue 4 / astro.com progressed lunation are cycle densification. Tarnas intro Moon is a thin survey paragraph — not this locus. Hand transits Moon intro is professional densification. Psychological Moon still only Luminaries preview. `object.function` unchanged. Next: densify Mercury psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.50 (2026-08-17)** — IL-1 ingest (no CORE): Sun psychological densification. Apollo's Chariot NEED_OWNER remains (jacket only; pirate dumps unused; no Greene summary). Hand Ch.4 Sun still NEED_OWNER. Same-author densification skipped (Mythic Advent Sun snippet; Luminaries not re-ingested). Independent field: Martin Lesson 2 unread; Sullivan *Dynasty* Sun/Moon is family-systems, not this principle locus; Tarnas intro Sun not this locus (do not auto-pick that PDF a third time); Wounding-and-will-to-live is a Chiron article. Best accessible dedicated principle text after field check: Greene *The Sun-god and the Astrological Sun* (CPA Apollon Issue 1 official PDF / authorized astro.com `in_sungod`) as `psychological` `school_specific` (carrier-not-physical-Sun / inner-light Know-thyself / core-identity-destiny / family-curse-breaker / cosmocrator-reconciler / vocation-as-inner-call / inner-healer will-to-live / unexpressed-Sun / aloneness-price — author's categories, not Luminaries solar-consciousness, Rudhyar light-as-integration, or Watters essential-self). Cataloged opened-not-ingested in 1.3.35; extracted now. Not a substitute for Apollo's Chariot. House/aspect natal recipes and heart/body dump excluded. `object.function` unchanged. Next: densify Moon psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.49 (2026-08-17)** — IL-1 discovery (no ingest, no CORE): Mars psychological field re-check after Venus fill. Inner Planets p.138 still NEED_OWNER (Google Books viewport empty; Archive printdisabled; pirate dumps unused; no Greene summary; third-party quotes of p.185/p.188 not ingested). Same-author densification skipped (CPA Mars webinars 2024 page re-checked, still description not transcript; astro.com Mythic Astrology Mars extract re-opened-not-ingested). Independent field: Mars Quartet still jacket; Martin Lesson 3 unread; Sullivan official site has no Mars principle excerpt; Costello events/listings only; Reinhart articles are not Mars-alone. Tarnas intro Mars is a thin survey paragraph — not this locus (do not auto-pick the same PDF a third time). Gerhardt astro.com Mars is natal/cultural essay. Hand transits Mars intro is professional densification. Psychological Mars still empty. `object.function` unchanged. Next: densify Sun psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.48 (2026-08-17)** — IL-1 ingest (no CORE): Venus psychological. Inner Planets p.69 NEED_OWNER remains (pirate dumps unused; no Greene summary). Relating unread. Mythic Venus still not ingested (same-author densification). CPA *Venus and Jupiter* page/reviews still not claims. Dual Goddess seminar body still unread. Martin Lesson 3 unread. Tarnas intro Venus is a thin survey sentence — not this locus (do not auto-pick the same PDF a third time). Gerhardt Venus questionnaire not this principle locus. Best accessible independent principle text after field check: Erin Sullivan official-site excerpt of *Venus and Jupiter* (Apollon 1999 / erinsullivan.com *Eros and Aphrodite: Love and Creation*) as `psychological` `school_specific` (channel-for-Eros / Urania-Pandemos dual goddess / bridge-ideal-real / same-impulse-for-relating-and-creating / Saturn-as-midwife / unchanneled-Eros / creativity-as-discovery / not-only-fine-arts / pre-creative-chaos — author's categories, not Hand bonding, Watters love/desire, or Rudhyar inward-way). Moon-Neptune raw-Eros and natal examples not this locus. Womb/medical dump excluded. `object.function` unchanged. Next: Mars psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.47 (2026-08-17)** — IL-1 ingest (no CORE): Neptune psychological. *The Astrological Neptune* NEED_OWNER remains (Google Books still title/TOC). Outer Planets NEED_OWNER remains. CPA Neptune page re-checked, not transcript. Mythic Neptune extract re-opened-not-ingested. Sullivan *The Elusive Neptune* opened-not-ingested (Pisces-transit/discovery/liminality, not this principle locus). Reinhart Saturn-Neptune and Uranus-Neptune essays are pair/transit. Sasportas/Martin still closed. Best accessible independent principle text after field check: Tarnas official-site *Introduction to Archetypal Astrology* (Neptune section) as `psychological` `school_specific` (transcendent-ideal / ocean-of-consciousness / thirst-for-transcendence / Nirvana-and-Maya / Narcissus / longing — author's categories, not Hand dissolution-of-distinction or Rudhyar ecstasy/prenatal). Same PDF as Uranus 1.3.46 after field check, not auto-picked. Tarnas Maya is Neptune-alone, not Hand Neptune+Saturn. Perinatal/medical/intuition dump excluded. Object still withheld. Next: Venus psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.46 (2026-08-17)** — IL-1 ingest (no CORE): Uranus psychological. Outer Planets NEED_OWNER remains; Art of Stealing Fire still unread (not a substitute); CPA Uranus page re-checked, not transcript; Mythic Uranus extract re-opened-not-ingested; Sullivan Midlife extract opened-not-ingested (Saturn-Uranus/midlife, not this principle locus); Reinhart pair/transit essays not this locus; Sasportas/Martin still closed. Best accessible independent principle text after field check: Tarnas official-site *Introduction to Archetypal Astrology* (cosmosandpsyche.com PDF, Uranus/Prometheus section) as `psychological` `school_specific` (Prometheus-figure / freedom-rebellion-revolution / breakthroughs / own-path / unintegrated-as-forced-change-from-without — author's categories, not Hand disruption/mutation or Rudhyar transform/through). Not a substitute for unread *Prometheus the Awakener*. 1781/tech/perinatal dump excluded. Object still withheld. Next: Neptune psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.45 (2026-08-17)** — IL-1 remaining planet budget locked to empty psychological slots (Pluto → Uranus → Neptune → Venus → Mars; then densify Sun/Moon/Mercury/Saturn; Jupiter psych paused). CORE=0 is not a KPI; CORE rule unchanged. Humanistic ≠ psychological. Do not hunt Hand-lemma confirmation. Recount deferred until those five psych slots are non-empty. Pluto psychological ingest (no CORE, object withheld): Greene/Campion *Living with Pluto* interview Parts 1–2 (astro.com authorized author speech) as `psychological` `school_specific` (life-force-in-substance / image-family / grind-or-victim / survival-instinct-when-overwhelmed — author's categories, not Hand reconstruction or Rudhyar celestial-seed). Outer Planets NEED_OWNER remains; this is not that volume. Field opened: Reinhart 1991 official essay opened-not-ingested (Scorpio-transit/collective); Cunningham/Hamaker unread; Sasportas/Martin still closed; Mythic Pluto extract opened-not-ingested; CPA page still not transcript. Evolutionary Green/Forrest not this psych fill. Next: Uranus psychological, one locus. Nothing `active`. CORE still unscored.
- **1.3.44 (2026-08-17)** — IL-1 discovery (no ingest, no CORE): Neptune psychological. *The Astrological Neptune* still NEED_OWNER (Google Books title+TOC only; pirate dumps unused; no Greene summary; espirited.com / forum / Goodreads intro quotes not ingested). Same-author densification skipped (CPA Neptune webinars 2018 page re-checked, still description not transcript — 1.3.33 rule holds; astro.com Mythic Astrology Neptune extract opened-not-ingested). Independent field: Sasportas *Gods of Change* still jacket; Martin Lesson 5 unread; Outer Planets still NEED_OWNER. Steven Forrest *Book of Neptune* is evolutionary/jacket, not this psych fill. Psychological Neptune still empty. Object still withheld. Next: Pluto psychological, same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.43 (2026-08-17)** — IL-1 discovery (no ingest, no CORE): Uranus psychological. Outer Planets volume still NEED_OWNER; pirate dumps unused; no Greene summary. Art of Stealing Fire is not a substitute. Same-author densification skipped (CPA Uranus webinars 2019 page re-checked, still description not transcript — 1.3.32 rule holds; astro.com Mythic Astrology Uranus extract opened-not-ingested). Independent field: Sasportas *Gods of Change* still jacket/printdisabled; Martin Lesson 5 unread; Tarnas *Prometheus the Awakener* cataloged unread (1987 client-brief intro not ingested as a substitute for that monograph). Psychological Uranus still empty. Object still withheld. Next: Neptune psychological, same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.42 (2026-08-17)** — IL-1 discovery (no ingest, no CORE): Mars psychological. Inner Planets p.138 still NEED_OWNER; pirate dumps unused; no Greene summary; third-party quotes of p.185/p.188 not ingested. Same-author densification skipped (CPA Mars webinars 2024 page re-checked, still description not transcript — 1.3.31 rule holds; astro.com Mythic Astrology Mars extract opened-not-ingested). Independent field: Mars Quartet still jacket only; Martin Lesson 3 unread; Dana Gerhardt astro.com Mars is not Greene; Hand transits Mars intro is professional densification. Psychological Mars still empty. `object.function` unchanged. Next: Uranus psychological, same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.41 (2026-08-17)** — IL-1 discovery (no ingest, no CORE): Venus psychological. Inner Planets p.69 still NEED_OWNER; pirate dumps unused; no Greene summary. Same-author densification skipped (Relating unread; astro.com Mythic Astrology Venus extract opened-not-ingested). No CPA Greene Venus webinar. Independent field: Martin Lesson 3 unread; Arroyo Venus-in-element unread; Costello NORWAC listing only. Best accessible independent candidate after field check: Erin Sullivan *Venus and Jupiter* — CPA page + reviews only, chapter body unread; cataloged, not ingested from jacket/reviews. Psychological Venus still empty. `object.function` unchanged. Next: Mars psychological, same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.40 (2026-08-17)** — IL-1 ingest (no CORE): Jupiter humanistic discovery. Psychological pool already filled (CPA page + *By Jove!* extract) — not re-ingested; Relating p.39 unread; Martin Lesson 4 unread. Humanistic field: Ruperti *Cycles of Becoming* Ch.V TOC only (unread, cataloged); other Rudhyar Jupiter articles are pair/cycle densification. Missing school class was humanistic. Best accessible primary after field check: Rudhyar *New Mansions* Jupiter (Khaldea) as humanistic `school_specific` (organizer-of-functions / purpose-form-function / Hierarch / religion-as-binding-back / expansion-only-if-Saturn-balanced / Soul-compensator / Greater-Fortune-overreach — author's categories, not Watters enlargement, Hand expansion, CPA contingent-benefic, or Greene gluttony/teleology). `object.function` unchanged. Food/overeating dump not copied into object slots. Next: Venus psychological, same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.39 (2026-08-17)** — IL-1 ingest (no CORE): Saturn psych/humanistic discovery. Psychological pool: Greene Introduction already ingested (not re-ingested); remaining *Saturn: A New Look* chapters unread same-author densification; CPA Saturn webinars 2015 page-only (not ingested from the page); Relating p.39 unread; Martin Lesson 4 unread. Missing school class was humanistic. Best accessible primary after field check: Rudhyar *New Mansions* Saturn (Khaldea) as humanistic `school_specific` (I-am-I / Ring-Pass-Not / systolic-contraction / Golden-Age instinct / fate-tester — author's categories, not Houlding personal-boundary, Greene psychic-process, or Hand resistance/structure). `object.function` and `themes` unchanged. Spine/kundalini dump not copied into object slots. Next: Jupiter humanistic (`nmnm_jupiter.php` located 1.3.38, not this pass), same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.38 (2026-08-17)** — IL-1 ingest (no CORE): Jupiter psych/humanistic discovery. Psychological pool checked first: CPA Jupiter page already ingested (not re-ingested); Relating p.39 unread (pirate dumps unused); CPA transcript / full *By Jove!* book unread; Martin Lesson 4 unread; Wessex/ANS reviews unused. Best accessible primary after field check: authorized astro.com extract of Greene *By Jove!* “Psychology of Jupiter” (`in_lgbyjove2_e.htm`) as psychological `school_specific` (gluttony-as-unconscious-quest / individuation-teleology / leap-toward-pattern / not-controllable — author's categories, not CPA contingent-benefic, Watters enlargement, or Hand expansion). Mick Jagger extract opened-not-ingested (natal densification / Layer 5). Humanistic still empty; Rudhyar NMNM Jupiter located (`nmnm_jupiter.php`) — not this locus, not auto-picked. `object.function` unchanged. Food/addiction dump not copied into object slots. Next: Saturn, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.37 (2026-08-17)** — IL-1 ingest (no CORE): Mercury psych/humanistic discovery. Psychological pool: Inner Planets Hermes-spontaneity already ingested (not re-ingested); remaining Inner Planets Mercury chapters unread same-author densification; no CPA Mercury webinar; Martin unread. Missing school class was humanistic. Best accessible primary after field check: Rudhyar *New Mansions* Mercury (Khaldea) as humanistic `school_specific` (weaver-of-relationship / inner-grown-pattern / operative-Wholeness / servant-of-Jupiter — author's categories, not Watters mind, Greene young-Hermes, or Ptolemy convertibility). `object.function` unchanged. Nervous-system/nadi dump not copied into object slots. Next: Jupiter, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.36 (2026-08-17)** — IL-1 ingest (no CORE): Moon psych/humanistic discovery. Psychological pool: Luminaries Moon preview already ingested (not re-ingested); no CPA Moon webinar; Darby Costello *The Astrological Moon* jacket+review NEED_OWNER (pirate dumps unused); Martin Lesson 2 unread. Missing school class was humanistic. Best accessible primary after field check: Rudhyar *New Mansions* The Song of Life (Khaldea) as humanistic `school_specific` (song-of-life / resurrected-past / not-dead-weight / raw-unindividuated-response / gestation-individuation — author's categories, not Watters night-world, Greene embodiment, or Ptolemy moisture). `object.function` unchanged. Alchemical-womb not copied into object.domains. Next: Mercury, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.35 (2026-08-17)** — IL-1 ingest (no CORE): Sun psych/humanistic discovery. Psychological pool: Luminaries Sun preview already ingested (not re-ingested); Apollo's Chariot CPA 2001 jacket only NEED_OWNER; CPA *Apollon* Issue 1 PDF opened (Greene Apollo article) but same-author densification after Luminaries — not this locus; Martin Lesson 2 unread; no CPA Sun webinar. Missing school class was humanistic. Best accessible primary after field check: Rudhyar *New Mansions* The Song of Light (Khaldea) as humanistic `school_specific` (Heart-vs-photosphere / light-as-integration / light-vs-life / will-as-directed-energy / our-Sun-as-Source — author's categories, not Watters essential-self, Greene solar-consciousness, or Ptolemy heat). `object.function` unchanged. Endocrine/nerve dump and 28-year cycles not copied into object slots. Next: Moon, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.34 (2026-08-17)** — IL-1 ingest (no CORE): Pluto psych/humanistic discovery. Psychological pool (Greene Outer Planets NEED_OWNER; CPA Pluto webinars page-only; Sasportas *Gods of Change* unread; Martin Lesson 5 unread; no dedicated Greene Pluto book) not ingested. Best accessible primary after field check: Rudhyar *New Mansions* Pluto (Khaldea) as humanistic `school_specific` (celestial-seed / hierophant-of-birth / God-in-the-lowest / penetration-of-depths — author's categories, not Hand reconstruction/decomposition). Object still withheld. Psychological Pluto still empty. Next: Sun, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.33 (2026-08-17)** — IL-1 ingest (no CORE): Neptune psych/humanistic discovery. Psychological pool (Greene Outer Planets NEED_OWNER; Greene *The Astrological Neptune* Archive printdisabled / Google Books cover; CPA Neptune webinars page-only; Sasportas *Gods of Change* unread; Martin Lesson 5 unread) not ingested. Best accessible primary after field check: Rudhyar *New Mansions* Neptune (Khaldea) as humanistic `school_specific` (ecstasy-realm / end-of-journey / prenatal-Great-Mother / compassion-atonement — author's categories, not Hand ultimate-reality/dissolution). Object still withheld. Psychological Neptune still empty. Next: Pluto, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.32 (2026-08-17)** — IL-1 ingest (no CORE): Uranus psych/humanistic discovery. Psychological pool (Greene Outer Planets NEED_OWNER; Sasportas *Gods of Change* jacket; Martin Lesson 5 unread; CPA Greene Uranus webinars page-only) not ingested. Best accessible primary after field check: Rudhyar *New Mansions* Uranus (Khaldea) as humanistic `school_specific` (transform / through / reconstruct-form / not-regeneration — author's categories, not Hand disruption/mutation). Object still withheld. Psychological Uranus still empty. Next: Neptune, same discovery rule, one locus; do not auto-pick Rudhyar. Nothing `active`. CORE still unscored.
- **1.3.31 (2026-08-17)** — IL-1 ingest (no CORE): Mars psych/humanistic discovery. Psychological pool (Greene p.138, Sasportas p.184, Martin Lesson 3, Bell *Mars Quartet*, CPA Greene Mars webinars) closed or jacket-only — not ingested. Best accessible primary: Rudhyar *New Mansions* Mars (Khaldea) as humanistic `school_specific` (first-gesture / surplus-energy release / desire-as-life-movement — author's categories, not Watters assertive-drive, Hand survival, or Greene warrior). `object.function` unchanged. Psychological Mars still empty. Next: Uranus, same discovery rule, one locus. Nothing `active`. CORE still unscored.
- **1.3.30 (2026-08-17)** — Parent research order for semantic cores (methodology, not ingest, not CORE): `docs/KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md`. Sequence: subject → bounds → constituents → definitions → schools → source types → literature map → selection criteria → shortlist → ingest/compare. IL-1 planet fill continues §6.9. Do not build the next core (or score CORE) from the first readable author. Psychology/medicine: evidence hierarchy is separate from school-convergence. Claims/`function` unchanged. Nothing `active`. CORE still unscored.
- **1.3.29 (2026-08-17)** — IL-1 source discovery reopen (methodology correction, not CORE): `NEED_OWNER(author/locus)` ≠ `NEED_EVIDENCE(semantic slot)`. Discovery = school → coverage → best accessible primary. Lift “no new books/authors.” Add `source_class=humanistic`. Rudhyar *New Mansions for New Men* Venus (Khaldea archival primary) ingested as humanistic `school_specific` (inward way / quintessence — author's categories, not Watters love/desire, Hand bonding, or Greene harlot). Clare Martin *Mapping the Psyche* Vol.1 cataloged as psychological-pool candidate; chapter body unread. Greene p.69 / Hand Ch.4 Sun–Mercury remain NEED_OWNER. No `function` rewrite. No CORE. Next: Mars (same discovery rule, one locus). Nothing `active`. CORE still unscored.
- **1.3.28 (2026-08-17)** — IL-1 Phase 1 research boundary + corpus QA (no methodology change, no new sources, no CORE): remaining queue is physical NEED_OWNER (Inner Planets Venus p.69 / Mars p.138; Outer Planets volume; Hand Ch.4 Sun/Moon/Mercury). CORE scoring blocked; CORE-candidate audit premature. Existing claims and `object.function` unchanged. QA of 303 planet rows recorded in `docs/astrology/IL1_CORPUS_QA.md` (atomization, false equivalence, fact/symbolic/medical/runtime hygiene). Do not pad bibliography. Next ingest = owner direct-read in locked order. Nothing `active`. CORE still unscored.
- **1.3.27 (2026-08-17)** — IL-1 ingest discipline (no methodology change, no CORE pass, no new bibliography): Hand Ch.4 Sun probed as next extractable declared locus. This host: Google Books `ZPhRV8aFQqcC` still jacket/match-index only; Open Library unavailable; pirate dumps unused. No Sun claims added. Do not backfill from model memory or toward Watters/Greene Sun lemmas. NEED_OWNER: ISBN 9780914918165, Ch.4 The Sun — same owner direct_read path as Venus–Pluto. Moon/Mercury Ch.4 share this unread window; do not start CORE-candidate audit on an incomplete Hand coverage. Nothing `active`. CORE still unscored.
- **1.3.26 (2026-08-17)** — IL-1 ingest discipline (no methodology change, no CORE pass, no new bibliography, no surrogate fill): NEED_OWNER blocks a **locus**, not the research pipeline. Venus p.69 stays first unclosed gap; do not bypass with secondary sources. Mars Inner Planets p.138 probed in the same legal corpus (Google Books viewport empty) and left pending — not ranked ahead of Venus. Greene *Outer Planets* Uranus probed: CPA 2005 Google Books has no preview; Archive CRCS `printdisabled`; jacket/TOC/reviews not ingested; *The Art of Stealing Fire* not used. Outer Planets Uranus/Neptune/Pluto = one physical-access NEED_OWNER for the volume. Next extractable declared locus while those Greene volumes stay closed: Hand Ch.4 Sun. Nothing `active`. CORE still unscored.
- **1.3.25 (2026-08-17)** — IL-1 ingest discipline (no methodology change, no CORE pass, no new bibliography): owner fetch order locked — Greene Inner Planets Venus p.69 → Mars p.138 → Outer Planets Uranus → Neptune → Pluto → Hand Ch.4 Sun → Moon → Mercury → new gap audit + first CORE-candidate audit without automatic promotion. Greene Outers before Hand luminaries/Mercury because outers are Hand monopoly. Independent extraction locked: extract Greene from the opened locus without aiming to confirm Hand lemmas; compare only after extraction. Venus p.69 still unread (Google Books viewport empty; Archive printdisabled; no Weiser Calaméo for Part Two). NEED_OWNER: Weiser 1993 ISBN 0-87728-741-4, Greene “The Great Harlot” p.69–. No pirate-dump ingest. Nothing `active`. CORE still unscored.
- **1.3.24 (2026-08-17)** — IL-1 research audit (no methodology change): Sun→Pluto corpus gap audit recorded in `docs/astrology/IL1_SUN_PLUTO_GAP_AUDIT.md`. 303 planet claims; 0 `core`. Closest two-class overlap = Saturn cold/dry/malefic (classical+traditional), still not CORE. Hand Sun/Moon/Mercury unextracted. Venus p.69 / Mars p.138 unread. Outers Hand-only. No `function` rewrite. Nothing `active`. Next locus must be named from the ranked already-open list, not a new book.
- **1.3.23 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Pluto only (15 atomic `professional` / `school_specific` claims). Calc already emits `astrology.planet.pluto`. Object **not** materialized. Completes Hand outer sequence (Uranus disruption → Neptune dissolution → Pluto reconstruction); not generic transformation. Death/rebirth symbolic, not mortality prediction. Psychotic-crisis/medication example excluded. Hand 1981 dated, not later Hand, not CORE. Catalog stays 24. ASC/MC still closed. Next = Sun→Pluto corpus gap audit, not another book. Nothing `active`.
- **1.3.22 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Neptune only (17 atomic `professional` / `school_specific` claims). Calc already emits `astrology.planet.neptune`. Object **not** materialized. Dissolution of distinction ≠ dreams/intuition/spirituality. Maya = Neptune+Saturn; artistic creativity = Neptune+Venus (combination claims, not Neptune-alone; no Layer 5 objects). Ideals ≠ illusion of perfection; martyr ≠ victim. Hand 1981 dated, not later Hand, not CORE. Catalog stays 24. Pluto still closed. Nothing `active`.
- **1.3.21 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Uranus only (12 atomic `professional` / `school_specific` claims; pp.72–75). Calc already emits `astrology.planet.uranus`. Object **not** materialized: celestial_object required slots would force Hand 1981 into `function`/`domains` or invent natal copy. Disruption ≠ generic change; mutation ≠ rebellion; Jupiter expansion ≠ Uranus alien-frame expansion. Collective/science/altered-consciousness ledger-only. Hand 1981 dated, not later Hand, not CORE. Catalog stays 24. Neptune/Pluto still closed. Nothing `active`.
- **1.3.20 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Saturn only (16 atomic `professional` / `school_specific` claims). Resistance ≠ punishment; consensus reality ≠ truth; consequences ≠ karma; responsibility ≠ guilt. Object `function` and `themes` unchanged (no Saturn=structure CORE). Companion to Jupiter–Saturn polarity. Next is Hand vs Classical/Watters/Psychological audit, not outers. Nothing `active`. CORE still unscored.
- **1.3.19 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Jupiter only (16 atomic `professional` / `school_specific` claims). Expansion ≠ integration ≠ incorporation. Healing/medicine ledger-only. Watters Mercury breadth-over-depth vs Hand Jupiter overview logged as future reconciliation; Mercury not rewritten. Object `function` unchanged. Saturn Hand not ingested. Nothing `active`. CORE still unscored.
- **1.3.18 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Mars only (13 atomic `professional` / `school_specific` claims). Not merged with Watters assertive-drive. Body/inflammation/iron-steel ledger-only, not `object.domains`. Psychological Mars still Inner Planets p.138 unread. Object `function` unchanged. Jupiter/Saturn Hand not ingested. Nothing `active`. CORE still unscored.
- **1.3.17 (2026-08-17)** — IL-1 ingest (no methodology change): Hand *Horoscope Symbols* Ch.4 Venus only (12 atomic `professional` / `school_specific` claims). Not merged with Watters love/desire. Psychological Venus still Inner Planets p.69 unread. `runtime_semantic_candidate` not added to schema. Object `function` unchanged. Sun/Moon/Mercury/Mars/Jupiter/Saturn Hand not ingested. Nothing `active`. CORE still unscored.
- **1.3.16 (2026-08-17)** — IL-1 ingest (no methodology change): Mars Inner Planets p.138 identified_but_unreadable (Greene primary; Sasportas p.184 reserve; no claims). Jupiter psychological: CPA Greene webinar/By Jove! page only — seminar-description claims, not the transcript; Relating p.39 candidate unread. Hand *Horoscope Symbols* Ch.4 named (not *Planets in Transit*); chapter body not opened here; Sun/Moon/Mercury atoms not ingested. No more psychological-book search. Nothing `active`. CORE still unscored.
- **1.3.15 (2026-08-17)** — IL-1 ingest (no methodology change): Venus psychological locus identified as Inner Planets Part Two p.69 (Greene, “The Mythology and Psychology of Venus”). Chapter body not opened; no Venus psych claims added. Relating is no longer the blocker. Astro.com `in_cdp_venus_e.htm` is Carolina de Pedro, not Greene — not ingested. Mars TOC p.138 identified, not extracted. Nothing `active`. CORE still unscored.
- **1.3.14 (2026-08-17)** — IL-1 ingest (no methodology change): refine Watters/Greene rows from the second research dump. Atomic splits (father≠attraction, traits≠health, orbit-fact≠symbolism). `runtime_semantic_candidate` / `do_not_compare_with` / `modern_general_practical` as source_class **not** added to schema. Watters stays `professional`. Greene Inner Planets Mercury (Hermes spontaneity) ingested as psychological `school_specific`. Body/health/fertility still ledger-only. Nothing `active`. CORE still unscored.
- **1.3.13 (2026-08-17)** — IL-1 ingest (no methodology change): Watters 2003 Skyscript planet intros (Sun–Jupiter) as modern general intro parked in `professional` (classification gap; not traditional). Compound lemmas split. Body/medical rows ledger-only. Greene *The Luminaries* Sun/Moon preview as psychological `school_specific`. Hand Ch.4 / Relating Venus / Mercury–Mars–Jupiter psych remain NEED_OWNER. Object `function` not rewritten. Nothing `active`. CORE still unscored.
- **1.3.12 (2026-08-17)** — IL-1 ingest (no methodology change): Houlding *Saturn: The Great Teacher* (Skyscript 2003) as living-traditional Saturn locus. Cold/dry/malefic/slow compared; personal-boundary and mature-through-constraint stay `school_specific`. Object `function` not rewritten. External T1–T4 Saturn pilot not imported. Nothing `active`. CORE still unscored.
- **1.3.11 (2026-08-17)** — IL-1 ingest (no methodology change): first `psychological` school_class from opened Greene *Saturn* Introduction (Weiser Classics 2021 p.1–8, publisher Calaméo preview). Psychic-process / pain-toward-self-discovery stay `school_specific`; Saturn `function` not rewritten; structure/limits/maturation not imported. Nothing `active`. CORE still unscored.
- **1.3.10 (2026-08-17)** — IL-1 ingest (no methodology change): first `traditional` school_class from opened Houlding loci (aspects 1995/2004; houses 1/6/7/12 extract). Orbs stay planetary; square not simply bad stays school_specific; house `domain` not rewritten. Nothing `active`. CORE still unscored.
- **1.3.9 (2026-08-17)** — IL-1 ingest (no methodology change): Valens I.1 planets, I.2 Aries, IX XII Places; Lilly CA I.19 orbs/partile. Collisions logged; objects not averaged; nothing `active`; no sign objects.
- **1.3.8 (2026-08-17)** — Activation gates (not methodology): unevidenced `requires_action: false` cannot become `active`; IL-1 Layer 5 gold list = curated candidates, IL-2 may demote to composed. User-facing provenance bands later via Trust Layer. No sequence/ontology change.
- **1.3.7 (2026-08-17)** — Public brand/trust language moved to [Trust Layer](../content/TODAYFLOW_TRUST_LAYER.md) (not an IL methodology change). Swiss/DE431 claim facts in Foundation §1.4.1.
- **1.3.6 (2026-08-17)** — Ptolemy I.17 + Lilly CA I.16 p.91: commanding *grouping* compared; equinox pair-relation stays school_specific. Ptolemy I.18 beholding not collapsed into Lilly Antiscion. Copy-paste Aries gap_note removed from other sign QUALITY files. No Layer 2 objects. No methodology change.
- **1.3.5 (2026-08-17)** — Lilly CA I.1 opened: aspect *geometry* compared with Ptolemy; qualitative labels remain school_specific (good/enmity ≠ harmonious-by-sex). Lilly CA I.16 sign *quality* claims for 12 signs; still no Layer 2 objects. `requires_action` stays false/not-evidenced. No methodology change.
- **1.3.4 (2026-08-17)** — Fill-rules from corpus collisions (no schema change): Layer 2 psych slots wait later loci; element/mode are distinct descriptive systems; houses = Lilly I.7 only; `requires_action: false` = not evidenced. Do not polish existing objects to a modern average.
- **1.3.3 (2026-08-17)** — Houses 1–12 from Lilly CA I.7 (not compared to Ptolemy I.13). Major aspects from Ptolemy I.16/I.27; `requires_action` left false. Sign *objects* withheld: Layer 2 required psych slots unattested; element/mode conflicts logged. No ASC/MC/outers. No methodology change.
- **1.3.2 (2026-08-17)** — IL-1 classical seven drafts (Sun–Saturn) from Ptolemy I.4–I.7 + Lilly CA I.8–I.14. Concrete gaps: Moon/Venus temperature mismatch; Mercury native quality vs convertibility; CORE still blocked. No methodology change.
- **1.3.1 (2026-08-17)** — IL-1 started. First draft `astro.object.saturn` from Ptolemy I.4–I.5 + Lilly CA I.8 (claims ledger → normalized object). CORE not scored. No methodology change.
- **1.3 (2026-08-17)** — Swiss stays in IL runtime stack; only *licensing* is a parallel gate. IL-1 objects must map to calc-layer entities.
- **1.2 (2026-08-17)** — Sequence LOCKED IL-0…IL-4; surface-neutral IL-1; Swiss licensing out of content track; methodology freeze until first ~100 objects.
- **1.1 (2026-08-17)** — research corpus methodology; evidence_tier CORE/SUPPORTED/SCHOOL-SPECIFIC/EDITORIAL; source registry (~35 candidates); ingest = paraphrase not copy; Swiss dual-license gate; forbidden list.
- **1.0 (2026-08-17)** — ontology + schema + freeze Today content until IL-3; gold set listed; no production objects.
