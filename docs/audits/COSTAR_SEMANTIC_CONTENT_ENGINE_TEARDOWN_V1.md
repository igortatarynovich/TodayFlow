# Co–Star Semantic & Content Engine Teardown V1

**Date:** 2026-08-21  
**Status:** LOCKED as empirical research SoT (Phase 0). **Not** Interpretation Library meaning. **Not** ingest. **Not** a clone brief. **Not** an app review.  
**Owner:** Product + Research.  
**IL freeze:** [INTERPRETATION_LIBRARY_V1.md](../astrology/INTERPRETATION_LIBRARY_V1.md) **1.3.75**. Do not change IL architecture until this teardown has an in-app Phase 1 **or** the owner explicitly unlocks IL.  
**Canon selection (frozen, not executing):** [TODAYFLOW_CANON_V1.md](../astrology/TODAYFLOW_CANON_V1.md).  
**Inventory (frozen, not executing):** [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](../astrology/KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md).

This file reverse-engineers Co–Star as a **working system**: what entities they use, what meanings they attach, how text is assembled, and why a person comes back. It is the empirical base for deciding what Knowledge Core TodayFlow actually needs.

It is **not** a source for IL claims. Co–Star sentences do not enter `claims/` or `objects_v1.json`.

---

## Architecture impact

- **SoT before:** next named IL pass was a short Evidence Corpus → Semantic Consensus → Canon proposal on planet claims (1.3.74). Knowledge Core research still ran author → claim → gap → another book. Co–Star appeared only as a landing-layout principle ([TODAYFLOW_TRUST_LAYER.md](../content/TODAYFLOW_TRUST_LAYER.md) §5) and as a **forbidden IL source** (IL §6.3).
- **SoT after:** further IL architecture / Canon execution / Outer fill / ASC–MC / literature is **frozen**. The next Knowledge Core decision waits on this teardown. Method: Co–Star output → underlying concepts → recurring semantic patterns → composition logic → personalization → content UX → then “what must exist as deterministic TodayFlow data?” Literature becomes gap-driven against that list, not a school-convergence program.
- **Public contract changed?** no
- **Migration required?** no — catalog 36 draft / 0 `active`; claims unchanged
- **Canon updated?** yes — this file · IL §6.29 · inventory execution order · parent research order · handoff
- **Backward compatible?** yes for runtime. Old “next = short corpus pass” is **superseded**. IL §6.3 still forbids ingesting Co–Star copy.

---

## 0. Why Co–Star, not “which school is more correct”

Co–Star’s success is not a proof that one historical reading of Mars is truer than another.

They split two jobs that TodayFlow mixed:

| Layer | Job | Test |
|-------|-----|------|
| **Calculation** | Sky positions are correct | Astronomy / ephemeris |
| **Meaning** | The reading is consistent, recognizable, and useful | User return, recognition, sharing |

Co–Star says this in public, in their own words. The natal-chart 101 page: the chart is “pure astronomy”; “anyone at NASA could understand and agree”; **astrology is how that astronomy is interpreted**. The US App Store listing: NASA data charts the stars; **human astrologers collaborate with AI** to produce the birth chart and daily horoscopes. Same listing: astrology is “a framework for understanding ourselves and our relationships,” not a claim of objective cosmic truth.

Observed market size (captured 2026-08-21, not a success proof by itself):

| Surface | Observation |
|---------|-------------|
| US App Store | 4.8 / 5 · **206K** ratings · version 5.43 |
| Google Play (`com.costarastrology`) | **5M+** installs |

That is a product-system signal. It is not a school-correctness signal.

### 0.1 Real quality criteria

The user does not score “does this Saturn match Lilly?”

They score:

1. Does this feel like me?
2. Is this unexpectedly specific?
3. Did it make me notice something?
4. Would I show this to a friend?
5. Would I open the app tomorrow?

An academically neat Saturn that loses on these five is **worse for the product** than a blunt, recognizable Saturn.

### 0.2 Do not copy Co–Star

Co–Star is a successful **provocative / social** astrology system.

TodayFlow’s likely position: keep the same personalization power, then make **daily practical usefulness** stronger — not only “what is happening to me,” but **what to do with it today**.

This teardown extracts the system. It does not import their voice, NASA marketing, fake reviews, or “algorithmically generate” as TodayFlow copy.

