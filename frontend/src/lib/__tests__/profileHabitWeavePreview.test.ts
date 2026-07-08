import {
  buildProfileHabitDrillStory,
  buildProfileHabitWeavePreview,
  PROFILE_HABIT_WEAVE_MAX_HABITS,
} from "@/lib/profileHabitWeavePreview";
import type { HabitMapEntry, HabitMapHabit, HabitMapOverviewItem } from "@/lib/habitMapModel";

const habits: HabitMapHabit[] = [
  { id: 1, name: "Утренняя прогулка", category: "body" },
  { id: 2, name: "2 мин дыхания", category: "mind" },
];

const entriesByHabit: Record<number, HabitMapEntry[]> = {
  1: [
    { habit_id: 1, date: "2026-07-01", completed: true },
    { habit_id: 1, date: "2026-07-02", completed: true },
  ],
  2: [{ habit_id: 2, date: "2026-07-02", completed: true }],
};

const overview: HabitMapOverviewItem[] = [
  { habit_id: 1, name: "Утренняя прогулка", category: "body", current_streak_days: 2 },
  { habit_id: 2, name: "2 мин дыхания", category: "mind", current_streak_days: 1 },
];

describe("profileHabitWeavePreview", () => {
  it("builds top habit rows with 35-day cells", () => {
    const preview = buildProfileHabitWeavePreview(habits, entriesByHabit, overview, "2026-07-03");
    expect(preview.hasAnyMarks).toBe(true);
    expect(preview.rows.length).toBeLessThanOrEqual(PROFILE_HABIT_WEAVE_MAX_HABITS);
    expect(preview.rows[0]?.cells).toHaveLength(35);
    expect(preview.rows[0]?.habitId).toBe(1);
    expect(preview.rows[0]?.filledCount).toBe(2);
  });

  it("builds drill story for completed habit day", () => {
    const preview = buildProfileHabitWeavePreview(habits, entriesByHabit, overview, "2026-07-03");
    const story = buildProfileHabitDrillStory(preview, 1, "2026-07-02");
    expect(story).toMatch(/Утренняя прогулка/);
    expect(story).toMatch(/отмечена/i);
  });
});
