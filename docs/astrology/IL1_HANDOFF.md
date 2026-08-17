# IL-1 handoff — next agent

**Date:** 2026-08-17  
**Owner intent:** continue **Interpretation Library IL-1 ingest**. Do not polish the methodology document. Do not reopen sequence / ontology / evidence.

Canon: [`INTERPRETATION_LIBRARY_V1.md`](./INTERPRETATION_LIBRARY_V1.md) (working tree has **1.3.8** activation gates, **not committed** at handoff).  
Today Meaning SoT remains [`docs/today/TODAY_CONTENT_PIPELINE_V1.md`](../today/TODAY_CONTENT_PIPELINE_V1.md). IL is pipeline step 2 lookup only.

Prior chat: [IL-1 ingest and gates](0dd63406-cfcc-47b2-b184-780f5aada991)

---

## 0. First 15 minutes

1. Read this file + IL § Sequence + **Activation gates** + §6 ingest + Layer 2/3/4 fill-rules.
2. **Commit the uncommitted 1.3.8 slice** if still dirty (activation gates). Do **not** mix Profile v2 / Foundation UI / landing / Trust Layer copy into that commit.
3. Prefer a **new short-lived branch from `main`** for further IL ingest. Current branch `cursor/today-scroll-and-number-tap` is a mixed train (Today scroll + IL + Trust Layer + Profile). Do not park IL on it.
4. Then ingest **only newly opened loci**. Next value is collisions, not document prose.

Uncommitted at handoff (include in the 1.3.8 commit if still unstaged):

- `docs/astrology/INTERPRETATION_LIBRARY_V1.md`
- `docs/schemas/astrology_interpretation_v1.schema.json` (descriptions only; type still boolean)
- `backend/tests/test_astrology_interpretation_schema_v1.py` (`test_activation_gates_block_active_ambiguity`)
- `docs/ASTROLOGY_COMPOSITION_MODEL.md` (Layer 5 = candidates)
- `docs/today/TODAY_CONTENT_PIPELINE_V1.md` (one clause)
- `docs/foundation_v1.md` (one clause)
- tracker **NOW (FOUNDATION)** line only — the file also has unrelated Trust/visual hunks; do not stage those

Exclude: `frontend/src/components/profile/v2/**`, `docs/TODAYFLOW_FOUNDATION_UI.md`, landing/Trust copy.

---

## 1. Locked (do not reopen)

Sequence: **IL-0 ✅ → IL-1 now → IL-2 composition rules → IL-3 engine → IL-4 expression**.

- IL-1 is **surface-neutral**: no `today_message` / `profile_blurb` / `compatibility_line`. `surface` exists only on expression packs (IL-4).
- Objects must map to entities the **current Swiss + Astro/calculation layer can emit**. No Uranus/Neptune/Pluto/ASC/MC until a real opened locus **and** calc emits them.
- Swiss = runtime ephemeris input. **Licensing** is a parallel legal gate, not a research blocker. Do not write “Swiss outside IL.”
- If sources do not fit the ontology: **log a concrete gap** from real material. Do **not** expand the schema “just in case.”
- Canonical objects must **not be richer than the evidence base**. Do not polish drafts into a modern average.
- Psychological planet layer waits for **opened** Greene/Hand/etc. — no backfill from model memory.
- Ingest = paraphrase + locus, never paste translations/scrapes.
- Evidence: `core` | `supported` | `school_specific` | `editorial`. CORE ≈ intersection of ingested **school classes**, not two classical authors. Engine primary theme only from `core` ∪ `supported`.
- meaning ≠ relevance ≠ expression. Profile changes **priority**, not meaning. One object feeds Profile / Today / Compatibility.

### Activation gates (not methodology)

Stop **before `status: active`**, not before IL-1 draft.

1. **`requires_action: false`** on an unattested locus ≠ “this aspect does not require action.” Draft + unread by runtime is OK. **`active` with that ambiguity is forbidden** until representation is unambiguous **or** ingest/runtime contract forbids reading the boolean as a negative assertion. Schema stays boolean for IL-1.
2. IL-1 Layer 5 gold list (~50–60) = **curated candidates**, not proven `non_compositional` exceptions. IL-2 may demote curated → composed.

