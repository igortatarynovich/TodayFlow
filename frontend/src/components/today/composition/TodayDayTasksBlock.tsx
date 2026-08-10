"use client";

import type { ReactNode } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import type { TodayDayTask } from "@/lib/todayDayTasks";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";
import styles from "@/components/today/composition/TodayDayTasks.module.css";

type Props = {
  todayTasks: TodayDayTask[];
  /** Raw progress rows for streak UI (daily cadence). */
  progressRows?: TodayProgressRow[];
  /** Optional rich gift UI for the primary practice task */
  practiceSlot?: ReactNode;
  affirmationSlot?: ReactNode;
};

/**
 * Block 5 — 1–2 today assignments + daily trackers.
 */
export function TodayDayTasksBlock({
  todayTasks,
  progressRows = [],
  practiceSlot = null,
  affirmationSlot = null,
}: Props) {
  const hasToday = todayTasks.length > 0 || practiceSlot || affirmationSlot;
  const hasDaily = progressRows.length > 0;

  if (!hasToday && !hasDaily) {
    return (
      <p className={styles.empty} data-testid="today-day-tasks-empty">
        {copy.tasksEmpty}
      </p>
    );
  }

  return (
    <div className={styles.root} data-testid="today-day-tasks">
      {hasToday ? (
        <section className={styles.section} data-testid="today-day-tasks-today">
          <p className={styles.sectionLabel}>{copy.tasksTodayLabel}</p>
          <ul className={styles.list}>
            {todayTasks.map((task) => {
              if (task.kind === "practice" && practiceSlot) {
                return (
                  <li key={task.id} className={styles.item} data-testid={`today-task-${task.kind}`}>
                    {practiceSlot}
                  </li>
                );
              }
              if (task.kind === "affirmation" && affirmationSlot) {
                return (
                  <li key={task.id} className={styles.item} data-testid={`today-task-${task.kind}`}>
                    {affirmationSlot}
                  </li>
                );
              }
              return (
                <li key={task.id} className={styles.card} data-testid={`today-task-${task.kind}`}>
                  <p className={styles.kind}>{task.kindLabel}</p>
                  <p className={styles.title}>{task.title}</p>
                  {task.detail ? <p className={styles.detail}>{task.detail}</p> : null}
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}

      {hasDaily ? (
        <section className={styles.section} data-testid="today-day-tasks-daily">
          <TodayProgressTracker rows={progressRows} title={copy.tasksDailyLabel} />
        </section>
      ) : null}
    </div>
  );
}
