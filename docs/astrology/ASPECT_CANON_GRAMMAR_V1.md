# Aspect Canon Grammar V1

**Date:** 2026-08-22  
**Status:** LOCKED (grammar + slot semantics). Dry-run lemmas are **not** locked values. **Not** fill. **Not** JSON. **Not** schema. **Not** objects. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.49. Territory: [MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md](./MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md). Planet grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Sign grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). House grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) · [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md) · [HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./HOUSE_CANON_COMPOSITION_SMOKE_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file answers: **which properties of an aspect does the Composition Engine need in order to relate two already-known planet functions?**

It does not answer “what square personality.” It is not a pair essay. It is not a growth narrative. It is not a copy of Sign Canon or House Canon.

1.3.94 already closed contemporary aspect territory. Do not reopen aspect research. Canon is allowed — and expected — to be **narrower** than that territory.

---

## Architecture impact

- **SoT before:** 1.3.94 locked include/secondary/exclude. One-slot vs two-atom Canon was named, not decided. Risk: two atoms because Signs had two, or because `requires_action` exists; copy `object.interaction` as Canon; treat square as “challenge causes growth”; write Mars□Saturn essays.
- **SoT after:** Aspect generative role is **relation** (how two functions meet), not a theme, not a planet, not a house. **One required slot:** `relation`. Effort / participation / `requires_action` stay surplus — recoverable from relation lemmas where they matter (trine automatic vs sextile directed). Stored `interaction` enum is classical grain, not this slot. Contrasting dry-runs check the grammar; values wait for fill. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.49 · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated as grammar source: Foundation §2.4; IL Layer 4 slot table; `hard` → friction; `soft` → flow; `requires_action` as a second atom; 1.3.94 families dumped as `interaction`.

---

## 0. Question this grammar is allowed to answer

```text
Planet  =  what the function is
Sign    =  how that function is done
House   =  where it is routed
Aspect  =  how two functions meet
```

Only this:

> How does an already-known planet function meet another already-known planet function?

If a proposed slot does not change AspectPair constructions, it is surplus. Signs got two slots because `excess` survived the deletion test. Houses got one because people/events did not. Aspects do not inherit either count.

---

## 1. Generative role (locked)

| Layer | Job | Not the job |
|-------|-----|-------------|
| **Planet Canon** | Function semantics (`core_function` · `drive` · `domains` …) | Costume, sun-sign portrait |
| **Sign Canon** | Manner semantics — how that function is carried | A second planet; a person-type |
| **House Canon** | Arena / routing — where that function lands | Sign manner; an angle; a person |
| **Aspect Canon** | Relation operator — how two functions meet | A theme; a pair essay; a third planet |

```text
Mars.core_function(act / pursue / assert)  ↔  Saturn.core_function(limit / structure / mature)
  ×  square.relation(friction / cross-purposes)
  →  acting/asserting meets limiting/structuring under friction / cross-purpose
```

The planets still act and limit. The aspect does not become “challenge,” “growth,” or “Mars.” LLM (IL-4) formulates the frame. It does not choose what a square is.

### 1.1 Aspect.relation ≠ object.interaction (locked)

They both sound like “how they meet.” They do different work.

| Slot | Question | Example (square vs sextile) |
|------|----------|-----------------------------|
| **object.interaction** | Classical schema enum already on the draft | square `friction`; trine **and** sextile both `flow` |
| **aspect.canon.relation** | How this aspect relates two planet functions, at lemma grain | square: friction · cross-purposes; sextile: directed-ease · participation |

The enum was enough in 1.3.82 to tell tension from flow. It is **not** enough to tell trine from sextile. That is a grain problem inside **one** slot, not a license for a second atom.

Do **not** name the Canon slot `interaction` — the collision would hide the two jobs. Do **not** overwrite the stored enum in this pass. Do **not** copy enum values into `relation`.

### 1.2 Operator ≠ theme (locked)

An aspect must not grow its own topic. If it does, the planets lose their jobs.

| Aspect | Operator (allowed as relation) | Theme (forbidden as the stem) |
|--------|-------------------------------|-------------------------------|
| Conjunction | blend / fuse | new-beginnings / birth |
| Opposition | polarity / facing | partnership-as-7th · “learning experience” |
| Square | friction / cross-purpose | challenge-causes-growth · conflict-as-character |
| Trine | easy-flow / natural-ease | luck / blessing / talent-as-destiny |
| Sextile | directed-ease / participation | Jupiter-opportunity as a topic |

---

## 2. Locked slots

One. Not two. Not six.

| Slot | What it means | Why the engine needs it |
|------|----------------|-------------------------|
| **relation** | How two planet functions meet (operator lemmas) | Distinguishes Mars□Saturn from Mars△Saturn, and trine from sextile, without pair essays |

Each slot is a short list of **lemmas**, not a sentence, not a Today line, not a pair cookbook.

### 2.1 Deletion test (locked)

> If this slot is removed, does the engine lose a real difference between AspectPair constructions?

| Slot | Delete it? | Result |
|------|------------|--------|
| **relation** | Engine cannot tell Mars□Saturn from Mars△Saturn. Hard/soft labels and the coarse `interaction` enum are not substitutes once trine and sextile must diverge. | **Required** |
| effort / participation as own slot | Trine automatic vs sextile directed is recoverable from relation lemmas (`natural-ease` vs `ease-with-participation`). Square “must work” is the growth-narrative trap. | **Surplus** |
| `requires_action` | Unevidenced schema boolean. `false` still ≠ “no action needed.” Not a Canon atom. | **Surplus** |
| excess / overdone-aspect | Planet.distorted already covers the function gone wrong (Mars combative). “Too much square” is still friction. Signs needed excess because manner-overdone ≠ planet.distorted. Aspects do not inherit that. | **Surplus** |
| valence / good-bad as own slot | Conjunction mixed-valence is composed from the two planet packs, not stored on the aspect. | **Surplus** |
| theme / life-lesson | Square-as-growth, trine-as-luck. Steals the planets’ jobs. | **Surplus** |
| pair-specific lemmas | `Mars□Saturn` as a stored meaning. Layer 5 / IL-2 candidate, not Aspect Canon. | **Surplus** |
| core_function / drive | Planet job. Square is not Mars `act`. Trine is not Jupiter `expand`. | **Surplus** |
| manner | Sign job. | **Surplus** |
| arena / house identity | Opposition is not the 7th. | **Surplus** |
| hard / soft / harmonious | Already a classification story. Not an operator (`hard` → friction). | **Surplus** |
| element arithmetic | Trine = same element is geometry/explanation, not meaning. | **Surplus** |
| orb / applying / separating | Calc / Foundation. Not relation. | **Surplus** |

STOP at one slot. Do not add a second because Sign Canon has `excess`, or because Cafe says sextile “takes effort.”

### 2.2 Planet-function collision (locked)

Do not restate a planet’s `core_function` as the aspect’s `relation`.

| Aspect | Not relation |
|--------|--------------|
| Conjunction | Sun `identify` · “new chapter” as a topic |
| Opposition | 7th `the-other` as a house arena · Venus `relate` as the aspect’s verb |
| Square | Mars `act` / `assert` · “growth” as a life lesson |
| Trine | Jupiter `expand` · luck as destiny |
| Sextile | Jupiter `opportunity` as a planet theme |

`friction` as square relation is allowed. `act` as square relation is not.

### 2.3 Guards (locked)

- **Aspect ≠ theme.** Square does not mean “you will grow from conflict.”
- **Aspect ≠ planet.** Square is not Mars. Trine is not Jupiter.
- **Aspect ≠ house.** Opposition is not the 7th.
- **Aspect ≠ pair essay.** Mars□Saturn is composed, not catalogued.
- **One pack per aspect.** The same square pack must route Mars□Saturn and Venus□Saturn.

---

## 3. Territory fitness (hypothesis, not Canon)

1.3.94 families are **input**. This cut is a grammar check. Fill (next) may drop more. It must not add families that are not on that map.

| Bucket | Goes to | Test |
|--------|---------|------|
| **operator-fit** | Candidate `relation` | Can it relate Mars.act to Saturn.limit, Venus.value to Mars.act, Sun.shine to Jupiter.expand, without becoming a theme, a planet, or a pair story? |
| **theme dump** | Stays in territory; **out of generative Canon** | Growth-narrative · luck-as-destiny · new-beginnings |
| **effort as own atom** | Fold into relation lemmas where it discriminates (sextile); otherwise **out** | `requires_action` · “you must work on this square” |
| **classification / arithmetic** | **Out** | hard/soft · same-element · Foundation §2.4 |
| **pair / pattern / orb** | **Out** | Mars□Saturn essays · T-square · applying |

Canon **must not** try to place every locked family. Expected leftovers include: demand-for-action (too close to `requires_action` / growth-narrative) · luck as Astrology.com mass shorthand · mixed-valence as a stored lemma (compose from the two planets) · strengthening as a conjunction slogan.

### 3.1 Cut (illustrative — not fill)

Operator-fit uses include **or** secondary from 1.3.94. Secondary is allowed as relation-candidate (sextile `directed-potential`). Theme include stays out (`challenge-causes-growth` was already exclude on the map).

| Aspect | Operator-fit (candidate) | Out of generative Canon |
|--------|--------------------------|-------------------------|
| Conjunction | blend · fuse · immediate-connection | new-beginnings · always-harmonious · combustion · mixed-valence as a stored stamp |
| Opposition | polarity · facing · the-other | 7th arena · square · learning-experience copy · projection-as-only-stem |
| Square | friction · blockage · cross-purposes | growth-narrative · conflict-as-topic · Mars · demand-for-action as a second atom |
| Trine | easy-flow · support · natural-ease | luck-as-destiny · Jupiter · same-element arithmetic · unused-unless-chosen as a sermon |
| Sextile | ease-with-participation · directed-potential · cooperation | sextile = trine · Jupiter-opportunity as a topic · “chill” as Canon |

Square `friction / cross-purposes` are recognizable. They are **not** Mars.core_function (`act / assert`). That is the point of the cut.

Sextile keeps **participation / directed** inside `relation`. That is how one slot tells trine from sextile. It is not a second atom.

---

## 4. How a pack is used (not implemented this pass)

```text
planet_a.core_function (+ drive)
  ×  planet_b.core_function (+ drive)
  ×  aspect.relation
  →  function A meets function B this way
  ×  sign.manner / house.arena   (already locked on those objects)
  →  IL-4 formulates
```

Do not store `Mars square Saturn` essays.

`interaction` · `requires_action` · hard/soft · orbs are not inputs to this transform.

Valence of a conjunction is read from the two planet packs, not from a conjunction “good/bad” field.

---

## 5. Dry-run (not locked)

Input = planet `core_function` from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md) + §3 operator-fit. Output = grammar check. **Fill later.** Do not copy these rows into objects.

