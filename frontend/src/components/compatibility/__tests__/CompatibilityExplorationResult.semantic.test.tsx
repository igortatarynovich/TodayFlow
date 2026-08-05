import { render, screen } from "@testing-library/react";
import { CompatibilityExplorationResult } from "@/components/compatibility/CompatibilityExplorationResult";
import type { CompatibilityExplorationModel } from "@/lib/buildCompatibilityExplorationModel";

function baseModel(over: Partial<CompatibilityExplorationModel> = {}): CompatibilityExplorationModel {
  return {
    scenarioId: "after_argument",
    scenarioTitle: "После ссоры",
    scenarioPoster: "После ссоры",
    scenarioSubtitle: "Как вы сходитесь снова",
    tone: "romantic",
    toneMode: "serious",
    presentation: "serious",
    pairLine: "Игорь · Анна",
    score: 72,
    scoreLabel: "Совместимость в этом сценарии",
    mainThought: "Сначала восстановите контакт, потом разбирайте содержание.",
    dimensions: [
      { id: "pace", emoji: "⏱", label: "Темп", score: 70 },
      { id: "trust", emoji: "🤝", label: "Доверие", score: 75 },
    ],
    narrative: [
      "Завтра разговор начнётся с паузы, а не с обвинения.",
      "Если удержать тон, появится окно для одной точной просьбы.",
    ],
    strongestResource: "Оба умеют возвращаться к теме без театра.",
    mainRisk: "Один ускорит разбор, второй закроется.",
    tips: ["Назовите одну конкретную просьбу.", "Не перечисляйте весь список претензий."],
    deepSections: [
      {
        id: "dynamics",
        title: "Динамика",
        takeaway: "Темп расходится в первые минуты.",
        detail: "Один хочет закрыть тему, второй — понять.",
        risk: "Давление ускоряет защиту.",
        action: "Договоритесь о десяти минутах без решений.",
      },
    ],
    continuationScenarios: [],
    ...over,
  };
}

describe("CompatibilityExplorationResult · Task 2.9b semantic layers", () => {
  it("renders main thought, duals, tips, and narrative quote as callouts/quotes", () => {
    render(<CompatibilityExplorationResult model={baseModel()} />);

    expect(screen.getByTestId("compat-exploration-main-thought")).toHaveAttribute("data-tone", "insight");
    expect(screen.getByTestId("compat-exploration-strongest")).toHaveAttribute("data-tone", "help");
    expect(screen.getByTestId("compat-exploration-risk")).toHaveAttribute("data-tone", "avoid");
    expect(screen.getByTestId("compat-exploration-tips")).toHaveAttribute("data-tone", "practice");
    expect(screen.getByTestId("compat-exploration-narrative-quote")).toHaveTextContent(/паузы/i);
  });
});
