# House Canon Grammar V1

**Date:** 2026-08-22  
**Status:** LOCKED (grammar + slot semantics). Dry-run lemmas are **not** locked values. **Not** fill. **Not** JSON. **Not** schema. **Not** objects. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.44. Territory: [MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md](./MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md). Planet grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Sign grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) · [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file answers: **which properties of a house does the Composition Engine need in order to route an already-known planet function into a chart arena?**

It does not answer “what 4th-house person.” It is not a life-area essay. It is not an event forecast. It is not a copy of Sign Canon.

1.3.89 already closed contemporary house territory. Do not reopen house research. Canon is allowed — and expected — to be **narrower** than that territory.

---

## Architecture impact

- **SoT before:** 1.3.89 locked include/secondary/exclude. Arena ≠ people-dump was named, not split. Risk: two slots because Signs had two; copy `planet.canon.domains`; equate House 1 with ASC; paste Lilly `domain`.
- **SoT after:** House generative role is **arena** (where), not manner (how) and not function (what). **One required slot:** `arena`. Classification (angular / succedent / cadent) and natural-sign identity stay stored fact, not operators. People-dumps and event recipes stay in territory. Contrasting dry-runs check the grammar; values wait for fill. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.44 · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated as grammar source: Lilly CA I.7 prose; Foundation §2.3; `1st = Aries`; `1st = ASC`; planet `domains` copy; 12 personality packs.

---

## 0. Question this grammar is allowed to answer

```text
Planet  =  what the function is
Sign    =  how that function is done
House   =  where it is routed
Aspect  =  how two functions relate  (already: interaction)
```

Only this:

> Where / in which sphere does an already-known planet function show up?

If a proposed slot does not change PlanetInHouse constructions, it is surplus. Signs got two slots because `excess` survived the deletion test. Houses do not inherit that count.

---

## 1. Generative role (locked)

| Layer | Job | Not the job |
|-------|-----|-------------|
| **Planet Canon** | Function semantics (`core_function` · `drive` · `domains` …) | Costume, sun-sign portrait |
| **Sign Canon** | Manner semantics — how that function is carried | A second planet; a person-type |
| **House Canon** | Arena / routing — where that function lands in this chart | Sign manner; planet function; an angle; a person |
| **Aspect Canon** | Relation operator (`friction` · `flow`) | Pair essays |

```text
Moon.core_function(feel / respond / protect)  ×  4th.arena(home / family / roots / private-base)
  →  feeling/protecting routed into home / family / private-base
```

The planet still feels. The house does not become Cancer, Moon, or “you will buy a house.” LLM (IL-4) formulates the frame. It does not choose what the 4th is.

### 1.1 House.arena ≠ planet.domains (locked)

They both sound like “where.” They do different work.

| Slot | Question | Example (Moon) |
|------|----------|----------------|
| **planet.canon.domains** | Where is this function semantically about, by itself? | emotions · needs · security · the-familiar |
| **house.canon.arena** | Where does this chart place that function as a life sphere? | 4th: home · family · roots · private-base |

Planet domains travel with the planet into every house. House arena is the construction’s chart location. Do **not** replace planet.domains with house.arena. Do **not** copy house.arena into planet.domains. Do **not** name the house slot `domains` — the collision would hide the two jobs.

Routing (named, not implemented): apply `planet.core_function` **into** `house.arena`. Intersection with planet.domains is a later composition concern, not a second house slot.

---

## 2. Locked slots

One. Not two. Not six.

| Slot | What it means | Why the engine needs it |
|------|----------------|-------------------------|
| **arena** | Chart sphere the planet function is routed into (place lemmas) | Distinguishes Moon×4th from Moon×10th; same pack routes Mars×4th and Venus×4th |

Each slot is a short list of **lemmas**, not a sentence, not a Today line, not a house-cookbook paragraph.

### 2.1 Deletion test (locked)

> If this slot is removed, does the engine lose a real difference between PlanetInHouse constructions?

| Slot | Delete it? | Result |
|------|------------|--------|
| **arena** | Engine cannot tell Moon×4th from Moon×10th. Lilly prose and natural-sign identity are not substitutes. | **Required** |
| excess / overdone-house | Planet.distorted already covers the function gone wrong (Moon clinging). “Too much 4th” is not required to route Moon into home. Signs needed excess because manner-overdone ≠ planet.distorted. Houses do not inherit that. | **Surplus** |
| people | Mother / father / spouse / co-workers as stems describe persons, not arenas. Parent-gender is a school split (1.3.89). | **Surplus** |
| activities / events | “You will buy a house” / planet-in-house recipes. Prediction, not routing. | **Surplus** |
| resources as own slot | 2nd/8th resource lemmas belong *inside* arena (`personal-resources` · `shared-resources`) if they are the sphere. | **Surplus** |
| private/public as own slot | Recoverable from arena lemmas (`private-base` vs `public-role`). | **Surplus** |
| manner | Sign job. 4th is not Cancer `close / protective-of-bond`. | **Surplus** |
| core_function / drive / needs | Planet job. 4th is not Moon `feel / protect / safety`. | **Surplus** |
| domains (copy of planet slot) | Different job; same name would merge them. | **Surplus** |
| angular / succedent / cadent | Already stored classification. Not an operator (`angular` → initiating). | **Surplus** |
| natural sign / natural planet | Identity dump. `4th = Cancer / Moon` is forbidden. | **Surplus** |
| angle identity | `1st = ASC` · `10th = MC`. Cusp is related; object is not the angle. KC-H-ASC≠1. | **Surplus** |

STOP at one slot. Do not add a second because Sign Canon has `excess`.

### 2.2 Natural-house collision (locked)

Do not restate the natural planet’s `core_function` or the natural sign’s `manner` as the house’s `arena`.

| House | Not arena |
|-------|-----------|
| 1st | ASC as the house · Aries `initiating` · Mars `act` / `assert` |
| 2nd | Taurus manner · Venus `value` / `attract` |
| 3rd | Gemini manner · Mercury `think` / `communicate` as the house’s verb |
| 4th | Cancer manner · Moon `feel` / `protect` · IC-as-the-house |
| 5th | Leo manner · Sun `shine` |
| 6th | Virgo manner · Mercury `discern` as the house’s verb |
| 7th | Libra manner · Venus `relate` as the house’s verb · DSC-as-the-house |
| 8th | Scorpio manner · Pluto `transform` |
| 9th | Sagittarius manner · Jupiter `expand` / `believe` |
| 10th | Capricorn manner · Saturn `limit` / `mature` · MC-as-the-house |
| 11th | Aquarius manner · Uranus `disrupt` |
| 12th | Pisces manner · Neptune `dissolve` |

`home` as 4th arena is allowed. `feel` as 4th arena is not.

### 2.3 Guards (locked)

- **House ≠ Sign.** 2nd does not receive Taurus semantics. 6th does not receive Virgo.
- **House ≠ Angle.** 1st ≠ ASC. 10th ≠ MC.
- **House ≠ personality.** The house does not describe the person.
- **House ≠ event prediction.** It routes a function into a semantic arena.

---

## 3. Territory fitness (hypothesis, not Canon)

1.3.89 families are **input**. This cut is a grammar check. Fill (next) may drop more. It must not add families that are not on that map.

| Bucket | Goes to | Test |
|--------|---------|------|
| **arena-fit** | Candidate `arena` | Can it locate Venus.value, Mars.act, Moon.feel, … without becoming a person, a sign, or an event? |
| **people dump** | Stays in territory; **out of generative Canon** | Mother / father / spouse / children-as-persons as the stem |
| **sign / planet identity** | **Out** | 4th = Cancer / Moon |
| **angle identity** | **Out** | 1st = ASC |
| **event / cookbook** | **Out** | Planet-in-house recipes |

Canon **must not** try to place every locked family. Expected leftovers include: parent-gender · vitality · pets · hospitals-prisons-monasteries as place-lists · karma-as-the-only-stem · sex as Astrology.com mass shorthand if intimacy/shared-resources already locates 8th.

### 3.1 Cut (illustrative — not fill)

Arena-fit uses include **or** secondary from 1.3.89. Secondary is allowed as arena-candidate (4th `private-base`). People-include stays out (`father` / `mother`).

| House | Arena-fit (candidate) | Out of generative Canon |
|-------|----------------------|-------------------------|
| 1st | self-presentation · appearance · first-impression · starting-in-the-world | ASC · Aries/Mars · vitality-as-Sun · head anatomy |
| 2nd | possessions · money · personal-resources · self-worth-as-having | Taurus/Venus · spending essays · body-as-resource as anatomy |
| 3rd | everyday-communication · siblings-neighbors · short-range · local-learning | Gemini/Mercury · 9th far-travel |
| 4th | home · family · roots · private-base | Cancer/Moon · IC · father-only · mother-only · Lilly endings |
| 5th | play · creativity · romance · pleasure | Leo/Sun · 7th partnership · children-as-person-essay |
| 6th | daily-work · routine · health-maintenance · service | Virgo/Mercury · 10th career · hypochondria-as-stem |
| 7th | partnership · one-to-one · contracts · the-other | Libra/Venus · DSC · 5th romance · 11th groups |
| 8th | shared-resources · crisis · intimacy · endings | Scorpio/Pluto · 12th retreat · sex as the only stem |
| 9th | philosophy · far-travel · higher-learning · belief | Sagittarius/Jupiter · 3rd near-facts |
| 10th | career · public-role · reputation · calling | Capricorn/Saturn · MC · father/mother as stem · 6th job |
| 11th | friends · groups · hopes · community | Aquarius/Uranus · 7th one-to-one |
| 12th | hidden · retreat · behind-the-scenes | Pisces/Neptune · 8th crisis · karma-as-only-stem · institution list as the stem |

4th `home / family / roots / private-base` are recognizable. They are **not** Moon.domains (`emotions / needs / security`). That is the point of the cut.

---

## 4. How a pack is used (not implemented this pass)

```text
planet.core_function (+ drive)
  ×  sign.manner            (how)
  ×  house.arena            (where)
  →  function done this way, routed into this sphere
  ×  aspect.interaction
  →  IL-4 formulates
```

Do not store `Moon in 4th` essays.

`angular` · natural sign · Lilly `domain` are not inputs to this transform.

---

## 5. Dry-run (not locked)

Input = planet `core_function` from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md) + §3 arena-fit. Output = grammar check. **Fill later.** Do not copy these rows into objects.

