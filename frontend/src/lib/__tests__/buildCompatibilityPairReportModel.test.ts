import { buildCompatibilityPairReportModel } from "@/lib/buildCompatibilityPairReportModel";

describe("buildCompatibilityPairReportModel", () => {
  it("builds journal sections with human conclusion", () => {
    const model = buildCompatibilityPairReportModel({
      name1: "Анна",
      name2: "Игорь",
      overallScore: 82,
      summary: "Вы легко вдохновляете друг друга.",
      editorial: {
        pair_thesis: "Вы очень легко вдохновляете друг друга, но одинаково болезненно переживаете моменты непонимания.",
        strengths: ["Общий темп", "Юмор"],
        tensions: ["Резкие слова в ссоре"],
      },
      aspects: [{ type: "Love", description: "Сильное притяжение", score: 8 }],
    });

    expect(model.pairLine).toBe("Анна ❤️ Игорь");
    expect(model.score).toBe(82);
    expect(model.mainConclusion).toMatch(/вдохновляете друг друга/);
    expect(model.sections.some((s) => s.title === "Любовь")).toBe(true);
    expect(model.sections.some((s) => s.title === "Конфликты")).toBe(true);
  });
});
