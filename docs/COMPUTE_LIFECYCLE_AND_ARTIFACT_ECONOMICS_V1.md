# Compute Lifecycle and Artifact Economics V1

**Date:** 2026-08-25  
**Status:** **LOCKED** — when artifacts are calculated, persisted, reused, and when LLM may run. **Not** a Knowledge Core expand. **Not** IL-2/3/4 reopen. **Not** public JSON. **Not** a paywall implementation. **Not** a Kimi quality cut.  
**Canon:** Swiss/JPL → calc → IL → Composition → LLM Expression ([INTERPRETATION_LIBRARY_V1.md](./astrology/INTERPRETATION_LIBRARY_V1.md)). Today meaning: [TODAY_CONTENT_PIPELINE_V1.md](./today/TODAY_CONTENT_PIPELINE_V1.md). Natal Decode GET: [PROFILE_NATAL_DECODE_CACHE_REFRESH_V1.md](./profile/PROFILE_NATAL_DECODE_CACHE_REFRESH_V1.md). Router caps: [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md). Payload facts: [audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md](./audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md). AGENTS.md Architecture impact.

This pass answers: **quality and cost are the same problem.** Semantic drift (new “character” because a prompt fingerprint moved) is a product defect. Recurring LLM on GET / login / new day / prompt bump is a cost defect. Fix lifecycle first. Do not degrade K3 where synthesis actually creates value until useless calls are gone.

Catalog **38 draft / 0 `active`**. Unchanged. Knowledge Core V1 stays frozen.

---

## Architecture impact

- **SoT before:** Cost Containment capped tokens/models. Natal Decode GET never rebuilds. I0 already named one Global Day per timezone + persist text. Runtime still mixed product compute with prompt-version hashes, per-user Global LLM, production prewarm, Tarot LLM on every draw.
- **SoT after:** **This file is lifecycle + economics SoT.** Layers have different cadences. Four version axes (`calc` / `semantic` / `expression` / `behavior`). Four Profile rebuild triggers only. `expression_version` (prompt) is **not** an invalidation key. Today persist key = `user × local_date × semantic_version`. Global Day = `date × locale/version`, not × user. LLM is last expression/synthesis. Three compute ledgers. Knowledge Core V1 is not expanded. **Work order:** Profile invalidation → shared Global Day → Personal Day lifecycle → Profile selection (after usage audit) → behavioral overlay → Tarot economics → Compatibility economics. Do **not** mechanically cut Profile to 5–8 themes.
- **Public contract changed?** no
- **Migration required?** no JSON. Existing snapshots reuse via identity fallback. Decode logs via legacy polish fingerprints.
- **Canon updated?** yes — this file · tracker · LLM quality unit economics · IL freeze “do not expand atoms” · README
- **Backward compatible?** yes for clients. Pre-release testing may still force-rebuild (ledger = engineering).

---

## 0. Principle

```text
Calculate once → interpret deterministically → persist → reuse
→ generate only where personalization creates extra value.
```

Not: each screen = LLM generation.

Matches the already chosen stack: Swiss/JPL → calc → IL (38 atoms → 616 IL-2 cells) → Composition / IL-3 rank → **selection** → LLM Expression.

K3 is justified when it synthesizes **already selected** structured meaning (natal portrait, paid deep report). It is not a daily ranking engine. Profile Selection is a later pass **after** a usage audit — not a blind 5–8 cut.

**Quality effect of this model:** the same birth data + same compatible semantic version → the same natal chart and canonical theses. Behavior may move; the sky portrait does not. That is more product, not less.

**Do not** cut Kimi quality on paid / natal synthesis **before** lifecycle. First delete meaningless calls. Then measure one real user lifecycle. Then decide whether the model even needs to get cheaper.

---

## 1. Three compute ledgers

| Ledger | What | Enters MAU COGS? |
|--------|------|------------------|
| **Core subscription** | Natal+CE initial · one Personal Today / user / local_date · behavioral deltas when meaningful | yes |
| **Premium** | Paid Tarot spreads · personal compatibility report · other deep paid synthesis | no — attached to the transaction |
| **Engineering** | Force rebuild, calibration, canon migration, eval, experiments | **no** — never fold into $/MAU |

Pre-release: automatic production prewarm of real accounts is **not required**. Testing uses **explicit force rebuild** (`user` / `date` / `stage`) logged as DEV/ADMIN, not as product economics.

---

## 2. Profile layers (not a monthly rebuild)

There is **no** calendar TTL on the natal-dependent Profile. Birth data unchanged → chart unchanged in a month, a year, ten years. Canonical theses from that chart must not rewrite themselves.

