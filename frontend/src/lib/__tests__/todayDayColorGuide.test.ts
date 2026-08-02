import {
  COLOR_DAY_UNAVAILABLE_RU,
  COLOR_HEX,
  colorGuideSkyStory,
  resolveTodayDayColorGuide,
} from "@/lib/todayDayColorGuide";

describe("resolveTodayDayColorGuide", () => {
  it("returns hex-only shell for known catalog name without BE prose (unavailable)", () => {
    const guide = resolveTodayDayColorGuide({ name: "Лазурь" });
    expect(guide?.name).toBe("Лазурь");
    expect(guide?.hex).toBe(COLOR_HEX["Лазурь"]);
    expect(guide?.benefit).toBe("");
    expect(guide?.clothing).toBe("");
    expect(guide?.unavailable).toBe(true);
  });

  it("prefers scenario talisman over API benefit/avoid", () => {
    const guide = resolveTodayDayColorGuide({
      name: "Лазурь",
      api: {
        name: "Лазурь",
        benefit_ru: "API benefit",
        clothing_ru: "Рубашка",
        accessory_ru: "Браслет",
        amount_ru: "Один акцент",
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
    expect(guide?.unavailable).toBe(false);
    expect(guide?.hex).toBe(COLOR_HEX["Лазурь"]);
  });

  it("returns null when name missing", () => {
    expect(resolveTodayDayColorGuide({ name: null })).toBeNull();
    expect(
      resolveTodayDayColorGuide({
        scenario: { name: { clothing: "x" } as unknown as string },
      }),
    ).toBeNull();
  });

  it("does not invent DEFAULT_COLOR for unknown name — honest unavailable", () => {
    const guide = resolveTodayDayColorGuide({ name: "золотистый" });
    expect(guide).not.toBeNull();
    expect(guide!.name).toBe("золотистый");
    expect(guide!.hex).toBe("");
    expect(guide!.benefit).toBe("");
    expect(guide!.unavailable).toBe(true);
  });

  it("fills prose only from BE api fields", () => {
    const guide = resolveTodayDayColorGuide({
      name: "Янтарный",
      api: {
        name: "Янтарный",
        benefit_ru: "тёплая поддержка энергии тела без разгона и без суеты",
        clothing_ru: "Янтарный шарф или тёплый свитер.",
        accessory_ru: "Украшение медового оттенка.",
        amount_ru: "тёплый акцент у лица или на руках",
        avoid_color_ru: "Холодный стальной",
        avoid_why_ru: "Усиливает срыв в «harsh / over_control».",
      },
    });
    expect(guide?.unavailable).toBe(false);
    expect(guide?.benefit).toMatch(/тёплая поддержка/i);
    expect(guide?.clothing).toMatch(/шарф/i);
  });
});

describe("colorGuideSkyStory", () => {
  it("returns unavailable copy when prose missing", () => {
    const guide = resolveTodayDayColorGuide({ name: "Янтарный" });
    expect(colorGuideSkyStory(guide!)).toBe(COLOR_DAY_UNAVAILABLE_RU);
  });

  it("returns benefit when BE prose present", () => {
    const guide = resolveTodayDayColorGuide({
      name: "Янтарный",
      api: { benefit_ru: "тёплая поддержка энергии тела без разгона и без суеты" },
    });
    expect(colorGuideSkyStory(guide!)).toMatch(/тёплая поддержка/i);
  });
});
