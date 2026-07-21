# Profile E2E — Block Passport: `life_spheres` (draft)

**Status:** draft · product decision fixed · **no funnel/code changes in this artifact**  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Related:** patterns gate (shipped, unchanged) · [PROFILE_E2E_PROMPT_REGISTRY.md](./PROFILE_E2E_PROMPT_REGISTRY.md) P4 · [PROFILE_CONTENT_CANON_V1.md](../PROFILE_CONTENT_CANON_V1.md) §7.1A  
**Executable ruleset (evidence / cues):** [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md)  
**Synthesis passport (user copy):** [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md)  
**Quality review:** [PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md](./PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md)  
**Date:** 2026-07-21

> **Product lock (pivoted):** spheres = **natal-presence**, independent of patterns.  
> Deterministic layer = eligibility · source selection · `sphere_cues` · house gate · validation.  
> **User-facing text** = `profile.spheres.synthesis.v1` on prepared cues (not raw planet=sign homework).  
> Projector `v0.2` remains A/B baseline and cue/trait kitchen — **not** long-term SoT for final copy.  
> Patterns gate stays as shipped. Funnel stop after patterns skip is **accidental coupling**, not target architecture.

---

## 0. Decision summary

| Question | Fixed answer |
|----------|----------------|
| What are spheres? | Базовая карта проявлений личности в ключевых сферах жизни |
| What are patterns? | Подтверждённые повторения во времени (отдельная сущность) |
| Eligibility source | Natal/foundation inputs + stable identity/styles — **independent of patterns** |
| Content engine | Deterministic evidence → **LLM sphere synthesis** → validation → Snapshot (**wired**) |
| Deterministic | Eligibility, cues, house gate, schema/ban checks — not final prose tables as product |
| LLM | Synthesis of practical manifestation map; never eligibility; never invent from empty cues; fail ⇒ omit (no projector boilerplate) |
| Ready coupling | Patterns and spheres must **not** jointly define a single global ready |

---

## 1. Passport table

| Field | Value |
|-------|--------|
| `block_id` | `life_spheres` |
| `purpose` | Показать, **как базовые особенности человека проявляются** в ключевых сферах жизни — прикладная карта «где и как это видно», без требования личной истории |
| `user_question` | **Как базовые особенности человека проявляются в ключевых сферах жизни?** |
| `allowed_sources` | См. §3 |
| `min_source_depth` | `birth_data_only` **для права блока существовать**, при наличии достаточных natal/foundation inputs (см. §4). Longitudinal depth **не** повышает eligibility |
| `forbidden_sources` | См. §3 |
| `insufficient_when` | Нет минимальных natal/foundation inputs для **конкретных** утверждений (см. §4–§5). Отсутствие patterns / living **не** insufficient |
| `generation_required` | **`yes`** for user-facing fields — [synthesis passport](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md). Projector may still emit for A/B / fallback experiments but is not target authority |
| `generation_gate` | `spheres_projection_allowed(foundations)` **and** non-empty `sphere_cues` per sphere. **Does not read** `patterns_generation_allowed`. Patterns ineligible/skipped **must not** close this gate |
| `allowed_claims` | См. §6 |
| `forbidden_claims` | См. §6 |
| `prompt_id` | Target: `profile.spheres.synthesis.v1`. Legacy `profile.spheres.v1` = not content authority. Projector = baseline / kitchen |
| `expected_response` | См. synthesis passport §2–§4; projector contract retained for A/B |
| `acceptance_criteria` | См. §5.3 |
| `on_reject` | Omit only fields/spheres that fail acceptance; do not invent; do not block unrelated blocks (identity/styles/patterns). Partial sphere map allowed when house-sensitive claims lack birth time |
| `snapshot_fields` | `life_spheres` (+ optional kitchen: `sphere_projection_version`, `sphere_evidence`, `sphere_claim_depth` per field) |
| `ui_surfaces` | Profile Direction · sphere cards. **Not** QuickMap longitudinal slots. Patterns surface stays separate |
| `appear_when` | Projection produced at least one non-empty sphere with passport-valid claims; portrait base (identity/styles) available or co-published; **patterns not required** |
| `access_tier` | `calc` / trial/free presence when foundations allow — **наличие** базовой карты. Subscription may deepen wording or lived overlay later; must not gate presence |
| `kitchen` | House numbers, planet ids, rule ids, projection version, evidence fingerprints, optional lived confirmations not yet user-facing |

---

## 2. Nine spheres — meaning

Stable ids (current contract; keep):  
`love` · `sex` · `money` · `work` · `family` · `kids` · `body` · `friends` · `decisions`

