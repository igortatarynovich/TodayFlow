# Aspect Canon Composition Smoke V1

**Date:** 2026-08-22  
**Status:** LOCKED (diagnostic). **Not** IL-2. **Not** LLM. **Not** pair essays. **Not** lemma rewrite. **Not** CORE. **Not** a grammar patch. **Not** `active`. **Not** ASC/MC.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.52. Packs: [ASPECT_CANON_V1.md](./ASPECT_CANON_V1.md) on five aspect `object.canon` ([ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md](./ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md)). Grammar: [ASPECT_CANON_GRAMMAR_V1.md](./ASPECT_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Prior smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) (1.3.82 AspectPair PASS stands as a **snapshot** of `interaction` as operator). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md).

This pass answers: **do stored `aspect.canon.relation` plus two planet `canon` packs yield a deterministic AspectPair frame without reading `interaction`, markdown, or pair-specific prose?** Catalog unchanged. Do not reopen Aspects to “improve” packs.

```text
planet.canon.core_function  ×  aspect.canon.relation  ×  planet.canon.core_function
  →  deterministic semantic frame  →  verdict
```

No user-facing sentence. No “Mars square Saturn means…”.

---

## Architecture impact

- **SoT before:** 1.3.82 scored AspectPair PASS from `aspect.interaction` (`friction` vs `flow`). 1.3.97 copied `canon.relation` onto five drafts. Trine and sextile still share `interaction=flow`. Next risk: treat that enum as Canon, or write pair essays to “prove” PASS.
- **SoT after:** live AspectPair frames read `object.canon.relation`. Four gates PASS on catalog atoms. 1.3.82 AspectPair rows stay as a snapshot of the old operator. Sign/House smokes unchanged. Catalog unchanged. No grammar invented. **STOP Aspects.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.52
- **Backward compatible?** yes (`draft`). Deprecated as next step: improving Aspect packs; reading `interaction` as topology; Aspect literature without a named Composition Engine failure.

---

## 0. Four gates (locked)

| Gate | Check |
|------|--------|
| **Stored source** | `relation` is `astro.aspect.*.canon.relation`. Not markdown. Not `interaction`. |
| **Cross-pair composability** | Mars□Saturn and Venus□Saturn use the **same** stored Square pack. |
| **Operator discrimination** | Square ≠ Opposition; Trine ≠ Sextile; Conjunction ≠ Trine. |
| **Topology-only** | Frame carries topology lemmas. No growth / luck / outcome / good-bad / pair-specific prose. |

Trine vs Sextile on **one planet pair** is the regression: both objects keep `interaction=flow`. If that field participates as the operator, the two frames collapse and the test fails.

### 0.1 Verdict rules

Same three values as 1.3.82 / 1.3.88 / 1.3.93.

| Verdict | Means |
|---------|--------|
| **PASS** | The frame is produced from allowed atoms. Payload (two functions, and how they are linked) is on the objects. |
| **PARTIAL** | The construction type is identified, but a named atom type is missing. |
| **FAIL** | Apparent meaning appears only from hidden astrology or a stored pair essay. |

### 0.2 Allowed inputs

| Kind | Allowed | Forbidden |
|------|---------|-----------|
| Planet | `object.canon` six slots | `function` · `themes` · `positive_expression` · `shadow` · provenance sentences as topology |
| Aspect | `object.canon.relation` | `interaction` as operator; `requires_action`; `angle` as topology; markdown fill; pair slogans |
| Sign / House | inherited prior smokes | using house 7 as opposition; using trine as luck |

`interaction` may be **attached** as classical storage. It does not generate `relation`. Draft `requires_action: false` is not “no action needed”.

Planet `drive` may contain words such as Jupiter `growth`. Those are planet atoms, not aspect topology. Topology-only inspects `relation`, not planet drive.

---

## 1. Stored source — Mars □ Saturn — **PASS**

**Inputs**

- Mars `canon.core_function`: `act` · `pursue` · `assert`  
- Saturn `canon.core_function`: `limit` · `structure` · `mature`  
- square `canon.relation`: `friction` · `blockage` · `cross-purposes`  
- square `interaction` (attached, not operator): `friction`

**Transform**

`relation` links two function bundles. It does not read `interaction`. It does not name a pair.

**Output frame**

```text
type:        aspect_pair
planet_a:    mars     core_function={act, pursue, assert}
planet_b:    saturn   core_function={limit, structure, mature}
relation:    friction · blockage · cross-purposes
legacy:      interaction=friction (attached)
```

