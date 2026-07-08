import { saveDayContinuity } from "@/lib/todayDayContinuity";
import { saveDayEngagement } from "@/lib/todayDayEngagement";
import {
  buildHabitDayStory,
  buildHabitMapObservation,
  buildHabitMapRow,
  countHabitMapMarks,
  habitCellColor,
  habitWeaveColor,
  type HabitMapEntry,
  type HabitMapHabit,
} from "@/lib/habitMapModel";

const habits: HabitMapHabit[] = [
  { id: 1, name: "Дыхание", category: "body" },
  { id: 2, name: "Фокус", category: "focus" },
];

const entriesByHabit: Record<number, HabitMapEntry[]> = {
  1: [
    { habit_id: 1, date: "2026-06-20", completed: true },
    { habit_id: 1, date: "2026-06-21", completed: true },
    { habit_id: 1, date: "2026-06-22", completed: true },
  ],
  2: [{ habit_id: 2, date: "2026-06-22", completed: true }],
};

describe("habitMapModel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("builds 35-day row with category weave colors", () => {
    const row = buildHabitMapRow(habits[0], entriesByHabit[1], null, "2026-06-22");
    expect(row.cells).toHaveLength(35);
    const marked = row.cells.filter((cell) => cell.completed);
    expect(marked.length).toBeGreaterThanOrEqual(2);
    expect(marked[0].color).toMatch(/214, 179, 122/);
    expect(habitWeaveColor(1, "body")).toMatch(/214, 179, 122/);
    expect(habitCellColor(1, "body", false, false)).toBe("#f8f5ef");
  });

  it("counts marks and builds day story with continuity", () => {
    saveDayEngagement("2026-06-22", {
      morningMoodId: "calm",
      morningMoodCapturedAtMs: Date.now(),
    });
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Отдых",
      outcome: "done",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    expect(countHabitMapMarks(entriesByHabit)).toBe(4);

    const story = buildHabitDayStory(
      habits[0],
      "2026-06-22",
      entriesByHabit[1][2],
      "ru",
      habits,
      entriesByHabit,
    );
    expect(story).toMatch(/Дыхание/);
    expect(story).toMatch(/отмечена/);
    expect(story).toMatch(/«Фокус»/);
    expect(story).toMatch(/закрыли спокойно/i);
  });

  it("returns observation after enough marks", () => {
    const observation = buildHabitMapObservation(
      habits,
      entriesByHabit,
      [
        { habit_id: 1, name: "Дыхание", category: "body", current_streak_days: 8 },
        { habit_id: 2, name: "Фокус", category: "focus", current_streak_days: 1 },
      ],
      "ru",
    );
    expect(observation?.text).toMatch(/Дыхание/);
    expect(observation?.text).toMatch(/8 дней/);
  });
});
