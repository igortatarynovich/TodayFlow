import { saveDayEngagement } from "@/lib/todayDayEngagement";
import { saveDayContinuity } from "@/lib/todayDayContinuity";
import {
  buildMoodDayStory,
  buildMoodMapCells,
  buildMoodMapObservation,
  shiftDateISO,
} from "@/lib/moodMapModel";
import { scanMoodMapDayRecords } from "@/lib/todayDayEngagement";

describe("moodMapModel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("indexes engagement records for the map", () => {
    saveDayEngagement("2026-06-20", {
      morningMoodId: "calm",
      morningMoodCapturedAtMs: Date.now(),
      focusTopicId: "work",
    });

    const records = scanMoodMapDayRecords();
    expect(records).toHaveLength(1);
    expect(records[0]).toMatchObject({ dateISO: "2026-06-20", moodId: "calm", focusLabel: "Работа" });
  });

  it("builds day story with continuity outcome", () => {
    saveDayEngagement("2026-06-22", {
      morningMoodId: "anxious",
      morningMoodCapturedAtMs: Date.now(),
      focusTopicId: "work",
      dayGoal: "Не торопиться",
    });
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Отдых",
      outcome: "not_done",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    const record = scanMoodMapDayRecords()[0];
    expect(record).toBeTruthy();
    const story = buildMoodDayStory(record!, "ru");
    expect(story).toMatch(/Тревожно/);
    expect(story).toMatch(/Не торопиться/);
    expect(story).toMatch(/не удалось выполнить/);
  });

  it("returns observation after enough marks", () => {
    for (let i = 0; i < 4; i += 1) {
      const dateISO = shiftDateISO("2026-06-22", -i);
      saveDayEngagement(dateISO, {
        morningMoodId: "calm",
        morningMoodCapturedAtMs: Date.now(),
      });
    }
    const observation = buildMoodMapObservation(scanMoodMapDayRecords(), "ru");
    expect(observation?.text).toMatch(/Спокойно/);
  });
});
