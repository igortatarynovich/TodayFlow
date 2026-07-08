import { loadDayContinuity, type DayFocusOutcome } from "@/lib/todayDayContinuity";
import {
  eveningHighlightLabel,
  scanMoodMapDayRecords,
  type MoodMapDayRecord,
} from "@/lib/todayDayEngagement";

export type MoodMapLocale = "ru" | "en";

export const MOOD_CELL_COLORS: Record<string, string> = {
  calm: "rgba(107, 143, 90, 0.88)",
  driven: "rgba(155, 118, 70, 0.92)",
  inspired: "rgba(201, 168, 115, 0.9)",
  tired: "rgba(154, 132, 104, 0.72)",
  anxious: "rgba(180, 120, 100, 0.78)",
  overloaded: "rgba(140, 90, 80, 0.85)",
};

export const MOOD_CELL_EMPTY = "rgba(180, 170, 158, 0.35)";

export type MoodMapDayCell = {
  dateISO: string;
  record: MoodMapDayRecord | null;
  color: string;
  isFuture: boolean;
};

export type MoodMapObservation = {
  text: string;
};

export function shiftDateISO(isoDate: string, deltaDays: number): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(year, (month || 1) - 1, day || 1);
  date.setDate(date.getDate() + deltaDays);
  return date.toISOString().split("T")[0];
}

export function buildMoodMapWindow(todayISO: string, windowDays = 35): string[] {
  const days: string[] = [];
  for (let index = windowDays - 1; index >= 0; index -= 1) {
    days.push(shiftDateISO(todayISO, -index));
  }
  return days;
}

export function buildMoodMapCells(todayISO: string, windowDays = 35): MoodMapDayCell[] {
  const byDate = new Map(scanMoodMapDayRecords().map((record) => [record.dateISO, record]));
  return buildMoodMapWindow(todayISO, windowDays).map((dateISO) => {
    const record = byDate.get(dateISO) ?? null;
    const isFuture = dateISO > todayISO;
    return {
      dateISO,
      record,
      color: record ? (MOOD_CELL_COLORS[record.moodId] ?? "rgba(191, 151, 95, 0.62)") : MOOD_CELL_EMPTY,
      isFuture,
    };
  });
}

const OUTCOME_COPY_RU: Record<DayFocusOutcome, string> = {
  done: "Вечером день закрыт — главное сделано.",
  partial: "Вечером день закрыт частично.",
  not_done: "Вечером обещание дня не удалось выполнить.",
};

const OUTCOME_COPY_EN: Record<DayFocusOutcome, string> = {
  done: "You closed the day—main focus done.",
  partial: "You closed the day partly.",
  not_done: "The promise of the day didn’t land by evening.",
};

export function formatMoodMapDate(dateISO: string, locale: MoodMapLocale): string {
  const d = new Date(`${dateISO}T12:00:00`);
  if (Number.isNaN(d.getTime())) return dateISO;
  return d.toLocaleDateString(locale === "ru" ? "ru-RU" : "en-US", {
    day: "numeric",
    month: "long",
  });
}

export function buildMoodDayStory(record: MoodMapDayRecord, locale: MoodMapLocale): string {
  const continuity = loadDayContinuity(record.dateISO);
  const parts: string[] = [];

  if (locale === "ru") {
    parts.push(`${formatMoodMapDate(record.dateISO, locale)} — ${record.moodLabel}.`);
    if (record.focusLabel) parts.push(`Фокус был на «${record.focusLabel}».`);
    if (record.dayGoal) parts.push(`Обещание дня: «${record.dayGoal}».`);
    const evening = eveningHighlightLabel(record.eveningHighlightId);
    if (evening) parts.push(`Вечером главным оказалось: ${evening.toLowerCase()}.`);
    if (continuity?.outcome) parts.push(OUTCOME_COPY_RU[continuity.outcome]);
    return parts.join(" ");
  }

  parts.push(`${formatMoodMapDate(record.dateISO, locale)} — ${record.moodLabel}.`);
  if (record.focusLabel) parts.push(`Focus was on ${record.focusLabel.toLowerCase()}.`);
  if (record.dayGoal) parts.push(`Promise of the day: “${record.dayGoal}”.`);
  const evening = eveningHighlightLabel(record.eveningHighlightId);
  if (evening) parts.push(`By evening, ${evening.toLowerCase()} stood out.`);
  if (continuity?.outcome) parts.push(OUTCOME_COPY_EN[continuity.outcome]);
  return parts.join(" ");
}

export function buildMoodMapObservation(records: MoodMapDayRecord[], locale: MoodMapLocale): MoodMapObservation | null {
  if (records.length < 3) return null;

  const counts = new Map<string, number>();
  for (const record of records) {
    counts.set(record.moodId, (counts.get(record.moodId) ?? 0) + 1);
  }
  const top = Array.from(counts.entries()).sort((a, b) => b[1] - a[1])[0];
  if (!top) return null;

  const [moodId, count] = top;
  const label = records.find((r) => r.moodId === moodId)?.moodLabel ?? moodId;
  const lowEnergy = new Set(["tired", "anxious", "overloaded"]).has(moodId);

  if (locale === "ru") {
    if (lowEnergy) {
      return {
        text: `За последние отметки чаще всего было «${label}» (${count} ${count === 1 ? "день" : count < 5 ? "дня" : "дней"}). Может, телу нужен более мягкий ритм.`,
      };
    }
    return {
      text: `За последние отметки чаще всего было «${label}» — ${count} ${count === 1 ? "день" : count < 5 ? "дня" : "дней"}. Так складывается тон твоих дней.`,
    };
  }

  if (lowEnergy) {
    return {
      text: `Lately you’ve often marked “${label}” (${count} day${count === 1 ? "" : "s"}). Your body may be asking for a gentler rhythm.`,
    };
  }
  return {
    text: `Lately “${label}” shows up most often—${count} day${count === 1 ? "" : "s"}. That’s the tone your days are taking.`,
  };
}