| Layer | When computed | Auto-update |
|-------|---------------|-------------|
| Natal chart / placements / aspects / houses | profile create / birth-data change | **never** by time |
| Canonical natal meaning / основные тезисы | after natal build | **never** by time |
| Character baseline | after natal | only if semantic engine/canon is **incompatible** (controlled migration) |
| Behavioral profile | natal baseline + accumulated behavior | when **meaningful delta** exists |
| Preferences / goals / user facts | user actions | dynamically (cheap; not K3) |
| Expression / summary | when the meaning source changed | at most periodically; not a full natal rebuild |

Monthly cadence, if any, applies **only** to the behavioral overlay:

```text
Natal baseline + accumulated behavior → current behavioral state
```

No meaningful delta → **no LLM**. Calendar month is not a trigger.

### Four rebuild triggers (only)

1. **Birth data changed** → rebuild natal-dependent layers (Swiss + decode + CE baseline).
2. **Semantic engine / canon version incompatible** with the stored artifact → **controlled migration**, not rebuild on every deploy / prompt tweak.
3. **Behavior accumulated a meaningful delta** → update **behavioral layer only**.
4. **Manual force rebuild** → DEV/ADMIN tool, engineering ledger.

**Not triggers:** `GET /profile`, login, app open, new calendar day, prompt/expression version bump, fingerprint churn that is not a compatibility break.

### Version axes (invalidation keys)

A polish of voice is not a new person and not new natal meaning. Binding snapshot identity to prompt versions turns every editorial pass into a mass rebuild and a new bill.

| Axis | What it versions | Invalidates |
|------|------------------|-------------|
| `calc_version` | Swiss/JPL, houses, aspects geometry | NatalFacts and everything downstream |
| `semantic_version` | IL / Composition / Selection meaning | CanonicalMeaning, SelectedThemes, Character baseline |
| `expression_version` | prompt, voice, LLM presentation | ProfileExpression **only**, and **not immediately** |
| `behavior_version` | accumulated user signals | BehavioralOverlay only, and only if meaningful delta |

`profile_hash` / decode cache key = identity + birth + `calc_version` + `semantic_version`. Never `expression_version`.

### Stored Profile layers

```text
NatalFacts → CanonicalMeaning → SelectedThemes → ProfileExpression → BehavioralOverlay
```

| Layer | Built from | Rebuild when |
|-------|------------|--------------|
| NatalFacts | calc | `calc_version` or birth data |
| CanonicalMeaning | IL-2 / natal theses | `semantic_version` or NatalFacts |
| SelectedThemes | IL-3 rank + Selection | `semantic_version` or CanonicalMeaning |
| ProfileExpression | K3 synthesis over SelectedThemes | `expression_version` (optional, deferred) or SelectedThemes |
| BehavioralOverlay | natal baseline + signals | `behavior_version` / meaningful delta |

An `expression_version` bump may rewrite prose later. It must **not** recompute natal, IL-2, or Character baseline.

### Selection (do not mechanical-cut Profile)

Today: IL-3 ranks candidates; the **system** picks primary/supporting; LLM **only expresses**. That cut can be strict now (Today already sends 1 IL line; next is to stop dumping `dropped` refusals and non-IL bags into the prompt as if they were meaning).

Profile: **do not** hard-cap at 5–8 themes until an audit shows which of the ~24 IL-3 themes Kimi actually uses, which it ignores, and which compete. Then Selection Engine must reproduce that choice deterministically. A blind cut can drop what makes the K3 portrait good.

Payload facts: [audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md](./audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md).

---

## 3. Today

**Cost model / persist key:**

```text
Personal Today  =  1 artifact × user × local_date × semantic_version
Global Day      =  1 artifact × date × locale/version     (not × user)
```

Re-open 20 times → **0 LLM**, same persisted artifact 20 times.

I0 already: identical inputs + identical rule versions → identical day meaning; GET does not call LLM; two people in one timezone + one rule version share **one Global Day** ([TODAY_CONTENT_PIPELINE_V1.md](./today/TODAY_CONTENT_PIPELINE_V1.md) I0).

LLM formulates **after** calc → IL-2 cells → IL-3 rank → **system Selection** → expression. It does not parse raw transits and does not choose the day's themes. Library coverage `transit_to_natal` 245 + `transit_through_house` 84 is cartesian math, not a prompt dump ([LIBRARY_SCALE_V1.md](./astrology/LIBRARY_SCALE_V1.md)).

