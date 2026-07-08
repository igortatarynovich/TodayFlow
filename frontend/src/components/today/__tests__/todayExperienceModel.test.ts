import {
  buildTodayExperienceActionLine,
  buildTodayExperienceProgress,
  buildTodayExperienceTheme,
} from "@/components/today/todayExperienceModel";

describe("buildTodayExperienceTheme", () => {
  it("prefers guide headline and day_model tempo + risk meta", () => {
    const theme = buildTodayExperienceTheme(
      {
        headline: "День ясности",
        day_model: {
          contract_version: "day_model_v0",
          strategy: { one_focus: "Фокус на одном решении" },
          scales: { tempo: "slow" },
          risk: { summary: "спешка" },
        },
      },
      "fallback",
    );
    expect(theme.headline).toBe("День ясности");
    expect(theme.meta).toContain("Спокойный темп");
    expect(theme.meta).toContain("спешка");
  });
});

describe("buildTodayExperienceActionLine", () => {
  it("uses best_move from core_message", () => {
    expect(
      buildTodayExperienceActionLine(
        {
          core_message: {
            body: "Тело",
            best_move: "Запиши одну мысль до 10:00",
          },
        },
        [],
      ),
    ).toBe("Запиши одну мысль до 10:00");
  });
});

describe("buildTodayExperienceProgress", () => {
  it("shows day started before action", () => {
    const p = buildTodayExperienceProgress({ actionDone: false, streakDays: 0 });
    expect(p.primary).toBe("День начался");
    expect(p.active).toBe(false);
  });

  it("shows movement after action with streak hint", () => {
    const p = buildTodayExperienceProgress({ actionDone: true, streakDays: 3 });
    expect(p.primary).toBe("Главный шаг закрыт");
    expect(p.secondary).toContain("3");
    expect(p.active).toBe(true);
  });
});
