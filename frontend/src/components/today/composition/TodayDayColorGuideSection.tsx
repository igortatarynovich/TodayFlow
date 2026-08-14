"use client";

import {
  COLOR_DAY_UNAVAILABLE_RU,
  type TodayDayColorGuide,
} from "@/lib/todayDayColorGuide";
import styles from "@/design-system/compositions/dsCompositionSurface.module.css";

type Props = {
  guide: TodayDayColorGuide;
};

/** #RRGGBB → "r, g, b" for rgba() composition; empty when hex missing (no fake gold). */
function hexToRgbTriplet(hex: string): string | null {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return `${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}`;
}

export function TodayDayColorGuideSection({ guide }: Props) {
  const rgb = hexToRgbTriplet(guide.hex);
  const unavailable = guide.unavailable || !guide.benefit.trim();

  return (
    <section
      className={styles.colorGuideSection}
      data-testid="today-zone-color-guide"
      data-fallback={unavailable ? "unavailable" : undefined}
      style={rgb ? { borderColor: `rgba(${rgb}, 0.35)` } : undefined}
    >
      <span className={styles.sectionEyebrow}>Цвет дня</span>
      {unavailable ? (
        <p className={styles.colorGuideBenefit} data-testid="today-color-unavailable">
          {COLOR_DAY_UNAVAILABLE_RU}
        </p>
      ) : (
        <>
          <h2 className={styles.colorGuideTitleRow}>
            {guide.hex ? (
              <span
                className={styles.colorGuideSwatch}
                style={{
                  background: guide.hex,
                  boxShadow: rgb ? `0 0 0 4px rgba(${rgb}, 0.14)` : undefined,
                }}
                aria-hidden
              />
            ) : null}
            <span className={styles.sectionTitle}>{guide.name}</span>
          </h2>
          <p
            className={styles.colorGuideBenefit}
            data-testid="today-color-intensity"
            data-intensity={guide.intensity}
          >
            Интенсивность: {guide.intensity}
          </p>
          <p className={styles.colorGuideBenefit}>{guide.benefit}</p>
          <dl className={styles.colorGuideList}>
            {guide.clothing ? (
              <div className={styles.colorGuideRow}>
                <dt>В одежде{guide.intensity === "мягко" ? " (мягко)" : " (ярче)"}</dt>
                <dd>{guide.clothing}</dd>
              </div>
            ) : null}
            {guide.accessory ? (
              <div className={styles.colorGuideRow}>
                <dt>Аксессуар</dt>
                <dd>{guide.accessory}</dd>
              </div>
            ) : null}
            {guide.amount ? (
              <div className={styles.colorGuideRow}>
                <dt>Сколько</dt>
                <dd>{guide.amount}</dd>
              </div>
            ) : null}
            {guide.avoidColor && guide.avoidWhy ? (
              <div className={`${styles.colorGuideRow} ${styles.colorGuideAvoid}`}>
                <dt>Лучше избегать</dt>
                <dd>
                  <strong>{guide.avoidColor}</strong> — {guide.avoidWhy}
                </dd>
              </div>
            ) : null}
          </dl>
        </>
      )}
    </section>
  );
}