User-facing provenance later = school band (*Traditional* · *Modern psychological* · *Cross-tradition* · *TodayFlow synthesis*), not “Lilly p.57”. That is Trust Layer / Expression, not IL ingest.

Public brand copy SoT: [`docs/content/TODAYFLOW_TRUST_LAYER.md`](../content/TODAYFLOW_TRUST_LAYER.md). Do not turn IL into a marketing doc.

---

## 2. Done

### Git (IL catalog)

| SHA | What |
|-----|------|
| `c9fe3d05` | Schema, corpus, classical seven drafts (Sun–Saturn) |
| `805bbbdb` | 12 houses (Lilly I.7) + 5 aspects (Ptolemy) + sign classifications; signs withheld |
| `b9f2643e` | Lilly I.1 aspect **geometry** compared; I.16 sign QUALITY claims; commanding grouping compared |
| `5dee20a5` | Trust Layer (brand) — **not** IL ingest |

Working tree after that: **1.3.8 activation gates** (see §0).

### Catalog (all `draft`, nothing `active`)

Runtime: `DATA/reference/astrology/interpretation_v1/`

- **24 objects** in `objects_v1.json`: 7 planets · 12 houses · 5 major aspects
- **0** `type=sign` objects
- **37** claim ledgers in `claims/`
- Schema example fixture `status: schema_example` is **not** meaning SoT (modern Saturn lemmas there are not product meaning)

| Layer | IDs | Provenance honesty |
|-------|-----|--------------------|
| 1 planets | `astro.object.{sun,moon,mercury,venus,mars,jupiter,saturn}` | Ptolemy I.4–I.7 + Lilly CA I.8–I.14 |
| 2 signs | **claims only** `astro.sign.{aries…pisces}` + `astro.sign.classifications` | Lilly QUALITY; psych slots unattested |
| 3 houses | `astro.house.01`–`12` | **Lilly CA I.7 only**. Lilly citing “Ptolomeian Doctrine” ≠ Ptolemy+Lilly consensus. Ptolemy I.13 is four-angle temperament, not 12 topical houses |
| 4 aspects | conjunction / sextile / square / trine / opposition | Geometry compared (Ptolemy I.16/I.27 + Lilly I.1). Qualitative labels **not** collapsed into `object.interaction` |
| 5 combos | none materialized | gold list in IL §8 = candidates |

Saturn is deliberately poor vs modern astrology: cooling quality / cold / dryness / slowness / solitude / austerity — **not** structure / limits / maturity.

### Opened loci (citable; ingest only from these)

**Ptolemy, Tetrabiblos**, Ashmand 1822, Gutenberg 70850:

- I.4–I.7 planets
- I.13 four angles (temperament — not 12 houses)
- I.14–I.15 sign classes
- I.16 configurations
- I.17 commanding/obeying (summer/winter grouping **and** equinox pair-relation)
- I.18 beholding / equal power
- I.21 triplicities (winds/rulers, **not** fire/earth/air/water on signs)
- I.27 application / bodily conjunction

**Lilly, Christian Astrology** 1659, Wikisource djvu:

- I.1 aspects, printed p.25–26 (geometry + good/enmity/concord)
- I.7 houses, printed ~p.50–56, djvu 75–81
- I.8–I.14 planets Saturn→Moon
- I.16 divisions, djvu 111–114; nature/quality of 12 signs, printed ~p.93–98
- I.16 commanding list, printed p.91, djvu 117
- I.16 Antiscion / Contrantiscion, printed p.89–91 (cites “PTOL. APHO.” — attribution ≠ consensus)

### Collisions already logged (do not “fix”)