---

## 1. Method

Four layers, in this order. Do not collapse them into a feature list.

```text
Co–Star output
  → underlying concepts
  → recurring semantic patterns
  → composition logic
  → personalization
  → content UX
  → what must exist as deterministic TodayFlow data?
```

| Layer | Question |
|-------|----------|
| **1. Astrology model** | Which entities and combinations do they actually use? |
| **2. Semantic model** | What meanings do they attach to planets, signs, houses, aspects, transits? |
| **3. Content engine** | How do those meanings become a specific sentence / Do / Don’t / push? |
| **4. Product psychology** | Why does the sentence feel personal, provoke, return, and get shared? |

**Legal:** paraphrase and atomize. Do not paste Co–Star daily copy into IL. Short public lemmas below are evidence of *their* grammar, cited to public URLs.

**Phase 0 vs Phase 1.** Phase 0 (this file) uses **public** Co–Star surfaces. A repo search on 2026-08-21 found **no in-app screenshot / transcription corpus**. Phase 1 (in-app daily, Do/Don’t, push, compatibility cards) waits on files dropped under `docs/audits/costar_teardown_corpus/` (see §10). Do not invent in-app atoms.

---

## 2. Corpus (what was actually opened)

### 2.1 Used this pass (public)

| Source | URL | What it yields |
|--------|-----|----------------|
| Marketing home | https://www.costarastrology.com/ | Positioning: NASA + biting truth; full natal vs sun-sign magazines; friends; real-time as planets move; “natural-language engine” |
| Astrology 101 index | https://www.costarastrology.com/how-does-astrology-work | Entity curriculum: astrology / natal / sun / rising / houses / house systems / aspects / transits & orbs |
| Natal chart 101 | `.../what-is-a-natal-chart` | Calc vs meaning split; planet **verbs**; sign **adverbs**; composition example |
| Houses 101 | `.../houses` | House **nouns**; ASC/MC/IC/DSC cross; house polarities |
| House systems 101 | `.../house-systems` | Default = **Porphyry**; Whole Sign and Placidus explained, not default |
| Aspects 101 | `.../aspects` | Aspect operators + importance ranks (including minors they de-rank) |
| Transits & orbs 101 | `.../transits-orbs` | Transit = now × natal; worked Sun and Saturn cycles; orb as buffer |
| What is astrology 101 | `.../what-is-astrology` | Geocentric lived sky vs heliocentric astronomy |
| US App Store | https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561 | Feature graph, premium SKUs, framework sentence, NASA + human + AI split, 4.8 / 206K |
| Google Play listing | https://play.google.com/store/apps/details?id=com.costarastrology | 5M+ installs |

Zodiac-sun-sign and rising-sign 101 bodies did not return extractable text this pass (SPA). Their existence is attested by the 101 index. Do not invent those pages.

### 2.2 Owner-cited, not independently captured here

- Apple-highlighted review: daily use, compatibility, quirky Do/Don’t, praise for writers.
- Vanity Fair (2019): blunt / rude push notifications as a brand trait.

Treat as **psychology signals**, not as transcribed copy.

### 2.3 Not in this repo

No Co–Star PNG/JPG/WebP, no OCR dump, no daily-horoscope corpus. Phase 1 is blocked until that corpus exists.

---

## 3. Layer 1 — Astrology model

What they **actually teach as the machine**, not what a textbook could include.

### 3.1 Entity inventory (observed)

| Entity | In public 101 / store? | Notes |
|--------|------------------------|-------|
| Tropical zodiac, 12 signs | yes | Signs treated as 30° equal; “constellations” language is popular, not sidereal |
| Planets: Sun … Pluto (10) | yes | Outers included. Nodes / Chiron / Lilith **not** in 101 |
| Ascendant as first-class | yes | Listed **in the planet-verb table** (“I seem…”) |
| MC / IC / Descendant | yes | House-cusp geometry; not given their own verb row in the natal table |
| 12 houses | yes | Explicitly **not** astronomical; from Earth’s rotation + ASC |
| House system | yes | **Porphyry default**. Angles = 1 / 4 / 7 / 10 cusps |
| Major aspects | yes | 0° · 60° · 90° · 120° · 180° |
| Minor aspects | yes in 101 | 30° · 45° · 150° labeled “not too important” |
| Transits | yes | Transiting planet aspect natal planet |
| Solar return | yes | Named as transiting Sun conjunct natal Sun / birthday |
| Saturn return | yes | Named as transiting Saturn conjunct natal Saturn |
| Secondary progressions / solar arc | **not** in 101 | Do not assume they are in the public model |
| Birth time + place | yes | Required for full chart / houses / rising |
| Friends’ charts / compatibility | App Store + home | Social graph is a first-class **product** entity |
| Daily horoscope | App Store | Personalized, push-backed |
| Q&A (“Ask the stars”) | Premium SKU | Not a chart entity; a content surface |
| Eros / love report / crush / year-ahead | Premium SKUs | Relationship and long-range products |

