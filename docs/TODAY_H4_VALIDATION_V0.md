# TODAY_H4_VALIDATION_V0 — Observable Pattern Hypothesis

**Статус:** `SUPPORTED` — preliminary editorial sign-off (2026-06-23)  
**Версия:** 0.2 (2026-06-23)  
**Гипотеза:** H4 Observable · **H5 candidate:** [TODAY_SELF_VERIFICATION_V0.md](./TODAY_SELF_VERIFICATION_V0.md)  
**Dataset:** [datasets/TODAY_H4_VALIDATION_V0.json](./datasets/TODAY_H4_VALIDATION_V0.json)

**Связь:** [TODAY_LANGUAGE_CALIBRATION_V0.md](today-language/TODAY_LANGUAGE_CALIBRATION_V0.md) · TL-0C.5

---

## Editorial sign-off (2026-06-23)

### H4 — Supported, with limitation

| | |
|---|---|
| **Status** | **SUPPORTED** (preliminary editorial) |
| **Finding** | Class R (observable) стабильно сильнее Class G (interpretive) на validation set |
| **Limitation** | H4 **не объясняет** все strong examples (delayed message, postponed conversation, expectation без observable action) |
| **Role** | **Editorial rule:** «сначала наблюдаемое, потом вывод» — хорошо для правки G→R |
| **Not** | Root data model для всего качества Today |

**Evidence:** 20/20 structural alignment (10 R → keep/exemplar; 10 G → rewrite/reject; G fixes → observable).

### H5 candidate

H4 likely **subset** of **H5 Self-Verification** — см. [TODAY_SELF_VERIFICATION_V0.md](./TODAY_SELF_VERIFICATION_V0.md).

---

## Зачем (исторически)

---

## Критерий подтверждения H4

H4 **подтверждается**, если на validation set:

1. **Class R** чаще → `keep` / `exemplar`
2. **Class G** чаще → `rewrite` / `reject`
3. **Class G** становится сильным **только** после `text_improved` с observable marker (перевод в наблюдаемое)

Не score alone — смотрим `pattern_class` × `editorial_decision` × `interpretation_required`.

---

## Поля записи

| Поле | Зачем |
|------|--------|
| `pattern_id` | IP-001…IP-008 |
| `pattern_class` | `R` \| `G` |
| `observable_marker` | Что можно наблюдать («вчера буквально») — null если G без observable |
| `interpretation_required` | `true` = нужна психологическая трактовка; `false` = observable |
| `editorial_decision` | keep / rewrite / reject / exemplar |
| `text` | Исходная фраза |
| `text_improved` | Для rewrite/reject→observable: наблюдаемая версия |
| `theme_id` | Опционально: связанная тема для G→observable пар |

---

## Class R — Observable / Recognition (10)

| id | IP | observable_marker | decision | cal_ref |
|----|-----|-------------------|----------|---------|
| h4-r01 | IP-002 | перегруз / один приоритет | keep | cal-031 |
| h4-r02 | IP-002 | слишком много задач | keep | cal-078 |
| h4-r03 | IP-004 | «надо собраться» | exemplar | cal-049 |
| h4-r04 | IP-004 | чужие приоритеты | exemplar | cal-050 |
| h4-r05 | IP-007 | усталость / тело | keep | cal-054 |
| h4-r06 | IP-001 | давно откладывал + отчёт | exemplar | cal-029 |
| h4-r07 | IP-001 | одна задача, не распыляться | keep | cal-074 |
| h4-r08 | IP-002 | реактивность на сигналы | keep | cal-055 |
| h4-r09 | IP-007 | усталость vs движение | keep | cal-030 |
| h4-r10 | IP-001 | задача уже начата | keep | cal-077 |

---

## Class G — Interpretive / Generic (10)

| id | IP | interpretation | decision | observable fix |
|----|-----|----------------|----------|----------------|
| h4-g01 | IP-003 | избегайте догадок | rewrite | cal-036 → text_improved |
| h4-g02 | IP-003 | догадки vs диалог | rewrite | cal-043 |
| h4-g03 | IP-003 | атмосфера доверия | rewrite | cal-045 |
| h4-g04 | IP-008 | изолирован → разговор | reject | cal-023 |
| h4-g05 | IP-008 | замыкание → откровенность | rewrite | cal-042 |
| h4-g06 | G-lex | эмоциональная гармония | rewrite | cal-040 |
| h4-g07 | G-lex | открытость / углубление связи | rewrite | cal-034 |
| h4-g08 | G-lex | ясность и открытость в любви | reject | cal-065 |
| h4-g09 | G-lex | **избегаете близости** | reject | editorial → observable pair |
| h4-g10 | G-lex | **сложно доверять** | reject | editorial → observable pair |

**h4-g09 / h4-g10:** синтетические интерпретации + `text_improved` с observable marker — проверка пункта 3 критерия H4.

---

## Процесс sign-off

1. Editorial review 20 entries (поля заполнены)
2. Посчитать: R → keep+exemplar rate; G → rewrite+reject rate
3. Проверить G с `text_improved`: observable version → would-be keep?
4. Зафиксировать: **CONFIRMED** / **REFINED** / **REFUTED** в JSON `validation_result`
5. Только после CONFIRMED/REFINED → правило генерации в канон (не TL-1 код сразу)

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v0.2 — editorial sign-off SUPPORTED + limitation; H5 candidate link |
| 2026-06-23 | v0.1 — 20 entries (10 R + 10 G); protocol + criteria |
