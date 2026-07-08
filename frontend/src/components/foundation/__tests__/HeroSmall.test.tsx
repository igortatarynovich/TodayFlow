import { render, screen } from "@testing-library/react";
import { HeroSmall } from "@/components/foundation/HeroSmall";
import { CompatibilityOrbitSymbol } from "@/components/visualIdentity/CompatibilityOrbitSymbol";

describe("HeroSmall", () => {
  it("renders foundation small hero with 48px symbol and section title", () => {
    render(
      <HeroSmall
        symbol={<CompatibilityOrbitSymbol size={48} />}
        kicker="Совместимость"
        title="Овен × Телец"
        meta="Как вы цепляетесь и где спотыкаетесь."
      />,
    );

    const hero = screen.getByTestId("hero-small");
    expect(hero).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Овен × Телец" })).toBeInTheDocument();
    expect(screen.getByText("Как вы цепляетесь и где спотыкаетесь.")).toBeInTheDocument();

    const symbol = hero.querySelector('[data-testid="compatibility-orbit-symbol"]');
    expect(symbol).toBeTruthy();
    expect(symbol).toHaveStyle({ width: "48px", height: "48px" });
  });

  it("flush mode drops outer chrome class behavior", () => {
    render(<HeroSmall flush symbol={<CompatibilityOrbitSymbol size={48} />} title="Тема" />);
    expect(screen.getByTestId("hero-small").className).toMatch(/heroSmallFlush/);
  });
});