### 3.2 Combinations they actually compose (from worked examples)

| Combination | Public example | Pattern |
|-------------|----------------|---------|
| Planet × sign | Mars in Gemini → “I take action in a curious, chaotic way.” | verb + adverb pack |
| Sign on house | Scorpio ruling 12th → “I approach secrets, dreams, and the unconscious with intensity and depth.” | house noun + sign adverb |
| Natal aspect | Gemini Mars conjunct Gemini Sun | fuse two already-composed planet×sign lines with an aspect operator |
| Transit | Transiting Sun square natal Sun → “Ego troubles” (every ~3 months) | transiting body × aspect × natal body + cycle timing |
| Return | Solar return / Saturn return | conjunction of a body to its natal place as a named life event |

Implied grammar (not a dump of their code):

```text
placement  = planet_verb  ×  sign_adverb  [× house_noun]
natal_asp  = placement_A  ×  aspect_operator  ×  placement_B
transit    = now_planet   ×  aspect_operator  ×  natal_placement  ×  cycle_clock
```

That is a **small** combinatorial engine. It is not “every traditional technique.”

### 3.3 What they leave out of the public model

No public 101 for: lunar nodes, Chiron, Lilith, Arabic parts, profections, primary directions, midpoints as a user-facing layer, electional, horary, dignity scoring as user copy.

For TodayFlow this is the important cut: **a successful mass product can run on natal placements + houses + major aspects + transits + social overlay.** Extra techniques are optional depth, not the core loop.

---

## 4. Layer 2 — Semantic model

Meanings they **publish**, not meanings we wish they used.

### 4.1 The grammar (locked observation)

From natal 101:

- **Planets = verbs** (first-person templates).
- **Signs = adverbs** (adjective packs).
- **Houses = nouns / context** (life areas).
- **Aspects = operators** (how two verbs relate).
- **Transits = the same operators in time.**

This is a composition language. It is not a bibliography.

### 4.2 Planet verbs (public lemmas)

Source: natal-chart 101 table. First-person. Mixed personal vs generational.

| Body | Public verb stem |
|------|------------------|
| Sun | I am fundamentally… |
| Moon | I experience emotion… |
| Ascendant | I seem… |
| Mercury | I communicate… |
| Venus | I love… |
| Mars | I take action… |
| Jupiter | I expand through… |
| Saturn | I discipline myself… |
| Uranus | My generation innovates… |
| Neptune | I dream… |
| Pluto | My generation experiences power… |

Observations for TodayFlow:

1. Every personal body is a **process in the first person**, not a keyword pile (not “Saturn = structure”).
2. ASC is treated as a **self-presentation verb**, equal in the table to planets. TodayFlow still has ASC/MC as `NEED_MODEL`.
3. Uranus and Pluto are **generational**, not “I rebel / I transform.” Neptune is personal (“I dream”). That split is already more product-useful than slogan CORE.
4. Venus = love (relational). Mars = take action. Jupiter = expand **through**. Saturn = discipline **myself**. These are composable stems.

### 4.3 Sign adverb packs (public lemmas)

Short, mixed valence, socially usable. They include unflattering words on purpose (`chaotic`, `power-hungry`, `anti`, `attention-loving`).

| Sign | Public pack (as published) |
|------|----------------------------|
| Aries | assertive, competitive, independent |
| Taurus | practical, stubborn, sensual, reliable |
| Gemini | curious, chaotic, witty |
| Cancer | sensitive, nurturing, gentle |
| Leo | bold, proud, attention-loving, charming |
| Virgo | responsible, meticulous, wholesome |
| Libra | fair, just, relativist |
| Scorpio | intense, deep, power-hungry |
| Sagittarius | restless, intellectual |
| Capricorn | responsible, serious, efficient, rational |
| Aquarius | unconventional, anti, boundary-pushing |
| Pisces | insightful, intuitive, empathetic |