| id | Chrome (RU) | Sphere meaning (what the block answers here) | Primary natal anchors (projection hints) |
|----|-------------|-----------------------------------------------|------------------------------------------|
| `love` | Любовь | Как входят в близость, что нужно для устойчивой связи, где ломается контакт | 7H · Venus · Moon · relationship_style |
| `sex` | Секс и сексуальность | Желание, темп, телесные/эмоциональные границы в сексуальности | 8H · Pluto · Venus · Mars |
| `money` | Деньги | Ценность, ресурс, устойчивость и риск вокруг денег | 2H · 8H · Jupiter · Saturn · money_style |
| `work` | Работа и реализация | Роль, видимость, опора в деле, где не стоит жить только чужими задачами | 10H · Sun · Saturn · strengths / growth_zones |
| `family` | Семья и дом | Дом, восстановление, форматы близости, которые дают опору | 4H · Moon |
| `kids` | Дети и родительство | Творчество / забота / ответственность «выращивать» (не только биодети) | 5H · Moon |
| `body` | Тело и энергия | Телесный ритм, нагрузка, восстановление | 6H · Mars · Moon · Saturn |
| `friends` | Дружба и окружение | Сеть поддержки, обмен, социальный контур | 11H · Mercury · relationship_style |
| `decisions` | Решения и дисциплина | Как принимают решения, где нужна структура и честные ограничения | 9H · Saturn · Mercury · decision_style |

**Rule:** each sphere must contribute **sphere-specific** manifestation. Copy-paste of `identity_core` into every `how` = reject (`identity_echo` class).

---

## 3. Allowed / forbidden inputs

### 3.1 Allowed (content authority)

| Source | Role |
|--------|------|
| Natal facts actually available | Signs/planets from ephemeris; houses/ASC/MC **only if birth time (and place as required) allow** |
| Deterministic house/planet interpretation already computed | Chart preview interpretations, taxonomy bullets tied to calculated positions |
| Stable `identity_*` from prior funnel/contract | Capsule of who — **input**, not duplicated as every sphere `how` |
| Styles: `relationship_style`, `money_style`, `decision_style` | Cross-cut lenses into love/money/decisions (and related) |
| Strengths / growth_zones | Optional sharpening of work/body risk-need — not sole filler |
| Numerology (calculated) | Soft secondary tint only where ruleset defines; never invents sphere alone |
| Projection ruleset version | Code-owned mapping sphere ← foundations |

### 3.2 Optional (non-eligibility)

| Source | Role |
|--------|------|
| Longitudinal / living / check-ins | **Lived observations** — may later confirm or nuance a sphere field; **never** opens or closes block eligibility |
| Confirmed `recurring_patterns` | May link as evidence under a sphere later; must not be required to publish spheres |
| Prior LLM spheres output | Not an authority once deterministic projection ships |

### 3.3 Forbidden

| Source | Why |
|--------|-----|
| Patterns step success as precondition | Accidental coupling; product lock forbids |
| Today / CUM day / daily taxonomy-as-fact | Day surface ≠ Profile foundations |
| Invented “regularly / always under stress” from birth-only | Patterns / longitudinal claim class |
| Empty catalog defaults / generic horoscope filler as personal map | Product Truth First |
| FE silent `DEFAULTS` paragraphs as production “ready” spheres | Dual-source fiction (legacy path) |
| Free LLM rewrite that changes claim content | Wording layer only, if ever allowed |

---

## 4. Minimum source depth & eligibility

### 4.1 Block eligibility (existence)

```text
spheres_projection_allowed =
  has_birth_date
  AND has_minimum_planetary_or_sign_foundations  # sun/moon/venus/mars/… as ruleset needs
  AND (identity_ready OR identity_partial_capsule_present)  # stable who, not empty
  AND styles_present_for_cross_cut_or_explicitly_optional_per_field
```

- `min_source_depth` for **existence:** `birth_data_only` (when foundations above hold).  
- `onboarding_answers` / check-ins: may enrich later; **not required**.  
- `patterns_generation_allowed == false`: **irrelevant** to spheres gate.

### 4.2 Claim-level eligibility (partial inside the block)

Absence of sufficient natal bases may block **only claims that depend on them**:

| Missing fact | Still project | Omit / hedge |
|--------------|---------------|--------------|
| Birth date | — | Whole block (no natal foundations) |
| Birth time / place (no ASC/houses) | Sign/planet-based sphere fields | House-dependent lines (7H/10H/…) — omit or mark claim_depth=`sign_only` |
| One planet missing | Other spheres | Fields that uniquely require that planet |
| Styles not ready | Natal-only sphere skeleton | Style-cross-cut sentences |
| Patterns / living missing | Full natal-presence map | Lived confirmation layer |

**Target:** partial `life_spheres` object is valid product state — not “forming until patterns”.

### 4.3 Capture note (current vs target)

