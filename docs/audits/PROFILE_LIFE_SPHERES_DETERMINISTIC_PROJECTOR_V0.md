# Profile · `life_spheres` Deterministic Projector Spec (v0)

**Status:** SoT for **eligibility · evidence · traits/cues kitchen · A/B baseline** · **not** long-term SoT for final user copy  
**Passport:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md)  
**User-copy target:** [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md)  
**Date:** 2026-07-21  
**projection_version:** `life_spheres_projector_v0.2` (D1 traits · D2 scored buckets)

> Executable ruleset for foundations → traits/buckets → optional projector prose (A/B).  
> **Pivot:** do not grow planet×sign×sphere×field tables as the product content engine.  
> Prefer `sphere_cues` → `profile.spheres.synthesis.v1`. Independent of patterns.

---

## 0. Scope of this artifact

| In | Out |
|----|-----|
| Foundations input contract | UI redesign / Screen Master |
| `spheres_projection_allowed` | Character `helps[]` / `life_mission` passports |
| Per-sphere inputs & claim depths | Subscription depth contracts |
| Field assembly rules (`how`…`helps`) | Full 9×6 copy catalog (templates live in code tables versioned here by id) |
| Partial projection | Global ready redesign (noted as constraint only) |
| Distinctness / identity-echo | LLM wording passport |
| `projection_version` · evidence · fingerprint | FE DEFAULTS removal (later PR) |
| PR-2 slice: `love` · `money` · `decisions` | Remaining six spheres (rules skeleton only) |

---

## 1. Pipeline position (target)

```text
identity → styles
       → [patterns IFF patterns_generation_allowed]   # shipped gate; unchanged
       → spheres IFF spheres_projection_allowed       # NEW; independent of patterns outcome

spheres content authority (target) = synthesis(cues from foundations)
projector(foundations) = A/B baseline + trait/cue source, not final SoT
legacy profile.spheres.v1 = NOT content authority (see Prompt Registry)
```

**Control-flow invariants (for PR-2 code):**

1. Skipped patterns must not stop the funnel before spheres.  
2. Failed patterns must not forbid spheres.  
3. Patterns gate logic stays as shipped.  
4. Global `ready` validator is **not** fully redesigned in PR-2; partial `life_spheres` may coexist with `status=partial` / forming shell until block-level readiness lands.

---

## 2. Foundations input (`SphereFoundationsV0`)

Projector reads a normalized pack. Callers assemble it from portrait funnel outputs + natal calc already available in Profile pipeline.

### 2.1 Required structure

```text
SphereFoundationsV0 {
  locale: "ru" | "en"
  person: { birth_date?: ISO date, birth_time?: ISO time|null, time_unknown?: bool, location?: … }
  identity: {
    identity_core: string        # ≥20 when styles succeeded; may be empty → block gate fails
    strengths: string[]          # optional sharpening
    growth_zones: string[]       # optional sharpening
  }
  styles: {
    relationship_style: string   # required for love (PR-2)
    money_style: string          # required for money (PR-2)
    decision_style: string       # required for decisions (PR-2)
  }
  natal: {
    sun_sign?: SignId
    moon_sign?: SignId
    mercury_sign?: SignId
    venus_sign?: SignId
    mars_sign?: SignId
    jupiter_sign?: SignId
    saturn_sign?: SignId
    pluto_sign?: SignId          # optional; sex later
    houses_available: bool       # true only if ASC/houses calculable (time + place as product requires)
    houses?: {
      "2"|"4"|"5"|"6"|"7"|"8"|"9"|"10"|"11": {
        sign?: SignId
        theme?: string           # from chart interpretation if present
        description?: string     # from chart interpretation if present
      }
    }
    planet_bullets?: {           # deterministic taxonomy lines already computed; optional
      sun?: string[]
      moon?: string[]
      …
    }
  }
  baseline?: { element_focus?, rhythm?, … }   # soft secondary only where rule cites it
  numerology?: { life_path?: int }            # soft secondary; never sole filler
}
```

`SignId` = canonical sign slug used elsewhere (`aries`…`pisces`) or display name — implementation must normalize once.

### 2.2 Availability classes

