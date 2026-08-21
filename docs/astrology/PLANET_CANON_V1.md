# Planet Canon V1

**Date:** 2026-08-21  
**Status:** LOCKED (ten planet packs + provenance). **Not** JSON. **Not** schema. **Not** objects. **Not** Signs. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.33. Territory: [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). Grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file is the product meaning of the ten planets. 1.3.77 is territory. 1.3.78 is grammar. 1.3.79 is synthesis **with origin control**. Dry-run lemmas are not inherited automatically.

```text
Mainstream territory → six-slot synthesis → direct/derived → collision audit → composition audit → lock
```

No new literature. No 1.3.78.1.

---

## Architecture impact

- **SoT before:** grammar locked; dry-run packs were illustrative. Risk: promote dry-run wording to Canon without knowing where convention ended and TodayFlow began.
- **SoT after:** each Canon atom is `direct` (normalization of a 1.3.77 family) or `derived` (synthesis from locked families of that planet). Four audits pass. Dry-run phrases that were copy, collisions, or undefended extras are **out**. Schema still later. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.33 · grammar next-pointer · inventory execution · handoff
- **Backward compatible?** yes for runtime. Deprecated: treating 1.3.78 dry-run as locked values.

---

## 0. Origin rule (locked)

| Origin | Means | Does not mean |
|--------|-------|----------------|
| **direct** | Normalization of a 1.3.77 include family (same concept, shorter lemma) | Copied vendor sentence |
| **direct-secondary** | Normalization of a 1.3.77 **secondary** family | A second stem that displaces include |
| **derived** | TodayFlow inference from **two or more** locked families of **this** planet | A new astrology; a Greene/Hand package; Google |

`derived` is not weaker. It marks where our model starts. If a Today/Profile line later feels wrong, check: territory error vs synthesis error.

**Reject** if: not in that planet’s 1.3.77 families even as parents; collides with another planet’s stem; sounds like user copy; or the derivation is not defensible (`Mars achievement`).

Pipeline per atom:

```text
lemma → direct | direct-secondary | derived → parent family/families → collision check → keep / rewrite / drop
```

---

## 1. Four audits (locked)

1. **Coverage** — all six slots filled for all ten planets.
2. **Territory containment** — every atom is a family on that planet’s 1.3.77 row, or derived only from those families. No new topics.
3. **Planet discrimination** — one stem does not smear two planets. Pairs in §3.
4. **Composability** — the lemma is a machine atom, not a Today sentence. `openness to opportunity` not `timely yes`. `appeasement` not `buying peace`. `dogmatism` not `preachy certainty`. `coercive control` not `annihilation of the other`.

---

## 2. Locked packs

Parents use 1.3.77 family names. Dry-run rejects are listed once in §4.

### Sun

Territory: self · identity · vitality · will · purpose

```text
core_function:  identify · vitalize · will
drive:          purpose · self-coherence
needs:          center · continuity
constructive:   vitality · integrity · self-direction
distorted:      ego-inflation · will-excess · depletion
domains:        self · identity · vitality · purpose
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| identify | core_function | direct | identity / self |
| vitalize | core_function | direct | vitality |
| will | core_function | direct | will |
| purpose | drive | direct | purpose / central concern |
| self-coherence | drive | derived | self + identity |
| center | needs | derived | self + identity |
| continuity | needs | derived | identity + vitality |
| vitality | constructive | direct | vitality |
| integrity | constructive | derived | self + will |
| self-direction | constructive | derived | will + purpose |
| ego-inflation | distorted | derived | self + will (+ ego secondary) |
| will-excess | distorted | derived | will |
| depletion | distorted | derived | vitality |
| self, identity, vitality, purpose | domains | direct | same |

**Vs Mars:** Sun `will` / `self-direction` = center of being. Mars `agency` = pursuit/assertion. Not interchangeable.  
**Vs Jupiter:** Sun `purpose` = what the self is for. Jupiter `meaning` = larger frame / belief. Jupiter does not take `purpose`.

### Moon

Territory: emotions · needs · instincts · security · subconscious

```text
core_function:  feel · respond · protect
drive:          safety
needs:          familiarity · responsiveness
constructive:   attunement · protection · instinct
distorted:      fusion · clinging · reactivity
domains:        emotions · needs · security · the-familiar
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| feel | core_function | direct | emotions |
| respond | core_function | derived | emotions + instincts |
| protect | core_function | derived | security + needs |
| safety | drive | direct | security |
| familiarity | needs | derived | security + needs |
| responsiveness | needs | derived | emotions + instincts |
| attunement | constructive | derived | emotions + instincts |
| protection | constructive | derived | security |
| instinct | constructive | direct | instincts |
| fusion | distorted | derived | emotions + security |
| clinging | distorted | derived | needs + security |
| reactivity | distorted | derived | instincts + emotions |
| emotions, needs, security | domains | direct | same |
| the-familiar | domains | derived | security + needs |

