> SUPERSEDED 2026-07-24 → см. docs/TODAYFLOW_PRODUCT_CANON_UNIFIED.md

# TodayFlow Core Product Canon

Last updated: 2026-07-21
Status: Canonical working document
Owner: Product + Engineering

## 1. Product Definition

`TodayFlow` is the brand and the system.

TodayFlow is not a collection of separate esoteric tools.
It is a **daily navigation system** built around one person — clarity, direction, and daily reflection through a personal map.

**Product kernel:** [DAILY_NAVIGATION_MODEL.md](../DAILY_NAVIGATION_MODEL.md) (Identity → Current Context → Guidance → Action).  
**Market + screens:** [MARKET_ATTENTION_AND_SCREEN_JOBS.md](../MARKET_ATTENTION_AND_SCREEN_JOBS.md) (рыночные уровни, 5 доменов Today, зачем открывать экран).  
**Daily loop:** [CORE_USER_LOOP.md](../CORE_USER_LOOP.md) (Theme → Action → Progress).

Core product formula:

TodayFlow creates a living life map of the user and uses that map to orient the user each day — what matters now, what to avoid, what it means for them, and the next step.

The system center is the user's personal core:
- name
- birth date
- birth time
- birth place

This core is used to assemble the person's stable personal map:
- natal chart
- numerology base
- zodiac identity and derived astrology signals
- baseline archetypes and psychological orientation

This is the user's:
- face
- life map
- orientation system
- reference point

## 2. Primary Product Surfaces

### A. Profile
This is the user's main personal page.

**Product model:** [PROFILE_SCREEN_MASTER.md](../profile/PROFILE_SCREEN_MASTER.md) (единственная UI-спека Profile).

It must show:
- natal chart
- core numerology number(s)
- zodiac sign and related identities
- strong sides
- weak sides
- what to avoid
- what supports them
- life areas and houses:
  - family
  - career
  - love
  - money
  - purpose
- ability to create additional profiles:
  - spouse
  - child
  - another important person

This page answers:
- who am I
- what is my structure
- what are my patterns
- how do life areas express through my map

### B. Today
This is the user's daily guide.

**Product model (blocks, Today Package, generation funnel):** [TODAY_PRODUCT_MODEL.md](../TODAY_PRODUCT_MODEL.md).  
**First 30 seconds after signup:** [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md).

It must show only today's relevant information:
- what today may bring
- what to focus on
- what to avoid
- how today's astrology interacts with the profile
- how the name / numerology / current day number reinforce the interpretation
- tarot card of the day
- explanation of how the tarot card influences this day specifically for this user

This page answers:
- what kind of day is this for me
- what can happen
- what should I do
- what should I not do

Additional rule:
- `Today` is not only a response surface, it is also a signal-collection surface.
- Every meaningful daily interaction may strengthen personalization:
  - state check-ins
  - daily focus choices
  - ritual feedback
  - mini-decision answers
  - question-of-the-day answers
- The system uses these signals to make later answers more personal, more precise, and less generic.
- Weekly and monthly state maps are not separate product roots; they are accumulated understanding layers around the same person.

### C. JTBD Entry Layer
This is an **optional explicit-input** layer (Questions Hub, future AI). It is **not** the product center.

The daily product center is **opening a surface** (Today, Profile, Compatibility) and receiving orientation without typing a question. See [DAILY_NAVIGATION_MODEL.md](../DAILY_NAVIGATION_MODEL.md).

When the user types a question, the same pipeline applies: Profile → Context → Guidance → Action — not a separate Q&A brain.

Implicit orientation still applies on every surface:
- the first screen they land on
- the structure of the page
- the main CTA
- the meaning and wording of blocks (ICA: Identity / Context / Guidance / Action)

Explicit free-form question input is optional; **daily navigation without questions** is mandatory.

### D. Separate Service Surfaces
These exist as independent services, but always read through the user's profile when personal context exists:
- horoscopes
- compatibility
- tarot service
- habits
- ascetic practices
- practices
- cycles
- mood tracking

Rule:
services may be standalone in navigation, but personalization must use the same core profile.

## 3. Information Architecture Rule

We remove everything excessive.

The product must become simple and legible:
- Profile = personal map
- Today = daily guide
- JTBD entry = implicit routing through surfaces, CTAs, and page structure
- Deeper services = optional layers around today's clarity, not separate product centers
- Compatibility = relationship lens
- Tarot = symbolic guidance
- Growth = habits, practices, mood, cycles, ascetic discipline

No screen should try to explain the whole system at once.

## 3.1 JTBD Rule

Users do not buy astrology, tarot, or numerology as isolated systems.