**Missing atom:** none

**Forbidden recovery:** “Mars square Saturn = delayed action that makes you grow.” That essay is not on the objects.

**Verdict:** PASS

---

## 2. Cross-pair — Venus □ Saturn — **PASS**

Same stored Square pack. Different planet functions.

| Pair | Functions linked under Square `relation` |
|------|------------------------------------------|
| Mars × Saturn | `act` · `pursue` · `assert` × `limit` · `structure` · `mature` |
| Venus × Saturn | `attract` · `value` · `relate` × same Saturn pack |

The aspect does not grow a Mars-keyed or Venus-keyed lemma list. Composability holds.

**Missing atom:** none

**Forbidden recovery:** “Venus square Saturn = cold love.” Pair essay.

**Verdict:** PASS

---

## 3. Operator discrimination — **PASS**

### Square ≠ Opposition (same planets)

Mars □ Saturn vs Mars ☍ Saturn. Difference is **only** `relation`.

| Aspect | `canon.relation` | `interaction` (not operator) |
|--------|------------------|------------------------------|
| Square | friction · blockage · cross-purposes | friction |
| Opposition | polarity · facing · the-other | polarization |

Both poles remain under opposition. Square does not absorb `the-other`. Opposition does not absorb `friction`.

### Trine ≠ Sextile (same pair — regression)

Venus △ Mars vs Venus ✶ Mars. Both objects: `interaction=flow`.

| Aspect | `canon.relation` | `interaction` |
|--------|------------------|---------------|
| Trine | easy-flow · support · **natural-ease** | flow |
| Sextile | **ease-with-participation** · directed-potential · cooperation | flow |

If the frame read `interaction`, both payloads would be `flow` and this row would FAIL. Live frames differ. `flow` is not a `relation` lemma on either pack.

### Conjunction ≠ Trine

Sun ☌ Mercury vs Jupiter △ Sun.

| Aspect | `canon.relation` |
|--------|------------------|
| Conjunction | blend · fuse · immediate-connection |
| Trine | easy-flow · support · natural-ease |

Conjunction pack has no harmonious / difficult lemma. Mixed-valence stays a guard. Quality of fusion waits for the two functions.

**Missing atom:** none

**Verdict:** PASS

---

## 4. Topology-only — **PASS**

Inspected payload = `canon.relation` on the five stored packs. Not planet `drive`. Not a generated sentence.

Absent from every `relation` list: growth · luck · outcome · success · failure · good · bad · harmonious · difficult · challenge · opportunity (as an aspect lemma).

No pair-specific prose field on the frame.

**Forbidden recovery:** “Trine = luck.” “Sextile = opportunity.” “Conjunction is good.”

**Verdict:** PASS

---

## 5. Snapshot — 1.3.82 AspectPair used `interaction`

[PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) scored Mars □ Saturn / Jupiter △ Sun **PASS** because `interaction` distinguished friction vs flow. That was enough **then**. Trine and sextile were not separable under that enum.

The 1.3.82 rows stay. They document the catalog operator **then**. Live AspectPair reads stored `canon.relation`.

Do not edit 1.3.82 verdicts to rewrite history. Do not treat `interaction=flow` as an open Aspect defect.

---

## 6. This pass does not do

- IL-2 engine · runtime wiring · LLM copy  
- New lemmas · pack revision · `function` rewrite · outers · `active`  
- Overwrite `interaction` or `requires_action`  
- Pair catalog rows · minors · orbs  
- ASC/MC maps or objects  
- Sign / House pack edits  

**Next named:** Mainstream Angle Semantic Map — **done 1.3.100.** Angle Canon grammar — **done 1.3.101.** Angle Canon fill — **done 1.3.102.** Angle Canon storage/materialization — **done 1.3.103.** stored Planet×Angle smoke — **done 1.3.104.** **STOP Angles.** Final atomic smoke — **done 1.3.105.** Knowledge Core V1 FREEZE — **done 1.3.106.** Next = IL-2. **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not enrich packs without a named Composition Engine failure.

---

## Changelog

- **1.1 (2026-08-22)** — 1.3.99 Angle Canon model locked. Next = Mainstream Angle Semantic Map.
- **1.0 (2026-08-22)** — 1.3.98. Stored Planet × Aspect smoke PASS. Four gates. Trine vs Sextile on one pair; `interaction=flow` is not the operator. Historical 1.3.82 AspectPair = snapshot. Catalog unchanged. STOP Aspects.
