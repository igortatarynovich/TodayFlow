# House Canon Composition Smoke V1

**Date:** 2026-08-22  
**Status:** LOCKED (diagnostic). **Not** IL-2. **Not** LLM. **Not** pair essays. **Not** lemma rewrite. **Not** Aspect Canon. **Not** CORE. **Not** a grammar patch. **Not** `active`.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.47. Packs: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md) on twelve house `object.canon` ([HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md](./HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md)). Grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Prior smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) · [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md) (1.3.82 / 1.3.88 house PARTIAL rows stand as **snapshots**). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md).

This pass answers: **do stored `house.canon.arena` plus planet `canon` yield a deterministic PlanetInHouse frame without Lilly prose, natural-sign identity, or pair-specific copy?** Historical PARTIAL is a snapshot of an earlier catalog. Do not reopen Signs or Houses to “improve” packs.

```text
planet.canon × house.canon.arena → deterministic semantic frame → verdict
```

No user-facing sentence. No “Moon in the 4th means…”.

---

## Architecture impact

- **SoT before:** 1.3.82 / 1.3.88 scored Moon × 4th PARTIAL — house `domain` was Lilly prose, `arena: null`. 1.3.92 copied packs onto drafts. Next risk: treat Lilly `domain` as the operator, equate 4th with Cancer/Moon/IC, or write pair essays to “prove” PASS.
- **SoT after:** PlanetInHouse frames read `object.canon.arena`. Operator, discrimination, and composability gates PASS on catalog atoms. 1.3.82 AspectPair rows and 1.3.88 PlanetInSign rows unchanged. Historical house PARTIAL in those files is a **snapshot**, not a live failure. Catalog unchanged. No grammar invented. **STOP Houses.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.47
- **Backward compatible?** yes (`draft`). Deprecated as next step: improving House packs; Lilly `domain` as arena; Sign/House literature without a named Composition Engine failure.

---

## 0. Verdict rules (locked)

Same three values as 1.3.82 / 1.3.88.

| Verdict | Means |
|---------|--------|
| **PASS** | The frame is produced from allowed atoms. Payload (what is routed, and where) is on the objects. |
| **PARTIAL** | The construction type is identified, but a named atom type is missing. |
| **FAIL** | Apparent meaning appears only from hidden astrology or a stored pair essay. |

House PARTIAL is **not** live after this pass. 1.3.82 and 1.3.88 keep their PARTIAL rows as historical snapshots.

Each construction records four fields:

1. **Inputs** — allowed atoms only  
2. **Transform** — what the house arena does to planet function  
3. **Output frame** — structured meaning, not copy  
4. **Missing atom** — `none` or a named type  

### 0.1 Allowed inputs

| Kind | Allowed | Forbidden |
|------|---------|-----------|
| Planet | `object.canon` six slots | `function` · `themes` · `positive_expression` · `shadow` · four-key `domains` used as house arena · `tempo` · provenance sentences |
| House | `object.canon.arena` | Lilly `domain` / `people` / `activities` as operators; `1st = ASC`; `4th = Cancer / Moon / IC`; angular arithmetic; “Moon in 4th = …” |
| Sign | `object.canon.manner` · `object.canon.excess` (inherited 1.3.88) | using sign manner as the house |

Lilly `domain` may be **attached** as classical storage. It does not generate arena.

### 0.2 Transform (diagnostic, not a new engine)

| Construction | Stored modifier | Intended job |
|--------------|-----------------|--------------|
| PlanetInHouse | `house.canon.arena` | **Route** an already-known planet function into a chart sphere |
| PlanetInSign | `sign.canon.manner` | Modify **how** (already PASS in 1.3.88) |
| AspectPair | `aspect.interaction` | Relate two functions (already PASS in 1.3.82) |

`planet.canon.domains` is the planet’s own semantic field. It is not the house arena. Do not replace one with the other.

---

## 1. Moon × 4th house — **PASS**

**Inputs**