They buy:
- clarity
- explanation
- control
- decision support
- daily orientation

The product must therefore be designed around user jobs to be done, not around internal modules.

The 4 mandatory top-level JTBD for TodayFlow are:
- understand myself
- understand another person
- make a decision
- understand what to do today

Every major surface, route, and API should map back to at least one of these jobs.

## 3.2 Question-First Rule

TodayFlow must be built around the user's question, but the user does not need to type that question directly into the product.

Canonical examples:
- "Что он/она чувствует?"
- "Стоит ли писать?"
- "Почему у меня не растут доходы?"
- "Почему я снова выбираю не тех?"
- "Как лучше прожить этот день?"

System rule:
- the product infers the likely JTBD from entry point, current screen, chosen action, and user context,
- assembles the answer through the shared core profile,
- returns one coherent response,
- then offers the one best deeper route.

Important:
- explicit free-form question input is optional,
- implicit intent recognition is mandatory.

Modules such as tarot, compatibility, growth layers, and profile remain implementation layers, not the user's mental model.

## 4. Personalization Rule *(Personal Model — уже канон)*

**SoT (не дублировать новым «принципом»):**  
[TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) · [PERSONAL_INTELLIGENCE_LAYER.md](../pim/PERSONAL_INTELLIGENCE_LAYER.md) · [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](../DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md).

All personal content must go through the same Personal Model / core profile snapshot.

If the profile exists, any module must interpret through it:
- horoscope
- compatibility
- tarot
- forecasts
- daily guidance

Modules answer domain questions for an **already known** person; they do not rebuild personality from birth/sign alone when a snapshot exists.

Additional personalization rule:
- the profile is not static onboarding data only;
- it is a living interpretation base that is updated through behavior and daily signals;
- `Today`, weekly state maps, monthly state maps, and future learning layers must all enrich the same user understanding model.

**Code compliance (канон → факт → fix):** [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](../audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md).

## 5. Multi-Profile Rule

A user can have multiple profiles in one account.

Supported first:
- self
- spouse/partner
- child

These profiles are used for:
- compatibility
- relationship interpretation
- family-oriented guidance

The self profile is primary.
Other profiles are secondary entities, not equal dashboard roots.

## 6. Text Generation Canon

### Main rule
Texts must be meaningful, alive, specific, and readable.

We do not use the current gate/validator as the main content shaper.

### New model
Every meaningful personalized text goes through API generation:
- profile interpretation
- today interpretation
- tarot interpretation
- themed tarot spreads
- compatibility overlays
- aspect-by-aspect profile breakdown

### Learning LLM rule
The product must also build a parallel learning LLM layer.

Its task is:
- to observe how the user describes themselves;
- to track what questions, tensions, and themes keep returning;
- to connect answers, diary entries, daily signals, and route choices;
- to refine how the system explains, warns, and guides;
- to gradually build a more accurate psychotype and decision style model.

This learning layer is shared infrastructure for web and iOS, not a separate product surface.

**Operational plan:** [PERSONAL_INTELLIGENCE_MODEL_V1.md](../pim/PERSONAL_INTELLIGENCE_MODEL_V1.md) · [PERSONAL_INTELLIGENCE_LAYER.md](../pim/PERSONAL_INTELLIGENCE_LAYER.md) · [USER_KNOWLEDGE_MODEL.md](../pim/USER_KNOWLEDGE_MODEL.md). **Today** events and prompts — [TODAY_PERSONALIZATION_CORE.md](../TODAY_PERSONALIZATION_CORE.md). **DayContext** — [DAY_ENGINE_AND_COHERENCE.md](../DAY_ENGINE_AND_COHERENCE.md), [DAY_CONTEXT_V0.md](../DAY_CONTEXT_V0.md). **North star** — [USER_MODEL_TARGET_STATE.md](../pim/USER_MODEL_TARGET_STATE.md). **Today experience** — [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md).

Important product rule:
- the system must remember which generated answers led to helpful reactions, continued engagement, route completion, or confusion;
- the system must use this to distinguish stronger and weaker response patterns over time;
- this learning loop is internal and must not be explicitly presented to the user as "training the model" or "teaching the machine".

The system must not state to the user that content is processed by AI.

### Role of validation now
Validation is allowed only as a safety/sanitation layer:
- remove empty output
- reject obvious garbage
- reject contradictions to payload shape
- reject duplicated or broken fragments

Validation must not flatten the voice or replace rich text with dead templates.

### Target quality
Each text must feel:
- personal
- concrete
- coherent
- emotionally literate
- useful

It must not feel:
- generic
- ritualistic in a hollow way
- repetitive
- assembled from dead templates
- abstract for the sake of sounding deep

