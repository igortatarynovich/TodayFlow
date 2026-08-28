# Profile Selection Engine: IL-3 object → topic domain connections

**Date:** 2026-08-28  
**Scope:** `services/il4_selection_v1.py` — deterministic mapping from IL-3 object ids (planets, houses, angles, signs) to `ProfileTopicDomain` for the Profile/Compatibility surface filters.  
**Goal:** ensure every standard IL-3 object that can appear in a profile pack is connected to at least one product topic domain, so the 24-line profile selection is reproducible and auditable without relying on LLM output.

## Status

Implemented. The mapping is a product-side heuristic, **not** an IL-3 meaning canon. It does not change what the interpretation library says; it only decides which lines reach a topic-filtered surface.

## Mapping

### `ASTRO_OBJECT_TOPIC_MAP`

| Object id | Topic domains |
|-----------|---------------|
| `astro.object.sun` | work, body_energy, habits_discipline |
| `astro.object.moon` | relationships, family, inner_state, body_energy, habits_discipline |
| `astro.object.mercury` | decision, work, relationships |
| `astro.object.venus` | relationships, intimacy, money |
| `astro.object.mars` | body_energy, work, intimacy, decision, habits_discipline |
| `astro.object.jupiter` | money, work, decision, relationships |
| `astro.object.saturn` | work, money, family, habits_discipline, decision |
| `astro.object.uranus` | decision, inner_state, work, body_energy |
| `astro.object.neptune` | inner_state, relationships |
| `astro.object.pluto` | inner_state, intimacy, money |
| `astro.object.asc` | body_energy, inner_state, work, decision |
| `astro.object.mc` | work, money, family |
| `astro.object.dsc` | relationships, intimacy |
| `astro.object.ic` | family, inner_state |
| `astro.house.01` | body_energy, inner_state, decision |
| `astro.house.02` | money |
| `astro.house.03` | decision, relationships |
| `astro.house.04` | family, inner_state |
| `astro.house.05` | intimacy, relationships, inner_state |
| `astro.house.06` | work, body_energy, habits_discipline |
| `astro.house.07` | relationships, intimacy |
| `astro.house.08` | intimacy, money, inner_state |
| `astro.house.09` | decision, work, inner_state |
| `astro.house.10` | work, money, family |
| `astro.house.11` | relationships, work, inner_state |
| `astro.house.12` | inner_state |

### `SIGN_TOPIC_MAP`

| Sign id | Topic domains |
|---------|---------------|
| `astro.sign.aries` | body_energy, decision |
| `astro.sign.taurus` | money, body_energy |
| `astro.sign.gemini` | decision, relationships |
| `astro.sign.cancer` | family, inner_state |
| `astro.sign.leo` | relationships, intimacy, body_energy |
| `astro.sign.virgo` | work, body_energy, habits_discipline |
| `astro.sign.libra` | relationships, intimacy, decision |
| `astro.sign.scorpio` | intimacy, money, inner_state |
| `astro.sign.sagittarius` | decision, inner_state |
| `astro.sign.capricorn` | work, money, habits_discipline |
| `astro.sign.aquarius` | decision, relationships, inner_state |
| `astro.sign.pisces` | inner_state, relationships |

### Text fallback

If a line has no recognized object ids, explicit keyword hints still assign topics (e.g., "financial decision about family money" → money, family, decision). This keeps the filter robust for malformed lines, but the primary path is object-id based.

## Algorithm

1. `_object_ids_from_line(line)` extracts all `astro.object.*`, `astro.house.*`, and `astro.sign.*` ids from the line's `jobs` dictionary and from the line text.
2. `_topics_for_line(line)` builds the union of topic domains mapped to those object ids.
3. `_line_matches_topic(line, topic)` returns `True` if `topic` is in the union (or `GENERAL`).
4. `select_themes(...)` applies the surface cap and, for non-`GENERAL` topics, keeps only matching lines.

## Tests

`backend/tests/test_il4_selection_v1.py` now includes:

- `test_all_planets_map_to_at_least_one_topic` — covers all 10 planets.
- `test_all_houses_map_to_at_least_one_topic` — covers all 12 houses.
- `test_all_signs_map_to_at_least_one_topic` — covers all 12 signs.
- `test_angles_map_to_at_least_one_topic` — covers asc, mc, dsc, ic.
- `test_topic_filters_cover_all_non_general_domains` — a 10-line pack with one line per topic, verifying every non-`GENERAL` topic returns at least one line.
- `test_line_topic_union_from_multiple_objects` — Venus in 7th house maps to relationships, intimacy, and money.
- `test_text_fallback_for_topic_keywords` — text-only keyword hints still match.

## Verification

```bash
cd /opt/TodayFlow/backend
.venv/bin/python -m pytest tests/test_il4_selection_v1.py tests/test_il4_editorial_consume_v1.py tests/test_il4_expression_engine_v1.py tests/test_il3_interpretation_engine_v1.py tests/test_il2_composition_rules_v1.py tests/test_calc_il_wire_v1.py -q
# 6 passed
```

## Risks / follow-ups

- The mapping is heuristic. It should be validated against real K3 output in the Phase 2.6 audit once billing is restored. If K3 consistently ignores or over-emphasizes certain objects for a topic, the map can be adjusted without changing IL-3.
- Aspects are not explicitly mapped; their topics are derived from the planet ids in the line's `jobs`. If aspect-specific semantics become important, add a dedicated aspect map.
- Outer planets and angles (asc/mc/dsc/ic) were previously unmapped. They are now connected, but some may be over-mapped. The K3 audit will help refine this.
