import { buildTodayDayBriefModel, cleanAmbassadorWhy } from "@/lib/todayDayBrief";
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
    expect(model.expect).toContain("Обострённая интуиция");
    expect(model.trap).toContain("Поиск подвоха");
    expect(model.doItems[0]).toContain("Доверять");
    expect(model.avoidItems[0]).toContain("Не лезть");
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

  it("rejects kitchen profection dump for why and prefers why_arose", () => {
    const dump =
      "Ещё активных личных транзитов: 2. Профекция года (возраст 36): 1-й дом, " +
      "управитель Сатурн. Секундарные прогрессии: прогресс. Солнце 1.1°. Solar return 2026.";
    expect(cleanAmbassadorWhy(dump)).toBeNull();

    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Стратегическая пауза",
          day_personal: { summary_ru: dump },
          story: "Длинная сцена про почту и пять писем — не вайб-список.",
          day_scenario: {
            conflict: {
              why_arose: "Серп Луны гасит лишний шум — день просит меньше входящего.",
            },
          },
        },
      },
      dateLabel: "10 августа",
      salutation: "Добрый день",
    });
    expect(model.why).toContain("Серп Луны");
    expect(model.why).not.toMatch(/профекц|Solar return/i);
    expect(model.vibeClosing).toBeNull();
  });

  it("clips long expect for compass scan", () => {
    const long =
      "Утром тело подаёт первые сигналы — чуть тяжелее оторваться. " +
      "Это не сон, это фаза: серп гаснет. " +
      "Если позволить себе лишние десять минут на ощутимые вещи, тело отдаст курс. " +
      "И ещё один абзац про почту и пять писем, который не должен попасть в компас целиком.";
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Пауза",
          expect: long,
          trap: "Второй кофе вместо опоры.",
          do: ["Телесная проверка перед работой."],
        },
      },
      dateLabel: "10 августа",
      salutation: "Добрый день",
    });
    expect(model.expect!.length).toBeLessThan(long.length);
    expect(model.expect).toContain("первые сигналы");
  });
});
