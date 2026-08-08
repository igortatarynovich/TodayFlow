import {
  buildTodayProgressDayDots,
  buildTodayProgressRows,
  formatTodayProgressStreakLabel,
} from "@/lib/todayGrowthTrackers";

describe("todayGrowthTrackers progress model", () => {
  it("formats streak labels like the handoff", () => {
    expect(formatTodayProgressStreakLabel(0)).toBe("Без серии");
    expect(formatTodayProgressStreakLabel(5)).toBe("5 дн. подряд");
  });

  it("builds 7 day dots oldest → newest", () => {
    const dots = buildTodayProgressDayDots("2026-08-08", new Set(["2026-08-06", "2026-08-08"]));
    expect(dots).toHaveLength(7);
    expect(dots[0].dateISO).toBe("2026-08-02");
    expect(dots[dots.length - 1].dateISO).toBe("2026-08-08");
    expect(dots.find((d) => d.dateISO === "2026-08-06")?.completed).toBe(true);
    expect(dots.find((d) => d.dateISO === "2026-08-07")?.completed).toBe(false);
  });

  it("orders rows habit → ascetic → practice and omits empty practice", () => {
    const rows = buildTodayProgressRows({
      todayISO: "2026-08-08",
      habit: { id: 1, name: "Стакан воды" },
      habitStreakDays: 5,
      habitCompletedDates: ["2026-08-08"],
      ascetic: { id: 2, title: "Без сахара" },
      asceticStreakDays: 2,
      asceticCompletedDates: ["2026-08-07", "2026-08-08"],
      practiceName: null,
      practiceStreakDays: 0,
      practiceCompletedDates: [],
    });
    expect(rows.map((r) => r.kind)).toEqual(["habit", "ascetic"]);
    expect(rows[0].kindLabel).toBe("Привычка");
    expect(rows[0].days).toHaveLength(7);
  });
});
