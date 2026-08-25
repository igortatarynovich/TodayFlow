# Practice Technique Targeted Shortlist v1

**Статус:** `ACCEPTED` — узкий shortlist на один research question. **Не** technique canon. **Не** повтор family shortlist.  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product + Research.  
**Parent question:** [PRACTICE_TECHNIQUE_NORMALIZATION_V1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md) (`insufficient_evidence`).  
**Family slice:** [PRACTICE_TECHNIQUE_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md) · [PRACTICE_TECHNIQUE_INGEST_V1.md](./PRACTICE_TECHNIQUE_INGEST_V1.md).  
**Criteria:** [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md) (C1–C9 остаются).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_targeted_shortlist_v1.json`](../../DATA/reference/practice/technique_targeted_shortlist_v1.json) · contract [`technique_targeted_shortlist_contract_v1.json`](../../DATA/reference/practice/technique_targeted_shortlist_contract_v1.json).

**Это:** поиск *resolution evidence* для вопроса Normalization V1.  
**Это не:** исследование «box breathing вообще» · majority vote · optional hold · Safety Review · Canonical Technique · `technique_id`.

`technique_canon_v1.json` остаётся **пустым**.  
Type `box_breathing` остаётся expression hypothesis.  
Другие landscape-семьи: `not_opened`.

---

## Architecture impact

- **SoT before:** Normalization V1 закрыл `equal_count_breath` как `insufficient_evidence`. Следующий шаг мог снова собрать health-education страницы 4-4-4-4, открыть Safety Review, или объявить hold optional.
- **SoT after:** после `insufficient_evidence` pipeline идёт **targeted shortlist → targeted ingest → Normalization V1.1**. Scope = один вопрос. Три допустимых вида resolution evidence. Replication 4-4-4-4 не закрывает вопрос. `resolution_role` и `identity_statement` классифицируют *что источник сообщает*, не канонический вывод. Pass закрыт: definition + contrast найдены в предпочтительных классах; variant в C7-preferred class **не** найден. `selected` = допуск к **targeted ingest**, не kernel. Если Normalization V1.1 снова `insufficient_evidence`, допустимо не канонизировать `box_breathing` и оставить type без production item.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen. Probes without `technique_id`.
- **Canon updated?** yes — этот файл · targeted shortlist JSON · provenance §11 / pipeline · landscape/coverage next pointer · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с Safety Review, записью canon, `technique_id`, или синтезом optional hold из этого pass.

---

## 0. Закон этого pass

1. **Один вопрос.** Является ли задержка после выдоха identity-bearing элементом метода, или источники используют box / square / equal-count breathing для нескольких структур?
2. **Не «box breathing вообще».** Family shortlist уже отобрал BHF / SFH / Newcastle. Повторять 4-4-4-4 не нужно.
3. **Три вида resolution evidence.** Definition · contrast · variant. Только они двигают Normalization V1.1.
4. **Replication ≠ resolution.** Страница, которая снова пишет 4-4-4-4 без requiredness / contrast / variant, почти ничего не добавляет.
5. **Классификация ≠ inference.** `resolution_role` и `identity_statement` фиксируют сообщение источника относительно вопроса, не kernel.
6. **Критерий остановки заранее.** Закрыть, когда есть resolution candidates для targeted ingest **или** разумный поиск не находит такого evidence. Не собирать десять одинаковых health-ed страниц.
7. **Дальше — Normalization V1.1, не Safety Review.** Путь: targeted ingest выбранных resolution loci, затем retry. Повторный `insufficient_evidence` допустим.

---

## 1. Research question (locked)

> Is the post-exhale hold identity-bearing for the box / square / equal-count method, or do sources use those names for structurally different sequences?

Не вопрос этого pass: работает ли метод, кто его «изобрёл», какой ISBN подтвердит type `box_breathing`.

---

## 2. Виды evidence

| Вид | Что источник *делает* | Для этого вопроса |
|-----|------------------------|-------------------|
| **Definition** | Прямо определяет структуру метода и перечисляет обязательные фазы | Resolution |
| **Contrast** | Различает 3-phase и 4-phase **или** даёт им разные названия; либо операционализирует no-hold equal breathing как *другое* условие, не как тот же метод | Resolution |
| **Variant** | Прямо говорит, что post-exhale hold можно исключить/добавить, **сохраняя идентичность метода** | Resolution |
| **Replication** | Снова пишет 4-4-4-4 (или уже ingest'нутый паттерн) без requiredness / contrast / variant | Не resolution |
| **Non-resolving** | Пишет структуру, но не отвечает на вопрос (нет contrast, нет «optional», нет определения обязательности) | Не resolution |

`identity_statement` (отдельно, не вывод канона):

| Значение | Источник сообщает |
|----------|-------------------|
| `required` | Post-exhale hold входит в определяемую им структуру метода |
| `optional` | Hold можно опустить/добавить, метод тот же |
| `absent_but_unaddressed` | Hold нет в описании; источник не объясняет, обязателен ли он и тот ли это метод |
| `distinguishes_method` | Источник отделяет эту структуру от другой *как другой метод / другое условие* |
| `unknown` | Источник пишет фазы, но не говорит, identity-bearing ли hold |

---

## 3. Критерий остановки

Targeted shortlist **закрывается**, когда выполняется одно:

1. **Resolution candidates.** Есть хотя бы один locus с `resolution_role` ∈ {definition, contrast, variant}, прошедший C1–C9 как selected — достаточно для targeted ingest и Normalization V1.1. Дальнейшие replication-страницы не собираются.
2. **Unresolved search.** Разумный поиск в предпочтительных `source_family` не находит definition / contrast / variant. Тогда `selected_loci = []`, вопрос остаётся unresolved, следующий шаг всё равно **Normalization V1.1** (retry на уже ingest'нутом корпусе, без новых records).

Этот pass закрыт по (1): definition + contrast найдены. Variant в preferred class **не** найден — это фиксируется, не дописывается из yoga/SEO блогов.

---

## 4. Уже ingest'нутые loci (не выбирать снова)

| `source_id` | `resolution_role` | `identity_statement` | Почему не resolution |
|-------------|-------------------|----------------------|----------------------|
| `src.bhf.heart_matters.box` | `replication` | `unknown` | Четыре фазы с обеими паузами; не говорит, обязателен ли empty-lung hold |
| `src.nhs.sfh.box_leaflet` | `replication` | `unknown` | То же: операционализация 4-phase, не requiredness |
| `src.nhs.newcastle.square` | `non_resolving` | `absent_but_unaddressed` | Три фазы под именем square; **не** противопоставляет 3-phase 4-phase и **не** переименовывает |

Newcastle — naming collision *наблюдается*, но locus сам contrast evidence не даёт. Conflict ingest уже записал.

---

## 5. Решения по новым loci

Полные гейты — JSON. Здесь — зачем locus в этом вопросе.

| `source_id` | class | `resolution_role` | `identity_statement` | decision |
|-------------|-------|-------------------|----------------------|----------|
| `src.byu.marchant.2025.square` | `academic_description` | **contrast** (плюс definition square = 4×hold) | `distinguishes_method` | **selected** |
| `src.nhs.wales.cavuhb.square` | `official_health` | **definition** (square как 4-4-6-2) | `unknown` | **selected** |
| `src.iyengar.light_on_pranayama.ch18` | `recognized_school` | definition *samavrtti* (unread) | `unknown` | supporting, NEED_OWNER |
| `src.balban.2023.box_protocol` | `academic_description` | `replication` | `unknown` | supporting — 4-hold box в methods; efficacy out of scope |
| `src.healthline.box` | SEO | `replication` | `unknown` | **rejected** C6/C7 |
| `src.usu.extension.box` | packaging | `replication` | `unknown` | **rejected** C3 |
| `src.growtherapy.square` | SEO | weak variant | `optional` (panic adaptation) | **rejected** C7 — не identity SoT |
| `src.yogaeasy.samavritti` | consumer yoga | variant-shaped | `optional` | **rejected** C7 |
| `src.ayurwiki.vritti` | wiki | — | `unknown` | **rejected** C2/C5 |

**Почему selected именно эти два**

- **Marchant 2025 (BYU):** methods задают *square* как inhale 4 / hold 4 / exhale 4 / hold 4 и отдельно *5:5* как inhale 5 / exhale 5 **без** holds. Это contrast: no-hold equal breathing — другое экспериментальное условие, не вариант square. Definition square включает post-exhale hold. C6: HRV/mood **не** ingest. C3: tactical mentions в intro не есть methods.
- **CAVUHB NHS Wales workbook:** «Square breathing» = in 4 / hold 4 / out **6** / hold **2**. То же имя, другая структура (не equal-count). Это definition evidence второй половины вопроса: ярлык square не фиксирует 4-4-4-4. Не variant: hold после выдоха *есть*, источник не говорит, что его можно убрать. Не contrast 3-phase vs 4-phase по имени.

**Чего нет**

- Preferred-class locus, который говорит: «post-exhale hold можно опустить, это всё ещё box/square». YogaEasy / Grow Therapy не selected.
- Official/academic locus, который *называет* трёхфазный Newcastle-паттерн другим методом, чем четырёхфазный box.

`selected_loci[]` = BYU Marchant · NHS Wales CAVUHB.

---

## 6. C1–C9 на этом pass

Те же hard gates. Дополнительно: **selected не может быть `replication`.**

| Gate | Что targeted slice показал |
|------|----------------------------|
| C1 | BYU methods и NHS Wales square section описывают шаги, не только эффект. |
| C2 | Public thesis PDF / NHS Wales workbook URL. Iyengar по-прежнему NEED_OWNER. Ayurwiki не locus. |
| C3 | BYU methods отделимы от SEAL-packaging. USU Extension — нет. |
| C4 | Счёт в protocols извлекаем; who-must-not-hold часто `bounds_unknown`. |
| C5 | Paraphrase kernel; не копировать scripts. |
| C6 | BYU — efficacy study: взять только operational definition / contrast. Workbook — anxiety help: взять только структуру square. |
| C7 | Academic + official_health предпочтительнее consumer yoga / SEO. |
| C8 | Конфликт фаз / имён записывается. Не усреднять Newcastle с BYU. |
| C9 | Семья не product_only. |

---

## 7. Pipeline после `insufficient_evidence`

```text
insufficient_evidence
  → targeted shortlist     (этот файл)
  → targeted ingest        (только selected resolution loci)
  → Normalization V1.1
