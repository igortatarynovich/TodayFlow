# Planet Canon Composition Smoke V1

**Date:** 2026-08-21  
**Status:** LOCKED (diagnostic). **Not** IL-2. **Not** LLM. **Not** pair essays. **Not** object fill. **Not** schema. **Not** CORE. **Not** a grammar patch.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.36. Packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md) on Sun–Saturn `object.canon` ([PLANET_CANON_SUN_SATURN_FILL_V1.md](./PLANET_CANON_SUN_SATURN_FILL_V1.md)). Grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md).

This pass answers: **do the six planet slots plus currently stored sign/house/aspect atoms yield a deterministic semantic frame without pair-specific prose?** PARTIAL is a valid architecture finding. Do not repair it here.

```text
planet.canon → modifier/operator atoms → deterministic semantic frame → verdict
```

No user-facing sentence. No “Mars square Saturn means…”.

---

## Architecture impact

- **SoT before:** seven planet drafts carry product `canon`. Next risk: treat Signs Mainstream map as automatic, or judge composition by pretty copy.
- **SoT after:** four constructions scored PASS / PARTIAL / FAIL against catalog atoms only. Aspect pairs with two planet packs **PASS**. Planet × classification-only sign and planet × classical house **PARTIAL**. Missing atom types named. No grammar invented to close the gaps. Catalog unchanged.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.36
- **Backward compatible?** yes (`draft`). Deprecated as next step: Signs Mainstream map *as content fill*; cookbook pair rows; silently mapping `earth` → practical.

---

## 0. Verdict rules (locked)

| Verdict | Means |
|---------|--------|
| **PASS** | The frame is produced from allowed atoms. Payload (what is related / routed) is on the objects. |
| **PARTIAL** | The construction type is identified, but a named atom type is missing. Direction exists; completion does not. |
| **FAIL** | Apparent meaning appears only from hidden astrology or a stored pair essay. |

PARTIAL is **not** fixed in 1.3.82. Do not add manner operators, house lemmas, or pair objects to “make it PASS”.

Each construction records four fields:

1. **Inputs** — allowed atoms only  
2. **Transform** — what the modifier/operator does to planet function  
3. **Output frame** — structured meaning, not copy  
4. **Missing atom** — `none` or a named type  

### 0.1 Allowed inputs

| Kind | Allowed | Forbidden |
|------|---------|-----------|
| Planet | `object.canon` six slots | `function` · `themes` · `positive_expression` · `shadow` · four-key `domains` · `tempo` · provenance sentences |
| Aspect | `interaction` (operator) | Lilly/Ptolemy claim prose; `requires_action` (unevidenced boolean, not an operator); pair slogans |
| Sign | `mode` · `element` · `orientation` | later-interpretive slots; QUALITY adjectives; “Capricorn = ambition” |
| House | presence of a domain slot | treating Lilly prose as Canon lemmas; “Moon in 4th = …” |

`requires_action: false` on draft aspects is **not** read as “no action needed”.

### 0.2 Transform types (diagnostic, not a new engine)

| Construction | Stored modifier | Intended job |
|--------------|-----------------|--------------|
| AspectPair | `aspect.interaction` | Relate two `core_function` (+ `drive`) bundles |
| PlanetInSign | sign classification triple | Modify **manner** of the planet function |
| PlanetInHouse | house domain slot | **Route** the planet function into arenas |

`interaction` values already on the objects: `friction` (square) · `flow` (trine). Those words are the operator. They are not expanded into cookbooks (`blockage`, `luck`).

---

## 1. Mars □ Saturn — **PASS**

**Inputs**

- Mars `canon.core_function`: `act` · `pursue` · `assert`  
- Mars `canon.drive`: `agency` · `desire`  
- Saturn `canon.core_function`: `limit` · `structure` · `mature`  
- Saturn `canon.drive`: `order`  
- square `interaction`: `friction`

**Transform**

`friction` relates two function bundles. It does not merge them and does not name a pair.

**Output frame**

```text
type:        aspect_pair
left:        mars  core_function={act, pursue, assert}  drive={agency, desire}
right:       saturn core_function={limit, structure, mature}  drive={order}
operator:    friction
payload:     act/pursue/assert  ↔  limit/structure/mature
```

Type of result (not a reading): action/assertion meets constraint/structure under friction. Branch (`constructive` vs `distorted`) is unspecified; that does not block the frame.

**Missing atom:** none

**Forbidden recovery:** “Mars square Saturn = frustration / blockage.” That essay is not on the objects.

**Verdict:** PASS

---

## 2. Venus × Capricorn — **PARTIAL**

**Inputs**

- Venus `canon.core_function`: `attract` · `value` · `relate`  
- Venus `canon.drive`: `pleasure` · `bond`  
- Capricorn `mode`: `cardinal`  
- Capricorn `element`: `earth`  
- Capricorn `orientation`: `negative`  
- Capricorn later-interpretive: **absent** (classification-only, 1.3.68 / 1.3.69)

**Transform**

Classification labels can be **attached** as modifiers. There is no locked operator that says what `cardinal` / `earth` / `negative` **do** to `attract/value/relate`. Mapping earth → practical or cardinal → initiating would be hidden Mainstream, not an atom.

**Output frame**

