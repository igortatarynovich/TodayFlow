# Sign Canon V1

**Date:** 2026-08-21  
**Status:** LOCKED (twelve sign packs + provenance + four gates). **Not** JSON. **Not** schema. **Not** objects. **Not** House Canon. **Not** CORE. **Not** a book.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.39. Territory: [MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md). Grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file is the product manner of the twelve signs. 1.3.83 is territory. 1.3.84 is grammar. 1.3.85 is synthesis **with origin control**. Grammar dry-run lemmas are not inherited automatically.

```text
Mainstream territory → manner/excess synthesis → four gates → cross-planet dry-run → lock
```

No new literature. No classification arithmetic. No schema until this dry-run stands.

---

## Architecture impact

- **SoT before:** grammar locked two slots; dry-run lemmas were illustrative. Risk: dump all 1.3.83 families into Canon, or copy ruler `core_function` into sign `manner`.
- **SoT after:** each Canon atom is `direct` / `direct-secondary` / `derived` from that sign’s locked 1.3.83 families. Four gates pass. Unused families stay in territory. Catalog untouched. Schema still later.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.39 · grammar next-pointer · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated: treating 1.3.84 dry-run wording as locked values; filling every territory family for symmetry.

---

## 0. Origin rule (locked)

Same tags as Planet Canon fill.

| Origin | Means | Does not mean |
|--------|-------|----------------|
| **direct** | Normalization of a 1.3.83 **include** family (same concept, shorter lemma) | Copied vendor sentence |
| **direct-secondary** | Normalization of a 1.3.83 **secondary** family | A second stem that displaces include |
| **derived** | TodayFlow inference from **two or more** locked families of **this** sign | A new astrology; a school package; Google |

`derived` is not weaker. It marks where our model starts.

**Reject** if: not in that sign’s 1.3.83 families even as parents; answers «что делает?» instead of «как?»; copies the domicile ruler’s `core_function`; uses `mode` / `element` / `orientation` as proof; or is user-facing copy.

Pipeline per atom:

```text
lemma → direct | direct-secondary | derived → parent family/families → four gates → keep / rewrite / drop
```

---

## 1. Four gates (locked)

1. **Origin control** — every `manner` / `excess` atom is a 1.3.83 include or secondary on that sign, or derived only from those families. No classification arithmetic. No fourth panel. No books.
2. **Operator test** — the lemma must naturally modify **several** planet functions, not only one convenient pair. Capricorn manner must work on Venus, Mercury, Mars, and Moon **without new sign-specific трактовок**.
3. **Domicile collision test** — the lemma answers «как?», not «что делает?». Do not restate the ruling planet’s `core_function` as the sign’s `manner` ([grammar §2.3](./SIGN_CANON_GRAMMAR_V1.md)).
4. **Discrimination test** — adjacent / contrast signs must give a distinguishable manner of the **same** planet. Venus × Capricorn must not be interchangeable with Venus × Scorpio.

Coverage is **not** “every 1.3.83 family placed.” Expected: **2–3** manner atoms and **1–2** excess atoms per sign. Leftover families stay recognizable as territory.

---

## 2. Locked packs

Parents use 1.3.83 family names. Grammar dry-run rejects are listed once in §4.

Planet `core_function` atoms used in dry-runs are from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md): Venus `attract · value · relate` · Mercury `think · communicate · learn` · Mars `act · pursue · assert` · Moon `feel · respond · protect`.

### Aries

Territory used: initiative / start · impulsiveness · directness.  
Left in territory: courage · leading / first · energy / activity · independence · impatience · competitive / challenge · willpower.

