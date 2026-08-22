# House Canon V1

**Date:** 2026-08-22  
**Status:** LOCKED (twelve house packs + provenance + five gates). **Not** JSON. **Not** schema. **Not** objects. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.45. Territory: [MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md](./MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md). Grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) · [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file is the product arena of the twelve houses. 1.3.89 is territory. 1.3.90 is grammar. 1.3.91 is synthesis **with origin control**. Grammar dry-run lemmas are not inherited automatically.

```text
Mainstream territory → arena synthesis → five gates → cross-planet dry-run → lock
```

No new literature. No natural-sign arithmetic. No schema until this dry-run stands. One slot only (`arena`).

---

## Architecture impact

- **SoT before:** grammar locked one slot; dry-run lemmas were illustrative. Risk: dump all 1.3.89 families, copy Cancer/Moon into 4th, or write “seek emotional security at home.”
- **SoT after:** each Canon atom is `direct` / `direct-secondary` / `derived` from that house’s locked 1.3.89 families. Five gates pass. Unused families stay in territory. Catalog untouched. Schema still later.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.45 · grammar next-pointer · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated: treating 1.3.90 dry-run wording as locked values; filling every territory family for symmetry.

---

## 0. Origin rule (locked)

Same tags as Planet / Sign Canon fill.

| Origin | Means | Does not mean |
|--------|-------|----------------|
| **direct** | Normalization of a 1.3.89 **include** family (same concept, shorter lemma) | Copied vendor sentence |
| **direct-secondary** | Normalization of a 1.3.89 **secondary** family | A second stem that displaces include |
| **derived** | TodayFlow inference from **two or more** locked families of **this** house | A new astrology; a school package; Google |

`derived` is not weaker. It marks where our model starts.

**Reject** if: not in that house’s 1.3.89 families even as parents; is a hidden interpretation of a planet; copies the natural sign’s `manner` or natural planet’s `core_function`; uses angularity as proof; equates the house with an angle; or is user-facing copy.

Pipeline per atom:

```text
lemma → direct | direct-secondary | derived → parent family/families → five gates → keep / rewrite / drop
```

---

## 1. Five gates (locked)

1. **Origin control** — every `arena` atom is a 1.3.89 include or secondary on that house, or derived only from those families. No classification arithmetic. No fourth panel. No books.
2. **Routing fit** — the lemma must naturally receive **several** planet functions, not only one convenient pair. 4th arena must work on Moon, Mars, and Venus **without planet-keyed house lemmas**.
3. **Collision control** — the lemma is a place, not a verb-planet, not a sign manner, not an angle ([grammar §2.2](./HOUSE_CANON_GRAMMAR_V1.md)).
4. **Discrimination** — adjacent / contrast houses must give a distinguishable arena of the **same** planet. Moon × 4th must not be interchangeable with Moon × 10th. Locked pairs: **2↔8 · 4↔10 · 5↔7 · 6↔10**. Also keep 3↔9 · 7↔11 · 8↔12 · 1↔10.
5. **Destination noun** — arena is a **semantic destination**, not a hidden interpretation. `home / family / roots / private-base` passes. `seek emotional security at home` fails: the house has started interpreting Moon.

Coverage is **not** “every 1.3.89 family placed.” Expected: **3–4** arena atoms per house. Leftover families stay recognizable as territory.

---

## 2. Locked packs

Parents use 1.3.89 family names. Grammar dry-run rejects are listed once in §4.

Planet `core_function` atoms used in dry-runs are from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md): Moon `feel · respond · protect` · Mars `act · pursue · assert` · Venus `attract · value · relate` · Mercury `think · communicate · learn`.

### 1st House

Territory used: self-presentation / persona · appearance / body-as-meeting · first-impression.  
Left in territory: starting-in-the-world · vitality · instinctive-reaction · independence.

```text
arena:  self-presentation · appearance · first-impression
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| self-presentation | arena | direct | self-presentation / persona |
| appearance | arena | direct | appearance / body-as-meeting |
| first-impression | arena | direct | first-impression |

**Collision:** not ASC · not Aries `initiating` · not Mars `act`. `starting-in-the-world` dropped — verb-like and too close to angular arithmetic.  
**Noun:** destinations of meeting the world, not “I start things.”  
**Routing:** Moon feels at the meeting-face; Mars acts there; Venus values there.

### 2nd House

Territory used: possessions / belongings · money / income · personal-resources.  
Left in territory: self-worth / values · security-through-having · talents-as-assets · sensual-material · body-as-resource.

```text
arena:  possessions · money · personal-resources
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| possessions | arena | direct | possessions / belongings |
| money | arena | direct | money / income |
| personal-resources | arena | direct | personal-resources |