The historical failure is Moon × 4th. Discrimination and composability must also hold, or this is a 4th-house special case, not a grammar.

### Moon × 4th

```text
planet:   feel · respond · protect
arena:    home · family · roots · private-base
frame:    feeling/protecting routed into home / family / private-base
out:      Lilly father/land/endings · Cancer · Moon=4th · “Moon in 4th” essay
not:      planet.domains (emotions · needs · security) as the house slot
```

### Moon × 10th

```text
planet:   feel · respond · protect
arena:    career · public-role · reputation · calling
frame:    feeling/protecting routed into public role / career
out:      MC · Capricorn · Saturn.limit as the house · 6th daily-job
```

Same planet as Moon × 4th. Difference is **only** house.arena. Grammar holds if those two frames cannot be swapped.

### Mars × 4th

```text
planet:   act · pursue · assert
arena:    home · family · roots · private-base
frame:    action routed into home / family / private-base
out:      “defend the family” as a Mars-keyed 4th lemma · Cancer
```

### Venus × 4th

```text
planet:   attract · value · relate
arena:    home · family · roots · private-base
frame:    valuing/relating routed into home / family / private-base
out:      “domestic Venus” as a Venus-keyed 4th lemma
```

Moon × 4th, Mars × 4th, and Venus × 4th share **one** 4th pack. If the 4th needed planet-specific lemmas, the grammar fails.

