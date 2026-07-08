import { getJson } from "@/lib/api";
import { buildMoodMapWindow, type MoodMapLocale } from "@/lib/moodMapModel";
import { scanMoodMapDayRecords } from "@/lib/todayDayEngagement";

export type CycleMapEntryIn = {
  date: string;
  cycle_day?: number | null;
  period_intensity?: string | null;
  ovulation?: boolean;
  fertile_window?: boolean;
};

const ACTIVE_MOODS = new Set(["driven", "inspired", "motivated"]);
const QUIET_MOODS = new Set(["tired", "calm", "heavy", "overloaded", "anxious"]);

function daysBetweenISO(isoA: string, isoB: string): number {
  const a = new Date(`${isoA}T00:00:00Z`).getTime();
  const b = new Date(`${isoB}T00:00:00Z`).getTime();
  return Math.round((b - a) / 86_400_000);
}

export function hasPeriodIntensity(intensity: string | null | undefined): boolean {
  const key = (intensity || "").toLowerCase();
  return key === "light" || key === "medium" || key === "heavy";
}

/** Count menstrual cycle starts from period-onset markers (not cycle_day). */
export function countMenstrualCycleStarts(entries: CycleMapEntryIn[]): number {
  const sorted = [...entries].sort((a, b) => a.date.localeCompare(b.date));
  let starts = 0;
  let inPeriod = false;
  let lastDate: string | null = null;
  for (const entry of sorted) {
    if (lastDate && daysBetweenISO(lastDate, entry.date) > 1) {
      inPeriod = false;
    }
    const onPeriod = hasPeriodIntensity(entry.period_intensity);
    if (onPeriod && !inPeriod) starts += 1;
    inPeriod = onPeriod;
    lastDate = entry.date;
  }
  return starts;
}

export function buildCycleMapObservation(entries: CycleMapEntryIn[], locale: MoodMapLocale = "ru"): string | null {
  const cycleStarts = countMenstrualCycleStarts(entries);
  if (cycleStarts < 4 && entries.length < 28) return null;

  const moodByDate = new Map(scanMoodMapDayRecords().map((record) => [record.dateISO, record]));

  let fertileMarks = 0;
  let fertileActive = 0;
  let periodMarks = 0;
  let periodQuiet = 0;

  for (const entry of entries) {
    const mood = moodByDate.get(entry.date);
    if (!mood) continue;
    if (entry.fertile_window) {
      fertileMarks += 1;
      if (ACTIVE_MOODS.has(mood.moodId)) fertileActive += 1;
    }
    if (hasPeriodIntensity(entry.period_intensity)) {
      periodMarks += 1;
      if (QUIET_MOODS.has(mood.moodId)) periodQuiet += 1;
    }
  }

  if (locale === "ru") {
    if (fertileMarks >= 4 && fertileActive >= 2) {
      return "В фертильные фазы на карте настроения чаще подвижные отметки — узор из нескольких циклов.";
    }
    if (periodMarks >= 4 && periodQuiet >= 3) {
      return "В дни с отметкой интенсивности цикла карта настроения чаще спокойнее — это уже повторяется.";
    }
    if (cycleStarts >= 4) {
      return "Несколько циклов на карте — ритм месяца начинает влиять на узор дней. Контекст, не цифра дня.";
    }
    return null;
  }

  if (fertileMarks >= 4 && fertileActive >= 2) {
    return "During fertile phases your mood map shows more active marks—a pattern across several cycles.";
  }
  if (periodMarks >= 4 && periodQuiet >= 3) {
    return "On high-intensity cycle days your mood map is often quieter—that pattern is repeating.";
  }
  if (cycleStarts >= 4) {
    return "Several cycles on the map—monthly rhythm is shaping the pattern. Context, not a day number.";
  }
  return null;
}

export async function fetchCycleMapEntries(todayISO: string, windowDays = 120): Promise<CycleMapEntryIn[]> {
  const window = buildMoodMapWindow(todayISO, windowDays);
  const fromIso = window[0] ?? todayISO;
  try {
    return await getJson<CycleMapEntryIn[]>(`/calendar/cycle?from_date=${fromIso}&to_date=${todayISO}`);
  } catch {
    return [];
  }
}

export async function fetchCycleMapObservation(todayISO: string, locale: MoodMapLocale = "ru"): Promise<string | null> {
  const entries = await fetchCycleMapEntries(todayISO);
  return buildCycleMapObservation(entries, locale);
}
