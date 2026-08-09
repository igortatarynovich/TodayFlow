"use client";

import {
  formatTodayProgressStreakLabel,
  type TodayProgressRow,
} from "@/lib/todayGrowthTrackers";
import { DsHabitStreakRow, DsSectionTitle } from "@/design-system";
import { TodayScreenBlock } from "@/components/today/composition/TodayScreenBlock";
import styles from "@/components/today/composition/TodayProgressTracker.module.css";

type Props = {
  rows: TodayProgressRow[];
  title?: string;
};

export function TodayProgressTracker({ rows, title = "Твой прогресс" }: Props) {
  if (!rows.length) return null;

  return (
    <TodayScreenBlock testId="today-zone-progress">
      <DsSectionTitle as="p" className={styles.title}>
        {title}
      </DsSectionTitle>
      <ul className={styles.list}>
        {rows.map((row, index) => (
          <li key={row.id} className={styles.rowItem}>
            <DsHabitStreakRow
              name={row.name}
              kind={row.kindLabel}
              streakLabel={formatTodayProgressStreakLabel(row.streakDays)}
              days={row.days.map((d) => d.completed)}
              testId={`today-progress-row-${row.kind}`}
            />
            {index < rows.length - 1 ? <div className={styles.divider} /> : null}
          </li>
        ))}
      </ul>
    </TodayScreenBlock>
  );
}