### Venus × 5th

```text
planet:   attract · value · relate
arena:    play · creativity · romance · pleasure
frame:    valuing/relating routed into play / romance / making
out:      7th partnership/contract · Leo
```

### Venus × 7th

```text
planet:   attract · value · relate
arena:    partnership · one-to-one · contracts · the-other
frame:    valuing/relating routed into one-to-one / contract
out:      5th romance-as-play · DSC
```

Same planet as Venus × 5th. Difference is play/romance vs partnership/contract.

### Mercury × 3rd

```text
planet:   think · communicate · learn
arena:    everyday-communication · siblings-neighbors · short-range · local-learning
frame:    thought/speech routed into the near / everyday
out:      Gemini · Mercury as a second verb · 9th far
```

### Mercury × 9th

```text
planet:   think · communicate · learn
arena:    philosophy · far-travel · higher-learning · belief
frame:    thought/speech routed into the far / higher
out:      Sagittarius · Jupiter.believe as the house · 3rd near
```

### Saturn × 10th

```text
planet:   limit · structure · mature
arena:    career · public-role · reputation · calling
frame:    limiting/structuring routed into public role / career
out:      Capricorn manner · MC · `limit` as the 10th’s verb
```

### 5.1 Grammar check

| Test | Result |
|------|--------|
| Moon×4th ≠ Moon×10th | yes — home/private-base vs career/public-role |
| Moon×4th, Mars×4th, Venus×4th share one 4th pack | yes — no planet-keyed house lemmas |
| Venus×5th ≠ Venus×7th | yes — play/romance vs partnership/contract |
| Mercury×3rd ≠ Mercury×9th | yes — near/everyday vs far/higher |
| No construction used `angular` or `1st = Aries` as operator | yes |
| No construction copied planet.core_function or planet.domains into house.arena | yes |
| No construction used Cancer/Capricorn manner as the house | yes |
| One slot was enough | yes — excess/people/events failed the deletion test |
| Dropped families still recognizable as territory | yes — parent-gender, institution lists, karma-as-stem stay out |

