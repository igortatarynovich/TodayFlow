import type { CalendarDayLite } from "./trackingRhythm";

/** Последние N дней по ISO (включая сегодня), по возрастанию даты. */
export function sliceLastNDaysSorted(allDays: CalendarDayLite[], n: number, todayIso: string): CalendarDayLite[] {
  const sorted = [...allDays].sort((a, b) => a.date.localeCompare(b.date));
  const end = new Date(todayIso + "T12:00:00");
  const out: CalendarDayLite[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(end);
    d.setDate(end.getDate() - i);
    const iso = d.toISOString().split("T")[0];
    const hit = sorted.find((x) => x.date === iso);
    out.push(
      hit ?? {
        date: iso,
        activities: {},
      },
    );
  }
  return out;
}
