/** Growth A — active habit/ascetic for Today mark rows + progress tracker (streak + 7-day dots). */

import { getJson, postJson } from "@/lib/api";
import { buildMoodMapWindow, shiftDateISO } from "@/lib/moodMapModel";

export const TODAY_PROGRESS_WINDOW_DAYS = 7;

export type TodayActiveHabit = { id: number; name: string };
export type TodayActiveAscetic = { id: number; title: string };

export type TodayProgressKind = "habit" | "ascetic" | "practice";

export type TodayProgressDayDot = {
  dateISO: string;
  completed: boolean;
  isFuture: boolean;
};

export type TodayProgressRow = {
  id: string;
  kind: TodayProgressKind;
  kindLabel: string;
  name: string;
  streakDays: number;
  days: TodayProgressDayDot[];
};

export type TodayGrowthTrackersResult = {
  habit: TodayActiveHabit | null;
  ascetic: TodayActiveAscetic | null;
  habitDoneToday: boolean;
  asceticDoneToday: boolean;
  progressRows: TodayProgressRow[];
};

type HabitRow = { id: number; name: string; is_active: boolean };
type AsceticRow = {
  id: number;
  title: string;
  status: string;
  streak_days?: number;
  last_completed_date?: string | null;
};
type HabitEntryRow = { date: string; completed: boolean };
type HabitOverviewItem = {
  habit_id: number;
  name: string;
  current_streak_days: number;
};
type CalendarAsceticTrack = {
  asceticism_id: string;
  title?: string | null;
  entries: { date: string; completed: boolean }[];
};
type CalendarHabitTrack = {
  id: number;
  name: string;
  completed_dates: string[];
};
type CalendarPayload = {
  habit_tracks?: CalendarHabitTrack[];
  ascetic_tracks?: CalendarAsceticTrack[];
};
type PracticeProgress = { current_streak_days: number };
type PracticeHistoryItem = { completed_at: string; practice_title?: string | null };
type PracticeHistoryResponse = { history: PracticeHistoryItem[] };
type PracticeCurrent = { id: string; title: string };

const KIND_LABEL: Record<TodayProgressKind, string> = {
  habit: "Привычка",
  ascetic: "Аскеза",
  practice: "Практика",
};

export function formatTodayProgressStreakLabel(streakDays: number): string {
  const n = Math.max(0, Math.floor(streakDays));
  if (n <= 0) return "Без серии";
  return `${n} дн. подряд`;
}

export function buildTodayProgressDayDots(
  todayISO: string,
  completedDates: ReadonlySet<string> | Iterable<string>,
  windowDays = TODAY_PROGRESS_WINDOW_DAYS,
): TodayProgressDayDot[] {
  const completed =
    completedDates instanceof Set ? completedDates : new Set(Array.from(completedDates));
  return buildMoodMapWindow(todayISO, windowDays).map((dateISO) => ({
    dateISO,
    completed: completed.has(dateISO),
    isFuture: dateISO > todayISO,
  }));
}

function completedDatesFromEntries(entries: { date: string; completed: boolean }[]): Set<string> {
  const out = new Set<string>();
  for (const entry of entries) {
    if (entry.completed) out.add(entry.date);
  }
  return out;
}

function completedDatesFromPracticeHistory(history: PracticeHistoryItem[]): Set<string> {
  const out = new Set<string>();
  for (const item of history) {
    const raw = item.completed_at;
    if (!raw) continue;
    const iso = raw.slice(0, 10);
    if (/^\d{4}-\d{2}-\d{2}$/.test(iso)) out.add(iso);
  }
  return out;
}

function matchAsceticTrack(
  tracks: CalendarAsceticTrack[],
  ascetic: TodayActiveAscetic,
): CalendarAsceticTrack | null {
  const byTitle = tracks.find((t) => (t.title || "").trim() === ascetic.title.trim());
  if (byTitle) return byTitle;
  const prefix = ascetic.title.trim().slice(0, 12);
  if (prefix) {
    const fuzzy = tracks.find((t) => (t.title || "").includes(prefix));
    if (fuzzy) return fuzzy;
  }
  return tracks[0] ?? null;
}

export function buildTodayProgressRows(input: {
  todayISO: string;
  habit: TodayActiveHabit | null;
  habitStreakDays: number;
  habitCompletedDates: Iterable<string>;
  ascetic: TodayActiveAscetic | null;
  asceticStreakDays: number;
  asceticCompletedDates: Iterable<string>;
  practiceName: string | null;
  practiceStreakDays: number;
  practiceCompletedDates: Iterable<string>;
}): TodayProgressRow[] {
  const rows: TodayProgressRow[] = [];

  if (input.habit) {
    rows.push({
      id: `habit:${input.habit.id}`,
      kind: "habit",
      kindLabel: KIND_LABEL.habit,
      name: input.habit.name,
      streakDays: input.habitStreakDays,
      days: buildTodayProgressDayDots(input.todayISO, input.habitCompletedDates),
    });
  }

  if (input.ascetic) {
    rows.push({
      id: `ascetic:${input.ascetic.id}`,
      kind: "ascetic",
      kindLabel: KIND_LABEL.ascetic,
      name: input.ascetic.title,
      streakDays: input.asceticStreakDays,
      days: buildTodayProgressDayDots(input.todayISO, input.asceticCompletedDates),
    });
  }

  if (input.practiceName) {
    rows.push({
      id: "practice",
      kind: "practice",
      kindLabel: KIND_LABEL.practice,
      name: input.practiceName,
      streakDays: input.practiceStreakDays,
      days: buildTodayProgressDayDots(input.todayISO, input.practiceCompletedDates),
    });
  }

  return rows;
}