## 6.1 Canonical Answer Shape

**Product contracts per need/intent:** [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) · [SCREEN_CONTRACTS_V1.md](../SCREEN_CONTRACTS_V1.md). Central object = `need_id`; envelope below is how assembled answers are shaped.

Any serious JTBD answer in TodayFlow must try to cover the following structure:
- clarity: what is happening
- explanation: why this is happening
- forecast: where this may lead next
- decision: what action is most reasonable
- today: what to do right now

If a response omits most of these layers, it is not yet a full TodayFlow answer.

This does not mean every screen must be long.
It means every flow must either provide these layers directly or clearly stage them in sequence.

## 7. Profile Generation Flow

1. User enters:
- name
- birth date
- birth time
- birth place

2. System builds the stable core:
- geocoding
- natal chart
- numerology base
- core snapshot

3. System requests profile interpretation in structured sections:
- general identity
- strengths
- weak sides
- love
- career
- money
- family
- purpose
- what to avoid
- what supports growth

4. Profile page reveals this material by sections, not as one giant wall.

## 8. Today Generation Flow

1. Read stable core profile snapshot.
2. Add current-day layers:
- transits
- numerology of the day
- lunar/cycle context
- tarot of the day

3. Generate a unified daily interpretation:
- what may happen
- what to do
- what to avoid
- where tension may appear
- where support exists

4. Generate the tarot explanation through the same profile lens.

## 8.1 Day Structure Rule

The product does not split into three separate products: morning, day, and evening.

Rule:
- there is one `Today` surface,
- time-of-day may gently affect emphasis,
- the system may send reminders or suggest the next relevant action for the current part of day,
- actions themselves should live on separate meaningful screens,
- the user should not be forced to process everything on one overloaded daily screen.

Morning, day, and evening are:
- optional timing modes,
- reminder logic,
- light framing for the same daily guide,
- not equal standalone product roots.

## 8.2 Canonical User Journey

**Contract (v2, 2026-06-23):** [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md) — routes, signup vs onboarding data, guest demo, PIM.

The canonical user journey is:

0. **guest value** — landing, `/demo/today`, sign-based surfaces (no account)
1. **signup** — account + legal + locale only (no birth data)
2. **onboarding** — `/onboarding/core` → intent → reality (not Profile hub)
3. **first today** — personal payoff (`Theme → Action → Progress`)
4. **profile** — life map / portrait **after** first Today (cabinet, not onboarding)
5. **deeper routes** — tarot, compatibility, growth, helper decision layers from Today or Profile

Expanded product reading:
- guest sees value before email
- input birth core in **onboarding**, not at signup
- build stable CoreProfile SN server-side
- **Today first** — operating layer is the first personal payoff
- **Profile second** — reveal the map when user is ready for depth
- from `Today`, `Profile`, and deeper surfaces, route into the one relevant next service

**Anti-pattern:** post-signup landing on `/profile?setup=core` as if Profile were onboarding.

The system must not feel like a set of unrelated tools.
It must feel like one guided journey with one center.

## 9. Implementation Rules

### Build once
Build once and reuse:
- natal chart
- numerology base
- stable core snapshot

### Recompute by date
Recompute by day:
- today interpretation
- day number
- tarot day context
- daily guidance

### Recompute by action
Recompute on user actions:
- journal summaries
- growth signals
- mood/cycle overlays
- rewards and streaks

## 10. Priority Direction

The next product truth is:

1. `Profile` must become the user's clear personal map.
2. `Today` must become the user's clear daily guide.
3. JTBD routing must become implicit across the product's main surfaces.
4. Other services stay separate, but always attach to the profile lens.
5. Dead template text generation must be replaced by high-quality API-driven interpretation.

## 11. Mandatory JTBD Packs

To claim product completeness, TodayFlow must explicitly support these packs:

### A. Love OS
- what the other person feels
- why the relationship gets stuck
- whether to continue or let go
- why the user repeats the same romantic pattern

### B. Money / Career OS
- why income is not growing
- what strength should be monetized
- whether to change work
- whether to act now or wait
- how to move to the next income level

### C. Decision OS
- do it or not
- write or not write
- stay or leave
- accept the offer or not
- risk now or wait

### D. Pattern OS
- why the same situations repeat
- why the same relationship endings repeat
- why discipline breaks
- why closeness is hard
- why toxic dynamics repeat

### E. State OS
- what is happening emotionally right now
- whether it is temporary
- why there is no energy
- how to get through the next 24 hours

### F. Daily Operating System
- what to focus on today
- what to avoid today
- where to act and where to hold
- whether the day is better for risk, closure, communication, or recovery
