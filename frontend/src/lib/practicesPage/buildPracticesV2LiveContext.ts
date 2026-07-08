import type { PracticeHistoryItem, PracticeProgressResponse } from "@/lib/types";
import {
  buildDayContinuityWeekCells,
  type DayContinuityWeekCell,
} from "@/lib/todayDayContinuityHeatmap";
import { historyCompletionDates } from "@/lib/practicesPage/practicesCatalogModel";

export type PracticesV2LiveContext = {
  streakDays: number;
  weeklyPercent: number;
  weekCells: DayContinuityWeekCell[];
  /** true when streak comes from GET /practices/progress */
  streakFromBackend: boolean;
};

function weekCellsFromHistory(
  history: PracticeHistoryItem[],
  todayISO?: string,
): DayContinuityWeekCell[] {
  const completed = historyCompletionDates(history);
  return buildDayContinuityWeekCells(todayISO, 7).map((cell) => ({
    ...cell,
    closed: completed.has(cell.dateISO),
  }));
}

export function buildPracticesV2LiveContext(input?: {
  progress?: PracticeProgressResponse | null;
  history?: PracticeHistoryItem[];
  todayISO?: string;
}): PracticesV2LiveContext {
  const history = input?.history ?? [];
  const weekCells = weekCellsFromHistory(history, input?.todayISO);
  const closedInWeek = weekCells.filter((cell) => cell.closed).length;
  const weeklyPercent = Math.round((closedInWeek / 7) * 100);

  if (input?.progress) {
    return {
      streakDays: input.progress.current_streak_days,
      weeklyPercent,
      weekCells,
      streakFromBackend: true,
    };
  }

  return {
    streakDays: 0,
    weeklyPercent,
    weekCells,
    streakFromBackend: false,
  };
}