**Pre-release:** do not lock testers out of force rebuild. Force = engineering ledger. Do not treat test regenerations as MAU economics.

---

## 4. Tarot (product ladder; not this implementation)

Tarot is **user-triggered generative compute**, not core daily meaning.

| Tier | Product | Compute |
|------|---------|---------|
| Free | Card of the day / very short base reading | hard budget |
| Paid | Full spread (several cards, question context, personal composition) | strong model OK — cost sits on the transaction (Co-Star-like paid spreads) |

Do **not** cheapen paid Tarot by a few cents of model downgrade. Monetize the compute.

Checkout/paywall remains a separate launch wave in [TODAYFLOW_PRODUCT_CANON_UNIFIED.md](./TODAYFLOW_PRODUCT_CANON_UNIFIED.md). This file locks the **compute split**, not Stripe.

---

## 5. Compatibility (product ladder; not Layer 5 recipes)

Most of Aries×Taurus, Moon×Moon, Venus×Mars, aspect×aspect, house interaction is **already IL-2 composition** of the 38-atom core. Do not open Layer 5 pair recipes until composition shows a named hole ([IL2_COMPOSITION_RULES_V1.md](./astrology/IL2_COMPOSITION_RULES_V1.md)).

| Tier | Path | Marginal LLM |
|------|------|----------------|
| Basic | deterministic calc + canonical library + prepared expression blocks | ≈ 0 |
| Personal report (paid) | two real charts + composition + Character context + synthesis | yes, monetized |

Free: «что между нами происходит». Paid: «почему именно у нас это так и что с этим делать».

---

## 6. Four knowledge domains (do not mix)

| Domain | Status | Not |
|--------|--------|-----|
| Astrology Knowledge Core | **frozen** 38 atoms / 616 IL-2 cells | do not expand for Profile/Today/Compat |
| Tarot Knowledge Core | `TAROT_CARD_BASE_V1` lookup, not IL-grade researched core | not astrology atoms |
| Numerology Knowledge Core | `NUMBER_BASE_V1` similarly | not astrology atoms |
| User Knowledge / PIM | facts about **this person** | not “what the sky means” |

Practices are an **intervention/action catalog** (goal, duration, intensity, context, modality) for Selection — not a fifth astrology atom family.

---

## 7. Runtime gaps (implementation debt)

| Desired | Current (2026-08-25) |
|---------|----------------------|
| Prompt not a Profile rebuild | **This pass:** `profile_hash` is identity+calc+semantic; snapshot fallback across old prompt-keyed rows; Natal Decode GET matches semantic + legacy polish fingerprints |
| Global Day 1× date × locale | I0 still runs Global **narrative LLM per user** |
| Personal key = semantic_version | fat day-story fingerprint (mood, goals, sky_digest, prompt_version, …) |
| GET miss → 0 LLM | GET does not LLM, but miss **enqueues prewarm** |
| Production prewarm off until release | cron still prewarms real testers (budgeted; `@example.com` excluded) |
| Behavioral-delta gate | `living` refreshes on GET; no “enough new signal → LLM” gate |
| Profile selection | full IL-3 bag until **usage audit**; not a 5–8 cut |
| Today Selection before LLM | 1 IL line already; `dropped` + dramaturgy still in prompt |
| Tarot free/paid compute gate | LLM on essentially every successful draw |
| Basic Compat ≈ 0 LLM | template first; registered/paid still async LLM enrichment |

Router cost guard stays. It does not replace this lifecycle.

## 8. Work order (locked)

Main savings **without** touching Kimi 3 quality on Profile:

1. **Profile invalidation** (this pass: prompt ≠ snapshot key)
2. **Shared Global Day**
3. **Personal Day lifecycle** (`user × local_date × semantic_version`; reopen = 0 LLM)
4. **Profile selection** (after “which of 24 does Kimi use” audit)
5. Behavioral overlay
6. Tarot economics
7. Compatibility economics

## 9. This pass does not do

- Public JSON · IL lemma / `active` · pair catalog
- Shared Global Day store · Tarot/Compat paywall code
- Mechanical 5–8 theme cut · K3 quality cut · Knowledge Core expand
- Relevance engine as a new meaning SoT

---

## Changelog

- **1.1 (2026-08-25)** — Version axes. Prompt is not an invalidation key. Layered Profile store. Work order locked. Profile hash + Natal Decode lookup implemented to that rule.
- **1.0 (2026-08-25)** — Lifecycle + artifact economics SoT. Four Profile triggers. Today persist keys. Three ledgers. Knowledge Core not expanded. Payload audit named as next meaning/cost cut.
