# Practice Technique Normalization v1

**Статус:** `ACCEPTED` — аналитическое сравнение ingested evidence. **Не** Canonical Technique.  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product + Research.  
**Ingest:** [PRACTICE_TECHNIQUE_INGEST_V1.md](./PRACTICE_TECHNIQUE_INGEST_V1.md).  
**Landscape:** [PRACTICE_TECHNIQUE_LANDSCAPE_V1.md](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_normalization_v1.json`](../../DATA/reference/practice/technique_normalization_v1.json) · contract [`technique_normalization_contract_v1.json`](../../DATA/reference/practice/technique_normalization_contract_v1.json).

**Это:** позволяют ли три evidence records одну технику с допустимыми variants, или landscape family склеила разные identity-bearing structures.  
**Это не:** majority vote · optional hold · technique canon · `technique_id` · safety review.

`technique_canon_v1.json` остаётся **пустым**.  
`practice.box_breathing.001` остаётся provisional, без `technique_id`.  
Другие семьи **не** открыты.

Решение этого pass: **`insufficient_evidence`**. Это успешное закрытие pass, не сбой.

---

## Architecture impact

- **SoT before:** три independent evidence records. Следующий шаг мог объявить «ядром являются четыре фазы, вторая задержка optional» (2 против 1) или сразу split семьи.
- **SoT after:** Normalization сравнивает четыре уровня и имеет **ровно три** исхода: `normalize_one` · `split_family` · `insufficient_evidence`. Количество loci не определяет kernel. Для `equal_count_breath` исход = `insufficient_evidence`. Landscape kernel не переписан. Семья не разделена. Открыт узкий research question про identity post-exhale hold. `normalize_one` всё равно не был бы canonical: впереди safety review. Public JSON / library attestation не меняются.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · normalization JSON · provenance pipeline/§11 · coverage · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с `technique_id`, записью canon, или kernel-синтезом из этого pass.

---

## 0. Закон этого pass

1. **Один главный вопрос.** Одна техника с variants, или несколько техник, преждевременно объединённых одной landscape family?
2. **Не голосовать 2 против 1.** Число loci не есть kernel.
3. **Четыре уровня, не один.** Mechanism · identity-bearing steps · bounds · variants vs conflicts.
4. **Три исхода.** Других нет. `insufficient_evidence` — легитимный успех.
5. **Не дописывать знание.** «Вторая задержка optional» ingest не дал.
6. **`normalize_one` ≠ canonical.** Даже этот исход вёл бы в Safety Review, не в `technique_id`.
7. **Дерево техник проверяется здесь.** Если family нарезана неправильно, это видно на этом pass, не на Item.

---

## 1. Pipeline

```text
Landscape → Shortlist → Ingest → Normalize → Safety Review → Canonical → Item expression
```

После `insufficient_evidence` Safety Review **не** открывается. Следующий шаг — targeted shortlist на research question.

---

## 2. Четыре уровня

| Уровень | Вопрос | Наблюдение | Статус |
|---------|--------|------------|--------|
| **Mechanism** | Регулируемое циклическое дыхание с заданными фазами/счётом? | Все три — timed repeating cycle. Не согласны, сколько фаз в цикле. | coarse compatible only |
| **Identity-bearing steps** | Какие фазы обязательны для идентичности метода? | Landscape: четыре равные фазы *включая паузы*. BHF/SFH пишут обе паузы. Newcastle не пишет паузу после выдоха. | **unresolved** |
| **Bounds** | Равный счёт / «4» — метод или параметр expression? | Все иллюстрируют 4. Никто не доказывает, что 4 = ядро. Длина сессии разная. | **unresolved** |
| **Variants vs conflicts** | Нет второй задержки — другая техника или допустимая вариация? | Поза / обвести квадрат — опции самих четырёхфазных страниц. Расхождение фаз ingest уже пометил как conflict, не variant. | **unresolved** |

---

## 3. Почему не `normalize_one`

- Сделать post-exhale hold optional = внести утверждение, которого нет в ingest.
- Landscape заранее считал паузы identity-bearing; молча demote нельзя.
- Общие ярлыки box/square не есть kernel.

## 4. Почему не `split_family`

- Ни один selected locus не говорит, что трёхфазная страница — *другой метод*.
- Одни имена на разных структурах могут быть naming collision, не две семьи.
- Split сейчас заморозил бы landscape до ответа на identity-вопрос.

## 5. Решение

`decision = insufficient_evidence`

**Research question:** является ли post-exhale hold identity-bearing для семьи box/square/equal-count, или источники используют одно название для структурно разных методов?

Targeted shortlist (следующий named pass) ищет loci, которые *разводят* эти структуры как разные методы **или** явно говорят, что пустая пауза не входит в идентичность. Не открывать следующую landscape-семью. Iyengar по-прежнему NEED_OWNER, не ingest.

Landscape `mechanism_shape` **не** переписан. Семья **не** разделена.

---

## 6. Запрещено

- Писать `technique_canon_v1.json`.
- Ставить `technique_id` на probe / любой item.
- Объявлять optional hold.
- Голосовать 2 vs 1.
- Идти в Safety Review / Canonical с этим решением.
- Открывать остальные семьи «пока conflict висит».
- Считать probe `box_breathing` attested.

---

## 7. Что дальше

1. Normalization закрыт как `insufficient_evidence`. Canon пуст.
2. Следующий named pass: **targeted shortlist** на research question (post-exhale hold identity).
3. Safety Review → Canonical — только после будущего `normalize_one` (отдельный pass).
4. `technique_id` — только при `canonical`.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-25 | v1.0 ACCEPTED — four-level compare; decision `insufficient_evidence`; research question on post-exhale hold identity; not canon |
