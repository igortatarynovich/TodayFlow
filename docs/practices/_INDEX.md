# Practices — индекс канона

## Active

| Документ | Роль |
|----------|------|
| [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md) | **SoT библиотеки** (v1.2): class → type → attributes · Canonical Technique → Item expression · pipeline Meaning→Retrieval→Library. Vocab: `DATA/reference/practice/content_taxonomy_v1.json` |
| [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md) | **Coverage** (v1.13): 26/26 P0 cells · type spine. Architecture stands. Sourced 17/26. Next cell = `need.recovery.recover` |
| [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md) | **Active fill:** lightweight provenance → accepted/skipped → Content Item. Не research ladder |
| [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md) | **SoT происхождения техники** (v1.24): одна запись на технику. LLM не источник метода. Meaning не знает `item_id` / `technique_id` |
| [CONTENT_LIBRARY_SELECTION_V1.md](./CONTENT_LIBRARY_SELECTION_V1.md) | **Runtime selector** (v1.0): deterministic selection of active Content Item by need (purpose/direction/state/context). No LLM, no randomness. Code: `services/content_library_selection_v1.py` |
| [PRACTICES_SCREEN_V1.md](./PRACTICES_SCREEN_V1.md) | **SoT экрана** (v1.1): цикл состояния; 6 needs (тело + рефлексия; Уснуть last); 9 formats (yoga/stretch/music + reflection/sleep); сессия; music layer |
| [practices_screen_mockup_v1.png](./practices_screen_mockup_v1.png) | **Визуальный референс** экрана (загруженный скрин спеки) — UI-паритет + C0b need-лента |

## Research archive (non-blocking)

История Landscape → Shortlist → Ingest → Normalization → Targeted* → Safety Review. **Не** active fill sequence. **Не** NOW. **Не** unlock. Index: [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

| Документ | Чем был |
|----------|---------|
| [PRACTICE_TECHNIQUE_LANDSCAPE_V1.md](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md) | карта семей |
| [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md) | C1–C9 |
| [PRACTICE_TECHNIQUE_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md) | slice `equal_count_breath` |
| [PRACTICE_TECHNIQUE_INGEST_V1.md](./PRACTICE_TECHNIQUE_INGEST_V1.md) | three evidence records |
| [PRACTICE_TECHNIQUE_NORMALIZATION_V1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md) | `insufficient_evidence` |
| [PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md) | hold identity |
| [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md) | two resolution loci |
| [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md) | `normalize_one` candidate |
| [PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md](./PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md) | `insufficient_safety` |
| [PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md) | who_must_not_hold; stop A |
| [PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1.md) | two hold-safety observations |

**Связанные (не заменяют этот пакет):**

- [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md) — практика дня / recommendation в Today
- [TODAYFLOW_FOUNDATION_UI.md](../TODAYFLOW_FOUNDATION_UI.md) — visual tokens (Practices не вводит параллельный Figma-канон экрана)
- [REFERENCE_LAYER_AND_BUILD_ORDER.md](../REFERENCE_LAYER_AND_BUILD_ORDER.md) — Practice / Habit / Ascetic registries
- [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) — parent порядка исследования. Practice fill **не** требует parent steps 5–10. Клинические/психологические утверждения — своя иерархия доказательности, не астрологический CORE.
- Legacy catalog keys в коде: map → need/format IDs, не SoT шапки
