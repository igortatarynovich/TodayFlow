import { loadDayContinuity } from "@/lib/todayDayContinuity";
import { loadDayEngagement } from "@/lib/todayDayEngagement";
import { buildMoodMapWindow, formatMoodMapDate, type MoodMapLocale, type MoodMapObservation } from "@/lib/moodMapModel";

export const HABIT_MAP_WINDOW_DAYS = 35;

export const HABIT_CELL_EMPTY = "rgba(236, 228, 214, 0.55)";
export const HABIT_CELL_MISSED = "#f8f5ef";

const CATEGORY_COLORS: Record<string, string> = {
  body: "rgba(214, 179, 122, 0.92)",
  focus: "rgba(191, 151, 95, 0.9)",
  mind: "rgba(107, 143, 90, 0.88)",
  rhythm: "rgba(175, 138, 82, 0.88)",
};

const HABIT_ID_PALETTE = [
  "rgba(214, 179, 122, 0.92)",
  "rgba(191, 151, 95, 0.9)",
  "rgba(155, 118, 70, 0.88)",
  "rgba(107, 143, 90, 0.88)",
  "rgba(180, 140, 100, 0.9)",
];

export type HabitMapHabit = {
  id: number;
  name: string;
  category: string | null;
};

export type HabitMapEntry = {
  habit_id: number;
  date: string;
  completed: boolean;
  note?: string | null;
};

export type HabitMapOverviewItem = {
  habit_id: number;
  name: string;
  category: string | null;
  current_streak_days: number;
};

export type HabitMapDayCell = {
  dateISO: string;
  completed: boolean;
  isFuture: boolean;
  color: string;
};

export type HabitMapRow = {
  habitId: number;
  name: string;
  category: string | null;
  cells: HabitMapDayCell[];
  currentStreakDays: number;
};

export type HabitMapSelectedCell = {
  habitId: number;
  dateISO: string;
};

export function habitWeaveColor(habitId: number, category: string | null): string {
  const key = category?.trim().toLowerCase();
  if (key && CATEGORY_COLORS[key]) return CATEGORY_COLORS[key];
  return HABIT_ID_PALETTE[Math.abs(habitId) % HABIT_ID_PALETTE.length];
}

export function habitCellColor(
  habitId: number,
  category: string | null,
  completed: boolean,
  isFuture: boolean,
): string {
  if (isFuture) return HABIT_CELL_EMPTY;
  if (!completed) return HABIT_CELL_MISSED;
  return habitWeaveColor(habitId, category);
}

export function indexHabitEntriesByDate(entries: HabitMapEntry[]): Map<string, HabitMapEntry> {
  const byDate = new Map<string, HabitMapEntry>();
  for (const entry of entries) {
    if (entry.completed) byDate.set(entry.date, entry);
  }
  return byDate;
}

export function buildHabitMapRow(
  habit: HabitMapHabit,
  entries: HabitMapEntry[],
  overview: HabitMapOverviewItem | null,
  todayISO: string,
  windowDays = HABIT_MAP_WINDOW_DAYS,
): HabitMapRow {
  const byDate = indexHabitEntriesByDate(entries);
  const cells = buildMoodMapWindow(todayISO, windowDays).map((dateISO) => {
    const completed = byDate.has(dateISO);
    const isFuture = dateISO > todayISO;
    return {
      dateISO,
      completed,
      isFuture,
      color: habitCellColor(habit.id, habit.category, completed, isFuture),
    };
  });

  return {
    habitId: habit.id,
    name: habit.name,
    category: habit.category,
    cells,
    currentStreakDays: overview?.current_streak_days ?? 0,
  };
}

export function buildHabitMapRows(
  habits: HabitMapHabit[],
  entriesByHabit: Record<number, HabitMapEntry[]>,
  overview: HabitMapOverviewItem[],
  todayISO: string,
  windowDays = HABIT_MAP_WINDOW_DAYS,
): HabitMapRow[] {
  return habits.map((habit) =>
    buildHabitMapRow(
      habit,
      entriesByHabit[habit.id] ?? [],
      overview.find((item) => item.habit_id === habit.id) ?? null,
      todayISO,
      windowDays,
    ),
  );
}

export function countHabitMapMarks(entriesByHabit: Record<number, HabitMapEntry[]>): number {
  let total = 0;
  for (const entries of Object.values(entriesByHabit)) {
    total += entries.filter((entry) => entry.completed).length;
  }
  return total;
}

