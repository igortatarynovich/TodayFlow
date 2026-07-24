/**
 * Токены интенсивности heatmap-карты (контраст, без текста внутри клеток).
 * Пороги долей: 0% | 1–30% | 30–70% | 70–100%
 */

export const HEATMAP_THRESHOLDS = {
  /** выше = не «пусто», а уже низкая интенсивность */
  lowMin: 1 / 1000,
  midMin: 0.3,
  highMin: 0.7,
} as const;

/**
 * Фон клетки: сначала читаем :root (legacy tokens in `styles/globals/01-tokens-base.css`), fallback — те же значения.
 * Меняй палитру в одном месте: `--heatmap-*` в tokens-base module.
 */
export const HEATMAP_CELL_BG = {
  noData: "var(--heatmap-no-data, rgba(180, 170, 158, 0.42))",
  intensity0: "var(--heatmap-intensity-0, rgba(232, 218, 195, 0.35))",
  intensityLow: "var(--heatmap-intensity-low, rgba(211, 177, 120, 0.38))",
  intensityMid: "var(--heatmap-intensity-mid, rgba(191, 151, 95, 0.62))",
  intensityHigh: "var(--heatmap-intensity-high, rgba(155, 118, 70, 0.92))",
  entityDone: "var(--heatmap-entity-done, rgba(132, 98, 52, 0.95))",
  entityMiss: "var(--heatmap-entity-miss, rgba(236, 228, 214, 0.55))",
  hoverRing: "var(--heatmap-hover-ring, rgba(120, 90, 45, 0.55))",
} as const;