| Class | Condition |
|-------|-----------|
| `A_birth` | `birth_date` present → sun_sign calculable |
| `B_planets` | ephemeris planet-in-sign available without birth time (moon/venus/… as calc provides) |
| `C_houses` | `houses_available == true` |
| `D_identity` | `identity_core` trimmed length ≥ 20 |
| `E_styles` | each of the three styles trimmed length ≥ 12 |

Patterns / living / check-ins are **not** fields of `SphereFoundationsV0`.

---

## 3. Eligibility: `spheres_projection_allowed`

```text
spheres_projection_allowed(F) =
  F.person.birth_date is present
  AND F.natal.sun_sign is present          # minimum planetary/sign foundation
  AND D_identity                           # identity_core ≥ 20
  AND (
       # PR-2: at least one of the three style-backed spheres can run
       E_styles.relationship_style
       OR E_styles.money_style
       OR E_styles.decision_style
     )
```

**Does not read:** `patterns_generation_allowed`, living, check-ins, prior LLM spheres.

| Outcome | Behavior |
|---------|----------|
| `false` | Do not project; Snapshot omits or keeps empty `life_spheres`; capture `may_generate=false` with reason |
| `true` | Run projector; emit partial or full map per §6 |

**Capture:** `block_eligibility.spheres.may_generate = spheres_projection_allowed(F)`.

---

## 4. Sphere input matrix (all nine)

Legend: **R** = required to emit sphere · **O** = optional enrich · **H** = house-only (omit claim if no houses) · **S** = style lens

| Sphere | Style lens | Sign/planet inputs | House inputs | Min to emit sphere (v0.1) |
|--------|------------|--------------------|--------------|---------------------------|
| `love` | **S** `relationship_style` **R** | Venus **R** if available else Sun **R**; Moon **O** | 7H **H** enrich `how` | style + (venus\|sun) + identity |
| `money` | **S** `money_style` **R** | Jupiter **O**, Saturn **O**, Sun **R** fallback | 2H **H**, 8H **H** | style + sun + identity |
| `decisions` | **S** `decision_style` **R** | Saturn **O**, Mercury **O**, Sun **R** fallback | 9H **H** | style + sun + identity |
| `work` | — (strengths **O**) | Sun **R**, Saturn **O** | 10H **H** | sun + identity *(post PR-2)* |
| `family` | — | Moon **R** if avail else Sun | 4H **H** | moon\|sun + identity *(post)* |
| `kids` | — | Moon **O**, Sun **R** | 5H **H** | sun + identity *(post)* |
| `body` | — | Mars **O**, Moon **O**, Saturn **O**, Sun **R** | 6H **H** | sun + identity *(post)* |
| `friends` | relationship_style **O** | Mercury **O**, Sun **R** | 11H **H** | sun + identity *(post)* |
| `sex` | — | Venus **O**, Mars **O**, Pluto **O**, Sun **R** | 8H **H** | (venus\|mars\|sun) + identity *(post)* |

### 4.1 Claims allowed without birth time (`claim_depth = sign_only` or `sign_plus_styles`)

Allowed when `houses_available == false`:

- All fields built from style + planet-in-sign + identity sharpening.  
- Must **not** mention house numbers, ASC, “в седьмом доме”, cusp themes.  
- May use planet-in-sign bullets if present.

### 4.2 Claims that require houses (`claim_depth` includes `houses`)

Only when `houses_available == true` and house entry exists:

- Append / weave house `description` (prefer) or `theme` into `how` (and optionally `need` if ruleset line cites house).  
- Never fabricate house text if interpretation empty — skip house weave, keep sign_plus_styles depth.

---

## 5. Source priority (per field assembly)

Strict order when combining fragments into one field:

```text
1. Style lens sentence          (for love/money/decisions — primary voice of need/risk/on/off)
2. Planet-in-sign fragment      (primary for how concrete natal color; secondary elsewhere)
3. House fragment               (only if C_houses; never overrides style contradiction — append as manifestation locus)
4. Identity sharpening          (≤1 short clause; MUST pass identity-echo checks — not a copy of identity_core)
5. Strengths / growth_zones     (optional; risk/need only; never entire how)
6. Baseline / numerology        (optional tint; never sole content of any field)
```

