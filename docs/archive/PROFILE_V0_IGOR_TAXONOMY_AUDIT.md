# Profile taxonomy audit · Igor / Sage / 7 / Aquarius

**Generated:** 2026-07-03

## Summary

| Metric | Count |
|--------|-------|
| Required categories | 31 |
| Filled | 29 |
| Unique | 29 |
| Duplicate | 0 |
| Weak | 0 |
| Missing (gaps) | 2 |

## Table

| layer | categoryId | text | source | status | duplicateOf |
|-------|------------|------|--------|--------|-------------|
| hero | identity | Игорь — человек, который постоянно ищет смысл и глубину во всём, что его окружает. | llm:interpretation.identity | unique | — |
| hero | main_strength | Сильная сторона — Глубина. | llm:interpretation.strengths[0] | unique | — |
| hero | main_conflict | Напряжение — закрытость. | llm:interpretation.watchouts[0] | unique | — |
| hero | life_theme | Главная тема — искать суть и собирать смысл из того, что кажется случайным. | reference:life_path.life_theme | unique | — |
| why | formation | Твой жизненный сценарий часто идет через тему дистанции, внутреннего поиска и необходимости доверять не только своему уму, но и жизни. | reference:life_path.pattern | unique | — |
| why | helps | Ты растешь, когда учишься делиться, объяснять и оставаться в контакте, а не только внутри себя. | reference:life_path.growth | unique | — |
| why | breaks | Ломается там, где включается закрытость. | reference:life_path.minus_side[0] | unique | — |
| corePattern | driver | Тебе важно не просто жить, а понимать, что происходит. Внутренний драйвер здесь — разобраться, дойти до сути и собрать смысл. | reference:life_path.driver | unique | — |
| corePattern | fear | Быть непонятым, потерять себя или оказаться в пустоте. | reference:life_path.main_fear | unique | — |
| corePattern | trap | Ловушка — Закрытость. | reference:life_path.minus_side[0] | unique | — |
| corePattern | decisions | Тебе проще начинать, когда есть структура, первый шаг и пространство подумать. | llm:interpretation.life_areas.decisions | unique | — |
| corePattern | recovery | Восстановление через тишину и прогулку без разговоров. | llm:interpretation.life_areas.body | unique | — |
| socialMirror | first_impression | Люди часто воспринимают тебя как закрытый, наблюдательный и не сразу понятный | reference:name_number.personality | unique | — |
| socialMirror | after_knowing | Ты транслируешь через глубину, анализ и поиск сути | reference:name_number.expression | unique | — |
| socialMirror | misread | Можешь казаться отстраненность, даже когда внутри всё иначе. | reference:sign.watchouts[0] | unique | — |
| socialMirror | trust | Сильная зона: много контактов, интерес к людям, легкость в связи. | reference:sign.friendship | unique | — |
| love | seeks | Близость для Водолея сложная зона. | reference:sign.intimacy | unique | — |
| love | fears | Боишься, когда попытка ограничить. | reference:sign.hurts[0] | unique | — |
| love | loves | В отношениях игорь ищет глубину и понимание, а не поверхностный контакт. | llm:interpretation.life_areas.love | unique | — |
| love | destroys | Разрушает контроль и ограничения. | reference:sign.dislikes | unique | — |
| love | strengthens | Близость крепнет через честность, общий смысл и право не спешить. | reference:life_path.relationship_strengthens | unique | — |
| money | growth_source | Ты силен в анализе, стратегии и глубокой работе. | llm:life_path.money_work[0] | unique | — |
| money | earning_style | В реализации может быть осторожным и расчётливым, когда дело касается риска. | llm:interpretation.life_areas.money | unique | — |
| money | risk | Тебе сложнее в поверхностных задачах и в постоянном контакте с людьми | reference:life_path.money_work[2] | unique | — |
| money | blind_spot | Слепая зона — Одиночество. | reference:life_path.minus_side[1] | unique | — |
| money | catalyst | Ускоряет независимость. | reference:sign.strengths[1] | unique | — |
| compass | amplify | — | — | missing | — |
| compass | avoid | Избегай одиночество. | reference:life_path.minus_side[1] | unique | — |
| compass | energy_direction | — | — | missing | — |
| compass | skill | Глубина — это не изоляция. | reference:life_path.lesson | unique | — |
| compass | check_soon | Проверь: Сильнее всего проявляется там, где нужен анализ и экспертиза. | llm:interpretation.life_areas.career | unique | — |

## Gaps (honest empty)

- `compass.amplify`
- `compass.energy_direction`

## Pass criteria

- All layers answer different user questions
- Each filled category = distinct dimension (not paraphrase)
- No literal duplicates across layers
- Gaps visible, no filler water