| Layer | Current | Target |
|-------|---------|--------|
| Capture `block_eligibility.spheres.may_generate` | `true` (“open until passport”) | **`true` when §4.1 holds** — passport confirms natal-presence |
| Funnel | spheres only after patterns success | Projection **independent** of patterns (future code; out of scope here) |
| Patterns gate | shipped | **unchanged** |

---

## 5. Deterministic projection contract

### 5.1 Pipeline (target)

```text
natal/foundations + identity + styles
        → deterministic sphere projection (code)
        → Snapshot.life_spheres
        → Direction UI

optional later:
        → wording layer (LLM) only if passport proves need
        → lived overlay (longitudinal) as confirmation, not eligibility
```

### 5.2 Field contract (per sphere)

Keep user-facing keys compatible with current Snapshot shape unless a later contract bump says otherwise:

| Field | Meaning | Deterministic requirement |
|-------|---------|---------------------------|
| `how` | How it shows in life | Required when sphere eligible; from anchors + identity/styles rules; sphere-specific |
| `need` | What is needed there | From styles/natal need rules; concrete |
| `risk` | Where it breaks | From growth/tension rules; not generic fear |
| `turns_on` | What engages | Concrete situation/verb |
| `turns_off` | What shuts down | Concrete situation/verb |
| `helps` | One practical support line **in this sphere** | Behavioral, doable; **not** global Character `helps[]` |

Optional kitchen / future public:

| Field | Meaning |
|-------|---------|
| `claim_depth` | `sign_only` \| `houses` \| `houses_plus_styles` \| … |
| `evidence` | rule ids + source refs (kitchen or thin UI “why”) |
| `lived` | optional confirmation slice when longitudinal exists |

### 5.3 Acceptance criteria

1. All projected spheres have non-empty `how` (≥ meaningful length per ruleset; not placeholder).  
2. No sphere `how` is near-duplicate of `identity_core` or of another sphere `how` (distinctness gate).  
3. No field asserts confirmed repetition / “as your days show” without lived layer.  
4. House claims appear only when houses are calculable.  
5. `projection_version` + fingerprint recorded in kitchen/meta.  
6. Dual outcome only: **stable projection** or **omit claim/sphere** — never “invent to fill 9×6”.

### 5.4 Optional wording layer (not content authority)

| Allowed | Forbidden |
|---------|-----------|
| Rephrase deterministic claims for voice/locale | Add new factual claims |
| Shorten / clarify | Contradict projection |
| Run only after projection exists | Determine eligibility |
| Separate prompt passport + gate if introduced | Revive `profile.spheres.v1` as sole filler |

Until wording passport exists: **ship deterministic text only**.

---

## 6. Allowed / forbidden claims

### Allowed

- “В любви тебе нужна … потому что …” grounded in Venus/7H/relationship_style.  
- “В работе опора — …; риск — …” grounded in Sun/10H/Saturn/strengths.  
- Sign-only formulations when houses unavailable: clearly not house-precise.  
- Practical `helps` line as **sphere support**, derived from the same foundations.

### Forbidden

- “У тебя регулярно … / каждый раз …” from birth-only (patterns class).  
- “Избегай семью/работу” as bare sphere advice without action chain (Voice / Daily Interpretation bans).  
- Same paragraph in all nine `how`s.  
- Mission-of-life masquerading as a sphere field.  
- Presenting catalog/FE defaults as personal calculation.  
- Implying spheres required longitudinal evidence to exist.

---

## 7. Omit / partial / UI rules

### 7.1 Block states (independent)

| State | Meaning |
|-------|---------|
| Base portrait available | identity (+ styles) publishable |
| Spheres available | deterministic projection produced (≥1 valid sphere / target: full map when foundations allow) |
| Patterns available | only when patterns gate open + step succeeds |

These are **independent**. Absence of patterns must not force spheres into “forming/hidden” if projection exists.

### 7.2 Partial / ready (target contract principle)

- Global `ready` must **not** mean “patterns ∧ spheres ∧ mission ∧ helps”.  
- Prefer block-level readiness flags or a portrait status that allows:
  - Character ready without patterns  
  - Direction spheres ready without patterns  
  - Patterns slot empty/omitted with unlock CTA (Voice §0.05–0.06), not system-status copy  

**Current prod debt:** `validate_required_fields` / funnel early return / FE `isProfilePortraitForming` couple completeness — **out of scope for this draft**; listed as follow-up.

### 7.3 UI

| Surface | Rule |
|---------|------|
| Direction · spheres | Show projected spheres when available; **may show without confirmed patterns** |
| QuickMap | Only base-allowed claims (identity/styles/calc). **Do not** simulate longitudinal depth or fake pattern chips |
| Patterns / Character patterns | Separate; omit when gate closed |
| Empty / missing houses | Honest partial + CTA that unlocks depth (“время рождения → ASC и дома”), person-facing value — never “система не досчитала spheres” |
| Legacy FE chart+DEFAULTS path | Must not compete with Snapshot projection in production V2 |

