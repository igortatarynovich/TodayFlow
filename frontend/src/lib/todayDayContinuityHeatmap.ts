import {
  isDayContinuityClosed,
  loadDayContinuity,
  type DayFocusOutcome,
} from "@/lib/todayDayContinuity";

export type DayContinuityWeekCell = {
  dateISO: string;
  weekdayLabel: string;
  closed: boolean;
  outcome?: DayFocusOutcome;
};

const WEEKDAY_SHORT_RU = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"] as const;

function formatWeekdayShortRu(date: Date): string {
  const idx = date.getDay();
  return WEEKDAY_SHORT_RU[idx] ?? "—";
}

/** Last N calendar days (oldest → newest) from local day-continuity storage — same source as Today. */
export function buildDayContinuityWeekCells(todayISO?: string, days = 7): DayContinuityWeekCell[] {
  const anchor = todayISO ?? new Date().toISOString().slice(0, 10);
  const end = new Date(`${anchor}T12:00:00`);
  if (Number.isNaN(end.getTime())) return [];

  const start = new Date(end);
  start.setDate(start.getDate() - Math.max(0, days - 1));

  const cells: DayContinuityWeekCell[] = [];
  for (let i = 0; i < days; i += 1) {
    const cur = new Date(start);
    cur.setDate(start.getDate() + i);
    const dateISO = cur.toISOString().slice(0, 10);
    const record = loadDayContinuity(dateISO);
    const closed = isDayContinuityClosed(record);
    cells.push({
      dateISO,
      weekdayLabel: formatWeekdayShortRu(cur),
      closed,
      outcome: record?.outcome,
    });
  }
  return cells;
}
