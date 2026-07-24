/** Growth A — load one active habit + one active ascetic for Today zone 4 / evening. */

import { getJson, postJson } from "@/lib/api";

export type TodayActiveHabit = { id: number; name: string };
export type TodayActiveAscetic = { id: number; title: string };

type HabitRow = { id: number; name: string; is_active: boolean };
type AsceticRow = {
  id: number;
  title: string;
  status: string;
  last_completed_date?: string | null;
};
type HabitEntryRow = { date: string; completed: boolean };

export async function loadTodayGrowthTrackers(dateISO: string): Promise<{
  habit: TodayActiveHabit | null;
  ascetic: TodayActiveAscetic | null;
  habitDoneToday: boolean;
  asceticDoneToday: boolean;
}> {
  const empty = {
    habit: null as TodayActiveHabit | null,
    ascetic: null as TodayActiveAscetic | null,
    habitDoneToday: false,
    asceticDoneToday: false,
  };
  try {
    const [habits, contracts] = await Promise.all([
      getJson<HabitRow[]>("/habits").catch(() => [] as HabitRow[]),
      getJson<AsceticRow[]>("/tracking/ascetic-contracts?status_filter=active").catch(
        () => [] as AsceticRow[],
      ),
    ]);
    const habitRow = habits.find((h) => h.is_active) ?? null;
    const asceticRow = contracts[0] ?? null;

    let habitDoneToday = false;
    if (habitRow) {
      try {
        const entries = await getJson<HabitEntryRow[]>(
          `/habits/${habitRow.id}/entries?from_date=${dateISO}&to_date=${dateISO}`,
        );
        habitDoneToday = entries.some((e) => e.date === dateISO && e.completed);
      } catch {
        habitDoneToday = false;
      }
    }

    const asceticDoneToday = Boolean(
      asceticRow?.last_completed_date && asceticRow.last_completed_date === dateISO,
    );

    return {
      habit: habitRow ? { id: habitRow.id, name: habitRow.name } : null,
      ascetic: asceticRow ? { id: asceticRow.id, title: asceticRow.title } : null,
      habitDoneToday,
      asceticDoneToday,
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