Pattern: 3–4 adjectives, at least one edge, no historical heat/dry, no Lilly temperament. **Recognition + distinctiveness**, not school pedigree.

Virgo and Capricorn both carry `responsible` — they do not over-optimize uniqueness. Context (planet/house) disambiguates.

### 4.4 House nouns (public lemmas)

| House | Public noun / context |
|-------|------------------------|
| 1 | Self-image, impressions you make |
| 2 | Personal resources, what makes you feel safe |
| 3 | What you know, everyday surroundings, siblings, familiar patterns |
| 4 | Home, family, close relationships, the past’s effect |
| 5 | Pleasure, creativity, self-expression, fun, children |
| 6 | Productivity, service, routines |
| 7 | Partnership, committed relationships, what others bring in |
| 8 | Other people’s resources, what’s out of your control, beginnings/endings, transformations, crises |
| 9 | Open-mindedness, philosophy, culture/ideas, expanded consciousness, travel |
| 10 | Public self, commitments, career, how you want to be remembered, legacy |
| 11 | Social world, friends, groups |
| 12 | Unconscious, dreams, fantasies |

Plus **six polarities** (private self vs public persona):

| Axis | Private | Public | Theme they name |
|------|---------|--------|-----------------|
| 1–7 | How you assert | How you function in close relationships | Independence vs Harmony |
| 2–8 | Material resources / identity from them | Reshaping of self | Stability vs Trust |
| 3–9 | Expressing what you know (near) | Expanding what you know (abstract) | Facts vs Ideas |
| 4–10 | Domestic / family / past | Goals / work / future | Private vs Public life |
| 5–11 | Creative self / personal pleasure | Shared goals / group over self | Self vs Collective |
| 6–12 | Helpfulness, routines, order | Psychic space / spiritual service | Survival vs Transcendence |

This is already a **composition rule**: a house is not a lonely noun; it sits on an axis. TodayFlow IL houses are `DRAFT_CLASSICAL` and have no polarity layer.

### 4.5 Aspect operators (public lemmas)

| Aspect | Degrees | Valence tag | Meaning word | Importance |
|--------|---------|-------------|--------------|------------|
| Conjunction | 0° | Neutral | Same same | Most |
| Opposition | 180° | Neutral | Mirror opposites | Most |
| Square | 90° | Friction / Frustration | Conflict | Very |
| Trine | 120° | Harmonious & Friendly | Harmony | Very |
| Sextile | 60° | Harmonious & Friendly | Supportive | Pretty |
| Semisextile | 30° | Harmonious | Growth | Not too |
| Semisquare | 45° | Friction | Friction | Not too |
| Quincunx | 150° | Friction | Adjustment | Not too |

Worked natal example (conjunction): two planet×sign lines are written first, then fused: “who you are is fused with the way you take action — for better and for worse.” The operator is **relational and mixed-valence**, not “good aspect / bad aspect” as destiny.

TodayFlow V1 inventory parks minors as `OUT_OF_V1`. Co–Star *lists* them and **de-ranks** them. That supports keeping minors out of V1 runtime while admitting they exist.

### 4.6 Transit meanings (worked, thin, timed)

They do not publish a 10×10×5 transit encyclopedia on the 101. They publish **cycle clocks + one-line effects**:

| Transit | Timing they give | One-line meaning |
|---------|------------------|------------------|
| Sun conjunct natal Sun | birthday / yearly | Ego activation |
| Sun square natal Sun | ~every 3 months | Ego troubles |
| Sun opposite natal Sun | ~6 months from birthday | Reflecting about being |
| Saturn conjunct natal Saturn | ~29 / 58 / 87 | Activation of responsibility |
| Saturn opposite natal Saturn | ~14 / 44 / 75 | Reflecting about discipline |

Pattern:

```text
transit_line = (activation | trouble | reflecting) × (natal_planet_theme)
```

Sun theme in these lines = **ego / being**. Saturn theme = **discipline / responsibility**. That matches their verb table, not Lilly’s cold/dry.

