import { saveDayEngagement } from "@/lib/todayDayEngagement";
import { saveDayContinuity } from "@/lib/todayDayContinuity";
import {
  buildEnergyDayStory,
  buildEnergyMapCells,
  buildEnergyMapObservation,
  buildEnergyMapRecordsWithMoodFallback,
  energyCellColor,
  inferEnergyFromMood,
} from "@/lib/energyMapModel";
import { shiftDateISO } from "@/lib/moodMapModel";
import {
  persistEnergyFromFusionResponse,
  scanEnergyMapDayRecords,
} from "@/lib/energyMapStorage";

describe("energyMapModel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("persists fusion energy records", () => {
    persistEnergyFromFusionResponse("2026-06-20", {
      date: "2026-06-20",
      scores: { energy: 72, focus: 60, emotional_balance: 55 },
    });

    const records = scanEnergyMapDayRecords();
    expect(records).toHaveLength(1);
    expect(records[0]).toMatchObject({ dateISO: "2026-06-20", energyScore: 72, source: "fusion_api" });
  });

  it("infers energy from morning mood when fusion is missing", () => {
    saveDayEngagement("2026-06-21", {
      morningMoodId: "driven",
      morningMoodCapturedAtMs: Date.now(),
    });

    const records = buildEnergyMapRecordsWithMoodFallback();
    expect(records).toHaveLength(1);
    expect(records[0]).toMatchObject({ dateISO: "2026-06-21", energyScore: 78, source: "mood_infer" });
    expect(inferEnergyFromMood("tired")).toBe(32);
  });

  it("builds day story with tempo and continuity", () => {
    saveDayEngagement("2026-06-22", {
      morningMoodId: "calm",
      morningMoodCapturedAtMs: Date.now(),
      focusTopicId: "work",
    });
    saveDayContinuity({
      dateISO: "2026-06-21",
      mainFocus: "Отдых",
      outcome: "done",
      closedAt: "2026-06-21T20:00:00.000Z",
    });
    persistEnergyFromFusionResponse("2026-06-22", {
      date: "2026-06-22",
      scores: { energy: 68, focus: 50, emotional_balance: 50 },
    });

    const record = scanEnergyMapDayRecords()[0];
    expect(record).toBeTruthy();
    const story = buildEnergyDayStory(record!, "ru");
    expect(story).toMatch(/темп дня/i);
    expect(story).toMatch(/Работа/);
    expect(story).toMatch(/закрыли спокойно/i);
  });

  it("colors cells by tempo band and returns observation after enough marks", () => {
    expect(energyCellColor(30)).toMatch(/154, 132, 104/);
    expect(energyCellColor(85)).toMatch(/107, 143, 90/);

    for (let i = 0; i < 4; i += 1) {
      const dateISO = shiftDateISO("2026-06-22", -i);
      persistEnergyFromFusionResponse(dateISO, {
        date: dateISO,
        scores: { energy: 82, focus: 70, emotional_balance: 65 },
      });
    }

    const cells = buildEnergyMapCells("2026-06-22", 7);
    expect(cells.filter((cell) => cell.record)).toHaveLength(4);

    const observation = buildEnergyMapObservation(scanEnergyMapDayRecords(), "ru");
    expect(observation?.text).toMatch(/темп|подвижн/i);
  });
});
