import { buildStoryDayFlow } from "@/lib/todayStoryDayFlow";

describe("todayStoryDayFlow", () => {
  it("always returns five phase points covering the whole day", () => {
    const points = buildStoryDayFlow();
    expect(points).toHaveLength(5);
    expect(points.map((p) => p.phase)).toEqual(["Утро", "День", "Диалоги", "Вечер", "Ночь"]);
    expect(points[0]!.body).toMatch(/старт/i);
    expect(points[3]!.body).toMatch(/итог|благодарност/i);
    expect(points[4]!.body).toMatch(/отдых|отпускан/i);
  });

  it("soft energy yields a heavier morning start", () => {
    const points = buildStoryDayFlow({
      energyLine: "Фаза луны минус энергия — спад честный и громкий.",
    });
    expect(points[0]!.valence).toBe("caution");
    expect(points[0]!.body).toMatch(/тяжёл|медленн|без разгона/i);
  });

  it("uses prioritize for the day tasks point", () => {
    const points = buildStoryDayFlow({
      prioritize: "Закрыть один важный разговор без давления",
    });
    expect(points[1]!.body).toMatch(/Закрыть один важный разговор/i);
  });

  it("marks dialogues caution when avoid is about words", () => {
    const points = buildStoryDayFlow({
      avoid: "Не ввязываться в острые споры и переписку на эмоциях",
    });
    expect(points[2]!.valence).toBe("caution");
    expect(points[2]!.body).toMatch(/Разговоры|острые/i);
  });
});