1.3.82 already showed Mars□Saturn and Jupiter△Sun can compose from a coarse operator. Discrimination and composability must also hold at lemma grain, or this is an enum special case, not a grammar.

### Mars □ Saturn

```text
planet_a:  act · pursue · assert
planet_b:  limit · structure · mature
relation:  friction · blockage · cross-purposes
frame:     acting/asserting meets limiting/structuring under friction / cross-purpose
out:       “challenge causes growth” · Mars as the square · demand-for-action as a second slot
```

### Jupiter △ Sun

```text
planet_a:  expand · believe
planet_b:  shine · identify · will
relation:  easy-flow · support · natural-ease
frame:     expanding/believing meets shining/identifying under natural ease
out:       luck-as-destiny · Jupiter as the trine · unused-talent sermon
```

Same construction type as 1.3.82 PASS. Difference after grammar: relation lemmas are richer than `flow`, and must not be Jupiter’s verb.

### Mars ☍ Saturn

```text
planet_a:  act · pursue · assert
planet_b:  limit · structure · mature
relation:  polarity · facing · the-other
frame:     acting/asserting faces limiting/structuring as opposite poles
out:       7th house · square friction · “learning experience”
```

Same planets as Mars □ Saturn. Difference is **only** aspect.relation. Grammar holds if those two frames cannot be swapped.

