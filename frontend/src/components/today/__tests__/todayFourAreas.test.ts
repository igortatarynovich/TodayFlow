import { computeSphereScoresProvisional } from "@/components/today/todayFourAreas";
import type { FusionResponse } from "@/components/today/todayPageUtils";

describe("computeSphereScoresProvisional (O11)", () => {
  const fusionTwoCategories: FusionResponse = {
    scores: { energy: 50, emotional_balance: 50, focus: 50 },
    recommendations: [],
    encouragement: "",
    rhythm_context: {
      goals: [{ title: "G", scope: "week", completed: false }],
      habits: [{ name: "H", category: null, frequency: "daily", completed_today: false }],
      ascetics: [],
      diary: { has_entry_today: false, entries_last_7_days: 0 },
    },
  };

  it("is false when meaning ring has score", () => {
    expect(
      computeSphereScoresProvisional([{ ring: "Love", score: 60, trend_7d: 0, confidence: "low", top_contributors: [] }], null),
    ).toBe(false);
  });

  it("is true when no rings and sparse rhythm", () => {
    expect(
      computeSphereScoresProvisional([], {
        scores: { energy: 50, emotional_balance: 50, focus: 50 },
        recommendations: [],
        encouragement: "",
        rhythm_context: {
          goals: [{ title: "Only goals", scope: "week", completed: false }],
          habits: [],
          ascetics: [],
          diary: { has_entry_today: false, entries_last_7_days: 0 },
        },
      }),
    ).toBe(true);
  });

  it("is false when no rings but two rhythm categories", () => {
    expect(computeSphereScoresProvisional([], fusionTwoCategories)).toBe(false);
  });
});
