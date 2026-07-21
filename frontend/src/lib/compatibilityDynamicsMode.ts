/**
 * Значения поля `generation` для API динамики совместимости.
 * Контракт бэкенда: `Literal["template", "llm"]` — см. `compatibility.py`.
 *
 * C1: `llm` means “want enrichment” — server still returns baseline immediately
 * and enqueues a background job. FE must not wait on Nebius for first paint.
 */
export const COMPATIBILITY_GENERATION_TEMPLATE = "template" as const;
export const COMPATIBILITY_GENERATION_LLM = "llm" as const;
/** Live analyze path: baseline + async enrichment for registered users. */
export const COMPATIBILITY_GENERATION_LIVE = COMPATIBILITY_GENERATION_LLM;
