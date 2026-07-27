# Day Scenario — Style Hook Mechanics V1

**Status:** ACCEPTED (product style SoT for calibration · not a new meaning SoT)  
**Date:** 2026-07-27  
**Evidence pack:** [day_scenario_style_calib_igor_v1/](./day_scenario_style_calib_igor_v1/) (8 contrast cases · `owner_target`)  
**Canon spine:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md) · [DAY_SCENARIO_EVERYDAY_QUALITY_C31.md](./DAY_SCENARIO_EVERYDAY_QUALITY_C31.md) · [TODAYFLOW_VOICE_CANON.md](../content/TODAYFLOW_VOICE_CANON.md)  
**Not:** replacement for C3.6.2 human golden consensus · not formula-bank overwrite

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** everyday/chorus/personalization gates + human golden labels; style bar
  implicit in Voice Canon + C3.1 scene rules
- **SoT after:** explicit hook mechanics (moment · stakes conflict · trap-before ·
  domestic check · trap-solving props · conflict humor · evening_payoff retention)
  with contrast corpus; meaning SoT unchanged (day_scenario_v1)
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + corpus README + DAY_SCENARIO_V1 / C31 links
- **Backward compatible?** yes — eval/prompt/gate consume later; runtime unchanged until wired
```

## Purpose

Зафиксировать **конкретные механики**, из-за которых «Сегодня» цепляет открыть завтра — не общие слова про персонализацию.  
Корпус `igor` = contrast BAD↔GOOD на реальных транзитах. Labels пока `owner_target`; для gate promotion нужен `human_consensus`.

**Этический край:** крючок = «любопытно сверить / маленькое полезное действие», не тревожный компульсивный чекин.

---

## Seven hooks (product rules)

| # | Hook | Что делает | Слот | Gate / defect (сейчас или next) |
|---|------|------------|------|----------------------------------|
| H1 | **Moment specificity** | Узнаётся *момент*, не тема дня | `scenes[].what_happens` · `domestic_example` | `SCENE_ABSTRACT` · `SCENE_MISSING_EVERYDAY` (landed) |
| H2 | **Conflict with stakes** | Одна нерешённая ось a↔b | `conflict.short_name` · `opposing_forces` | next: `CONFLICT_ABSTRACT` / one-sided luck (eval only) |
| H3 | **Trap-before** | Предупреждение *до*, не разбор *после* | `scenes[].trap` | `SCENE_MISSING_CHOICE` (soft) · strengthen wording in prompt |
| H4 | **Domestic check** | Вечером сверяемо: случилось / нет | `domestic_example` | `SCENE_MISSING_EVERYDAY` |
| H5 | **Props solve trap** | Цвет / практика / аффирмация **компенсируют** trap | `props.*` + `compensates_trap` / `link_to_conflict` | `AFFIRMATION_UNNATURAL` (landed) · next: `PROP_ORPHAN` · `AFFIRMATION_AMPLIFIES_TRAP` |
| H6 | **Humor on conflict** | Шутка только про сегодняшнюю ось | `props.humor` | `ASTRO_JARGON_BARE` · next: surface humor in UI |
| H7 | **Evening payoff** | Отложенная проверка → причина открыть вечером/завтра | `evening_payoff` / `evening_closure` | FE: partial (`evening_closure`) · ensure projector + chapter `vibe` |

### Anti-patterns (из BAD корпуса)

| Pattern | Пример | Product reject |
|---------|--------|----------------|
| Theme without moment | «хороший день для общения» | `SCENE_ABSTRACT` / `SCENE_IS_ADVICE` |
| Conflict without stakes | «День активности» | eval `CONFLICT_ABSTRACT` |
| Orphan color | «красный, потому что Марс» | next `PROP_ORPHAN` |
| Wellness / manifestation affirm | «Вселенная поддерживает…» | `AFFIRMATION_UNNATURAL` |
| Affirm that *amplifies* trap | «Я сильный…» в день паузы | next `AFFIRMATION_AMPLIFIES_TRAP` |
| Jargon humor | «Марс в оппозиции…» | `ASTRO_JARGON_BARE` |
| Esoteric practice stamp | «Загадайте желание на новолуние» | next `PRACTICE_ESOTERIC_CLICHE` |

Орбы / ° / названия аспектов как несущая фраза — **только §0 Facts** (корпус) / kitchen; user-facing — смысл + жизнь.

---

## How to use this pack (ordered)

1. **Prompt / editorial** — при C3.1+ refresh: вшить H1–H7 как hard style rules (few-shot = GOOD slots, не freeform эссе).  
2. **Props gate (next eng)** — orphan color, affirm≠trap, humor≠jargon, practice≠generic; contrast cases `20260824` / `20260828` = fixtures.  
3. **UI** — показать `humor` + явный `evening_payoff` в chapter `supports` / `vibe` (сейчас humor генерится, FE почти не рендерит).  
4. **Eval** — score GOOD vs live output на H1–H7; BAD = negative fixtures (не смешивать с C362 `human` consensus без sealed review).  
5. **Human consensus** — 2–3 читателя на `slot_labels_*`; расхождения → gate calibration, не silent prompt tweak.  
6. **Numerology** — `personal_day_source: classic_reduce_v0` может ≠ продуктовой формуле; при расхождении пересчитать число, не ломая слоты.

**Запрет:** formula-bank overwrite GOOD-прозы после LLM. Fill-empty / reject-invalid / retry — как в C3.1.

---

## Retention loop (product)

```text
moment (H1) → stakes conflict (H2) → trap-before (H3)
    → domestic check (H4) → props that win the trap (H5–H6)
    → evening_payoff (H7) → reopen tomorrow
```

Условие устойчивости: достаточно частые ощущаемые попадания. Иначе тот же крючок разрушает доверие. Поэтому human_consensus — не бюрократия, а safety для масштаба.

---

## Next engineering (explicit)

| ID | Work | Depends |
|----|------|---------|
| SH-1 | Land corpus under `day_scenario_style_calib_igor_v1/` | done (this pack) |
| SH-2 | Prompt patch: H1–H7 + 1–2 GOOD few-shot slots (RU) | SH-1 |
| SH-3 | Props editorial gate (`PROP_ORPHAN`, amplifies-trap, jargon humor) | SH-1 · C3.1 |
| SH-4 | FE: render `humor` + strengthen evening payoff in chapters | C2 |
| SH-5 | Human consensus pass on 8 cases → sealed labels | SH-1 |
| SH-6 | Align `personal_day` with product numerology formula | product decide |

---

## Related

- Corpus README: [day_scenario_style_calib_igor_v1/README.md](./day_scenario_style_calib_igor_v1/README.md)  
- Human golden (separate track): [DAY_SCENARIO_HUMAN_GOLDEN_C362.md](./DAY_SCENARIO_HUMAN_GOLDEN_C362.md)  
- Everyday gate: [DAY_SCENARIO_EVERYDAY_QUALITY_C31.md](./DAY_SCENARIO_EVERYDAY_QUALITY_C31.md)
