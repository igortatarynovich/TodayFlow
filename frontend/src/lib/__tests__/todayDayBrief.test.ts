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
        global_day: {
          drivers: [{ id: "moon-ingress", kind: "moon_ingress", fact_ru: "Луна вошла в Весы" }],
        },
        day_story: {
          contract_version: "day_story_v1",
          theme: "Мягкий поток",
          trap: "Торопить ответ",
          do: ["Держать один канал"],
          day_foundation: {
            lunar: {
              phase: { id: "waxing_gibbous", name: "Растущая Луна", cycle_day: 11, themes: "Сбор сил" },
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
    expect(model.moonCard?.title).toBe("Луна в Весах");
    expect(model.moonCard?.meta).toContain("Растущая Луна");
    expect(model.moonCard?.meta).toContain("11-й день цикла");
    expect(model.moonCard?.sheetRows.map((r) => r.label)).toEqual(
      expect.arrayContaining(["Знак", "Фаза", "Цикл", "Смена знака"]),
    );
    expect(model.moonCard?.context).toBeTruthy();
    expect(model.skyStrip).toBeNull();
    expect(model.moonPhase).toBeCloseTo(11 / 29.53058867, 5);
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

  it("falls back to lunarHint when foundation phase is missing", () => {
    const model = buildTodayDayBriefModel({
      contract: baseContract,
      dateLabel: "14 августа",
      salutation: "Привет",
      lunarHint: { id: "new", name: "Новолуние", cycle_day: 1.18 },
    });
    expect(model.moonPhase).toBeCloseTo(1.18 / 29.53058867, 5);
  });

  it("resolves moonPhase from welcome glass reason when foundation/hint empty", () => {
    const model = buildTodayDayBriefModel({
      contract: baseContract,
      dateLabel: "14 августа",
      salutation: "Привет",
      welcomeGlass: {
        moodPills: [],
        reasonLine: "Новолуние — Тихий сброс, прояснение мотивов",
        activityTags: [],
      },
    });
    expect(model.lunarCaption).toContain("Новолуние");
    expect(model.moonPhase).toBe(0);
  });

  it("prefers sky_today Moon-in-sign over catalog phase caption", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        sky_today: {
          contract_version: "sky_today_v1",
          moon: { body: "moon", body_ru: "Луна", sign: "Virgo", sign_ru: "Дева", degree: 28.7 },
          headline: {
            id: "sky-mercury-conjunction-jupiter",
            planet_a: "mercury",
            planet_b: "jupiter",
            planet_a_ru: "Меркурий",
            planet_b_ru: "Юпитер",
            sign_a: "Leo",
            sign_b: "Leo",
            sign_a_ru: "Лев",
            sign_b_ru: "Лев",
            aspect: "conjunction",
            aspect_ru: "соединение",
              title_ru: "Меркурий во Льве — соединение — Юпитер во Льве",
          },
          positions: [],
          aspects: [],
        },
        day_story: {
          contract_version: "day_story_v1",
          day_foundation: {
            lunar: {
              phase: { id: "new", name: "Новолуние" },
              moon_sign: { sign_ru: "Дева" },
            },
          },
        },
      },
      dateLabel: "15 августа",
      salutation: "Привет",
    });
    expect(model.lunarCaption).toBe("Луна в Деве");
    expect(model.skyStrip?.moonLabel).toBe("Луна в Деве");
    expect(model.skyStrip?.headlineLabel).toContain("Меркурий во Льве");
    expect(model.whyFactors.find((f) => f.id === "lunar")?.label).toBe("Луна в Деве");
    expect(model.skyStrip?.personalLine).toBeNull();
  });

  it("puts natal overlay on MY DAY personalLine, not the Global sky strip", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        personal_growth: { development_point: "точка роста персонажа" },
        sky_today: {
          moon: { body: "moon", body_ru: "Луна", sign: "Virgo", sign_ru: "Дева" },
        },
        day_story: {
          contract_version: "day_story_v1",
          day_scenario: {
            conflict: {
              why_personal: "тебе обычно проще держать слово, если оно взвешено заранее",
            },
          },
        },
      },
      dateLabel: "15 августа",
      salutation: "Привет",
    });
    expect(model.skyStrip?.personalLine).toBeNull();
    expect(model.personalLine).toContain("держать слово");
    expect(model.personalLine).not.toContain("точка роста");
  });

  it("does not treat unavailable shell copy as personalLine or atmosphere", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        global_context: { period: "Не удалось загрузить." },
        personal_growth: { development_point: "Не удалось загрузить." },
        day_story: {
          contract_version: "day_story_v1",
          interpretation_status: "unavailable",
          theme: "Ровный продуктивный ритм.",
          day_scenario: {
            conflict: { why_personal: "тебе обычно проще держать слово" },
          },
        },
      },
      dateLabel: "18 августа",
      salutation: "Привет",
    });
    expect(model.personalLine).toBeNull();
    expect(model.atmosphereLine).toBe("Ровный продуктивный ритм.");
    expect(model.doItems).toEqual([]);
  });

  it("reads Global driver and strength/risk chips from global_day", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        global_day: {
          primary_energy: "clarity",
          energy_scores: { clarity: 0.78, tension: 0.2 },
          drivers: [
            { id: "moon-ingress", kind: "moon_ingress", fact_ru: "Луна вошла в Деву" },
            { id: "mars-sat", kind: "sky_aspect", fact_ru: "Марс в квадрате к Сатурну" },
          ],
          strength: ["deep_work", "admin_order"],
          risk: ["hard_negotiation", "unknown_type"],
          windows: [
            {
              time: "08:30",
              driver_id: "moon-ingress",
              intensity: 0.4,
              supports: ["deep_work"],
              cautions: ["hard_negotiation"],
            },
            {
              time: "14:30",
              driver_id: "mars-sat",
              intensity: 0.8,
              supports: ["deep_work"],
              cautions: ["hard_negotiation"],
            },
          ],
        },
      },
      dateLabel: "15 августа",
      salutation: "Привет",
    });
    expect(model.visualMode).toBe("clarity");
    expect(model.energyPct).toBe(78);
    expect(model.modeLabel).toBe("Ясность");
    expect(model.mainDriver?.title).toContain("Луна вошла в Деву");
    expect(model.mainDriver?.body).toBe("Смена знака");
    expect(model.mainDriver?.planets).toEqual(["moon"]);
    expect(model.mainDriver?.sheetRows.some((r) => r.label === "Время" && r.value === "08:30")).toBe(
      true,
    );
    expect(
      model.mainDriver?.sheetRows.some(
        (r) => r.label === "Поддерживает" && String(r.value).includes("Глубокая работа"),
      ),
    ).toBe(true);
    expect(
      model.mainDriver?.sheetRows.some(
        (r) => r.label === "Осторожнее" && String(r.value).includes("Жёсткий торг"),
      ),
    ).toBe(true);
    expect(model.mainDriver?.sheetRows.some((r) => r.label === "Связь с энергией")).toBe(true);
    expect(model.transits.map((t) => t.title)).toEqual(
      expect.arrayContaining(["Луна вошла в Деву", "Марс в квадрате к Сатурну"]),
    );
    expect(model.transits.find((t) => t.id === "mars-sat")?.time).toBe("14:30");
    expect(model.transits.find((t) => t.id === "mars-sat")?.planets).toEqual(
      expect.arrayContaining(["mars", "saturn"]),
    );
    expect(model.dayWindow?.start).toBe("08:30");
    expect(model.dayWindow?.end).toBe("14:30");
    expect(model.dayWindow?.mark).toBeCloseTo((8 * 60 + 30 - 6 * 60) / (18 * 60), 5);
    expect(model.strengthChips.map((c) => c.id)).toEqual(["deep_work", "admin_order"]);
    expect(model.strengthChips[0]?.sheetRows[0]?.value).toContain("Луна вошла в Деву");
    expect(model.strengthChips[0]?.sheetRows.some((r) => r.label === "Время")).toBe(true);
    expect(model.riskChips.map((c) => c.id)).toEqual(["hard_negotiation"]);
    expect(model.riskChips[0]?.sheetRows[0]?.value).toContain("Луна вошла в Деву");
  });

  it("does not leak driver kind ids and maps lunar drivers to the moon image", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        global_day: {
          primary_energy: "renewal",
          drivers: [{ id: "lun-1", kind: "phase_change", fact_ru: "Новолуние." }],
        },
      },
      dateLabel: "15 августа",
      salutation: "Привет",
    });
    expect(model.modeLabel).toBe("Обновление");
    expect(model.mainDriver?.title).toBe("Новолуние.");
    expect(model.mainDriver?.body).toBe("Смена фазы");
    expect(model.mainDriver?.body).not.toMatch(/phase_change/);
    expect(model.mainDriver?.planets).toEqual(["moon"]);
  });

  it("omits energy percent and day window when Engine left them empty", () => {
    const model = buildTodayDayBriefModel({
      contract: {
        ...baseContract,
        global_day: {
          primary_energy: "tension",
          drivers: [{ id: "d1", kind: "sky_aspect", fact_ru: "Марс в соединении с Венерой" }],
          windows: [{ time: "11:00", driver_id: "d1" }],
        },
      },
      dateLabel: "15 августа",
      salutation: "Привет",
    });
    expect(model.energyPct).toBeNull();
    expect(model.dayWindow).toBeNull();
    expect(model.transits[0]?.title).toContain("Марс в соединении с Венерой");
    expect(model.transits[0]?.time).toBe("11:00");
    expect(model.transits[0]?.planets).toEqual(expect.arrayContaining(["mars", "venus"]));
  });
});
