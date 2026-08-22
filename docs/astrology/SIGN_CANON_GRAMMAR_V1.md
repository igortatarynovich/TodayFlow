# Sign Canon Grammar V1

**Date:** 2026-08-21  
**Status:** LOCKED (grammar + slot semantics). Dry-run lemmas are **not** locked values. **Not** fill. **Not** JSON. **Not** schema. **Not** objects. **Not** House Canon. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.38. Territory: [MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md). Planet grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file answers: **which properties of a sign does the Composition Engine need in order to change the manner of an already-known planet function?**

It does not answer “what Capricorn person.” It is not a motivation profile. It is not a personality pack.

1.3.83 already closed contemporary sign territory. Do not reopen sign research. Canon is allowed — and expected — to be **narrower** than that territory.

---

## Architecture impact

- **SoT before:** 1.3.83 locked include/secondary/exclude. Trait ≠ manner was named, not split. Risk: copy planet’s six slots onto signs, or dump all families into Sign Canon.
- **SoT after:** Sign generative role is **manner** (how), not function (what). Two slots: `manner` · `excess`. Classification (`mode` · `element` · `orientation`) stays stored fact, not an operator. Directional/trait families stay in territory. Contrasting dry-runs check the grammar; values wait for fill. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.38 · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated as grammar source: Lilly QUALITY; `earth` → practical; planet six-slot copy; 12 personality packs.

---

## 0. Question this grammar is allowed to answer

```text
Planet  =  what the function is
Sign    =  how that function is done
House   =  where it is routed  (later)
Aspect  =  how two functions relate  (already: interaction)
```

Only this:

> Which sign properties does the engine need so it can modify the **manner** of a known planet function?

If a proposed slot does not change PlanetInSign constructions, it is surplus.

---

## 1. Generative role (locked)

| Layer | Job | Not the job |
|-------|-----|-------------|
| **Planet Canon** | Function semantics (`core_function` · `drive` · …) | Costume, sun-sign portrait |
| **Sign Canon** | Manner semantics — how that function is carried | A second planet; a person-type |
| **House Canon** | Arena / routing | Sign manner |
| **Aspect Canon** | Relation operator (`friction` · `flow`) | Pair essays |

```text
Venus.core_function(value / relate)  ×  Capricorn.manner(reserved / practical / structured)
  →  valuing done in a reserved, practical, structured way
```

The planet still values. The sign does not become “ambition.” LLM (IL-4) formulates the frame. It does not choose what Capricorn is.

Classification facts remain on the object. They do **not** generate manner (`earth` → practical, `cardinal` → initiating).

---

## 2. Locked slots

Two. Not six.

| Slot | What it means | Why the engine needs it |
|------|----------------|-------------------------|
| **manner** | How the planet function is carried (operator lemmas) | Distinguishes Venus×Capricorn from Venus×Scorpio |
| **excess** | That same manner overdone | Distinguishes sign-flavored distortion from planet.distorted |

Each slot is a short list of **lemmas**, not a sentence, not a Today line, not a sun-sign blurb.

### 2.1 Deletion test (locked)

> If this slot is removed, does the engine lose a real difference between PlanetInSign constructions?

| Slot | Delete it? | Result |
|------|------------|--------|
| **manner** | Engine cannot tell Venus×Capricorn from Venus×Scorpio. Classification triple is not a substitute. | **Required** |
| **excess** | Planet.distorted is still the *planet’s* problem (Venus indulgence / people-pleasing). Venus×Capricorn gone too far is withholding / worth-made-conditional — not those lemmas. | **Required** |
| drive / aim | Capricorn ambition would steal planet.drive. Venus in Capricorn is not “Venus wants achievement.” | **Surplus** |
| needs | Planet already has needs. Sign-as-need is a person profile. | **Surplus** |
| domains / arenas | House job. `home/family` · `humanitarian` · `beauty` as place are not manner. | **Surplus** |
| core_function | Sign is not a verb-planet. | **Surplus** |
| tempo / pace as own slot | Pace words belong *inside* manner (`initiating` · `slow-and-steady` · `mobile` · `enduring`) if they are how. ACM `merge_tempo` is machine, not Canon. | **Surplus** |
| register / tone as own slot | Warm / reserved / intense *are* manner. | **Surplus** |
| classification | Already stored. Not an operator. | **Surplus** |