export async function loadTodayGrowthTrackers(dateISO: string): Promise<TodayGrowthTrackersResult> {
  const empty: TodayGrowthTrackersResult = {
    habit: null,
    ascetic: null,
    habitDoneToday: false,
    asceticDoneToday: false,
    progressRows: [],
  };

  try {
    const fromISO = shiftDateISO(dateISO, -(TODAY_PROGRESS_WINDOW_DAYS - 1));

    const [habits, contracts, overview, calendar, practiceProgress, practiceHistory, practiceCurrent] =
      await Promise.all([
        getJson<HabitRow[]>("/habits").catch(() => [] as HabitRow[]),
        getJson<AsceticRow[]>("/tracking/ascetic-contracts?status_filter=active").catch(
          () => [] as AsceticRow[],
        ),
        getJson<HabitOverviewItem[]>("/habits/overview/summary").catch(() => [] as HabitOverviewItem[]),
        getJson<CalendarPayload>(`/tracking/calendar?from_date=${fromISO}&to_date=${dateISO}`).catch(
          () => ({}) as CalendarPayload,
        ),
        getJson<PracticeProgress>("/practices/progress").catch(() => null),
        getJson<PracticeHistoryResponse>("/practices/history?limit=40").catch(
          () => ({ history: [] }) as PracticeHistoryResponse,
        ),
        getJson<PracticeCurrent>("/practices/current").catch(async () => {
          const list = await getJson<PracticeCurrent[]>("/practices?limit=1").catch(() => []);
          return list[0] ?? null;
        }),
      ]);

    const habitRow = habits.find((h) => h.is_active) ?? null;
    const asceticRow = contracts[0] ?? null;

    const habit: TodayActiveHabit | null = habitRow
      ? { id: habitRow.id, name: habitRow.name }
      : null;
    const ascetic: TodayActiveAscetic | null = asceticRow
      ? { id: asceticRow.id, title: asceticRow.title }
      : null;

    let habitEntries: HabitEntryRow[] = [];
    if (habit) {
      habitEntries = await getJson<HabitEntryRow[]>(
        `/habits/${habit.id}/entries?from_date=${fromISO}&to_date=${dateISO}`,
      ).catch(() => [] as HabitEntryRow[]);
    }

    const habitTrack = habit
      ? (calendar.habit_tracks ?? []).find((t) => t.id === habit.id)
      : undefined;
    const habitCompleted = habitTrack
      ? new Set(habitTrack.completed_dates)
      : completedDatesFromEntries(habitEntries);

    const habitDoneToday = habitCompleted.has(dateISO);
    const habitStreak =
      overview.find((item) => item.habit_id === habit?.id)?.current_streak_days ??
      (habitDoneToday ? 1 : 0);

    const asceticTrack = ascetic
      ? matchAsceticTrack(calendar.ascetic_tracks ?? [], ascetic)
      : null;
    let asceticCompleted = asceticTrack
      ? completedDatesFromEntries(asceticTrack.entries)
      : new Set<string>();
    if (ascetic?.id && asceticRow?.last_completed_date === dateISO) {
      asceticCompleted = new Set(asceticCompleted);
      asceticCompleted.add(dateISO);
    }
    const asceticDoneToday = Boolean(
      (asceticRow?.last_completed_date && asceticRow.last_completed_date === dateISO) ||
        asceticCompleted.has(dateISO),
    );
    const asceticStreak = Math.max(0, Number(asceticRow?.streak_days ?? 0));

    const practiceCompleted = completedDatesFromPracticeHistory(practiceHistory?.history ?? []);
    const practiceName = practiceCurrent?.title?.trim() || null;
    const practiceStreak = Math.max(0, Number(practiceProgress?.current_streak_days ?? 0));
    const includePractice =
      Boolean(practiceName) &&
      (practiceStreak > 0 || practiceCompleted.size > 0 || Boolean(practiceCurrent?.id));

    const progressRows = buildTodayProgressRows({
      todayISO: dateISO,
      habit,
      habitStreakDays: habit ? habitStreak : 0,
      habitCompletedDates: habitCompleted,
      ascetic,
      asceticStreakDays: ascetic ? asceticStreak : 0,
      asceticCompletedDates: asceticCompleted,
      practiceName: includePractice ? practiceName : null,
      practiceStreakDays: practiceStreak,
      practiceCompletedDates: practiceCompleted,
    });

    return {
      habit,
      ascetic,
      habitDoneToday,
      asceticDoneToday,
      progressRows,
    };
  } catch {
    return empty;
  }
}

export async function markHabitCompletedToday(habitId: number, dateISO: string): Promise<void> {
  await postJson(`/habits/${habitId}/entries`, {
    date: dateISO,
    completed: true,
  });
}

export async function markAsceticCompletedToday(contractId: number, dateISO: string): Promise<void> {
  await postJson(`/tracking/ascetic-contracts/${contractId}/checkin`, {
    date: dateISO,
    completed: true,
  });
}
