# Sign Canon Composition Smoke V1

**Date:** 2026-08-22  
**Status:** LOCKED (diagnostic). **Not** IL-2. **Not** LLM. **Not** pair essays. **Not** lemma rewrite. **Not** House Canon. **Not** CORE. **Not** a grammar patch. **Not** `active`.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.42. Packs: [SIGN_CANON_V1.md](./SIGN_CANON_V1.md) on twelve sign `object.canon` ([SIGN_CANON_MATERIALIZATION_V1.md](./SIGN_CANON_MATERIALIZATION_V1.md)). Grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Prior smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) (1.3.82 stands: Venus × Capricorn was PARTIAL *then*). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md).

This pass answers: **do stored `sign.canon.manner` / `excess` plus planet `canon` yield a deterministic PlanetInSign frame without classification arithmetic or pair-specific prose?** PARTIAL remains valid for House. Do not repair House here.

```text
planet.canon × sign.canon.manner → deterministic semantic frame → verdict
```

No user-facing sentence. No “Venus in Capricorn means…”.

---

## Architecture impact

- **SoT before:** 1.3.82 scored Venus × Capricorn PARTIAL — classification triple attached, `manner: null`. 1.3.87 copied packs onto drafts. Next risk: treat `mode`/`element` as the operator, or write pair essays to “prove” PASS.
- **SoT after:** PlanetInSign frames read `object.canon.manner`. Operator, discrimination, and classification-independence gates PASS on catalog atoms. 1.3.82 AspectPair rows unchanged. Moon × 4th stays PARTIAL. Catalog unchanged. No grammar invented.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.42
- **Backward compatible?** yes (`draft`). Deprecated as next step: improving Sign packs; `earth` → practical; House literature in the Signs train.

---

## 0. Verdict rules (locked)

Same three values as 1.3.82.

| Verdict | Means |
|---------|--------|
| **PASS** | The frame is produced from allowed atoms. Payload (what is done, and how) is on the objects. |
| **PARTIAL** | The construction type is identified, but a named atom type is missing. |
| **FAIL** | Apparent meaning appears only from hidden astrology or a stored pair essay. |

PARTIAL is **not** fixed in 1.3.88 for House. Do not add house lemmas to “make it PASS”.

Each construction records four fields:

1. **Inputs** — allowed atoms only  
2. **Transform** — what the sign manner does to planet function  
3. **Output frame** — structured meaning, not copy  
4. **Missing atom** — `none` or a named type  

### 0.1 Allowed inputs

| Kind | Allowed | Forbidden |
|------|---------|-----------|
| Planet | `object.canon` six slots | `function` · `themes` · `positive_expression` · `shadow` · four-key `domains` used as manner · `tempo` · provenance sentences |
| Sign | `object.canon.manner` · `object.canon.excess` | `mode` / `element` / `orientation` as operators; later-interpretive slots; QUALITY adjectives; “Capricorn = ambition”; `earth` → practical |
| House | presence of a domain slot (inherited 1.3.82) | treating Lilly prose as Canon lemmas |

Classification labels may be **attached**. They do not generate manner.

### 0.2 Transform (diagnostic, not a new engine)

| Construction | Stored modifier | Intended job |
|--------------|-----------------|--------------|
| PlanetInSign | `sign.canon.manner` | Modify **how** an already-known planet function is done |
| PlanetInHouse | house domain slot | **Route** the planet function (still missing lemmas) |

`canon.excess` is the overdone branch of that same manner. Which branch applies is unspecified; that does not block the frame.

---

## 1. Venus × Capricorn — **PASS**

**Inputs**

- Venus `canon.core_function`: `attract` · `value` · `relate`  
- Venus `canon.drive`: `pleasure` · `bond`  
- Capricorn `canon.manner`: `reserved` · `disciplined` · `structured`  
- Capricorn `canon.excess`: `withholding` · `hardening`  
- Capricorn classification (attached, not operator): `mode=cardinal` · `element=earth` · `orientation=negative`

**Transform**

`manner` modifies how `attract/value/relate` is carried. It does not replace Venus with Saturn. It does not read `earth`.

**Output frame**

```text
type:        planet_in_sign
function:    attract / value / relate
drive:       pleasure / bond
manner:      reserved · disciplined · structured
excess:      withholding · hardening
operator:    sign.canon.manner
```

**Missing atom:** none