### 2.2 `excess` is a branch of `manner`

Same relation as planet `constructive` / `distorted` to `core_function`. Excess Capricorn is still reserved/practical, overdone. Do not invent a second sign in `excess`.

Do not copy planet.distorted into sign.excess.

### 2.3 Domicile collision (locked)

Do not restated the ruling planet’s `core_function` as the sign’s `manner`.

| Sign | Not manner (planet already does this) |
|------|----------------------------------------|
| Aries | `act` / `assert` (Mars) |
| Taurus / Libra | `attract` / `value` (Venus) |
| Gemini / Virgo | `think` / `communicate` (Mercury) |
| Cancer | `feel` (Moon) |
| Leo | `shine` / `identify` (Sun) |
| Sagittarius | `expand` (Jupiter) |
| Capricorn | `limit` / `mature` as Saturn’s verb — `structured` as *how another planet proceeds* is allowed |
| Aquarius | `disrupt` (Uranus) |
| Pisces | `dissolve` (Neptune) |
| Scorpio | `intensify` / `transform` as Pluto’s verb — `intense` / `probing` as how is allowed |

---

## 3. Territory fitness (hypothesis, not Canon)

1.3.83 families are **input**. This cut is a grammar check. Fill (next) may drop more. It must not add families that are not on that map.

| Bucket | Goes to | Test |
|--------|---------|------|
| **operator-fit** | Candidate `manner` / `excess` | Can it modify Venus.value, Mars.act, Mercury.think, … without becoming a new aim? |
| **directional / trait** | Stays in territory; **out of generative Canon** | Answers “what this sign wants / is like as a person” |
| **arena / topic** | House-like; **out** | `home/family` · `humanitarian` · `beauty` as place |

Canon **must not** try to place every locked family. Expected leftovers include: ambition · achievement · purpose · humanitarian · home/family · beauty · leading-as-identity · luck · transformation-as-identity.

### 3.1 Cut (illustrative — not fill)

Operator-fit uses include **or** secondary from 1.3.83. Secondary is allowed as manner-candidate (Capricorn `practical` · `structure`). Trait include stays out (`ambition`).

| Sign | Operator-fit (candidate manner) | Out of generative Canon |
|------|--------------------------------|-------------------------|
| Aries | initiating / start · direct · headlong / impulsive | leading-as-identity · courage-as-character · competitive · willpower |
| Taurus | slow-and-steady · steadfast · sensual-as-how | security-as-aim · possession-as-character |
| Gemini | mobile · versatile · switching | communication-as-Mercury · wit-as-personality · curiosity-as-drive |
| Cancer | close · protective-of-bond · indirect | home/family-as-arena · safety-as-Moon-drive · nurturing-as-identity |
| Leo | central / displayed · warm · generous-as-how | pride-as-character · need-for-appreciation · leadership-as-identity |
| Virgo | precise · discerning · utilitarian | service-as-identity · helpful-as-virtue |
| Libra | balancing · other-regarding · tactful | beauty-as-arena · relating-as-Venus · fairness-as-identity |
| Scorpio | intense · probing · concentrated | will-as-character · transformation-as-Pluto · passion-as-planet-stem |
| Sagittarius | exploratory · free · far-ranging | meaning-seeking-as-drive · optimism-as-mood · luck |
| Capricorn | reserved · disciplined · practical · structured · enduring | ambition · achievement · purpose · recognition / status · responsibility-as-character |
| Aquarius | detached · unconventional | humanitarian-as-arena · individuality-as-identity · invention-as-Uranus |
| Pisces | permeable · imaginal · adaptive | compassion-as-character · spiritual-as-identity · sensitivity-as-Moon/Neptune-only |

Capricorn `ambition / achievement / purpose` are recognizable. They are **not** good operators on Venus.value. That is the point of the cut.

---

## 4. How a pack is used (not implemented this pass)

```text
planet.core_function (+ drive)
  ×  sign.manner
  →  function done this way
  ×  sign.excess     when the construction is on a distorted branch
  ×  house           later (route)
  ×  aspect.interaction
  →  IL-4 formulates
```

Do not store `Venus in Capricorn` essays.

`mode` · `element` · `orientation` are not inputs to this transform.

---

## 5. Dry-run (not locked)

Input = planet `core_function` from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md) + §3 operator-fit. Output = grammar check. **Fill later.** Do not copy these rows into objects.

