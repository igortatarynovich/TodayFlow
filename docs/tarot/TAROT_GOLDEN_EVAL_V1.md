# Tarot Golden Eval v1

**Статус:** ACTIVE (2026-07-25) — рубрикатор + harness; **freeze lift** только после прогона с результатами  
**Тип:** quality eval / gate  
**Связанные:** [TAROT_GOLDEN_DATASET_V1.md](./TAROT_GOLDEN_DATASET_V1.md) · [TAROT_INTERPRETATION_ENGINE_V1.md](./TAROT_INTERPRETATION_ENGINE_V1.md)

---

## 0. Разделение

| Artifact | Role |
|----------|------|
| **Golden Dataset** | сценарии без баллов |
| **Golden Eval** | рубрикатор + прогон ответов по датасету |

Не смешивать: новые сценарии не требуют менять рубрикатор; правка шкалы не требует переписывать датасет.

---

## 1. Rubric (1–5)

| id | Критерий | 1 | 5 |
|----|----------|---|---|
| `answered_question` | Ответил на вопрос | уходит в энциклопедию карт | прямой ответ на *этот* вопрос |
| `clarity` | Понятность | мутно / канцелярит | ясно с первого чтения |
| `story_not_card_list` | История вместо списка | «карта 1… карта 2…» | одна история конфликта |
| `symbolism_natural` | Символика | шаблон / «Аркан» | символ вплетён в ситуацию |
| `practical_use` | Практическая польза | нет шага / абстракция | один применимый next_step |
| `no_repetition` | Нет повторов | одни и те же фразы | каждый блок несёт новое |
| `no_false_confidence` | Нет ложной уверенности | «точно / гарантированно / он думает…» | честные границы знания |
| `want_to_finish` | Хочется дочитать | скучно / обрыв | держит внимание до шага |

Отдельно (да/нет/null): **`paid_worth`** — «Я бы заплатил за такой разбор.»  
(null = не оценивалось автоматически / ждёт человека)

---

## 2. Anti-sameness

На наборе ≥ N ответов (цель ~30; v1 seed = все сценарии датасета × live):

- средний pairwise similarity `direct_answer` (простая n-gram / token Jaccard)
- флаг `anti_sameness_pass` если средняя схожесть ниже порога

Не поднимать freeze, если ответы — один шаблон с переставленными существительными.

---

## 3. answer_shape (из Dataset)

Структурные флаги сценария проверяются отдельно от 1–5:

| flag | Offline / Live |
|------|----------------|
| `no_arkan_label` | текст без «Аркан» |
| `compare_options` | choice: есть различение вариантов |
| `one_story` | нет механического списка карт |
| `direct_answer` | non-empty direct_answer |
| `next_step` | non-empty next_step |
| `no_other_mind_as_fact` | нет «он точно…» / «она думает…» как факт |
| `no_exact_date` | нет конкретной календарной даты |
| `distinct_minors` | Q1 pack fields различаются у соседних карт |
| `card_name_ablation_ready` | после удаления имён карт текст всё ещё различает ситуации (heuristic) |

---

## 4. SoT paths

| Layer | Path |
|-------|------|
| Canon | этот документ |
| Rubric result schema | `docs/schemas/tarot_golden_eval_result_v1.schema.json` |
| Scorer | `backend/src/todayflow_backend/services/tarot_golden_eval_v1.py` |
| CLI | `scripts/tarot_golden_eval_v1.py` |
| Dataset input | `backend/tests/fixtures/tarot_golden_dataset_v1.json` |

Public `tarot_answer_v1` **не** меняется. Prompt wording — только после Eval (Q3).

---

## 5. Modes

```bash
# Offline: pack + shape gates (no LLM)
PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_golden_eval_v1.py

# Live: LLM answers + rubric heuristics (+ optional --out report.json)
PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_golden_eval_v1.py --live --out /tmp/tarot_golden_eval.json
```

Human can override `paid_worth` and rubric scores in the report later; harness never invents architecture changes from low scores alone.

---

## 6. Freeze lift gate

Поднять Interpretation Stack freeze **только если**:

1. Live прогон по Golden Dataset записан (report)
2. Нет системных провалов shape (`no_arkan_label`, `direct_answer`, `next_step`)
3. Anti-sameness не провален
4. Средние rubric ≥ порога продукта (зафиксировать в report `gates`)
5. **LLM pass rate ≥ 0.85** (quality reject → fallback не считается pass)

Пока отчёт не принят владельцем — freeze **ACTIVE**.

Первый live: [TAROT_GOLDEN_EVAL_LIVE_2026-07-25](../audits/TAROT_GOLDEN_EVAL_LIVE_2026-07-25.md) — **7/12 LLM · freeze not lifted**.

---

## 7. Acceptance

- [x] Rubric + result schema + scorer + CLI
- [x] Offline tests on Dataset
- [x] first live report recorded (2026-07-25) — llm_pass 7/12, freeze not lifted
- [ ] live report accepted by owner / freeze lift decision
