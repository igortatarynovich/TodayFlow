# Mainstream Sign Semantic Map V1

**Date:** 2026-08-21  
**Status:** LOCKED (territory + concept families). **Not** TodayFlow Canon. **Not** JSON. **Not** schema. **Not** objects. **Not** CORE. **Not** a book. **Not** manner operators.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.37. Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). Planet analog: [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). Smoke finding: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md). Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md).

This file is the Mainstream V1 **sign** map. It names concept families a contemporary user already treats as “what this sign is like.” It does not dump twelve personality portraits into objects. It does not invent a private astrology.

The consumer is already known (1.3.82): Sign Canon must later answer **how a sign modifies a planet function**, not “which Capricorn personality.” This pass still only locks **territory**. It does not decide which families become manner, and it does not apply them to Venus.

---

## Architecture impact

- **SoT before:** 1.3.82 named a missing Sign Canon manner operator. Risk: fill signs from Lilly QUALITY, from `earth` → practical / `cardinal` → initiating, or as 12 personality keyword dumps.
- **SoT after:** bounded panel is the same as planets — **Astrodienst · Cafe Astrology · Astrology.com**. Mainstream signs = **concept families**, not word-counting, not classification arithmetic. Include / secondary / exclude locked per sign. Trait ≠ manner is named as a later grammar control, not executed here. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.37 · inventory execution order · handoff
- **Backward compatible?** yes. Sign objects stay classification-only. `mode` / `element` / `orientation` remain stored facts, not proof of this map.

---

## 0. What this is / is not

| This file | Not this file |
|-----------|----------------|
| Semantic **territory** | Sign Canon (generative slots) |
| Concept families | JSON objects |
| Include / secondary / exclude | Cross-school CORE |
| One finite sign pass | House / aspect / ASC/MC maps |
| Input to later **manner** grammar | Assignment of manner vs trait |

Opposite error, also forbidden: paste the table below into `objects_v1.json` as QUALITY, `themes`, or later-interpretive prose.

Uniqueness of TodayFlow comes later, as **structuring** of this convention for composition (`Venus × Capricorn`, `Mars × Aries`) — not as a different Capricorn.

### 0.1 Known consumer (do not execute here)

1.3.82: PlanetInSign needs a **manner operator**. The question is not “what is Capricorn?” but “how does Capricorn modify a planet function?”

Example that this file **must not decide**:

```text
mainstream Capricorn may include: ambitious · disciplined · practical · reserved · responsible

trait / motivation (maybe later out of Sign Canon):  ambitious
possible manner (maybe later in):                   structured / practical / controlled
PlanetInSign example (not locked here):             Venus.value + Capricorn.structured/practical manner
```

1.3.84 Sign Canon Grammar splits territory into those roles. This pass only names the convention.

### 0.2 Classification is not proof

Existing `element` · `mode` · `orientation` may **later explain** a family. They must not **generate** one.

Forbidden this pass:

```text
earth     → practical
cardinal  → initiating
fixed     → stubborn
mutable   → adaptable
water     → emotional
fire      → impulsive
```

If a family is include, it is because the panel independently points at that sign’s territory. Aries may include initiating because Cafe lists it on **Aries**. Capricorn must not receive initiating because it is also cardinal.

Cafe’s shared element dump (“Earth signs are reliable, practical, and sensual”) is **not** evidence for Taurus, Virgo, or Capricorn. Use only what those sign pages say about **that** sign.

---

## 1. Bounded panel (locked)

Same encyclopedia / mass-reference class as 1.3.77. Not a school. Not a monograph. Not Layer 2 portrait books.

