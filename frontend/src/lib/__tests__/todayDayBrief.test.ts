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
  it("assembles atmosphere + orientation fields without inventing", () => {
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
            conflict: {
              why_arose: "Серп гаснет — день просит меньше входящего.",
            },
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
        moodPills: ["Ясный ум", "Порядок в делах"],
        reasonLine: null,
        activityTags: ["подготовка"],
      },
      energyLine: "Тихий стратегический темп",
      energyCause: "Трин Луны и Плутона",
    });

    expect(model.atmosphereLine).toBe("Стратегическая пауза");
    expect(model.vibe).toBe("Стратегическая пауза");
    expect(model.atmosphereNote).toContain("Серп гаснет");
    expect(model.expect).toContain("Обострённая интуиция");
    expect(model.trap).toContain("Поиск подвоха");
    expect(model.doItems[0]).toContain("Доверять");
    expect(model.avoidItems[0]).toContain("Не лезть");
    expect(model.moodPills).toEqual(["Ясный ум", "Порядок в делах"]);
    expect(model.accents).toEqual(["Работа"]);
    expect(model.vibeClosing).toBeNull();
    expect(model.activityTags).toEqual(["подготовка"]);
    expect(model.supportLine).toContain("Доверять");
    expect(model.betterCards.map((c) => c.id)).toEqual(
      expect.arrayContaining(["work", "people"]),
    );
    expect(model.betterCards.find((c) => c.id === "work")?.body).toBeTruthy();
  });

  it("builds lunar caption, why factors, and personal line from foundation", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        day_atmosphere: {
          visual_mode: "flow",
          intensity: 0.5,
          warmth: 0.5,
          motion: "low",
          contrast: "medium",
          decor_variant: "default",
          time_phase: "day",
        },
        day_story: {
          contract_version: "day_story_v1",
          theme: "Мягкий поток",
          trap: "Торопить ответ",
          do: ["Держать один канал"],
          day_foundation: {
            lunar: {
              phase: { name: "Растущая Луна", themes: "Сбор сил" },
              moon_sign: { sign_ru: "Весы" },
              beats: [{ id: "b1", title: "Тригон Луна — Плутон", story_ru: "Глубина без драмы." }],
            },
            numerology: { personal_day: 10, summary_ru: "Число про ясность выбора." },
          },
          day_scenario: {
            conflict: {
              why_personal: "Ты уже чувствуешь, где лишний шум.",
            },
            scenes: [
              {
                scene_id: "s1",
                sphere: "work",
                opportunity: "Одно ясное письмо.",
              },
              {
                scene_id: "s2",
                sphere: "relationships",
                opportunity: "Короткий честный разговор.",
              },
              {
                scene_id: "s3",
                sphere: "energy",
                opportunity: "Пауза без телефона.",
              },
            ],
          },
        },
      },
      dateLabel: "10 августа 2026",
      salutation: "Доброе утро",
    });

    expect(model.visualMode).toBe("flow");
    expect(model.modeLabel).toBeTruthy();
    expect(model.lunarCaption).toBe("Растущая Луна в Весы");
    expect(model.whyFactors.some((f) => f.id === "lunar")).toBe(true);
    expect(model.whyFactors.some((f) => f.id === "number")).toBe(true);
    expect(model.betterCards).toHaveLength(3);
    expect(model.personalLine).toContain("лишний шум");
  });

  it("omits empty sections and does not duplicate atmosphere into expect note", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Один тон",
          story: "Один тон",
          expect: "Один тон",
        },
      },
      dateLabel: "10 августа",
      salutation: "Привет",
      welcomeGlass: {
        moodPills: [],
        reasonLine: "Один тон",
        activityTags: [],
      },
    });
    expect(model.atmosphereLine).toBe("Один тон");
    expect(model.atmosphereNote).toBeNull();
    expect(model.expect).toBe("Один тон");
    expect(model.vibeClosing).toBeNull();
  });

  it("rejects kitchen profection dump for atmosphere note", () => {
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
    expect(model.atmosphereNote).toContain("Серп Луны");
    expect(model.atmosphereNote).not.toMatch(/профекц|Solar return/i);
    expect(model.vibeClosing).toBeNull();
  });

  it("keeps expect readable (not ultra-short compass clip)", () => {
    const long =
      "Утром тело подаёт первые сигналы — чуть тяжелее оторваться. " +
      "Это не сон, это фаза: серп гаснет. " +
      "Если позволить себе лишние десять минут на ощутимые вещи, тело отдаст курс.";
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
    expect(model.expect).toContain("первые сигналы");
    expect(model.expect).toContain("серп гаснет");
  });
});
