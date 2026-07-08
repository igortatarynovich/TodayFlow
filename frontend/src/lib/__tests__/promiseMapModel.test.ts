import { saveDayContinuity } from "@/lib/todayDayContinuity";
import { saveDayEngagement } from "@/lib/todayDayEngagement";
import {
  buildPromiseDayStory,
  buildPromiseMapCells,
  buildPromiseMapObservation,
  promiseCellColor,
  scanPromiseMapDayRecords,
} from "@/lib/promiseMapModel";

describe("promiseMapModel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("indexes closed continuity and open day promises", () => {
    saveDayContinuity({
      dateISO: "2026-06-20",
      mainFocus: "Не торопиться",
      outcome: "done",
      closedAt: "2026-06-20T20:00:00.000Z",
    });
    saveDayEngagement("2026-06-21", {
      dayGoal: "Один разговор",
      morningMoodId: "calm",
      morningMoodCapturedAtMs: Date.now(),
    });

    const records = scanPromiseMapDayRecords();
    expect(records).toHaveLength(2);
    expect(records.find((r) => r.dateISO === "2026-06-20")).toMatchObject({
      promiseText: "Не торопиться",
      outcome: "done",
    });
    expect(records.find((r) => r.dateISO === "2026-06-21")).toMatchObject({
      promiseText: "Один разговор",
      outcome: "open",
    });
  });

  it("builds day story with outcome and mood", () => {
    saveDayEngagement("2026-06-22", {
      dayGoal: "Не торопиться",
      morningMoodId: "anxious",
      morningMoodCapturedAtMs: Date.now(),
      focusTopicId: "work",
    });
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Не торопиться",
      outcome: "not_done",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    const record = scanPromiseMapDayRecords()[0];
    expect(record).toBeTruthy();
    const story = buildPromiseDayStory(record!, "ru");
    expect(story).toMatch(/Не торопиться/);
    expect(story).toMatch(/осталось открытым/i);
    expect(story).toMatch(/Тревожно/);
  });

  it("colors cells and returns observation after enough closed days", () => {
    expect(promiseCellColor("done", false)).toMatch(/107, 143, 90/);
    expect(promiseCellColor("open", false)).toMatch(/214, 179, 122/);

    for (let i = 0; i < 4; i += 1) {
      const dateISO = `2026-06-${String(19 - i).padStart(2, "0")}`;
      saveDayContinuity({
        dateISO,
        mainFocus: `Фокус ${i}`,
        outcome: i % 2 === 0 ? "done" : "not_done",
        closedAt: `${dateISO}T20:00:00.000Z`,
      });
    }

    const cells = buildPromiseMapCells("2026-06-19");
    expect(cells.filter((cell) => cell.record).length).toBeGreaterThanOrEqual(3);

    const observation = buildPromiseMapObservation(scanPromiseMapDayRecords(), "ru");
    expect(observation?.text).toMatch(/обещан/i);
  });
});
