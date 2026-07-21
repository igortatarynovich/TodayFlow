# Compatibility Review Pack v1

**Цель:** scorecard отсекает технический брак; ценность и качество текста оцениваются людьми по реальным примерам.

**Связь:** [COMPATIBILITY_CONTENT_CANON_V1.md](./COMPATIBILITY_CONTENT_CANON_V1.md) · runner `backend/evals/compatibility_quality/run_review_packs_v1.py`

---

## Состав одного пакета

| # | Блок | Содержание |
|---|------|------------|
| 1 | Входные данные | tier, способ расчёта, person_1/2, `source_depth`, вопрос, locale, missing/hidden |
| 2 | Запрос модели | system / developer / user целиком, контекст, prompt ID/version, model, params, JSON schema |
| 3 | Сырой ответ | до parser / validators / banned / tariff cut / fallback / UI |
| 4 | Итог продукта | parsed contract, validation, user-facing, locked by tier, postprocess, retry/fallback |
| — | Tech | latency, tokens (если есть), cost (если есть), model |
| — | Оценка | liked / bad / repeats / invented / missing / shippable / 1–10 |

Секреты, токены и технические ID пользователей **не** попадают в пакет.

---

## Первый прогон (10 кейсов)

Не 30 сразу. Пакет:

1. 3× registered по знакам  
2. 2× registered по датам  
3. 2× registered с профилями  
4. 2× premium с вопросом  
5. 1× сложный / неполный  

Запуск (в окружении с LLM, напр. backend-контейнер):

```bash
python /path/to/run_review_packs_v1.py --batch first10
```

Артефакты: `backend/evals/compatibility_quality/runs/review_packs_<UTC>/`  
— `case_XX_*.md` / `.json` + `index.json`

---

## Критерий решения

Production enrichment на content v1 — только после ручной оценки (≥ эти 10, затем расширение) и сравнения с текущим baseline. Флаг: `COMPATIBILITY_CONTENT_V1`.