**Vs Venus:** Moon = feeling-care / safety. Venus = `affection` / relating / valuing. Moon does not take `affection`. Venus does not take `safety` or `attunement`.  
**Vs Neptune:** Moon does **not** take `sensitivity` or `receptivity`. Neptune keeps `sensitivity`. Moon keeps `feel` / `attunement`.

### Mercury

Territory: thinking · communication · learning · information

```text
core_function:  think · communicate · learn
drive:          sense-making · exchange
needs:          input · channel
constructive:   clarity · curiosity · skill
distorted:      noise · rumination · pedantry
domains:        thinking · communication · learning · information
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| think | core_function | direct | thinking |
| communicate | core_function | direct | communication |
| learn | core_function | direct | learning |
| sense-making | drive | derived | thinking + information |
| exchange | drive | direct | communication |
| input | needs | derived | information + learning |
| channel | needs | derived | communication |
| clarity | constructive | derived | thinking + communication |
| curiosity | constructive | derived | learning |
| skill | constructive | direct-secondary | skills |
| noise | distorted | derived | communication + information |
| rumination | distorted | derived | thinking |
| pedantry | distorted | derived | thinking + learning |
| thinking, communication, learning, information | domains | direct | same |

### Venus

Territory: love · attraction · relationships · values · pleasure

```text
core_function:  attract · value · relate
drive:          pleasure · bond
needs:          reciprocity · worth
constructive:   affection · taste · fairness
distorted:      appeasement · indulgence · vanity
domains:        love · attraction · relationships · values · pleasure
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| attract | core_function | direct | attraction |
| value | core_function | direct | values |
| relate | core_function | direct | relationships |
| pleasure | drive | direct | pleasure |
| bond | drive | derived | love + relationships |
| reciprocity | needs | derived | relationships + love |
| worth | needs | derived | values |
| affection | constructive | derived | love + attraction |
| taste | constructive | direct-secondary | beauty / aesthetics |
| fairness | constructive | derived | values + relationships |
| appeasement | distorted | derived | relationships + pleasure |
| indulgence | distorted | derived | pleasure |
| vanity | distorted | derived | attraction + self-as-valued (values + attraction) |
| love, attraction, relationships, values, pleasure | domains | direct | same |

`harmony` stays 1.3.77 secondary; not required in the pack (bond covers relating-aim).

### Mars

Territory: action · drive · desire · assertion · conflict

```text
core_function:  act · pursue · assert
drive:          agency · desire
needs:          autonomy · outlet
constructive:   courage · initiative · decisiveness
distorted:      aggression · impulsivity · force
domains:        action · desire · competition · confrontation
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| act | core_function | direct | action |
| pursue | core_function | derived | action + drive |
| assert | core_function | direct | assertion |
| agency | drive | derived | action + drive + assertion |
| desire | drive | direct | desire |
| autonomy | needs | derived | assertion + drive |
| outlet | needs | derived | action + drive |
| courage | constructive | direct-secondary | courage |
| initiative | constructive | derived | action + drive |
| decisiveness | constructive | derived | action + assertion |
| aggression | distorted | direct | conflict / aggression |
| impulsivity | distorted | derived | action + drive |
| force | distorted | derived | assertion + conflict |
| action, desire | domains | direct | same |
| competition | domains | derived | action + assertion |
| confrontation | domains | direct | conflict |

**Reject:** `achievement` (Sun/Jupiter/Saturn; derivation not defensible). `will` (Sun). `domination` / `coercive control` (Pluto). `sexuality` as a fifth domain (desire already routes erotic pursuit; extra lemma not required).

### Jupiter

Territory: growth · expansion · opportunity · belief · meaning

```text
core_function:  expand · believe
drive:          growth · opportunity · meaning
needs:          horizon · faith
constructive:   generosity · perspective · openness-to-opportunity
distorted:      excess · inflation · dogmatism
domains:        growth · opportunity · belief · meaning
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| expand | core_function | direct | expansion / growth |
| believe | core_function | direct | belief / faith |
| growth | drive | direct | growth |
| opportunity | drive | direct | opportunity |
| meaning | drive | direct | meaning |
| horizon | needs | derived | growth + opportunity |
| faith | needs | direct | belief / faith |
| generosity | constructive | derived | expansion + growth |
| perspective | constructive | derived | meaning + expansion |
| openness-to-opportunity | constructive | derived | opportunity + expansion |
| excess | distorted | derived | expansion |
| inflation | distorted | derived | growth + belief |
| dogmatism | distorted | derived | belief + meaning |
| growth, opportunity, belief, meaning | domains | direct | same |

