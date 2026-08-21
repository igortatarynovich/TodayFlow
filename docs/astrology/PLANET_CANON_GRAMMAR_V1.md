# Planet Canon Grammar V1

**Date:** 2026-08-21  
**Status:** LOCKED (grammar + slot semantics). Dry-run packs are **not** locked values. **Not** fill. **Not** JSON. **Not** schema. **Not** objects. **Not** Signs. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.32. Territory: [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). Method: [TODAYFLOW_CANON_V1.md](./TODAYFLOW_CANON_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Time clustering: inventory `KC-T-CLASS` / Foundation `temporal_class`.

This file answers: **which atoms does the Composition Engine need from a planet?** Schema comes later. Old IL keys are not the starting point.

1.3.77 already closed “what contemporary Western astrology usually means by each planet.” Do not reopen planet research.

---

## Architecture impact

- **SoT before:** Mainstream planet territory + concept families locked (1.3.77). Next was “Canon shape.” Shape risked being reverse-engineered from `function` · `themes` · `positive_expression` · `shadow` · `domains` · `tempo`.
- **SoT after:** Planet Canon grammar is **six slots** the engine can compose: `core_function` · `drive` · `needs` · `constructive` · `distorted` · `domains`. `needs` ≠ `drive`. **`tempo` is not a Canon slot** — orbital/transit pace lives in Foundation / runtime metadata (`temporal_class`). Grammar is independent of current JSON Schema. Old IL compatibility is not a constraint. Dry-run on ten planets shows the grammar works; values wait for 1.3.79. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.32 · inventory execution · handoff
- **Backward compatible?** yes for runtime (`draft` ignored). Deprecated as grammar source: current object keys; stuffing astronomy into Canon `tempo`.

---

## 0. Four decisions (this pass only)

1. **Planet Canon grammar exists** as engine atoms, not as a schema patch.
2. **Slots** are named (six in, `tempo` out).
3. **Semantics** of each slot are locked, including `needs` ≠ `drive`.
4. **Dry-run** on Sun–Pluto checks the grammar. Packs are illustrative.

Not this pass: fill · schema · objects · Signs · books · CORE · preserving old IL keys.

---

## 1. Why grammar before schema

Current IL object keys (`function` · `themes` · `positive_expression` · `shadow` · `domains` · `tempo`) describe a **storage shape** from IL-0. They do not describe what composition needs.

| Old key | Why it is not the grammar |
|---------|---------------------------|
| `function` | On drafts this is still classical elemental (heat, moisture). Engine needs a **verb**. |
| `themes` | Bag of nouns. Engine cannot tell process from domain from shadow. |
| `positive_expression` / `shadow` | Close to constructive / distorted, but unlabeled as branches of one function. |
| `domains` | Keep — this *is* a composition atom. |
| `tempo` | Mixes meaning with astronomy (Mars “fast”, Pluto “slow”). See §3. |

**Acceptance (product, not schema):** grammar is good if one planet pack + sign/house/aspect atoms can stably build Profile and Today compositions **without pre-written pair essays**.

That matches [ACM-Compose](../ASTROLOGY_COMPOSITION_MODEL.md): PlanetInSign / AspectPair are derived, not catalogued.

```text
Mars.core_function(act/pursue)  +  Capricorn.mode/element (placeholder)
  →  action expressed through a structured, goal-directed, practical manner

Mars.core_function(act/assert)  +  Saturn.core_function(limit/structure)  +  square(friction)
  →  impulse to act meets constraint / control; resolution required
```

LLM (IL-4) formulates that structure into user language. It does not choose what Mars is.

Sign / house / aspect atoms above are **placeholders**. Signs are not this pass.

---

## 2. Locked slots

| Slot | What it means | Why the engine needs it |
|------|----------------|-------------------------|
| **core_function** | What the planet **does** (process verbs) | Main composition verb |
| **drive** | What that function **aims at** | Motivation; why it moves |
| **needs** | What the function **requires** to run well | Personalization / recommendation; not the same as drive |
| **constructive** | Healthy / productive expression | Positive branch |
| **distorted** | Excess / problem expression | Tension / shadow branch |
| **domains** | Where the function usually shows up | Semantic routing |

Each slot is a short list of **lemmas** (concept families), not a sentence, not a Today line.

### 2.1 `needs` ≠ `drive` (locked)

| | Drive | Needs |
|--|-------|-------|
| Question | What is it going for? | What must be present so it can go for that without distorting? |
| Moon | seek emotional safety | familiarity · emotional responsiveness |
| Saturn | establish order / control | boundaries · realistic constraints |
| Mars | agency · desire · achievement | autonomy · outlet for action |

If a lemma answers “so that…” it is drive. If it answers “without which it goes distorted…” it is needs. Do not copy drive into needs.

### 2.2 Constructive / distorted are branches of the same function

They are not extra planets. Distorted Mars is still `act/assert`, in excess. Do not invent a second Mars in `distorted`.

### 2.3 `core_function` is verbs, `domains` are places/arenas

`act` is function. `competition` is domain. Do not put arenas in `core_function`.

---

## 3. `tempo` is not Canon

Owner constraint: Mars fast / Pluto slow is partly **astronomical / transit**, not intrinsic meaning.

| Layer | Holds | Does not hold |
|-------|-------|----------------|
| **Foundation / runtime** | `temporal_class` (`fast` · `medium` · `slow` · `natal`); orbital period class; transit duration | “what Mars means” |
| **Planet Canon** | the six slots in §2 | speed, generation-length, “this week is slow because Pluto” |

Today **may** use Foundation pace for timing (how long a transit bites). That is calc + metadata, not a seventh meaning slot.

Qualitative manner (`direct` · `activating` vs `diffuse`) is recovered from `core_function` + `constructive` (act vs dissolve vs limit). It is not a separate Canon field in V1.

ACM `merge_tempo(planet.tempo, sign.tempo)` is machine-vector tempo, not this grammar. Do not copy it into Canon.

---

## 4. How a pack is used (not implemented this pass)

```text
calc body
  →  planet pack (six slots)
  →  × sign atoms (later Mainstream + Canon)
  →  × house atoms (later)
  →  × aspect operator (later)
  →  constructive vs distorted branch (aspect / condition)
  →  domains → routing
  →  needs → recommendation / personalization
  →  IL-4 formulates
```

Do not store `Mars in Capricorn` or `Mars square Saturn` as essays.

Old IL compatibility is **not** a fill constraint. Storage is **1.3.80**: nested `canon` with these six names. Do not shrink the grammar to fit `function`/`themes`.

---

## 5. Dry-run (not locked)

Input = 1.3.77 include families. Output = grammar check. **1.3.79 fills.** Do not copy these rows into objects.

Mars follows the owner example. Moon and Saturn show `needs` ≠ `drive`. Remaining packs are the same shape from territory; they are not a second research cycle.

### Sun

```text
core_function:  shine · identify · will
drive:          coherence of self · purpose
needs:          recognition of center · room to exist as oneself
constructive:   vitality · integrity · leadership of own life
distorted:      ego-inflation · domination of others’ center · burnout of will
domains:        identity · vitality · purpose · self-expression
```

### Moon

```text
core_function:  feel · respond · protect
drive:          emotional safety
needs:          familiarity · emotional responsiveness
constructive:   attunement · care · instinctive timing
distorted:      mood-fusion · clinging · reactive withdrawal
domains:        emotions · needs · security · the familiar
```

### Mercury

```text
core_function:  think · communicate · learn
drive:          make sense · exchange information
needs:          input · a channel to speak or write
constructive:   clarity · curiosity · skillful wording
distorted:      noise · overthinking · splitting hairs
domains:        thinking · communication · learning · information
```

### Venus

```text
core_function:  attract · value · relate
drive:          harmony · pleasure · being liked / liking
needs:          reciprocity · something worth valuing
constructive:   affection · taste · fair exchange
distorted:      people-pleasing · indulgence · buying peace
domains:        love · attraction · relationships · values · pleasure
```

### Mars

```text
core_function:  act · pursue · assert
drive:          agency · desire · achievement
needs:          autonomy · outlet for action
constructive:   courage · initiative · decisiveness · healthy assertion
distorted:      aggression · impulsivity · domination · unnecessary conflict
domains:        action · desire · competition · confrontation · sexuality
```

### Jupiter

```text
core_function:  expand · believe · enlarge meaning
drive:          growth · opportunity · a bigger frame
needs:          horizon · something to have faith in
constructive:   generosity · perspective · timely yes
distorted:      excess · inflation · preachy certainty
domains:        growth · opportunity · belief · meaning
```

### Saturn

```text
core_function:  limit · structure · mature
drive:          establish order / control
needs:          boundaries · realistic constraints
constructive:   responsibility · discipline · durable form
distorted:      rigidity · fear-as-rule · punitive control
domains:        limits · work · time · authority · commitment
```

### Uranus

```text
core_function:  disrupt · free · innovate
drive:          independence · a life that is one’s own
needs:          room to differ · a break in the pattern
constructive:   originality · liberation · useful reform
distorted:      revolt without aim · erratic rupture · detachment as superiority
domains:        change · freedom · innovation · the unconventional
```

### Neptune

```text
core_function:  dissolve · imagine · idealize
drive:          union with an ideal · soften hard edges
needs:          inspiration · a permeable but not annihilated boundary
constructive:   compassion · imagination · devotion
distorted:      illusion · drift · self-erasure
domains:        imagination · ideals · sensitivity · the unseen
```

### Pluto

```text
core_function:  intensify · strip · regenerate
drive:          contact with power · irreversible change
needs:          depth · honesty about what cannot stay
constructive:   transformation · regeneration · clean use of power
distorted:      compulsion · control-through-intensity · annihilation of the other
domains:        power · intensity · crisis-and-return · the under-layer
```

Dry-run check: each pack has a verb, an aim, a condition of health, two branches, and arenas. Moon/Saturn/Mars keep drive and needs distinct. No pack uses orbital speed as meaning.

---

## 6. This pass does not do

- Lock the dry-run lemmas as Canon values
- Change JSON Schema or rewrite objects
- Map slots onto `function`/`themes` as if that were compatibility
- Signs / houses / aspects / ASC
- Books · CORE · Co–Star ingest

**Next named (one task):** smoke-test **locked 1.3.82**. Sign map **locked 1.3.83**. Sign grammar **locked 1.3.84**. Sign Canon fill **locked 1.3.85**. Next = Sign Canon storage.

---

## Changelog

- **1.1 (2026-08-21)** — 1.3.79 fill locked in PLANET_CANON_V1.md. Dry-run remains illustrative only.
- **1.0 (2026-08-21)** — 1.3.78. Six Canon slots. `tempo` → Foundation/runtime. `needs` ≠ `drive`. Dry-run only. Grammar before schema.
