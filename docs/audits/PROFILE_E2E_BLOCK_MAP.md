# Profile E2E — Block Map (current V2 + target gaps)

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md)  
**Passport template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**life_spheres passport:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md)  
**Projector spec:** [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md)  
**Date:** 2026-07-21  
**Surface:** `ProfileV2SystemScreen` + QuickMap builders · PR-4 boundaries

> Rule: **no full passport → no block.** Rows below describe **current code reality** unless Gap vs target says otherwise.
>
> Defects on this map are **architectural** (`GENERATION_GATE`, `UI_GATE`, …). Do not label gaps as «модель выдумала».

Legend tier: `trial` ≈ full depth during trial · `free` · `sub` (depth) · `calc` = deterministic always when facts allow.

---

## Current production blocks

| Block | Зачем (now) | User question | Sources | Calc | Interp | Prompt | Snapshot / field | Appear when | Tier now | Kitchen only | Gap vs target |
|-------|-------------|---------------|---------|------|--------|--------|------------------|-------------|----------|--------------|---------------|
| Hero name / pills | Identify person | Who is this? | person, astro anchors | signs labels | — | — | person, frameworkAnchors | always if profile route | trial/free | — | OK |
| Hero quote | Core vibe | Who am I in essence? | contract or taxonomy intro | — | synthesis | identity | `identity_core` / header.intro | contract ready / forming message | trial/free | — | Must not show fake headline if forming |
| Completeness / birth CTA | Unlock depth | What’s missing? | missing_fields, time_unknown | — | — | — | missing_fields | incomplete | all | — | Need «what opens / why» Voice §0 |
| Evidence aside | Honesty | Why this portrait? | source_depth client mirror | closed days | honesty lines | — | living signals, confidence | always | all | % KPI removed PR-4 | Align client depth with backend |
| Identity · archetype | Stable label | What’s my archetype? | baseline + contract | archetype_seed | display label | — | baseline, identity | ready | calc | — | OK as calc |
| Identity · astro signatures | Facts | What’s my natal base? | natal preview / core astro | ephemeris | role only if card body | — | positions | anchors exist | calc | full chart coords | Progressive disclosure incomplete |
| Character · strengthens | Strengths | What strengthens me? | contract / taxonomy slots | — | LLM + FE merge | identity | strengths | non-empty | trial/free | — | Dedup vs growth |
| Character · drains | Limits | What drains me? | growth_zones / taxonomy | — | LLM + FE | identity | growth_zones | non-empty | trial/free | — | Naming «drains» vs growth |
| Character · helps | Supports | What helps? | contract helps | — | patterns step | patterns | helps | non-empty | trial/free | — | No CUM day recs (PR-4) |
| Character · decisions | Decision style | How do I decide? | contract | — | styles | styles | decision_style | non-empty | trial/free | — | OK |
| Character · patterns | Repeats | What repeats? | recurring_patterns | — | patterns LLM | patterns | recurring_patterns | only with longitudinal (gate shipped) | trial growth / sub | — | UI must not show confirmed repeats without evidence |
| Character · forming lead | Framework | How does this form? | taxonomy / who | — | knowledge | — | — | frameworkLead | trial/free | — | May duplicate identity |
| Direction · mission | Life direction | What’s my direction? | life_mission | — | patterns | patterns | life_mission | non-empty | trial/free | — | Own passport TBD; accidental patterns packaging |
| Direction · spheres | How base traits show in life areas | How do my foundations show in key spheres? | **Target:** deterministic projection from natal + identity + styles | natal signs/planets; houses when time allows | **Target:** code projector (`life_spheres_projector_v0.1`) | legacy `profile.spheres.v1` **not** content authority | `life_spheres` (partial OK) | `spheres_projection_allowed` (natal-presence); **independent of patterns** | calc / trial/free presence | rule ids, fingerprint | **Current debt:** funnel stops after patterns skip/fail (`GENERATION_GATE` mis-applied to spheres); dual source LLM + FE DEFAULTS/houses. **Target locked** by passport + projector spec — not an open product gap |
| Sources · natal strip | Natal as source | What’s the natal basis? | frameworkAnchors + cards | chart | card body only | — | natal preview | deep prop | calc | wheel/houses behind portal | Target: visual + anchors + expand |
| Sources · portal deep | Full chart | Details? | natal API | full chart | editorial? | natal editorial paths | — | user expands | calc/sub depth | orbs, coords | Organize; not wall |
| Maps CTA | Exit to Tracking | How do I change over time? | — | — | — | — | — | always | nav | — | OK thin CTA |
| Forming banner | Honesty | Portrait not ready | status forming | — | — | — | status, forming_message | forming | all | — | OK |
| First-Today notice | Journey | Need first day? | firstTodayState | — | — | — | local | incomplete journey | all | — | Product name Today OK |

---

## Target blocks (not yet wired as full rows)

Must gain full 15-answer passports before implementation:

| Block | User question | Appear when | Tier |
|-------|---------------|-------------|------|
| Emotional needs | How do I need to feel safe? | evidence in contract/ruleset | free/sub |
| Communication style | How do I relate in talk? | from relationship_style or dedicated claim | free/sub |
| Inner tension | What’s the core conflict? | non-duplicate claim | free/sub |
| Under pressure | How do I act under load? | not birth-only invention | sub depth |
| Recovery | How do I restore? | evidence | free/sub |
| Numerology basis | What do my numbers contribute? | numbers calculated | calc always |
| Confirmed observations | What repeats in my days? | longitudinal only | trial growth / sub |
| Missing-time explainer | What ASC/houses unlock? | time_unknown | all |
| Missing-place explainer | What geo unlocks? | no coords | all |

---

## Missing-data matrix (Profile)

| Missing | Still show | Omit / limit | CTA shape |
|---------|------------|--------------|-----------|
| birth date | journal-like nothing on Profile natal | natal, numerology, personal compat | get date — what opens |
| birth time | planets by sign, numerology, archetypes | ASC, MC, houses, time-sensitive | time — ASC/houses why |
| birth place | same as time for horizon | ASC/MC/houses accuracy | place — horizon why |
| history / living | full static portrait **including** natal-presence `life_spheres` when projector gate holds | recurring_patterns, living_changes, longitudinal evidence | use Today — patterns unlock (spheres must **not** wait on this) |
| subscription after trial | complete static level | deeper why/how/longitudinal application | deepen understanding — not chopped cards |

---

## Trial / free / subscription (content contracts — draft)

Per [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](../UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md): **three separate contracts**, not trimmed Premium.

| Layer | Trial | Free after trial | Subscription |
|-------|-------|------------------|--------------|
| Static who-you-are | Full available | Full available | Full + deeper links |
| Natal organized | Yes | Yes | + richer interpretation (not wall) |
| Patterns | Only with evidence | Only with evidence | Longitudinal + confirm/reject |
| Application | Light | Limited refresh | direct_answer / do / avoid / how (Content Canon premium) |
| Memory | Starts accumulating | Limited history use | Long history + contradiction explain |

Concrete trial end condition: **TBD product+tech** (daily return + min meaningful evidence) — not arbitrary screen count.

---

## FE projection notes

`buildProfileQuickMapViewModel` merges:

1. `profile_contract_v1`  
2. Profile V0 taxonomy / zodiac knowledge slots  
3. Optional CUM themes  

→ Risk of **projection degradation** and duplicate meanings across Character cards. Must be traced in sample pack UI column.
