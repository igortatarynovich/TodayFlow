import {
  isDayNotReady,
  localCalendarDateISO,
  readDayLifecycle,
  type TodayContractV1,
} from "@/lib/todayContract";

describe("day lifecycle C5 helpers", () => {
  it("detects day_not_ready by generation_id and progress", () => {
    const byId = {
      generation_id: "day-not-ready-c5",
      progress: {},
    } as TodayContractV1;
    expect(isDayNotReady(byId)).toBe(true);

    const byStatus = {
      generation_id: "329",
      progress: { day_lifecycle: { status: "day_not_ready", ready_time: "08:30" } },
    } as TodayContractV1;
    expect(isDayNotReady(byStatus)).toBe(true);
    expect(readDayLifecycle(byStatus)?.ready_time).toBe("08:30");

    const ready = {
      generation_id: "329",
      progress: { day_lifecycle: { status: "ready" } },
    } as TodayContractV1;
    expect(isDayNotReady(ready)).toBe(false);
  });

  it("localCalendarDateISO matches local Y-M-D", () => {
    const d = new Date(2026, 6, 27, 1, 30, 0); // Jul 27 local
    expect(localCalendarDateISO(d)).toBe("2026-07-27");
  });
});
