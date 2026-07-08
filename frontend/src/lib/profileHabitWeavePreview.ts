import { getJson } from "@/lib/api";
import {
  buildHabitDayStory,
  buildHabitMapRows,
  countHabitMapMarks,
  type HabitMapEntry,
  type HabitMapHabit,
  type HabitMapOverviewItem,
} from "@/lib/habitMapModel";
import { PROFILE_MAPS_HEATMAP_WINDOW_DAYS, type ProfileMapHeatmapCell } from "@/lib/profileMapsHeatmapPreview";
import { shiftDateISO, type MoodMapLocale } from "@/lib/moodMapModel";

export const PROFILE_HABIT_WEAVE_MAX_HABITS = 3;

export type ProfileHabitWeaveRow = {
  habitId: number;
  name: string;
  href: string;
  currentStreakDays: number;
  cells: ProfileMapHeatmapCell[];
  filledCount: number;
};

export type ProfileHabitWeavePreview = {
  rows: ProfileHabitWeaveRow[];
  habits: HabitMapHabit[];
  entriesByHabit: Record<number, HabitMapEntry[]>;
  hasAnyMarks: boolean;
};

type HabitApiRow = {
  id: number;
  name: string;
  category: string | null;
};

function toPreviewRow(
  row: ReturnType<typeof buildHabitMapRows>[number],
  windowDays: number,
): ProfileHabitWeaveRow {
  const cells = row.cells.slice(-windowDays).map((cell) => ({
    dateISO: cell.dateISO,
    color: cell.color,
    hasMark: cell.completed,
    isFuture: cell.isFuture,
    title: cell.completed ? `${cell.dateISO} — ${row.name}` : cell.dateISO,
  }));

  return {
    habitId: row.habitId,
    name: row.name,
    href: "/habits",
    currentStreakDays: row.currentStreakDays,
    cells,
    filledCount: cells.filter((cell) => cell.hasMark).length,
  };
}

export function buildProfileHabitWeavePreview(
  habits: HabitMapHabit[],
  entriesByHabit: Record<number, HabitMapEntry[]>,
  overview: HabitMapOverviewItem[],
  todayISO: string,
  windowDays = PROFILE_MAPS_HEATMAP_WINDOW_DAYS,
  maxHabits = PROFILE_HABIT_WEAVE_MAX_HABITS,
): ProfileHabitWeavePreview {
  const rows = buildHabitMapRows(habits, entriesByHabit, overview, todayISO, windowDays)
    .filter((row) => row.cells.some((cell) => cell.completed))
    .sort((a, b) => b.currentStreakDays - a.currentStreakDays || b.habitId - a.habitId)
    .slice(0, maxHabits)
    .map((row) => toPreviewRow(row, windowDays));

  return {
    rows,
    habits,
    entriesByHabit,
    hasAnyMarks: countHabitMapMarks(entriesByHabit) > 0,
  };
}

export function buildProfileHabitDrillStory(
  preview: ProfileHabitWeavePreview,
  habitId: number,
  dateISO: string,
  locale: MoodMapLocale = "ru",
): string | null {
  const habit = preview.habits.find((row) => row.id === habitId);
  if (!habit) return null;
  const entry =
    preview.entriesByHabit[habitId]?.find((row) => row.date === dateISO && row.completed) ?? null;
  if (!entry) return null;
  return buildHabitDayStory(habit, dateISO, entry, locale, preview.habits, preview.entriesByHabit);
}

export async function fetchProfileHabitWeavePreview(
  todayISO: string,
  windowDays = PROFILE_MAPS_HEATMAP_WINDOW_DAYS,
): Promise<ProfileHabitWeavePreview | null> {
  try {
    const [habitsData, overviewData] = await Promise.all([
      getJson<HabitApiRow[]>("/habits"),
      getJson<HabitMapOverviewItem[]>("/habits/overview/summary"),
    ]);

    if (!habitsData.length) {
      return { rows: [], habits: [], entriesByHabit: {}, hasAnyMarks: false };
    }

    const fromDate = shiftDateISO(todayISO, -(windowDays - 1));
    const entriesLists = await Promise.all(
      habitsData.map((habit) =>
        getJson<HabitMapEntry[]>(`/habits/${habit.id}/entries?from_date=${fromDate}&to_date=${todayISO}`).catch(
          () => [],
        ),
      ),
    );

    const entriesByHabit: Record<number, HabitMapEntry[]> = {};
    habitsData.forEach((habit, index) => {
      entriesByHabit[habit.id] = entriesLists[index] ?? [];
    });

    const habits: HabitMapHabit[] = habitsData.map((habit) => ({
      id: habit.id,
      name: habit.name,
      category: habit.category,
    }));

    return buildProfileHabitWeavePreview(habits, entriesByHabit, overviewData, todayISO, windowDays);
  } catch {
    return null;
  }
}
