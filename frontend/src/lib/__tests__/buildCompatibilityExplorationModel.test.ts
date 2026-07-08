import { buildExplorationFromDynamics, buildExplorationFromPairInput } from "@/lib/buildCompatibilityExplorationModel";
import { buildScenarioDeepSectionsFromPairDeep } from "@/lib/compatibilityScenarioDeepSections";
import { getScenarioSkin } from "@/lib/compatibilityScenarioSkins";
import type { SignCompatProductSurface } from "@/components/compatibility/CompatibilityDynamicsSurface";

const mockSurface: SignCompatProductSurface = {
  score_tagline: "Вы хорошо держитесь вместе в кризисах, если роли распределены заранее.",
  subscores: { attraction: 79, stability: 83, conflicts: 68, sexuality: 81 },
  overview_paragraphs: ["Первый абзац narrative.", "Второй абзац."],
  blocks: [
    {
      key: "attraction",
      title: "Притяжение",
      subtitle: "sub",
      takeaway: "Сильный ресурс пары.",
      detail: "detail",
      risk: "Борьба за лидерство под давлением.",
      action: "Распределите роли заранее.",
    },
    {
      key: "conflicts",
      title: "Конфликты",
      subtitle: "sub",
      takeaway: "t",
      detail: "d",
      risk: "Главный риск — борьба за лидерство.",
      action: "Договоритесь о правилах.",
    },
  ],
  roles: { you_bullets: ["a"], partner_bullets: ["b"] },
  scenarios: [{ id: "closer", title: "t", bullets: ["Совет 1", "Совет 2"] }],
};

describe("buildCompatibilityExplorationModel", () => {
  it("builds playful scenario with short stat layout", () => {
    const model = buildExplorationFromDynamics({
      seriesId: "partner_in_crime",
      pairTitle: "Овен × Рак",
      score: 82,
      productSurface: mockSurface,
    });

    expect(model.presentation).toBe("playful");
    expect(model.toneMode).toBe("playful");
    expect(model.deepSections).toHaveLength(0);
    expect(model.tips).toHaveLength(0);
    expect(model.dimensions[0].quip).toBeTruthy();
    expect(model.scoreLabel).not.toBe("Сильная связь");
  });

  it("maps apocalypse scenario dimensions from dynamics", () => {
    const model = buildExplorationFromDynamics({
      seriesId: "apocalypse",
      pairTitle: "Овен × Рак",
      score: 82,
      productSurface: mockSurface,
    });

    expect(model.scenarioId).toBe("apocalypse");
    expect(model.score).toBe(82);
    expect(model.dimensions).toHaveLength(4);
    expect(model.dimensions[0].label).toBe("Поддержка");
    expect(model.mainThought).toContain("кризисах");
    expect(model.tips.length).toBeLessThanOrEqual(3);
    expect(model.continuationScenarios.length).toBeGreaterThan(0);
  });

  it("builds pair exploration with scenario skin", () => {
    const model = buildExplorationFromPairInput(
      {
        name1: "Аня",
        name2: "Макс",
        overallScore: 76,
        summary: "Хорошая база.",
        aspects: [{ type: "Love", description: "Тянет друг к другу.", score: 80 }],
        deepDive: {
          dimensions: [
            { key: "attraction", label: "Притяжение", score: 80, summary: "Быстрый контакт." },
            { key: "communication", label: "Коммуникация", score: 65, summary: "Нужен темп." },
            { key: "stability", label: "Стабильность", score: 72, summary: "Быт держит." },
          ],
        },
      },
      "office",
    );

    expect(model.scenarioId).toBe("office");
    expect(model.pairLine).toBe("Аня × Макс");
    expect(model.dimensions[0].emoji).toBeTruthy();
    expect(model.deepSections.length).toBeGreaterThan(0);
    expect(model.deepSections[0].title).toBe("Надёжность");
  });

  it("maps dynamics deep sections to scenario skin (4 slots max)", () => {
    const fullSurface: SignCompatProductSurface = {
      ...mockSurface,
      blocks: [
        { key: "attraction", title: "Generic", subtitle: "", takeaway: "A", detail: "", risk: "", action: "" },
        { key: "stability", title: "Generic", subtitle: "", takeaway: "S", detail: "", risk: "", action: "" },
        { key: "conflicts", title: "Generic", subtitle: "", takeaway: "C", detail: "", risk: "", action: "" },
        { key: "sexuality", title: "Generic", subtitle: "", takeaway: "X", detail: "", risk: "", action: "" },
        { key: "extra", title: "Extra", subtitle: "", takeaway: "E", detail: "", risk: "", action: "" },
      ],
    };
    const model = buildExplorationFromDynamics({
      seriesId: "office",
      pairTitle: "A × B",
      score: 70,
      productSurface: fullSurface,
    });
    expect(model.deepSections).toHaveLength(4);
    expect(model.deepSections.map((s) => s.title)).toEqual(["Надёжность", "Рабочие трения", "Синергия", "Энергия"]);
  });

  it("reorders pair deep sections from attachment deep_block_order", () => {
    const skin = getScenarioSkin("love");
    const sections = buildScenarioDeepSectionsFromPairDeep(
      skin,
      {
        dimensions: [
          { key: "communication", label: "Comm", score: 70, summary: "Comm summary" },
          { key: "emotional", label: "Emo", score: 65, summary: "Emo summary" },
          { key: "stability", label: "Stab", score: 80, summary: "Stab summary" },
        ],
      },
      [],
      ["conflicts", "communication", "emotions", "sexuality", "long_term"],
    );
    expect(sections[0]?.id).toBe("conflicts");
  });
});