**Forbidden in priority list:** living, patterns, Today, FE DEFAULTS, legacy LLM spheres output.

If after (1)–(3) a required field still cannot meet min length → **omit sphere** (or omit field per §6), do not fill from (6) alone.

---

## 6. Partial projection rules

### 6.1 Object shape

```json
{
  "life_spheres": {
    "love": { "how": "…", "need": "…", "risk": "…", "turns_on": "…", "turns_off": "…", "helps": "…" }
  },
  "life_spheres_meta": {
    "projection_version": "life_spheres_projector_v0.1",
    "fingerprint": "sha256:…",
    "spheres_projected": ["love", "money", "decisions"],
    "spheres_omitted": [
      {"id": "work", "reason": "not_in_slice_v0_1"},
      {"id": "sex", "reason": "not_in_slice_v0_1"}
    ],
    "per_sphere": {
      "love": {
        "claim_depth": "sign_plus_styles",
        "evidence": ["style:relationship_style", "planet:venus", "rule:love.how.v1"]
      }
    }
  }
}
```

- User-facing Snapshot may nest meta under kitchen / `meta.life_spheres_projection` — implementation choice, but fingerprint + version **must** be persisted.  
- **Partial map is valid:** missing keys for non-projected spheres ≠ error.  
- Do **not** emit empty strings to satisfy 9×6.  
- Do **not** require all nine for projection success in v0.1.

### 6.2 Per-sphere emit rule

Emit sphere `S` iff:

1. Block gate `spheres_projection_allowed` true, AND  
2. Sphere is in active slice (PR-2: `{love, money, decisions}`), AND  
3. Sphere min inputs from §4 table satisfied, AND  
4. All six fields pass §7 min length + §8 validation.

Else omit sphere with reason in meta.

### 6.3 Field omit

v0.1: all-or-nothing per sphere (six fields). No half-filled sphere objects.  
Later: may allow field-level omit with kitchen reasons — not in v0.1.

---

## 7. Field construction rules

### 7.1 Length & voice (all fields)

| Field | Min chars (trim) | Max chars | Voice |
|-------|------------------|-----------|-------|
| `how` | 40 | 520 | 2–4 sentences; sphere-specific manifestation; verb/situation |
| `need` | 24 | 280 | What is needed **in this sphere** |
| `risk` | 24 | 280 | Where it breaks **here**; not generic anxiety |
| `turns_on` | 20 | 220 | Concrete engage |
| `turns_off` | 20 | 220 | Concrete shut-down |
| `helps` | 20 | 220 | One doable support **in this sphere** ≠ Character `helps[]` |

Locale: emit in `F.locale`. No system-state language (Voice §0).

### 7.2 Assembly algorithm (generic)

For each field `f` of sphere `S`:

1. Select ordered template slots from rule table `rules[S][f]` (versioned ids).  
2. Bind slots from priority sources (§5); skip empty bindings.  
3. Join with locale-appropriate separators; trim; clip to max.  
4. If below min → fail sphere emit.  
5. Record evidence rule ids + source keys.

Templates are **code tables** keyed by `rule_id`. This spec defines **binding semantics**; exact RU/EN strings live beside code but each `rule_id` must be listed in §9 / PR-2 tables below before use.

### 7.3 Field semantics

| Field | Must answer | Must not |
|-------|-------------|----------|
| `how` | How this sphere shows for **this** person | Paste `identity_core`; claim “регулярно/каждый раз” from birth-only |
| `need` | What they need in-sphere | Life mission; avoid-list without action |
| `risk` | Break point in-sphere | Invented longitudinal stress-as-fact |
| `turns_on` | What engages | Generic “гармония/энергия” filler |
| `turns_off` | What shuts down | Bare “избегай семью/работу” |
| `helps` | One practical move | Copy global Character helps; day/CUM tip |

---

## 8. Validation gates (projector-local)

Run after assembly, before Snapshot merge. Fail → omit sphere (or whole projection if zero spheres).

### 8.1 `identity_echo`

Reuse spirit of `profile_contract_quality_v1.identity_echo_in_spheres`, tightened for partial maps:

