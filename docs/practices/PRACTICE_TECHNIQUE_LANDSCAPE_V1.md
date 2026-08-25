# Practice Technique Landscape v1

**Статус:** `ACCEPTED` — research ledger поля техник. **Не** technique canon. Full shortlist **не** открыт.  
**Версия:** 1.1 (2026-08-25) — vertical slice pointer.  
**Владелец:** Product + Research.  
**Parent order:** [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) шаги 5–7.  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Taxonomy:** [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md).  
**Machine ledger:** [`technique_landscape_v1.json`](../../DATA/reference/practice/technique_landscape_v1.json) · contract [`technique_landscape_contract_v1.json`](../../DATA/reference/practice/technique_landscape_contract_v1.json).

**Это:** какие устойчивые *семейства методов* существуют в поле; какими **типами источников** они описываются; какие kernel / bounds / variants надо различать до shortlist.  
**Это не:** корпус авторов · ingest · `technique_canon_v1.json` · efficacy · разрешение писать Content Items.

`technique_canon_v1.json` остаётся **пустым**. Full shortlist **не открыт**. Один family-slice: [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md).

---

## Architecture impact

- **SoT before:** provenance locked the pipeline, но следующий шаг звучал как «проверить 11 против источников». Риск — взять первую узнаваемую школу (PMR, CBT-I, values self-affirmation, forceful pranayama) и объявить её SoT нашего type.
- **SoT after:** named pass = **landscape**. Четыре карты по `content_class`. Строка ledger = `candidate_family`, не автор и не canonical technique. Taxonomy `type` может попадать в семью, не совпадать с ней, или быть product-only. Четыре probe-риска зафиксированы явно (§4). Shortlist / ingest запрещены этим документом.
- **Public contract changed?** no
- **Migration required?** no runtime. Library fill still frozen. `technique_id` still optional and unused.
- **Canon updated?** yes — этот файл · landscape JSON · provenance §11 · coverage next_pass · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с открытием shortlist или наполнением technique canon из этого pass.

---

## 0. Закон этого pass

1. **Семейство ≠ type ≠ item.** Type — код taxonomy. Family — устойчивый метод в поле. Item — наша формулировка. Один type может не иметь семьи; одна семья может покрывать несколько types.
2. **Тип источника, не фамилия.** `source_families[]` из provenance §4. Запрещено lock авторов / обязательных томов.
3. **Карта поля, не корпус.** Ledger не делает семью канонической. По умолчанию `shortlist_status = not_opened`. Shortlist V1 может пометить **ровно одну** семью `sliced`.
4. **Не схлопывать соседние методы.** PMR ≠ informal somatic release. Values self-affirmation ≠ coping statement. Sleep window rule ≠ CBT-I. Forceful pranayama ≠ «короткий выдох».
5. **Существование семьи ≠ efficacy.** `claim_risk` помечает, *где продукт обычно врёт*, не разрешает claims.
6. **Выход не в technique canon.** Criteria V1 ([PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md), parent шаг 8) задаёт допуск. Shortlist корпуса в этом файле **не** открывается; slice живёт в [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md).

Parent mapping: шаги 1–4 (предмет, границы, составляющие) уже в taxonomy + provenance §3. Этот файл = шаги 5–7.

---

## 1. Строка ledger

Каждая семья:

| Поле | Смысл |
|------|--------|
| `candidate_family` | устойчивое имя метода в поле, не бренд приложения |
| `content_class` | `practice` \| `meditation` \| `affirmation` \| `discipline` |
| `candidate_types[]` | taxonomy types, которые *могут* выражать семью; пусто = поле есть, нашего type нет или type запрещено мапить |
| `mechanism_shape` | что человек делает / на что направляет внимание |
| `bounds_to_research[]` | safety- и identity-границы, которые shortlist обязан уметь закрыть |
| `variant_axes[]` | что можно менять, не создавая другую семью |
| `source_families[]` | классы текстов, не авторы |
| `claim_risk` | где продукт чаще всего подменяет construct или обещает исход |
| `probe_links[]` | architecture-probe `item_id`, если payload попал в эту семью |
| `shortlist_status` | `not_opened` \| `sliced` (не более одной семьи) |

`claim_risk`: `none_until_ingest` · `product_only` · `likely_invention` · `construct_mismatch` · `family_collapse` · `medical_protocol_bleed` · `manifestation` · `efficacy_bleed`

---

## 2. Четыре карты (сводка)

Полные строки — JSON. Здесь — какие семьи поле обязано различать, чтобы случайная школа не стала SoT.

### 2.1 practice

Дыхание в поле — несколько семей, не один «breathwork»:

