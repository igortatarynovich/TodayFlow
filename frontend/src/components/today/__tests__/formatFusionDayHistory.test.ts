import {
  formatFusionDayHistoryEn,
  formatFusionDayHistoryMeaningLineRu,
  formatFusionDayHistoryReflectionLineRu,
  formatFusionDayHistoryRu,
  formatFusionDayHistoryWeekSummaryRu,
} from "@/components/today/todayRitualCopy";

describe("formatFusionDayHistoryRu", () => {
  it("formats yesterday + delta", () => {
    const line = formatFusionDayHistoryRu({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 55, emotional_balance: 60, focus: 52 },
      },
      fusion_score_delta_vs_yesterday: { energy: 8, emotional_balance: -2, focus: 9 },
    });
    expect(line).toBe(
      "Вчера: энергия 55, баланс 60, фокус 52 · к сегодня: энергия +8, баланс -2, фокус +9",
    );
  });

  it("DE-9 v1.3: all-zero delta uses explanatory tail instead of zeros", () => {
    const line = formatFusionDayHistoryRu({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 50, emotional_balance: 50, focus: 50 },
      },
      fusion_score_delta_vs_yesterday: { energy: 0, emotional_balance: 0, focus: 0 },
    });
    expect(line).toContain("Вчера: энергия 50");
    expect(line).toContain("Flow");
    expect(line).not.toContain("к сегодня: энергия 0");
  });

  it("O7: when fusion_score_delta_trustworthy is false, standalone line without fake yesterday scores", () => {
    const line = formatFusionDayHistoryRu({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 62, emotional_balance: 55, focus: 58 },
      },
      fusion_score_delta_vs_yesterday: { energy: 12, emotional_balance: -5, focus: 3 },
      fusion_score_delta_trustworthy: false,
    });
    expect(line).not.toContain("Вчера: энергия");
    expect(line).not.toContain("к сегодня:");
    expect(line).toContain("не было отметок");
  });
});

describe("formatFusionDayHistoryEn", () => {
  it("uses EN tail when delta is all zero", () => {
    const line = formatFusionDayHistoryEn({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 50, emotional_balance: 50, focus: 50 },
      },
      fusion_score_delta_vs_yesterday: { energy: 0, emotional_balance: 0, focus: 0 },
    });
    expect(line).toContain("Yesterday: energy 50");
    expect(line).toContain("Flow");
    expect(line).not.toContain("toward today: energy 0");
  });

  it("O7: when delta not trustworthy, standalone line without yesterday scores", () => {
    const line = formatFusionDayHistoryEn({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 62, emotional_balance: 55, focus: 58 },
      },
      fusion_score_delta_vs_yesterday: { energy: 12, emotional_balance: -5, focus: 3 },
      fusion_score_delta_trustworthy: false,
    });
    expect(line).not.toContain("Yesterday: energy");
    expect(line).not.toContain("toward today:");
    expect(line).toContain("No Flow markers");
  });
});

describe("formatFusionDayHistoryWeekSummaryRu", () => {
  it("formats trailing_7d_summary with en dash between min and max", () => {
    const line = formatFusionDayHistoryWeekSummaryRu({
      contract_version: "day_history_v0",
      trailing_7d_summary: {
        energy: { avg: 51.7, min: 42, max: 61, days: 7 },
        emotional_balance: { avg: 48.2, min: 40, max: 55, days: 7 },
        focus: { avg: 54.9, min: 48, max: 62, days: 7 },
      },
    });
    expect(line).toBe(
      "7 дней до вчера: энергия ср. 52 (42\u201361), баланс ср. 48 (40\u201355), фокус ср. 55 (48\u201362)",
    );
  });

  it("returns null without trailing_7d_summary", () => {
    expect(
      formatFusionDayHistoryWeekSummaryRu({
        contract_version: "day_history_v0",
        yesterday: { date: "2026-05-03", fusion_scores: { energy: 50, emotional_balance: 50, focus: 50 } },
        fusion_score_delta_vs_yesterday: { energy: 0, emotional_balance: 0, focus: 0 },
      }),
    ).toBeNull();
  });

  it("O7: hides week line when trailing_7d_summary_trustworthy is false", () => {
    expect(
      formatFusionDayHistoryWeekSummaryRu({
        contract_version: "day_history_v0",
        trailing_7d_summary_trustworthy: false,
        trailing_7d_summary: {
          energy: { avg: 50, min: 50, max: 50, days: 7 },
          emotional_balance: { avg: 50, min: 50, max: 50, days: 7 },
          focus: { avg: 50, min: 50, max: 50, days: 7 },
        },
      }),
    ).toBeNull();
  });
});

describe("formatFusionDayHistoryMeaningLineRu", () => {
  it("formats yesterday Flow steps and spheres", () => {
    const line = formatFusionDayHistoryMeaningLineRu({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 50, emotional_balance: 50, focus: 50 },
        meaning_active: true,
        meaning_completions_total: 2,
        meaning_day_signals: { habit_completed: 1, practice_completed: 1, sphere_opened: 1 },
        day_flow: { evening_completed: true },
      },
    });
    expect(line).toBe("Вчера: 2 шага в Flow, вечер закрыт, открыта 1 сфера.");
  });

  it("returns null when yesterday was inactive", () => {
    expect(
      formatFusionDayHistoryMeaningLineRu({
        contract_version: "day_history_v0",
        yesterday: {
          date: "2026-05-03",
          fusion_scores: { energy: 50, emotional_balance: 50, focus: 50 },
          meaning_active: false,
        },
      }),
    ).toBeNull();
  });
});

describe("formatFusionDayHistoryReflectionLineRu", () => {
  it("formats evening reflection excerpt", () => {
    const line = formatFusionDayHistoryReflectionLineRu({
      contract_version: "day_history_v0",
      yesterday: {
        date: "2026-05-03",
        fusion_scores: { energy: 50, emotional_balance: 50, focus: 50 },
        reflection_excerpt: {
          contract_version: "day_connection_excerpt_v0",
          evening_reflection: "Получилось не разгонять чаты",
          has_reflection: true,
        },
      },
    });
    expect(line).toBe("Вчера вечером: «Получилось не разгонять чаты»");
  });
});