**Collision:** not Taurus manner · not Venus `value`. `self-worth` dropped — interpretive (“I feel worthy”), not a destination.  
**Vs 8th:** personal holding, not shared-resources.

### 3rd House

Territory used: everyday-communication · siblings / neighbors · local-learning / facts.  
Left in territory: short-range-movement · writing-speaking · media-devices · elementary-schooling · curiosity-about-near.

```text
arena:  everyday-communication · siblings-neighbors · local-learning
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| everyday-communication | arena | direct | everyday-communication |
| siblings-neighbors | arena | direct | siblings / neighbors |
| local-learning | arena | direct | local-learning / facts |

**Collision:** not Gemini manner · not Mercury `think` as the house’s verb.  
**Vs 9th:** near / everyday, not far / higher.  
**Noun:** the near sphere, not “Mercury talks a lot.”

### 4th House

Territory used: home / hearth · family · roots / origins · private-base / inner-foundation.  
Left in territory: childhood-conditioning · ancestry · real-estate / land · belonging / safety-of-base · father-only · mother-only.

```text
arena:  home · family · roots · private-base
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| home | arena | direct | home / hearth |
| family | arena | direct | family |
| roots | arena | direct | roots / origins |
| private-base | arena | direct | private-base / inner-foundation |

**Collision:** not Cancer manner · not Moon `feel` / `protect` · not IC. Parent-gender stays out.  
**Noun pass:** `home / family / roots / private-base`.  
**Noun fail (rejected):** `seek emotional security at home` — interprets Moon; pair-specific.  
**Vs 10th:** private base, not public role.

### 5th House

Territory used: play · creativity / making · romance / lovers-not-partners.  
Left in territory: pleasure / fun · children / creations · speculation / gambling · performance · hobbies.

```text
arena:  play · creativity · romance
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| play | arena | direct | play |
| creativity | arena | direct | creativity / making |
| romance | arena | direct | romance / lovers-not-partners |

**Collision:** not Leo manner · not Sun `shine`. Children-as-persons dropped. `pleasure` dropped — mood, not destination (overlaps play).  
**Vs 7th:** romance/play, not partnership/contract.

### 6th House

Territory used: daily-work / job-not-career · routine / chores · health-maintenance.  
Left in territory: service / helpfulness · co-workers / subordinates · nutrition / self-care · order / methods · pets.

```text
arena:  daily-work · routine · health-maintenance
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| daily-work | arena | direct | daily-work / job-not-career |
| routine | arena | direct | routine / chores |
| health-maintenance | arena | direct | health-maintenance |

**Collision:** not Virgo manner · not Mercury as the house’s verb. `service` dropped — smears 12th sacrifice and reads as identity.  
**Vs 10th:** the day’s job, not public career.

### 7th House

Territory used: partnership · one-to-one · contracts / negotiation.  
Left in territory: the-other / counterpart · marriage · open-opponents · counseling / mediation · business-partnership.

```text
arena:  partnership · one-to-one · contracts
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| partnership | arena | direct | partnership |
| one-to-one | arena | direct | one-to-one |
| contracts | arena | direct | contracts / negotiation |

**Collision:** not Libra manner · not Venus `relate` as the house’s verb · not DSC. `the-other` dropped — person-stem.  
**Vs 5th:** contract, not romance. **Vs 11th:** one person, not the group.

### 8th House

Territory used: shared-resources / others’-money · crisis / upheaval · intimacy / merging.  
Left in territory: endings / material-loss · inheritance / taxes · sexuality · death-and-rebirth · research / deep-probe.

```text
arena:  shared-resources · crisis · intimacy
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| shared-resources | arena | direct | shared-resources / others’-money |
| crisis | arena | direct | crisis / upheaval |
| intimacy | arena | direct | intimacy / merging |

**Collision:** not Scorpio manner · not Pluto `transform`. `endings` dropped — event-like; `sex` dropped — mass shorthand.  
**Vs 2nd:** shared, not personal. **Vs 12th:** crisis/merge, not hidden-retreat.

### 9th House

Territory used: philosophy / world-view · far-travel · higher-learning.  
Left in territory: belief / meaning-seeking · publishing · foreign-culture / language · law-and-judgment · spiritual-leaning.

```text
arena:  philosophy · far-travel · higher-learning
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| philosophy | arena | direct | philosophy / world-view |
| far-travel | arena | direct | far-travel |
| higher-learning | arena | direct | higher-learning |

**Collision:** not Sagittarius manner · not Jupiter `expand` / `believe`. `belief` dropped — restates Jupiter.  
**Vs 3rd:** far / higher, not near / everyday.

### 10th House

Territory used: career / profession · public-role / standing · reputation · calling / what-we-become.  
Left in territory: authority-figures · achievement / honors · responsibility · parental-public-image.

```text
arena:  career · public-role · reputation · calling
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| career | arena | direct | career / profession |
| public-role | arena | direct | public-role / standing |
| reputation | arena | direct | reputation |
| calling | arena | direct | calling / what-we-become |

