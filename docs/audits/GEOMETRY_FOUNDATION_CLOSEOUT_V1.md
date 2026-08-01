# Geometry foundation closeout (coords → UTC → bodies → angles)

**Status:** closed 2026-08-01 (foundation only — not interpretation / hooks / knowledge bases)

## Checklist

| Criterion | Status |
|-----------|--------|
| Geocode covers small towns; ambiguous names require explicit choice | **LIVE** — Nominatim merge; `need_choice` / HTTP 409; suggest list + FE persists `City, Country`. Smoke: Слуцк → coords; Alexandria / Мозырь → choice |
| TZ resolved from place/coords on save (not FE-only) | **LIVE** — `birth_timezone_resolve_v1` + engine refuse civil-as-UT |
| `FLG_SWIEPH` primary in prod; Moshier not silent | **LIVE** — `astro/ephe` bundled; `SWISS_EPHEMERIS_PATH=/app/ephe`; `/health` + chart metadata `ephemeris_source=swiss_swieph`; Moshier → `EphemerisDegradedError` / HTTP 503; backend mode `ephemeris_degraded` not cached |
| Igor / Kyiv (and affected) recalculated; cache invalidated | **LIVE** — TZ backfill + Swiss re-warm |
| Angles cross-checked vs independent source | **LIVE** — see §Cross-check |
| `today_tap_events` / tap history not rewritten | **held** — count unchanged through TZ + Swiss re-warm |
| Semantic layer (hooks / KB) only after this phase | gated until this doc stays green |

## Cross-check results

### Control profiles (prod after Swiss + TZ)

| Profile | Inputs | ASC | MC | `ephemeris_source` |
|---------|--------|-----|----|--------------------|
| Igor (id=2) | 1990-02-13 12:12 Europe/Minsk, 53.9045°N 27.5615°E, Placidus | Gemini 14.77° (λ 74.7689°) | Aquarius 6.33° (λ 306.3257°) | `swiss_swieph` |
| Kyiv (id=1) | 1995-05-26 00:55 Europe/Kyiv, 50.4501°N 30.5234°E | Aquarius 5.40° (λ 305.4048°) | Sagittarius 4.27° (λ 244.2655°) | `swiss_swieph` |

Pre-fix (null TZ, civil-as-UT): Igor ASC was Cancer ~24.2° (Δ ≈ 39°).

### Public reference — Albert Einstein

Inputs used by Astrotheme / Astro-Seek (AA): 1879-03-14 **11:30 LMT** Ulm, 48°24′N 10°00′E, Placidus tropical.  
LMT → UT = 10:50 (longitude 10°E ≈ +40 min). Do **not** use modern `Europe/Berlin` for 1879.

| Angle / body | Astrotheme published | TodayFlow Swiss SE | Δ |
|--------------|----------------------|--------------------|---|
| Sun | Pisces 23°30′ | Pisces 23.51° | ~0.5′ |
| Moon | Sagittarius 14°32′ | Sagittarius 14.53° | ~0.4′ |
| ASC | Cancer 11°38′ | Cancer 11.65° | ~0.8′ |
| MC | Pisces 12°50′ | Pisces 12.84° | ~0.4′ |

Acceptance: within a few arcminutes — **pass**.

Igor/Kyiv angles use the same Swiss path + correct IANA TZ; Einstein proves the angle pipeline matches an independent published chart when civil→UT is historically correct.

## Non-goals

- Street-level geocoding (city-center coverage is enough for houses)
- Full GeoNames dump (Nominatim coverage accepted as comparable for v1; revisit if small-town gaps appear)
- Rewriting historical tap accuracy
- Quincunx / sky_drivers (handled separately in Wave2 contract)
- Return to hooks / KB / semantic screens before this checklist stays green
