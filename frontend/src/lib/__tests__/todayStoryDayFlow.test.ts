import { buildStoryDayFlow, valenceChromeLabel } from "@/lib/todayStoryDayFlow";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";

describe("todayStoryDayFlow", () => {
  it("returns empty when no glance windows (no invented phases)", () => {
    expect(buildStoryDayFlow({})).toEqual([]);
    expect(buildStoryDayFlow({ glanceWindows: [] })).toEqual([]);
  });

  it("renders only real glance windows with label_short as body and detail", () => {
    const windows: GlanceTimelineItem[] = [
      {
        time_local: "2026-08-05T16:15:00",
        label_short: "Хорошее окно для разговоров",
        detail: "Мягче контакт — спокойные диалоги и разбор дел.",
        valence: "favorable",
        driver_id: "a",
        copy_source: "kimi_v1",
      },
      {
        time_local: "2026-08-05T04:45:00",
        label_short: "Короткие задачи",
        detail: null,
        valence: "favorable",
        driver_id: "b",
        copy_source: "bank_fill",
      },
    ];
    const points = buildStoryDayFlow({ glanceWindows: windows });
    expect(points.map((p) => p.phase)).toEqual(["04:45", "16:15"]);
    expect(points[0]?.body).toBe("Короткие задачи");
    expect(points[0]?.detail).toBeNull();
    expect(points[1]?.body).toBe("Хорошее окно для разговоров");
    expect(points[1]?.detail).toMatch(/диалог/i);
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

  it("maps valence chrome without inventing product plot", () => {
    expect(valenceChromeLabel("favorable")).toBe("Благоприятно");
    expect(valenceChromeLabel("caution")).toBe("Осторожнее");
    expect(valenceChromeLabel("neutral")).toBe("");
  });
});
