import {
  buildCycleMapObservation,
  countMenstrualCycleStarts,
  hasPeriodIntensity,
  type CycleMapEntryIn,
} from "@/lib/cycleMapModel";
import { saveDayEngagement } from "@/lib/todayDayEngagement";

function cycleEntry(
  date: string,
  overrides: Partial<CycleMapEntryIn> = {},
): CycleMapEntryIn {
  return {
    date,
    period_intensity: null,
    ovulation: false,
    fertile_window: false,
    ...overrides,
  };
}

describe("cycleMapModel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("counts menstrual cycle starts from period onset", () => {
    const entries: CycleMapEntryIn[] = [
      cycleEntry("2026-01-01", { period_intensity: "heavy" }),
      cycleEntry("2026-01-02", { period_intensity: "medium" }),
      cycleEntry("2026-01-28", { period_intensity: "light" }),
      cycleEntry("2026-02-25", { period_intensity: "heavy" }),
    ];
    expect(countMenstrualCycleStarts(entries)).toBe(3);
    expect(hasPeriodIntensity("heavy")).toBe(true);
    expect(hasPeriodIntensity("none")).toBe(false);
  });

  it("returns null before 4 cycles and sparse data", () => {
    expect(buildCycleMapObservation([cycleEntry("2026-06-01", { period_intensity: "light" })])).toBeNull();
  });

  it("builds fertile-phase cross-map observation without day numbers", () => {
    const fertileDates = [
      "2026-01-14",
      "2026-01-15",
      "2026-02-11",
      "2026-02-12",
      "2026-03-10",
      "2026-03-11",
      "2026-04-07",
      "2026-04-08",
    ];
    const periodStarts = ["2026-01-01", "2026-01-29", "2026-02-26", "2026-03-26"];
    const entries = [
      ...periodStarts.map((date) => cycleEntry(date, { period_intensity: "heavy" })),
      ...fertileDates.map((date) => cycleEntry(date, { fertile_window: true })),
    ];
    for (const date of fertileDates) {
      saveDayEngagement(date, {
        morningMoodId: "driven",
        morningMoodCapturedAtMs: Date.now(),
      });
    }
    const observation = buildCycleMapObservation(entries, "ru");
    expect(observation).toMatch(/фертильн/i);
    expect(observation).not.toMatch(/день\s*\d+/i);
  });

  it("falls back to generic multi-cycle observation", () => {
    const entries: CycleMapEntryIn[] = [
      cycleEntry("2026-01-01", { period_intensity: "heavy" }),
      cycleEntry("2026-01-29", { period_intensity: "heavy" }),
      cycleEntry("2026-02-26", { period_intensity: "heavy" }),
      cycleEntry("2026-03-26", { period_intensity: "heavy" }),
    ];
    expect(buildCycleMapObservation(entries, "ru")).toMatch(/Несколько циклов/i);
  });
});