### Venus △ Mars

```text
planet_a:  attract · value · relate
planet_b:  act · pursue · assert
relation:  easy-flow · support · natural-ease
frame:     valuing/relating meets acting/asserting under natural ease
out:       luck · “good vibes” as Canon
```

### Venus ✶ Mars

```text
planet_a:  attract · value · relate
planet_b:  act · pursue · assert
relation:  ease-with-participation · directed-potential · cooperation
frame:     valuing/relating meets acting/asserting as ease available to be used
out:       trine automatic flow · Jupiter-opportunity as a topic
```

Same planets as Venus △ Mars. Difference is automatic ease vs directed / with-participation. One slot. No second atom.

### Sun ☌ Mercury

```text
planet_a:  shine · identify · will
planet_b:  think · communicate · learn
relation:  blend · fuse · immediate-connection
frame:     shining/identifying fuses with thinking/communicating
out:       new-beginnings · always-harmonious · combustion · mixed-valence stored on the aspect
```

Valence waits for the two planet packs. The aspect only blends.

### Venus □ Saturn

```text
planet_a:  attract · value · relate
planet_b:  limit · structure · mature
relation:  friction · blockage · cross-purposes
frame:     valuing/relating meets limiting/structuring under friction / cross-purpose
out:       “cold Venus” as a Venus-keyed square lemma
```