---

## 6. This pass does not do

- Lock dry-run lemmas as Canon values
- Fill twelve houses · schema · objects · `active`
- Repeat 1.3.88 smoke-test (needs fill + storage first)
- Repair Moon × 4th PARTIAL by writing arena onto catalog objects
- Aspect / ASC/MC maps
- Sign pack edits · books · CORE · Co–Star ingest
- Houlding *The Houses* · Lilly overwrite

**Next named:** House Canon fill — **done 1.3.91** ([HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md)). House Canon storage/materialization — **done 1.3.92.** Planet × House smoke — **done 1.3.93.** Mainstream Aspect Semantic Map — **done 1.3.94.** Aspect Canon grammar — **done 1.3.95.** Aspect Canon fill — **done 1.3.96.** Aspect Canon storage/materialization — **done 1.3.97.** Stored Planet × Aspect smoke — **done 1.3.98.** **STOP Aspects.** Next = **ASC/MC**. Then **STOP Houses** after PASS.

---

## Changelog

- **1.2 (2026-08-22)** — Aspect Canon grammar locked 1.3.95. Grammar unchanged. Next = Aspect Canon fill.
- **1.1 (2026-08-22)** — Fill locked 1.3.91. Grammar unchanged. Dry-run lemmas remain illustrative; locked values live in HOUSE_CANON_V1.
- **1.0 (2026-08-22)** — 1.3.90. House = arena (where). One slot (`arena`). planet.domains ≠ house.arena. Deletion test drops excess/people/events. Dry-run only. Grammar before fill.
