import { buildTodayMyDayRhythm } from "@/lib/todayMyDayRhythm";

describe("buildTodayMyDayRhythm", () => {
  it("omits when there are no natal clocks — does not dump Global windows", () => {
    expect(
      buildTodayMyDayRhythm({
        glanceRows: [],
        windows: [
          { time: "14:30", driver_id: "sky-1", supports: ["deep_work"], cautions: ["hard_negotiation"] },
        ],
      }),
    ).toEqual([]);
  });

  it("joins Engine supports/cautions onto natal clocks by time", () => {
    const rows = buildTodayMyDayRhythm({
      glanceRows: [
        {
          time_local: "2026-08-15T14:20:00",
          label_short: "Точный аспект",
          valence: "favorable",
          driver_id: "natal-1",
        },
      ],
      windows: [
        {
          time: "14:30",
          driver_id: "sky-1",
          supports: ["deep_work"],
          cautions: ["hard_negotiation"],
        },
      ],
    });
    expect(rows).toHaveLength(1);
    expect(rows[0]?.time).toBe("14:20");
    expect(rows[0]?.title).toBe("Точный аспект");
    expect(rows[0]?.supports).toContain("Глубокая работа");
    expect(rows[0]?.cautions).toContain("Жёсткий торг");
  });

  it("keeps natal clocks without inventing action chips when windows do not match", () => {
    const rows = buildTodayMyDayRhythm({
      glanceRows: [
        {
          time_local: "08:00",
          label_short: "Утро",
          valence: "caution",
          driver_id: "natal-am",
        },
      ],
      windows: [{ time: "21:00", driver_id: "sky-night", supports: ["rest"], cautions: [] }],
    });
    expect(rows).toHaveLength(1);
    expect(rows[0]?.supports).toEqual([]);
    expect(rows[0]?.cautions).toEqual([]);
  });
});
