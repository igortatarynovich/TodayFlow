import { render, screen } from "@testing-library/react";
import { HeroMedium } from "@/components/foundation/HeroMedium";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";

describe("HeroMedium", () => {
  it("renders foundation medium hero with 80px symbol slot", () => {
    render(
      <HeroMedium
        symbol={<ArchetypeSymbol seed="Sage" size={80} stroke="currentColor" />}
        kicker="Главная тема дня"
        title="Сначала ясность, потом шаг."
        subline="День про структуру без спешки."
        pillars={[{ id: "sun", label: "Солнце · Водолей" }]}
      />,
    );

    const hero = screen.getByTestId("hero-medium");
    expect(hero).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Сначала ясность, потом шаг." })).toBeInTheDocument();
    expect(screen.getByText("День про структуру без спешки.")).toBeInTheDocument();

    const symbol = hero.querySelector('[data-testid="archetype-symbol"]');
    expect(symbol).toBeTruthy();
    expect(symbol).toHaveStyle({ width: "80px", height: "80px" });
  });

  it("shows loading copy when loading", () => {
    render(
      <HeroMedium
        symbol={<ArchetypeSymbol seed="Sage" size={80} />}
        title="ignored"
        loading
        loadingText="Собираем основу твоего дня…"
      />,
    );

    expect(screen.getByText("Собираем основу твоего дня…")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "ignored" })).not.toBeInTheDocument();
  });

  it("embedded mode skips full viewport min-height class behavior", () => {
    render(
      <HeroMedium
        embedded
        symbol={<ArchetypeSymbol seed="Sage" size={80} />}
        title="Тема"
      />,
    );

    expect(screen.getByTestId("hero-medium").className).toMatch(/heroMediumEmbedded/);
  });
});
