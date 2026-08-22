# Aspect Canon Grammar V1

**Date:** 2026-08-22  
**Status:** LOCKED (grammar + slot semantics). Dry-run lemmas are **not** locked values. **Not** fill. **Not** JSON. **Not** schema. **Not** objects. **Not** CORE. **Not** a book. **Not** IL-2.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.49. Territory: [MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md](./MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md). Planet grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Sign grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). House grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) · [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md) · [HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./HOUSE_CANON_COMPOSITION_SMOKE_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file answers **one** question:

> What **minimal payload** does an aspect need so the Composition Engine can relate two already-known planet functions **without interpreting them in advance**?

It does not answer “what square personality.” It is not a pair essay. It is not a growth narrative. It is not a copy of Sign Canon or House Canon. It does not decide Profile / Today / Compatibility separately. If the atomic frame is right, the consumer is downstream.

1.3.94 already closed contemporary aspect territory. Do not reopen aspect research. Canon is allowed — and expected — to be **narrower** than that territory.

---

## Architecture impact

- **SoT before:** 1.3.94 locked include/secondary/exclude. One-slot vs two-atom Canon was named, not decided. Risk: two atoms because Signs had two, or because `requires_action` exists; copy `object.interaction` as Canon; treat square as “challenge causes growth”; write Mars□Saturn essays; let Aspect Canon decide what the link *means*.
- **SoT after:** Aspect generative role is **topology / quality of the link** (`relation`), not the meaning of that link. **One required slot:** `relation`. A second dimension (effort / participation / valence / outcome) fails the deletion test: if one slot is kept, composition still has the five mechanisms. Conjunction Canon stays **mixed-valence** — character comes from the two functions, not from a pre-written result. Extra slots needed only for a pretty sentence are IL-2, not Canon. Dry-run lemmas wait for fill. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.49 · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated as grammar source: Foundation §2.4; IL Layer 4 slot table; `hard` → friction; `soft` → flow; `requires_action` as a second atom; 1.3.94 families dumped as `interaction`; Aspect Canon as a mini-Composition Engine.

---

## 0. Question this grammar is allowed to answer

```text
Planet  =  what the function is
Sign    =  how that function is done
House   =  where it is routed
Aspect  =  topology / quality of how two functions meet
```

Only this:

> What minimal aspect payload does the engine need to bind two known planet functions **without interpreting them first**?

If a proposed slot does not change that bind, it is surplus. Signs got two slots because `excess` survived the deletion test. Houses got one because people/events did not. Aspects do not inherit either count. Profile / Today / Compatibility are not separate aspect grammars.

Target boundary (locked):

```text
Planet A atoms + Planet B atoms + Aspect operator  →  structured frame
IL-2                                              →  composition rules
IL-4                                              →  formulates
```

Aspect Canon describes the operator. It does **not** decide what the meeting means.

---

## 1. Generative role (locked)

| Layer | Job | Not the job |
|-------|-----|-------------|
| **Planet Canon** | Function semantics (`core_function` · `drive` · `domains` …) | Costume, sun-sign portrait |
| **Sign Canon** | Manner semantics — how that function is carried | A second planet; a person-type |
| **House Canon** | Arena / routing — where that function lands | Sign manner; an angle; a person |
| **Aspect Canon** | Topology / quality of the link | Meaning of the link; a theme; a pair essay; a third planet |

```text
Mars.core_function(act / assert)  ↔  Saturn.core_function(limit / structure)
  ×  square.relation(friction / cross-purposes)
  →  acting/asserting meets limiting/structuring under friction / cross-purpose
```

The planets still act and limit. The aspect does not become “challenge,” “growth,” or “Mars.” LLM (IL-4) formulates the frame. It does not choose what a square is.

### 1.1 Aspect Canon is not a mini-Composition Engine (locked)

Need for a nicer sentence is **not** proof of a second Canon slot. That work belongs to IL-2 (how atoms combine) and IL-4 (how the frame is said). If 1.3.95 looks “thin” next to a finished Today line, that is the point.

### 1.2 Aspect.relation ≠ object.interaction (locked)

They both sound like “how they meet.” They do different work.

| Slot | Question | Example (square vs sextile) |
|------|----------|-----------------------------|
| **object.interaction** | Classical schema enum already on the draft | square `friction`; trine **and** sextile both `flow` |
| **aspect.canon.relation** | Topology / quality of the link, at lemma grain | square: friction · cross-purposes; sextile: directed-ease · participation |

The enum was enough in 1.3.82 to tell tension from flow. It is **not** enough to tell trine from sextile. That is a grain problem inside **one** slot, not a license for a second atom.

Do **not** name the Canon slot `interaction` — the collision would hide the two jobs. Do **not** overwrite the stored enum in this pass. Do **not** copy enum values into `relation`.

### 1.3 Operator ≠ theme, outcome, or valence (locked)

An aspect must not grow its own topic, result, or moral. If it does, the planets lose their jobs.

| Aspect | Operator (allowed as relation) | Forbidden as the stem |
|--------|-------------------------------|------------------------|
| Conjunction | blend / fuse / immediate-connection | new-beginnings · always-harmonious · always-difficult · success / failure |
| Opposition | polarity / facing / the-other | partnership-as-7th · conflict-as-square · “learning experience” |
| Square | friction / blockage / cross-purposes | challenge-causes-growth · success-through-struggle · conflict-as-character |
| Trine | easy-flow / support / natural-ease | luck / blessing / talent-as-destiny |
| Sextile | directed-ease / participation / opportunity-as-relating-mode | Jupiter-opportunity as a topic · trine collapse |

---

## 2. Locked slots

One. Not two. Not six.

| Slot | What it means | Why the engine needs it |
|------|----------------|-------------------------|
| **relation** | Topology / quality of how two planet functions meet (operator lemmas) | Distinguishes the five mechanisms below without pair essays |

Each slot is a short list of **lemmas**, not a sentence, not a Today line, not a pair cookbook.

### 2.1 What one slot must preserve (locked)

Literal deletion test:

> If we leave **only** `relation`, does the engine lose substantial information **necessary for composition**?

Checked against locked 1.3.94 territory. Grammar must preserve the **mechanism**, not every include lemma.

| Aspect | Territory (1.3.94) | Mechanism one slot must keep |
|--------|--------------------|------------------------------|
| Conjunction | blend · unite · fuse · immediate-connection | functions join directly |
| Opposition | polarity · facing · the-other · awareness-of-opposite | functions meet through polarity; **both sides remain** |
| Square | friction · blockage · cross-purposes · demand-for-action | functions collide |
| Trine | easy-flow · support · natural-ease · complementary | functions interact freely |
| Sextile | ease-with-participation · opportunity · cooperation · directed-potential | interaction is available **and** assumes participation |

**Sextile is the stress-test.** If `relation` can tell trine = natural / easy flow from sextile = cooperative / opportunity requiring participation, a second slot is not needed.

Demand-for-action stays in square *territory*. It does not become a second atom (`requires_action`) and it does not become an outcome (“you will grow”). Collision is the mechanism.

### 2.2 Deletion test (locked)

> If this slot is removed, does the engine lose a real difference between AspectPair constructions?

| Slot | Delete it? | Result |
|------|------------|--------|
| **relation** | Engine cannot tell Mars□Saturn from Mars△Saturn, nor keep both poles of an opposition, nor tell trine from sextile. Hard/soft labels and the coarse `interaction` enum are not substitutes. | **Required** |
| effort / participation as own slot | Trine automatic vs sextile directed is recoverable from relation lemmas (`natural-ease` vs `ease-with-participation`). Square “must work” is the growth-narrative trap. Sextile stress-test passed inside `relation`. | **Surplus** |
| `requires_action` | Unevidenced schema boolean. `false` still ≠ “no action needed.” Not a Canon atom. | **Surplus** |
| excess / overdone-aspect | Planet.distorted already covers the function gone wrong (Mars combative). “Too much square” is still friction. Do not copy planet constructive/distorted onto the aspect. | **Surplus** |
| valence / good-bad as own slot | Conjunction mixed-valence is a **guard on the pack**, not a second atom. Character comes from the two functions. | **Surplus** |
| outcome (growth / success / failure) | Result of the meeting. IL-2 / later surfaces, not topology. | **Surplus** |
| theme / life-lesson / morality | Square-as-growth, “challenge makes you stronger.” Steals the planets’ jobs. | **Surplus** |
| pair-specific lemmas | `Mars□Saturn` as a stored meaning. Layer 5 / IL-2 candidate, not Aspect Canon. | **Surplus** |
| core_function / drive | Planet job. Square is not Mars `act`. Trine is not Jupiter `expand`. | **Surplus** |
| manner | Sign job. | **Surplus** |
| arena / house identity | Opposition is not the 7th. | **Surplus** |
| hard / soft / harmonious | Already a classification story. Not an operator (`hard` → friction). | **Surplus** |
| element arithmetic | Trine = same element is geometry/explanation, not meaning. | **Surplus** |
| orb / applying / separating | Calc / Foundation. Not relation. Not this pass. | **Surplus** |
| surface-specific rules | Today / Profile / Compatibility as three aspect grammars. Consumer is downstream. | **Surplus** |

STOP at one slot. Do not add a second because Sign Canon has `excess`, because Cafe says sextile “takes effort,” or because a pretty sentence wants more fields.

### 2.3 Conjunction mixed-valence (locked)

Conjunction Canon **stays mixed-valence**. That is an architecture control, not a leftover family and not a second slot.

The pack may say blend / fuse / immediate-connection. It may **not** say harmonious, difficult, success, or failure. Whether the fusion helps or strains is read from Planet A × Planet B, later by IL-2. Fill must not collapse this.

### 2.4 Planet-function collision (locked)

Do not restate a planet’s `core_function` as the aspect’s `relation`.

| Aspect | Not relation |
|--------|--------------|
| Conjunction | Sun `identify` · “new chapter” as a topic · harmonious/difficult stamp |
| Opposition | 7th `the-other` as a house arena · Venus `relate` as the aspect’s verb · square friction |
| Square | Mars `act` / `assert` · “growth” as a life lesson |
| Trine | Jupiter `expand` · luck as destiny |
| Sextile | Jupiter `opportunity` as a planet theme |

`friction` as square relation is allowed. `act` as square relation is not.

### 2.5 Guards (locked)

- **Aspect ≠ theme.** Square does not mean “you will grow from conflict.”
- **Aspect ≠ outcome.** No stored growth / success / failure.
- **Aspect ≠ morality.** No “challenge that makes you stronger.”
- **Aspect ≠ valence stamp.** No good/bad on the operator. Conjunction stays mixed-valence.
- **Aspect ≠ planet.** Square is not Mars. Trine is not Jupiter. Do not copy planet constructive/distorted.
- **Aspect ≠ house.** Opposition is not the 7th.
- **Aspect ≠ pair essay.** Mars□Saturn is composed, not catalogued.
- **Aspect ≠ event prediction.**
- **Aspect ≠ orb / applying / separating.**
- **Aspect ≠ mini-Composition Engine.** Topology of the link, not what the link means.
- **Aspect ≠ surface grammar.** No separate Today / Profile / Compatibility rules.
- **One pack per aspect.** The same square pack must route Mars□Saturn and Venus□Saturn.

---

## 3. Territory fitness (hypothesis, not Canon)

1.3.94 families are **input**. This cut is a grammar check. Fill (next) may drop more. It must not add families that are not on that map.

| Bucket | Goes to | Test |
|--------|---------|------|
| **operator-fit** | Candidate `relation` | Can it bind Mars.act to Saturn.limit, Jupiter.expand to Sun.identify, Venus.value to Mars.act, without becoming a theme, an outcome, or a pair story? |
| **theme / outcome / morality dump** | Stays in territory; **out of generative Canon** | Growth-narrative · luck-as-destiny · new-beginnings · success/failure |
| **effort as own atom** | Fold into relation lemmas where it discriminates (sextile); otherwise **out** | `requires_action` · “you must work on this square” |
| **classification / arithmetic** | **Out** | hard/soft · same-element · Foundation §2.4 |
| **pair / pattern / orb** | **Out** | Mars□Saturn essays · T-square · applying |

Canon **must not** try to place every locked family. Expected leftovers include: demand-for-action as a second atom (mechanism is collision) · luck as Astrology.com mass shorthand · strengthening as a conjunction slogan. Mixed-valence is **not** a leftover — it is the conjunction guard in §2.3.

### 3.1 Cut (illustrative — not fill)

Operator-fit uses include **or** secondary from 1.3.94. Secondary is allowed as relation-candidate (sextile `directed-potential`). Theme include stays out (`challenge-causes-growth` was already exclude on the map).

| Aspect | Operator-fit (candidate) | Out of generative Canon |
|--------|--------------------------|-------------------------|
| Conjunction | blend · fuse · immediate-connection | new-beginnings · always-harmonious · always-difficult · combustion · success/failure |
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
  →  structured frame: function A meets function B under this topology
  →  IL-2 applies composition rules
  →  IL-4 formulates
```

Do not store `Mars square Saturn` essays.

`interaction` · `requires_action` · hard/soft · orbs are not inputs to this transform.

Valence of a conjunction is read from the two planet packs, not from a conjunction “good/bad” field.

---

## 5. Dry-run (not locked)

Input = planet `core_function` / `drive` from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md) + §3 operator-fit. Output = grammar check. **Fill later.** Do not copy these rows into objects.

Mars □ Saturn already composed in 1.3.82. It is **not** sufficient proof of this grammar. Four mechanisms plus trine-vs-sextile on one pair are required. If any of those frames collapse to “ease” or “conflict,” the grammar fails.

Planet lemmas below are locked packs, not new research.

### Square — friction

Mars □ Saturn. Mars.act/assert × Saturn.structure/constrain

```text
planet_a:  act · pursue · assert
planet_b:  limit · structure · mature
relation:  friction · blockage · cross-purposes
frame:     acting/asserting meets limiting/structuring under friction / cross-purpose
out:       “challenge causes growth” · success-through-struggle · Mars as the square · demand-for-action as a second slot
```

Checks collision of functions. Not an outcome.

### Trine — flow

Jupiter △ Sun. Jupiter.expand/meaning × Sun.identity/purpose

```text
planet_a:  expand · believe          drive: growth · opportunity · meaning
planet_b:  identify · vitalize · will   drive: purpose · self-coherence
relation:  easy-flow · support · natural-ease
frame:     expanding/believing meets identifying/purpose under natural ease
out:       luck-as-destiny · Jupiter as the trine · unused-talent sermon
```

Checks free interaction. Trine is not luck.

### Opposition — polarity

Mars ☍ Saturn. Same planets as the square row, so the only changed atom is `relation`. Both functions must remain. The frame must not collapse to square-conflict.

```text
planet_a:  act · pursue · assert
planet_b:  limit · structure · mature
relation:  polarity · facing · the-other
frame:     acting/asserting and limiting/structuring remain as opposite poles; they face
out:       7th house · square friction · one side deleted · “learning experience”
```

Grammar holds if this frame cannot be swapped with Mars □ Saturn.

### Conjunction — fusion

```text
planet_a:  identify · vitalize · will
planet_b:  think · communicate · learn
relation:  blend · fuse · immediate-connection
frame:     identifying/will fuses with thinking/communicating; quality not pre-assigned
out:       new-beginnings · always-harmonious · always-difficult · combustion · success/failure stored on the aspect
```

Sun ☌ Mercury. Two functions become immediately bound. Grammar does **not** decide whether that is good or bad. Mixed-valence stands.

### Trine vs Sextile — same planet pair

This is the deletion / discrimination test. If both payloads come out as generic ease, one slot has failed.

#### Venus △ Mars

```text
planet_a:  attract · value · relate
planet_b:  act · pursue · assert
relation:  easy-flow · support · natural-ease
frame:     valuing/relating meets acting/asserting under natural ease
out:       luck · “good vibes” as Canon · same payload as sextile
```

#### Venus ✶ Mars

```text
planet_a:  attract · value · relate
planet_b:  act · pursue · assert
relation:  ease-with-participation · directed-potential · cooperation
frame:     valuing/relating meets acting/asserting as ease available to be used
out:       trine automatic flow · Jupiter-opportunity as a topic · same payload as trine
```

Same planets. Difference is automatic ease vs directed / with-participation. One slot. No second atom.

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
frame:     feeling/protecting and limiting/structuring remain as opposite poles
out:       7th partnership · 4th home · square as the opposition · one pole deleted
```

### 5.1 Grammar check

| Test | Result |
|------|--------|
| Square keeps collision, not outcome | yes — Mars.act meets Saturn.limit under friction |
| Trine keeps free flow, not luck | yes — Jupiter.expand meets Sun.identify under natural-ease |
| Opposition keeps both poles, does not collapse to conflict | yes — same planets as square; relation is polarity/facing |
| Conjunction fuses without good/bad | yes — mixed-valence guard; blend only |
| Venus△Mars ≠ Venus✶Mars | yes — natural-ease vs directed / with-participation |
| If trine and sextile were both “ease,” grammar would fail | they are not |
| Mars□Saturn and Venus□Saturn share one square pack | yes — no planet-keyed aspect lemmas |
| No construction used `hard` / `soft` / same-element as operator | yes |
| No construction copied planet.core_function or constructive/distorted into aspect.relation | yes |
| No construction used 7th arena or Jupiter.expand as the aspect | yes |
| No construction assigned Today / Profile / Compatibility rules | yes |
| One slot was enough | yes — effort / valence / outcome / `requires_action` / excess / theme failed the deletion test |
| Extra fields for a pretty sentence | not taken as Canon; IL-2 / IL-4 |
| Dropped families still recognizable as territory | yes — demand-for-action as atom, luck-as-destiny, growth-narrative stay out |
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
- IL-2 composition rules · surface-specific aspect grammars

**Next named:** Aspect Canon fill — **done 1.3.96.** Aspect Canon storage/materialization — **done 1.3.97.** Stored Planet × Aspect smoke — **done 1.3.98.** Angle Canon model — **done 1.3.99.** Mainstream Angle map — **done 1.3.100.** Angle Canon grammar — **done 1.3.101.** Angle Canon fill — **done 1.3.102.** **STOP Aspects.** Next = Angle Canon storage/materialization → stored Planet×Angle smoke → STOP Angles → final atomic smoke → Knowledge Core V1 FREEZE. After freeze: IL-2. **STOP Houses.** **STOP Signs.** Do not reopen 1.3.94 research.

---

## Changelog

- **1.4 (2026-08-22)** — Angle Canon model locked 1.3.99. Grammar unchanged. Next = Mainstream Angle Semantic Map.
- **1.3 (2026-08-22)** — Aspect Canon storage/materialization locked 1.3.97. Grammar unchanged. Stored Planet × Aspect smoke — **done 1.3.98.** Angle model — **done 1.3.99.** **STOP Aspects.**
- **1.2 (2026-08-22)** — Aspect Canon fill locked 1.3.96. Grammar unchanged. Next = storage/materialization. **Done 1.3.97.**
- **1.1 (2026-08-22)** — Owner proof tightened. Central question = minimal payload to bind two known functions without prior interpretation. Conjunction mixed-valence locked as a guard, not a leftover. Aspect Canon ≠ mini-Composition Engine (pretty sentences are IL-2). Dry-run requires four mechanisms plus trine-vs-sextile on one pair. Slot count unchanged (one: `relation`).
- **1.0 (2026-08-22)** — 1.3.95. Aspect = relation (how two functions meet). One slot (`relation`). Effort / `requires_action` surplus. `relation` ≠ stored `interaction`. Dry-run only. Grammar before fill.
