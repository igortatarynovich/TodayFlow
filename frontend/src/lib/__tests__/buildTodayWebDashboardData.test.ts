import {
  buildTodayWebTimeline,
  buildTodayWebWeeklyActivity,
} from "@/lib/buildTodayWebDashboardData";

describe("buildTodayWebDashboardData PR-2 honesty", () => {
  it("returns empty timeline when morning has no celestial events", () => {
    expect(buildTodayWebTimeline(null)).toEqual([]);
    expect(buildTodayWebTimeline({} as never)).toEqual([]);
  });

  it("does not invent weekly wave bars without step history", () => {
    expect(buildTodayWebWeeklyActivity({ dailySteps: [] })).toBeNull();
  });

  it("maps real daily steps to binary week activity", () => {
    const steps = Array.from({ length: 7 }, (_, i) => ({ done: i % 2 === 0 }));
    expect(buildTodayWebWeeklyActivity({ dailySteps: steps })).toEqual([1, 0, 1, 0, 1, 0, 1]);
  });
});
