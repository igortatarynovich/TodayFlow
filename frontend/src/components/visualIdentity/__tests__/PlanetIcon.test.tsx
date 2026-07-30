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

  it("ships seal-weight assets for all ten traditional planets", () => {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");
    const slugs = [
      "sun",
      "moon",
      "mercury",
      "venus",
      "mars",
      "jupiter",
      "saturn",
      "uranus",
      "neptune",
      "pluto",
    ] as const;
    const root = path.join(process.cwd(), "public/images/icons/planets");
    for (const slug of slugs) {
      const svg = fs.readFileSync(path.join(root, `${slug}.svg`), "utf8");
      expect(svg).toMatch(/viewBox="0 0 56 56"/);
      // Seal pass: heavier stroke and/or filled mass (not the old 1.5-only set).
      expect(svg.includes('stroke-width="2.75"') || svg.includes('fill="#000"')).toBe(true);
    }
  });
});