Orb: they say astrologers use **1°–10°**; the worked solar-return diagram uses **±3°**. So even their public engine treats orb as a **product threshold**, not a school holy number.

---

## 5. Layer 3 — Content engine

How meaning becomes a thing you can read. Inferred from public grammar + store surfaces. Phase 1 must confirm with real screens.

### 5.1 Pipeline they advertise

```text
NASA / sky positions
  → natal + current aspects (calculation)
  → professional-astrologer methods
  → natural-language engine (algorithmic generation)
  → human astrologers × AI
  → surfaces: chart · daily · push · friends · questions · relationship SKUs
```

Objectivity is claimed at **positions**. Generation is claimed at **language**. That is the same split as TodayFlow’s intended `calc → atoms → composition → LLM formulates` — except they do not pretend the meaning layer is historically unique.

### 5.2 Sentence factory (reconstructed)

From the worked public sentences, a daily or natal line is probably:

1. Pick a **focal placement** (planet in sign, optionally house).
2. Fill `verb_stem + adverb_pack` (and house noun if the surface is “where”).
3. If two bodies: apply **aspect operator** (fuse / conflict / harmony / support / mirror).
4. If time-bound: stamp **cycle clock** (today, this week, return age).
5. Run a **voice pass**: short, first-person or imperative, mixed valence, concrete.

Worked reconstructions (from *their* public examples, not TodayFlow copy):

| Input | Output pattern |
|-------|----------------|
| Mars in Gemini | I take action + curious/chaotic |
| Scorpio on 12 | I approach [12th nouns] + intense/deep |
| Sun conjunct Mars in Gemini | identity line fused with action line |
| Sun square Sun | ego + trouble + quarterly clock |

The engine is **template-hard** at the concept layer and **writer-soft** at the wording layer. App Store: writers are part of the product (owner-cited review). Vanity Fair: the voice *is* the notification.

### 5.3 Content slots (product, not astrology)

From App Store features + owner-cited review, the content types are distinct slots:

| Slot | Job |
|------|-----|
| Natal placement blurb | “This is you” |
| Daily horoscope | “This is today” |
| Push | Re-open; often ruder/shorter than the in-app paragraph |
| Do / Don’t | Quirky, specific, shareable constraint |
| Compatibility card | “This is us” — social object |
| Question answer | On-demand, premium |
| Relationship situation (Eros) | What to do with a dyad today |

Do/Don’t is **not** a new planet. It is a **content UX transform** of the same atoms: turn a verb×adverb×operator into a constraint.

TodayFlow already has do/don’t as a Guidance job ([TODAYFLOW_PRODUCT_CANON_UNIFIED.md](../TODAYFLOW_PRODUCT_CANON_UNIFIED.md)). Co–Star shows the slot must be **quirky and specific**, not a generic “be patient with Saturn.”

### 5.4 What the engine is *not*

- Not a dump of Lilly for Saturn.
- Not a unique transit essay per pair written from scratch each night (they advertise an engine).
- Not sun-sign magazine copy (they contrast against that).
- Not “the LLM decides what Mars means today.” Methods of professional astrologers are claimed as the method layer; AI is claimed as a collaborator on wording.

---

## 6. Layer 4 — Product psychology

Why the text works as a habit.

### 6.1 Loop they actually sell

```text
exact chart (not sun sign)
  → recognizable “this is me”
  → daily personalized forecast
  → push (habit)
  → friends / compatibility (social object)
  → questions / Eros / reports (depth + revenue)
```

Home page sequence matches: birth chart → better together → real-time as planets move.

### 6.2 Personalization mechanics (observed)

| Mechanic | How it feels personal | Astrology cost |
|----------|----------------------|----------------|
| Full natal vs sun-sign | “They used my time and place” | Birth time + houses + ASC |
| Planet×sign sentence | Specific combination, not a sign essay | 10×12 table, not 12 sun texts |
| Daily as sky moves | New today, not a static bio | Transits + orbs |
| Friends | Chart becomes a social graph | Synastry overlay |
| Mixed-valence adjectives | Feels honest (`power-hungry`, `chaotic`) | Permission to be unflattering |
| First person | Identity, not lecture | Verb stems |
| Biting / blunt voice | Surprise + share | Writers, not more planets |
| Do/Don’t | Actionable quirk | Content slot |
| “No bad signs, only complicated dynamics” | Compatibility without insult | Operator language (complicated, not doomed) |