```text
manner:  initiating · direct · headlong
excess:  premature-charge · over-direct
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| initiating | manner | direct | initiative / start |
| direct | manner | direct-secondary | directness |
| headlong | manner | direct | impulsiveness |
| premature-charge | excess | derived | initiative / start + impulsiveness |
| over-direct | excess | derived | directness + impulsiveness |

**Domicile:** not `act` / `assert` (Mars). `initiating` is Cafe-on-Aries, not cardinal arithmetic.  
**Operator:** Venus values by starting and going straight; Mercury thinks by cutting to the point; Mars acts by starting (manner, not a second Mars); Moon feels by moving first.

### Taurus

Territory used: slow-and-steady · steadfast / persevering · patient · stubborn / immovable · possession / having.  
Left in territory: stability / security · sensual / pleasure · comfort / material ease · dependable.

```text
manner:  slow-and-steady · steadfast · patient
excess:  immovable · over-holding
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| slow-and-steady | manner | direct | slow-and-steady |
| steadfast | manner | direct | steadfast / persevering |
| patient | manner | direct-secondary | patient |
| immovable | excess | direct-secondary | stubborn / immovable |
| over-holding | excess | derived | steadfast / persevering + possession / having |

**Domicile:** not `attract` / `value` / `relate` (Venus). `sensual` dropped — operator-fails on Mercury and smears Venus.  
**Operator:** Venus values slowly and holds; Mercury thinks without rushing the conclusion; Mars acts with stamina; Moon feels without dropping the bond.

### Gemini

Territory used: versatility · mobility / rarely-settling · changeable / dual.  
Left in territory: communication · curiosity / learning · wit · sociable · superficial · restless schedule.

```text
manner:  mobile · versatile · switching
excess:  scattered · unstaying
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| mobile | manner | direct | mobility / rarely-settling |
| versatile | manner | direct | versatility |
| switching | manner | derived | changeable / dual + mobility / rarely-settling |
| scattered | excess | derived | versatility + mobility / rarely-settling |
| unstaying | excess | derived | mobility / rarely-settling + changeable / dual |

**Domicile:** not `think` / `communicate` / `learn` (Mercury). Communication stays territory.  
**Operator:** Venus relates by changing channel; Mercury thinks by moving across topics; Mars acts by switching approach; Moon feels in more than one register.

### Cancer

Territory used: closeness · protection / holding-on · indirect approach.  
Left in territory: feeling / emotional · safety / security-of-bond · home / family · nurturing · sensitive / shy · imagination · mood.

```text
manner:  close · indirect · holding
excess:  clinging · sideways-defense
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| close | manner | direct | closeness |
| indirect | manner | direct-secondary | indirect approach |
| holding | manner | direct | protection / holding-on |
| clinging | excess | derived | closeness + protection / holding-on |
| sideways-defense | excess | derived | indirect approach + protection / holding-on |

**Domicile:** not `feel` / `respond` / `protect` as verbs (Moon). `holding` is how a function is kept (does not release), not Moon’s verb `protect`. Home/family stays arena.  
**Operator:** Venus values through closeness and not-letting-go; Mercury thinks sideways and near the bond; Mars acts by holding a line rather than charging; Moon feels by staying close (manner, not a second Moon).

### Leo

Territory used: centrality / being-seen · warmth · creative display · need for appreciation.  
Left in territory: generosity · pride / dignity · leadership / regal manner · loyalty · drama / flair · big-picture.

```text
manner:  central · warm · displayed
excess:  over-display · center-demand
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| central | manner | direct | centrality / being-seen |
| warm | manner | direct | warmth |
| displayed | manner | direct | creative display |
| over-display | excess | derived | centrality / being-seen + creative display |
| center-demand | excess | derived | centrality / being-seen + need for appreciation |

**Domicile:** not `identify` / `vitalize` / `will` / `shine` (Sun). Generosity dropped — operator-fails on Saturn.limit.  
**Operator:** Venus values in the open and warmly; Mercury thinks as something to be seen; Mars acts from center stage; Moon feels where it can be received.

### Virgo

Territory used: precision / detail · discernment / differentiation · utility / useful · critique / analytical.  
Left in territory: service / helpful · conscientious · reserved · perfectionist · crafts / making-well.

```text
manner:  precise · discerning · utilitarian
excess:  over-critique · over-refine
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| precise | manner | direct | precision / detail |
| discerning | manner | direct | discernment / differentiation |
| utilitarian | manner | direct | utility / useful |
| over-critique | excess | derived | discernment / differentiation + critique / analytical |
| over-refine | excess | derived | precision / detail + critique / analytical |

