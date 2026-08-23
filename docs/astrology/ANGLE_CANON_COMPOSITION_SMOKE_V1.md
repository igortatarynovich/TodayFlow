# Angle Canon Composition Smoke V1

**Date:** 2026-08-23  
**Status:** LOCKED (diagnostic). **Not** IL-2. **Not** LLM. **Not** pair essays. **Not** lemma rewrite. **Not** CORE. **Not** a grammar patch. **Not** `active`.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.58. Packs: [ANGLE_CANON_V1.md](./ANGLE_CANON_V1.md) on two angle `object.canon` ([ANGLE_CANON_STORAGE_MATERIALIZATION_V1.md](./ANGLE_CANON_STORAGE_MATERIALIZATION_V1.md)). Grammar: [ANGLE_CANON_GRAMMAR_V1.md](./ANGLE_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). House packs: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md) on house `object.canon` ([HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md](./HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md)). House smoke: [HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./HOUSE_CANON_COMPOSITION_SMOKE_V1.md) (1.3.93 PASS stands; occupancy is not this operator). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md).

This pass answers: **do stored `angle.canon.orientation` plus a planet `canon` yield a deterministic PlanetAtAngle frame without House 1/10 arena, occupancy-as-conjunction, or planet-on-angle prose?** Catalog unchanged. Do not reopen Angles to “improve” packs.

```text
planet.canon.core_function  AT  angle.canon.orientation
  →  deterministic semantic frame  →  verdict
```

Not:

```text
planet IN house.canon.arena
```

No user-facing sentence. No “Mars rising means…”.

---

## Architecture impact

- **SoT before:** 1.3.103 copied locked orientation packs onto two `type=angle` drafts. Next risk: read House 1/10 `arena` as the angle; treat occupancy of the 1st as conjunction with ASC; write planet-on-angle essays to “prove” PASS.
- **SoT after:** live PlanetAtAngle frames read `object.canon.orientation`. Four gates PASS on catalog atoms. House 1.3.93 PlanetInHouse remains the occupancy operator. Catalog unchanged. No grammar invented. **STOP Angles.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.58
- **Backward compatible?** yes (`draft`). Deprecated as next step: improving Angle packs; House 1 = ASC; occupancy = conjunction; Angle literature without a named Composition Engine failure.

---

## 0. Four gates (locked)

| Gate | Check |
|------|--------|
| **Stored source** | `orientation` is `astro.object.asc` / `astro.object.mc` `canon.orientation`. Not markdown. Not `house.canon.arena`. Not 1.3.101 dry-run wording. |
| **Cross-planet composability** | Mars AT ASC and Venus AT ASC use the **same** stored ASC pack. |
| **Operator discrimination** | Mars AT ASC ≠ Mars AT MC ≠ Mars IN 1st ≠ Mars IN 10th. Occupancy ≠ conjunction. |
| **Orientation-only** | Frame carries orientation lemmas. No House 1/10 arena tokens. No appearance / career / mask / profession. No pair essay. |

### 0.1 Verdict rules

Same three values as 1.3.82 / 1.3.88 / 1.3.93 / 1.3.98.

| Verdict | Means |
|---------|--------|
| **PASS** | The frame is produced from allowed atoms. Payload (which function, which chart edge) is on the objects. |
| **PARTIAL** | The construction type is identified, but a named atom type is missing. |
| **FAIL** | Apparent meaning appears only from hidden astrology or a stored pair essay. |

### 0.2 Allowed inputs

| Kind | Allowed | Forbidden |
|------|---------|-----------|
| Planet | `object.canon` six slots | `function` · `themes` · `positive_expression` · `shadow` · provenance sentences as orientation |
| Angle | `object.canon.orientation` | House 1/10 `arena`; Lilly house `domain`; root `orientation` (Lilly polarity); occupancy of 1st/10th as the edge; markdown fill; “Mars conjunct ASC means…” |
| House | inherited 1.3.93 PlanetInHouse (`canon.arena`) as **negative control** | `1st = ASC`; `10th = MC`; using arena as orientation |

House `arena` may be **attached** on the occupancy frame. It does not generate angle orientation.

---

## 1. Stored source — Mars AT ASC — **PASS**

**Inputs**

- Mars `canon.core_function`: `act` · `pursue` · `assert`
- ASC `canon.orientation`: `doorway-meeting` · `how-met` · `automatic-response`

**Transform**

`orientation` hangs a known function on the rising edge. It does not read House 1 `arena`. It does not name a rising-sign portrait.

**Output frame**

```text
type:        planet_at_angle
planet:      mars     core_function={act, pursue, assert}
angle:       asc
orientation: doorway-meeting · how-met · automatic-response
```

