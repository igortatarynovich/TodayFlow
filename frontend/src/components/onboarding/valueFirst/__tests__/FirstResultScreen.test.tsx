import { render, screen, fireEvent } from "@testing-library/react";
import { FirstResultScreen } from "@/components/onboarding/valueFirst/FirstResultScreen";
import type { FirstResultModel } from "@/lib/buildFirstResultModel";

const preview: FirstResultModel = {
  displayName: "Igor",
  heroTitle: "Igor, я уже вижу первые линии.",
  heroSubtitle: "Сейчас скажу главное. Остальное — если захочешь развернуть.",
  keyInfluences: [
    { id: "sun", label: "Солнечный знак", value: "Водолей", traits: ["Свобода", "Идеи", "Независимость"] },
    { id: "life_path", label: "Число пути", value: "7", traits: ["Глубина", "Анализ", "Интуиция"] },
  ],
  globalWhySummary: "На это указывают Водолей, число пути 7 и воздушная стихия.",
  nameInsight: {
    displayName: "Igor",
    headline: "Igor — имя уже несёт свой ритм и числовой оттенок.",
    tiles: [
      { id: "expression", label: "Число имени", value: "7", meaning: "Ты проявляешься через глубину." },
    ],
  },
  dominantTrait: {
    headline: "Ты принимаешь решения через логику и концепцию.",
    supporting: ["Тебе важно понимать, что происходит."],
    whyExplanation: "Главная линия карты складывается из воздушной стихии и жизненного сценария числа 7.",
  },
  miniPortrait: ["Ты думаешь иначе.", "Тебе важен смысл, а не просто действие."],
  portraitCards: [
    {
      id: "1",
      icon: "🧠",
      title: "Как ты чаще принимаешь решения",
      body: "Ты принимаешь решения через логику.",
      cardType: "observation",
      whyExplanation: "Здесь особенно заметно влияние воздушной стихии и числа пути 7.",
    },
  ],
  moreObservations: [
    {
      id: "2",
      icon: "🌱",
      title: "Что помогает тебе развиваться",
      body: "Тебе особенно полезно учиться через опыт.",
      cardType: "recommendation",
      whyExplanation: "Такой способ развития хорошо согласуется с твоим числом пути 7.",
    },
  ],
  surprise: {
    label: "Одна деталь, которая может удивить",
    body: "Сегодня особенно полезно помнить: понимаешь больше, чем говоришь.",
    whyExplanation: "На это указывают Водолей и число пути 7.",
  },
  closingMessage: "Это начало. Сегодня можно прожить первый день — и уже завтра карта станет глубже.",
  refineHint: "Можно сразу начать день или минуту уделить уточнению карты.",
  firstTodayCtaLabel: "Начнём первый день",
  refineCtaLabel: "Уточнить карту",
  audit: { candidateCount: 20, selectedIds: ["1"], selections: [] },
};

function openDeepenPanel() {
  fireEvent.click(screen.getByRole("button", { name: "Хочешь — покажу подробнее" }));
}

describe("FirstResultScreen", () => {
  it("renders conversation opening with CTAs and deepen panel", () => {
    render(
      <FirstResultScreen
        preview={preview}
        firstTodayHref="/today?first=1"
        refineHref="/onboarding/refine"
      />,
    );

    expect(screen.getByTestId("first-result-screen")).toBeInTheDocument();
    expect(screen.getByTestId("conversation-turn-preview_recognition")).toBeInTheDocument();
    expect(screen.getByTestId("onboarding-preview-first-today")).toHaveAttribute("href", "/today?first=1");
    expect(screen.getByTestId("onboarding-preview-refine")).toHaveAttribute("href", "/onboarding/refine");
    expect(screen.getByText(/это начало/i)).toBeInTheDocument();

    fireEvent.click(screen.getAllByRole("button", { name: "Почему?" })[0]);
    expect(screen.getByText(/воздушной/i)).toBeInTheDocument();

    openDeepenPanel();
    expect(screen.getByTestId("name-insight-section")).toBeInTheDocument();
  });

  it("expands additional observations inside deepen panel", () => {
    render(
      <FirstResultScreen
        preview={preview}
        firstTodayHref="/today?first=1"
        refineHref="/onboarding/refine"
      />,
    );

    openDeepenPanel();
    fireEvent.click(screen.getByTestId("show-more-observations"));
    expect(screen.getByTestId("portrait-card-more-2")).toBeInTheDocument();
  });
});