**Domicile:** not `think` / `communicate` / `learn` (Mercury). Virgo manner is how sorting is done, not a second Mercury.  
**Operator:** Venus values by sorting what is useful; Mercury thinks by differentiating; Mars acts with exactness; Moon feels by checking what holds.

### Libra

Territory used: balance / proportion · tact / diplomacy · indecision · harmony.  
Left in territory: relating / companionship · fairness / justice · beauty / aesthetic · charm / likable · refined.

```text
manner:  balancing · tactful · proportionate
excess:  indecision · over-accommodation
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| balancing | manner | direct | balance / proportion |
| tactful | manner | direct-secondary | tact / diplomacy |
| proportionate | manner | derived | balance / proportion + harmony |
| indecision | excess | direct-secondary | indecision |
| over-accommodation | excess | derived | harmony + tact / diplomacy |

**Domicile:** not `attract` / `value` / `relate` (Venus). Beauty stays arena. Relating stays Venus.  
**Operator:** Venus values by weighing both sides; Mercury thinks by keeping proportion; Mars acts without breaking the other; Moon feels with tact.

### Scorpio

Territory used: intensity · probing / seeing-through · possessive · extremes.  
Left in territory: passion · will / determination · secrecy / self-protective · resourceful · psychological depth · transformation.

```text
manner:  intense · probing · concentrated
excess:  possessive · corrosive
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| intense | manner | direct | intensity |
| probing | manner | direct | probing / seeing-through |
| concentrated | manner | derived | intensity + probing / seeing-through |
| possessive | excess | direct-secondary | possessive |
| corrosive | excess | derived | intensity + extremes |

**Domicile:** not `intensify` / `transform` / `regenerate` (Pluto). `intense` / `probing` are how, not Pluto’s verb. Passion stays planet-stem.  
**Operator:** Venus values by going through rather than around; Mercury thinks by probing; Mars acts with concentrated force; Moon feels without dilution.

### Sagittarius

Territory used: freedom · exploration / adventure · movement / wanderlust · restless · excess.  
Left in territory: optimism / cheer · meaning-seeking / philosophy · honest / outspoken · faith in possibility.

```text
manner:  exploratory · free · far-ranging
excess:  uncommitted-ranging · overshoot
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| exploratory | manner | direct | exploration / adventure |
| free | manner | direct | freedom |
| far-ranging | manner | derived | movement / wanderlust + exploration / adventure |
| uncommitted-ranging | excess | derived | freedom + restless |
| overshoot | excess | derived | movement / wanderlust + excess |

**Domicile:** not `expand` / `believe` (Jupiter). Meaning-seeking stays Jupiter.drive. `free` here is unconstrained ranging of an already-known function, not Uranus `free` (the function of breaking constraint).  
**Operator:** Venus values by looking farther; Mercury thinks toward a horizon; Mars acts by ranging; Moon feels without being fenced.

### Capricorn

Territory used: discipline / self-discipline · reserved / serious · structure / organization.  
Left in territory: ambition / achievement · endurance / tenacity · purpose / goal · practical · responsibility / duty · conservative / tradition · recognition / status · resourceful.

```text
manner:  reserved · disciplined · structured
excess:  withholding · hardening
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| reserved | manner | direct | reserved / serious |
| disciplined | manner | direct | discipline / self-discipline |
| structured | manner | direct-secondary | structure / organization |
| withholding | excess | derived | reserved / serious + discipline / self-discipline |
| hardening | excess | derived | discipline / self-discipline + structure / organization |

**Domicile:** not `limit` / `mature` as Saturn’s verbs. `structured` is how another planet proceeds, not Saturn `structure` as the function itself. Ambition / achievement / purpose / status stay directional-trait. `practical` and `enduring` are operator-fit leftovers — not required once the three manner atoms discriminate.  
**Operator (locked, same three atoms, no Capricorn-specific rewrite):**