**Vs Sun:** Jupiter `meaning` ≠ Sun `purpose`. No `purpose` on Jupiter.  
`luck` stays secondary, not a Canon stem.

### Saturn

Territory: limits · responsibility · structure · discipline · maturity

```text
core_function:  limit · structure · mature
drive:          order
needs:          boundaries · realism
constructive:   responsibility · discipline · form
distorted:      rigidity · inhibition · severity
domains:        limits · structure · responsibility · discipline
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| limit | core_function | direct | limits |
| structure | core_function | direct | structure |
| mature | core_function | direct | maturity |
| order | drive | derived | structure + limits |
| boundaries | needs | derived | limits + structure |
| realism | needs | direct-secondary | realism |
| responsibility | constructive | direct | responsibility |
| discipline | constructive | direct | discipline |
| form | constructive | direct-secondary | form / definition |
| rigidity | distorted | derived | structure + limits |
| inhibition | distorted | derived | limits + fear/blocks secondary |
| severity | distorted | derived | discipline + limits |
| limits, structure, responsibility, discipline | domains | direct | same |

**Reject:** `control` as drive or distorted stem (Pluto). Use `order` / `severity`.  
`realistic constraints` → `boundaries` + `realism` (derived / secondary), not the phrase.

### Uranus

Territory: change · disruption · freedom · independence · innovation

```text
core_function:  disrupt · free · innovate
drive:          independence · freedom
needs:          latitude · novelty
constructive:   originality · liberation
distorted:      reactivity · instability · aloofness
domains:        change · disruption · freedom · innovation
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| disrupt | core_function | direct | disruption |
| free | core_function | direct | freedom |
| innovate | core_function | direct | innovation |
| independence | drive | direct | independence |
| freedom | drive | direct | freedom |
| latitude | needs | derived | freedom + independence |
| novelty | needs | derived | change + innovation |
| originality | constructive | direct-secondary | originality / individuality |
| liberation | constructive | direct-secondary | liberation / freedom (panel compact) |
| reactivity | distorted | derived | disruption + change |
| instability | distorted | derived | change + disruption |
| aloofness | distorted | derived | independence + freedom |
| change, disruption, freedom, innovation | domains | direct | same |

**Reject:** `a life that is one’s own` (synthesis-as-copy; `independence` is the atom). `transformation` (Pluto).  
**Vs Pluto:** Uranus `change` / `disrupt`. Pluto `transform` / `regenerate`. Not synonyms.

### Neptune

Territory: imagination · ideals · sensitivity · illusion · dissolution

```text
core_function:  dissolve · imagine · idealize
drive:          union · ideal
needs:          inspiration · containment
constructive:   compassion · imagination · devotion
distorted:      illusion · drift · self-erasure
domains:        imagination · ideals · sensitivity · illusion
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| dissolve | core_function | direct | dissolution |
| imagine | core_function | direct | imagination |
| idealize | core_function | direct | ideals |
| union | drive | derived | ideals + dissolution |
| ideal | drive | direct | ideals |
| inspiration | needs | derived | imagination + ideals |
| containment | needs | derived | sensitivity + dissolution |
| compassion | constructive | derived | sensitivity + ideals |
| imagination | constructive | direct | imagination |
| devotion | constructive | derived | ideals |
| illusion | distorted | direct | illusion |
| drift | distorted | derived | dissolution + imagination |
| self-erasure | distorted | derived | dissolution + sensitivity |
| imagination, ideals, sensitivity, illusion | domains | direct | same |

`containment` is the abstract of the dry-run’s permeable-boundary sentence: derived, not convention, not user copy.  
**Vs Moon:** Neptune `sensitivity`. Moon `feel` / `attunement`. Neptune does not take `safety`.

### Pluto

Territory: power · intensity · compulsion · transformation · regeneration

```text
core_function:  intensify · transform · regenerate
drive:          power
needs:          depth · passage
constructive:   regeneration · concentration
distorted:      compulsion · coercive-control · obsession
domains:        power · intensity · depths
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| intensify | core_function | direct | intensity |
| transform | core_function | direct | transformation |
| regenerate | core_function | direct | regeneration |
| power | drive | direct | power |
| depth | needs | derived | intensity + compulsion |
| passage | needs | derived | transformation + regeneration |
| regeneration | constructive | direct | regeneration |
| concentration | constructive | derived | intensity |
| compulsion | distorted | direct | compulsion |
| coercive-control | distorted | derived | power + compulsion |
| obsession | distorted | derived | intensity + compulsion |
| power, intensity | domains | direct | same |
| depths | domains | derived | intensity |

