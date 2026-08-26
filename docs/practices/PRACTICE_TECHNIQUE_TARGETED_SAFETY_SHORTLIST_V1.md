# Practice Technique Targeted Safety Shortlist v1

**Статус:** `ACCEPTED` — узкий safety shortlist на один research question. **Не** technique canon. **Не** повтор identity shortlist.  
**Версия:** 1.0 (2026-08-26).  
**Владелец:** Product + Research.  
**Parent:** [PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md](./PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md) (`insufficient_safety`, S-B2).  
**Candidate:** [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md) (`normalize_one`; hold `required`).  
**Criteria:** [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md) (C1–C9) плюс более высокий порог для медицинских противопоказаний.  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_targeted_safety_shortlist_v1.json`](../../DATA/reference/practice/technique_targeted_safety_shortlist_v1.json) · contract [`technique_targeted_safety_shortlist_contract_v1.json`](../../DATA/reference/practice/technique_targeted_safety_shortlist_contract_v1.json).

**Это:** поиск *safety evidence* для `who_must_not_hold` у техники с обязательными задержками.  
**Это не:** исследование box/square · efficacy · оптимальный счёт · rewrite kernel · Canonical Technique · `technique_id` · продуктовый список противопоказаний.

`technique_canon_v1.json` остаётся **пустым**.  
Kernel V1.1 **не** переоткрывается.  
Safety Review V1 контракт **не** переписывается этим pass.

Решение этого pass: **stop A** — preferred-class hold evidence найден → selected loci для Targeted Safety Ingest.

---

## Architecture impact

- **SoT before:** Safety Review V1 = `insufficient_safety`. S-B2: SFH stop-rules ≠ `may_release` без `who_must_not_hold`; unknown ≠ ban. Следующий шаг мог импортировать wellness who-lists, перенести COPD «не задерживай на лестнице» на seated timed holds, или сразу писать canon.
- **SoT after:** отдельный **safety evidence track** для уже normalized candidate. Три вида речи. Wellness / popularizer / tradition **не** достаточный SoT для медицинских противопоказаний. Selected = допуск к Targeted Safety Ingest, не закрытый who-list. Structural finding записан: не склеивать method-page silence, rehab exertion advice и yoga kumbhaka exclusion в одно бинарное `who_must_not_hold` внутри shortlist. Если позже нужна модель exclude / precaution / stop_rule — решение owner на Safety Review V1.1 после ingest.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · JSON · provenance §11 · coverage · landscape pointer · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с canon, `technique_id`, optional hold, или `may_release` из этого pass.

---

## 0. Закон этого pass

1. **Один вопрос.** Кому / при каких обстоятельствах нельзя делать breath holds, или нужна предварительная профессиональная оценка?
2. **Не box breathing вообще.** Kernel уже `four_timed_phases`, hold `required`.
3. **Три вида речи.** `hold_exclusion` · `hold_precaution` · `general_breathwork_precaution`. Только первые два могут быть selected.
4. **Общее не переносится на holds.** `general_breathwork_precaution` = supporting, не закрывает `who_must_not_hold`.
5. **Выше порог источника.** Для медицинских противопоказаний не принимать wellness, популяризаторов и традицию как достаточный SoT. Предпочтение: official health / clinical guidance / professional medical / peer-reviewed safety literature. Locus — задержка дыхания или близкий механизм.
6. **Не менять контракт внутри shortlist.** Если empirical model = exclude / precaution / stop_rule, а не бинарное must_not — записать structural finding и вернуть owner на Safety Review V1.1.
7. **Дальше ingest, не canon.** Путь: Targeted Safety Ingest → Safety Review V1.1.

---

## 1. Research question (locked)

> For a technique whose identity includes required breath holds, which conditions or circumstances require not performing breath holds, or require prior professional assessment?

Не вопрос: работает ли метод, какой счёт лучше, можно ли убрать hold.

---

## 2. Виды evidence

| Вид | Что источник *делает* | Для этого вопроса |
|-----|------------------------|-------------------|
| **`hold_exclusion`** | Прямо говорит не выполнять breath holding при названном условии | Может быть selected |
| **`hold_precaution`** | Требует осторожности, модификации или профессиональной консультации именно из‑за hold / близкого retention | Может быть selected |
| **`general_breathwork_precaution`** | Относится к дыхательным упражнениям / активности вообще | Supporting; **не** selected; не авто-перенос на required hold |
| **`experimental_script`** | Стоп внутри протокола исследования | Уже ingest'нуто; не who-list |
| **`none`** | Метод без safety-речи про holds | Не resolution |

---

## 3. Критерий остановки

| Код | Когда | Этот pass |
|-----|--------|-----------|
| **A** | Достаточно preferred-class `hold_exclusion` и/или `hold_precaution` | **закрыто здесь** → Targeted Safety Ingest |
| **B** | Только `general_breathwork_precaution` | unresolved; не переносить на holds |
| **C** | Надёжные источники показывают, что универсальный who-list некорректен | structural finding; не invent список; owner / Safety Contract V1.1 |

A не означает, что `who_must_not_hold` закрыт. Только допуск к ingest.

---

## 4. Уже ingest'нутые loci (не выбирать снова)

| `source_id` | `safety_speech` | Почему не новый selected |
|-------------|-----------------|--------------------------|
| BHF box | `none` | Method page без who-list |
| SFH leaflet | `general_breathwork_precaution` | Stop-rules (dizziness / grounding). S-B2: этого мало |
| Newcastle square | `none` | Нет who-list |
| Marchant 2025 | `experimental_script` | Shallow-if-dizzy — скрипт исследования |
| CAVUHB square | `none` | Нет who-list |

---

## 5. Решения по новым loci

| `source_id` | class | `safety_speech` | decision |
|-------------|-------|-----------------|----------|
| `src.wjm.joshi.2024.yoga_hypertension` | `academic_description` | **hold_exclusion** | **selected** |
| `src.nivethitha.2017.bahir_kumbhaka` | `academic_description` | **hold_precaution** | **selected** |
| `src.bts.2009.physio_spontaneously_breathing` | `official_health` | `general_breathwork_precaution` | supporting — hold *during exertion* in COPD rehab, другой job |
| `src.nhs.cuh.breathlessness_leaflet3` | `official_health` | `general_breathwork_precaution` | supporting — то же: activity, не timed practice |
| `src.clevelandclinic.box` | `official_health` | `none` | supporting — method page, нет who-list; SEAL packaging |
| `src.healthline.box` | seo | consult-first list | **rejected** — wellness не SoT |
| `src.medicalnewstoday.box` | seo | consult-first list | **rejected** — popularizer не SoT |

**Почему selected эти два**

- **Joshi / Raveendran / Arumugam, World J Methodol 2024:** peer-reviewed medical review. Пишет, что kumbhaka (breath retention) contraindicated при hypertension, heart disease, recovery from illness/surgery/injury. Не называет box/square. Не клинический guideline. C6: yoga-as-therapy **не** ingest.
- **Nivethitha 2017:** peer-reviewed pilot. Bahir kumbhaka = external / empty-lung retention. Сообщает острый подъём SBP/DBP/MAP. Сам who-list не пишет. Близкий механизм к post-exhale hold. Dose 4-count vs yoga retention ingest обязан держать раздельно.

**Чего нет**

- Official-health locus *этого* метода с population who-must-not-hold.
- Preferred-class exclusion для pregnancy как отдельного условия (есть только на wellness pages).
- Основания склеить rehab «не задерживай на лестнице» с kumbhaka contraindication в один продуктовый список.

`selected_loci[]` = Joshi 2024 · Nivethitha 2017.

---

## 6. Structural finding (не смена контракта)

Три разных речевых акта:

1. Official-health **method pages** этого candidate — учат holds, who-list не публикуют.
2. Official-health **breathlessness rehab** — не задерживать дыхание *на усилии*.
3. Peer-reviewed **yoga kumbhaka** — exclusion/physiology для retention в другом named practice.

Shortlist **не** превращает это в бинарное `who_must_not_hold`. Поле Safety Review V1 не переименовывается. Если после ingest корректная модель = exclude / precaution / stop_rule — это owner на **Safety Review V1.1**.

Это **не** stop C: универсальный список не доказан некорректным; просто три речи нельзя склеить заранее.

---

## 7. C1–C9 на этом pass

Те же hard gates. Дополнительно: **selected не может быть `general_breathwork_precaution`.** Selected source_family ∈ {`official_health`, `clinical_psychology`, `academic_description`}.

| Gate | Что показал slice |
|------|-------------------|
| C1 | Selected loci называют retention / empty-lung hold, не только «breathing helps BP». |
| C2 | PMC / DOI. Nivethitha = legally readable abstract. |
| C3 | Hold отделяется от SEAL / yoga-therapy branding. |
| C4 | Exclusion или физиологический bound читается, либо явно не who-list. |
| C5 | Paraphrase; не копировать yoga tables / scripts. |
| C6 | Efficacy yoga/COPD/HRV не ingest. |
| C7 | Wellness who-lists fail. Tradition/school не selected для противопоказаний. |
| C8 | Три speech acts не усредняются. |
| C9 | Семья не product_only. |

---

## 8. Pipeline

```text
Safety Review V1 insufficient_safety
  → targeted safety shortlist     (этот файл)
  → targeted safety ingest        (только selected)
  → Safety Review V1.1
```

Не напрямую в canonicalization. Kernel / Normalization не reopen.

---

## 9. Запрещено

- Исследовать box/square identity заново.
- Авто-переносить general breathwork / exertion advice на required holds.
- Принимать Healthline / MNT / yoga blogs как SoT противопоказаний.
- Писать `technique_canon_v1.json` или `technique_id`.
- Объявлять hold optional.
- Invent продуктовый who-list из kumbhaka + COPD rehab.
- Переписывать Safety Review V1 контракт.
- Открывать Safety Review V1.1 до ingest.
- Открывать следующую landscape-семью.

---

## 10. Что дальше

1. Targeted Safety Shortlist закрыт (A). Canon пуст. Probe не attested.
2. Следующий named pass: **Targeted Safety Ingest** selected loci.
3. Затем Safety Review V1.1 — не canonical.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | v1.0 ACCEPTED — who_must_not_hold; stop A; Joshi 2024 + Nivethitha 2017 selected; wellness rejected; structural finding recorded, contract unchanged |