```text
Venus    value · relate     × reserved · disciplined · structured
Mercury  think · communicate × reserved · disciplined · structured
Mars     act · assert       × reserved · disciplined · structured
Moon     feel · protect     × reserved · disciplined · structured
```

Valuing, thinking, acting, and feeling are still the planet’s job. Capricorn only names the manner.

### Aquarius

Territory used: detachment / cool · invention / unconventional · individuality / original.  
Left in territory: progressive / future-facing · humanitarian / the-group · independent · intellectual · eccentric · friendly-but-selective · idealistic.

```text
manner:  detached · unconventional · original
excess:  cold-distance · idea-obstinacy
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| detached | manner | direct | detachment / cool |
| unconventional | manner | direct | invention / unconventional |
| original | manner | direct | individuality / original |
| cold-distance | excess | derived | detachment / cool + individuality / original |
| idea-obstinacy | excess | derived | invention / unconventional + individuality / original |

**Domicile:** not `disrupt` / `free` / `innovate` (Uranus). Humanitarian stays arena. `original` is how a function is authored, not Uranus `innovate` as the function.  
**Operator:** Venus values at a remove and off-pattern; Mercury thinks unconventionally; Mars acts from an original line; Moon feels without fusing.

### Pisces

Territory used: imagination / inner-world · adaptability / hard-to-hold · permeability / flowing.  
Left in territory: sensitivity · compassion · artistic / poetic · dreamy · spiritual / faith-seeking · helpful / devoted · intuition.

```text
manner:  permeable · imaginal · adaptive
excess:  unfocused · impression-as-fact
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| permeable | manner | direct | permeability / flowing |
| imaginal | manner | direct | imagination / inner-world |
| adaptive | manner | direct | adaptability / hard-to-hold |
| unfocused | excess | derived | adaptability / hard-to-hold + permeability / flowing |
| impression-as-fact | excess | derived | imagination / inner-world + permeability / flowing |

**Domicile:** not `dissolve` / `imagine` / `idealize` as verbs (Neptune). `imaginal` is how a function is carried (image-led), not Neptune `imagine`. Compassion stays character. Sensitivity not taken (Moon smear).  
**Operator:** Venus values by letting edges blur; Mercury thinks with image in the lead; Mars acts by adapting around the obstacle; Moon feels without a hard rim.

---

## 3. Four-gate audit

### 3.1 Origin control

Every parent in §2 is an include or secondary family on that sign’s 1.3.83 row. No `earth` → practical. No `cardinal` → initiating. No fourth panel.

Aries `initiating` is Cafe-on-Aries. Capricorn does not inherit it. Capricorn `structured` is Cafe “sign of organization”, not earth-dump. Pisces `adaptive` is Astrodienst-on-Pisces, not mutable-dump. Gemini `adaptable` was not copied onto Virgo or Pisces.

### 3.2 Operator test

Target construction: **one Capricorn pack, four planet inputs.**

| Construction | Frame (same sign atoms) |
|--------------|-------------------------|
| Venus × Capricorn | valuing / relating done reservedly, with discipline, inside a structure |
| Mercury × Capricorn | thinking / communicating done reservedly, with discipline, inside a structure |
| Mars × Capricorn | acting / asserting done reservedly, with discipline, inside a structure |
| Moon × Capricorn | feeling / protecting done reservedly, with discipline, inside a structure |

No Capricorn-specific Venus essay. No Capricorn-specific Mercury essay. If a later line needs a new Capricorn lemma to make Mercury work, the pack is wrong — do not add a planet-keyed sign atom.

Spot checks (same rule, not extra packs):

| Sign manner | Venus | Mercury | Mars | Moon |
|-------------|-------|---------|------|------|
| Aries initiating · direct · headlong | start-and-straight valuing | cut-to-the-point thought | start-and-straight action | first-move feeling |
| Gemini mobile · versatile · switching | channel-changing relating | topic-moving thought | approach-switching action | multi-register feeling |
| Scorpio intense · probing · concentrated | through-not-around valuing | probing thought | concentrated force | undiluted feeling |
| Pisces permeable · imaginal · adaptive | edge-blur valuing | image-led thought | adaptive action | rimless feeling |