- Moon `canon.core_function`: `feel` · `respond` · `protect`  
- Moon `canon.drive`: `safety`  
- 4th `canon.arena`: `home` · `family` · `roots` · `private-base`  
- 4th Lilly `domain` (attached, not operator): `father, land, hidden things, and endings`

**Transform**

`arena` routes `feel/respond/protect` into a chart sphere. It does not replace Moon with Cancer. It does not read Lilly `domain`.

**Output frame**

```text
type:        planet_in_house
planet:      moon   core_function={feel, respond, protect}  drive={safety}
arena:       home · family · roots · private-base
payload:     feel/respond/protect  →  home/family/roots/private-base
```

Type of result (not a reading): feeling/protecting is routed into the private base. Branch (`constructive` vs `distorted`) is unspecified; that does not block the frame.

**Missing atom:** none

**Forbidden recovery:** “Moon in 4th = seek emotional security at home.” That essay is not on the objects. Lilly father/land is not the operator.

**Verdict:** PASS

---

## 2. Moon × 10th house — **PASS**

**Inputs**

- Same Moon pack as §1  
- 10th `canon.arena`: `career` · `public-role` · `reputation` · `calling`

**Transform**

Same planet function. Different stored arena. Discrimination is the point of the slot.

**Output frame**

```text
type:        planet_in_house
planet:      moon   core_function={feel, respond, protect}  drive={safety}
arena:       career · public-role · reputation · calling
payload:     feel/respond/protect  →  career/public-role/reputation/calling
```

Moon × 4th arena is not a subset of Moon × 10th arena. `home` is not on the 10th. `career` is not on the 4th.

**Missing atom:** none

**Forbidden recovery:** “Moon in 10th = public mother / career emotions.” Angle identity (`10th = MC`) is not an operator.

**Verdict:** PASS

---

## 3. Mars / Venus × 4th — **PASS**

Same stored 4th pack. Different planet functions.

| Planet | Function routed into 4th arena |
|--------|--------------------------------|
| Mars | `act` · `pursue` · `assert` → `home` · `family` · `roots` · `private-base` |
| Venus | `attract` · `value` · `relate` → same 4th arena |

The house does not grow a Mars-keyed or Venus-keyed lemma list. Composability holds.

**Missing atom:** none

**Forbidden recovery:** “Mars in 4th = fights at home.” Pair essay.

**Verdict:** PASS

---

## 4. Snapshot — 1.3.82 / 1.3.88 house PARTIAL

Those files scored Moon × 4th PARTIAL because `house.canon.arena` was not on the object. The rows stay. They document the catalog **then**. Live PlanetInHouse reads stored arena and is PASS.

Do not edit 1.3.82 or 1.3.88 verdicts to rewrite history. Do not treat those PARTIAL lines as an open House defect.

---

## 5. This pass does not do

- IL-2 engine · runtime wiring · LLM copy  
- New lemmas · pack revision · `function` rewrite · outers · `active`  
- House/Sign object edits · pair catalog rows  
- Inventing `4th = Cancer` or Lilly `domain` as arena  
- Aspect Mainstream / Aspect Canon grammar — map **done 1.3.94**; grammar **done 1.3.95**

**Next named:** Mainstream Aspect Semantic Map V1 — **done 1.3.94.** Aspect Canon grammar — **done 1.3.95.** Next = **Aspect Canon fill**. **STOP Houses.** **STOP Signs.** Do not improve planet/sign/house packs without a named Composition Engine failure.

---

## Changelog

- **1.1 (2026-08-22)** — 1.3.94 map and 1.3.95 Aspect Canon grammar in. Next = Aspect Canon fill. STOP Houses stands.
- **1.0 (2026-08-22)** — 1.3.93. PlanetInHouse PASS from stored `arena`. Moon × 4th ≠ Moon × 10th. Same 4th pack on Moon / Mars / Venus. Historical 1.3.82 / 1.3.88 house PARTIAL = snapshot. Catalog unchanged. STOP Houses.