```text
type:             planet_in_sign
function:         attract / value / relate
drive:            pleasure / bond
modifier_labels:  mode=cardinal  element=earth  orientation=negative
manner:           null
```

**Missing atom:** Sign Canon **manner operator** (grammar for how mode / element / orientation modify a planet function). Classification enums are not that grammar.

**Forbidden recovery:** “Venus in Capricorn = reserved / ambitious love.” Not on the object.

**Verdict:** PARTIAL

This is the useful finding: Signs Mainstream map is required **as territory for Sign Canon grammar**, not as twelve portraits and not as a Lilly QUALITY paste.

---

## 3. Moon × 4th house — **PARTIAL**

**Inputs**

- Moon `canon.core_function`: `feel` · `respond` · `protect`  
- Moon `canon.drive`: `safety`  
- Moon `canon.needs`: `familiarity` · `responsiveness`  
- Moon `canon.domains`: `emotions` · `needs` · `security` · `the-familiar`  
- House 4 `domain` (and `internal_meaning` / `people` / `activities` / `resources` / `risks`): **present**, classical prose

**Transform**

A house should route planet function into arenas that can meet `canon.domains`. The 4th-house slot exists, but its value is Lilly prose (`father, land, hidden things, and endings`), not a lemma list. Using that prose as the frame, or collapsing it to modern “home / mother”, is historical cookbook.

**Output frame**

```text
type:                   planet_in_house
function:               feel / respond / protect
drive:                  safety
planet_domains:         emotions / needs / security / the-familiar
house_domain_present:   true
house_arena_lemmas:     null
house_domain_shape:     classical_prose
```

**Missing atom:** House Canon **`domains` as lemma list** plus a routing rule into planet `canon.domains`. Do not promote Lilly `domain` to that grammar.

**Forbidden recovery:** “Moon in 4th = home and family.”

**Verdict:** PARTIAL

---

## 4. Jupiter △ Sun — **PASS**

**Inputs**

- Jupiter `canon.core_function`: `expand` · `believe`  
- Jupiter `canon.drive`: `growth` · `opportunity` · `meaning`  
- Sun `canon.core_function`: `identify` · `vitalize` · `will`  
- Sun `canon.drive`: `purpose` · `self-coherence`  
- trine `interaction`: `flow`

**Transform**

`flow` relates two function bundles. The packs supply **what** is in flow. The operator does not invent a pair slogan.

**Output frame**

```text
type:        aspect_pair
left:        jupiter  core_function={expand, believe}  drive={growth, opportunity, meaning}
right:       sun      core_function={identify, vitalize, will}  drive={purpose, self-coherence}
operator:    flow
payload:     expand/believe/meaning  with  identify/will/purpose
stems:       meaning ≠ purpose (two stems, not one)
```

If the operator were only `flow` with empty planet packs, this would FAIL. Packs are present, so the payload is determined.

**Missing atom:** none (operator remains coarse; constructive/distorted branch unspecified; not blocking)

**Forbidden recovery:** “Jupiter trine Sun = luck / blessing.”

**Verdict:** PASS

---

## 5. Scoreboard

| Construction | Verdict | Missing atom |
|--------------|---------|--------------|
| Mars □ Saturn | **PASS** | none |
| Venus × Capricorn | **PARTIAL** | Sign Canon manner operator |
| Moon × 4th house | **PARTIAL** | House Canon domain lemmas + routing |
| Jupiter △ Sun | **PASS** | none |

**Planet Canon (six slots):** sufficient as AspectPair payload. Do not reopen planet research.

**Aspect `interaction`:** sufficient *type* of operator for tension vs flow. Not a pair encyclopedia. Aspect Canon grammar can wait.

**Sign objects:** classification-complete is **not** composition-complete. Next Signs work is Mainstream territory → **Sign Canon grammar** (same shape as 1.3.77 → 1.3.78), not QUALITY fill.

**House objects:** classical `domain` prose is **not** House Canon. Named later. Do not start House literature in the Signs pass.

No FAIL row. No silent repair.

---

## 6. This pass does not do

- IL-2 engine · runtime wiring · LLM copy  
- New lemmas on planets · `function` rewrite · outers · `active`  
- Sign/house object edits · pair catalog rows  
- Inventing `earth → practical` to flip PARTIAL to PASS  

**Next named:** Signs Mainstream Semantic Map — **done 1.3.83**. Sign Canon grammar — **done 1.3.84**. Sign Canon fill — **done 1.3.85**. Sign Canon storage — **done 1.3.86**. Sign Canon materialization — **done 1.3.87**. Planet × Sign smoke-test — **done 1.3.88**. Houses Mainstream map — **done 1.3.89.** House Canon grammar — **done 1.3.90.** House Canon fill — **done 1.3.91.** House Canon storage/materialization — **done 1.3.92.** Planet × House smoke — **done 1.3.93.** Mainstream Aspect Semantic Map — **done 1.3.94.** Aspect Canon grammar — **done 1.3.95.** Next = **Aspect Canon fill**. STOP Signs.

---

## Changelog

- **1.1 (2026-08-22)** — House live state is 1.3.93 PASS. This file’s Moon × 4th PARTIAL is a snapshot of the catalog then.
- **1.0 (2026-08-21)** — 1.3.82. Four constructions. Aspect pairs PASS. Sign × planet and house × planet PARTIAL. No object change.
