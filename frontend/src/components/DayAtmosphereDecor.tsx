"use client";

/**
 * Decorative layer for Day Atmosphere (FOUNDATION_UI §11.4 / §13).
 * Geometry is CSS-only, keyed by `html[data-day-decor]` (DAY_MODE_DECOR_VARIANTS).
 * Photo wash paints once on the product frame via `--day-bg-art` — not here.
 * When `html[data-day-photo=step]`, this layer is display:none (step owns photo).
 */
export function DayAtmosphereDecor() {
  return (
    <div className="day-atmosphere-decor" aria-hidden="true" data-testid="day-atmosphere-decor">
      <div className="day-atmosphere-decor__art" />
    </div>
  );
}