| Семья | Зачем отдельно | Typical types |
|-------|----------------|---------------|
| slow / extended-exhale | выдох ≥ вдох, без задержки как ядра | `extended_exhale`, `paced_breathing` |
| equal-count / square | равные фазы, включая паузы | `box_breathing` |
| physiological sigh | двойной вдох + длинный выдох как отдельный паттерн | `physiological_sigh` |
| activating / forceful | pump / forceful exhale (pranayama-class и clinical activation) | *ни один наш type пока не является этим ядром* |
| unattested short oral exhale | текущий `energizing_breath` payload | `energizing_breath` |

Тело — не одно «somatic»:

| Семья | Не путать с |
|-------|-------------|
| sensory grounding (через органы чувств) | interoceptive «вернись в тело» |
| progressive muscle (tense→release по группам) | один жест плеч |
| informal somatic release (drop / shake) | PMR-протокол |

Ещё семьи practice: gentle movement · expressive writing / prompted reflection · intention / mental rehearsal · micro-behavior · environment / stimulus change · small creative act · ritual as *wrapper* (последовательность других ядер, не отдельная магия).

### 2.2 meditation

Поле держит разные attentional jobs. Нельзя взять MBSR как SoT всех meditation types.

Различать минимум: focused attention · open monitoring · body-scan attention · mindfulness как **ярлык** vs метод · goodwill / metta · self-compassion meditation · relaxation imagery · walking · silence · acceptance as stance · gratitude as directed attention · visualization · guided reflection · sleep-transition attention.

`meditation.sleep` = evening downregulate attention, **не** лечение инсомнии и **не** автоматически yoga nidra.

### 2.3 affirmation

Главный развод поля — **не** список слоганов, а разные cognitive jobs:

| Семья | Mechanism shape | Наши types |
|-------|-----------------|------------|
| values self-affirmation | письмо / речь про *ценность*, не про исход | **ни один type не является этим construct** |
| coping statement | короткая фраза про обращение с текущим затруднением | `capability` (probe), частично `resilience` / `agency` |
| self-compassion phrase | поддерживающая позиция к себе | `compassion` |
| identity / worth statement | «кто я» независимо от результата | `self_identity`, `self_worth`, `self_trust` |
| permission / boundary | разрешение предела | `permission`, `boundary` |
| manifestation / outcome charm | «повторяй — получишь деньги/любовь» | **запрещённая семья**; types не мапить |

### 2.4 discipline

Различать behavioral rule на период и клинический протокол:

| Семья | Наши types | Не делать |
|-------|------------|-----------|
| schedule / sleep-window rule | `sleep_discipline` | не называть CBT-I |
| clinical insomnia protocol (CBT-I class) | `[]` | не product type; держать в карте, чтобы *не* притянуть probe |
| consistency / implementation | `routine_commitment`, `consistency_challenge`, movement/mindfulness commitments | не medical |
| stimulus limit | `digital_limit`, `attention_discipline`, `social_discipline` | не «детокс вылечит» |
| abstinence / reduction | `abstinence`, `reduction`, `comfort_reduction` | не автоматически «аскеза традиции» |
| historical-philosophical ascetic | пока `[]` или overlap с abstinence | открывать **только если** продукт явно хочет слой аскез |
| food / consumption / money caps | соответствующие types | medical / shame risk |
| speech / silence / service | соответствующие types | tradition vs behavioral — не смешивать без модели |

---

## 3. Типы источников по class

Не библиография. Классы текстов, которые shortlist потом имеет право рассматривать.

| Class | Допустимые `source_families` | Не evidence |
|-------|------------------------------|-------------|
| practice | `clinical_psychology`, `mindfulness_protocol`, `behavioral_science`, `official_health`, `academic_description`, `recognized_school` | SEO grounding, viral breath threads, LLM |
| meditation | `mindfulness_protocol`, `academic_description`, `tradition_primary`, `recognized_school` | guided-sleep YouTube script, копия MBSR workbook |
| affirmation | `behavioral_science`, `clinical_psychology`, `academic_description` | manifestation coaches, money-mantra decks |
| discipline | `behavioral_science`, `official_health`, `academic_description`; `historical_philosophical` **только** для явного аскетического слоя | punitive detox-as-medicine |

`tradition_primary` для meditation не повышает `efficacy`. `official_health` для sleep window не превращает item в CBT-I.

---

## 4. Четыре жёстких различия (probes)

### 4.1 `energizing_breath` — reject или remap, не канон

Probe `practice.energizing_breath.001`: «вдох носом, выдох ртом короче вдоха».

В поле activating breath — это **forceful / pumping** семейство (сильный выдох, усилие, часто противопоказано при головокружении, беременности, гипертонии — bounds to research). Текущий payload в это ядро **не попадает**.

Ledger:

- `family.practice.activating_forceful_breath` — поле есть, `candidate_types[]` пуст.
- `family.practice.unattested_short_exhale` — `energizing_breath` + probe. `claim_risk = likely_invention`. `likely_disposition = reject_or_remap`.

