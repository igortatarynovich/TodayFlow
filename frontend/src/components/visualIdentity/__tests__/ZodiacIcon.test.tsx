import { render, screen } from "@testing-library/react";
import { ZodiacIcon } from "@/components/visualIdentity/ZodiacIcon";

describe("ZodiacIcon", () => {
  it("renders asset-mode zodiac symbol at requested size", () => {
    render(<ZodiacIcon sign="Aquarius" size={24} stroke="currentColor" />);
    const symbol = screen.getByTestId("zodiac-symbol");
    expect(symbol).toBeInTheDocument();
    expect(symbol).toHaveStyle({ width: "24px", height: "24px" });
  });

  it("resolves RU zodiac names", () => {
    render(<ZodiacIcon sign="Водолей" size={20} />);
    expect(screen.getByTestId("zodiac-symbol")).toBeInTheDocument();
  });

  it("returns null for unknown signs", () => {
    const { container } = render(<ZodiacIcon sign="Ophiuchus" />);
    expect(container.firstChild).toBeNull();
  });
});