### 3.3 Domicile collision

| Sign | Forbidden (ruler already does this) | Kept as how |
|------|-------------------------------------|-------------|
| Aries | `act` / `assert` (Mars) | initiating · direct · headlong |
| Taurus | `attract` / `value` / `relate` (Venus) | slow-and-steady · steadfast · patient |
| Gemini | `think` / `communicate` / `learn` (Mercury) | mobile · versatile · switching |
| Cancer | `feel` / `respond` / `protect` (Moon) | close · indirect · holding |
| Leo | `identify` / `vitalize` / `will` (Sun) | central · warm · displayed |
| Virgo | `think` / `communicate` / `learn` (Mercury) | precise · discerning · utilitarian |
| Libra | `attract` / `value` / `relate` (Venus) | balancing · tactful · proportionate |
| Scorpio | `intensify` / `transform` (Pluto) | intense · probing · concentrated |
| Sagittarius | `expand` / `believe` (Jupiter) | exploratory · free · far-ranging |
| Capricorn | `limit` / `mature` (Saturn) | reserved · disciplined · structured |
| Aquarius | `disrupt` / `innovate` (Uranus) | detached · unconventional · original |
| Pisces | `dissolve` (Neptune) | permeable · imaginal · adaptive |

Close calls kept with a how/what split: Capricorn `structured` ≠ Saturn `structure`; Pisces `imaginal` ≠ Neptune `imagine`; Sagittarius `free` ≠ Uranus `free`; Cancer `holding` ≠ Moon `protect`.

### 3.4 Discrimination

Same planet, different sign. Frames must not swap.

| Pair | Difference |
|------|------------|
| Venus × Capricorn vs Venus × Scorpio | reserved / disciplined / structured vs intense / probing / concentrated |
| Venus × Capricorn vs Venus × Taurus | reserved / structured vs slow-and-steady / steadfast / patient |
| Venus × Libra vs Venus × Taurus | balancing / tactful vs slow-and-steady / steadfast |
| Venus × Leo vs Venus × Aries | central / warm / displayed vs initiating / direct / headlong |
| Mercury × Gemini vs Mercury × Pisces | mobile / switching vs permeable / imaginal |
| Mercury × Gemini vs Mercury × Virgo | mobile / switching vs precise / discerning |
| Mercury × Capricorn vs Mercury × Gemini | reserved / structured vs mobile / switching |
| Mars × Aries vs Mars × Capricorn | initiating / headlong vs reserved / disciplined / structured |
| Mars × Aries vs Mars × Scorpio | initiating / direct vs intense / concentrated |
| Moon × Cancer vs Moon × Capricorn | close / holding vs reserved / structured |
| Moon × Cancer vs Moon × Pisces | close / holding vs permeable / adaptive |
| Saturn × Aquarius vs Saturn × Capricorn | detached / unconventional vs reserved / structured |

Capricorn has no `initiating`. That is discrimination, not a missing family.

---

## 4. Dry-run / territory rejects (do not revive)

