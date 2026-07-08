import { saveDayContinuity } from "@/lib/todayDayContinuity";
import { buildDayContinuityWeekCells } from "@/lib/todayDayContinuityHeatmap";

describe("buildDayContinuityWeekCells", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("returns 7 days oldest to newest from local continuity", () => {
    saveDayContinuity({
      dateISO: "2026-07-05",
      mainFocus: "Фокус",
      outcome: "done",
      closedAt: "2026-07-05T21:00:00.000Z",
    });

    const cells = buildDayContinuityWeekCells("2026-07-07", 7);
    expect(cells).toHaveLength(7);
    expect(cells[0]?.dateISO).toBe("2026-07-01");
    expect(cells[6]?.dateISO).toBe("2026-07-07");
    expect(cells.find((cell) => cell.dateISO === "2026-07-05")?.closed).toBe(true);
    expect(cells.find((cell) => cell.dateISO === "2026-07-06")?.closed).toBe(false);
  });
});