```

Safety Review **не** открывается от `insufficient_evidence` и **не** открывается от этого shortlist.

Если Normalization V1.1 снова `insufficient_evidence` — это допустимый исход. Тогда продуктовое решение может быть: **не** канонизировать `box_breathing`; оставить type без production item, пока provenance не достаточен.

`normalize_one` (если когда-либо) всё равно вёл бы в Safety Review, не сразу в `technique_id`.

---

## 8. Запрещено

- Исследовать «box breathing вообще» или открывать следующую landscape-семью.
- Выбирать replication 4-4-4-4 «для полноты».
- Объявлять optional hold из SEO / yoga blogs.
- Писать `technique_canon_v1.json`.
- Ставить `technique_id` на probe.
- Идти в Safety Review / Canonical.
- Считать `selected` каноном или аттестацией type.
- Переписывать landscape `mechanism_shape`.
- Усреднять BYU (square = 4 holds) с Newcastle (square без post-exhale hold).

---

## 9. Что дальше

1. Targeted shortlist закрыт. Targeted ingest двух selected loci закрыт: [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md). Canon пуст. Type не attested.
2. Следующий named pass: **Normalization V1.1** (два identity-вопроса, затем overall verdict). Не Safety Review.
3. Safety Review — только после будущего `normalize_one` с достаточно определённым kernel.
4. `technique_id` — только при `canonical`.
5. Повторный `insufficient_evidence` после V1.1 — допустим; тогда type может остаться без production item.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-25 | pointer: Targeted Ingest V1 closed; next = Normalization V1.1 |
| 2026-08-25 | v1.0 ACCEPTED — post-exhale hold identity; definition + contrast selected; variant not found in preferred class; next = targeted ingest → Normalization V1.1 |
