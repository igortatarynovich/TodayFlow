"use client";

import { DsGlassCard, DsEyebrow } from "@/design-system";
import styles from "@/components/today/composition/TodayRecapAchievements.module.css";

export type TodayRecapItem = {
  id: string;
  label: string;
  value: string;
  done: boolean;
};

type Props = {
  items: TodayRecapItem[];
};

/** Recap as achievement tiles — not a plain text list. */
export function TodayRecapAchievements({ items }: Props) {
  return (
    <div className={styles.root} data-testid="today-handoff-recap">
      <div className={styles.grid}>
        {items.map((item) => (
          <DsGlassCard
            key={item.id}
            className={item.done ? styles.cardDone : styles.card}
            testId={`today-recap-${item.id}`}
          >
            <DsEyebrow>{item.label}</DsEyebrow>
            <p className={styles.value}>{item.value}</p>
            <p className={styles.status} aria-hidden>
              {item.done ? "✓" : "·"}
            </p>
          </DsGlassCard>
        ))}
      </div>
    </div>
  );
}
