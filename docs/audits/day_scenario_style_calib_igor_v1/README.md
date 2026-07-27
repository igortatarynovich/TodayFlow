# Калибровочный корпус «Сегодня» — igor-1990-02-13-minsk

**Status:** ACCEPTED (`owner_target` · style contrast · micro-fixes 2026-07-27)  
**Product mechanics SoT:** [DAY_SCENARIO_STYLE_HOOK_MECHANICS_V1.md](../DAY_SCENARIO_STYLE_HOOK_MECHANICS_V1.md)  
**Not:** C3.6.2 human golden consensus (отдельный трек)

8 кейсов: `cases/calib-igor-{YYYYMMDD}.md`. Один натал, реальные транзиты (Swiss Ephemeris, Moshier) на полдень по Минску. Каждый файл: §0 Facts → §1 BAD → §2 GOOD на тех же facts.

## corpus_rules

- Один конфликт на день — две силы, не список тем.
- Орбы, градусы, названия аспектов — только в §0. В §2 (GOOD) их быть не должно.
- User-facing может называть планету/знак только если это объясняет конфликт человеку.
- Реквизит выводится из тех же двух сил конфликта.
- BAD и GOOD на одном §0 (честный контраст).
- `day_card: not_revealed` — не учить модель выдумывать карту.
- `personal_day_source: classic_reduce_v0` — может ≠ продуктовой формуле; при расхождении пересчитать число, структура кейса не меняется.
- Labels: `label_source: owner_target` до human_consensus.

## Список кейсов

| Файл | Дата | Фокус контраста |
|---|---|---|
| [calib-igor-20260727.md](./cases/calib-igor-20260727.md) | 27.07.2026 | базовый эталон формата |
| [calib-igor-20260730.md](./cases/calib-igor-20260730.md) | 30.07.2026 | знак / точка пути vs число-8 |
| [calib-igor-20260803.md](./cases/calib-igor-20260803.md) | 03.08.2026 | эмоциональный пик / резкость слова |
| [calib-igor-20260807.md](./cases/calib-igor-20260807.md) | 07.08.2026 | лёгкость слова vs дисциплина числа-4 |
| [calib-igor-20260812.md](./cases/calib-igor-20260812.md) | 12.08.2026 | новое приглашение vs незакрытые дела |
| [calib-igor-20260819.md](./cases/calib-igor-20260819.md) | 19.08.2026 | навязчивая мысль vs одиночный разбор |
| [calib-igor-20260824.md](./cases/calib-igor-20260824.md) | 24.08.2026 | **props-only BAD** · взорвать vs доиграть |
| [calib-igor-20260828.md](./cases/calib-igor-20260828.md) | 28.08.2026 | **props-only BAD** · зеркало vs пауза |

## Правила приёмки

- §0 + §1 BAD + §2 GOOD на одних facts  
- GOOD: `short_name`, `opposing_forces.a/b`, ≥2 сцены с `what_happens` ≠ совету, props color/practice/affirmation/humor  
- в §2 нет орбов/°/несущих названий аспектов  
- таблицы `slot_labels_*` заполнены  
- `day_card` честно `not_revealed`  
- micro-fix: в GOOD props нет «планета=цвет» / скобок аспект-пар

## Как использовать (см. mechanics)

1. Prompt few-shot = GOOD слоты (не freeform §3).  
2. Props gate fixtures = BAD props в 24.08 / 28.08.  
3. Human consensus → sealed labels перед promotion в blocking gates.  
4. Не смешивать с C362 `label_source=human` без blind review.

## Sphere note

Корпусные `reflection` / `romantic_partnership` / `energy_body` — style IDs. При machine-ingest маппить на канон сцен продукта (`home`, `relationships`, `communication`, …).