1. Moon/Venus temperature: Ptolemy moisture + moderate heat vs Lilly cold+moist.
2. Mercury: Ptolemy alternates dry/moist vs Lilly native cold/dry melancholy; convertibility compared only as *takes colour from what it joins*.
3. Sun benefic: Ptolemy common vs Lilly fortune-if-dignified.
4. Element: Lilly fire/earth/air/water vs Ptolemy I.21 winds/rulers on the same triangles.
5. Mode: schema `cardinal\|fixed\|mutable` loses Ptolemy tropical vs equinoctial; Lilly glues four as moveable/cardinal (Lilly I.16 nature also calls Aries/Libra equinoctial).
6. Houses: Lilly “Ptolomeian Doctrine” ≠ opened Ptolemy topical houses.
7. `requires_action`: boolean; `false` = not established by opened locus.
8. Aspect quality: Ptolemy harmonious/discordant-by-sex ≠ Lilly good/enmity/concord. Do not copy Lilly labels into `interaction`.
9. Commanding: **grouping** Aries–Virgo vs Libra–Pisces compared. Ptolemy **pair-relation** (equal distance from equinox) stays school_specific.
10. Ptolemy I.18 beholding ≠ Lilly Antiscion + Contrantiscion.
11. Lilly Northern list in the same chapter says six signs but names five (Leo omitted in this scan). Commanding list on p.91 is the compared grouping.
12. Lilly long/short ascension is rising-time technique; opened list puts Aquarius in both — not normalized as Layer 2 meaning.
13. Layer 2 required psych slots (`motivation` / `strengths` / `excess` / `deficiency` / `behavioral_tendencies`) unattested classically — **do not materialize 12 sign objects**.

CORE cannot be scored yet (only two classical school classes opened). Do not teach “Saturn = structure” as CORE.

---

## 3. What to do next

**Only newly opened loci.** Same pipeline: read → paraphrase claim → `gap_notes` on collision → maybe normalize object **if** required slots are attested without invention.

Useful next opens (optional, not a backlog to invent from memory):

- Lilly ~p.105 terms/aspects table (still unopened; noted in aspect `gap_notes`)
- Valens *Anthologies* (in corpus, not opened)
- Skyscript / Houlding (traditional ontology; paraphrase, no scrape)
- Greene / Hand / Sasportas / Arroyo / George — **only after those books are actually opened**

Do **not**:

- polish Saturn/houses/aspects to a modern average
- create Layer 2 sign objects from QUALITY lines
- create Layer 5 combo objects yet (candidates list exists; wait until atoms are denser **or** owner asks — still candidates, not proven exceptions)
- set any object `active`
- wire runtime / Today prompts
- expand schema for `unknown` / `not_evidenced`
- open a parallel “canonical v2”

### Ingest recipe

```text
opened locus
  → claims/<id>.json  (paraphrase + locus + evidence_tier + gap_notes)
  → objects_v1.json   only if required object slots are attested
  → tests in backend/tests/test_astrology_interpretation_schema_v1.py
  → IL changelog patch (1.3.x, “no methodology change”)
```

Validate: host often has no pytest. Use `python3` + `jsonschema` and `exec` the test file with `__file__` set.

Author for commits (do not `git config`): `TodayFlow Agent <agent@todayflow.app>` via env.

### Tests to keep true

- nothing `active`
- no `type==sign` objects
- no surface keys
- no `evidence_tier: core` yet
- aspects: geometry compared; `requires_action is False` cannot be `active`
- houses: Lilly only
- Aries fiery remains `school_specific`, not compared to Ptolemy fire

---

## 4. Parallel trains (not this job)

Leave these alone unless the owner’s query is explicitly about them:

- Profile v2 viewport / recognition scene
- Foundation UI visual language v0.5/v0.6
- Trust Layer landing `#trust` / ads copy
- Today scroll / day-number tap (original reason for branch `cursor/today-scroll-and-number-tap`)

Product authority: canon `docs/` → tracker → **server**. Git is a ledger. `main` is the only product base.

---

## 5. Paste into the next chat

```text
Continue Interpretation Library IL-1 ingest.

Handoff: docs/astrology/IL1_HANDOFF.md
Canon: docs/astrology/INTERPRETATION_LIBRARY_V1.md

LOCKED: sequence IL-0✅ → IL-1 now → IL-2 rules → IL-3 engine → IL-4 expression.
Do not polish the IL document. Do not reopen methodology/ontology/schema.
Do not materialize 12 sign objects. Do not set status=active.
Do not mix Profile/Trust/landing into IL commits.

First: if 1.3.8 activation gates are still uncommitted, commit those six IL files only.
Then: ingest only newly opened loci (same claims → object pipeline). Next value is real collisions, not a modern average.
```