Mars □ Saturn and Venus □ Saturn share **one** square pack. If the square needed planet-specific lemmas, the grammar fails.

### Moon ☍ Saturn

```text
planet_a:  feel · respond · protect
planet_b:  limit · structure · mature
relation:  polarity · facing · the-other
frame:     feeling/protecting faces limiting/structuring as opposite poles
out:       7th partnership · 4th home · square as the opposition
```

### 5.1 Grammar check

| Test | Result |
|------|--------|
| Mars□Saturn ≠ Mars☍Saturn | yes — friction/cross-purpose vs polarity/facing |
| Venus△Mars ≠ Venus✶Mars | yes — natural-ease vs directed / with-participation |
| Mars□Saturn and Venus□Saturn share one square pack | yes — no planet-keyed aspect lemmas |
| Sun☌Mercury does not store good/bad on the aspect | yes — blend only |
| No construction used `hard` / `soft` / same-element as operator | yes |
| No construction copied planet.core_function into aspect.relation | yes |
| No construction used 7th arena or Jupiter.expand as the aspect | yes |
| One slot was enough | yes — effort / `requires_action` / excess / theme failed the deletion test |
| Dropped families still recognizable as territory | yes — demand-for-action, luck-as-destiny, growth-narrative stay out |
| Stored `interaction` was not treated as this slot | yes — sextile remains `flow` on the object; grammar still discriminates |

---

## 6. This pass does not do

- Lock dry-run lemmas as Canon values
- Fill five aspects · schema · objects · `active`
- Overwrite `object.interaction` or `requires_action`
- Repeat 1.3.82 smoke-test (needs fill + storage first)
- Pair application (Mars□Saturn essays)
- Minors · orbs · applying/separating · dignity · patterns
- ASC/MC maps
- Sign / House pack edits · books · CORE · Co–Star ingest

**Next named:** Aspect Canon fill. Then storage/materialization · Planet × Aspect smoke. **STOP Houses.** **STOP Signs.** Do not reopen 1.3.94 research.

---

## Changelog

- **1.0 (2026-08-22)** — 1.3.95. Aspect = relation (how two functions meet). One slot (`relation`). Effort / `requires_action` surplus. `relation` ≠ stored `interaction`. Dry-run only. Grammar before fill.
