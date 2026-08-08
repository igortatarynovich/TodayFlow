"use client";

import {
  formatTodayProgressStreakLabel,
  type TodayProgressRow,
} from "@/lib/todayGrowthTrackers";
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
      <p className={styles.title}>{title}</p>
      <ul className={styles.list}>
        {rows.map((row, index) => (
          <li
            key={row.id}
            className={styles.row}
            data-testid={`today-progress-row-${row.kind}`}
            data-kind={row.kind}
          >
            <div className={styles.rowHead}>
              <p className={styles.name}>{row.name}</p>
              <p className={styles.streak}>{formatTodayProgressStreakLabel(row.streakDays)}</p>
            </div>
            <p className={styles.kind}>{row.kindLabel}</p>
            <div className={styles.dots} aria-hidden>
              {row.days.map((day) => (
                <span
                  key={day.dateISO}
                  className={styles.dot}
                  data-done={day.completed ? "true" : "false"}
                  data-future={day.isFuture ? "true" : "false"}
                />
              ))}
            </div>
            {index < rows.length - 1 ? <div className={styles.divider} /> : null}
          </li>
        ))}
      </ul>
    </TodayScreenBlock>
  );
}