**Forbidden recovery:** “Venus in Capricorn = reserved / ambitious love.” Ambition is territory, not Canon. `practical` is not on the object.

**Verdict:** PASS

This closes the 1.3.82 Sign gap. 1.3.82 remains the historical PARTIAL snapshot. Do not rewrite that file’s verdict.

---

## 2. Venus × Scorpio — **PASS** (discrimination)

**Inputs**

- Same Venus pack as §1  
- Scorpio `canon.manner`: `intense` · `probing` · `concentrated`  
- Scorpio `canon.excess`: `possessive` · `corrosive`

**Output frame**

```text
type:        planet_in_sign
function:    attract / value / relate
manner:      intense · probing · concentrated
excess:      possessive · corrosive
```

Venus × Capricorn manner ≠ Venus × Scorpio manner. Interchange would FAIL discrimination ([SIGN_CANON_V1.md](./SIGN_CANON_V1.md) §3.4).

**Missing atom:** none  
**Verdict:** PASS

---

## 3. Mercury / Mars / Moon × Capricorn — **PASS** (operator)

Same Capricorn `manner` / `excess` as §1. No Capricorn-specific Mercury, Mars, or Moon lemma.

| Planet | function | manner (unchanged) |
|--------|----------|-------------------|
| Venus | attract · value · relate | reserved · disciplined · structured |
| Mercury | think · communicate · learn | reserved · disciplined · structured |
| Mars | act · pursue · assert | reserved · disciplined · structured |
| Moon | feel · respond · protect | reserved · disciplined · structured |

If a later line needs a new Capricorn atom to make Mercury work, the pack is wrong — do not add a planet-keyed sign atom.

**Missing atom:** none  
**Verdict:** PASS

---

## 4. Mars × Aries vs Mars × Capricorn — **PASS** (classification is not the operator)

Both signs are `mode=cardinal`. Manners differ.

| Sign | mode | manner |
|------|------|--------|
| Aries | cardinal | initiating · direct · headlong |
| Capricorn | cardinal | reserved · disciplined · structured |

Capricorn does not receive `initiating` from cardinal. Mapping `cardinal` → initiating would FAIL this row.

**Missing atom:** none  
**Verdict:** PASS (both frames; distinguishable)

---

## 5. Moon × 4th house — **PARTIAL** (inherited)

Unchanged from 1.3.82. House `domain` is Lilly prose, not House Canon lemmas. 1.3.88 does not repair it.

```text
type:                 planet_in_house
function:             feel / respond / protect
house_arena_lemmas:   null
house_domain_shape:   classical_prose
missing:              house_canon.domain_lemmas
verdict:              PARTIAL
```

**Forbidden recovery:** “Moon in 4th = home and family.”

---

## 6. Scoreboard

| Construction | Verdict | Missing atom |
|--------------|---------|--------------|
| Venus × Capricorn | **PASS** | none |
| Venus × Scorpio | **PASS** | none |
| Mercury × Capricorn | **PASS** | none |
| Mars × Capricorn | **PASS** | none |
| Moon × Capricorn | **PASS** | none |
| Mars × Aries | **PASS** | none |
| Moon × 4th house | **PARTIAL** | House Canon domain lemmas |

Twelve signs each produce a determined Venus × Sign frame from stored `canon.manner`. Manner lists are unique per sign. Classification labels stay attached and unused as operators.

**Sign Canon (two slots):** sufficient as PlanetInSign manner. Do not reopen sign research. Do not pad leftover 1.3.83 families.

**Classification:** stored fact. Not an operator.

**House objects:** still PARTIAL. Named next. Do not start House literature inside this Signs pass.

No FAIL row. No silent repair. No catalog edit.

---

## 7. This pass does not do

- IL-2 engine · runtime wiring · LLM copy  
- New lemmas · pack revision · `function` rewrite · outers · `active`  
- Sign/house object edits · pair catalog rows  
- Inventing `earth → practical` or `cardinal → initiating`  
- House Mainstream / House Canon grammar (map locked 1.3.89; grammar is next)

**Next named:** Houses Mainstream map — **done 1.3.89.** House Canon grammar — **done 1.3.90.** Next = House Canon fill. **STOP Signs.** Do not improve packs without a named Composition Engine failure.

---

## Changelog

- **1.0 (2026-08-22)** — 1.3.88. PlanetInSign PASS from stored manner. Discrimination and operator gates pass. Classification is not the operator. House row remains PARTIAL. Catalog unchanged.
