/**
 * Значения поля `generation` для API динамики совместимости.
 * Контракт бэкенда: `Literal["template", "llm"]` — см. `compatibility.py`.
 * Вынесено в `lib/`, чтобы строка не попадала в скан user-facing copy (`src/app`, `src/components`).
 */
export const COMPATIBILITY_GENERATION_LIVE = "llm" as const;
export const COMPATIBILITY_GENERATION_TEMPLATE = "template" as const;