| Lemma or family | Why out |
|-----------------|---------|
| Capricorn `ambition` / `achievement` / `purpose` / `recognition / status` | Directional / trait. Venus×Capricorn is not “Venus wants achievement.” |
| Capricorn `practical` / `enduring` as extra manner | Operator-fit, but three manner atoms already discriminate. Do not pad. |
| Capricorn excess `worth-made-conditional` | Grammar example; parents would lean on status. Use `withholding` · `hardening`. |
| Aries `assert` / `act` | Mars `core_function`. |
| Aries `leading` / `courage` / `competitive` | Identity / character, not operator. |
| Aries excess `combative-heat` | Competitive-as-character. Use `premature-charge` · `over-direct`. |
| Taurus `sensual` as manner | Venus-smear; operator-fails on Mercury. |
| Gemini `communicate` / `think` | Mercury `core_function`. |
| Gemini `wit` | Personality, not operator. |
| Cancer `feel` / `protect` as verbs | Moon `core_function`. |
| Cancer `home/family` | House arena. |
| Leo `shine` / `identify` | Sun `core_function`. |
| Leo `generous` as manner | Operator-fails on Saturn.limit. |
| Virgo `communicate` | Mercury; Virgo mental family is discernment. |
| Libra `relate` / `beauty` | Venus / arena. |
| Scorpio `transform` | Pluto `core_function`. |
| Sagittarius `expand` | Jupiter `core_function`. |
| Sagittarius excess `preach from the road` | User copy. Use `uncommitted-ranging` · `overshoot`. |
| Aquarius `disrupt` | Uranus `core_function`. |
| Aquarius `humanitarian` | Arena. |
| Pisces `dissolve` | Neptune `core_function`. |
| Pisces `compassion` | Character, not operator. |
| Any `earth` / `cardinal` / `mutable` operator | Classification is stored fact, not Canon. |

1.3.84 grammar examples still hold as **slot semantics**. Their wording is replaced by the atoms above where the two differ.

---

## 5. Cross-planet dry-run (locked as fill-check, not as stored pairs)

Do not copy these rows into objects. Do not write `Venus in Capricorn` essays. LLM (IL-4) formulates later.

### Venus × Capricorn

```text
planet:   value · relate
manner:   reserved · disciplined · structured
excess:   withholding · hardening
frame:    valuing/relating done reservedly, with discipline, inside a structure
out:      ambition · achievement · purpose · status
```

### Venus × Scorpio

```text
planet:   value · relate
manner:   intense · probing · concentrated
excess:   possessive · corrosive
frame:    valuing/relating that goes through rather than around
out:      transformation-as-identity · passion as planet-stem
```

Same planet. Difference is **only** sign.manner. The two frames cannot be swapped.

### Mercury × Capricorn

```text
planet:   think · communicate
manner:   reserved · disciplined · structured
excess:   withholding · hardening
frame:    thought/speech done reservedly, with discipline, inside a structure
```

Same Capricorn atoms as Venus × Capricorn. No Mercury-in-Capricorn lemma.

### Mars × Capricorn

```text
planet:   act · assert
manner:   reserved · disciplined · structured
excess:   withholding · hardening
frame:    action done reservedly, with discipline, inside a structure
```

### Moon × Capricorn

```text
planet:   feel · protect
manner:   reserved · disciplined · structured
excess:   withholding · hardening
frame:    feeling/protecting done reservedly, with discipline, inside a structure
```

### Mercury × Gemini vs Mercury × Pisces

```text
Gemini:   mobile · versatile · switching     → thought that changes channel
Pisces:   permeable · imaginal · adaptive    → thought that lets image lead
```

### Mars × Aries vs Mars × Capricorn

```text
Aries:      initiating · direct · headlong
Capricorn:  reserved · disciplined · structured
```

Capricorn does not receive `initiating` from cardinal.

---

## 6. This pass does not do

- JSON / schema / `object.canon` on signs / `active`
- Repeat 1.3.82 smoke-test (needs storage first; Venus × Capricorn stays PARTIAL until then)
- House Mainstream map / House Canon
- Reopen 1.3.83 research · books · CORE · Co–Star ingest
- Repair PARTIAL by writing manner onto catalog objects
- Fill leftover territory families for symmetry

**Next named:** Sign Canon storage (schema nest for `manner` · `excess`) — **done 1.3.86.** Sign Canon materialization — **done 1.3.87.** Planet × Sign smoke-test — **done 1.3.88.** Houses Mainstream map — **done 1.3.89.** House Canon grammar — **done 1.3.90.** Next = House Canon fill. STOP Signs.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.85. Twelve packs locked. Origin direct / direct-secondary / derived. Four gates. Cross-planet dry-run. Dry-run not auto-Canon. Unused families stay in territory.
