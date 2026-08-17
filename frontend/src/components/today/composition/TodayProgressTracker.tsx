"use client";

import {
  formatTodayProgressStreakLabel,
  type TodayProgressRow,
} from "@/lib/todayGrowthTrackers";
import { DsEyebrow, DsHabitStreakRow, DsListPanel, DsStarDivider } from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type Props = {
  rows: TodayProgressRow[];
  title?: string;
};

export function TodayProgressTracker({ rows, title = "Твой прогресс" }: Props) {
  if (!rows.length) return null;

  return (
    <DsListPanel tone="glass" testId="today-zone-progress">
      {title ? <DsEyebrow>{title}</DsEyebrow> : null}
      <div className={layout.stack}>
        {rows.map((row, index) => (
          <div key={row.id}>
            <DsHabitStreakRow
              name={row.name}
              kind={row.kindLabel}
              streakLabel={formatTodayProgressStreakLabel(row.streakDays)}
              days={row.days.map((d) => d.completed)}
              testId={`today-progress-row-${row.kind}`}
            />
            {index < rows.length - 1 ? <DsStarDivider /> : null}
          </div>
        ))}
      </div>
    </DsListPanel>
  );
}
