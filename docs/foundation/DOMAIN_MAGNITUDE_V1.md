# Domain magnitude v1 — calibrated valence weights

**Status:** ACTIVE (storage extract 2026-08-03)  
**Module:** `todayflow_backend.data.domain_magnitude_v1`  
**Consumer:** `today_domain_verdicts_v1.valence_domain` → `top_driver_v1`  
**Related:** [foundation_v1.md](../foundation_v1.md) §2.4 aspect *character*; Wave 2 contract domain verdicts

---

## 0. What this is / is not

| | |
|--|--|
| **Is** | Product-calibrated signed magnitudes for domain × aspect × planet |
| **Is not** | Atomic foundation fact (unlike sign ruler / aspect character) |
| **Character** | Still `aspect_is_harmonious` / `aspect_is_challenging` from foundation |
| **Change policy** | Do **not** silently edit numbers — Architecture impact + product accept |

Migration 2026-08-03: if/elif draft → explicit lookup. **Values unchanged.**

---

## 1. Resolver order

1. Any harmonious aspect → `1.0` (global, before domain table)
2. Domain `special_cases` (exact aspect or any challenging × natal point)
3. `conjunction` → `conjunction_by_transit[planet]` else `conjunction_other`
4. Any other challenging → `challenging_fallback`
5. Else `default` (0.0)

Unknown domain id historically used the energy branch — preserved via `_DEFAULT_DOMAIN = "energy"`.

---

## 2. Documented rule (was implicit)

**Mars conjunction by domain** (`MARS_CONJUNCTION_RULE_RU`):

- work / energy → positive charge (0.75 / 0.85)
- relationships → friction (−0.75, pooled with saturn/pluto)
- money → negative (−0.7, pooled with saturn/pluto; no separate “drive” branch)

Formalized as text only — magnitudes unchanged.

---

## 3. Open calibration questions (numbers frozen)

### 3.1 Money — no square+planet specials

Other domains have square/challenging specials (work: mars/saturn; relationships: venus/moon; energy: mars). Money has empty `special_cases` and only `challenging_fallback = -0.75`, despite `DOMAIN_NATAL_POINTS["money"]` including venus/jupiter/pluto.

**Decision now:** treat as **open gap** — leave empty. Do not invent money specials without a calibration pass.

### 3.2 challenging_fallback scale

| domain | fallback |
|--|--|
| work | −0.65 |
| money | −0.75 |
| relationships | −0.7 |
| energy | −0.6 |

**Decision now:** preserve. Unifying “principle vs four independent picks” is a future product pass — not part of this storage migration.

---

## 4. Architecture impact (this migration)

- **SoT before:** magnitudes inline in `valence_domain` if/elif (“Draft tables”)
- **SoT after:** `domain_magnitude_v1.DOMAIN_MAGNITUDE_V1` + `resolve_valence`
- **Public contract changed?** no — same floats
- **Migration required?** no
- **Canon updated?** yes — this doc; foundation §5 notes table extracted
- **Backward compatible?** yes — behavior pinned by `test_today_domain_verdicts_v1`
