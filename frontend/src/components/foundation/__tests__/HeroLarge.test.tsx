import { render, screen } from "@testing-library/react";
import { HeroLarge, HeroLargeChipRow, HeroLargeInsightPanel } from "@/components/foundation/HeroLarge";

describe("HeroLarge", () => {
  it("renders foundation hero with 120px symbol slot and canonical structure", () => {
    render(
      <HeroLarge
        symbolSeed="Sage"
        kicker="Профиль"
        sectionLabel="Кто ты"
        title="Sage"
        digest="Ты лучше всего раскрываешься там, где есть понимание смысла."
        pillars={[{ id: "sun", label: "Солнце в Водолее", accent: true }]}
        topAction={<button type="button">Данные рождения</button>}
      />,
    );

    const hero = screen.getByTestId("hero-large");
    expect(hero).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Sage" })).toBeInTheDocument();
    expect(screen.getByText("Кто ты")).toBeInTheDocument();
    expect(screen.getByText("Солнце в Водолее")).toBeInTheDocument();
    expect(screen.getByText(/понимание смысла/)).toBeInTheDocument();

    const symbol = hero.querySelector('[data-testid="archetype-symbol"]');
    expect(symbol).toBeTruthy();
    expect(symbol).toHaveStyle({ width: "120px", height: "120px" });
  });

  it("renders insight panel companions for teaser strips", () => {
    render(
      <HeroLargeInsightPanel eyebrow="Твой старт сегодня">
        <HeroLargeChipRow items={["Фокус: Ясность", "Состояние: Стабильно"]} />
      </HeroLargeInsightPanel>,
    );

    expect(screen.getByText("Твой старт сегодня")).toBeInTheDocument();
    expect(screen.getByText("Фокус: Ясность")).toBeInTheDocument();
    expect(screen.getByText("Состояние: Стабильно")).toBeInTheDocument();
  });
});