export function habitsCompletedOnDate(
  habits: HabitMapHabit[],
  entriesByHabit: Record<number, HabitMapEntry[]>,
  dateISO: string,
): HabitMapHabit[] {
  return habits.filter((habit) =>
    entriesByHabit[habit.id]?.some((entry) => entry.date === dateISO && entry.completed),
  );
}

export function buildHabitDayStory(
  habit: HabitMapHabit,
  dateISO: string,
  entry: HabitMapEntry | null,
  locale: MoodMapLocale,
  allHabits: HabitMapHabit[],
  entriesByHabit: Record<number, HabitMapEntry[]>,
): string {
  const engagement = loadDayEngagement(dateISO);
  const continuity = loadDayContinuity(dateISO);
  const completed = entry?.completed ?? false;
  const othersDone = habitsCompletedOnDate(allHabits, entriesByHabit, dateISO).filter((h) => h.id !== habit.id);
  const parts: string[] = [];

  if (locale === "ru") {
    parts.push(`${formatMoodMapDate(dateISO, locale)} — «${habit.name}».`);
    if (completed) {
      parts.push("Привычка отмечена — ещё один штрих на карте.");
      if (entry?.note?.trim()) parts.push(`Заметка: «${entry.note.trim()}».`);
    } else {
      parts.push("В этот день отметки не было — пауза тоже часть ритма.");
    }
    if (othersDone.length > 0) {
      const names = othersDone.map((h) => `«${h.name}»`).join(", ");
      parts.push(`В тот же день на карте: ${names}.`);
    }
    if (engagement.morningMoodId) {
      parts.push("Утро в Today было отмечено — день начался осознанно.");
    }
    if (continuity?.outcome === "done") {
      parts.push("Вечером день закрыли спокойно — ритм привычек часто держится после этого.");
    } else if (continuity?.outcome === "not_done") {
      parts.push("К вечеру обещание дня осталось открытым — на привычки могло не хватить сил.");
    }
    return parts.join(" ");
  }

  parts.push(`${formatMoodMapDate(dateISO, locale)} — “${habit.name}”.`);
  if (completed) {
    parts.push("Habit logged—another stroke on your map.");
    if (entry?.note?.trim()) parts.push(`Note: “${entry.note.trim()}”.`);
  } else {
    parts.push("No mark this day—a pause is part of the rhythm too.");
  }
  if (othersDone.length > 0) {
    const names = othersDone.map((h) => `“${h.name}”`).join(", ");
    parts.push(`Same day on the map: ${names}.`);
  }
  if (engagement.morningMoodId) {
    parts.push("Morning was marked in Today—the day started with intention.");
  }
  if (continuity?.outcome === "done") {
    parts.push("You closed the evening well—habit rhythm often steadies after that.");
  } else if (continuity?.outcome === "not_done") {
    parts.push("The day’s promise stayed open—habits may have had less room.");
  }
  return parts.join(" ");
}

export function buildHabitMapObservation(
  habits: HabitMapHabit[],
  entriesByHabit: Record<number, HabitMapEntry[]>,
  overview: HabitMapOverviewItem[],
  locale: MoodMapLocale,
): MoodMapObservation | null {
  const totalMarks = countHabitMapMarks(entriesByHabit);
  if (totalMarks < 3) return null;

  const strongest = [...overview].sort((a, b) => b.current_streak_days - a.current_streak_days)[0];
  const multiHabitDays = buildMoodMapWindow(new Date().toISOString().split("T")[0], HABIT_MAP_WINDOW_DAYS).filter(
    (dateISO) => habitsCompletedOnDate(habits, entriesByHabit, dateISO).length >= 2,
  ).length;

  if (locale === "ru") {
    if (strongest && strongest.current_streak_days >= 7) {
      return {
        text: `«${strongest.name}» держит самый длинный ритм — ${strongest.current_streak_days} дней подряд на карте.`,
      };
    }
    if (multiHabitDays >= 2) {
      return { text: "Есть дни, когда несколько привычек отмечены вместе — узор складывается." };
    }
    return { text: "Отметки постепенно рисуют личный ритм — продолжай жить Today." };
  }

  if (strongest && strongest.current_streak_days >= 7) {
    return {
      text: `“${strongest.name}” holds the longest rhythm—${strongest.current_streak_days} days in a row on the map.`,
    };
  }
  if (multiHabitDays >= 2) {
    return { text: "Some days carry several habits together—the weave is forming." };
  }
  return { text: "Your marks are drawing a personal rhythm—keep living Today." };
}
