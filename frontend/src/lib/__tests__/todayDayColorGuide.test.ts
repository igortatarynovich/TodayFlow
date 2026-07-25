import { colorGuideSkyStory, resolveTodayDayColorGuide } from "@/lib/todayDayColorGuide";

describe("resolveTodayDayColorGuide", () => {
  it("returns catalog row for known color", () => {
    const guide = resolveTodayDayColorGuide({ name: "Лазурь" });
    expect(guide?.name).toBe("Лазурь");
    expect(guide?.benefit).toMatch(/ясност/i);
    expect(guide?.clothing).toBeTruthy();
    expect(guide?.accessory).toBeTruthy();
    expect(guide?.amount).toBeTruthy();
    expect(guide?.avoidColor).toBeTruthy();
    expect(guide?.avoidWhy).toBeTruthy();
  });

  it("prefers scenario talisman over API benefit/avoid", () => {
    const guide = resolveTodayDayColorGuide({
      name: "Лазурь",
      api: {
        name: "Лазурь",
        benefit_ru: "API benefit",
        avoid_color_ru: "API avoid",
        avoid_why_ru: "API why",
      },
      scenario: {
        name: "Лазурь",
        note: "Держит ясность в коротких решениях.",
        avoidColor: "кислотный жёлтый",
        avoidWhy: "Размывает точность конфликта дня.",
      },
    });
    expect(guide?.benefit).toMatch(/ясност|коротких/i);
    expect(guide?.avoidColor).toBe("кислотный жёлтый");
    expect(guide?.avoidWhy).toMatch(/конфликта/i);
  });

  it("returns null when name missing", () => {
    expect(resolveTodayDayColorGuide({ name: null })).toBeNull();
  });

  it("uses default preset for unknown color name", () => {
    const guide = resolveTodayDayColorGuide({ name: "золотистый" });
    expect(guide?.name).toBe("золотистый");
    expect(guide?.benefit).toBeTruthy();
  });
});

describe("colorGuideSkyStory", () => {
  it("returns benefit line for sky card", () => {
    const guide = resolveTodayDayColorGuide({ name: "Янтарный" });
    expect(colorGuideSkyStory(guide!)).toBe(guide!.benefit);
  });
});
