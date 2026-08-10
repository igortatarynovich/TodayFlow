import { buildTodayDayBriefModel } from "@/lib/todayDayBrief";
import type { TodayContractV1 } from "@/lib/todayContract";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "Период спокойной ясности" },
  personal_growth: { development_point: "Один шаг" },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
};

describe("buildTodayDayBriefModel", () => {
  it("assembles ambassador brief from day_story without inventing", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Стратегическая пауза",
          events_lead: "Луна в Раке в точном трине с Плутоном.",
          expect: "Обострённая интуиция.",
          trap: "Поиск подвоха на ровном месте.",
          do: ["Доверять шестому чувству", "Готовить почву"],
          avoid: ["Не лезть на рожон"],
          vibe_closing: "Спокойная уверенность и глубокий фокус.",
          day_scenario: {
            scenes: [
              {
                scene_id: "s1",
                sphere: "work",
                sphere_label_ru: "Работа",
                role_in_story: "primary",
              },
              {
                scene_id: "s2",
                sphere: "relationships",
                sphere_label_ru: "Отношения",
                role_in_story: "support",
              },
            ],
          },
        },
      },
      dateLabel: "10 августа 2026",
      salutation: "Доброе утро",
      headline: null,
      welcomeGlass: {
        moodPills: ["спокойствие"],
        reasonLine: null,
        activityTags: ["подготовка"],
      },
      energyLine: "Тихий стратегический темп",
      energyCause: "Трин Луны и Плутона",
    });

    expect(model.vibe).toBe("Стратегическая пауза");
    expect(model.why).toContain("Луна в Раке");
    expect(model.expect).toBe("Обострённая интуиция.");
    expect(model.trap).toBe("Поиск подвоха на ровном месте.");
    expect(model.doItems).toEqual(["Доверять шестому чувству", "Готовить почву"]);
    expect(model.avoidItems).toEqual(["Не лезть на рожон"]);
    expect(model.accents).toEqual(["Работа"]);
    expect(model.vibeClosing).toContain("Спокойная уверенность");
    expect(model.activityTags).toEqual(["подготовка"]);
  });

  it("omits empty sections and does not duplicate vibe into closing", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Один тон",
          story: "Один тон",
        },
      },
      dateLabel: "10 августа",
      salutation: "Привет",
    });
    expect(model.vibe).toBe("Один тон");
    expect(model.why).toBeNull();
    expect(model.expect).toBeNull();
    expect(model.vibeClosing).toBeNull();
  });
});