**Reject:** `honesty about what cannot stay` (authorial sentence; `depth` + `passage` are the atoms). `annihilation of the other` → `coercive-control`. `irreversible change` (smears Uranus `change`). `strip` (undefended extra verb).  
**Vs Saturn:** Pluto `power` / `coercive-control`. Saturn `order` / `severity`. Saturn does not take `control`.

---

## 3. Discrimination audit

| Pair | Risk | Lock |
|------|------|------|
| Sun ↔ Mars | will / agency | Sun `will` · `self-direction`. Mars `agency` · `assert`. |
| Venus ↔ Moon | affection / emotional care | Venus `affection` · `bond`. Moon `attunement` · `safety`. |
| Jupiter ↔ Sun | purpose / meaning | Sun `purpose`. Jupiter `meaning`. |
| Saturn ↔ Pluto | control / power | Saturn `order` · `severity`. Pluto `power` · `coercive-control`. No Saturn `control`. |
| Uranus ↔ Pluto | change / transformation | Uranus `change` · `disrupt`. Pluto `transform` · `regenerate`. |
| Moon ↔ Neptune | sensitivity / receptivity | Moon `feel` · `attunement`. Neptune `sensitivity` · `dissolve`. No Moon `sensitivity`. No Neptune `safety`. |

Shared *words* across slots of **one** planet are allowed when they are the same process (`vitality` as constructive and domain). Shared *stems* across **two** planets are not.

---

## 4. Dry-run rejects (do not revive)

| Dry-run lemma | Why out |
|---------------|---------|
| Mars `achievement` | Not in Mars territory; belongs Sun/Jupiter/Saturn unless a new derivation is proven. Not proven. |
| Mars `domination` / `unnecessary conflict` | Pluto-smear / copy. Use `force` · `aggression`. |
| Mars `sexuality` as extra domain | Desire already routes it; extra lemma not required for V1. |
| Saturn drive `control` | Pluto-smear. Use `order`. |
| Saturn `realistic constraints` as phrase | Split to `boundaries` + `realism`. |
| Saturn `punitive control` | Copy + Pluto-smear. Use `severity`. |
| Uranus `a life that is one’s own` | Synthesis-as-prose. Use `independence`. |
| Neptune `permeable but not annihilated boundary` | Good psychology, not a lemma. Use derived `containment`. |
| Pluto `honesty about what cannot stay` | Authorial sentence. Use `depth` · `passage`. |
| Pluto `annihilation of the other` | User copy. Use `coercive-control`. |
| Jupiter `timely yes` | Copy. Use `openness-to-opportunity`. |
| Jupiter `preachy certainty` | Copy. Use `dogmatism`. |
| Venus `buying peace` | Copy. Use `appeasement`. |
| Sun `shine` / `leadership of own life` / `room to exist as oneself` | Poetic or copy. Use `vitalize` · `self-direction` · `center`. |
| Mercury `splitting hairs` / `a channel to speak or write` | Copy. Use `pedantry` · `channel`. |

1.3.78 grammar examples for Moon/Saturn `needs` vs `drive` still hold as **slot semantics**. Their wording is replaced by the atoms above.

---

## 5. Coverage · containment · composability

**Coverage:** 10 × 6 slots filled.

**Containment:** every parent is a 1.3.77 include or secondary on that planet. No fourth panel. No books.

**Composability (spot checks, placeholders for sign/aspect — not locked):**

```text
Mars.act/pursue × Capricorn.cardinal/earth
  → action routed through structured, goal-directed expression

Mars.assert + Saturn.limit/structure + square(friction)
  → pursuit meets order; resolution required
  (not “control”; Saturn is order/limits)

Sun.will + Jupiter.meaning
  → self-purpose meets a larger frame (two stems, not one)

Moon.safety + Venus.bond
  → need-for-safety meets relating/valuing (not two kinds of “love”)

Uranus.disrupt + Pluto.transform
  → pattern-break vs irreversible reconstitution

Neptune.containment as needs
  → recommendation atom: keep a bound while dissolving; not a Today sentence
```

LLM formulates. These packs do not.

---

## 6. This pass does not do

- JSON / schema / object rewrite / `active`
- Signs / houses / aspects / ASC
- Books · CORE · Co–Star ingest
- Promoting remaining dry-run prose

**Next named:** schema pass — **done 1.3.80**. Fill — **done 1.3.81**. Smoke-test — **done 1.3.82**. Sign map — **done 1.3.83**. Next = Sign Canon grammar.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.79. Ten packs locked. Origin direct / direct-secondary / derived. Four audits. Dry-run not auto-Canon.