Не плодить siblings. Не мапить type на kapalabhati «потому что тоже энергия».

### 4.2 `affirmation.capability` — coping statement, не self-affirmation

Probe `affirmation.capability.001`: «Я справлюсь с тем, что прямо сейчас».

Research self-affirmation (как construct) = контакт с *ценностью*, обычно письменно, не гарантия исхода. Coping statement = краткая фраза обращения с трудностью (CBT-adjacent educational practice). Это **разные семьи**.

`capability` → `family.affirmation.coping_statement`.  
`family.affirmation.values_self_affirmation`. `candidate_types[]` пуст, пока taxonomy не заведёт отдельный type. Не подтягивать probe к values-литературе.

`claim_risk = construct_mismatch` если type продолжают читать как «научная аффирмация». Manifestation запрещён отдельно.

### 4.3 `body_release` — не PMR

Probe `practice.body_release.001`: плечи вверх — сброс.

PMR = последовательное напряжение и отпускание мышечных групп. Informal somatic release = локальный drop / shake. Схлопывание = `family_collapse`.

- `progressive_relaxation` → `family.practice.progressive_muscle_relaxation`
- `body_release` (+ `shaking_release`) → `family.practice.informal_somatic_release`

Recovery cell с `progressive_relaxation` **не** аттестует shoulder-drop item. Shoulder-drop **не** наследует Jacobson-протокол.

### 4.4 `sleep_discipline` — не CBT-I

Probe `discipline.sleep_discipline.001`: семь дней тот же час.

В поле есть:

- простая regularity / sleep-window rule (behavioral hygiene-adjacent);
- клинический пакет CBT-I (stimulus control + restriction + cognitive work, medical frame).

Probe — первое. CBT-I держится строкой с `candidate_types[] = []`, `claim_risk = medical_protocol_bleed`, чтобы shortlist не «уточнил» наш type до протокола лечения инсомнии.

7 дней item window ≠ длина клинического курса. Efficacy sleep **запрещён**.

---

## 5. Probes → семьи (индекс)

| Probe | Семья в этом ledger | Не мапить на |
|-------|---------------------|--------------|
| `practice.sensory_grounding.001` | sensory_grounding | PMR, meditation.grounding как тот же kernel |
| `practice.extended_exhale.001` | slow_paced_breath | box / forceful |
| `practice.box_breathing.001` | equal_count_breath | viral tactical as source |
| `practice.energizing_breath.001` | unattested_short_exhale | activating_forceful_breath |
| `practice.prompted_reflection.001` | expressive_writing | named clinical protocol |
| `affirmation.capability.001` | coping_statement | values_self_affirmation |
| `practice.body_release.001` | informal_somatic_release | PMR |
| `meditation.relaxation.001` | relaxation_imagery | autogenic protocol name; PMR |
| `meditation.sleep.001` | sleep_transition_attention | CBT-I; yoga nidra auto-map |
| `discipline.sleep_discipline.001` | schedule_window_rule | clinical_insomnia_protocol |
| `practice.micro_action.001` | micro_behavior | motivational slogan |

Остальные 122 items этим pass **не** разбираются построчно. Их types попадают в семьи через `candidate_types[]`, не как attestation.

---

## 6. Запрещено

- Писать строки в `technique_canon_v1.json`.
- Открывать **все** семьи сразу или фиксировать авторов / ISBN как SoT семьи.
- Считать семью каноном, потому что type так называется.
- Мапить `energizing_breath` → forceful pranayama.
- Мапить `capability` → values self-affirmation.
- Мапить `body_release` → PMR.
- Мапить `sleep_discipline` или `meditation.sleep` → CBT-I.
- Копировать протоколы. Заявлять efficacy. Писать новые Content Items.

---

## 7. Что дальше

1. Landscape стоит. Criteria V1 принят. Full shortlist **закрыт** (`shortlist_opened = false`).
2. Vertical slice: [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md). Ingest: [PRACTICE_TECHNIQUE_INGEST_V1](./PRACTICE_TECHNIQUE_INGEST_V1.md).
3. Следующий named pass: **targeted shortlist** на identity post-exhale hold. Не следующая семья. Не Safety Review.
4. `technique_id` — только на canonical.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-25 | pointer: Normalization V1 = insufficient_evidence; landscape kernel unchanged |
| 2026-08-25 | pointer: equal_count ingest done; next = Normalization V1 |
| 2026-08-25 | v1.1 — vertical slice pointer; `equal_count_breath` may be `sliced`; `official_health` added to that family's source_families; canon still empty |
| 2026-08-25 | Criteria V1 accepted; shortlist still closed; next = shortlist by family |
| 2026-08-25 | v1.0 ACCEPTED — four class maps; ledger families; shortlist closed; four probe distinctions locked as research splits, not canon |
