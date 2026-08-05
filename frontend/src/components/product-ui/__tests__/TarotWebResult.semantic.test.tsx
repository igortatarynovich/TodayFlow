import { render, screen } from "@testing-library/react";
import { TarotWebResult } from "@/components/product-ui/TarotWebResult";
import type { TarotReadingStoryModel } from "@/lib/buildTarotReadingStoryModel";

function baseModel(over: Partial<TarotReadingStoryModel> = {}): TarotReadingStoryModel {
  return {
    question: "Стоит ли менять работу?",
    mainAnswer: "Сначала проясни одно условие здесь. Потом решай о шаге.",
    storyNarrative: "Карты складываются вокруг ясности перед прыжком.",
    symbolsOverview: "Луна держит сомнение. Шут предлагает шаг без идеала.",
    cardInsights: [],
    insights: { holding: null, shifting: null, attention: null },
    todaySuggestion: "Скажи одну конкретную просьбу без списка условий.",
    followUpPrompt: null,
    followUpChips: [],
    actions: [],
    choiceStory: {
      option_a_summary: "Даёт ясность. Стоит потерять скорость.",
      option_b_summary: "Даёт покой. Стоит отложить разговор.",
      confidence_note: "Карты не обещают гарантию исхода.",
    },
    ...over,
  };
}

describe("TarotWebResult · Task 2.9b semantic layers", () => {
  it("renders answer, next step, choice duals, confidence, and why as callouts/quotes", () => {
    render(<TarotWebResult model={baseModel()} />);

    expect(screen.getByTestId("tarot-narrative-answer")).toHaveAttribute("data-tone", "insight");
    expect(screen.getByTestId("tarot-narrative-today")).toHaveAttribute("data-tone", "practice");
    expect(screen.getByTestId("tarot-choice-a-help")).toHaveAttribute("data-tone", "help");
    expect(screen.getByTestId("tarot-choice-a-risk")).toHaveAttribute("data-tone", "avoid");
    expect(screen.getByTestId("tarot-choice-b-help")).toHaveAttribute("data-tone", "help");
    expect(screen.getByTestId("tarot-confidence-note")).toHaveTextContent(/не обещают гарантию/i);
    expect(screen.getByTestId("tarot-why-details")).toBeInTheDocument();
    expect(screen.getByTestId("tarot-narrative-symbols")).toBeInTheDocument();
    expect(screen.getByTestId("tarot-narrative-why")).toBeInTheDocument();
  });
});
