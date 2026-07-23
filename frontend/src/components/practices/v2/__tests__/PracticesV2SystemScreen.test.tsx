import { render, screen } from "@testing-library/react";
import { PracticesV2SystemScreen } from "@/components/practices/v2/PracticesV2SystemScreen";
import { buildPracticesV2LiveContext } from "@/lib/practicesPage/buildPracticesV2LiveContext";

describe("PracticesV2SystemScreen", () => {
  it("renders journey scenes with practice of day and library", () => {
    render(
      <PracticesV2SystemScreen
        locale="ru"
        displayName="Мария"
        userInitial="М"
        statusLabel="Луна в Рыбах"
        searchQuery=""
        onSearchChange={() => {}}
        tabs={[
          { id: "all", label: "Все", tone: "dark" },
          { id: "breath", label: "Дыхание" },
        ]}
        activeTabId="all"
        onTabChange={() => {}}
        heroBody="Персональная практика на сегодня."
        heroPrimaryHref="/practices/p1"
        heroSecondaryHref="#library"
        practiceOfDay={{
          title: "Тихий фокус",
          description: "Собери внимание перед важным делом.",
          minutes: 12,
          steps: 4,
          href: "/practices/p1",
        }}
        practiceRecommendation={{
          kind: "practice",
          text: "Дыши медленнее перед стартом.",
          reason: "День просит мягкий вход, без рывка.",
        }}
        programCards={[
          {
            id: "p1",
            href: "/practices/p1",
            title: "Дыхание 4-7-8",
            description: "Успокаивающая техника.",
            durationLabel: "5 мин",
            iconGlyph: "✦",
            featured: true,
          },
        ]}
        quickItems={[]}
        live={buildPracticesV2LiveContext()}
        monthLabel="Май"
      />,
    );

    expect(screen.getByTestId("practices-v2-system")).toBeInTheDocument();
    expect(screen.getByTestId("practices-journey-support")).toBeInTheDocument();
    expect(screen.getByTestId("practices-journey-library")).toBeInTheDocument();
    expect(screen.getByTestId("practices-journey-bridge")).toBeInTheDocument();
    expect(screen.getByText("Сегодняшняя опора")).toBeInTheDocument();
    expect(screen.getByText("Центр ежедневных ритуалов")).toBeInTheDocument();
    expect(screen.getByText("Тихий фокус")).toBeInTheDocument();
    expect(screen.getByTestId("practices-day-story-reason")).toHaveTextContent(
      /День просит мягкий вход/,
    );
    expect(screen.getByTestId("practices-day-story-text")).toHaveTextContent(
      /Дыши медленнее/,
    );
    expect(screen.getByText("Библиотека практик")).toBeInTheDocument();
    expect(screen.getByText("Дыхание 4-7-8")).toBeInTheDocument();
    expect(
      screen.getByText(/Заверши первую практику — здесь появится твой недельный ритм/),
    ).toBeInTheDocument();
  });
});
