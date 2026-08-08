import { buildStoryDayFlow } from "@/lib/todayStoryDayFlow";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";

describe("todayStoryDayFlow", () => {
  it("returns empty when no glance windows (no invented phases)", () => {
    expect(buildStoryDayFlow({})).toEqual([]);
    expect(buildStoryDayFlow({ glanceWindows: [] })).toEqual([]);
  });

  it("renders only real glance windows with label_short as body", () => {
    const windows: GlanceTimelineItem[] = [
      {
        time_local: "2026-08-05T16:15:00",
        label_short: "Диалоги и письма",
        valence: "favorable",
        driver_id: "a",
      },
      {
        time_local: "2026-08-05T04:45:00",
        label_short: "Короткие задачи",
        valence: "favorable",
        driver_id: "b",
      },
    ];
    const points = buildStoryDayFlow({ glanceWindows: windows });
    expect(points.map((p) => p.phase)).toEqual(["04:45", "16:15"]);
    expect(points[0]?.body).toBe("Короткие задачи");
    expect(points[0]?.timed).toBe(true);
    expect(points[1]?.body).toBe("Диалоги и письма");
    expect(points.every((p) => p.timed)).toBe(true);
  });

  it("drops rows without label_short (no invent filler)", () => {
    const windows: GlanceTimelineItem[] = [
      {
        time_local: "2026-08-05T10:00:00",
        label_short: "",
        valence: "caution",
        driver_id: "empty",
      },
      {
        time_local: "2026-08-05T12:00:00",
        label_short: "Пауза",
        valence: "caution",
        driver_id: "ok",
      },
    ];
    const points = buildStoryDayFlow({ glanceWindows: windows });
    expect(points).toHaveLength(1);
    expect(points[0]?.body).toBe("Пауза");
  });
});
