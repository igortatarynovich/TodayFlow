"use client";

import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  guide: TodayDayColorGuide;
};

export function TodayDayColorGuideSection({ guide }: Props) {
  return (
    <section className={styles.colorGuideSection} data-testid="today-zone-color-guide">
      <span className={styles.sectionEyebrow}>Цвет дня</span>
      <h2 className={styles.sectionTitle}>{guide.name}</h2>
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