### 7.4 Voice

Profile text speaks about the person and the value of the next step — never about funnel stages, skipped LLM, or “patterns failed”.

---

## 8. Proof checks (capture)

For production-faithful packs, `life_spheres` must satisfy the four proofs:

| # | Check | Pass | Fail class |
|---|-------|------|------------|
| 1 | Eligibility | `spheres_projection_allowed` true **without** requiring patterns; false only on §4 insufficient foundations | `GENERATION_GATE` · `INSUFFICIENT_DATA` · `BLOCK_PURPOSE` |
| 2 | Projection spec | Ruleset inputs/outputs match this passport (no free LLM as content) | `INPUT` · `PROMPT` (if wording) |
| 3 | Contract | Snapshot `life_spheres` matches acceptance; no identity_echo; house claims only with houses | `RESPONSE_SCHEMA` · `VALIDATION` |
| 4 | UI | Direction shows same spheres; QuickMap does not invent patterns/depth | `SNAPSHOT` · `API` · `PROJECTION` · `UI_GATE` |

**Case A expectation (birth-only, patterns gated off):**  
Target — spheres **may** be present via deterministic projection.  
Current production — spheres **not started** after patterns skip → defect = accidental coupling (`GENERATION_GATE` mis-applied to spheres), not MODEL.

---

## 9. Collateral: `life_mission` and `helps`

Today both are produced inside the **patterns** funnel step (`profile_funnel_patterns_v0`) and disappear when patterns are skipped. That is **not** part of `life_spheres`, but blocks Direction/Character and false-couples “portrait completeness” to longitudinal eligibility.

### 9.1 `helps` (Character · supports) — draft disposition

| Option | Recommendation |
|--------|----------------|
| A. Move to identity or styles step | **Preferred for presence:** 2+ support lines from identity/styles/natal, independent of patterns |
| B. Keep longitudinal-only | Only if product decides Character helps = lived supports — then omit without history + CTA |
| C. Split | Base `helps` from foundations; optional lived helps later |

**Passport stance (draft):** Character `helps[]` is **not** patterns evidence. Target = **A or C**. Sphere-level `helps` string remains inside each sphere (deterministic). Naming collision (`helps` list vs sphere.`helps`) should be clarified in contract docs (`character_helps` vs `sphere.helps`) in implementation stage.

### 9.2 `life_mission` (Direction · mission) — draft disposition

| Option | Recommendation |
|--------|----------------|
| A. Deterministic / identity-derived direction line | Possible natal-presence companion to spheres |
| B. Separate passport with own gate | If mission is “confirmed life direction over time” → longitudinal; omit without history |
| C. Stay in patterns step | **Rejected as target** — accidental packaging |

**Passport stance (draft):** `life_mission` needs **its own passport** before reattach. Until then: do not silently require it for spheres availability. Likely split: short direction from foundations (presence) vs deep mission narrative (depth) — undecided; **do not block spheres** on mission.

### 9.3 What this spheres passport does *not* own

- Opening/closing patterns gate  
- Redefining `recurring_patterns` / `living_changes`  
- Final schema rename for `helps` / mission  
- Funnel reorder implementation  

---

## 10. Current production vs target (debt list)

| Item | Current | Target |
|------|---------|--------|
| Content source | LLM `profile.spheres.v1` after patterns | Deterministic projection |
| Eligibility | Implicit: patterns success | Explicit natal-presence gate |
| Capture may_generate | `true` (unconfirmed) | `true` when §4.1 — **confirmed by this passport** |
| Funnel coupling | Early return skips spheres | Spheres independent of patterns |
| Global ready | Requires patterns + spheres + mission + helps | Independent block readiness |
| FE dual source | Legacy chart/DEFAULTS exists | Snapshot projection only on V2 |
| Prompt registry P4 | Trigger “after patterns”; unique knowledge “Suspect” | Align to this passport |

**Out of scope for this document:** code, funnel, quality validator, FE forming rules.

---

## 11. Dual outcome

For `life_spheres` after projection ruleset exists:

1. **Stable contract:** deterministic projection (+ optional wording) matches this passport.  
2. **Do not generate / omit claims:** foundations insufficient for those claims → no invention.

Forbidden outcome: free LLM fills 9×6 to satisfy schema while patterns were the real gate.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Draft opened: natal-presence · deterministic-first · independent of patterns; mission/helps collateral noted |
| 2026-07-21 | Linked deterministic projector spec v0.1 (executable ruleset) |