```text
norm = lowercase + collapse whitespace
For each projected sphere:
  if norm(how) contains norm(identity_core) OR norm(identity_core) contains norm(how)
     AND len(norm(how)) ≥ 24:
       FAIL that sphere (identity_echo)
```

Also FAIL if ≥50% of content tokens of `how` overlap identity_core token set (Jaccard ≥ 0.5) — catches paraphrase echo.

### 8.2 `spheres_not_distinct`

Among projected `how` values with len ≥ 24:

```text
if how_a == how_b OR (len > 40 AND one contains the other) → FAIL both (or drop later sphere)
```

Additionally for PR-2: `need` of love must not equal `need` of money/decisions (exact norm match).

### 8.3 `style_passthrough`

`how` must not equal the raw style string. Style may be **reused as a clause**, not the entire field.

```text
if norm(how) == norm(style_lens) → FAIL
```

### 8.4 `house_overclaim`

If `houses_available == false` and field text matches house markers (`дом`, `house`, `ASC`, `асцендент` as structural claim) → FAIL.

### 8.5 `longitudinal_leak`

If field matches patterns-class markers without lived layer (`регулярно`, `каждый раз`, `по чек-инам`, `as your days show`) → FAIL.

### 8.6 Generic phrase

Apply existing `GENERIC_PHRASE_MARKERS_RU` (and EN set when locale=en) to concatenated sphere fields.

---

## 9. PR-2 slice — detailed rules (`love` · `money` · `decisions`)

### 9.1 Shared helpers

| Helper | Definition |
|--------|------------|
| `style_clause(text)` | First sentence of style, clipped ≤160 |
| `planet_line(planet)` | First taxonomy bullet for planet-in-sign, else `"{Planet} in {sign}"` localized factual + one fixed trait line from sign×planet table |
| `house_line(n)` | `houses[n].description` or `theme`, clipped ≤200; null if unavailable |
| `identity_hint` | Extract ≤12-word non-overlapping fragment from identity_core via deny-list of copying whole core — **optional**; if echo risk, skip |

### 9.2 `love`

| Field | Bindings (priority) | rule_ids |
|-------|---------------------|----------|
| `how` | `planet_line(venus\|sun)` + optional `house_line(7)` + optional soft identity_hint **not** equal to core | `love.how.planet` · `love.how.house7` |
| `need` | Derive from `relationship_style` via need-transform templates (clarity / pace / honesty classes keyed by keyword buckets in style) | `love.need.from_style` |
| `risk` | Opposite tension of need class + optional moon fragment | `love.risk.from_style` · `love.risk.moon` |
| `turns_on` | Engage template from same style class | `love.on.from_style` |
| `turns_off` | Shut-down template from same style class | `love.off.from_style` |
| `helps` | One behavioral line tied to need class | `love.helps.from_style` |

**Style class buckets (v0.1):** implement as keyword → class map in code (`clarity`, `pace`, `care`, `autonomy`, `depth`). Unmatched → class `general` with non-generic templates that still embed a **verbatim short quote** (≤40 chars) from `relationship_style` so output stays personal.

### 9.3 `money`

| Field | Bindings | rule_ids |
|-------|----------|----------|
| `how` | `planet_line(jupiter\|saturn\|sun)` + optional `house_line(2)` + optional `house_line(8)` | `money.how.planet` · `money.how.house2` · `money.how.house8` |
| `need` | From `money_style` class buckets (`structure`, `growth`, `security`, `exchange`) | `money.need.from_style` |
| `risk` | Opposite of need class | `money.risk.from_style` |
| `turns_on` | Style class engage | `money.on.from_style` |
| `turns_off` | Style class shut-down | `money.off.from_style` |
| `helps` | One weekly/behavioral finance support line | `money.helps.from_style` |

### 9.4 `decisions`

