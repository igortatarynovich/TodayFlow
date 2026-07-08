import { render, screen } from "@testing-library/react";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";

describe("PlanetIcon", () => {
  it("renders asset-mode planet symbol at requested size", () => {
    render(<PlanetIcon planet="Sun" size={24} stroke="currentColor" />);
    const symbol = screen.getByTestId("planet-symbol");
    expect(symbol).toBeInTheDocument();
    expect(symbol).toHaveStyle({ width: "24px", height: "24px" });
  });

  it("resolves RU planet names", () => {
    render(<PlanetIcon planet="Луна" size={20} />);
    expect(screen.getByTestId("planet-symbol")).toBeInTheDocument();
  });

  it("returns null for unknown bodies", () => {
    const { container } = render(<PlanetIcon planet="Chiron" />);
    expect(container.firstChild).toBeNull();
  });
});
