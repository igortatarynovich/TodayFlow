import { buildStoryDayFlow } from "@/lib/todayStoryDayFlow";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";

describe("todayStoryDayFlow", () => {
  it("always frames the day with morning, evening, and night rest", () => {
    const points = buildStoryDayFlow({
      energyLine: "Фаза луны минус энергия — спад честный.",
    });
    expect(points[0]?.phase).toBe("Утро");
    expect(points[0]?.body).toMatch(/тяжёл|медленн/i);
    expect(points[points.length - 2]?.phase).toBe("Вечер");
    expect(points[points.length - 2]?.body).toMatch(/итог|благодарност/i);
    expect(points[points.length - 1]?.phase).toBe("Ночь");
    expect(points[points.length - 1]?.body).toMatch(/отдых|отпускан/i);
  });

  it("inserts real glance windows between morning and evening", () => {
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
    const points = buildStoryDayFlow({
      energyLine: "Ровный темп",
      glanceWindows: windows,
    });
    expect(points.map((p) => p.phase)).toEqual(["Утро", "04:45", "16:15", "Вечер", "Ночь"]);
    expect(points[1]?.body).toMatch(/Короткие задачи/i);
    expect(points[1]?.timed).toBe(true);
    expect(points[2]?.body).toMatch(/Диалоги/i);
  });

  it("falls back to day tasks/dialogues when no timed windows", () => {
    const points = buildStoryDayFlow({
      prioritize: "Закрыть один важный разговор",
      avoid: "Не ввязываться в острые споры",
    });
    expect(points.some((p) => /Задачи:/i.test(p.body))).toBe(true);
    expect(points.some((p) => p.phase === "Диалоги" && p.valence === "caution")).toBe(true);
  });
});
