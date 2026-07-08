/** Полоса отметок по линиям дня (данные с `/tracking/calendar`). */

export type LineId = "goal" | "habits" | "asceticism" | "practice";

export type CalendarDayLite = {
  date: string;
  activities: {
    practice?: { completed?: boolean; count?: number };
    goal?: { completed?: boolean };
    habits?: { completed?: boolean; count?: number };
    asceticism?: { completed?: boolean };
  };
};

export type Mark = "done" | "miss" | "warn";

export function lineDone(day: CalendarDayLite, lineId: LineId): boolean {
  switch (lineId) {
    case "practice":
      return Boolean(day.activities.practice?.completed);
    case "goal":
      return Boolean(day.activities.goal?.completed);
    case "asceticism":
      return Boolean(day.activities.asceticism?.completed);
    case "habits": {
      const h = day.activities.habits;
      return Boolean(h?.completed || (h?.count ?? 0) > 0);
    }
    default:
      return false;
  }
}

export function computeMarks(days: CalendarDayLite[], lineId: LineId): Mark[] {
  const marks: Mark[] = [];
  let streak = 0;
  for (const day of days) {
    const done = lineDone(day, lineId);
    if (done) {
      marks.push("done");
      streak++;
    } else {
      marks.push(streak >= 2 ? "warn" : "miss");
      streak = 0;
    }
  }
  return marks;
}
