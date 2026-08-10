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

/** Thin handoff recap — one glass with priority / promise / practice rows. */
export function TodayRecapAchievements({ items }: Props) {
  return (
    <div className={styles.root} data-testid="today-handoff-recap">
      <DsGlassCard className={styles.sheet} testId="today-recap-sheet">
        <ul className={styles.list}>
          {items.map((item) => (
            <li
              key={item.id}
              className={item.done ? styles.rowDone : styles.row}
              data-testid={`today-recap-${item.id}`}
            >
              <DsEyebrow>{item.label}</DsEyebrow>
              <p className={styles.value}>{item.value}</p>
            </li>
          ))}
        </ul>
      </DsGlassCard>
    </div>
  );
}