| # | Source | Pages opened this pass | Role |
|---|--------|------------------------|------|
| 1 | **Astrodienst** | [A Brief Introduction: the Signs](https://www.astro.com/astrology/in_signs_e.htm) | Compact modern keyword line per sign + backdrop note that signs color planetary positions |
| 2 | **Cafe Astrology** | Sign pages `zodiac{sign}.html` (Aries–Pisces) | Modern popular keywords + Sun-in-sign body. Planet-in-sign / compatibility **out** as evidence |
| 3 | **Astrology.com** | [Zodiac signs index](https://www.astrology.com/zodiac-signs) · [Aries](https://www.astrology.com/zodiac-signs/aries) · [Capricorn](https://www.astrology.com/zodiac-signs/capricorn) | Mass contemporary reference |

Astrodienst also says signs are understood via elements and ruling planets. That is classification pedagogy, not a license to derive this map from `element` / ruler identity.

**Recognition check (not a panel source):** Co–Star 101. Ask after a family is named: would a contemporary user recognize this?

Do not ingest vendor paragraphs into `claims/`. Cite concept → source.

**Evidence hygiene on Cafe:** Sun-in-sign and the sign’s own keyword line count. Moon/Mercury/Venus/Mars-in-sign and “man/woman” love pages do not. House-association dumps do not. Anatomy / metal / stone do not.

---

## 2. How “mainstream” is judged (no bureaucracy)

**Wrong:** require each lemma to appear as the same string in 2/3 sources.

**Right:** sources sketch a **territory**. Near-synonyms collapse to one **concept family**.

Examples of one family, not three lemmas:

- initiative · starting · first to begin · pioneering → **initiative / start**
- steadfast · stable · staying power · plodding persistence → **steadfast / stable**
- ambitious · achievement · get to the top · sense of purpose → **ambition / achievement / purpose**

A family is **include** when the panel independently points at that territory (wording may differ).  
A family is **secondary** when it is present but not the first modern association, or it is a mass shorthand / ruler-overlap of the include family.  
A family is **exclude** when it is one school, one author, medical/body dump, compatibility, planet-in-sign recipe, house=sign, ruler=sign, or classification arithmetic.

LLM (build-time, supplied field only) may propose family collapse. It does not add a fourth source, vote Google, or lock.

---

## 3. Territory table (locked)

First term = central contemporary association. This is **not** Canon. This is **not** manner.

| Sign | Mainstream territory |
|------|----------------------|
| Aries | initiative · energy · courage · impulsiveness · leading |
| Taurus | stability · sensuality · steadfastness · security · possession |
| Gemini | communication · curiosity · versatility · mobility · wit |
| Cancer | closeness · feeling · safety · home/family · protection |
| Leo | centrality · generosity · pride · creative display · warmth |
| Virgo | precision · discernment · utility · service · critique |
| Libra | balance · harmony · relating · fairness · beauty |
| Scorpio | intensity · probing · passion · will · extremes |
| Sagittarius | freedom · exploration · optimism · meaning-seeking · movement |
| Capricorn | ambition · discipline · endurance · purpose · achievement |
| Aquarius | individuality · progressive · humanitarian · detachment · invention |
| Pisces | sensitivity · compassion · imagination · adaptability · permeability |

Discrimination that the table must keep: Cancer **closeness/feeling** vs Taurus **stability/security**; Aries **initiative/leading** vs Capricorn **ambition/achievement** (Capricorn is not given initiating); Gemini **mobility/wit** vs Aquarius **individuality/humanitarian**; Virgo **critique/utility** vs Libra **fairness/harmony**; Scorpio **intensity/probing** vs Aries **drive**.

---

## 4. Concept families (locked)

Panel notes are paraphrases, not copy. Compact Astrodienst line is the reference paragraph; the same page’s children’s portraits are not the stem.

### Aries

| | Families |
|--|----------|
| **Include** | initiative / start · energy / activity · courage · impulsiveness · leading / first |
| **Secondary** | independence · impatience · competitive / challenge · willpower · directness |
| **Exclude** | Aries = Mars · fire → impulsive · cardinal → initiating · head/anatomy · compatibility · career lists (military/startups) |

Astrodienst compact: willpower, impulsive, initiative, courage, energy, activity. Cafe keywords: active, initiating, leading, independent, aggressive, impatient, energetic, pioneering, assertive. Astrology.com: bold, independent, passionate, determined, impulsive; first-sign / leadership / forward motion.

`initiating` is include because Cafe names it on **Aries**, not because Aries is cardinal.

### Taurus

| | Families |
|--|----------|
| **Include** | stability / security · steadfast / persevering · sensual / pleasure · possession / having · slow-and-steady |
| **Secondary** | stubborn / immovable (mass shorthand of steadfast) · comfort / material ease · dependable · patient |
| **Exclude** | earth → practical · Taurus = Venus · neck/throat · “stubborn as a bull” as the only stem · compatibility · planet-in-sign recipes |

Astrodienst compact: sensual, pleasure-seeker, steadfast, strives for security. Cafe keywords: persevering, down-to-earth, stable, stubborn, possessive, dependable, physical, sensual. Astrology.com index: stabilizer, stamina, sensualized by Venus, stubborn as a bull, weather any storm.

`practical` is **not** auto-added from the earth dump. Cafe “down-to-earth” stays inside steadfast / material, not a separate generated lemma.

### Gemini

| | Families |
|--|----------|
| **Include** | communication · curiosity / learning · versatility · mobility / rarely-settling · wit |
| **Secondary** | sociable · changeable / dual · superficial (Cafe keyword; mass shadow of versatility) · restless schedule |
| **Exclude** | Gemini = Mercury · air → communicative · hands/lungs · twins mythology as product stem · compatibility |

Astrodienst compact: mental, witty, communicative, mobile, learning; rarely touches down. Cafe keywords: talkative, mental, adaptable, flexible, changeable, sociable, versatile, inquisitive, witty. Astrology.com index: fickle/flighty, restless, witty, overbooked, learning from peers, duality.

`adaptable` on Cafe is a Gemini keyword. Do not copy it onto Virgo or Pisces from mutable.

### Cancer

| | Families |
|--|----------|
| **Include** | feeling / emotional · closeness · safety / security-of-bond · home / family · protection / holding-on |
| **Secondary** | nurturing · sensitive / shy · indirect approach · imagination · mood (Astrology.com mass) |
| **Exclude** | water → emotional · Cancer = Moon · breasts/stomach · mother-as-only-meaning · compatibility · “psychic” as the stem |

Astrodienst compact: emotional, stubborn, seeks safety and closeness, family. Cafe keywords: gentle, conservative, feeling, nurturing, defensive, contemplative. Astrology.com index: motherly, nurturing, compassionate, moody, all-in or all-out.

Cancer **safety** is bond/home. Taurus **security** is stability/possession. Do not collapse them.

### Leo

| | Families |
|--|----------|
| **Include** | centrality / being-seen · generosity · pride / dignity · creative display · warmth |
| **Secondary** | leadership / regal manner · loyalty (fixed mass) · drama / flair · need for appreciation · big-picture |
| **Exclude** | Leo = Sun · fire → proud · heart/anatomy · compatibility · “conceited” as the only stem |

Astrodienst compact: glamour, generosity, organizer, center of attention. Cafe keywords: magnanimous, generous, hospitable, caring, warm, authoritative, open. Astrology.com index: center stage, bold, warmth, dramatic flair, loudest roar.

### Virgo

| | Families |
|--|----------|
| **Include** | precision / detail · discernment / differentiation · utility / useful · service / helpful · critique / analytical |
| **Secondary** | conscientious · reserved · perfectionist (Astrology.com mass) · crafts / making-well |
| **Exclude** | earth → practical · Virgo = Mercury · intestines/nervous system · virgin-purity as product stem · health/routine house dump · compatibility |

Astrodienst compact: precise, differentiates, does what is necessary, utilitarian, critical. Cafe keywords: analytical, intelligent, reserved, critical, helpful, conscientious. Astrology.com index: attention to detail, perfectionist, critical, catching then perfecting flaws.

Do not steal Gemini’s communication stem. Virgo’s mental family is **discernment**, not talk.

### Libra

| | Families |
|--|----------|
| **Include** | balance / proportion · harmony · relating / companionship · fairness / justice · beauty / aesthetic |
| **Secondary** | tact / diplomacy · indecision (mass of weighing) · charm / likable · refined |
| **Exclude** | Libra = Venus · air → social · kidneys · compatibility 50/50 as the only stem · “codependent” as Canon |

Astrodienst compact: sense of beauty and proportion, tactful, seeks balance and harmony. Cafe keywords: just, sociable, refined, accommodating, kind, fair, diplomatic, indecisive, artistic. Astrology.com index: weigh pros and cons, partnerships above all, reciprocal, 50/50.

### Scorpio

| | Families |
|--|----------|
| **Include** | intensity · probing / seeing-through · passion · will / determination · extremes |
| **Secondary** | secrecy / self-protective · resourceful · possessive · psychological depth · transformation (Astrology.com mass; Pluto overlap — not the only stem) |
| **Exclude** | Scorpio = Pluto or Mars · water → intense · genitals/anatomy · eagle/phoenix school-stack as product · cabalistic transformation · compatibility · revenge cliché as the stem |

Astrodienst compact: corrosive, passionate, piercing, extreme situations. Cafe keywords: passionate, perceptive, resourceful, possessive, psychological, determined, probing, focused. Astrology.com index: intense, unmoving emotional depth, fierceness, phases of transformation.

`transformation` is secondary mass, same caution as planet Pluto: convention, not unstructured function.

### Sagittarius

| | Families |
|--|----------|
| **Include** | freedom · exploration / adventure · optimism / cheer · meaning-seeking / philosophy · movement / wanderlust |
| **Secondary** | honest / outspoken · restless · excess (Astrology.com Jupiter-mass) · faith in possibility |
| **Exclude** | Sagittarius = Jupiter · fire → optimistic · hips/thighs · luck as the sign · compatibility · “travel buddy” as Canon |

Astrodienst compact: free spirit, carefree, love of movement, cheerful, wanderlust. Cafe keywords: optimistic, restless, enthusiastic, adventurous, honest, outspoken, independent. Astrology.com index: expressive, jolly, larger than life, explores unknown territory, travel/debate.

### Capricorn

| | Families |
|--|----------|
| **Include** | ambition / achievement · discipline / self-discipline · endurance / tenacity · purpose / goal · reserved / serious |
| **Secondary** | practical (Cafe Sun-in-Capricorn: values the practical — **not** from earth dump) · structure / organization (Cafe: “the sign of organization”; Saturn overlap) · responsibility / duty · conservative / tradition · recognition / status · resourceful |
| **Exclude** | earth → practical · cardinal → initiating / builder · Capricorn = Saturn · Capricorn = 10th house career · knees/skeleton · karma as the stem · compatibility · Capricorn man/woman · planet-in-sign recipes (Venus in Capricorn, etc.) |

Astrodienst compact: enduring, sense of purpose, proud, ambitious. Cafe keywords: tenacious, conservative, resourceful, disciplined, wise, ambitious, prudent, constant. Cafe Sun-in-Capricorn: reserved, practical values, organize/manage, society’s framework, plan for the future, get to the top, responsibility, tradition. Astrology.com: hard work, ambitious, determined, businesslike, long game, perseverance, self-mastery, building/organizing (on the dedicated page; **do not** take “as a cardinal sign, builder/climber” as proof).

**Trait ≠ manner (control, not a split):** ambitious / responsible may describe character or motivation. disciplined / practical / reserved / structure-organization may later modify another planet’s function. 1.3.84 decides. This row keeps all of them as territory.

Capricorn does **not** inherit Aries’ initiating. Cardinal is stored on the object; it is not this map.

### Aquarius

| | Families |
|--|----------|
| **Include** | individuality / original · progressive / future-facing · humanitarian / the-group · detachment / cool · invention / unconventional |
| **Secondary** | independent · intellectual · eccentric · friendly-but-selective · idealistic |
| **Exclude** | Aquarius = Uranus (or Saturn) · air → progressive · ankles · technology as the only stem · compatibility · “paradox” as Canon |

Astrodienst compact: communicative, humanitarian, progressive, fraternal. Cafe keywords: individualistic, independent, humanitarian, inventive, original, eccentric, intellectual, idealistic, cool, friendly, detached. Astrology.com index: innovation vs fixed, technological, unconventional, better the collective, individualism.

Do not steal Gemini’s talkativeness. Aquarius communication, when present, is ideas-for-the-group.

### Pisces

| | Families |
|--|----------|
| **Include** | sensitivity · compassion · imagination / inner-world · adaptability / hard-to-hold · permeability / flowing |
| **Secondary** | artistic / poetic · dreamy · spiritual / faith-seeking · helpful / devoted · intuition (Astrology.com mass; do not steal Moon/Neptune as the only stem) |
| **Exclude** | water → sensitive · Pisces = Neptune · feet/veins · two-fish mythology as product · compatibility · addiction/delusion as the stem · “psychic” as Canon |

Astrodienst compact: sensitive, compassionate, helpful, sociable, very adaptable, hard to get a hold on. Cafe keywords: intuitive, dreamy, artistic, humane, sympathetic, sensitive, compassionate, perceptive, impressionable. Astrology.com index: mystical mutability, psychic receptivity, dreamy confusion, known and unknown.

`adaptable` is include because Astrodienst names it on **Pisces**, not because Pisces is mutable.

---

## 5. Shared exclude (all twelve)

- Classification arithmetic (`earth` → practical, `cardinal` → initiating, and the rest of §0.2)
- Ruler identity (sign = its planet)
- House identity (Aries = 1st, Capricorn = 10th, …)
- Planet-in-sign cookbooks
- Compatibility / best-match tables
- Anatomy, metal, stone, color, flower
- Sun-sign career lists and “ideal jobs”
- Man/woman love portraits
- Layer 2 school packages (Lilly QUALITY, Houlding ontology, Rudhyar Pulse, unread psychological portraits)
- Children’s “if you are a Leo” essays as product stem
- Dumping this table into JSON

---

## 6. Forward look — Sign Canon (grammar and fill now locked)

Territory is the input. Canon is a **model PlanetInSign can use**. Do not stop at personality keywords.

Grammar locked 1.3.84. Fill locked 1.3.85 ([SIGN_CANON_V1.md](./SIGN_CANON_V1.md)). Storage locked 1.3.86 ([SIGN_CANON_STORAGE_V1.md](./SIGN_CANON_STORAGE_V1.md)). Materialization locked 1.3.87 ([SIGN_CANON_MATERIALIZATION_V1.md](./SIGN_CANON_MATERIALIZATION_V1.md)). Next = 1.3.88 Planet × Sign smoke-test. **House Canon after PASS.**

Schema today still has sign `mode` · `element` · `orientation` only. Mapping families onto manner slots is done in fill, not this file. Storage is the next named pass.

---

## 7. This pass does not do

- Object rewrite · QUALITY fill · later-interpretive fill · schema · CORE · books
- Sign Canon grammar · manner assignment · Venus × Capricorn application
- House / aspect / ASC maps
- Dumping §3 into JSON
- A 2/3 word spreadsheet
- Repairing 1.3.82 PARTIAL

**Next named:** Sign Canon Grammar — **done 1.3.84.** Sign Canon fill — **done 1.3.85.** Sign Canon storage — **done 1.3.86.** Sign Canon materialization — **done 1.3.87.** Planet × Sign smoke-test — **done 1.3.88.** Houses Mainstream map — **done 1.3.89.** House Canon grammar — **done 1.3.90.** House Canon fill — **done 1.3.91.** House Canon storage/materialization — **done 1.3.92.** Planet × House smoke — **done 1.3.93.** Mainstream Aspect Semantic Map — **done 1.3.94.** Aspect Canon grammar — **done 1.3.95.** Aspect Canon fill — **done 1.3.96.** Aspect Canon storage/materialization — **done 1.3.97.** Next = **1.3.98 stored Planet × Aspect smoke**. STOP Signs.

---

## Changelog

- **1.0 (2026-08-21)** — 1.3.83. Same panel as planets. Territory table locked. Concept families include/secondary/exclude locked per sign. Classification is not proof. Trait ≠ manner named, not split. Not Canon, not JSON.