### 6.3 Return and share

Return is engineered by **push + daily clock + social graph**, not by a better Saturn footnote.

Share is engineered by **short, rude-or-funny, specific lines** and by **compatibility as an object you can hold up to a friend**.

The Apple-highlighted review (owner-cited) names exactly those hooks: daily habit, compatibility, quirky Do/Don’t, writers.

### 6.4 Epistemic posture

They do **not** ask the user to believe astrology is true. They ask the user to use it as a **framework for self and relations**. That lowers the proof burden on meaning and raises the proof burden on **usefulness and recognition**.

TodayFlow’s Trust Layer already split NASA/JPL accuracy from Canon-as-method. IL research then re-merged them by treating school-convergence as the meaning test. This teardown splits them again.

---

## 7. Comparison to TodayFlow

Do not treat Co–Star as the product spec. Treat it as a working benchmark.

| Dimension | Co–Star (observed) | TodayFlow (current SoT) |
|-----------|--------------------|-------------------------|
| Calc | NASA-branded positions; Porphyry houses | Swiss / JPL ephemerides; **Placidus** default ([DAY_SOURCES_CANON.md](../DAY_SOURCES_CANON.md), [PRODUCT_DATA_PROVIDERS.md](../PRODUCT_DATA_PROVIDERS.md)) |
| Meaning test | Recognition, specificity, habit, share | Until 1.3.73–1.3.74: school intersection / CORE; then Canon criteria — **not yet executed**, now frozen |
| Planet semantics | First-person verbs; outers mostly generational | Classical elemental `function` on Sun–Saturn drafts; outers claims-only; slogans forbidden |
| Signs | 3–4 mixed-valence adverbs | Lilly classification-only drafts; later-interpretive deferred |
| Houses | Life-area nouns + polarities | 12 house drafts, `DRAFT_CLASSICAL` |
| ASC | First-class verb | `NEED_MODEL` — not an IL object |
| Aspects | 5 majors + 3 minors de-ranked | 5 majors; minors `OUT_OF_V1` |
| Daily | Transit engine + voice + push | Today pipeline: sky → global day → natal overlay → ritual → personal → presentation |
| Action | Do/Don’t as content slot | do/don’t exists as Guidance; practical Today is the intended edge |
| Social | Friends, compatibility, Eros | Compatibility is a first-class screen ([MARKET_ATTENTION_AND_SCREEN_JOBS.md](../MARKET_ATTENTION_AND_SCREEN_JOBS.md)) |
| Voice | Blunt, shareable | Person-not-system ([TODAYFLOW_VOICE_CANON.md](../content/TODAYFLOW_VOICE_CANON.md)); landing already used Co–Star *layout* principle, not their copy |
| Runtime | Engine + human writers + AI | Intended: Canon → Composition → LLM formulates; **Canon not filled** |

### 7.1 Where we mixed the two requirements

Calculation (Swiss, Placidus, orbs, VOC) was held to a correctness bar.

Meaning was also held to a correctness bar (Ptolemy → Lilly → Greene → Hand → Rudhyar → CORE).

Co–Star holds **only calc** to that bar. Meaning is held to **consistency + recognition + use**.

### 7.2 Product position (not a lock of copy)

Co–Star: provocative / social astrology.

TodayFlow: same personalization power, **stronger daily practical usefulness** — Today as “what to do with this,” not only “what is happening to me.”

That means our Canon still needs Co–Star-like **composable stems**. It then needs extra atoms Co–Star can skip: **do / avoid / attention** that survive a value gate and a day, not just a screenshot.

---

## 8. What this changes in Knowledge Core

### 8.1 Research order (supersedes author-first *and* delays Canon execution)

Wrong next step (1.3.74): score 491 planet claims into Consensus → lock Canon packs.

Right next step: finish this teardown (Phase 1 in-app) → list **deterministic atoms TodayFlow must own** → only then fill Canon / IL to that list.

Literature after that is **gap-shaped**. Example (illustrative, not a book order): if Venus × Saturn composition cannot say boundaries / withholding / commitment in a way that is recognizable and useful, research **that gap**. Do not read a Saturn monograph because Saturn exists.

