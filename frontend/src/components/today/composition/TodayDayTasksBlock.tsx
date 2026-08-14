"use client";

import type { ReactNode } from "react";
import { DsCaption, DsContentCard, DsEyebrow } from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import type { TodayDayTask } from "@/lib/todayDayTasks";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type Props = {
  todayTasks: TodayDayTask[];
  progressRows?: TodayProgressRow[];
  practiceSlot?: ReactNode;
  affirmationSlot?: ReactNode;
};

/**
 * Block 5 — today assignments + daily trackers (Form Kit).
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
      <p data-testid="today-day-tasks-empty">
        <DsCaption>{copy.tasksEmpty}</DsCaption>
      </p>
    );
  }

  return (
    <div className={layout.stack} data-testid="today-day-tasks">
      {hasToday ? (
        <section className={layout.stack} data-testid="today-day-tasks-today">
          <DsEyebrow>{copy.tasksTodayLabel}</DsEyebrow>
          <div className={layout.stack}>
            {todayTasks.map((task) => {
              if (task.kind === "practice" && practiceSlot) {
                return (
                  <div key={task.id} data-testid={`today-task-${task.kind}`}>
                    {practiceSlot}
                  </div>
                );
              }
              if (task.kind === "affirmation" && affirmationSlot) {
                return (
                  <div key={task.id} data-testid={`today-task-${task.kind}`}>
                    {affirmationSlot}
                  </div>
                );
              }
              return (
                <DsContentCard
                  key={task.id}
                  tone="solid"
                  testId={`today-task-${task.kind}`}
                  eyebrow={task.kindLabel}
                  title={task.title}
                  body={task.detail || undefined}
                />
              );
            })}
          </div>
        </section>
      ) : null}

      {hasDaily ? (
        <section className={layout.stack} data-testid="today-day-tasks-daily">
          <TodayProgressTracker rows={progressRows} title={copy.tasksDailyLabel} />
        </section>
      ) : null}
    </div>
  );
}