Eight contrasting constructions. If the grammar only worked for Venus × Capricorn, it would be a special case, not a grammar.

### Venus × Capricorn

```text
planet:   value · relate
manner:   reserved · practical · structured
excess:   withholding · worth-made-conditional
frame:    valuing/relating done reservedly, practically, with structure
out:      ambition · achievement · purpose
```

### Mars × Aries

```text
planet:   act · pursue · assert
manner:   initiating · direct · headlong
excess:   premature charge · combative heat
frame:    action done by starting and going straight at it
out:      leading-as-identity · courage-as-character
```

Not `assert` as Aries manner (Mars already asserts).

### Mercury × Gemini

```text
planet:   think · communicate · learn
manner:   mobile · versatile · switching
excess:   scattered · staying-nowhere
frame:    thought/speech that changes channel and keeps moving
out:      communication as a second Mercury · wit-as-personality
```

### Moon × Cancer

```text
planet:   feel · respond · protect
manner:   close · protective-of-bond · indirect
excess:   clinging · sideways defense
frame:    feeling/protecting done through closeness and holding-on
out:      home/family as house arena · safety as Moon.drive
```

### Venus × Scorpio

```text
planet:   value · relate
manner:   intense · probing · concentrated
excess:   possessive · corrosive
frame:    valuing/relating that goes through rather than around
out:      transformation-as-identity · passion as Mars/Venus stem
```

Same planet as Venus × Capricorn. Difference is **only** sign.manner. Grammar holds if those two frames cannot be swapped.

### Jupiter × Sagittarius

```text
planet:   expand · believe
manner:   exploratory · free · far-ranging
excess:   uncommitted ranging · preach from the road
frame:    expansion done by moving toward a farther horizon
out:      meaning-seeking as Jupiter.drive · luck
```

Not `expand` as Sagittarius manner.

### Mercury × Pisces

```text
planet:   think · communicate
manner:   permeable · imaginal · adaptive
excess:   unfocused · impression-as-fact
frame:    thought that lets edges blur and image lead
out:      compassion-as-character · dissolve as Neptune
```

Same planet as Mercury × Gemini. Difference is mobile/switching vs permeable/imaginal.

### Saturn × Aquarius

```text
planet:   limit · structure · mature
manner:   detached · unconventional
excess:   cold system · idea-obstinacy
frame:    limiting/structuring done at a remove, off the default pattern
out:      humanitarian as arena · disrupt as Uranus
```

### 5.1 Grammar check

| Test | Result |
|------|--------|
| Venus×Capricorn ≠ Venus×Scorpio | yes — reserved/practical vs intense/probing |
| Mercury×Gemini ≠ Mercury×Pisces | yes — mobile/switching vs permeable/imaginal |
| Mars×Aries ≠ Capricorn initiating | yes — Capricorn has no initiating |
| No construction used `earth` / `cardinal` as operator | yes |
| No construction copied planet.core_function into sign.manner | yes |
| Dropped families still recognizable as territory | yes — ambition, home/family, beauty, humanitarian stay out |

---

## 6. This pass does not do

- Lock dry-run lemmas as Canon values
- Fill twelve signs · schema · objects · `active`
- Repeat 1.3.82 smoke-test (needs fill + storage first)
- House Mainstream map / House Canon
- Reopen 1.3.83 research · books · CORE · Co–Star ingest
- Repair PARTIAL by writing manner onto catalog objects

**Next named:** Sign Canon fill — **done 1.3.85** ([SIGN_CANON_V1.md](./SIGN_CANON_V1.md)). Sign Canon storage — **done 1.3.86** ([SIGN_CANON_STORAGE_V1.md](./SIGN_CANON_STORAGE_V1.md)). Sign Canon materialization — **done 1.3.87**. Planet × Sign smoke-test — **done 1.3.88**. Houses Mainstream map — **done 1.3.89.** House Canon grammar — **done 1.3.90.** Next = House Canon fill. STOP Signs.

---

## Changelog

- **1.1 (2026-08-21)** — Fill locked 1.3.85. Grammar unchanged. Dry-run lemmas remain illustrative; locked values live in SIGN_CANON_V1.
- **1.0 (2026-08-21)** — 1.3.84. Sign = manner. Two slots (`manner` · `excess`). Territory narrower than Canon is expected. Dry-run only. Grammar before fill.
