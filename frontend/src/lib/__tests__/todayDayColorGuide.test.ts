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

  it("merges API overrides when present", () => {
    const guide = resolveTodayDayColorGuide({
      name: "Лазурь",
      api: {
        name: "Лазурь",
        benefit_ru: "API benefit",
        clothing_ru: "API clothing",
      },
    });
    expect(guide?.benefit).toBe("API benefit");
    expect(guide?.clothing).toBe("API clothing");
    expect(guide?.accessory).toMatch(/браслет/i);
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
