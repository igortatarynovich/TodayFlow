"use client";

import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  guide: TodayDayColorGuide;
};

/** #RRGGBB → "r, g, b" for rgba() composition; falls back to a neutral gold if unparsable. */
function hexToRgbTriplet(hex: string): string {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return "201, 169, 110";
  const n = parseInt(m[1], 16);
  return `${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}`;
}

export function TodayDayColorGuideSection({ guide }: Props) {
  const rgb = hexToRgbTriplet(guide.hex);
  return (
    <section
      className={styles.colorGuideSection}
      data-testid="today-zone-color-guide"
      style={{ borderColor: `rgba(${rgb}, 0.35)` }}
    >
      <span className={styles.sectionEyebrow}>Цвет дня</span>
      <h2 className={styles.colorGuideTitleRow}>
        <span
          className={styles.colorGuideSwatch}
          style={{ background: guide.hex, boxShadow: `0 0 0 4px rgba(${rgb}, 0.14)` }}
          aria-hidden
        />
        <span className={styles.sectionTitle}>{guide.name}</span>
      </h2>
      <p className={styles.colorGuideBenefit}>{guide.benefit}</p>
      <dl className={styles.colorGuideList}>
        <div className={styles.colorGuideRow}>
          <dt>В одежде</dt>
          <dd>{guide.clothing}</dd>
        </div>
        <div className={styles.colorGuideRow}>
          <dt>Аксессуар</dt>
          <dd>{guide.accessory}</dd>
        </div>
        <div className={styles.colorGuideRow}>
          <dt>Сколько</dt>
          <dd>{guide.amount}</dd>
        </div>
        <div className={`${styles.colorGuideRow} ${styles.colorGuideAvoid}`}>
          <dt>Лучше избегать</dt>
          <dd>
            <strong>{guide.avoidColor}</strong> — {guide.avoidWhy}
          </dd>
        </div>
      </dl>
    </section>
  );
}