### 8.2 Hypothesis: what must exist as deterministic TodayFlow data

Not locked. This is the candidate list Phase 1 will thicken or cut.

**Must exist as data (else LLM invents meaning):**

1. Planet **verb / process stems** (first-person or impersonal equivalent), including a personal vs generational flag for outers.
2. Sign **adverb packs** (short, mixed valence, composable).
3. House **nouns** and optionally **polarities** (1–7 … 6–12).
4. Aspect **operators** (fuse / conflict / harmony / support / mirror) with an importance rank.
5. Transit **clocks** for bodies we actually surface (Sun cycle, Saturn cycle, and whichever others Today uses).
6. ASC as a **self-presentation stem** (Co–Star already does; we do not).
7. Composition rules: `verb × adverb [× noun] × operator × clock`.
8. Content-slot transforms: identity line, daily line, do, don’t, share line — **rules**, not 10 000 essays.

**May stay out of V1 data (Co–Star public model does not need them to run the loop):**

- Minor aspects as runtime (they list and de-rank).
- Progressions / solar arc as IL objects.
- Nodes / Chiron / Lilith as gold.
- Historical temperament (hot/dry) as Today `function`.
- School-intersection CORE as a permission bit.

**Must not be copied from Co–Star into IL:**

- Their sentences, Do/Don’t, pushes, or adjective strings as `source`.
- Their Porphyry default (ours is Placidus unless canon changes house system — a **calc** decision, not a teardown souvenir).

### 8.3 Benchmark

After Canon exists, a pack is not done when it is well-cited.

It is done when a composed Today/Profile line beats “accurate but dead” on the five quality criteria in §0.1, using Co–Star as the **feel benchmark**, not as the text source.

---

## 9. Gaps this pass does not close

| Gap | Why it matters | Unblock |
|-----|----------------|---------|
| No in-app daily / Do–Don’t / push corpus in repo | Content engine §5 is reconstructed from 101 + store, not from tonight’s screen | Owner drops screens/transcriptions → Phase 1 |
| Sun-sign and rising 101 bodies uncaptured | ASC verb is in natal table; rising page may add more | Re-fetch or screenshot those two URLs |
| Synastry operators unpublished | Compatibility is core product; 101 does not show the dyad grammar | Phase 1 compatibility screens |
| Orb table unpublished except ±3° solar-return example | We must not steal an orb policy from one diagram | Keep Foundation/Day Sources orbs until a product decision |
| Writer-bank vs live LLM mix unknown | Affects how much TodayFlow should freeze vs generate | Phase 1: repeated days, identical natal, watch reuse |

Do **not** fill these gaps by scraping the app, pirating copy, or asking an LLM to “remember Co–Star horoscopes.”

---

## 10. Phase 1 capture protocol

When screens exist, put them in `docs/audits/costar_teardown_corpus/` with a sidecar `.md` per screen:

```text
screen_id:
surface: natal | daily | push | do_dont | compatibility | question | eros | other
visible_entities: [Sun, Mars, square, house_10, ...]
verbatim_user_text: |
  (short; internal research; not for IL ingest)
atoms:
  - verb:
  - adverb:
  - noun:
  - operator:
  - clock:
  - slot: identity | daily | do | dont | share | question
personalization_cues: birth_time | friend | today_date | ...
quality_scores: me / specific / notice / share / return   # 1-5
```

Then extend **this file** §3–§6 with attested in-app patterns. Still no IL ingest.

---

## 11. Freeze and next

**This file’s job after 1.3.76:** recognition check on Mainstream rows. Not a meaning source. Not the IL unlock.

**Still forbidden:** IL ingest of Co–Star copy · cloning voice/features.

**This pass done:** Phase 0 teardown from public Co–Star 101 + store listings.

**IL next (1.3.76):** Mainstream Western Astrology V1 planet map. Use this teardown to ask “would a contemporary user recognize this territory?” — not to copy.

Phase 1 in-app atomization remains useful when a corpus exists; it does not block the Mainstream map.

---

## Changelog

- **1.1 (2026-08-21)** — Role restated after 1.3.76: recognition check, not Knowledge Core unlock.
- **1.0 (2026-08-21)** — Phase 0. Public 101 + App Store / Play reverse-engineered into four layers. IL architecture frozen (1.3.75). In-app corpus absent from repo.