| Field | Bindings | rule_ids |
|-------|----------|----------|
| `how` | `planet_line(saturn\|mercury\|sun)` + optional `house_line(9)` | `decisions.how.planet` · `decisions.how.house9` |
| `need` | From `decision_style` class buckets (`structure`, `speed`, `consensus`, `analysis`) | `decisions.need.from_style` |
| `risk` | Opposite of need class | `decisions.risk.from_style` |
| `turns_on` | Style class engage | `decisions.on.from_style` |
| `turns_off` | Style class shut-down | `decisions.off.from_style` |
| `helps` | One decision hygiene line (single next step / timebox / write criteria) | `decisions.helps.from_style` |

### 9.5 Post–PR-2 spheres

`work`, `family`, `kids`, `body`, `friends`, `sex`: **not emitted** in `v0.1`. Meta lists `not_in_slice_v0_1`. Full binding tables land in `v0.2` of this doc before code expands.

---

## 10. `projection_version`, evidence, fingerprint

### 10.1 Version

Constant: `life_spheres_projector_v0.1`  
Bump when: rule_ids change semantics, bucket maps change, field mins change, sphere set of slice changes.

### 10.2 Evidence (per sphere)

Ordered list of strings:

```text
"style:{field_name}" | "planet:{name}" | "house:{n}" | "rule:{rule_id}" | "identity:hint"
```

Stored in meta; not required on user-facing card chrome.

### 10.3 Fingerprint

```text
payload = canonical_json({
  "projection_version": VERSION,
  "locale": F.locale,
  "sphere_ids": sorted(emitted ids),
  "inputs": {
     # only keys that affected emission
     "identity_core_hash": sha256(norm(identity_core))[:16],
     "styles": { k: sha256(norm(v))[:16] for used styles },
     "natal": {
        "sun_sign", used planet signs, "houses_available",
        "houses_used": { n: sha256(norm(desc|theme))[:16] }
     },
     "rule_ids": sorted(all rule_ids fired)
  },
  "life_spheres": emitted object
})
fingerprint = "sha256:" + sha256(payload)
```

Same foundations + version ⇒ same fingerprint (byte-stable canonical JSON).

---

## 11. Funnel / Snapshot integration constraints (PR-2)

| Concern | Rule |
|---------|------|
| When to run | After styles success; after patterns step **attempt or skip**; never requires patterns ok |
| Merge | `life_spheres` from projector overwrites empty; must not require LLM spheres |
| Legacy LLM | If temporarily still callable: mark `meta.spheres_source=legacy_llm_debt` and **do not** treat as target; preferred PR-2 path = projector only for slice spheres |
| Global ready | Unchanged this PR — Case A may remain `partial` while carrying projected spheres in Snapshot |
| Capture Case A | `patterns.ran=false`; `spheres.may_generate=true` when gate holds; `spheres` projected; Snapshot contains love/money/decisions (as eligible); UI/projection path must not drop them solely because patterns empty |
| Capture Case B | Patterns as today when eligible; spheres still from projector (not patterns success) |

---

## 12. Test contract (must exist with PR-2 code)

| Test | Assert |
|------|--------|
| `test_spheres_gate_independent_of_patterns` | birth-only foundations → gate true even if patterns disallowed |
| `test_projector_love_money_decisions_sign_only` | no houses → three spheres; no house markers; fingerprint stable |
| `test_projector_with_houses_enriches_how` | houses_available → evidence contains `house:7` / `2` / `9` when descriptions present |
| `test_identity_echo_omits_sphere` | how=identity_core → sphere omitted |
| `test_style_passthrough_rejected` | how=raw style → omit |
| `test_partial_map_omits_other_six` | keys only slice spheres |
| `test_funnel_continues_after_patterns_skip` | integration: skip patterns → projector still runs |

---

## 13. Dual outcome

1. **Stable projection** for eligible slice spheres meeting §7–§8.  
2. **Omit** sphere or block when gate/inputs/validation fail — never invent to fill schema.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | v0.1 spec: foundations, gate, 9-sphere matrix, PR-2 love/money/decisions rules, validation, fingerprint |
| 2026-07-21 | Quality review SoT: [PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md](./PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md) — sign-only `how` boilerplate = blocking RULESET |
| 2026-07-21 | v0.2: D1 planet×sign traits (`life_spheres_traits_v0`) · D2 scored buckets (`life_spheres_style_buckets_v0`); quality pack 8/8 |