**Missing atom:** none

**Forbidden recovery:** “Mars rising means you look aggressive / first impression is fight.” That essay is not on the objects. `appearance` · `first-impression` are House 1 arena, not ASC orientation.

**Verdict:** PASS

---

## 2. Cross-planet — Venus AT ASC — **PASS**

Same stored ASC pack. Different planet function.

| Planet | Function hung on ASC `orientation` |
|--------|-------------------------------------|
| Mars | `act` · `pursue` · `assert` × `doorway-meeting` · `how-met` · `automatic-response` |
| Venus | `attract` · `value` · `relate` × same ASC pack |

The angle does not grow a Mars-keyed or Venus-keyed lemma list. Composability holds.

**Missing atom:** none

**Forbidden recovery:** “Venus rising = pretty face.” Pair essay. `appearance` is House 1.

**Verdict:** PASS

---

## 3. Operator discrimination — **PASS**

### Mars AT ASC ≠ Mars AT MC (same planet)

Difference is **only** `orientation`.

| Angle | `canon.orientation` |
|-------|---------------------|
| ASC | doorway-meeting · how-met · automatic-response |
| MC | culmination · outer-mark · aiming |

Mars function stays `act` · `pursue` · `assert`. ASC does not absorb `culmination`. MC does not absorb `how-met`.

### Mars AT ASC ≠ Mars IN 1st (geometric guard)

Same planet. Different construction.

| Construction | Stored modifier | Type |
|--------------|-----------------|------|
| Mars AT ASC | `orientation`: doorway-meeting · how-met · automatic-response | `planet_at_angle` |
| Mars IN 1st | `arena`: self-presentation · appearance · first-impression | `planet_in_house` |

A planet can occupy House 1 without conjuncting ASC. Occupancy ≠ conjunction. Frames must not match. House 1 `arena` tokens are absent from ASC `orientation`.

### Mars AT MC ≠ Mars IN 10th

| Construction | Stored modifier |
|--------------|-----------------|
| Mars AT MC | culmination · outer-mark · aiming |
| Mars IN 10th | career · public-role · reputation · calling |

Occupancy of the 10th is not conjunction with MC. `career` is not an MC orientation lemma.

**Missing atom:** none

**Verdict:** PASS

---

## 4. Orientation-only — **PASS**

Inspected payload = `canon.orientation` on the two stored angle packs. Not planet `drive`. Not a generated sentence. Not House `arena`.

Absent from every `orientation` list: self-presentation · appearance · first-impression · mask · career · public-role · reputation · calling · profession · personal-facing · public-facing.

No pair-specific prose field on the frame.

**Forbidden recovery:** “ASC = the mask.” “MC = career.” “Planet in 1st = planet on ASC.”

**Verdict:** PASS

---

## 4.1 Locked rows

| Row | Verdict |
|-----|---------|
| Mars AT ASC — **PASS** | stored ASC `orientation` |
| Venus AT ASC — **PASS** | same ASC pack |
| Mars AT ASC ≠ Mars AT MC | operator discrimination |
| Mars AT ASC ≠ Mars IN 1st | Occupancy ≠ conjunction |
| Mars AT MC ≠ Mars IN 10th | Occupancy ≠ conjunction |

**Forbidden recovery:** “Mars rising means you look aggressive.” “MC = career.” “Planet in 1st = planet on ASC.” Those recoveries are not on the objects.

---

## 5. Snapshot — occupancy was never this operator

[HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./HOUSE_CANON_COMPOSITION_SMOKE_V1.md) scored PlanetInHouse PASS from stored `arena`. That is occupancy. This pass does not rewrite those rows. Live PlanetAtAngle reads stored `orientation`. The 1.3.93 rows stay as a snapshot of the occupancy operator.

Do not edit 1.3.93 verdicts to collapse 1st into ASC. Do not treat House PASS as an Angle defect.

---

## 6. This pass does not do

- IL-2 engine · runtime wiring · LLM copy
- New lemmas · pack revision · `function` rewrite · `active`
- DSC / IC objects
- Rising-sign portraits · MC-in-sign careers
- Sign / House / Aspect / Planet pack edits
- Final atomic smoke (next named after STOP Angles)

**Next named:** final atomic smoke (Planet + Sign + House + Aspect + Angle, all stored). Then Knowledge Core V1 FREEZE → IL-2. **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not enrich packs without a named Composition Engine failure.

---

## Changelog

- **1.0 (2026-08-23)** — 1.3.104. Stored Planet × Angle smoke PASS. Four gates. Mars AT ASC ≠ Mars AT MC ≠ Mars IN 1st ≠ Mars IN 10th. Occupancy ≠ conjunction. Catalog unchanged. STOP Angles.
