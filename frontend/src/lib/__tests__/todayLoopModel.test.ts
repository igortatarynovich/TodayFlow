import { buildTodayLoopModel } from "@/lib/todayLoopModel";
import type { TodayContractV1 } from "@/lib/todayContract";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "Пауза" },
  personal_growth: { development_point: "Держать темп ровным." },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
  day_story: {
    contract_version: "day_story_v1",
    trap: "Тянет компенсировать утро вторым кофе и быстрым стартом.",
    do: ["Короткая телесная проверка перед работой."],
    evening_closure: "Если удержали паузу — день закрывается спокойнее.",
  },
  primary_action: "Сделать один спокойный шаг.",
};

describe("buildTodayLoopModel", () => {
  it("builds morning manifesto from suggestions without inventing", () => {
    const model = buildTodayLoopModel({
      contract: base,
      dayGoal: null,
      promiseSuggestions: [
        { id: "do_0", text: "Сегодня я сделаю телесную проверку перед работой." },
        { id: "development", text: "Сегодня я держу темп ровным." },
      ],
      isEveningSurface: false,
    });
    expect(model.mode).toBe("morning");
    expect(model.accepted).toBe(false);
    expect(model.manifesto).toContain("телесную проверку");
    expect(model.alternatives).toHaveLength(1);
  });

  it("marks accepted when dayGoal set and switches evening checkout", () => {
    const model = buildTodayLoopModel({
      contract: base,
      dayGoal: "Сегодня я не бужу себя стимулом.",
      promiseSuggestions: [{ id: "do_0", text: "Сегодня я сделаю телесную проверку." }],
      isEveningSurface: true,
    });
    expect(model.mode).toBe("evening");
    expect(model.accepted).toBe(true);
    expect(model.manifesto).toContain("не бужу");
    expect(model.trapCheck).toContain("кофе");
    expect(model.eveningClosure).toContain("закрывается");
  });

  it("omits kitchen trap dump", () => {
    const model = buildTodayLoopModel({
      contract: {
        ...base,
        day_story: {
          ...base.day_story!,
          trap: "Профекция года (возраст 36): управитель Сатурн. 1.1°.",
        },
      },
      isEveningSurface: true,
    });
    expect(model.trapCheck).toBeNull();
  });
});
