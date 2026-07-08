import { buildPracticesV2LiveContext } from "@/lib/practicesPage/buildPracticesV2LiveContext";

describe("buildPracticesV2LiveContext", () => {
  it("uses backend progress streak and history for weekly cells", () => {
    const ctx = buildPracticesV2LiveContext({
      progress: {
        total_completed: 12,
        personalized_completed: 4,
        general_completed: 8,
        by_category: [],
        current_streak_days: 8,
        longest_streak_days: 14,
        weeks_active: 3,
      },
      history: [
          {
            id: 1,
            practice_id: "breath-478",
            completed_at: "2026-07-06T10:00:00",
            is_personalized: false,
          },
        ],
      todayISO: "2026-07-06",
    });

    expect(ctx.streakDays).toBe(8);
    expect(ctx.streakFromBackend).toBe(true);
    expect(ctx.weekCells).toHaveLength(7);
    expect(ctx.weekCells.some((cell) => cell.closed)).toBe(true);
  });

  it("returns zero streak for guests without progress", () => {
    const ctx = buildPracticesV2LiveContext({ todayISO: "2026-07-06" });
    expect(ctx.streakDays).toBe(0);
    expect(ctx.streakFromBackend).toBe(false);
  });
});