**Collision:** not Capricorn manner · not Saturn `limit` · not MC. Parent-gender stays out.  
**Vs 6th:** public office / calling, not daily-work. **Vs 4th:** public, not private-base.

### 11th House

Territory used: friends / acquaintances · groups / organizations · community / the-collective.  
Left in territory: hopes / wishes · benefactors / teachers · humanitarian-cause · personal-goals-without-office.

```text
arena:  friends · groups · community
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| friends | arena | direct | friends / acquaintances |
| groups | arena | direct | groups / organizations |
| community | arena | direct | community / the-collective |

**Collision:** not Aquarius manner · not Uranus `disrupt`. `hopes` dropped — inner aim, not a destination.  
**Vs 7th:** the group, not one-to-one.

### 12th House

Territory used: hidden / below-the-surface · retreat / seclusion · behind-the-scenes.  
Left in territory: institutions-of-withdrawal · self-undoing · dreams · sacrifice · hospitals-prisons-monasteries as place-list · karma.

```text
arena:  hidden · retreat · behind-the-scenes
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| hidden | arena | direct | hidden / below-the-surface |
| retreat | arena | direct | retreat / seclusion |
| behind-the-scenes | arena | direct | behind-the-scenes |

**Collision:** not Pisces manner · not Neptune `dissolve`. Institution list stays out as the stem.  
**Vs 8th:** withdrawal / unbound, not crisis / shared-loss.

---

## 3. Cross-planet dry-run (locked as a check, not as pair essays)

Same 4th pack on three planets. Difference between Moon × 4th and Moon × 10th is **only** arena.

### Moon × 4th

```text
planet:   feel · respond · protect
arena:    home · family · roots · private-base
frame:    feeling/protecting routed into home / family / private-base
out:      seek-emotional-security-at-home · Cancer · Moon=4th · Lilly prose
```

### Moon × 10th

```text
planet:   feel · respond · protect
arena:    career · public-role · reputation · calling
frame:    feeling/protecting routed into public role / career
```

### Mars × 4th

```text
planet:   act · pursue · assert
arena:    home · family · roots · private-base
frame:    action routed into home / family / private-base
```

### Venus × 4th

```text
planet:   attract · value · relate
arena:    home · family · roots · private-base
frame:    valuing/relating routed into home / family / private-base
```

No Mars-keyed or Venus-keyed 4th lemma.

### Venus × 5th vs Venus × 7th

```text
5th:  play · creativity · romance      → valuing routed into play / romance
7th:  partnership · one-to-one · contracts → valuing routed into one-to-one / contract
```

### Mercury × 3rd vs Mercury × 9th

```text
3rd:  everyday-communication · siblings-neighbors · local-learning
9th:  philosophy · far-travel · higher-learning
```

### 3.1 Gate check

| Test | Result |
|------|--------|
| Origin | all arena atoms `direct` from that house’s include |
| Routing | Moon / Mars / Venus × 4th share one pack |
| Collision | no natural sign, ruler verb, or angle |
| Discrimination 4↔10 | home/private-base vs career/public-role |
| Discrimination 6↔10 | daily-work vs career/calling |
| Discrimination 5↔7 | romance/play vs partnership/contract |
| Discrimination 2↔8 | personal-resources vs shared-resources |
| Destination noun | 4th is places; `seek emotional security at home` rejected |
| Compression | leftover families remain in 1.3.89 territory |

---

## 4. This pass does not do

- JSON / schema / `object.canon` on houses / `active`
- Repair Moon × 4th PARTIAL by writing arena onto catalog objects
- Storage / materialization (next named, one pass)
- Aspect / ASC/MC maps
- Sign pack edits · books · CORE · Co–Star ingest
- Lilly overwrite · Houlding *Houses*
- Fill leftover territory families for symmetry
- A second house slot

**Next named:** House Canon storage / materialization — **done 1.3.92.** Planet × House smoke — **done 1.3.93.** Mainstream Aspect Semantic Map — **done 1.3.94.** Aspect Canon grammar — **done 1.3.95.** Aspect Canon fill — **done 1.3.96.** Aspect Canon storage/materialization — **done 1.3.97.** Stored Planet × Aspect smoke — **done 1.3.98.** **STOP Aspects.** Next = **ASC/MC**. Then **STOP Houses**. Do not enrich packs for richness. Next semantic owner after house smoke = Aspect.

---

## Changelog

- **1.0 (2026-08-22)** — 1.3.91. Twelve packs locked. Origin direct from 1.3.89 include. Five gates. Destination-noun test. Cross-planet dry-run. Unused families stay in territory.
