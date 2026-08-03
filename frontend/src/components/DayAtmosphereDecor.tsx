"use client";

/**
 * Decorative layer for Day Atmosphere (FOUNDATION_UI §11.4 / §13).
 * Art is CSS-only closed variants keyed by html[data-day-mode] / [data-day-decor].
 * Mockup PNGs are art direction seed — not raw SoT backgrounds.
 */
export function DayAtmosphereDecor() {
  return (
    <div className="day-atmosphere-decor" aria-hidden="true" data-testid="day-atmosphere-decor">
      <div className="day-atmosphere-decor__art" />
    </div>
  );
}
